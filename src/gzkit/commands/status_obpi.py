"""OBPI status building, rendering, and index/collection for the status subsystem."""

from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    _is_pool_adr_id,
    console,
    resolve_obpi,
)
from gzkit.commands.status_obpi_inspect import (
    _extract_human_attestation,
    _extract_tracked_defects,
    _has_substantive_body,
    _has_substantive_implementation_summary,
    _has_substantive_section,
    _implementation_summary_validation_commands,
    _inspect_obpi_brief,
    _issue_details,
    _markdown_label_value,
    _resolved_key_proof_body,
    _section_body,
    _section_body_with_prefix,
    _tracked_defect_refs,
)
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    derive_obpi_semantics,
)
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts

# Re-export inspection symbols so existing imports keep working.
__all__ = [
    "_extract_human_attestation",
    "_extract_tracked_defects",
    "_has_substantive_body",
    "_has_substantive_implementation_summary",
    "_has_substantive_section",
    "_implementation_summary_validation_commands",
    "_inspect_obpi_brief",
    "_issue_details",
    "_markdown_label_value",
    "_resolved_key_proof_body",
    "_section_body",
    "_section_body_with_prefix",
    "_tracked_defect_refs",
]

# ---------------------------------------------------------------------------
# OBPI index & file collection
# ---------------------------------------------------------------------------


def _build_obpi_index(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
) -> list[tuple[str, str, Path]]:
    """Scan all OBPI files once and return (canonical_id, canonical_parent, path) tuples."""
    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    index: list[tuple[str, str, Path]] = []
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        obpi_id = ledger.canonicalize_id(metadata.get("id", obpi_file.stem))
        parent = metadata.get("parent", "")
        canonical_parent = ledger.canonicalize_id(parent) if parent else ""
        index.append((obpi_id, canonical_parent, obpi_file))
    return index


def _collect_obpi_files_for_adr(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
    obpi_index: list[tuple[str, str, Path]] | None = None,
) -> tuple[dict[str, Path], list[str]]:
    if _is_pool_adr_id(adr_id):
        return {}, []

    canonical_adr = ledger.canonicalize_id(adr_id)
    graph = ledger.get_artifact_graph()
    adr_info = graph.get(canonical_adr, {})
    expected_obpis = [
        child_id
        for child_id in adr_info.get("children", [])
        if graph.get(child_id, {}).get("type") == "obpi"
        and not graph.get(child_id, {}).get("withdrawn", False)
    ]

    if obpi_index is None:
        obpi_index = _build_obpi_index(project_root, config, ledger)

    obpi_files: dict[str, Path] = {}
    for obpi_id, canonical_parent, obpi_file in obpi_index:
        if canonical_parent == canonical_adr or obpi_id in expected_obpis:
            obpi_files[obpi_id] = obpi_file

    return obpi_files, expected_obpis


# ---------------------------------------------------------------------------
# OBPI status rows & summaries
# ---------------------------------------------------------------------------


def _adr_obpi_status_rows(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
    obpi_index: list[tuple[str, str, Path]] | None = None,
) -> list[dict[str, Any]]:
    """Build per-OBPI status rows for a target ADR."""
    obpi_files, expected_obpis = _collect_obpi_files_for_adr(
        project_root, config, ledger, adr_id, obpi_index=obpi_index
    )
    rows: list[dict[str, Any]] = []
    graph = ledger.get_artifact_graph()

    for expected_id in sorted(expected_obpis):
        if expected_id in obpi_files:
            continue
        semantics = derive_obpi_semantics(
            graph.get(expected_id, {}),
            obpi_id=expected_id,
            artifact_graph=graph,
            found_file=False,
            file_completed=False,
            implementation_evidence_ok=False,
            key_proof_ok=False,
            project_root=project_root,
        )
        rows.append(
            {
                "id": expected_id,
                "linked_in_ledger": True,
                "found_file": False,
                "file": None,
                "completed": bool(semantics["completed"]),
                "ledger_completed": bool(semantics["ledger_completed"]),
                "evidence_ok": bool(semantics["evidence_ok"]),
                "implementation_evidence_ok": False,
                "key_proof_ok": False,
                "runtime_state": semantics["runtime_state"],
                "proof_state": semantics["proof_state"],
                "attestation_requirement": semantics["attestation_requirement"],
                "attestation_state": semantics["attestation_state"],
                "req_proof_state": semantics["req_proof_state"],
                "req_proof_inputs": list(semantics["req_proof_inputs"]),
                "req_proof_summary": dict(semantics["req_proof_summary"]),
                "anchor_state": semantics["anchor_state"],
                "anchor_commit": semantics["anchor_commit"],
                "current_head": semantics["current_head"],
                "anchor_issues": list(semantics["anchor_issues"]),
                "anchor_drift_files": list(semantics["anchor_drift_files"]),
                "frontmatter_status": None,
                "brief_status": None,
                "reflection_issues": list(semantics["reflection_issues"]),
                "tracked_defects": [],
                "issues": ["linked in ledger but no OBPI file found", *list(semantics["issues"])],
                "issue_details": _issue_details(
                    ["linked in ledger but no OBPI file found", *list(semantics["issues"])],
                    [],
                ),
            }
        )

    for obpi_id, obpi_file in sorted(obpi_files.items()):
        inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id=obpi_id, graph=graph)
        rows.append(
            {
                "id": obpi_id,
                "linked_in_ledger": obpi_id in expected_obpis,
                "found_file": True,
                "file": str(obpi_file.relative_to(project_root)),
                "completed": bool(inspection["completed"]),
                "ledger_completed": bool(inspection["ledger_completed"]),
                "file_completed": bool(inspection["file_completed"]),
                "evidence_ok": bool(inspection["evidence_ok"]),
                "implementation_evidence_ok": bool(inspection["implementation_evidence_ok"]),
                "key_proof_ok": bool(inspection["key_proof_ok"]),
                "human_attestation": dict(inspection["human_attestation"]),
                "runtime_state": inspection["runtime_state"],
                "proof_state": inspection["proof_state"],
                "attestation_requirement": inspection["attestation_requirement"],
                "attestation_state": inspection["attestation_state"],
                "req_proof_state": inspection["req_proof_state"],
                "req_proof_inputs": list(inspection["req_proof_inputs"]),
                "req_proof_summary": dict(inspection["req_proof_summary"]),
                "anchor_state": inspection["anchor_state"],
                "anchor_commit": inspection["anchor_commit"],
                "current_head": inspection["current_head"],
                "anchor_issues": list(inspection["anchor_issues"]),
                "anchor_drift_files": list(inspection["anchor_drift_files"]),
                "frontmatter_status": inspection["frontmatter_status"],
                "brief_status": inspection["brief_status"],
                "reflection_issues": list(inspection["reflection_issues"]),
                "tracked_defects": list(inspection["tracked_defects"]),
                "issues": list(inspection["issues"]),
                "issue_details": list(inspection["issue_details"]),
            }
        )

    return sorted(rows, key=lambda row: cast(str, row.get("id", "")))


def _obpi_row_complete(row: dict[str, Any]) -> bool:
    """Return True when an OBPI row is complete.

    Ledger receipts are authoritative: if the ledger records a completion receipt
    the OBPI counts as complete even when the brief file is absent.  Falls back to
    the composite ``completed`` flag (ledger + evidence + attestation) when the
    brief file is present.
    """
    if row.get("ledger_completed"):
        return True
    return bool(row.get("found_file")) and bool(row.get("completed"))


def _summarize_obpi_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive completion summary for a collection of OBPI status rows."""
    total = len(rows)
    completed = sum(1 for row in rows if _obpi_row_complete(row))
    missing_files = sum(1 for row in rows if not row.get("found_file"))
    outstanding_ids = [cast(str, row.get("id", "")) for row in rows if not _obpi_row_complete(row)]

    if total == 0:
        unit_status = "unscoped"
    elif completed == total:
        unit_status = "completed"
    elif completed == 0:
        unit_status = "pending"
    else:
        unit_status = "in_progress"

    return {
        "total": total,
        "completed": completed,
        "incomplete": total - completed,
        "missing_files": missing_files,
        "unit_status": unit_status,
        "outstanding_ids": sorted(outstanding_ids),
    }


def _obpi_closeout_blockers(row: dict[str, Any]) -> list[str]:
    """Return closeout-blocking messages for one OBPI row."""
    obpi_id = cast(str, row.get("id", "(unknown)"))
    issues = [
        str(issue)
        for issue in cast(list[str], row.get("issue_details", row.get("issues", [])))
        if str(issue).strip()
    ]
    if issues:
        return [f"{obpi_id}: {issue}" for issue in issues]
    if _obpi_row_complete(row):
        return []

    runtime_state = str(row.get("runtime_state", "pending"))
    proof_state = str(row.get("proof_state", "missing"))
    return [f"{obpi_id}: not closeout-ready (runtime={runtime_state}, proof={proof_state})"]


def _adr_closeout_readiness(obpi_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive fail-closed ADR closeout readiness from linked OBPI rows."""
    blockers: list[str] = []
    blocking_ids: list[str] = []
    for row in obpi_rows:
        row_blockers = _obpi_closeout_blockers(row)
        if not row_blockers:
            continue
        blockers.extend(row_blockers)
        blocking_ids.append(cast(str, row.get("id", "")))

    return {
        "ready": not blockers,
        "blockers": blockers,
        "blocking_ids": sorted(obpi_id for obpi_id in blocking_ids if obpi_id),
    }


def _apply_obpi_lifecycle_overrides(
    adr_id: str, payload: dict[str, Any], obpi_summary: dict[str, Any]
) -> None:
    """Enforce OBPI-first completion semantics on lifecycle status surfaces."""
    if _is_pool_adr_id(adr_id):
        return

    total = int(obpi_summary.get("total", 0))
    unit_status = str(obpi_summary.get("unit_status", "unscoped"))
    lifecycle_status = str(payload.get("lifecycle_status", "Pending"))

    if total > 0 and unit_status != "completed" and lifecycle_status in {"Completed", "Validated"}:
        payload["lifecycle_status"] = "Pending"


# ---------------------------------------------------------------------------
# Single-OBPI status entry
# ---------------------------------------------------------------------------


def _build_obpi_status_entry(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    obpi_id: str,
) -> dict[str, Any]:
    """Build enriched runtime status payload for one OBPI."""
    graph = ledger.get_artifact_graph()
    raw_info = graph.get(obpi_id)
    _resolved_id, obpi_file = resolve_obpi(project_root, config, ledger, obpi_id)
    linked_in_ledger = bool(raw_info and raw_info.get("type") == "obpi")
    info: dict[str, Any] = raw_info if linked_in_ledger and isinstance(raw_info, dict) else {}

    parent_adr = info.get("parent")
    if obpi_file and not isinstance(parent_adr, str):
        metadata = parse_artifact_metadata(obpi_file)
        parent_adr = metadata.get("parent")
    result: dict[str, Any] = {
        "obpi": obpi_id,
        "id": obpi_id,
        "parent_adr": parent_adr,
        "linked_in_ledger": linked_in_ledger,
        "found_file": obpi_file is not None,
        "file": str(obpi_file.relative_to(project_root)) if obpi_file else None,
    }

    if obpi_file is None:
        semantics = derive_obpi_semantics(
            info,
            obpi_id=obpi_id,
            artifact_graph=graph,
            found_file=False,
            file_completed=False,
            implementation_evidence_ok=False,
            key_proof_ok=False,
            project_root=project_root,
        )
        result.update(
            {
                "completed": bool(semantics["completed"]),
                "ledger_completed": bool(semantics["ledger_completed"]),
                "file_completed": False,
                "evidence_ok": bool(semantics["evidence_ok"]),
                "implementation_evidence_ok": False,
                "key_proof_ok": False,
                "human_attestation": {"present": False, "valid": False},
                "runtime_state": semantics["runtime_state"],
                "proof_state": semantics["proof_state"],
                "attestation_requirement": semantics["attestation_requirement"],
                "attestation_state": semantics["attestation_state"],
                "req_proof_state": semantics["req_proof_state"],
                "req_proof_inputs": list(semantics["req_proof_inputs"]),
                "req_proof_summary": dict(semantics["req_proof_summary"]),
                "anchor_state": semantics["anchor_state"],
                "anchor_commit": semantics["anchor_commit"],
                "current_head": semantics["current_head"],
                "anchor_issues": list(semantics["anchor_issues"]),
                "anchor_drift_files": list(semantics["anchor_drift_files"]),
                "frontmatter_status": None,
                "brief_status": None,
                "reflection_issues": list(semantics["reflection_issues"]),
                "tracked_defects": [],
                "issues": ["linked in ledger but no OBPI file found", *list(semantics["issues"])],
                "issue_details": _issue_details(
                    ["linked in ledger but no OBPI file found", *list(semantics["issues"])],
                    [],
                ),
            }
        )
        return result

    inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id=obpi_id, graph=graph)
    result.update(
        {
            "completed": bool(inspection["completed"]),
            "ledger_completed": bool(inspection["ledger_completed"]),
            "file_completed": bool(inspection["file_completed"]),
            "evidence_ok": bool(inspection["evidence_ok"]),
            "implementation_evidence_ok": bool(inspection["implementation_evidence_ok"]),
            "key_proof_ok": bool(inspection["key_proof_ok"]),
            "human_attestation": dict(inspection["human_attestation"]),
            "runtime_state": inspection["runtime_state"],
            "proof_state": inspection["proof_state"],
            "attestation_requirement": inspection["attestation_requirement"],
            "attestation_state": inspection["attestation_state"],
            "req_proof_state": inspection["req_proof_state"],
            "req_proof_inputs": list(inspection["req_proof_inputs"]),
            "req_proof_summary": dict(inspection["req_proof_summary"]),
            "anchor_state": inspection["anchor_state"],
            "anchor_commit": inspection["anchor_commit"],
            "current_head": inspection["current_head"],
            "anchor_issues": list(inspection["anchor_issues"]),
            "anchor_drift_files": list(inspection["anchor_drift_files"]),
            "frontmatter_status": inspection["frontmatter_status"],
            "brief_status": inspection["brief_status"],
            "reflection_issues": list(inspection["reflection_issues"]),
            "tracked_defects": list(inspection["tracked_defects"]),
            "issues": list(inspection["issues"]),
            "issue_details": list(inspection["issue_details"]),
        }
    )
    return result


# ---------------------------------------------------------------------------
# OBPI rendering helpers
# ---------------------------------------------------------------------------


def _render_obpi_unit_status(unit_status: str) -> str:
    if unit_status == "completed":
        return "[green]COMPLETED[/green]"
    if unit_status == "in_progress":
        return "[yellow]IN PROGRESS[/yellow]"
    if unit_status == "pending":
        return "[yellow]PENDING[/yellow]"
    return "[cyan]UNSCOPED[/cyan]"


def _render_obpi_runtime_state(runtime_state: str, found_file: bool) -> str:
    if runtime_state == "validated":
        return "[green]VALIDATED[/green]"
    if runtime_state == "attested_completed":
        return "[green]ATTESTED COMPLETED[/green]"
    if runtime_state == "completed":
        return "[green]COMPLETED[/green]"
    if runtime_state == "in_progress":
        return "[yellow]IN PROGRESS[/yellow]"
    if runtime_state == "drift":
        return "[red]DRIFT[/red]"
    if not found_file:
        return "[red]MISSING FILE[/red]"
    return "[yellow]PENDING[/yellow]"


def _render_obpi_row_status(row: dict[str, Any]) -> str:
    obpi_id = cast(str, row.get("id", "(unknown)"))
    runtime_state = str(row.get("runtime_state", "pending"))
    issues = cast(list[str], row.get("issue_details", row.get("issues", [])))
    status_label = _render_obpi_runtime_state(runtime_state, bool(row.get("found_file")))

    if issues:
        issues_text = ", ".join(issues)
        return f"{obpi_id}: {status_label} ({issues_text})"
    return f"{obpi_id}: {status_label}"


def _print_status_obpi_section(
    obpi_rows: list[dict[str, Any]],
    obpi_summary: dict[str, Any],
) -> None:
    """Render OBPI completion block for one ADR status row."""
    obpi_total = cast(int, obpi_summary.get("total", 0))
    obpi_completed = cast(int, obpi_summary.get("completed", 0))
    obpi_unit_status = cast(str, obpi_summary.get("unit_status", "unscoped"))
    obpi_open_rows = [row for row in obpi_rows if not _obpi_row_complete(row)]

    console.print(f"  OBPI Unit:       {_render_obpi_unit_status(obpi_unit_status)}")
    console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")
    if obpi_total == 0:
        console.print("  OBPIs:           none linked")
        return
    if not obpi_open_rows:
        console.print("  OBPIs:           all linked OBPIs completed with evidence")
        return

    console.print(f"  OBPI Open:       {len(obpi_open_rows)} remaining")
    preview_rows = obpi_open_rows[:3]
    for row in preview_rows:
        console.print(f"    - {_render_obpi_row_status(row)}")
    hidden_count = len(obpi_open_rows) - len(preview_rows)
    if hidden_count > 0:
        console.print(f"    - ... and {hidden_count} more")


def _render_obpi_status_details(result: dict[str, Any]) -> None:
    """Render the focused OBPI runtime status view."""
    obpi_id = cast(str, result["obpi"])
    parent_adr = result.get("parent_adr")
    file_path = result.get("file") or "(missing)"
    runtime_state = str(result.get("runtime_state", "pending"))
    proof_state = str(result.get("proof_state", "missing"))
    attestation_state = str(result.get("attestation_state", "not_required"))
    anchor_state = str(result.get("anchor_state", "not_applicable"))
    anchor_commit = result.get("anchor_commit") or "(none)"
    current_head = result.get("current_head") or "(unknown)"
    issues = cast(list[str], result.get("issue_details", result.get("issues", [])))

    console.print(f"[bold]{obpi_id}[/bold]")
    if isinstance(parent_adr, str) and parent_adr:
        console.print(f"  Parent ADR: {parent_adr}")
    console.print(f"  File: {file_path}")
    console.print(
        "  Runtime State: "
        + _render_obpi_runtime_state(runtime_state, bool(result.get("found_file")))
    )
    console.print(f"  Proof State: {proof_state}")
    console.print(f"  Attestation State: {attestation_state}")
    console.print(f"  Anchor State: {anchor_state}")
    console.print(f"  Anchor Commit: {anchor_commit}")
    console.print(f"  Current HEAD: {current_head}")
    console.print(
        "  Completion: "
        + ("[green]COMPLETE[/green]" if result.get("completed") else "[yellow]PENDING[/yellow]")
    )
    console.print("  Issues:")
    if not issues:
        console.print("    - none")
        return
    for issue in issues:
        console.print(f"    - {issue}")
