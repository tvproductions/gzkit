"""Stage 5 pre-flight checklist for OBPI completion (GHI #196).

Reactive triage at Stage 5 — discovering brief readiness gaps, frontmatter
drift, lock ownership mismatches, missing ARB receipts, or stale plan-audit
receipts after invoking ``gz obpi complete`` — wastes operator time. This
command runs the same checks mechanically, upfront, with a clear pass/fail
report and a named remediation per failure.

The intended invocation pattern is **before** ``gz obpi complete``:

    uv run gz obpi precomplete OBPI-0.0.16-04
    # If exit 0, proceed to:
    uv run gz obpi complete OBPI-0.0.16-04 --attestor ... --attestation-text ...

The ``gz-obpi-pipeline`` skill wires this in as Stage 5 Step 0.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from rich.markup import escape

from gzkit.canonical_steps import CANONICAL_STEP_COMMANDS
from gzkit.cli.helpers.exit_codes import (
    EXIT_POLICY_BREACH,
    EXIT_SUCCESS,
    EXIT_USER_ERROR,
)
from gzkit.commands.common import console, get_project_root
from gzkit.commands.validate_task_envelope import pending_obpi_task_envelope_errors
from gzkit.governance.req_coverage import discover_covers, parse_brief_req_kinds

if TYPE_CHECKING:
    from collections.abc import Iterable


class CheckResult(BaseModel):
    """One precondition check: name, pass/fail, evidence message, remediation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Stable precondition check identifier")
    ok: bool = Field(..., description="Whether the precondition passed")
    message: str = Field(..., description="Observed evidence for the check result")
    remediation: str | None = Field(None, description="Operator remediation when blocked")


def obpi_precomplete_cmd(*, obpi_id: str, as_json: bool = False) -> int:
    """Handle ``gz obpi precomplete``.

    Exit codes (per .claude/rules/cli.md):
      0 = all preconditions met (safe to invoke gz obpi complete)
      1 = user/config error (brief not found, OBPI id invalid, etc.)
      3 = policy breach (one or more preconditions failed)

    Non-zero exit codes are propagated via ``SystemExit`` so
    ``gzkit.cli.main`` terminates the process with the correct code — its
    else-branch swallows handler return values otherwise.
    """
    project_root = get_project_root()

    brief_path = _resolve_brief_path(project_root, obpi_id)
    if brief_path is None:
        console.print(f"[red]Brief not found for {obpi_id}[/red]")
        raise SystemExit(EXIT_USER_ERROR)

    checks = list(_run_all_checks(project_root, brief_path, obpi_id))

    if as_json:
        print(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "ready": all(c.ok for c in checks),
                    "checks": [c.model_dump() for c in checks],
                },
                indent=2,
            )
        )
    else:
        _render_human_report(obpi_id, checks)

    if not all(c.ok for c in checks):
        raise SystemExit(EXIT_POLICY_BREACH)
    return EXIT_SUCCESS


def resolve_brief_path(project_root: Path, obpi_id: str) -> Path | None:
    """Find the OBPI brief by id under either obpis/ or briefs/ layout.

    Matches on the id the caller SUPPLIED, never on a prefix derived from it. A
    bare ``OBPI-<semver>-<index>`` still resolves — it globs as its own prefix —
    but a fully-qualified id matching no brief is NOT FOUND rather than the
    nearest sibling. Deriving the bare form and searching it first meant a full
    id resolved to a different OBPI: demoting a feature ADR to pool releases its
    semver for reuse while the parked OBPI ids keep it, so one prefix can name
    two OBPIs under two different parent ADRs (GHI #826).

    Honors ``config.paths.design_root`` so the lookup works regardless of
    project layout (``docs/design`` in production, ``design`` in test
    fixtures from ``_quick_init``).
    """
    from gzkit.config import GzkitConfig

    try:
        config = GzkitConfig.load(project_root / ".gzkit.json")
        design_root = config.paths.design_root
    except (OSError, ValueError):
        design_root = "docs/design"
    candidates: list[Path] = []
    for layout in ("obpis", "briefs"):
        candidates.extend(project_root.glob(f"{design_root}/adr/**/{layout}/{obpi_id}*.md"))
    # Sorted, not glob order: `Path.glob` is filesystem-ordered, so an unsorted
    # pick makes the answer vary by machine (the GHI #721 family).
    return sorted(candidates)[0] if candidates else None


_resolve_brief_path = resolve_brief_path  # Compatibility for existing command callers.


def _run_all_checks(project_root: Path, brief_path: Path, obpi_id: str) -> Iterable[CheckResult]:
    """Run every Stage 5 precondition check; yield each CheckResult in order."""
    yield _check_brief_readiness(project_root, brief_path)
    yield _check_reconcile_idempotent(project_root)
    yield _check_lock_held(project_root, obpi_id)
    yield _check_arb_receipts_passed(project_root, obpi_id)
    yield _check_plan_audit_receipt(project_root, obpi_id)
    yield _check_brief_headings_scoped(project_root, brief_path)
    yield _check_behave_req_coverage_scoped(project_root, brief_path, obpi_id)
    yield _check_task_envelope_coherence(project_root, brief_path)
    yield _check_acceptance_records(project_root, obpi_id)
    yield _check_operator_block(project_root, obpi_id)
    yield _check_stage2_dispatch(project_root, obpi_id)


def _check_acceptance_records(project_root: Path, obpi_id: str) -> CheckResult:
    """Read current proof and closure, never reinterpret historical verdict prose."""
    from gzkit.acceptance_store import acceptance_blockers  # noqa: PLC0415

    blockers = acceptance_blockers(project_root, obpi_id)
    return CheckResult(
        name="adversarial_validation",
        ok=not blockers,
        message="; ".join(blockers) if blockers else "Current obligations independently accepted",
        remediation=f"gz obpi acceptance {obpi_id} status",
    )


def _check_stage2_dispatch(project_root: Path, obpi_id: str) -> CheckResult:
    """Stage 2's mandated dispatch must be recorded, or knowingly declared (GHI #845).

    The operator ruling of 2026-08-21 is that the implementer dispatch and the
    two-stage spec-reviewer + quality-reviewer review ARE the work. Before this
    check, an OBPI whose Stage 2 ran inline produced a completion receipt
    byte-identical to one that dispatched properly.

    Declared single-driver PASSES. Silent single-driver does not. That asymmetry
    is the whole point: a gate with no compliant path for a session that cannot
    dispatch is un-compliable, and an un-compliable gate gets worked around.
    """
    from gzkit.obpi_dispatch_channel import (
        dispatch_channel,
        is_single_driver,
        render_dispatch_channel,
        single_driver_declaration,
    )
    from gzkit.pipeline_runtime import pipeline_plans_dir

    plans_dir = pipeline_plans_dir(project_root)
    if not (plans_dir / f".pipeline-active-{obpi_id}.json").is_file():
        # Say it rather than pass silently: "no pipeline ran" and "the pipeline
        # dispatched correctly" must never render identically.
        return CheckResult(
            name="stage2_dispatch",
            ok=True,
            message=(
                "no active pipeline marker - dispatch not assessable here "
                "(whether this OBPI should have run through the pipeline is a "
                "separate question this check does not answer)"
            ),
        )

    # project_root, not plans_dir: since GHI #886 the channel's evidence is the
    # Layer-2 ledger, and the marker below is consulted only to answer whether a
    # pipeline is running at all.
    channel = dispatch_channel(project_root, obpi_id)
    declaration = single_driver_declaration(project_root, obpi_id)
    rendered = render_dispatch_channel(channel, declaration=declaration)

    if not is_single_driver(channel) or declaration:
        return CheckResult(name="stage2_dispatch", ok=True, message=rendered)
    return CheckResult(
        name="stage2_dispatch",
        ok=False,
        message=rendered,
        remediation=(
            "Stage 2's mandated dispatch is unrecorded. Either dispatch the roster "
            "and record each one - `uv run gz obpi dispatch "
            f"{obpi_id} --role Implementer --model <tier> --task 1` - or, if this "
            "session genuinely cannot dispatch, declare it: `uv run gz obpi dispatch "
            f'{obpi_id} --single-driver --reason "<why>"`. Declared single-driver '
            "is permitted; silent single-driver is what this gate refuses."
        ),
    )


def _check_brief_readiness(project_root: Path, brief_path: Path) -> CheckResult:
    """Brief MUST pass `gz obpi validate --authored` before completion."""
    from gzkit.hooks.obpi import ObpiValidator

    validator = ObpiValidator(project_root)
    errors = validator.validate_file(brief_path, require_authored=True)
    if errors:
        first = errors[0] if errors else "(no detail)"
        return CheckResult(
            name="brief_readiness",
            ok=False,
            message=f"{len(errors)} validator error(s); first: {first}",
            remediation=(
                f"Run `uv run gz obpi validate --authored "
                f"{brief_path.relative_to(project_root).as_posix()}` and address each error."
            ),
        )
    return CheckResult(
        name="brief_readiness",
        ok=True,
        message=f"passes --authored validation ({brief_path.name})",
    )


def _check_reconcile_idempotent(project_root: Path) -> CheckResult:
    """`gz frontmatter reconcile --dry-run` MUST produce empty rewrite list.

    Catches the GHI #193 class-of-failure (gz obpi complete writes
    `Completed` but canonical-ledger form is `in_progress`): if the brief
    was just `complete`d in a prior precomplete attempt, the dry-run will
    surface the drift and recommend a reconcile round-trip before completion.
    """
    from gzkit.governance.frontmatter_coherence import reconcile_frontmatter

    receipt = reconcile_frontmatter(project_root, dry_run=True)
    if receipt.files_rewritten:
        files = ", ".join(rw.path for rw in receipt.files_rewritten[:3])
        suffix = "..." if len(receipt.files_rewritten) > 3 else ""
        return CheckResult(
            name="reconcile_idempotent",
            ok=False,
            message=f"{len(receipt.files_rewritten)} file(s) would be rewritten: {files}{suffix}",
            remediation="Run `uv run gz frontmatter reconcile` to clear drift.",
        )
    if receipt.refused_rewrites:
        refused = ", ".join(r.path for r in receipt.refused_rewrites[:3])
        suffix = "..." if len(receipt.refused_rewrites) > 3 else ""
        return CheckResult(
            name="reconcile_idempotent",
            ok=True,
            message=(
                f"no pending frontmatter rewrites; "
                f"{len(receipt.refused_rewrites)} refused rewrite(s) surfaced by the "
                f"transition monitor: {refused}{suffix} — review refused_rewrites in "
                f"the reconciliation receipt"
            ),
        )
    return CheckResult(
        name="reconcile_idempotent",
        ok=True,
        message="no pending frontmatter rewrites",
    )


def _held_lock_files(project_root: Path, obpi_id: str) -> list[Path]:
    """Lock files for ``obpi_id``, sorted; shared by every check that reads the claim."""
    locks_dir = project_root / ".gzkit" / "locks" / "obpi"
    # The supplied id only: a lock claimed for a prefix sibling is a different
    # OBPI's claim, and honoring it hands two agents the same green light (#826).
    return sorted(locks_dir.glob(f"{obpi_id}*.json")) if locks_dir.is_dir() else []


def _check_lock_held(project_root: Path, obpi_id: str) -> CheckResult:
    """OBPI lock MUST exist before `gz obpi complete` runs."""
    if not (project_root / ".gzkit" / "locks" / "obpi").is_dir():
        return CheckResult(
            name="lock_held",
            ok=False,
            message="No .gzkit/locks/obpi/ directory",
            remediation=f"Run `uv run gz obpi lock claim {obpi_id}`.",
        )
    candidates = _held_lock_files(project_root, obpi_id)
    if not candidates:
        return CheckResult(
            name="lock_held",
            ok=False,
            message=f"No lock file matches {obpi_id}",
            remediation=f"Run `uv run gz obpi lock claim {obpi_id}`.",
        )
    return CheckResult(
        name="lock_held",
        ok=True,
        message=f"lock present at {candidates[0].relative_to(project_root).as_posix()}",
    )


#: The steps whose passing run attestation evidence needs, keyed by the step
#: identity a receipt records. `lint` is the ruff lint receipt's category.
_REQUIRED_RECEIPT_STEPS: tuple[str, ...] = ("lint", "typecheck", "unittest")


def _utc(raw: object) -> datetime | None:
    """Parse an ISO-8601 timestamp as an aware datetime; None when undatable."""
    if not isinstance(raw, str) or not raw.strip():
        return None
    try:
        parsed = datetime.fromisoformat(raw.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _lock_claimed_at(project_root: Path, obpi_id: str) -> datetime | None:
    for path in _held_lock_files(project_root, obpi_id):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(payload, dict) and (claimed := _utc(payload.get("claimed_at"))):
            return claimed
    return None


def _receipt_step(payload: dict) -> str | None:
    """Return the step a receipt records: `lint` for a lint receipt, else `step.name`."""
    if str(payload.get("schema", "")).startswith("gzkit.arb.lint_receipt"):
        return "lint"
    step = payload.get("step")
    return step.get("name") if isinstance(step, dict) else None


def _newest_receipts_since(receipts_dir: Path, claimed: datetime) -> dict[str, dict]:
    """Newest receipt per step whose run began at or after the lock claim."""
    newest: dict[str, tuple[datetime, dict]] = {}
    for path in receipts_dir.glob("arb-*.json") if receipts_dir.is_dir() else []:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        stamp, step = _utc(payload.get("timestamp_utc")), _receipt_step(payload)
        if stamp is None or step is None or stamp < claimed:
            continue
        if step not in newest or stamp > newest[step][0]:
            newest[step] = (stamp, payload)
    return {step: payload for step, (_stamp, payload) in newest.items()}


def _check_arb_receipts_passed(project_root: Path, obpi_id: str) -> CheckResult:
    """Require the newest lint/typecheck/unittest receipt since the lock claim to pass.

    A presence check answered "is something armed" and passed over 577 failed runs
    among 3718 receipts (GHI #889). The receipts that count are this OBPI's:
    written after its lock claim, newest per step (operator ruling 2026-09-14,
    "Newest per step, since lock"), and each must record ``exit_status`` 0. Red
    history before the claim is not a finding; green history before it is not
    evidence.
    """
    unittest_cmd = " ".join(CANONICAL_STEP_COMMANDS["unittest"])
    remediation = (
        "Run `uv run gz arb ruff`, `uv run gz arb typecheck`, and "
        f"`uv run gz arb step --name unittest -- {unittest_cmd}` until each passes, "
        "then re-run precomplete."
    )
    claimed = _lock_claimed_at(project_root, obpi_id)
    if claimed is None:
        return CheckResult(
            name="arb_receipts",
            ok=False,
            message=f"No readable lock claim for {obpi_id}, so no receipt can be scoped to it",
            remediation=f"Run `uv run gz obpi lock claim {obpi_id}` first. {remediation}",
        )
    newest = _newest_receipts_since(project_root / "artifacts" / "receipts", claimed)
    problems: list[str] = []
    for step in _REQUIRED_RECEIPT_STEPS:
        payload = newest.get(step)
        if payload is None:
            problems.append(f"{step}: no receipt since the lock claim")
        elif payload.get("exit_status") != 0:
            problems.append(
                f"{step}: newest receipt {payload.get('run_id')} records "
                f"exit_status={payload.get('exit_status')!r}"
            )
    if problems:
        return CheckResult(
            name="arb_receipts", ok=False, message="; ".join(problems), remediation=remediation
        )
    return CheckResult(
        name="arb_receipts",
        ok=True,
        message="newest since lock claim passed: "
        + ", ".join(f"{step} {newest[step].get('run_id')}" for step in _REQUIRED_RECEIPT_STEPS),
    )


def _check_plan_audit_receipt(project_root: Path, obpi_id: str) -> CheckResult:
    """Plan-audit receipt MUST exist with verdict PASS for the target OBPI."""
    plans_dir = project_root / ".claude" / "plans"
    if not plans_dir.is_dir():
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message="No .claude/plans/ directory",
            remediation=f"Run `uv run gz plan audit {obpi_id}`.",
        )
    candidates = sorted(plans_dir.glob(f".plan-audit-receipt-{obpi_id}*.json"))
    if not candidates:
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message=f"No plan-audit receipt for {obpi_id}",
            remediation=f"Run `uv run gz plan audit {obpi_id}`.",
        )
    receipt_path = candidates[-1]
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message=f"Receipt unreadable: {exc}",
            remediation=f"Re-run `uv run gz plan audit {obpi_id}`.",
        )
    verdict = receipt.get("verdict", "")
    if verdict != "PASS":
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message=f"Receipt verdict is {verdict!r} at {receipt_path.name}",
            remediation=(f"Address audit gaps and re-run `uv run gz plan audit {obpi_id}`."),
        )
    return CheckResult(
        name="plan_audit_receipt",
        ok=True,
        message=f"PASS receipt at {receipt_path.name}",
    )


def _check_brief_headings_scoped(project_root: Path, brief_path: Path) -> CheckResult:
    """Evidence section headings on this brief MUST be H3, not H2 (GHI #238).

    GHI #422 fix #2: catch heading drift at Stage 3, before ``gz obpi complete``
    mutates the brief. The whole-tree ``audit_brief_headings`` validator fires
    at git-sync (Stage 5), too late to abort cleanly.
    """
    from gzkit.governance.trust_audits.briefs import (  # noqa: PLC0415
        _BRIEF_EVIDENCE_H3_HEADINGS,
        _scan_one_brief_headings,
    )

    canonical_forms: dict[str, str] = {h.casefold(): h for h in _BRIEF_EVIDENCE_H3_HEADINGS}
    errors = _scan_one_brief_headings(brief_path, canonical_forms, project_root)
    if errors:
        first = errors[0].message
        return CheckResult(
            name="brief_headings",
            ok=False,
            message=f"{len(errors)} H2 evidence heading(s); first: {first[:120]}",
            remediation=(
                "Convert H2 evidence headings (`## Implementation Summary`, "
                "`## Key Proof`, `## Closing Argument`) to H3 (`### ...`)."
            ),
        )
    return CheckResult(
        name="brief_headings",
        ok=True,
        message="evidence headings are H3 (or absent)",
    )


def _check_behave_req_coverage_scoped(
    project_root: Path, brief_path: Path, obpi_id: str
) -> CheckResult:
    """Heavy-lane OBPI's REQs MUST have @REQ-* scenario tags BEFORE completion.

    GHI #422 fix #2: catch missing scenario coverage at Stage 3, before
    ``gz obpi complete`` mutates the brief to ``Completed``. The whole-tree
    ``audit_behave_req_tags`` validator only fires on briefs already in
    Completed/Validated status (post-mutation, too late). Lite-lane briefs
    are exempt; waivered OBPIs report ok with the waiver rationale.
    """
    from gzkit.governance.trust_audits.briefs import (  # noqa: PLC0415
        _ACCEPTANCE_SECTION,
        _LANE_IN_FRONTMATTER,
        _REQ_ID_IN_BRIEF,
        _load_behave_coverage_waivers,
    )

    try:
        text = brief_path.read_text(encoding="utf-8")
    except OSError as exc:
        return CheckResult(
            name="behave_req_coverage",
            ok=False,
            message=f"brief unreadable: {exc}",
            remediation=f"Re-create or restore {brief_path.name}.",
        )

    lane_match = _LANE_IN_FRONTMATTER.search(text)
    if not lane_match or lane_match.group(1).lower() != "heavy":
        return CheckResult(
            name="behave_req_coverage",
            ok=True,
            message="lite-lane brief; BDD coverage not required",
        )

    waivers = _load_behave_coverage_waivers(project_root)
    if obpi_id in waivers:
        return CheckResult(
            name="behave_req_coverage",
            ok=True,
            message=f"waived: {waivers[obpi_id][:80]}",
        )

    accept_match = _ACCEPTANCE_SECTION.search(text)
    all_req_ids = (
        sorted(set(_REQ_ID_IN_BRIEF.findall(accept_match.group(1)))) if accept_match else []
    )
    if not all_req_ids:
        return CheckResult(
            name="behave_req_coverage",
            ok=True,
            message="no REQ IDs in Acceptance Criteria",
        )

    # ADR-0.0.59 kind discipline (mirror `gz obpi complete`, GHI #636): only
    # BEHAVIOR REQs need a proof channel here. SUPPORT (ledger event + structural
    # validator) and STRUCTURAL-FENCE (parent-ADR Boundary Invariants) REQs are
    # exempt — requiring a scenario/test for them is the named anti-pattern
    # (`.gzkit/rules/tests.md` § REQ Scope Discipline). Untagged (legacy) REQs
    # default to BEHAVIOR. A BEHAVIOR REQ is satisfied by a `@REQ-*` scenario tag
    # OR an `@covers` unit test under `tests/**`; `discover_covers` unions both,
    # matching the kind-aware completion chokepoint so the pre-flight never
    # false-flags work that `gz obpi complete` accepts.
    req_kinds = parse_brief_req_kinds(brief_path)
    exempt_kinds = ("SUPPORT", "STRUCTURAL-FENCE")
    behavior_reqs = [r for r in all_req_ids if req_kinds.get(r, "BEHAVIOR") not in exempt_kinds]
    if not behavior_reqs:
        return CheckResult(
            name="behave_req_coverage",
            ok=True,
            message=f"all {len(all_req_ids)} REQ(s) are SUPPORT/STRUCTURAL-FENCE; exempt by kind",
        )

    tests_root = project_root / "tests"
    features_root = project_root / "features"
    missing = [
        r for r in behavior_reqs if not discover_covers(r, tests_root, features_root=features_root)
    ]
    if missing:
        first = ", ".join(missing[:3])
        suffix = f" (+{len(missing) - 3} more)" if len(missing) > 3 else ""
        return CheckResult(
            name="behave_req_coverage",
            ok=False,
            message=(
                f"{len(missing)} BEHAVIOR REQ(s) lack a covering test or scenario: {first}{suffix}"
            ),
            remediation=(
                f'Add a `@covers("REQ-X.Y.Z-NN-MM")` unit test under `tests/**` or a '
                f"`@REQ-X.Y.Z-NN-MM` scenario tag under `features/**` for {obpi_id}'s "
                "BEHAVIOR REQs, or add a waiver entry in "
                "`data/behave_coverage_waivers.json` with rationale."
            ),
        )
    return CheckResult(
        name="behave_req_coverage",
        ok=True,
        message=f"{len(behavior_reqs)} BEHAVIOR REQ(s) all covered (test or scenario)",
    )


def _check_task_envelope_coherence(project_root: Path, brief_path: Path) -> CheckResult:
    """Early-warn on task-envelope Signature-(b) residue (GHI #590).

    Mirrors the fail-closed gate in ``gz obpi complete``: an OBPI that would close
    with any task-envelope residue — Sig (a) unattributed labor, Sig (b)
    ``seq=01``-only-without-``req_atomic``, or Sig (c) layer-drift — reddens
    ``gz check`` on the next session. Surfacing it here lets the operator remediate
    *before* invoking ``gz obpi complete``.
    """
    errors = pending_obpi_task_envelope_errors(project_root, brief_path)
    if errors:
        return CheckResult(
            name="task_envelope_coherence",
            ok=False,
            message=" | ".join(e.message for e in errors),
            remediation=(
                "Subdivide labor via `uv run gz task start --seq next`, declare "
                "`req_atomic:` in the brief frontmatter (Sig b), attribute worklog "
                "events with a `task_id` (Sig a), or reconcile divergent TASK ids "
                "across channels (Sig c) — see `gz task envelope diagnose <OBPI>`."
            ),
        )
    return CheckResult(
        name="task_envelope_coherence",
        ok=True,
        message="No seq=01-only-without-req_atomic residue; completion will not reopen the gate.",
    )


def _check_operator_block(project_root: Path, obpi_id: str) -> CheckResult:
    """Refuse READY while ``obpi_id`` awaits an operator ruling (GHI #887).

    Reads Layer 2 rather than the pipeline marker's ``required_human_action`` key.
    ``ADR-0.0.9`` Rule 5, verbatim: *"Layer 3 artifacts cannot block gates. Only
    L1 (canon) and L2 (events) can be gate evidence."*

    The failure this closes is the licensing direction, the same one GHI #879
    recorded on the Step-4b verdict: an agent reads ``READY: all N preconditions
    met`` as authorization and solicits attestation. On ``OBPI-0.35.0-02`` four
    operator decisions were outstanding while the pipeline kept running, and
    nothing could say so.

    A missing or unreadable ledger passes. Absence of evidence is not a blocker —
    fabricating one would make the check unfalsifiable in a fresh project tree.
    """
    from gzkit.obpi_lifecycle import operator_block_state  # noqa: PLC0415

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    try:
        text = ledger_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return CheckResult(
            name="operator_block",
            ok=True,
            message="no ledger readable; no operator block recorded",
        )

    events: list[dict] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)

    entry = operator_block_state(events).get(obpi_id)
    if entry is None:
        return CheckResult(
            name="operator_block",
            ok=True,
            message="no outstanding operator ruling",
        )

    return CheckResult(
        name="operator_block",
        ok=False,
        message=(
            f"waiting on an operator ruling: {entry['reason']} "
            f"(action awaited: {entry['next_operator_action']})"
        ),
        remediation=(
            "Completion cannot be solicited while a named human decision is "
            "outstanding. Record the ruling with `uv run gz obpi unblock "
            f'{obpi_id} --ruling "<decision>" --operator "<who>"`, then re-run '
            "this check. If the ruling never lands, the honest state is blocked, "
            "not ready."
        ),
    )


def _render_human_report(obpi_id: str, checks: list[CheckResult]) -> None:
    """Render checklist with ✓/✗ markers + remediation hints."""
    console.print(f"\n[bold]Stage 5 precomplete check: {obpi_id}[/bold]\n")
    for check in checks:
        marker = "[green]✓[/green]" if check.ok else "[red]✗[/red]"
        console.print(f"  {marker} {check.name}: {escape(check.message)}")
        if not check.ok and check.remediation:
            console.print(f"      [dim]→ {check.remediation}[/dim]")
    failed = [c for c in checks if not c.ok]
    console.print()
    if failed:
        console.print(
            f"[red]BLOCKED: {len(failed)} of {len(checks)} preconditions not met. "
            f"Address remediations above before invoking `gz obpi complete`.[/red]"
        )
    else:
        console.print(
            f"[green]READY: all {len(checks)} preconditions met. "
            f"Safe to invoke `gz obpi complete {obpi_id}`.[/green]"
        )


__all__ = ["CheckResult", "obpi_precomplete_cmd"]
