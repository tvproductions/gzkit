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
import re
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict, Field
from rich.markup import escape

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


def _resolve_brief_path(project_root: Path, obpi_id: str) -> Path | None:
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


def _run_all_checks(project_root: Path, brief_path: Path, obpi_id: str) -> Iterable[CheckResult]:
    """Run every Stage 5 precondition check; yield each CheckResult in order."""
    yield _check_brief_readiness(project_root, brief_path)
    yield _check_reconcile_idempotent(project_root)
    yield _check_lock_held(project_root, obpi_id)
    yield _check_arb_receipts_present(project_root)
    yield _check_plan_audit_receipt(project_root, obpi_id)
    yield _check_brief_headings_scoped(project_root, brief_path)
    yield _check_behave_req_coverage_scoped(project_root, brief_path, obpi_id)
    yield _check_task_envelope_coherence(project_root, brief_path)
    yield _check_adversarial_validation(brief_path)
    yield _check_operator_block(project_root, obpi_id)
    yield _check_stage2_dispatch(project_root, obpi_id)


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


def _check_lock_held(project_root: Path, obpi_id: str) -> CheckResult:
    """OBPI lock MUST exist before `gz obpi complete` runs."""
    locks_dir = project_root / ".gzkit" / "locks" / "obpi"
    if not locks_dir.is_dir():
        return CheckResult(
            name="lock_held",
            ok=False,
            message="No .gzkit/locks/obpi/ directory",
            remediation=f"Run `uv run gz obpi lock claim {obpi_id}`.",
        )
    # The supplied id only: a lock claimed for a prefix sibling is a different
    # OBPI's claim, and honoring it hands two agents the same green light (#826).
    candidates = sorted(locks_dir.glob(f"{obpi_id}*.json"))
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


def _check_arb_receipts_present(project_root: Path) -> CheckResult:
    """ARB receipts (lint/typecheck/unittest) SHOULD be present for Heavy-lane attestation.

    Per AGENTS.md § Attestation, Heavy-lane attestation without inline
    receipt IDs is rejected. This check surfaces missing receipts before
    the operator drafts attestation text.
    """
    receipts_dir = project_root / "artifacts" / "receipts"
    if not receipts_dir.is_dir():
        return CheckResult(
            name="arb_receipts",
            ok=False,
            message="No artifacts/receipts/ directory",
            remediation=(
                "Run `uv run gz arb ruff` and "
                "`uv run gz arb step --name unittest -- uv run -m unittest -q` "
                "before drafting attestation."
            ),
        )
    arb_receipts = sorted(receipts_dir.glob("arb-*.json"), key=lambda p: p.stat().st_mtime)
    if not arb_receipts:
        return CheckResult(
            name="arb_receipts",
            ok=False,
            message="No ARB receipts found in artifacts/receipts/",
            remediation=(
                "Run `uv run gz arb ruff`, "
                "`uv run gz arb step --name unittest -- uv run -m unittest -q`, "
                "and `uv run gz arb step --name typecheck -- uv run gz typecheck`."
            ),
        )
    return CheckResult(
        name="arb_receipts",
        ok=True,
        message=f"{len(arb_receipts)} ARB receipt(s) present (newest: {arb_receipts[-1].name})",
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


# The Step-4b section ends at the next heading of the same or shallower depth.
# Bounding the verdict scan matters: every brief goes on to narrate the defect it
# fixed, and "a refuted claim could reach attestation" in a Value Narrative is
# prose about the past, not this OBPI's verdict.
_NEXT_HEADING_RE = re.compile(r"^#{2,3}\s+", re.MULTILINE)


# The two verdicts that must never read as clean, READ FROM THE CHOKEPOINT rather
# than restated here (GHI #959). Both layers now share one membership: the completion
# command blocks either verdict without a resolution, and this pre-flight puts the
# same pair in front of a human first.
#
# This was a literal set until 2026-09-04, and the copies had DIFFERENT membership --
# the pre-flight carried both verdicts while the fail-closed chokepoint tested only
# `refuted`, so Step 4b's "never hand the operator a known caveat dressed as clean"
# was enforced solely in the layer AGENTS.md calls "the bypassable pre-flight".
# Sourcing it is the same discipline `_verdict_vocabulary` already applies to
# `ADVERSARY_VERDICTS`, and for the reason that function names: a vocabulary
# maintained in two places is the two-copies-one-binds failure this repository
# keeps paying for.
def _refutation_verdicts() -> frozenset[str]:
    """Return the verdicts the completion chokepoint treats as refutations."""
    from gzkit.commands.obpi_complete_adversarial import (  # noqa: PLC0415
        REFUTATION_VERDICTS,
    )

    return REFUTATION_VERDICTS


def _verdict_pattern() -> re.Pattern[str]:
    r"""Compile a scanner over the completion command's own verdict vocabulary.

    Built from ``ADVERSARY_VERDICTS`` rather than a second literal list: a
    vocabulary maintained in two places is the two-copies-one-binds failure this
    repository keeps paying for, and the pre-flight must read exactly what the
    chokepoint accepts.

    Two independent guards stop `refuted` from matching inside `not-refuted` or
    `refuted-with-caveats`. Alternation is ordered longest-first because `re` takes
    the leftmost branch that matches, and the ``[\w-]`` lookaround pair refuses a
    token glued to another word by a letter or a hyphen. Either alone would close
    the hole; both are kept because a denial silently read as an assertion is the
    exact defect this check exists to stop.
    """
    alternatives = "|".join(sorted(_verdict_vocabulary(), key=len, reverse=True))
    return re.compile(rf"(?<![\w-])({alternatives})(?![\w-])", re.IGNORECASE)


def _verdict_vocabulary() -> tuple[str, ...]:
    """Return the verdicts `gz obpi complete --adversary-verdict` accepts, verbatim."""
    from gzkit.commands.obpi_complete_adversarial import (  # noqa: PLC0415
        ADVERSARY_VERDICTS,
    )

    return ADVERSARY_VERDICTS


# A brief declares which verdict STANDS; the check reads the declaration rather
# than inferring it from position. Emphasis is optional on either side of the
# label because briefs are hand-authored markdown.
#
# The declaration must OWN ITS LINE. A colon alone is not enough of a
# discriminator: OBPI-0.35.0-04 carries three round headings shaped
# `#### Round 12 - THE STANDING VERDICT: NOT-REFUTED, the acceptance round`, and a
# colon-only rule read all three as declarations, then refused the brief for
# declaring verdicts that "conflicted" -- a check inventing its own ambiguity out
# of ordinary prose. Anchoring to line start (and admitting only indentation,
# blockquote and list markers before the label, never `#`) separates a deliberate
# one-line declaration from a sentence that happens to use the words. Whitespace
# inside the pattern is `[ \t]` rather than `\s` for the same reason: a declaration
# is one line, so the label may not pair with a colon on a later one.
_STANDING_VERDICT_RE = re.compile(
    r"^[ \t>\-]*\*{0,2}[ \t]*standing[ \t]+verdict[ \t]*\*{0,2}[ \t]*:"
    r"[ \t]*\*{0,2}[ \t]*([\w-]+)",
    re.IGNORECASE | re.MULTILINE,
)


def _step_4b_section(text: str, step_4b_end: int) -> str:
    """Return the Step-4b section body, bounded by the next heading."""
    rest = text[step_4b_end:]
    next_heading = _NEXT_HEADING_RE.search(rest)
    return rest[: next_heading.start()] if next_heading else rest


def _step_4b_verdicts(text: str, step_4b_end: int) -> list[str]:
    """Return the verdict tokens recorded in the Step-4b section, in order."""
    section = _step_4b_section(text, step_4b_end)
    return [m.group(1).lower() for m in _verdict_pattern().finditer(section)]


def _declared_standing_verdicts(text: str, step_4b_end: int) -> list[str]:
    """Return every DECLARED standing verdict in the Step-4b section, in order.

    Returns the raw declared tokens -- including ones outside the vocabulary -- so
    the caller can refuse an unrecognized declaration rather than silently ignoring
    it. A declaration naming a non-verdict is a failed declaration, never an absent
    one: ignoring it would let ``**Standing verdict:** shipped`` fall through to the
    history scan and read as if nothing had been claimed.
    """
    section = _step_4b_section(text, step_4b_end)
    return [m.group(1).lower() for m in _STANDING_VERDICT_RE.finditer(section)]


def _check_adversarial_validation(brief_path: Path) -> CheckResult:
    """Heavy-lane briefs MUST record a Step-4b verdict that is not a refutation.

    Checks the brief, not the ledger: ``gz obpi complete`` writes the
    ``adversarial_validation`` event, so at precomplete time no such event can
    exist yet. The brief section is the pre-check; the ledger event is the durable
    receipt. Surfacing the gap here spares the operator a rejected completion.

    **The predicate is the recorded verdict, not the heading (GHI #879).** GHI #676
    landed this check as ``_STEP_4B_RE.search(text)`` — a heading match, to which a
    brief recording ``REFUTED`` and one recording ``NOT-REFUTED`` are the same input.
    It reported ``READY: all 10 preconditions met`` on ``OBPI-0.35.0-02``, whose
    section records ``REFUTED`` twice, and an agent read that as authorization to
    solicit attestation. AGENTS.md § PRIME DIRECTIVE names the shape: *"A PRESENCE
    CHECK ANSWERS 'is something armed', NEVER 'did the governed procedure run'."*
    The failure direction is what made it costly — it reported green, so it actively
    licensed the next step.

    What this check does NOT claim: which verdict is the STANDING one. Rounds are
    narrated in prose, and position is not the answer — ``OBPI-0.34.0-04`` opens with
    ``Verdict: NOT-REFUTED (SHIP)`` and then discusses six earlier refutations, so a
    last-token rule reads it backwards. So the check fails closed on a refutation
    APPEARING at all and says plainly that it cannot tell whether it stands. That is
    the honest direction for a pre-flight: it converts a green that licenses into a
    red that requires a human to read the section.

    **A refutation must be DISCHARGEABLE, not permanently blocking (GHI #964).** Under
    the GHI #960 loop doctrine a refutation is an INPUT to ``if(4a && 4b) pass; else
    loop``, so the normal shape of a converged Step 4b is a history of refuted rounds
    ending in a clean one — and failing on any refutation token made the pre-flight
    unpassable for exactly that shape. The escape is a DECLARATION the brief writes and
    this check reads (``**Standing verdict:** <verdict>``), never a position rule. Absent
    a declaration the fail-closed behavior above is unchanged, so nothing is weakened:
    a brief must SAY which verdict stands to get credit for it.

    The asymmetry with ``gz obpi complete`` is deliberate and preserved. This is the
    bypassable pre-flight; the chokepoint is ``_enforce_adversarial_validation``, which
    refuses EVERY refutation verdict regardless of resolution (GHI #960 removed the
    ``refuted`` + ``--adversary-resolution`` completion path this docstring once named).
    This check adds no new gate — it stops the pre-flight from reporting green about a
    state the chokepoint would refuse.
    """
    from gzkit.governance.trust_audits.adversarial_validation import (  # noqa: PLC0415
        _STEP_4B_RE,
    )
    from gzkit.governance.trust_audits.briefs import _LANE_IN_FRONTMATTER  # noqa: PLC0415

    try:
        text = brief_path.read_text(encoding="utf-8")
    except OSError as exc:
        return CheckResult(
            name="adversarial_validation",
            ok=False,
            message=f"brief unreadable: {exc}",
            remediation=f"Re-create or restore {brief_path.name}.",
        )

    lane_match = _LANE_IN_FRONTMATTER.search(text)
    if not lane_match or lane_match.group(1).lower() != "heavy":
        return CheckResult(
            name="adversarial_validation",
            ok=True,
            message="lite-lane brief; Step 4b evidence not required",
        )

    step_4b = _STEP_4B_RE.search(text)
    if not step_4b:
        return CheckResult(
            name="adversarial_validation",
            ok=False,
            message="heavy-lane brief carries no '### Step 4b' evidence section",
            remediation=(
                "Dispatch an independent adversary prompted to REFUTE the completion "
                "claim, then add a `### Step 4b — Independent Adversarial Validation` "
                "section naming the adversary, the verdict, the claim it broke, and "
                "how that was resolved. Pass the verdict to `gz obpi complete` via "
                "--adversary-verdict/--adversary so it lands in the ledger. If no "
                "adversary could run, record the degraded floor explicitly: "
                "--adversary-verdict degraded-human-only --adversary human."
            ),
        )

    verdicts = _step_4b_verdicts(text, step_4b.end())
    if not verdicts:
        return CheckResult(
            name="adversarial_validation",
            ok=False,
            message=(
                "Step 4b section records no recognized verdict "
                f"({', '.join(sorted(_verdict_vocabulary()))})"
            ),
            remediation=(
                "State the adversary's verdict in the Step 4b section using the same "
                "vocabulary `gz obpi complete --adversary-verdict` accepts. A section "
                "that names no verdict is indistinguishable from one that was never "
                "run, which is the gap Step 4b exists to close."
            ),
        )

    # A DECLARED standing verdict governs, in BOTH directions (GHI #964). It is read
    # before the history scan because that scan cannot distinguish a discharged round
    # from a live one -- which is precisely why the declaration exists.
    declared = _declared_standing_verdicts(text, step_4b.end())
    distinct = sorted(set(declared))
    if len(distinct) > 1:
        return CheckResult(
            name="adversarial_validation",
            ok=False,
            message=f"Step 4b declares conflicting standing verdicts: {', '.join(distinct)}",
            remediation=(
                "Leave exactly one `**Standing verdict:** <verdict>` line in the Step 4b "
                "section, naming the verdict of the round that STANDS. Two declarations "
                "that disagree are the ambiguity this check exists to refuse — resolving "
                "it by picking one would restore the position rule the check dropped."
            ),
        )
    if distinct:
        standing = distinct[0]
        if standing not in _verdict_vocabulary():
            return CheckResult(
                name="adversarial_validation",
                ok=False,
                message=f"Step 4b declares an unrecognized standing verdict '{standing}'",
                remediation=(
                    "Declare the standing verdict using the same vocabulary "
                    "`gz obpi complete --adversary-verdict` accepts "
                    f"({', '.join(sorted(_verdict_vocabulary()))}). A declaration naming "
                    "something else is a failed declaration, not an absent one, so it is "
                    "refused rather than ignored."
                ),
            )
        if standing in _refutation_verdicts():
            return CheckResult(
                name="adversarial_validation",
                ok=False,
                message=f"Step 4b declares standing verdict '{standing}'",
                remediation=(
                    "The brief declares that a REFUTATION stands. Return to Stage 2, fix "
                    "the refuted claim and re-run the adversary, then declare the verdict "
                    "that round returns. `gz obpi complete` refuses every refutation "
                    "verdict (GHI #960), so a standing refutation cannot be completed "
                    "past — it loops. A known refutation must never be handed to the "
                    "operator dressed as clean."
                ),
            )
        return CheckResult(
            name="adversarial_validation",
            ok=True,
            message=f"Step 4b declares standing verdict '{standing}'",
        )

    refutations = sorted({v for v in verdicts if v in _refutation_verdicts()})
    if refutations:
        return CheckResult(
            name="adversarial_validation",
            ok=False,
            message=f"Step 4b records {', '.join(refutations)}",
            remediation=(
                "Establish which verdict STANDS — this check cannot tell from prose, and "
                "position is not the answer. If a later round overturned the refutation, "
                "add one `**Standing verdict:** <verdict>` line to the Step 4b section "
                "naming that round's verdict; the historical refutation tokens may stay "
                "exactly as recorded. If the refutation still stands, return to Stage 2, "
                "fix the refuted claim and re-run the adversary — `gz obpi complete` "
                "refuses every refutation verdict (GHI #960), so complete on the verdict "
                "the passing round returns and cite the earlier rounds in "
                "--adversary-resolution as the record of what was found and discharged. "
                "A known refutation must never be handed to the operator dressed as clean."
            ),
        )

    return CheckResult(
        name="adversarial_validation",
        ok=True,
        message=f"Step 4b records {', '.join(sorted(set(verdicts)))}",
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
