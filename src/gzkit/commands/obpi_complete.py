"""Atomic OBPI completion command.

``gz obpi complete`` validates, writes evidence, flips status, records
attestation, and emits a completion receipt in a single all-or-nothing
transaction.  If any step fails, no files or ledger entries are modified.
"""

from __future__ import annotations

import contextlib
import json
import re
import secrets
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, NoReturn, cast

from gzkit.arb.paths import receipts_root
from gzkit.arb.validator import CANONICAL_STEP_COMMANDS
from gzkit.commands.adr_audit import (
    ATTESTATION_TYPE_HUMAN,
    ATTESTATION_TYPE_OPERATOR_VERBATIM,
    _enforce_uncovered_acceptance_confirmation,
    _requires_human_obpi_attestation,
)
from gzkit.commands.closeout_form import _upsert_frontmatter_value
from gzkit.commands.common import (
    GzCliError,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_obpi_file,
)
from gzkit.commands.validate_task_envelope import pending_obpi_task_envelope_errors
from gzkit.governance.req_coverage import (
    TestRef,
    discover_covers,
    parse_brief_req_kinds,
    parse_brief_reqs,
)
from gzkit.governance.trust_audits.attestation_receipts import (
    AttestationReceiptValidationResult,
    validate_attestation_receipts,
)
from gzkit.governance.trust_audits.sensitivity import (
    detect_brief_security_floor,
    detect_brief_security_surfaces,
)
from gzkit.hooks.obpi import section_body
from gzkit.ledger import (
    LEDGER_SCHEMA,
    Ledger,
    LedgerEvent,
    parse_frontmatter_value,
    resolve_adr_lane,
)

# section_body is used in _has_human_attestation_content for H2 section extraction
from gzkit.ledger_events import (
    audit_receipt_emitted_event,
    brief_reconcile_drift_overridden_event,
    obpi_completion_uncovered_accept_event,
    obpi_receipt_emitted_event,
    security_floor_overridden_event,
)
from gzkit.utils import capture_validation_anchor

# ---------------------------------------------------------------------------
# OBPI-0.0.22-05 — Gate 5 security walkthrough + ARB receipt gate
# ---------------------------------------------------------------------------

_SECURITY_RULE_RELATIVE_PATH = Path(".gzkit") / "rules" / "security-sensitivity.md"
_SECURITY_CHECKLIST_HEADING = re.compile(
    r"^\s*#{2,3}\s+walkthrough\s+checklist\s*$",
    re.IGNORECASE,
)
_SECURITY_RECEIPT_GLOB = "arb-step-security-*.json"
_SECURITY_RECEIPT_MAX_AGE_HOURS = 24


def _load_security_checklist(project_root: Path) -> list[str]:
    """Return the security walkthrough checklist parsed from the rule file.

    The checklist is enumerated in ``.gzkit/rules/security-sensitivity.md``
    (authored by OBPI-0.0.22-06). Per REQ-0.0.22-05-02 the list is read at
    runtime — never hardcoded into the OBPI command surface.
    """
    rule_path = project_root / _SECURITY_RULE_RELATIVE_PATH
    if not rule_path.is_file():
        msg = (
            f"Security checklist rule file missing: {_SECURITY_RULE_RELATIVE_PATH} "
            "(authored by OBPI-0.0.22-06). Land that OBPI before completing "
            "any sensitivity:security brief."
        )
        raise GzCliError(msg)

    text = rule_path.read_text(encoding="utf-8")
    items: list[str] = []
    in_section = False
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if _SECURITY_CHECKLIST_HEADING.match(line):
            in_section = True
            continue
        if in_section and line.lstrip().startswith("#"):
            break
        if in_section and line.lstrip().startswith("- "):
            items.append(line.lstrip()[2:].strip())
    return items


def _security_canonical_slot_filled() -> bool:
    """Return True when the ``security`` slot in CANONICAL_STEP_COMMANDS is non-empty."""
    return bool(CANONICAL_STEP_COMMANDS.get("security"))


def _find_fresh_security_receipt(
    receipts_dir: Path,
    *,
    max_age_hours: int = _SECURITY_RECEIPT_MAX_AGE_HOURS,
) -> tuple[Path | None, Path | None]:
    """Return (newest_receipt, fresh_receipt) for the security-scan stream.

    ``newest_receipt`` is the most recent ``arb-step-security-*.json`` regardless
    of age; ``fresh_receipt`` is the same receipt only when its
    ``timestamp_utc`` is within ``max_age_hours``. Either is ``None`` when no
    receipt exists or no fresh receipt exists, respectively.
    """
    if not receipts_dir.is_dir():
        return None, None
    candidates: list[tuple[datetime, Path]] = []
    for path in receipts_dir.glob(_SECURITY_RECEIPT_GLOB):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        ts = payload.get("timestamp_utc")
        if not isinstance(ts, str):
            continue
        try:
            created_at = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        except ValueError:
            continue
        candidates.append((created_at, path))
    if not candidates:
        return None, None
    candidates.sort(key=lambda item: item[0], reverse=True)
    newest_at, newest_path = candidates[0]
    threshold = datetime.now(UTC) - timedelta(hours=max_age_hours)
    fresh = newest_path if newest_at >= threshold else None
    return newest_path, fresh


def _render_security_walkthrough(
    *,
    obpi_id: str,
    parent_adr: str,
    checklist_items: list[str],
) -> None:
    """Render the security walkthrough panel ahead of the GHI #290 ATTEST gate."""
    console.print("")
    console.print("[bold yellow]=== Security Review Walkthrough (ADR-0.0.22) ===[/bold yellow]")
    console.print(f"  OBPI:        {obpi_id}")
    console.print(f"  Parent ADR:  {parent_adr}")
    console.print("  The following security review items must be confirmed:")
    for item in checklist_items:
        console.print(f"    - {item}")
    console.print("")


def _enforce_security_review_gate(
    *,
    obpi_id: str,
    parent_adr: str,
    project_root: Path,
    sensitivity: str | None,
    as_json: bool,
    accept_security_floor: str | None = None,
) -> None:
    """Enforce REQ-0.0.22-05-{01,02,04,05,06}.

    No-op when ``sensitivity`` is not ``"security"``. Otherwise:

    1. Fail-closed (exit 3) when the canonical security-scan slot in
       ``CANONICAL_STEP_COMMANDS`` is empty (REQ-0.0.22-05-04).
    2. Fail-closed (exit 3) when no ``arb-step-security-*`` receipt exists
       (REQ-0.0.22-05-05) — ``receipt-missing``.
    3. Fail-closed (exit 3) when the newest receipt is older than 24 hours
       (REQ-0.0.22-05-06) — ``receipt-stale``.
    4. Render the rule-file-derived checklist before the GHI #290 ATTEST
       gate runs (REQ-0.0.22-05-01).

    ``accept_security_floor`` (GHI #462) provides an operator escape when
    the canonical slot is structurally unfilled — auto-detect classified the
    brief security-sensitive on surface-overlap but the toolchain feature
    ADR (promoting ``pool.agentic-security-review``) has not yet landed to
    fill the slot. The operator passes a rationale string; the override is
    recorded in console output for audit trail. The receipt-missing and
    receipt-stale checks remain enforced (they only fire when the slot is
    filled), so this escape narrows only the slot-unfilled deadlock.

    ``_fail`` raises ``SystemExit``; this function therefore either returns
    normally (security checks passed and walkthrough rendered) or terminates
    the process via ``_fail``.
    """
    if sensitivity != "security":
        return

    if not _security_canonical_slot_filled():
        if accept_security_floor:
            console.print(
                "[yellow]⚠ Security-scan canonical slot unfilled; "
                f"--accept-security-floor override applied (GHI #462). Reason: "
                f"{accept_security_floor}[/yellow]"
            )
            return
        _fail(
            "Security-scan canonical slot in CANONICAL_STEP_COMMANDS is unfilled "
            f"for parent ADR {parent_adr}; the toolchain feature ADR (promoting "
            "pool.agentic-security-review) must fill it before sensitivity:security "
            "briefs can be completed. To override when the brief change is "
            "structurally defensive/additive and not actually security-relevant, "
            "pass --accept-security-floor 'REASON' (GHI #462).",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    arb_dir = receipts_root(project_root=project_root)
    newest, fresh = _find_fresh_security_receipt(arb_dir)
    if newest is None:
        _fail(
            f"receipt-missing: no arb-step-security-* receipt under {arb_dir}; "
            "sensitivity:security brief requires a fresh security-scan receipt "
            f"within {_SECURITY_RECEIPT_MAX_AGE_HOURS}h.",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    if fresh is None:
        # newest is narrowed to Path by the `if newest is None: _fail(...)` guard
        # above (_fail is NoReturn).
        stale_path = newest
        try:
            stale_payload = json.loads(stale_path.read_text(encoding="utf-8"))
            stale_ts = stale_payload.get("timestamp_utc", "<unknown>")
        except (OSError, json.JSONDecodeError):
            stale_ts = "<unknown>"
        _fail(
            f"receipt-stale: newest arb-step-security-* receipt {stale_path.name} "
            f"created {stale_ts} (> {_SECURITY_RECEIPT_MAX_AGE_HOURS}h old); "
            "re-run the canonical security-scan command and retry.",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    checklist = _load_security_checklist(project_root)
    _render_security_walkthrough(
        obpi_id=obpi_id,
        parent_adr=parent_adr,
        checklist_items=checklist,
    )


# ---------------------------------------------------------------------------
# OBPI-0.0.24-02 — Attestation receipt-binding gate
# ---------------------------------------------------------------------------


def _read_adr_kind(adr_file: Path) -> str:
    """Return the parent ADR's ``kind`` frontmatter value, lowercased.

    Defaults to ``"feature"`` when the field is missing — preserving the
    pre-ADR-0.0.17 behavior for any pre-kind-schema briefs still in flight.
    """
    if not adr_file.is_file():
        return "feature"
    content = adr_file.read_text(encoding="utf-8")
    raw = parse_frontmatter_value(content, "kind")
    if not raw:
        return "feature"
    return raw.strip().lower()


def _build_meta_receipt_evidence(
    *,
    obpi_id: str | None,
    parent_adr: str,
    parent_lane: str,
    parent_kind: str,
    result: AttestationReceiptValidationResult,
) -> dict[str, Any]:
    """Construct the evidence payload for the meta-receipt-bind ledger event.

    The ``run_id`` is a stable arb-step receipt-shape ID so downstream
    tooling can resolve it the same way every other receipt resolves.
    """
    run_id = f"arb-meta-receipt-bind-{secrets.token_hex(16)}"
    resolved_ids = [
        entry.run_id for entry in result.entries if entry.status == "resolved" and entry.run_id
    ]
    payload: dict[str, Any] = {
        "run_id": run_id,
        "claim": "attestation receipts resolved",
        "exit_status": 0,
        "resolved_receipt_ids": resolved_ids,
        "parent_adr": parent_adr,
        "parent_lane": parent_lane,
        "parent_kind": parent_kind,
    }
    if obpi_id is not None:
        payload["obpi_id"] = obpi_id
    return payload


def _enforce_attestation_receipt_gate(
    *,
    obpi_id: str | None,
    parent_adr: str,
    parent_lane: str,
    parent_kind: str,
    attestation_text: str,
    attestor: str,
    ledger: Ledger,
    project_root: Path,
    as_json: bool,
    dry_run: bool,
) -> list[str]:
    """Run the receipt-binding gate; emit meta-receipt-bind on success.

    Returns the receipt-IDs resolved into the ledger (empty when none were
    cited/resolved or on the dry-run / warn-only paths). The former ``ln:``
    proof-binding consumer of this list (GHI #599) was retired with the ``ln:``
    surface (ADR-0.0.69 / GHI #601); the resolved IDs now feed only the ledger.

    Behavior matrix (REQ-0.0.24-02-02..04):

    | Lane / Kind                       | Validator result | Outcome |
    |-----------------------------------|------------------|---------|
    | heavy / any                       | non-zero         | exit 3  |
    | any / foundation                  | non-zero         | exit 3  |
    | lite / non-foundation             | non-zero         | warning, proceed |
    | any                               | zero, no warn    | emit meta-receipt-bind |
    | lite / non-foundation             | zero, warn_only  | warning, proceed (no meta event) |

    The gate runs BEFORE the operator-verbatim attestation step; a
    mechanical-receipt failure short-circuits attestation recording (REQ-07
    in the brief, mechanism for REQ-02).
    """
    if dry_run:
        return []
    result = validate_attestation_receipts(
        attestation_text,
        lane=parent_lane,
        kind=parent_kind,
        project_root=project_root,
    )
    fail_closed = parent_lane.lower() == "heavy" or parent_kind.lower() == "foundation"

    if result.exit_code != 0:
        if fail_closed:
            failure_lines = [
                f"  - {entry.status}: {entry.message}" for entry in result.entries
            ] or ["  - (no resolvable receipts cited)"]
            detail = "\n".join(failure_lines)
            _fail(
                "Attestation receipt-binding gate failed (heavy/foundation policy).\n"
                f"{detail}\n"
                "Recovery: re-run the cited ARB commands and re-cite the resolved receipt IDs.",
                exit_code=3,
                as_json=as_json,
                obpi_id=obpi_id or parent_adr,
            )
        console.print(
            "[yellow]Warning:[/yellow] attestation receipt-binding produced unresolved "
            "citations on lite-non-foundation; proceeding (warn-only)."
        )
        return []

    if result.warn_only:
        console.print(
            "[yellow]Warning:[/yellow] no ARB receipts cited in attestation "
            "(lite-non-foundation policy)."
        )
        return []

    evidence = _build_meta_receipt_evidence(
        obpi_id=obpi_id,
        parent_adr=parent_adr,
        parent_lane=parent_lane,
        parent_kind=parent_kind,
        result=result,
    )
    meta_event = audit_receipt_emitted_event(
        adr_id=parent_adr,
        receipt_event="meta-receipt-bind",
        attestor=attestor,
        evidence=evidence,
    )
    ledger.append(meta_event)
    resolved = evidence.get("resolved_receipt_ids", [])
    return [r for r in resolved if isinstance(r, str)]


# ---------------------------------------------------------------------------
# OBPI-0.0.25-01 — REQ-coverage gate
# ---------------------------------------------------------------------------


def _qualified_to_unittest_target(ref: TestRef, project_root: Path) -> str | None:
    """Render a ``TestRef`` as a unittest dotted target.

    ``ref.qualified_name`` is ``ClassName.method_name`` or ``func_name`` from
    the AST scanner. The unittest runner needs ``module.path.ClassName.method``
    relative to the project root. Returns ``None`` when the file path falls
    outside ``project_root`` or cannot be expressed as a Python module.
    """
    try:
        rel = Path(ref.file_path).resolve().relative_to(project_root.resolve())
    except (ValueError, OSError):
        return None
    parts = list(rel.with_suffix("").parts)
    if not parts:
        return None
    module = ".".join(parts)
    return f"{module}.{ref.qualified_name}"


def _run_captured(cmd: list[str], *, cwd: str) -> subprocess.CompletedProcess[str]:
    """Run ``cmd`` capturing text output, tolerant of non-UTF-8 sub-process bytes.

    Decodes with ``errors="replace"`` so a covering-test sub-process that emits
    bytes outside UTF-8 (observed on Windows — GHI #534, ``invalid start byte
    0xa7``) cannot raise ``UnicodeDecodeError`` out of the reader path and abort
    completion. ``UnicodeDecodeError`` is a ``ValueError``, so the callers'
    ``(OSError, SubprocessError)`` guards would not otherwise catch it.
    """
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _behave_ref_passes(ref: TestRef, project_root: Path, req_id: str) -> bool:
    """Run the behave scenario tagged ``req_id`` and return True iff exit code is 0."""
    try:
        completed = _run_captured(
            ["uv", "run", "-m", "behave", ref.file_path, "--tags", f"@{req_id}", "--no-summary"],
            cwd=str(project_root),
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return completed.returncode == 0


def _any_covering_test_passes(refs: list[TestRef], project_root: Path, *, req_id: str) -> bool:
    """Return True iff at least one discovered covering test passes.

    Behave refs (``.feature`` file paths) are dispatched through
    ``_behave_ref_passes``; all other refs run under ``uv run -m unittest``.
    One green observation satisfies the REQ (REQ-0.0.25-01-06).
    """
    for ref in refs:
        if ref.file_path.endswith(".feature"):
            if _behave_ref_passes(ref, project_root, req_id):
                return True
            continue
        target = _qualified_to_unittest_target(ref, project_root)
        if target is None:
            continue
        try:
            completed = _run_captured(
                ["uv", "run", "-m", "unittest", target],
                cwd=str(project_root),
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if completed.returncode == 0:
            return True
    return False


def _reject_behavior_waivers(
    *,
    waivable: set[str],
    req_kinds: dict[str, str],
    obpi_id: str,
    as_json: bool,
) -> None:
    """Refuse to waive a BEHAVIOR REQ at the completion layer (GHI #537).

    ADR-0.0.59 makes the proof-channel mapping closed: BEHAVIOR's *only* channel is a
    ``@covers``-decorated test. ``gz validate --req-kind-discipline`` enforced that at
    brief-authoring time; nothing enforced it here, so a brief could tag a REQ
    ``[behavior]`` and then close it through the SUPPORT-shaped ``--accept-uncovered``
    channel with a prose rationale. ADR-0.0.59's own OBPI-05 did exactly that.

    An untagged REQ defaults to BEHAVIOR — otherwise omitting the tag would become the
    bypass that unlocks the waiver.
    """
    behavior = sorted(req for req in waivable if req_kinds.get(req, "BEHAVIOR") == "BEHAVIOR")
    if not behavior:
        return
    listed = ", ".join(behavior)
    _fail(
        f"Completion blocked: {listed} tagged [BEHAVIOR] and cannot be accepted-uncovered. "
        "BEHAVIOR's only proof channel is a `@covers`-decorated test (ADR-0.0.59 Decision; "
        "`.gzkit/rules/tests.md` REQ Scope Discipline) — a prose rationale cannot substitute "
        "for a test that never ran. SUPPORT and STRUCTURAL-FENCE REQs never reach this path: "
        "they are exempt from the coverage gate by proof channel, so `--accept-uncovered` has "
        "no REQ kind it may waive. Recovery: author the covering test and confirm with "
        "`uv run gz covers <OBPI-ID>`, or retag the REQ if its claim is not a code behavior.",
        exit_code=3,
        as_json=as_json,
        obpi_id=obpi_id,
    )


def _apply_uncovered_waivers(
    *,
    gaps: list[str],
    accept_uncovered: list[str],
    accept_uncovered_reason: list[str],
    req_kinds: dict[str, str],
    fail_closed: bool,
    obpi_id: str,
    parent_adr: str,
    attestor: str,
    attestor_present: bool,
    project_root: Path,
    as_json: bool,
    ledger: Any,
    sensitivity: str | None = None,
    parent_kind: str | None = None,
) -> list[str]:
    """Apply --accept-uncovered waivers to gaps; emit ledger events. Returns remaining gaps."""
    accepted_set = set(accept_uncovered)
    waivable = accepted_set & set(gaps)
    if not waivable:
        return [g for g in gaps if g not in accepted_set]
    # GHI #537: the kind gate precedes the lane gate. Waiving a BEHAVIOR REQ is
    # forbidden on every lane — it is a proof-channel rule, not a lane policy.
    _reject_behavior_waivers(
        waivable=waivable, req_kinds=req_kinds, obpi_id=obpi_id, as_json=as_json
    )
    if fail_closed:
        try:
            acceptance_type = _enforce_uncovered_acceptance_confirmation(
                obpi_id=obpi_id,
                parent_adr=parent_adr,
                req_ids=sorted(waivable),
                attestor=attestor,
                attestor_present=attestor_present,
                project_root=project_root,
                sensitivity=sensitivity,
                parent_kind=parent_kind,
            )
        except GzCliError as exc:
            _fail(str(exc), exit_code=3, as_json=as_json, obpi_id=obpi_id)
            return gaps  # unreachable; _fail raises SystemExit
    else:
        acceptance_type = "lite-auto"
    if ledger is not None:
        reason_map = {
            req: accept_uncovered_reason[i] if i < len(accept_uncovered_reason) else ""
            for i, req in enumerate(accept_uncovered)
        }
        for req in sorted(waivable):
            ledger.append(
                obpi_completion_uncovered_accept_event(
                    obpi_id=obpi_id,
                    req_id=req,
                    operator=attestor,
                    rationale=reason_map.get(req, ""),
                    acceptance_type=acceptance_type,
                )
            )
    return [g for g in gaps if g not in accepted_set]


def _enforce_req_coverage_gate(
    *,
    obpi_id: str | None,
    parent_adr: str,
    parent_lane: str,
    parent_kind: str,
    brief_path: Path,
    project_root: Path,
    as_json: bool,
    dry_run: bool,
    accept_uncovered: list[str] | None = None,
    accept_uncovered_reason: list[str] | None = None,
    attestor: str = "",
    attestor_present: bool = False,
    ledger: Any = None,
    sensitivity: str | None = None,
) -> None:
    """Refuse completion when any brief REQ has no passing covering test.

    Behavior matrix (REQ-0.0.25-01-02..04, mirrors the receipt-binding gate):

    | Lane / Kind                       | Coverage outcome | Outcome |
    |-----------------------------------|------------------|---------|
    | heavy / any                       | gap or red test  | exit 3  |
    | any / foundation                  | gap or red test  | exit 3  |
    | lite / non-foundation             | gap or red test  | warning, proceed |
    | any                               | all REQs green   | proceed |

    ``accept_uncovered`` (ADR-0.0.25-02) names REQ-IDs whose coverage gaps the
    operator explicitly waives. Heavy/foundation waivers require TTY+``ACCEPT``
    confirmation. Each waiver emits a ``obpi_completion_uncovered_accept`` ledger
    event. Only gap-REQs (no covering tests) can be waived; failing-cover REQs
    cannot.

    Runs AFTER the ADR-0.0.24 receipt-binding gate so a missing receipt
    short-circuits the (slower) test-discovery + scoped-run path
    (FAIL-CLOSED REQUIREMENT #11 in the brief acknowledges the ordering as
    parallel-or-sequential; sequential-after-receipt-binding is chosen for
    cost discipline).
    """
    if dry_run:
        return

    reqs = parse_brief_reqs(brief_path)
    # ADR-0.0.59 kind discipline: only BEHAVIOR REQs are proven by @covers. SUPPORT
    # (ledger event + structural validator) and STRUCTURAL-FENCE (parent-ADR Boundary
    # Invariants) REQs are exempt from the coverage requirement — requiring a test for
    # them is the named anti-pattern (.gzkit/rules/tests.md § REQ Scope Discipline).
    # Untagged (legacy) REQs default to BEHAVIOR, preserving prior behaviour.
    req_kinds = parse_brief_req_kinds(brief_path)
    tests_root = project_root / "tests"
    features_root = project_root / "features"
    gaps: list[str] = []
    failing: list[str] = []
    for req in reqs:
        if req_kinds.get(req, "BEHAVIOR") in ("SUPPORT", "STRUCTURAL-FENCE"):
            continue
        refs = discover_covers(req, tests_root, features_root=features_root)
        if not refs:
            gaps.append(req)
            continue
        if not _any_covering_test_passes(refs, project_root, req_id=req):
            failing.append(req)

    fail_closed = parent_lane.lower() == "heavy" or parent_kind.lower() == "foundation"

    # OBPI-0.0.25-02: process --accept-uncovered waivers before checking remaining gaps
    if accept_uncovered:
        gaps = _apply_uncovered_waivers(
            gaps=gaps,
            accept_uncovered=accept_uncovered,
            accept_uncovered_reason=accept_uncovered_reason or [],
            req_kinds=req_kinds,
            fail_closed=fail_closed,
            obpi_id=obpi_id or parent_adr,
            parent_adr=parent_adr,
            attestor=attestor,
            attestor_present=attestor_present,
            project_root=project_root,
            as_json=as_json,
            sensitivity=sensitivity,
            parent_kind=parent_kind,
            ledger=ledger,
        )

    if not gaps and not failing:
        return

    diagnostic_lines = [f"  - uncovered: {req}" for req in gaps]
    diagnostic_lines.extend(f"  - failing-cover: {req}" for req in failing)
    detail = "\n".join(diagnostic_lines)

    if fail_closed:
        _fail(
            "OBPI completion REQ-coverage gate failed (heavy/foundation policy).\n"
            f"{detail}\n"
            "Recovery: add a `@covers(REQ-X.Y.Z-NN-MM)` test for each gap, "
            "or fix the failing covering tests, then re-run completion.",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id or parent_adr,
        )
    console.print(
        "[yellow]Warning:[/yellow] REQ-coverage gate reported gaps "
        "(lite-non-foundation; warn-only):\n" + detail
    )


# ---------------------------------------------------------------------------
# OBPI-0.0.37-08 — Stage 5 reconcile-receipt fail-close gate
# ---------------------------------------------------------------------------

_RECONCILE_DRIFT_DIMENSIONS = (
    ("allowlist_delta_count", "allowlist"),
    ("discovery_delta_count", "discovery"),
    ("verification_delta_count", "verification"),
    ("req_count_delta", "req_count"),
    ("citation_delta_count", "citation"),
)


def _reconcile_drift_dimensions(event: dict[str, Any]) -> list[str]:
    """Return the names of drifted dimensions carried by a ``brief_reconciled`` event."""
    return [name for key, name in _RECONCILE_DRIFT_DIMENSIONS if event.get(key, 0)]


def _latest_reconcile_receipt(
    obpi_id: str, project_root: Path
) -> tuple[datetime | None, bool, list[str], str | None]:
    """Scan the ledger for the most recent ``brief_reconciled`` event for ``obpi_id``.

    Returns ``(latest_ts, has_drift, drifted_dims, receipt_id)``; ``latest_ts`` is
    ``None`` when no matching event exists.
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    latest_ts: datetime | None = None
    has_drift = False
    drifted_dims: list[str] = []
    receipt_id: str | None = None
    if not ledger_path.is_file():
        return latest_ts, has_drift, drifted_dims, receipt_id

    for raw in ledger_path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            event = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if event.get("event") != "brief_reconciled" or event.get("brief_id") != obpi_id:
            continue
        try:
            ts = datetime.fromisoformat(str(event.get("ts", "")).replace("Z", "+00:00"))
        except ValueError:
            continue
        if latest_ts is None or ts > latest_ts:
            latest_ts = ts
            has_drift = bool(event.get("has_drift", False))
            drifted_dims = _reconcile_drift_dimensions(event)
            receipt_id = event.get("id") or event.get("run_id")
    return latest_ts, has_drift, drifted_dims, receipt_id


def _enforce_reconcile_receipt_gate(
    *,
    obpi_id: str,
    brief_path: Path,
    project_root: Path,
    ledger: Ledger,
    attestor: str,
    as_json: bool,
    accept_stale_reconciliation: bool = False,
    accept_stale_reconciliation_reason: str | None = None,
) -> None:
    """Refuse Stage 5 completion when the reconciliation receipt is absent, stale, or drifted.

    Three failure modes (REQ-0.0.37-08-01/02/03):
    1. No ``brief_reconciled`` event for this OBPI → exit 3.
    2. Most recent receipt predates a mutation in the brief's allowed-path domain → exit 3.
    3. Receipt is fresh but ``has_drift`` payload is True → exit 3.

    Escape hatch (REQ-0.0.37-08-04/05): when ``accept_stale_reconciliation`` is True
    and ``accept_stale_reconciliation_reason`` is at least 10 characters, emit a
    ``brief_reconcile_drift_overridden`` ledger event and return (bypass the gate).
    """
    # Consume OBPI-07's canonical allowlist + drift helpers (read-only) so the
    # Stage 5 gate computes the SAME allowlist domain as the Stage 1 gate in
    # pipeline_runtime — one source, no silent Stage-1/Stage-5 divergence
    # (AGENTS.md § DO IT RIGHT 1a). Importing is a consume, not a modify, so it
    # respects the brief's Denied Paths boundary on pipeline_runtime.py.
    from gzkit.governance.reconcile_freshness import is_receipt_fresh  # noqa: PLC0415
    from gzkit.pipeline_runtime import (  # noqa: PLC0415
        _extract_brief_allowlist,
        _find_drifted_path,
    )

    # Pairing check: --accept-stale-reconciliation requires --reason (≥10 chars)
    if accept_stale_reconciliation and len((accept_stale_reconciliation_reason or "").strip()) < 10:
        _fail(
            "--accept-stale-reconciliation requires --reason '<text>' (minimum 10 characters).",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    latest_ts, has_drift, drifted_dims, latest_receipt_id = _latest_reconcile_receipt(
        obpi_id, project_root
    )

    # Apply escape hatch (overrides all three failure modes below)
    if accept_stale_reconciliation and accept_stale_reconciliation_reason:
        ledger.append(
            brief_reconcile_drift_overridden_event(
                brief_id=obpi_id,
                attestor=attestor,
                reason=accept_stale_reconciliation_reason,
                original_receipt_id=latest_receipt_id,
                original_drift_dimensions=drifted_dims,
            )
        )
        return

    # REQ-0.0.37-08-01: no receipt
    if latest_ts is None:
        _fail(
            f"Completion blocked: no `brief_reconciled` receipt for {obpi_id}. "
            f"Run `gz obpi brief-drift {obpi_id}` then retry.",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id,
        )
        return  # unreachable; _fail raises SystemExit

    # REQ-0.0.37-08-02: stale receipt
    allowed_paths = _extract_brief_allowlist(brief_path)
    if allowed_paths and not is_receipt_fresh(latest_ts, allowed_paths, project_root):
        drifted_path = _find_drifted_path(latest_ts, allowed_paths, project_root)
        _fail(
            f"Completion blocked: reconciliation receipt for {obpi_id} is stale "
            f"(receipt_ts={latest_ts.isoformat()}, drifted path={drifted_path!r}). "
            f"Run `gz obpi brief-drift {obpi_id}` to refresh.",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id,
        )
        return

    # REQ-0.0.37-08-03: fresh but drifted
    if has_drift:
        dims_str = ", ".join(drifted_dims) if drifted_dims else "unknown"
        _fail(
            f"Completion blocked: reconciliation receipt for {obpi_id} has_drift=True "
            f"(drifted dimensions: {dims_str}). "
            f"Run `gz obpi brief-drift {obpi_id}` to refresh.",
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id,
        )


def _resolve_and_validate(
    project_root: Path,
    config: Any,
    ledger: Ledger,
    obpi: str,
    as_json: bool,
) -> tuple[Path, str, str, str, str, bool, str | None]:
    """Resolve OBPI file and validate preconditions.

    Returns (obpi_file, obpi_id, original_content, resolved_parent, parent_lane,
    requires_human, effective_sensitivity).

    ``effective_sensitivity`` is the brief's declared ``sensitivity`` frontmatter
    value when present, falling back to the auto-detected floor from
    :func:`detect_brief_security_floor` (GHI #413). Both the security gate and
    the attestation matrix consume this value so completion enforces the same
    floor that ``audit_sensitivity_binding`` reports at validate time.
    """
    obpi_file, obpi_id = resolve_obpi_file(project_root, config, ledger, obpi)
    if not obpi_file.exists():
        _fail(f"Brief not found: {obpi_file}", exit_code=1, as_json=as_json, obpi_id=obpi_id)

    original_content = obpi_file.read_text(encoding="utf-8")
    current_status = (parse_frontmatter_value(original_content, "status") or "").strip().lower()
    if current_status == "completed":
        _fail("Brief is already Completed.", exit_code=1, as_json=as_json, obpi_id=obpi_id)

    # GHI #668 class-fix: `gz obpi complete` is a governed OBPI-status writer
    # (_build_completed_brief upserts `status: Completed`). Consult the shared
    # terminal rule so this primary verb refuses to promote a terminal
    # (withdrawn/superseded) OBPI — the GHI #348 clobber class — the same as the
    # reconcile chokepoint and the auto-fix path (ADR-0.31.0 Decision item 4).
    from gzkit.governance.frontmatter_coherence import obpi_status_is_terminal

    if obpi_status_is_terminal(current_status):
        _fail(
            f"Brief carries terminal OBPI status '{current_status}' (no outgoing "
            f"transition); refusing to complete it (GHI #348 clobber class). "
            f"Recover with `gz obpi repudiate` or correct the ledger, then re-run.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    graph = ledger.get_artifact_graph()
    obpi_info = graph.get(obpi_id, {})
    if obpi_info.get("type") != "obpi":
        _fail(f"OBPI not found in ledger: {obpi_id}", exit_code=1, as_json=as_json, obpi_id=obpi_id)
    if obpi_info.get("ledger_completed"):
        _fail(
            "OBPI is already completed in the ledger.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    parent_adr = cast(str | None, obpi_info.get("parent"))
    if not parent_adr:
        _fail(
            "OBPI is missing parent ADR in ledger.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    assert parent_adr is not None  # narrowing: _fail raises SystemExit
    if _is_pool_adr_id(parent_adr):
        _fail(
            f"Pool-linked OBPI cannot be completed: {obpi_id}",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    _adr_file, resolved_parent = resolve_adr_file(project_root, config, parent_adr)
    parent_lane = resolve_adr_lane(graph.get(resolved_parent, {}), config.mode)
    # ADR-0.0.22 third axis: a brief carrying ``sensitivity: security`` requires
    # attestation regardless of lane or kind via the OR in
    # ``_requires_human_obpi_attestation``. GHI #413: when the declaration is
    # absent, fall back to the registry-driven floor so completion enforces the
    # same auto-detect that ``audit_sensitivity_binding`` already reports.
    declared_sensitivity = parse_frontmatter_value(original_content, "sensitivity")
    detected_sensitivity = detect_brief_security_floor(original_content, project_root)
    effective_sensitivity = declared_sensitivity or detected_sensitivity
    brief_frontmatter = {"sensitivity": effective_sensitivity} if effective_sensitivity else None
    requires_human = _requires_human_obpi_attestation(
        resolved_parent, parent_lane, brief_frontmatter
    )
    return (
        obpi_file,
        obpi_id,
        original_content,
        resolved_parent,
        parent_lane,
        requires_human,
        effective_sensitivity,
    )


def _resolve_evidence(
    original_content: str,
    implementation_summary: str | None,
    key_proof: str | None,
    obpi_id: str,
    as_json: bool,
) -> tuple[str, str]:
    """Resolve evidence from flags or existing brief content.

    Returns (effective_summary, effective_proof).
    """
    effective_summary = implementation_summary or _read_existing_summary(original_content)
    effective_proof = key_proof or _read_existing_key_proof(original_content)

    if not effective_summary or not effective_summary.strip():
        _fail(
            "Implementation summary is required. Provide --implementation-summary "
            "or ensure the brief has a substantive ### Implementation Summary section.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    assert effective_summary is not None  # narrowing: _fail raises SystemExit
    if not effective_proof or not effective_proof.strip():
        _fail(
            "Key proof is required. Provide --key-proof "
            "or ensure the brief has a substantive ### Key Proof section.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    assert effective_proof is not None  # narrowing: _fail raises SystemExit
    return effective_summary, effective_proof


def _enforce_task_envelope_gate(
    *, obpi_file: Path, project_root: Path, as_json: bool, obpi_id: str
) -> None:
    """Fail-closed task-envelope-coherence chokepoint gate (GHI #590).

    Block completion of an OBPI that would land any ``task-envelope-coherence``
    residue — Sig (a) unattributed labor, Sig (b) seq=01-only-without-
    ``req_atomic``, or Sig (c) layer-drift — the generator of the recurring
    ``gz check`` reopenings. Enforcing all three in the state-mutating completion
    command (not only the bypassable ``gz obpi precomplete`` pre-flight) means the
    residue can never reach ``main`` on any agent's path. Same rules as
    ``gz validate --task-envelope-coherence``, scoped to this OBPI.
    """
    errors = pending_obpi_task_envelope_errors(project_root, obpi_file)
    if errors:
        _fail(
            " | ".join(e.message for e in errors),
            exit_code=3,
            as_json=as_json,
            obpi_id=obpi_id,
        )


def obpi_complete_cmd(
    obpi: str,
    attestor: str,
    attestation_text: str,
    implementation_summary: str | None,
    key_proof: str | None,
    as_json: bool,
    dry_run: bool,
    attestor_present: bool = False,
    accept_uncovered: list[str] | None = None,
    accept_uncovered_reason: list[str] | None = None,
    accept_security_floor: str | None = None,
    accept_stale_reconciliation: bool = False,
    accept_stale_reconciliation_reason: str | None = None,
    adversary_verdict: str | None = None,
    adversary: str | None = None,
    adversary_job_id: str | None = None,
    refuted_claim: str | None = None,
    adversary_resolution: str | None = None,
    adversary_fallback_reason: str | None = None,
) -> None:
    """Atomically complete an OBPI: validate, write evidence, flip status, emit receipt."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    # 1. Resolve & validate
    (
        obpi_file,
        obpi_id,
        original_content,
        resolved_parent,
        parent_lane,
        requires_human,
        effective_sensitivity,
    ) = _resolve_and_validate(project_root, config, ledger, obpi, as_json)

    # 1a. OBPI-0.0.37-08 Stage 5 reconcile-receipt gate: fail-closed on absent,
    # stale, or drifted brief_reconciled receipt. Skipped for --dry-run so
    # plans can be previewed headlessly.
    if not dry_run:
        _enforce_reconcile_receipt_gate(
            obpi_id=obpi_id,
            brief_path=obpi_file,
            project_root=project_root,
            ledger=ledger,
            attestor=attestor,
            as_json=as_json,
            accept_stale_reconciliation=accept_stale_reconciliation,
            accept_stale_reconciliation_reason=accept_stale_reconciliation_reason,
        )

    # 2. Resolve evidence
    effective_summary, effective_proof = _resolve_evidence(
        original_content,
        implementation_summary,
        key_proof,
        obpi_id,
        as_json,
    )

    # 3. Build would-be brief content
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    new_content = _build_completed_brief(
        content=original_content,
        attestor=attestor,
        attestation_text=attestation_text,
        implementation_summary=effective_summary,
        key_proof=effective_proof,
        date_completed=today,
    )

    # 4. Validate would-be content
    validation_errors = _validate_would_be_content(new_content, requires_human)
    if validation_errors:
        errors_text = "; ".join(validation_errors)
        _fail(
            f"Brief content validation failed: {errors_text}",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    # 4a. ADR-0.0.22 security gate: when the brief carries sensitivity:security
    # (declared OR auto-detected), enforce the canonical-slot, receipt-freshness
    # and rule-file-checklist contract before the GHI #290 ATTEST gate fires.
    # Skipped for --dry-run so plans can be previewed headlessly.
    if not dry_run:
        _enforce_security_review_gate(
            obpi_id=obpi_id,
            parent_adr=resolved_parent,
            project_root=project_root,
            sensitivity=effective_sensitivity,
            as_json=as_json,
            accept_security_floor=accept_security_floor,
        )

    # GHI #462: --accept-security-floor declares the auto-detect over-classified
    # the brief. Downgrade effective_sensitivity for downstream gates so the
    # attestor-present co-presence proxy is no longer refused, the security
    # walkthrough is skipped, and the receipt records sensitivity:absent.
    # The override is already recorded in console output by _enforce_security_review_gate.
    security_floor_override_event: LedgerEvent | None = None
    if accept_security_floor and effective_sensitivity == "security":
        # ADR-0.0.72-04: BUILD the override witness now (surfaces are computed
        # from the pre-downgrade brief); it is emitted AFTER the atomic
        # completion transaction commits — best-effort and structurally OUTSIDE
        # the rollback boundary — by _emit_security_floor_override_best_effort
        # below. Emitting here (or inside the transaction) would risk a phantom
        # record on a failed completion, a double-emit on retry, or gating an
        # already-committed completion; coupling the witness to the committed
        # receipt post-transaction avoids all three (brief REQ-04
        # "best-effort-after-completion ... NEVER a new gate"; Step-4b, Codex).
        overridden_surfaces = detect_brief_security_surfaces(original_content, project_root)
        security_floor_override_event = security_floor_overridden_event(
            obpi_id=obpi_id,
            surfaces=", ".join(overridden_surfaces) or "declared:security",
            reason=accept_security_floor,
            attestor=attestor,
        )
        effective_sensitivity = None
        # Recompute requires_human now that sensitivity is downgraded; the
        # caller's brief_frontmatter no longer carries security, so
        # heavy/foundation rules apply normally.
        brief_frontmatter_downgraded: dict[str, str] | None = None
        requires_human = _requires_human_obpi_attestation(
            resolved_parent, parent_lane, brief_frontmatter_downgraded
        )

    # 4a-bis. ADR-0.0.24-02 receipt-binding gate: heavy/foundation = fail-closed
    # on unresolvable ARB receipts; lite-non-foundation = warn-only. Runs
    # BEFORE the GHI #290 TTY gate so a mechanical-receipt failure short-
    # circuits human prompting (REQ-0.0.24-02-07, mechanism for REQ-02).
    adr_file_for_kind, _ = resolve_adr_file(project_root, config, resolved_parent)
    parent_kind = _read_adr_kind(adr_file_for_kind)
    _enforce_attestation_receipt_gate(
        obpi_id=obpi_id,
        parent_adr=resolved_parent,
        parent_lane=parent_lane,
        parent_kind=parent_kind,
        attestation_text=attestation_text,
        attestor=attestor,
        ledger=ledger,
        project_root=project_root,
        as_json=as_json,
        dry_run=dry_run,
    )

    # OBPI-0.0.25-02: validate --accept-uncovered pairing before the gate
    if accept_uncovered and not dry_run:
        if not accept_uncovered_reason:
            _fail(
                "--accept-uncovered requires --accept-uncovered-reason "
                "(one reason per waived REQ).",
                exit_code=1,
                as_json=as_json,
                obpi_id=obpi_id,
            )
        reasons_list: list[str] = accept_uncovered_reason or []
        if len(accept_uncovered) != len(reasons_list):
            _fail(
                f"--accept-uncovered and --accept-uncovered-reason counts must match "
                f"({len(accept_uncovered)} vs {len(reasons_list)}).",
                exit_code=1,
                as_json=as_json,
                obpi_id=obpi_id,
            )

    # 4a-ter. ADR-0.0.25-01 REQ-coverage gate: heavy/foundation = fail-closed
    # on any uncovered or failing-covered REQ; lite-non-foundation = warn-only.
    # ADR-0.0.25-02 adds --accept-uncovered override path with TTY gate and
    # ledger-event recording. Runs AFTER the receipt-binding gate (ADR-0.0.24).
    _enforce_req_coverage_gate(
        obpi_id=obpi_id,
        parent_adr=resolved_parent,
        parent_lane=parent_lane,
        parent_kind=parent_kind,
        brief_path=obpi_file,
        project_root=project_root,
        as_json=as_json,
        dry_run=dry_run,
        accept_uncovered=accept_uncovered,
        accept_uncovered_reason=accept_uncovered_reason,
        attestor=attestor,
        attestor_present=attestor_present,
        ledger=ledger,
        sensitivity=effective_sensitivity,
    )

    # 4a-quater. Task-envelope Signature-(b) chokepoint gate (GHI #590): mirror
    # of `gz validate --task-envelope-coherence` Sig (b), scoped to this OBPI and
    # enforced *before* the brief flips to Completed — so seq=01-only-without-
    # req_atomic residue can never reach main and reopen Tier 0 next session.
    _enforce_task_envelope_gate(
        obpi_file=obpi_file,
        project_root=project_root,
        as_json=as_json,
        obpi_id=obpi_id,
    )

    # 4b. Operator-verbatim conversational attestation. Per the canon-owner
    # declaration (operator verbatim, 2026-05-12 x2 + 2026-05-14: "WHEN I SAY
    # ATTEST COMPLETED IT IS MOTHERFUCKING COMPLETE - ALWAYS, ALWAYS, ALWAYS";
    # "MY WORD IS AUTHORITY IN ALL CASES"), the operator's verbatim attestation
    # relayed into this invocation via --attestation-text IS the Gate-5
    # attestation for every lane / kind / sensitivity. The prior TTY-typed
    # ATTEST authenticity gate (GHI #290/#292/#412) is no longer invoked;
    # _enforce_human_attestation_authenticity in adr_audit.py and its pipeline-
    # marker scaffolding are now unused and slated for removal under a separate
    # ADR. See AGENTS.md section "Lane & Kind & Sensitivity Attestation Matrix".
    # Skipped for --dry-run so plans can be previewed headlessly.
    attestation_type: str = ATTESTATION_TYPE_HUMAN
    if requires_human and not dry_run:
        if not attestation_text.strip():
            _fail(
                "Human attestation required for this OBPI: pass the operator's "
                "verbatim attestation via --attestation-text (e.g. "
                "'attest completed -- <evidence>'). The text is the attestation.",
                exit_code=1,
                as_json=as_json,
                obpi_id=obpi_id,
            )
        attestation_type = ATTESTATION_TYPE_OPERATOR_VERBATIM
        console.print(
            "[green]OK[/green] Operator-verbatim conversational attestation "
            "accepted (canon-owner declaration; AGENTS.md Attestation Matrix)."
        )

    # 5. Build audit ledger entry and receipt event
    adr_dir = obpi_file.parent.parent
    audit_entry = _build_attestation_audit_entry(
        obpi_id=obpi_id,
        adr_id=resolved_parent,
        attestor=attestor,
        attestation_text=attestation_text,
        date=today,
        requires_human=requires_human,
        attestation_type=attestation_type,
    )
    completion_term = "attested_completed" if requires_human else "completed"
    anchor = capture_validation_anchor(project_root, resolved_parent)
    evidence: dict[str, Any] = {
        "value_narrative": effective_summary[:500],
        "key_proof": effective_proof[:500],
        "parent_adr": resolved_parent,
        "parent_lane": parent_lane,
        "obpi_completion": completion_term,
        "attestation_requirement": "required" if requires_human else "optional",
    }
    if requires_human:
        evidence["human_attestation"] = True
        evidence["attestation_text"] = attestation_text
        evidence["attestation_date"] = today
        evidence["attestation_type"] = attestation_type

    receipt_event = obpi_receipt_emitted_event(
        obpi_id=obpi_id,
        receipt_event="completed",
        attestor=attestor,
        evidence=evidence,
        parent_adr=resolved_parent,
        obpi_completion=completion_term,
        anchor=anchor,
    )

    # Dry run
    if dry_run:
        _print_dry_run(
            obpi_id,
            resolved_parent,
            parent_lane,
            requires_human,
            completion_term,
            attestor,
            audit_entry,
            receipt_event,
            as_json,
        )
        return

    # 5c. GHI #676 Step-4b gate — the LAST gate before the write. Placed after the
    # structural gates (reconcile, REQ coverage, security floor) so those report
    # their own cause first: an operator with an uncovered REQ must hear about the
    # REQ, not the adversary. A --dry-run has already returned above; it writes
    # nothing, so it gates nothing.
    _enforce_adversarial_validation(
        obpi_id=obpi_id,
        parent_lane=parent_lane,
        verdict=adversary_verdict,
        adversary=adversary,
        resolution=adversary_resolution,
        as_json=as_json,
        fallback_reason=adversary_fallback_reason,
    )

    # 6-8. Execute atomic transaction
    adversarial_event = _build_adversarial_event(
        obpi_id=obpi_id,
        verdict=adversary_verdict,
        adversary=adversary,
        job_id=adversary_job_id,
        refuted_claim=refuted_claim,
        resolution=adversary_resolution,
    )
    try:
        _execute_transaction(
            obpi_file=obpi_file,
            original_content=original_content,
            new_content=new_content,
            adr_dir=adr_dir,
            audit_entry=audit_entry,
            ledger=ledger,
            receipt_event=receipt_event,
            adversarial_event=adversarial_event,
        )
    except OSError as exc:
        _fail(f"I/O error during completion: {exc}", exit_code=2, as_json=as_json, obpi_id=obpi_id)

    # ADR-0.0.72-04 / Step-4b (Codex, rounds 1-4): emit the override witness
    # AFTER the atomic transaction has committed — structurally OUTSIDE its
    # rollback boundary (like _surrender_lock_at_completion below). Only reached
    # on a committed completion (a failed transaction _fail-exits above), so it
    # can never be a phantom record; and being fully best-effort it can never
    # gate the completion nor revert a committed receipt (brief REQ-04 "NEVER a
    # new gate"). Under-records on failure, never over-records.
    _emit_security_floor_override_best_effort(ledger, security_floor_override_event)

    # Token-block exit edge (GHI #619): completion mechanically surrenders the
    # work lock and writes its register entry — no manual `gz obpi lock release`.
    # The observation report (GHI #764) is sourced from the brief the agent just
    # completed, so the record carries what the traversal learned without asking
    # the operator for anything the brief does not already hold.
    _surrender_lock_at_completion(
        project_root=project_root,
        ledger=ledger,
        obpi_id=obpi_id,
        attestor=attestor,
        attestation_text=attestation_text,
        implementation_summary=effective_summary,
        key_proof=effective_proof,
        commit_sha=anchor.commit,
        brief_rel_path=obpi_file.relative_to(project_root).as_posix(),
        observation=_read_observation(original_content),
        open_loops=_read_open_loops(original_content),
    )

    # Success output
    _print_success(obpi_id, resolved_parent, parent_lane, completion_term, attestor, as_json)


def _surrender_lock_at_completion(
    *,
    project_root: Path,
    ledger: Ledger,
    obpi_id: str,
    attestor: str,
    attestation_text: str,
    implementation_summary: str,
    key_proof: str,
    commit_sha: str,
    brief_rel_path: str,
    observation: str | None = None,
    open_loops: str | None = None,
) -> None:
    """Write the completion register entry and surrender any held work lock.

    The token-block exit edge (GHI #619): OBPI completion is a mechanical
    surrender. A full completion exchange record is written as the register entry,
    and if a lock is held it is deleted and an ``obpi_lock_released`` event is
    emitted citing that record — no operator prompt, no manual
    ``gz obpi lock release`` chore. Best-effort and fail-safe: if the register entry
    cannot be written the lock is left for TTL reaping rather than surrendered
    without one (token-block discipline § Sub-Invariant 5). Runs after the atomic
    transaction has committed, so it never affects completion's all-or-nothing
    guarantee.

    ``observation`` and ``open_loops`` carry the observation report half of the
    exchange record (GHI #764) and are optional on the same terms as everything
    else here: absent, the writer falls back to boilerplate and surrender still
    happens. The caller sources them from the brief's own ``### Value Narrative``
    and ``## Tracked Defects``, so the normal path needs no new operator input.
    """
    from gzkit.exchange_records import write_completion_exchange  # noqa: PLC0415
    from gzkit.ledger_events import obpi_lock_released_event  # noqa: PLC0415
    from gzkit.lock_manager import (  # noqa: PLC0415
        current_branch,
        delete_lock,
        read_lock,
        resolve_agent,
    )

    agent = resolve_agent(None)
    held = read_lock(project_root, obpi_id)
    try:
        handoff_path = write_completion_exchange(
            project_root,
            obpi_id=obpi_id,
            agent=agent,
            attestor=attestor,
            attestation_text=attestation_text,
            implementation_summary=implementation_summary,
            key_proof=key_proof,
            last_lock_event_timestamp=held.claimed_at if held is not None else None,
            commit_sha=commit_sha,
            branch=current_branch(),
            brief_rel_path=brief_rel_path,
            observation=observation,
            open_loops=open_loops,
        )
    except OSError:
        return
    if held is not None:
        delete_lock(project_root, obpi_id)
        ledger.append(
            obpi_lock_released_event(
                obpi_id=obpi_id,
                agent=agent,
                force=False,
                handoff_path=handoff_path.relative_to(project_root).as_posix(),
            )
        )


def _print_dry_run(
    obpi_id: str,
    resolved_parent: str,
    parent_lane: str,
    requires_human: bool,
    completion_term: str,
    attestor: str,
    audit_entry: dict[str, Any],
    receipt_event: Any,
    as_json: bool,
) -> None:
    """Print dry-run plan."""
    if as_json:
        print(
            json.dumps(
                {
                    "status": "dry_run",
                    "obpi_id": obpi_id,
                    "parent_adr": resolved_parent,
                    "lane": parent_lane,
                    "requires_human_attestation": requires_human,
                    "completion_term": completion_term,
                    "attestor": attestor,
                    "audit_entry": audit_entry,
                    "receipt_event": receipt_event.model_dump(),
                }
            )
        )
    else:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  OBPI: {obpi_id}")
        console.print(f"  Parent ADR: {resolved_parent}")
        console.print(f"  Lane: {parent_lane}")
        console.print(f"  Attestor: {attestor}")
        console.print(f"  Completion: {completion_term}")
        if requires_human:
            console.print(
                "  [green]Gate 5:[/green] live run accepts the operator-verbatim "
                "attestation passed via --attestation-text as the human "
                "attestation (canon-owner declaration; AGENTS.md Attestation "
                "Matrix). No interactive TTY is required."
            )


def _print_success(
    obpi_id: str,
    resolved_parent: str,
    parent_lane: str,
    completion_term: str,
    attestor: str,
    as_json: bool,
) -> None:
    """Print success output."""
    if as_json:
        print(
            json.dumps(
                {
                    "status": "completed",
                    "obpi_id": obpi_id,
                    "parent_adr": resolved_parent,
                    "completion_term": completion_term,
                    "attestor": attestor,
                }
            )
        )
    else:
        console.print(f"[green]Completed:[/green] {obpi_id}")
        console.print(f"  Parent ADR: {resolved_parent}")
        console.print(f"  Lane: {parent_lane}")
        console.print(f"  Attestor: {attestor}")
        console.print(f"  Completion: {completion_term}")


# ---------------------------------------------------------------------------
# Transaction execution with rollback
# ---------------------------------------------------------------------------


def _emit_security_floor_override_best_effort(
    ledger: Ledger,
    event: LedgerEvent | None,
) -> None:
    """Append the ``security_floor_overridden`` witness (ADR-0.0.72-04), best-effort.

    Runs AFTER the atomic completion transaction has committed and OUTSIDE its
    rollback boundary, so — mirroring :func:`_surrender_lock_at_completion` — it
    can never affect completion's all-or-nothing guarantee. Both the append AND
    its failure-warning are non-throwing: a failed emission is swallowed so it can
    NEVER gate the completion or revert a committed receipt (brief REQ-04 "a
    failed emission is a defect to fix, NEVER a new gate"; Step-4b rounds 1-4,
    Codex). It under-records on failure, never over-records or leaves a phantom.
    """
    if event is None:
        return
    try:
        ledger.append(event)
    except (OSError, ValueError):
        # The warning path must itself be non-throwing (a console backed by a
        # closed stream raises ValueError) — Step-4b round 4, Codex.
        with contextlib.suppress(OSError, ValueError):
            console.print(
                "[yellow]warning: security_floor_overridden ledger emission failed "
                "(best-effort; the --accept-security-floor override still applied and "
                "the completion committed). Re-run a ledger census if you need the "
                "override record.[/yellow]"
            )


def _execute_transaction(
    *,
    obpi_file: Path,
    original_content: str,
    new_content: str,
    adr_dir: Path,
    audit_entry: dict[str, Any],
    ledger: Ledger,
    receipt_event: Any,
    adversarial_event: LedgerEvent | None = None,
) -> None:
    """Execute the three-phase write with rollback on failure.

    Order: audit ledger -> brief file -> main ledger.
    The audit ledger must be written first because the obpi-completion-validator
    hook checks it before allowing the brief status change.
    """
    audit_ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"
    audit_written = False

    try:
        # Phase 1: Write attestation to ADR-local audit ledger
        _append_audit_ledger(adr_dir, audit_entry)
        audit_written = True

        # Phase 2: Write brief file (single atomic write)
        obpi_file.write_text(new_content, encoding="utf-8")

        # Phase 3: Emit receipt to main ledger. The Step-4b verdict lands FIRST
        # (GHI #676) so a completion receipt can never exist in the ledger without
        # the adversarial finding that gated it.
        if adversarial_event is not None:
            ledger.append(adversarial_event)
        ledger.append(receipt_event)

        # Phase 4: Auto-complete in_progress TASKs tied to this OBPI
        # (GHI #552 layer 4 — TASK auto-coordination at completion).
        # Mirrors the auto-start at pipeline launch; closes the per-REQ
        # execution witnesses without requiring manual `gz task complete`.
        from gzkit.commands.task import auto_complete_obpi_tasks  # noqa: PLC0415

        obpi_id_str = receipt_event.id if hasattr(receipt_event, "id") else ""
        parent_adr_str = receipt_event.parent if hasattr(receipt_event, "parent") else ""
        if obpi_id_str and parent_adr_str:
            auto_complete_obpi_tasks(
                ledger,
                obpi_id=obpi_id_str,
                parent_adr=parent_adr_str,
            )

    except Exception:
        # Rollback: restore brief if it was changed
        if obpi_file.read_text(encoding="utf-8") != original_content:
            obpi_file.write_text(original_content, encoding="utf-8")

        # Rollback: remove audit ledger entry if it was written
        if audit_written:
            _rollback_audit_ledger(audit_ledger_file)

        raise


# ---------------------------------------------------------------------------
# Brief content builders
# ---------------------------------------------------------------------------


def _extract_h3_body(content: str, heading: str) -> str | None:
    """Extract the body of an H3 section with correct H2/H3 boundaries."""
    pattern = (
        rf"^### {re.escape(heading)}\s*$"
        rf"([\s\S]*?)"
        rf"(?=^#{{2,3}} |\n---|\Z)"
    )
    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        return None
    body = match.group(1).strip()
    return body if body else None


def _read_existing_summary(content: str) -> str | None:
    """Read existing Implementation Summary from the brief."""
    body = _extract_h3_body(content, "Implementation Summary")
    if body is None:
        return None
    # Check if it's just template placeholders
    lines = [line.strip() for line in body.splitlines() if line.strip() and line.strip() != "-"]
    substantive = [line for line in lines if not _is_placeholder(line)]
    return body if substantive else None


def _read_existing_key_proof(content: str) -> str | None:
    """Read existing Key Proof from the brief."""
    body = _extract_h3_body(content, "Key Proof")
    if body is None:
        return None
    if _is_placeholder(body):
        return None
    return body


def _read_observation(content: str) -> str | None:
    """Read the brief's ``### Value Narrative`` as the traversal's observation report.

    This is where the completing agent already writes what the traversal learned
    about the block — the before/after, the constraint discovered, the approach
    rejected. It had no channel into the exchange record, so that record's
    ``## Important Context`` emitted boilerplate byte-identical across all 33
    mechanically-written records (GHI #764).

    Returns ``None`` when the section is absent or holds only scaffold prose. That
    is a real case, not a defensive branch: 116 of 368 briefs carrying the section
    write their narrative *inside* the HTML scaffold comment, which
    ``_sanitize_exchange_text`` strips by design so a prompt is never carried inward
    as content. Those degrade to the prior boilerplate rather than to an empty
    section.
    """
    body = _extract_h3_body(content, "Value Narrative")
    if body is None or _is_placeholder(body):
        return None
    return body


def _read_open_loops(content: str) -> str | None:
    """Read the brief's ``## Tracked Defects`` as the residual left for the next occupant.

    An H2 section, so it does not go through :func:`_extract_h3_body`. This is the
    prospective content ``## Pending Work / Open Loops`` exists to carry; before
    GHI #764 that section held the *implementation summary*, which is retrospective
    — the writer had retrospective content and a prospective schema and placed it
    where it fit rather than where it belonged.
    """
    match = re.search(
        r"^## Tracked Defects\s*$([\s\S]*?)(?=^## |\n---|\Z)",
        content,
        flags=re.MULTILINE,
    )
    if match is None:
        return None
    body = match.group(1).strip()
    if not body or _is_placeholder(body):
        return None
    return body


_PLACEHOLDERS = {
    "tbd",
    "todo",
    "...",
    "none",
    "(none)",
    "-",
    "n/a",
    "paste test output here",
    "paste lint/format/type check output here",
    "one-sentence concrete outcome",
    "<name>",
}


def _is_placeholder(text: str) -> bool:
    """Return True if text is a non-substantive placeholder."""
    clean = text.strip().lower()
    if not clean:
        return True
    if clean in _PLACEHOLDERS:
        return True
    # Template bullet patterns: full-line "- Label:" or extracted label "Label:"
    if re.match(r"^-\s+\w[^:]*:\s*$", clean):
        return True
    # Label-only text ending in colon with no value (from bullet value extraction)
    if re.match(r"^[\w][\w\s/]*:\s*$", clean):
        return True
    # HTML comments are placeholders
    return clean.startswith("<!--") and clean.endswith("-->")


def _build_completed_brief(
    *,
    content: str,
    attestor: str,
    attestation_text: str,
    implementation_summary: str,
    key_proof: str,
    date_completed: str,
) -> str:
    """Build the full completed brief content with all sections updated."""
    # 1. Update frontmatter status
    result = _upsert_frontmatter_value(content, "status", "Completed")

    # 2. Replace ### Implementation Summary section
    result = _replace_h3_section(
        result,
        "Implementation Summary",
        implementation_summary,
    )

    # 3. Replace ### Key Proof section
    result = _replace_h3_section(result, "Key Proof", key_proof)

    # 4. Update ## Human Attestation section
    result = _update_human_attestation(result, attestor, attestation_text, date_completed)

    # 5. Update **Status:** line
    result = re.sub(
        r"\*\*Status:\*\*\s*\S+",
        "**Status:** Completed",
        result,
    )

    # 6. Update **Date Completed:** line
    result = re.sub(
        r"\*\*Date Completed:\*\*\s*\S+",
        f"**Date Completed:** {date_completed}",
        result,
    )

    return result


def _replace_h3_section(content: str, heading: str, new_body: str) -> str:
    """Replace the body of an H3 section, preserving the heading.

    Stops at the next H2 or H3 heading, a horizontal rule (---), or EOF.
    """
    pattern = (
        rf"(^### {re.escape(heading)}\s*$)"
        rf"([\s\S]*?)"
        rf"(?=^#{{2,3}} |\n---|\Z)"
    )
    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        return content

    replacement = f"{match.group(1)}\n\n{new_body.strip()}\n\n"
    return content[: match.start()] + replacement + content[match.end() :]


def _update_human_attestation(content: str, attestor: str, attestation_text: str, date: str) -> str:
    """Update the Human Attestation section values (GHI #479)."""
    # Locate the ## Human Attestation section so substitutions are scoped to
    # its body only — a global count=1 match clobbers the first ^- Attestation:
    # bullet it finds, which may be inside ## Implementation Summary.
    section_pattern = (
        r"(^## Human Attestation\s*$)"
        r"([\s\S]*?)"
        r"(?=^## |\n---|\Z)"
    )
    section_match = re.search(section_pattern, content, flags=re.MULTILINE)
    if not section_match:
        return content

    before = content[: section_match.start(2)]
    body = section_match.group(2)
    after = content[section_match.end(2) :]

    body = re.sub(r"(^- Attestor:\s*).*$", rf"\g<1>`{attestor}`", body, count=1, flags=re.MULTILINE)
    body = re.sub(
        r"(^- Attestation:\s*).*$", rf"\g<1>{attestation_text}", body, count=1, flags=re.MULTILINE
    )
    body = re.sub(r"(^- Date:\s*).*$", rf"\g<1>{date}", body, count=1, flags=re.MULTILINE)
    return before + body + after


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_would_be_content(content: str, requires_human: bool) -> list[str]:
    """Validate the would-be brief content matches completion requirements.

    Mirrors the checks in obpi-completion-validator.py hook.
    """
    errors: list[str] = []

    if not _has_substantive_implementation_summary(content):
        errors.append("Missing or non-substantive Implementation Summary")

    if not _has_substantive_key_proof(content):
        errors.append("Missing or non-substantive Key Proof")

    if requires_human and not _has_human_attestation_content(content):
        errors.append("Missing human attestation content")

    return errors


def _has_substantive_implementation_summary(content: str) -> bool:
    """Check for substantive Implementation Summary (mirrors hook check)."""
    match = re.search(
        r"^### Implementation Summary\s*$([\s\S]*?)(?:^#{2,3} |\n---|\Z)",
        content,
        flags=re.MULTILINE,
    )
    if not match:
        return False
    section = match.group(1)
    # Primary: "- Key: value" bullets with actual content after the colon
    bullets = re.findall(r"^- [^:\n]+:[ \t]*(.+)$", section, flags=re.MULTILINE)
    if not bullets:
        # Fallback: plain "- text" bullets
        bullets = re.findall(r"^- \s*(.+)$", section, flags=re.MULTILINE)
    return any(not _is_placeholder(b) for b in bullets)


def _has_substantive_key_proof(content: str) -> bool:
    """Check for substantive Key Proof (mirrors hook check)."""
    for heading in ("Key Proof", "Verification", "Gate Evidence"):
        match = re.search(
            rf"^### {re.escape(heading)}\s*$([\s\S]*?)(?:^#{{2,3}} |\n---|\Z)",
            content,
            flags=re.MULTILINE,
        )
        if match:
            body = match.group(1).strip()
            if body and not _is_placeholder(body):
                return True
    return False


def _has_human_attestation_content(content: str) -> bool:
    """Check for substantive Human Attestation section.

    Validates all three required fields (GHI-126):
    - Attestor: non-placeholder name
    - Attestation: substantive text
    - Date: ISO 8601 date (YYYY-MM-DD)
    """
    body = section_body(content, "Human Attestation")
    if body is None:
        return False
    attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
    if not attestor_match:
        return False
    attestor_val = attestor_match.group(1).strip().strip("`")
    if not attestor_val or attestor_val.lower() in _PLACEHOLDERS:
        return False
    attestation_match = re.search(r"^- Attestation:\s*(.+)$", body, flags=re.MULTILINE)
    if not attestation_match:
        return False
    attestation_val = attestation_match.group(1).strip()
    if not attestation_val or attestation_val.lower() in _PLACEHOLDERS:
        return False
    date_match = re.search(r"^- Date:\s*`?(\d{4}-\d{2}-\d{2})`?$", body, flags=re.MULTILINE)
    return bool(date_match)


# ---------------------------------------------------------------------------
# Audit ledger operations
# ---------------------------------------------------------------------------


def _build_attestation_audit_entry(
    *,
    obpi_id: str,
    adr_id: str,
    attestor: str,
    attestation_text: str,
    date: str,
    requires_human: bool,
    attestation_type: str = ATTESTATION_TYPE_HUMAN,
) -> dict[str, Any]:
    """Build the ADR-local audit ledger entry for attestation.

    ``attestation_type`` is the value resolved by the GHI #290 authenticity
    gate: ``human`` (TTY+ATTEST) or ``agent-relayed-operator-attestation``
    (GHI #292 --attestor-present). Ignored when ``requires_human`` is False;
    self-close paths always record ``self-close-exception``.
    """
    entry: dict[str, Any] = {
        "type": "obpi-audit",
        "timestamp": datetime.now(UTC).isoformat(),
        "obpi_id": obpi_id,
        "adr_id": adr_id,
        "attestation_type": attestation_type if requires_human else "self-close-exception",
        "evidence": {
            "human_attestation": requires_human,
            "attestation_text": attestation_text,
            "attestation_date": date,
        },
        "action_taken": "attestation_recorded",
        "agent": "cli:obpi-complete",
    }
    return entry


def _append_audit_ledger(adr_dir: Path, entry: dict[str, Any]) -> None:
    """Append an entry to the ADR-local JSONL audit ledger."""
    logs_dir = adr_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ledger_file = logs_dir / "obpi-audit.jsonl"
    with ledger_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def _rollback_audit_ledger(ledger_file: Path) -> None:
    """Remove the last line from the audit ledger (rollback the last append)."""
    if not ledger_file.exists():
        return
    lines = ledger_file.read_text(encoding="utf-8").splitlines()
    if lines:
        ledger_file.write_text("\n".join(lines[:-1]) + "\n" if lines[:-1] else "", encoding="utf-8")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


ADVERSARY_VERDICTS: tuple[str, ...] = (
    "refuted",
    "not-refuted",
    "refuted-with-caveats",
    "degraded-human-only",
)

# Step-4b tier order (GHI #678). Codex (a different vendor) is REQUIRED first
# because a Claude validating Claude shares this agent's blind spots — the exact
# failure 4b exists to break. A named non-Claude vendor is proof of the cross-vendor
# tier-1 property; the set is an explicit allowlist so an unrecognized adversary
# fails CLOSED (must justify the fallback) rather than passing by ambiguity.
_CROSS_VENDOR_ADVERSARY_PREFIXES: tuple[str, ...] = (
    "codex",
    "gpt",
    "openai",
    "gemini",
    "google",
    "grok",
    "xai",
    "llama",
    "meta",
    "mistral",
    "deepseek",
    "qwen",
)


def _is_cross_vendor_adversary(adversary: str) -> bool:
    """Return True when the adversary names a different-vendor (non-Claude) model.

    Cross-vendor is the tier-1 property Step 4b requires: it shares none of this
    agent's blind spots. Detection is an explicit allowlist of vendor prefixes —
    an unrecognized name is treated as NOT cross-vendor so the gate fails closed
    (the caller must justify why Codex was unavailable), never open by ambiguity.
    """
    name = adversary.strip().lower()
    return any(name.startswith(prefix) for prefix in _CROSS_VENDOR_ADVERSARY_PREFIXES)


def _build_adversarial_event(
    *,
    obpi_id: str,
    verdict: str | None,
    adversary: str | None,
    job_id: str | None,
    refuted_claim: str | None,
    resolution: str | None,
) -> LedgerEvent | None:
    """Render the Step-4b verdict as an ``adversarial_validation`` ledger event.

    Returns ``None`` when no verdict was supplied — the lite lane, where the gate
    does not fire. Optional detail fields are omitted rather than emitted as null,
    matching ``_EventBase._serialize``.
    """
    if not verdict or not adversary:
        return None
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "schema": LEDGER_SCHEMA,
        "event": "adversarial_validation",
        "id": f"ADV-{obpi_id}-{now.strftime('%Y%m%dT%H%M%SZ')}",
        "ts": now.isoformat(),
        "obpi_id": obpi_id,
        "verdict": verdict,
        "adversary": adversary,
    }
    for key, value in (
        ("job_id", job_id),
        ("refuted_claim", refuted_claim),
        ("resolution", resolution),
    ):
        if value:
            payload[key] = value
    return LedgerEvent.model_validate(payload)


def _enforce_adversarial_validation(
    *,
    obpi_id: str,
    parent_lane: str,
    verdict: str | None,
    adversary: str | None,
    resolution: str | None,
    as_json: bool,
    fallback_reason: str | None = None,
) -> None:
    """Fail closed unless Step 4b's adversary verdict is recorded (GHI #676).

    Step 4b is already a fail-closed gate in the pipeline skill: no OBPI reaches
    attestation without an independent adversary re-deriving the completion claim
    under instruction to REFUTE. Nothing enforced it at the chokepoint, so an agent
    that skipped 4b and one that was refuted and attested anyway left indistinguishable
    durable records — the verdict lived only in a transcript or a vendor cache.

    Heavy lane only, matching the lane that already carries fail-closed Gate 3/4.
    A ``refuted`` verdict with no recorded resolution is itself blocking: a known
    refutation must never be handed to the operator dressed as clean.
    """
    if parent_lane.lower() != "heavy":
        return

    if not verdict or not adversary:
        _fail(
            "Completion blocked: Step 4b independent adversarial validation is not "
            f"recorded for {obpi_id}. The heavy lane forbids attestation on evidence "
            "the authoring agent produced alone (GHI #643/#676) — an adversary "
            "prompted to REFUTE must re-derive the completion claim, and its verdict "
            "must land in the ledger, not a transcript. Re-run with "
            "--adversary-verdict <" + "|".join(ADVERSARY_VERDICTS) + "> "
            "--adversary <vendor/model>. If neither a different-vendor adversary nor "
            "an independent subagent could run, record the degraded floor explicitly: "
            "--adversary-verdict degraded-human-only --adversary human.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    if verdict == "refuted" and not resolution:
        _fail(
            f"Completion blocked: the adversary refuted {obpi_id} and no resolution is "
            "recorded. A known refutation must never be handed to the operator dressed "
            "as clean. Fix the refuted claim, re-verify against the adversary's own "
            "check, then re-run with --adversary-resolution '<what was fixed and how "
            "the adversary's check was re-run>'.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    # Tier order (GHI #678): Codex (tier 1, different vendor) is REQUIRED first. A
    # Claude-family adversary shares this agent's blind spots — the exact failure 4b
    # exists to break — so it is admissible only when Codex was genuinely unavailable,
    # and that reason must be recorded. The human degraded floor is exempt (its verdict
    # already flags it); a proven cross-vendor adversary needs no justification.
    is_human_floor = verdict == "degraded-human-only" or adversary.strip().lower() == "human"
    if (
        not is_human_floor
        and not _is_cross_vendor_adversary(adversary)
        and not (fallback_reason and fallback_reason.strip())
    ):
        _fail(
            f"Completion blocked: Step 4b for {obpi_id} used a non-cross-vendor "
            f"(tier-2 Claude-family) adversary '{adversary}' with no recorded reason "
            "Codex was unavailable. Codex (tier 1) shares none of this agent's blind "
            "spots and is REQUIRED first (a Claude validating Claude shares failure "
            "modes). Run codex:setup: if it reports ready=true, re-run Step 4b through "
            "Codex. If Codex is genuinely unavailable, record why with "
            "--adversary-fallback-reason '<observed Codex unavailability, e.g. setup "
            'ready=false / not authenticated>\'. "It was convenient" is not a reason.',
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )


def _fail(msg: str, *, exit_code: int, as_json: bool, obpi_id: str) -> NoReturn:
    """Report an error and exit.

    Always raises SystemExit; never returns normally.
    """
    if as_json:
        print(json.dumps({"status": "error", "obpi_id": obpi_id, "error": msg}))
    else:
        console.print(f"[red]Error:[/red] {msg}")
    raise SystemExit(exit_code)
