"""ADR audit-check, covers-check, and emit-receipt command implementations."""

import json
import re
from datetime import date
from pathlib import Path
from typing import Any, cast

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
from gzkit.events import EventAnchor
from gzkit.hooks.core import enrich_completed_receipt_evidence
from gzkit.hooks.obpi import normalize_git_sync_state, normalize_scope_audit
from gzkit.ledger import (
    Ledger,
    audit_receipt_emitted_event,
    normalize_req_proof_inputs,
)
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


def adr_audit_check(adr: str, as_json: bool) -> None:
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
    findings: list[dict[str, Any]] = []
    complete: list[str] = []

    if not expected_obpis and not obpi_files:
        findings.append(
            {
                "id": None,
                "issue": "No OBPI briefs are linked to this ADR.",
            }
        )

    for expected_id in expected_obpis:
        if expected_id not in obpi_files:
            findings.append(
                {
                    "id": expected_id,
                    "issue": "Linked in ledger but no OBPI file found.",
                }
            )

    graph = ledger.get_artifact_graph()
    for obpi_id, obpi_file in sorted(obpi_files.items()):
        inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id=obpi_id, graph=graph)
        if inspection["reasons"]:
            findings.append(
                {
                    "id": obpi_id,
                    "file": str(obpi_file.relative_to(project_root)),
                    "issue": "; ".join(inspection["reasons"]),
                    "frontmatter_status": inspection["frontmatter_status"],
                    "brief_status": inspection["brief_status"],
                }
            )
        else:
            complete.append(obpi_id)

    adr_dir = project_root / config.paths.adrs
    coverage = _compute_adr_coverage(project_root, adr_id, adr_dir)

    # REQ coverage is blocking when REQs are defined for the ADR.
    # Uncovered REQs are findings (not advisory) — they fail the audit.
    coverage_findings: list[dict[str, Any]] = [
        {
            "id": u["req_id"],
            "issue": "REQ not covered by any @covers test annotation.",
        }
        for u in coverage["uncovered"]
    ]

    passed = not findings and not coverage_findings

    result = {
        "adr": adr_id,
        "passed": passed,
        "checked_obpis": sorted(obpi_files.keys()),
        "complete_obpis": complete,
        "findings": findings,
        "coverage": coverage,
        "coverage_findings": coverage_findings,
    }

    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    else:
        console.print(f"[bold]ADR audit-check:[/bold] {adr_id}")
        if passed:
            console.print("[green]PASS[/green] All linked OBPIs are completed with evidence.")
            if complete:
                for obpi_id in complete:
                    console.print(f"  - {obpi_id}")
        else:
            if findings:
                console.print("[red]FAIL[/red] OBPI completeness/evidence gaps found:")
                for finding in findings:
                    finding_id = finding.get("id") or "(none)"
                    issue = finding.get("issue", "")
                    console.print(f"  - {finding_id}: {issue}")
            if coverage_findings:
                console.print(
                    f"[red]FAIL[/red] {len(coverage_findings)} REQ(s) missing @covers traceability:"
                )
                for cf in coverage_findings:
                    console.print(f"  - {cf['id']}")
        _print_coverage_section(coverage, [])

    if not passed:
        raise SystemExit(1)


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
    """Return True when ADR ID is in the 0.0.x foundation series."""
    return re.match(r"^ADR-0\.0\.\d+(?:[.-].*)?$", adr_id) is not None


def _requires_human_obpi_attestation(parent_adr: str | None, parent_lane: str) -> bool:
    """Return whether completed evidence must include human-attestation fields.

    Foundation ADRs (0.0.x) always require human attestation.  For non-foundation
    ADRs, the parent lane sets the compliance floor -- a Lite OBPI under a Heavy ADR
    still requires attestation per AGENTS.md Lane Inheritance Rule.
    """
    if not isinstance(parent_adr, str) or not parent_adr:
        return False
    if _is_foundation_adr(parent_adr):
        return True
    return parent_lane == "heavy"


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


def adr_emit_receipt_cmd(
    adr: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
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

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        return

    ledger.append(event)
    console.print("[green]Audit receipt emitted.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Event: {receipt_event}")
    console.print(f"  Attestor: {attestor}")
