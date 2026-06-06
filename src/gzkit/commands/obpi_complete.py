"""Atomic OBPI completion command.

``gz obpi complete`` validates, writes evidence, flips status, records
attestation, and emits a completion receipt in a single all-or-nothing
transaction.  If any step fails, no files or ledger entries are modified.
"""

from __future__ import annotations

import json
import re
import secrets
import subprocess
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, cast

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
from gzkit.governance.trust_audits.sensitivity import detect_brief_security_floor
from gzkit.hooks.obpi import section_body
from gzkit.ledger import Ledger, parse_frontmatter_value, resolve_adr_lane

# section_body is used in _has_human_attestation_content for H2 section extraction
from gzkit.ledger_events import (
    audit_receipt_emitted_event,
    obpi_completion_uncovered_accept_event,
    obpi_receipt_emitted_event,
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
        # newest is non-None here but Path | None narrows are flow-sensitive;
        # cast to Path so type checkers do not complain about ``newest.name``.
        stale_path = cast(Path, newest)
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
) -> None:
    """Run the receipt-binding gate; emit meta-receipt-bind on success.

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
        return
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
        return

    if result.warn_only:
        console.print(
            "[yellow]Warning:[/yellow] no ARB receipts cited in attestation "
            "(lite-non-foundation policy)."
        )
        return

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


def _apply_uncovered_waivers(
    *,
    gaps: list[str],
    accept_uncovered: list[str],
    accept_uncovered_reason: list[str],
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
    if accept_security_floor and effective_sensitivity == "security":
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

    # 6-8. Execute atomic transaction
    try:
        _execute_transaction(
            obpi_file=obpi_file,
            original_content=original_content,
            new_content=new_content,
            adr_dir=adr_dir,
            audit_entry=audit_entry,
            ledger=ledger,
            receipt_event=receipt_event,
        )
    except OSError as exc:
        _fail(f"I/O error during completion: {exc}", exit_code=2, as_json=as_json, obpi_id=obpi_id)

    # Success output
    _print_success(obpi_id, resolved_parent, parent_lane, completion_term, attestor, as_json)


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


def _execute_transaction(
    *,
    obpi_file: Path,
    original_content: str,
    new_content: str,
    adr_dir: Path,
    audit_entry: dict[str, Any],
    ledger: Ledger,
    receipt_event: Any,
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

        # Phase 3: Emit receipt to main ledger
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


def _fail(msg: str, *, exit_code: int, as_json: bool, obpi_id: str) -> None:
    """Report an error and exit.

    Always raises SystemExit; never returns normally.
    """
    if as_json:
        print(json.dumps({"status": "error", "obpi_id": obpi_id, "error": msg}))
    else:
        console.print(f"[red]Error:[/red] {msg}")
    raise SystemExit(exit_code)
