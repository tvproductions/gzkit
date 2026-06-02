"""ADR audit-check, covers-check, and emit-receipt command implementations."""

import json
import re
import sys
from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, cast

from gzkit.commands.adr_audit_covers_backfill import (
    BackfillResult,
    evaluate_backfill_for_audit,
    format_backfill_finding,
)
from gzkit.commands.adr_coverage import (
    OBPI_SEMVER_ITEM_RE,
    REQ_ID_RE,
    _build_covers_rows,
    _collect_adr_requirement_targets,
    _collect_covers_annotations,
    _compute_adr_coverage,
    _extract_adr_semver,
    _extract_h2_section_lines,
    _extract_obpi_requirement_targets,
    _print_adr_covers_check_result,
    _print_coverage_section,
    _req_prefix_for_obpi,
)
from gzkit.commands.common import (
    GzCliError,
    _reject_pool_adr_for_lifecycle,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_adr_ledger_id,
)
from gzkit.commands.status import _collect_obpi_files_for_adr, _inspect_obpi_brief
from gzkit.event_evidence import EventAnchor
from gzkit.hooks.core import enrich_completed_receipt_evidence
from gzkit.hooks.obpi import normalize_git_sync_state, normalize_scope_audit
from gzkit.ledger import (
    Ledger,
    audit_receipt_emitted_event,
    normalize_req_proof_inputs,
    parse_frontmatter_value,
)
from gzkit.traceability import find_covers_in_source
from gzkit.utils import capture_validation_anchor

# Re-export coverage symbols so existing imports keep working.
__all__ = [
    "OBPI_SEMVER_ITEM_RE",
    "REQ_ID_RE",
    "_build_covers_rows",
    "_collect_adr_requirement_targets",
    "_collect_covers_annotations",
    "_compute_adr_coverage",
    "_extract_adr_semver",
    "_extract_h2_section_lines",
    "_extract_obpi_requirement_targets",
    "_print_adr_covers_check_result",
    "_print_coverage_section",
    "_req_prefix_for_obpi",
]


def _collect_obpi_findings(
    project_root: Path,
    obpi_files: dict[str, Path],
    expected_obpis: list[str],
    ledger: Ledger,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (findings, complete_obpi_ids) for OBPI linkage + evidence checks."""
    findings: list[dict[str, Any]] = []
    complete: list[str] = []

    if not expected_obpis and not obpi_files:
        findings.append({"id": None, "issue": "No OBPI briefs are linked to this ADR."})

    for expected_id in expected_obpis:
        if expected_id not in obpi_files:
            findings.append(
                {"id": expected_id, "issue": "Linked in ledger but no OBPI file found."}
            )

    graph = ledger.get_artifact_graph()
    for obpi_id, obpi_file in sorted(obpi_files.items()):
        inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id=obpi_id, graph=graph)
        if inspection["reasons"]:
            findings.append(
                {
                    "id": obpi_id,
                    "file": obpi_file.relative_to(project_root).as_posix(),
                    "issue": "; ".join(inspection["reasons"]),
                    "frontmatter_status": inspection["frontmatter_status"],
                    "brief_status": inspection["brief_status"],
                }
            )
        else:
            complete.append(obpi_id)
    return findings, complete


def _partition_coverage_findings(
    coverage: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Split coverage ``uncovered`` entries by severity.

    GHI #268 — Advisory uncovered REQs (the default emitted by
    :func:`_compute_adr_coverage`) surface as warnings and do not block the
    audit; non-advisory severities are reserved for future per-REQ escalation
    and retain fail-closed behavior.
    """
    findings: list[dict[str, Any]] = [
        {
            "id": u["req_id"],
            "issue": "REQ not covered by any @covers test annotation.",
            "severity": u.get("severity", "advisory"),
        }
        for u in coverage["uncovered"]
    ]
    blocking = [cf for cf in findings if cf["severity"] != "advisory"]
    advisory = [cf for cf in findings if cf["severity"] == "advisory"]
    return findings, blocking, advisory


def _render_audit_check_result(
    adr_id: str,
    passed: bool,
    findings: list[dict[str, Any]],
    complete: list[str],
    coverage: dict[str, Any],
    coverage_blocking: list[dict[str, Any]],
    coverage_advisory: list[dict[str, Any]],
    backfill: BackfillResult | None = None,
) -> None:
    """Print the human-readable audit-check summary."""
    console.print(f"[bold]ADR audit-check:[/bold] {adr_id}")
    if passed:
        console.print("[green]PASS[/green] All linked OBPIs are completed with evidence.")
        for obpi_id in complete:
            console.print(f"  - {obpi_id}")
    else:
        if findings:
            console.print("[red]FAIL[/red] OBPI completeness/evidence gaps found:")
            for finding in findings:
                finding_id = finding.get("id") or "(none)"
                console.print(f"  - {finding_id}: {finding.get('issue', '')}")
        if coverage_blocking:
            console.print(
                f"[red]FAIL[/red] {len(coverage_blocking)} REQ(s) missing @covers traceability:"
            )
            for cf in coverage_blocking:
                console.print(f"  - {cf['id']}")
    if coverage_advisory:
        console.print(
            f"[yellow]Advisory[/yellow] {len(coverage_advisory)} REQ(s) without "
            "@covers traceability (non-blocking):"
        )
        for cf in coverage_advisory:
            console.print(f"  - {cf['id']}")
    _print_coverage_section(coverage, [])
    if backfill is not None:
        _render_backfill_section(backfill)


def _render_backfill_section(backfill: BackfillResult) -> None:
    """Render the covers-backfill heuristic section after the Advisory block."""
    if backfill.findings:
        first_severity = backfill.findings[0].severity
        count = len(backfill.findings)
        if first_severity == "blocking":
            header = f"[red]FAIL[/red] {count} covers-backfill finding(s):"
        else:
            header = f"[yellow]Backfill[/yellow] {count} covers-backfill warning(s):"
        console.print(header)
        for finding in backfill.findings:
            console.print(f"  {format_backfill_finding(finding)}")
    if backfill.unresolvable:
        console.print(
            f"[yellow]Unresolvable[/yellow] {len(backfill.unresolvable)} "
            "covers-backfill location(s) not resolvable in git:"
        )
        for diag in backfill.unresolvable:
            console.print(f"  {diag}")


def _collect_covers_locations_for_adr(
    project_root: Path,
    adr_id: str,
) -> list[tuple[str, str, int]]:
    """Return (target, rel_file, line_no) triples for REQs matching this ADR.

    Walks ``tests/**/*.py`` using :func:`~gzkit.traceability.find_covers_in_source`
    and filters to REQ IDs whose prefix matches the ADR's semver (e.g.
    ``REQ-0.0.23-`` for ``ADR-0.0.23``). Line numbers are 1-indexed.

    The semver is extracted via the canonical ``_extract_adr_semver`` helper
    so ``ADR-0.1.0-f`` resolves to ``0.1.0`` (not ``0.1.0-f``) and the
    REQ-prefix filter correctly accepts ``REQ-0.1.0-NN-MM`` decorators.
    """
    from gzkit.commands.adr_coverage import _extract_adr_semver

    semver = _extract_adr_semver(adr_id)
    if semver is None:
        return []
    req_prefix = f"REQ-{semver}-"
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        return []
    locations: list[tuple[str, str, int]] = []
    for test_file in sorted(tests_dir.rglob("*.py")):
        content = test_file.read_text(encoding="utf-8")
        rel_path = test_file.relative_to(project_root).as_posix()
        for req_id, line_no in find_covers_in_source(content):
            if req_id.startswith(req_prefix):
                locations.append((req_id, rel_path, line_no))
    return locations


def _collect_obpi_completion_events_for_adr(
    ledger: Ledger,
    obpi_ids: list[str],
) -> list[Mapping[str, Any]]:
    """Return ledger events for completed/attested_completed receipts for all OBPIs."""
    _receipt_events = {"completed", "attested_completed"}
    events: list[Mapping[str, Any]] = []
    for obpi_id in obpi_ids:
        for event in ledger.query(event_type="obpi_receipt_emitted", artifact_id=obpi_id):
            receipt_event = (event.extra or {}).get("receipt_event", "")
            if receipt_event in _receipt_events:
                events.append(event.model_dump())
    return events


def adr_audit_check(adr: str, as_json: bool, strict: bool = False) -> None:
    """Verify linked OBPIs are complete and contain implementation evidence."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "audit-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    findings, complete = _collect_obpi_findings(project_root, obpi_files, expected_obpis, ledger)

    adr_dir = project_root / config.paths.adrs
    coverage = _compute_adr_coverage(project_root, adr_id, adr_dir)
    coverage_findings, coverage_blocking, coverage_advisory = _partition_coverage_findings(coverage)

    passed = not findings and not coverage_blocking

    # Derive lane and kind from the ADR's frontmatter.
    adr_content = adr_file.read_text(encoding="utf-8")
    adr_lane = parse_frontmatter_value(adr_content, "lane") or "lite"
    if adr_lane not in {"lite", "heavy"}:
        adr_lane = "lite"
    adr_kind = "foundation" if _is_foundation_adr(adr_id) else "feature"

    # Collect covers locations and OBPI completion events for the heuristic.
    covers_locations = _collect_covers_locations_for_adr(project_root, adr_id)
    all_obpi_ids = sorted(obpi_files.keys())
    obpi_completion_events = _collect_obpi_completion_events_for_adr(ledger, all_obpi_ids)

    backfill = evaluate_backfill_for_audit(
        project_root,
        adr_lane=adr_lane,
        adr_kind=adr_kind,
        strict=strict,
        covers_locations=covers_locations,
        obpi_completion_events=obpi_completion_events,
        thresholds_path=project_root / "data" / "audit_thresholds.json",
    )

    result = {
        "adr": adr_id,
        "passed": passed,
        "checked_obpis": sorted(obpi_files.keys()),
        "complete_obpis": complete,
        "findings": findings,
        "coverage": coverage,
        "coverage_findings": coverage_findings,
        "coverage_blocking": coverage_blocking,
        "coverage_advisory": coverage_advisory,
        "covers_backfill_findings": [f.model_dump() for f in backfill.findings],
        "covers_backfill_unresolvable": list(backfill.unresolvable),
    }

    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    else:
        _render_audit_check_result(
            adr_id,
            passed,
            findings,
            complete,
            coverage,
            coverage_blocking,
            coverage_advisory,
            backfill=backfill,
        )

    if not passed:
        raise SystemExit(1)
    if backfill.exit_code != 0:
        raise SystemExit(backfill.exit_code)


def adr_covers_check(adr: str, as_json: bool) -> None:
    """Verify @covers traceability for an ADR and its linked OBPIs."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "covers-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    (
        requirement_targets,
        criteria_without_req_ids,
        invalid_requirement_targets,
    ) = _collect_adr_requirement_targets(project_root, obpi_files)

    expected_targets = [adr_id, *sorted(expected_obpis), *requirement_targets]
    covers = _collect_covers_annotations(project_root)
    rows, missing = _build_covers_rows(adr_id, expected_targets, covers)

    referenced_targets = sorted(k for k in covers if k.startswith(("ADR-", "OBPI-", "REQ-")))
    unmatched_targets = sorted(k for k in referenced_targets if k not in expected_targets)
    passed = not missing and not criteria_without_req_ids and not invalid_requirement_targets

    result = {
        "adr": adr_id,
        "passed": passed,
        "expected_targets": expected_targets,
        "covered_targets": [row["target"] for row in rows if row["covered"]],
        "missing_targets": missing,
        "requirement_targets": requirement_targets,
        "criteria_without_req_ids": criteria_without_req_ids,
        "invalid_requirement_targets": invalid_requirement_targets,
        "rows": rows,
        "unmatched_targets": unmatched_targets,
    }

    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    else:
        _print_adr_covers_check_result(result)

    if not passed:
        raise SystemExit(1)


def _is_foundation_adr(adr_id: str) -> bool:
    """Return True when ADR ID is in the 0.0.x foundation series.

    NOTE: This predicate is retained for taxonomy classification purposes only
    (e.g. ``adr_audit.py`` line 264 — ``adr_kind`` derivation for audit
    reporting). It is NO LONGER load-bearing for attestation routing.
    ``_requires_human_obpi_attestation`` now returns True unconditionally per
    ADR-0.0.36 and OBPI-0.0.36-02. Do not re-introduce attestation routing
    logic that calls this function.
    """
    return re.match(r"^ADR-0\.0\.\d+(?:[.-].*)?$", adr_id) is not None


def _requires_security_review_attestation(
    brief_frontmatter: Mapping[str, Any] | None,
) -> bool:
    """Return True when a brief carries ``sensitivity: security`` (ADR-0.0.22).

    Third axis of the (kind × lane × sensitivity) attestation matrix. Operates
    on a parsed frontmatter mapping so call sites own parsing and unit tests
    can construct synthetic dicts. The schema currently enumerates only
    ``"security"`` for the ``sensitivity`` field; future values must declare
    their own attestation rule rather than silently inheriting this one.
    """
    if not isinstance(brief_frontmatter, Mapping):
        return False
    return brief_frontmatter.get("sensitivity") == "security"


def _requires_human_obpi_attestation(
    parent_adr: str | None,
    parent_lane: str,
    brief_frontmatter: Mapping[str, Any] | None = None,
) -> bool:
    """Return whether completed evidence must include human-attestation fields.

    Per ADR-0.0.36 and OBPI-0.0.36-02, human attestation is UNIVERSAL: every
    OBPI completion requires it regardless of parent ADR kind, lane, or
    sensitivity. The foundation/lane/security branching logic has been
    collapsed. The signature is preserved for call-site compatibility; all
    three parameters are accepted but not evaluated.
    """
    return True


# ---------------------------------------------------------------------------
# GHI #290 authenticity gate + GHI #292 agent-relayed escape path
#
# DEAD CODE as of the canon-owner attestation declaration: the operator's
# verbatim conversational attestation relayed via --attestation-text is the
# Gate-5 attestation for every lane / kind / sensitivity (see AGENTS.md
# section "Lane & Kind & Sensitivity Attestation Matrix"). Nothing calls
# _enforce_human_attestation_authenticity or _validate_active_pipeline_marker
# anymore. This scaffolding (the TTY prompt, pipeline-marker validation, nonce
# coupling, --attestor-present plumbing) is retained pending removal under a
# separate ADR so the deletion lands with its own test fallout, not bundled
# into the doctrine change.
# ---------------------------------------------------------------------------

_GHI_290_AUTHENTICITY_CONFIRMATION = "ATTEST"

ATTESTATION_TYPE_HUMAN = "human"
ATTESTATION_TYPE_AGENT_RELAYED = "agent-relayed-operator-attestation"
ATTESTATION_TYPE_OPERATOR_VERBATIM = "operator-verbatim-conversational"


def _is_human_attestation_tty_available() -> bool:
    """Return True when stdin and stdout are both attached to a real TTY.

    Split out so tests can patch it. An agent subprocess without a controlling
    terminal returns False here, which is the desired enforcement path.
    """
    try:
        return bool(sys.stdin.isatty()) and bool(sys.stdout.isatty())
    except (ValueError, OSError):
        return False


_PIPELINE_MARKER_STALE_HOURS = 4
_PIPELINE_MARKER_NONCE_RE = re.compile(r"^[a-f0-9]{32}$")
_PIPELINE_MARKER_VALID_STAGES = frozenset({"implement", "verify", "ceremony", "sync", "audit"})


def _ledger_path_for(project_root: Path) -> Path:
    """Return the canonical ledger path used for marker provenance lookup."""
    return project_root / ".gzkit" / "ledger.jsonl"


def _ledger_has_pipeline_launched(ledger_path: Path, obpi_id: str, nonce: str) -> bool:
    """Return True when the ledger contains a pipeline_launched event matching obpi_id+nonce."""
    if not ledger_path.is_file():
        return False
    try:
        with ledger_path.open(encoding="utf-8") as handle:
            for raw in handle:
                line = raw.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if record.get("event") != "pipeline_launched":
                    continue
                if record.get("id") != obpi_id:
                    continue
                if record.get("nonce") == nonce:
                    return True
    except OSError:
        return False
    return False


def _check_marker_freshness(payload: dict[str, Any]) -> tuple[bool, str]:
    """Return (ok, reason) for the marker's started_at freshness window."""
    started_at = payload.get("started_at")
    if not isinstance(started_at, str):
        return False, "marker started_at field is missing"
    try:
        ts = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
    except ValueError:
        return False, f"marker started_at is not parseable: {started_at!r}"
    age = datetime.now(UTC) - ts
    if age > timedelta(hours=_PIPELINE_MARKER_STALE_HOURS):
        return False, (
            f"marker is stale (started_at={started_at}, "
            f"age exceeds {_PIPELINE_MARKER_STALE_HOURS}h freshness window)"
        )
    return True, ""


def _validate_active_pipeline_marker(
    project_root: Path, obpi_id: str, parent_adr: str
) -> tuple[bool, str]:
    """Validate the active pipeline marker for ``obpi_id`` (GHI #412).

    A trivially-touched file no longer satisfies this gate. The marker must
    parse as a JSON object with the fields ``gz obpi pipeline`` writes at
    Stage 1, must be fresh, and its nonce must appear in a
    ``pipeline_launched`` ledger event for the same OBPI. Returns
    ``(True, "")`` when every check passes, otherwise ``(False, reason)``.
    """
    marker = project_root / ".claude" / "plans" / f".pipeline-active-{obpi_id}.json"
    if not marker.is_file():
        return False, f"marker file does not exist: {marker.as_posix()}"
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"marker is not readable JSON: {exc}"
    if not isinstance(payload, dict):
        return False, "marker payload is not a JSON object"
    if payload.get("obpi_id") != obpi_id:
        return False, (f"marker obpi_id does not match: {payload.get('obpi_id')!r} != {obpi_id!r}")
    marker_parent = payload.get("parent_adr")
    if marker_parent != parent_adr:
        return False, (
            f"marker parent_adr does not match expected parent: {marker_parent!r} != {parent_adr!r}"
        )
    stage = payload.get("current_stage")
    if stage not in _PIPELINE_MARKER_VALID_STAGES:
        return False, f"marker current_stage is not canonical: {stage!r}"
    nonce = payload.get("nonce")
    if not isinstance(nonce, str) or not _PIPELINE_MARKER_NONCE_RE.fullmatch(nonce):
        return False, "marker nonce is missing or malformed"
    fresh_ok, fresh_reason = _check_marker_freshness(payload)
    if not fresh_ok:
        return False, fresh_reason
    if not _ledger_has_pipeline_launched(_ledger_path_for(project_root), obpi_id, nonce):
        return False, (
            "no matching pipeline_launched ledger event for this marker; "
            "the marker was not produced by an operator-initiated pipeline run"
        )
    return True, ""


def _active_pipeline_marker_exists(project_root: Path, obpi_id: str) -> bool:
    """Backward-compat: return True only when the marker is structurally authentic.

    Pre-GHI #412 this was a trivial ``marker.is_file()`` check. The forgery
    surface that exposed (any process with write access could satisfy the
    agent-relayed attestation gate) is now closed: the marker must parse,
    match expected obpi_id, carry a valid nonce, be fresh, and be witnessed
    by a ``pipeline_launched`` ledger event. Callers that need the rejection
    reason should call :func:`_validate_active_pipeline_marker` directly.
    """
    marker = project_root / ".claude" / "plans" / f".pipeline-active-{obpi_id}.json"
    if not marker.is_file():
        return False
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(payload, dict):
        return False
    parent_adr = payload.get("parent_adr")
    if not isinstance(parent_adr, str):
        return False
    ok, _reason = _validate_active_pipeline_marker(project_root, obpi_id, parent_adr)
    return ok


def _enforce_human_attestation_authenticity(
    *,
    obpi_id: str,
    parent_adr: str,
    attestor: str,
    attestation_text: str,
    attestor_present: bool = False,
    project_root: Path | None = None,
    sensitivity: str | None = None,
    parent_kind: str | None = None,
) -> str:
    """Enforce the GHI #290 authenticity gate and resolve the attestation path.

    The gate closes the vector that allowed a prior agent session to fabricate
    a ``human_attestation: true`` receipt for OBPI-0.0.20-03 on 2026-04-23.
    It has three branches (GHI #292 adds the third):

    1. **TTY path (``human``).** stdin AND stdout are attached to a real TTY.
       The operator reviews the echoed attestation payload and types the
       exact word ``ATTEST`` (uppercase, no quotes) to confirm. Returns
       :data:`ATTESTATION_TYPE_HUMAN`.
    2. **Agent-relayed path (``agent-relayed-operator-attestation``).** No
       TTY, but ``attestor_present=True`` AND the marker passes
       :func:`_validate_active_pipeline_marker` (structure, freshness,
       ledger-witnessed nonce — GHI #412). Returns
       :data:`ATTESTATION_TYPE_AGENT_RELAYED` so the caller can record a
       taxonomically distinct ledger receipt. **GHI #412 narrowing:** the
       agent-relayed path is refused entirely when ``sensitivity == "security"``
       or ``parent_kind == "foundation"`` — those scopes require live TTY
       attestation, never a file-based proxy.
    3. **Fail-closed.** No TTY and either ``attestor_present=False`` or the
       marker fails authenticity validation. Agent-synthesized attestation
       from a fully-headless context is prohibited per GHI #290; the function
       raises :class:`GzCliError`.
    """
    if _is_human_attestation_tty_available():
        console.print("")
        console.print("[bold yellow]=== Human Attestation Required (GHI #290) ===[/bold yellow]")
        console.print(f"  OBPI:        {obpi_id}")
        console.print(f"  Parent ADR:  {parent_adr}")
        console.print(f"  Attestor:    {attestor}")
        console.print(f"  Attestation: {attestation_text}")
        console.print("")
        console.print(
            f"Type the word [bold]{_GHI_290_AUTHENTICITY_CONFIRMATION}[/bold] "
            "(uppercase, no quotes) to confirm you personally attest, "
            "or anything else to abort:"
        )
        try:
            response = input("> ").strip()
        except (EOFError, KeyboardInterrupt) as exc:
            msg = "Attestation aborted (no confirmation received)."
            raise GzCliError(msg) from exc

        if response != _GHI_290_AUTHENTICITY_CONFIRMATION:
            msg = (
                f"Attestation declined (expected "
                f"{_GHI_290_AUTHENTICITY_CONFIRMATION!r}, got {response!r})."
            )
            raise GzCliError(msg)
        return ATTESTATION_TYPE_HUMAN

    if attestor_present:
        if project_root is None:
            msg = (
                "--attestor-present requires project context to verify the "
                "pipeline marker; internal caller did not pass project_root."
            )
            raise GzCliError(msg)
        if isinstance(sensitivity, str) and sensitivity.lower() == "security":
            msg = (
                "--attestor-present is refused for sensitivity:security "
                "attestation (GHI #412 + #434). The agent-relayed path is a "
                "file-based co-presence proxy and cannot satisfy the authority "
                "boundary required for security scopes. Run this command from "
                "an interactive shell and type the confirmation yourself."
            )
            raise GzCliError(msg)
        ok, reason = _validate_active_pipeline_marker(project_root, obpi_id, parent_adr)
        if not ok:
            msg = (
                f"--attestor-present rejected: {reason}. "
                f"Start the pipeline with 'uv run gz obpi pipeline {obpi_id}' "
                f"first, or re-run this command from an interactive shell and "
                f"type the confirmation yourself."
            )
            raise GzCliError(msg)
        console.print("")
        console.print(
            "[bold yellow]=== Agent-Relayed Operator Attestation (GHI #292) ===[/bold yellow]"
        )
        console.print(f"  OBPI:        {obpi_id}")
        console.print(f"  Parent ADR:  {parent_adr}")
        console.print(f"  Attestor:    {attestor}")
        console.print(f"  Attestation: {attestation_text}")
        console.print(
            "  [dim]Co-presence proxy: validated active pipeline marker "
            f".claude/plans/.pipeline-active-{obpi_id}.json[/dim]"
        )
        return ATTESTATION_TYPE_AGENT_RELAYED

    msg = (
        "Human attestation required for this OBPI, but the process is not "
        "attached to an interactive terminal (stdin/stdout is not a TTY). "
        "Agent-synthesized attestation is prohibited per GHI #290. "
        "Re-run this command from an interactive shell and type the "
        "confirmation yourself, or pass --attestor-present from an active "
        "'gz obpi pipeline' session (GHI #292)."
    )
    raise GzCliError(msg)


_UNCOVERED_ACCEPTANCE_CONFIRMATION = "ACCEPT"


def _enforce_uncovered_acceptance_confirmation(
    *,
    obpi_id: str,
    parent_adr: str,
    req_ids: list[str],
    attestor: str,
    attestor_present: bool = False,
    project_root: Path | None = None,
    sensitivity: str | None = None,
    parent_kind: str | None = None,
) -> str:
    """Gate the --accept-uncovered override for heavy/foundation parents.

    Three-branch mirror of ``_enforce_human_attestation_authenticity``:

    1. **TTY path.** stdin AND stdout are attached to a real TTY; operator
       types ``ACCEPT`` to confirm each waiver. Returns
       :data:`ATTESTATION_TYPE_HUMAN`.
    2. **Agent-relayed path.** No TTY but ``attestor_present=True`` AND an
       active pipeline marker exists. Returns
       :data:`ATTESTATION_TYPE_AGENT_RELAYED`.
    3. **Fail-closed.** Headless + no marker → raises :class:`GzCliError`.
    """
    req_list = ", ".join(req_ids)
    if _is_human_attestation_tty_available():
        console.print("")
        console.print("[bold yellow]=== Uncovered REQ Acceptance (ADR-0.0.25) ===[/bold yellow]")
        console.print(f"  OBPI:     {obpi_id}")
        console.print(f"  ADR:      {parent_adr}")
        console.print(f"  Attestor: {attestor}")
        console.print(f"  Waiving:  {req_list}")
        console.print("")
        console.print(
            f"Type the word [bold]{_UNCOVERED_ACCEPTANCE_CONFIRMATION}[/bold] "
            "(uppercase, no quotes) to confirm you accept these uncovered REQs, "
            "or anything else to abort:"
        )
        try:
            response = input("> ").strip()
        except (EOFError, KeyboardInterrupt) as exc:
            msg = "Uncovered-REQ acceptance aborted (no confirmation received)."
            raise GzCliError(msg) from exc
        if response != _UNCOVERED_ACCEPTANCE_CONFIRMATION:
            msg = (
                f"Uncovered-REQ acceptance declined (expected "
                f"{_UNCOVERED_ACCEPTANCE_CONFIRMATION!r}, got {response!r})."
            )
            raise GzCliError(msg)
        return ATTESTATION_TYPE_HUMAN

    if attestor_present:
        if project_root is None:
            msg = (
                "--attestor-present requires project context to verify the "
                "pipeline marker; internal caller did not pass project_root."
            )
            raise GzCliError(msg)
        if isinstance(sensitivity, str) and sensitivity.lower() == "security":
            msg = (
                "--attestor-present is refused for sensitivity:security "
                "uncovered-REQ acceptance (GHI #412 + #434). Run this command "
                "from an interactive shell and type the confirmation yourself."
            )
            raise GzCliError(msg)
        ok, reason = _validate_active_pipeline_marker(project_root, obpi_id, parent_adr)
        if not ok:
            msg = (
                f"--attestor-present rejected: {reason}. "
                f"Start the pipeline with 'uv run gz obpi pipeline {obpi_id}' first."
            )
            raise GzCliError(msg)
        console.print("")
        console.print(
            "[bold yellow]=== Agent-Relayed Uncovered REQ Acceptance (ADR-0.0.25) ===[/bold yellow]"
        )
        console.print(f"  OBPI:     {obpi_id}")
        console.print(f"  ADR:      {parent_adr}")
        console.print(f"  Attestor: {attestor}")
        console.print(f"  Waiving:  {req_list}")
        console.print(
            "  [dim]Co-presence proxy: active pipeline marker "
            f".claude/plans/.pipeline-active-{obpi_id}.json[/dim]"
        )
        return ATTESTATION_TYPE_AGENT_RELAYED

    msg = (
        "--accept-uncovered requires interactive TTY confirmation for heavy/foundation OBPIs. "
        "stdin/stdout is not a TTY and --attestor-present was not set (or the pipeline marker "
        f"is missing). Run from an interactive shell or start the pipeline with "
        f"'uv run gz obpi pipeline {obpi_id}' first (GHI #292)."
    )
    raise GzCliError(msg)


def _validate_obpi_completed_required_fields(evidence: dict[str, Any]) -> None:
    """Validate baseline completed-receipt evidence fields."""
    required_fields = ("value_narrative", "key_proof")
    missing: list[str] = []
    for field in required_fields:
        value = evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(field)
    if missing:
        msg = f"Missing required completed-evidence field(s): {', '.join(sorted(missing))}."
        raise GzCliError(msg)


def _validate_obpi_human_attestation_fields(evidence: dict[str, Any], attestor: str) -> None:
    """Validate heavy/foundation human-attestation evidence contract.

    Reports all missing/invalid fields at once instead of one-at-a-time (GHI #80).
    """
    errors: list[str] = []
    placeholder_names = {"n/a", "tbd", "todo", "none", "-", "...", ""}
    if attestor.strip().lower() in placeholder_names:
        errors.append("--attestor must be a real name, not a placeholder.")
    if evidence.get("human_attestation") is not True:
        errors.append("evidence.human_attestation must be true.")

    attestation_text = evidence.get("attestation_text")
    if not isinstance(attestation_text, str) or not attestation_text.strip():
        errors.append("evidence.attestation_text must be a non-empty string.")

    attestation_date = evidence.get("attestation_date")
    if not isinstance(attestation_date, str) or not re.match(
        r"^\d{4}-\d{2}-\d{2}$", str(attestation_date)
    ):
        errors.append("evidence.attestation_date must be formatted as YYYY-MM-DD.")
    elif attestation_date:
        try:
            date.fromisoformat(attestation_date)
        except ValueError:
            errors.append("evidence.attestation_date must be a valid YYYY-MM-DD date.")

    if errors:
        joined = " ".join(errors)
        msg = f"Heavy/Foundation OBPI completion: {joined}"
        raise GzCliError(msg)


def _validate_explicit_req_proof_inputs(raw_inputs: Any) -> list[dict[str, str]]:
    """Validate an explicit req_proof_inputs payload when supplied."""
    if raw_inputs is None:
        return []
    if not isinstance(raw_inputs, list) or not raw_inputs:
        msg = "evidence.req_proof_inputs must be a non-empty list of proof input objects."
        raise GzCliError(msg)

    normalized = normalize_req_proof_inputs(raw_inputs)
    if len(normalized) != len(raw_inputs):
        msg = (
            "Each evidence.req_proof_inputs item must include non-empty "
            "name/kind/source fields and status present|missing."
        )
        raise GzCliError(msg)
    return normalized


def _validate_obpi_completion_evidence(
    *,
    project_root: Path,
    obpi_content: str,
    evidence: dict[str, Any] | None,
    parent_adr: str | None,
    parent_lane: str,
    attestor: str,
) -> tuple[dict[str, Any], str, EventAnchor | None]:
    """Validate and normalize evidence for OBPI completed receipts."""
    if evidence is None:
        msg = "OBPI completed receipts require --evidence-json with value_narrative and key_proof."
        raise GzCliError(msg)

    _validate_obpi_completed_required_fields(evidence)
    requires_human_attestation = _requires_human_obpi_attestation(parent_adr, parent_lane)

    if requires_human_attestation:
        _validate_obpi_human_attestation_fields(evidence, attestor)

    completion_term = "attested_completed" if requires_human_attestation else "completed"
    normalized = dict(evidence)
    explicit_req_proof_inputs = _validate_explicit_req_proof_inputs(
        normalized.get("req_proof_inputs")
    )
    human_attestation = None
    if normalized.get("human_attestation") is True:
        human_attestation = {
            "valid": True,
            "attestor": attestor,
            "attestation_text": normalized.get("attestation_text"),
            "date": normalized.get("attestation_date"),
        }
    normalized["req_proof_inputs"] = explicit_req_proof_inputs or normalize_req_proof_inputs(
        None,
        fallback_key_proof=cast(str, normalized.get("key_proof")),
        human_attestation=human_attestation,
    )
    normalized["obpi_completion"] = completion_term
    normalized["attestation_requirement"] = "required" if requires_human_attestation else "optional"
    if isinstance(parent_adr, str) and parent_adr:
        normalized["parent_adr"] = parent_adr
    normalized["parent_lane"] = parent_lane
    explicit_scope_audit = normalized.get("scope_audit")
    scope_audit = normalize_scope_audit(explicit_scope_audit)
    if explicit_scope_audit is not None and scope_audit is None:
        msg = (
            "evidence.scope_audit must be an object with allowlist, changed_files, "
            "and out_of_scope_files string arrays."
        )
        raise GzCliError(msg)

    explicit_git_sync_state = normalized.get("git_sync_state")
    git_sync_state = normalize_git_sync_state(explicit_git_sync_state)
    if explicit_git_sync_state is not None and git_sync_state is None:
        msg = (
            "evidence.git_sync_state must include branch/remote/head/remote_head, "
            "dirty/diverged booleans, ahead/behind integers, and action/warning/blocker arrays."
        )
        raise GzCliError(msg)

    enriched_evidence, anchor = enrich_completed_receipt_evidence(
        project_root=project_root,
        content=obpi_content,
        base_evidence=normalized,
        parent_adr=parent_adr,
        recorder_source="cli:obpi_emit_receipt",
        scope_audit=scope_audit,
        git_sync_state=git_sync_state,
    )
    return enriched_evidence, completion_term, anchor


def _select_adr_package_dir(matches: list[Path]) -> Path | None:
    """Select the ADR package *directory* from a glob match set, deterministically.

    The closeout glob ``docs/design/adr/**/<adr-id>*`` matches both the package
    directory and the ADR markdown file inside it (``<adr-id>.md``). Picking the
    first raw glob hit is filesystem-order-dependent: macOS/APFS happens to yield
    the directory first, but Linux/ext4 yields hash-arbitrary order and can yield
    the file — silently skipping every OBPI brief and passing the coverage gate.
    Filter to directories and sort so selection is order-independent.
    """
    dirs = sorted(d for d in matches if d.is_dir())
    return dirs[0] if dirs else None


def _check_adr_obpi_coverage_gaps(
    adr_id: str,
    project_root: Path,
    ledger: "Ledger",
) -> list[tuple[str, list[str]]]:
    """Return (obpi_id, unwaived_gap_req_ids) pairs for the closing ADR (ADR-0.0.25-02).

    Walks the ADR package directory, parses each OBPI brief's REQs, checks
    coverage structurally (no test re-run), then subtracts any REQ waivers
    recorded via ``obpi_completion_uncovered_accept`` ledger events. Returns
    an empty list when all OBPIs have full or waived coverage.
    """
    import json as _json

    from gzkit.governance.req_coverage import discover_covers, parse_brief_reqs

    adr_dir = _select_adr_package_dir(list(project_root.glob(f"docs/design/adr/**/{adr_id}*")))
    if adr_dir is None:
        return []

    brief_paths = sorted(adr_dir.rglob("OBPI-*.md"))
    if not brief_paths:
        return []

    tests_root = project_root / "tests"
    features_root = project_root / "features"

    # Load acceptance waivers from ledger JSONL
    waived: set[tuple[str, str]] = set()
    ledger_path = getattr(ledger, "path", None)
    if ledger_path and Path(str(ledger_path)).is_file():
        with Path(str(ledger_path)).open(encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = _json.loads(line)
                except (ValueError, KeyError):
                    continue
                if evt.get("event") == "obpi_completion_uncovered_accept":
                    extra = evt.get("extra", {})
                    oid = extra.get("obpi_id", "")
                    rid = extra.get("req_id", "")
                    if oid and rid:
                        waived.add((oid, rid))

    result: list[tuple[str, list[str]]] = []
    for brief_path in brief_paths:
        reqs = parse_brief_reqs(brief_path)
        if not reqs:
            continue
        obpi_id = brief_path.stem
        gaps: list[str] = []
        for req in reqs:
            refs = discover_covers(req, tests_root, features_root=features_root)
            if not refs and (obpi_id, req) not in waived:
                gaps.append(req)
        if gaps:
            result.append((obpi_id, gaps))

    return result


def _apply_human_attestation_gates(
    *,
    adr_id: str,
    adr_file: Path,
    receipt_event: str,
    attestor: str,
    attestor_present: bool,
    evidence: dict[str, Any] | None,
    ledger: "Ledger",
    project_root: Path,
    dry_run: bool,
) -> None:
    """Run the ADR-0.0.24-02 receipt-binding gate then resolve attestation_type.

    The prior GHI #290 TTY authenticity gate is no longer invoked: per the
    canon-owner declaration the operator's verbatim attestation relayed via
    the receipt evidence is the Gate-5 attestation. See AGENTS.md section
    "Lane & Kind & Sensitivity Attestation Matrix".
    """
    from gzkit.commands.obpi_complete import _enforce_attestation_receipt_gate, _read_adr_kind

    adr_attestation_text = ""
    if isinstance(evidence, dict):
        candidate = evidence.get("attestation_text") or evidence.get("scope")
        if isinstance(candidate, str):
            adr_attestation_text = candidate
    adr_lane_raw = parse_frontmatter_value(adr_file.read_text(encoding="utf-8"), "lane") or "lite"
    adr_kind = _read_adr_kind(adr_file)
    _enforce_attestation_receipt_gate(
        obpi_id=None,
        parent_adr=adr_id,
        parent_lane=adr_lane_raw.strip().lower(),
        parent_kind=adr_kind,
        attestation_text=adr_attestation_text,
        attestor=attestor,
        ledger=ledger,
        project_root=project_root,
        as_json=False,
        dry_run=dry_run,
    )
    attestation_text = adr_attestation_text
    attestation_type = _enforce_human_authenticity_gate(
        adr_id=adr_id,
        receipt_event=receipt_event,
        attestor=attestor,
        attestor_present=attestor_present,
        evidence=evidence,
        project_root=project_root,
        attestation_text=attestation_text,
    )
    if isinstance(evidence, dict):
        evidence["attestation_type"] = attestation_type


def _enforce_human_authenticity_gate(
    *,
    adr_id: str,
    receipt_event: str,
    attestor: str,
    attestor_present: bool,
    evidence: dict[str, Any] | None,
    project_root: Path,
    attestation_text: str,
) -> str:
    """Resolve the attestation_type for an ADR human-attestation receipt.

    Per the canon-owner declaration (AGENTS.md section "Lane & Kind &
    Sensitivity Attestation Matrix"), the operator's verbatim attestation
    relayed via the receipt evidence IS the Gate-5 attestation for every
    lane / kind / sensitivity. The prior TTY-typed ATTEST authenticity gate
    (GHI #290) is no longer invoked; ``attestor`` / ``attestor_present`` /
    ``project_root`` are retained on the signature for the call graph and
    are slated for removal with the gate scaffolding under a separate ADR.
    """
    text = attestation_text
    if isinstance(evidence, dict):
        candidate = evidence.get("attestation_text") or evidence.get("scope")
        if isinstance(candidate, str):
            text = candidate
    if not (text or "").strip():
        msg = (
            f"Human-attestation receipt '{receipt_event}' for {adr_id} requires "
            "the operator's verbatim attestation text in --evidence-json "
            "(the 'attestation_text' or 'scope' field)."
        )
        raise GzCliError(msg)
    return ATTESTATION_TYPE_OPERATOR_VERBATIM


def _emit_adr_closeout_receipt(
    *,
    adr_id: str,
    project_root: Path,
    ledger: "Ledger",
    attestor: str,
    dry_run: bool,
) -> None:
    """Emit a ``closed`` receipt after verifying no unwaived REQ gaps remain."""
    gaps = _check_adr_obpi_coverage_gaps(adr_id, project_root, ledger)
    if gaps:
        lines = "\n".join(f"  {obpi_id}: {', '.join(reqs)}" for obpi_id, reqs in gaps)
        msg = (
            f"ADR closeout blocked — unwaived REQ coverage gaps in {adr_id}:\n"
            f"{lines}\n"
            "Waive each gap with `gz obpi complete --accept-uncovered <REQ-ID> "
            "--accept-uncovered-reason <REASON>` before closing the ADR."
        )
        console.print(f"[red]Error:[/red] {msg}")
        raise SystemExit(3)
    anchor = capture_validation_anchor(project_root, adr_id)
    close_event = audit_receipt_emitted_event(
        adr_id=adr_id,
        receipt_event="closed",
        attestor=attestor,
        evidence=None,
        anchor=anchor,
    )
    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(close_event.model_dump(), indent=2))
        return
    ledger.append(close_event)
    console.print("[green]ADR closeout receipt emitted.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print("  Event: closed")


def adr_emit_receipt_cmd(
    adr: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
    attestor_present: bool = False,
) -> None:
    """Emit an ADR audit receipt event anchored in the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "issued receipts")

    # ADR-0.0.25-02: --event closed triggers a structural REQ-coverage gate
    # across all OBPI briefs before emitting the closeout receipt.
    if receipt_event == "closed":
        _emit_adr_closeout_receipt(
            adr_id=adr_id,
            project_root=project_root,
            ledger=ledger,
            attestor=attestor,
            dry_run=dry_run,
        )
        return

    evidence: dict[str, Any] | None = None
    if evidence_json:
        try:
            parsed = json.loads(evidence_json)
        except json.JSONDecodeError as exc:
            msg = f"Invalid --evidence-json: {exc}"
            raise GzCliError(msg) from exc
        if not isinstance(parsed, dict):
            msg = "--evidence-json must decode to a JSON object"
            raise GzCliError(msg)
        evidence = parsed

    anchor = capture_validation_anchor(project_root, adr_id)
    event = audit_receipt_emitted_event(
        adr_id=adr_id,
        receipt_event=receipt_event,
        attestor=attestor,
        evidence=evidence,
        anchor=anchor,
    )

    if not dry_run and _is_human_attestation_receipt_event(receipt_event):
        _apply_human_attestation_gates(
            adr_id=adr_id,
            adr_file=adr_file,
            receipt_event=receipt_event,
            attestor=attestor,
            attestor_present=attestor_present,
            evidence=evidence,
            ledger=ledger,
            project_root=project_root,
            dry_run=dry_run,
        )

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        if _is_human_attestation_receipt_event(receipt_event):
            console.print(
                "[yellow]Attestation:[/yellow] live run would record the "
                "operator-verbatim attestation text from --evidence-json."
            )
        return

    ledger.append(event)
    console.print("[green]Audit receipt emitted.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Event: {receipt_event}")
    console.print(f"  Attestor: {attestor}")


_HUMAN_ATTESTATION_RECEIPT_EVENTS = frozenset({"validated", "attested", "accepted"})


def _is_human_attestation_receipt_event(receipt_event: str) -> bool:
    """Return True for ADR receipt events that represent a human attestation.

    Keeps the gate scoped: ``emitted``, ``corrected``, ``superseded``, and
    other informational events remain headless-safe; Gate 5 attestation
    events require the authenticity check.
    """
    return receipt_event.strip().lower() in _HUMAN_ATTESTATION_RECEIPT_EVENTS


def _adr_audit_marker_path(project_root: Path, adr_id: str) -> Path:
    """Return the per-ADR audit-ceremony marker path."""
    return project_root / ".claude" / "plans" / f".pipeline-active-{adr_id}.json"


def adr_audit_begin_cmd(adr: str) -> None:
    """Open an ADR audit ceremony — write the co-presence marker.

    The marker is the same shape ``gz obpi pipeline`` writes for OBPI
    ceremonies; ``_active_pipeline_marker_exists`` (GHI #292) accepts it
    as proof that an operator-typed CLI entry-point opened the ceremony.
    The skill ``/gz-adr-audit`` calls this verb at the start of Step 8 so
    the agent-relayed Gate-5 emit can pass the authenticity gate without
    fabricating the marker by hand.

    Idempotent: a re-invocation refreshes ``updated_at`` and rewrites the
    payload; the marker exists at most once per ADR.
    """
    from datetime import UTC, datetime

    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "opened audit ceremonies")

    from gzkit.ledger import pipeline_launched_event
    from gzkit.pipeline_runtime import generate_pipeline_nonce

    marker_path = _adr_audit_marker_path(project_root, adr_id)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    nonce = generate_pipeline_nonce()
    payload: dict[str, Any] = {
        "obpi_id": adr_id,
        "parent_adr": adr_id,
        "lane": "audit",
        "entry": "audit",
        "execution_mode": "audit",
        "current_stage": "audit",
        "started_at": timestamp,
        "updated_at": timestamp,
        "receipt_state": "audit-active",
        "nonce": nonce,
        "blockers": [],
        "required_human_action": (
            "Operator verbal attestation expected at Gate-5 emit; agent relays."
        ),
        "next_command": f"uv run gz adr emit-receipt {adr_id} --event validated --attestor-present",
        "resume_point": "emit-receipt",
    }
    marker_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    ledger.append(
        pipeline_launched_event(
            obpi_id=adr_id,
            parent_adr=adr_id,
            lane="audit",
            nonce=nonce,
            marker_path=marker_path.relative_to(project_root).as_posix(),
            entry="audit",
        )
    )
    console.print("[green]ADR audit ceremony opened.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Marker: {marker_path}")


def adr_audit_end_cmd(adr: str) -> None:
    """Close an ADR audit ceremony — remove the co-presence marker.

    Called by the ``/gz-adr-audit`` skill after a successful Gate-5
    emit. Marker hygiene matters: leaving the marker behind would make
    a second agent-relayed emit succeed without a fresh operator
    invocation, defeating the co-presence proof. Missing-marker is a
    soft warning, not an error — closing an already-closed ceremony
    is idempotent.
    """
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)

    marker_path = _adr_audit_marker_path(project_root, adr_id)
    if marker_path.is_file():
        marker_path.unlink()
        console.print("[green]ADR audit ceremony closed.[/green]")
        console.print(f"  ADR: {adr_id}")
        console.print(f"  Marker removed: {marker_path}")
    else:
        console.print("[yellow]No active ADR audit marker to close.[/yellow]")
        console.print(f"  ADR: {adr_id}")
        console.print(f"  Expected: {marker_path}")
