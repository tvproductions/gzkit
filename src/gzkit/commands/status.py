"""Status command implementation."""

import json
import re
from pathlib import Path
from typing import Any, cast

from rich import box
from rich.table import Table

from gzkit.commands.common import (
    GzCliError,
    _apply_pool_adr_status_overrides,
    _gate4_na_reason,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
)
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    parse_frontmatter_value,
    resolve_adr_lane,
)
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts


def _render_gate_status(gate_status: str | None) -> str:
    if gate_status == "pass":
        return "[green]PASS[/green]"
    if gate_status == "fail":
        return "[red]FAIL[/red]"
    if gate_status == "n/a":
        return "[cyan]N/A[/cyan]"
    return "[yellow]PENDING[/yellow]"


def _qc_readiness(
    gates: dict[str, str], lane: str, obpi_summary: dict[str, Any]
) -> tuple[str, list[str]]:
    """Derive summarized QC readiness and pending checkpoints from gate statuses."""
    blockers: list[str] = []
    obpi_total = int(obpi_summary.get("total", 0))
    obpi_unit_status = str(obpi_summary.get("unit_status", "unscoped"))
    if obpi_total > 0 and obpi_unit_status != "completed":
        blockers.append("OBPI completion")

    if gates.get("2") != "pass":
        blockers.append("TDD")
    if lane == "heavy":
        if gates.get("3") != "pass":
            blockers.append("Docs")
        if gates.get("4") not in {"pass", "n/a"}:
            blockers.append("BDD")
        if gates.get("5") != "pass":
            blockers.append("Human attestation")
    readiness = "ready" if not blockers else "pending"
    return readiness, blockers


def _render_qc_readiness(readiness: str, blockers: list[str]) -> str:
    if readiness == "ready":
        return "[green]READY[/green]"
    return f"[yellow]PENDING[/yellow] (pending: {', '.join(blockers)})"


def _render_pending_checks_cell(blockers: list[str]) -> str:
    """Render compact pending-check codes for table view."""
    if not blockers:
        return "-"

    code_map = {
        "OBPI completion": "O",
        "TDD": "T",
        "Docs": "D",
        "BDD": "B",
        "Human attestation": "H",
    }
    return ",".join(code_map.get(blocker, "?") for blocker in blockers)


def _build_adr_status_entry(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
    info: dict[str, Any],
) -> dict[str, Any]:
    """Build enriched ADR status payload for one ADR."""
    entry = dict(info)
    lane = resolve_adr_lane(entry, config.mode)
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)
    gate4_na = _gate4_na_reason(project_root, lane)
    entry["lane"] = lane
    entry["gates"] = {
        "1": "pass",
        "2": gate_statuses.get(2, "pending"),
        "3": gate_statuses.get(3, "pending") if lane == "heavy" else "n/a",
        "4": "n/a" if gate4_na is not None else gate_statuses.get(4, "pending"),
        "5": "pass" if entry.get("attested") else "pending",
    }
    if gate4_na is not None:
        entry["gate4_na_reason"] = gate4_na

    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    entry.update(Ledger.derive_adr_semantics(entry))
    _apply_pool_adr_status_overrides(adr_id, entry)
    entry["obpis"] = obpi_rows
    obpi_summary = _summarize_obpi_rows(obpi_rows)
    entry["obpi_summary"] = obpi_summary
    _apply_obpi_lifecycle_overrides(adr_id, entry, obpi_summary)
    return entry


def _collect_adr_statuses(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    graph: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Collect enriched status payload for each ADR in the graph."""
    adrs: dict[str, dict[str, Any]] = {}
    for adr_id, info in graph.items():
        if info.get("type") != "adr":
            continue
        adrs[adr_id] = _build_adr_status_entry(project_root, config, ledger, adr_id, info)
    return adrs


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


def _print_status_gate_section(
    info: dict[str, Any],
    lane: str,
    gates: dict[str, str],
    attested: bool,
    attestation_term: Any,
) -> None:
    """Render optional gate-by-gate diagnostics for one ADR."""
    console.print("  Gate 1 (ADR):   [green]PASS[/green]")
    console.print(f"  Gate 2 (TDD):   {_render_gate_status(gates.get('2'))}")
    if lane != "heavy":
        return

    console.print(f"  Gate 3 (Docs):  {_render_gate_status(gates.get('3'))}")
    console.print(f"  Gate 4 (BDD):   {_render_gate_status(gates.get('4'))}")
    if gates.get("4") == "n/a":
        console.print(f"                 ({info.get('gate4_na_reason')})")

    if attested:
        detail = f" ({attestation_term})" if attestation_term else ""
        console.print(f"  Gate 5 (Human): [green]PASS[/green]{detail}")
        return
    console.print("  Gate 5 (Human): [yellow]PENDING[/yellow]")


def _render_status_row(
    adr_id: str, info: dict[str, Any], default_mode: str, show_gates: bool
) -> None:
    """Render one ADR row for text status output."""
    attested = bool(info.get("attested", False))
    lifecycle_status = info.get("lifecycle_status", "Pending")
    lane = cast(str, info.get("lane", default_mode))
    gates = cast(dict[str, str], info.get("gates", {}))
    attestation_term = info.get("attestation_term")
    obpi_rows = cast(list[dict[str, Any]], info.get("obpis", []))
    obpi_summary = cast(dict[str, Any], info.get("obpi_summary", {}))

    console.print(f"[bold]{adr_id}[/bold] ({lifecycle_status})")
    _print_status_obpi_section(obpi_rows, obpi_summary)

    qc_readiness, qc_blockers = _qc_readiness(gates, lane, obpi_summary)
    console.print(f"  QC Readiness:   {_render_qc_readiness(qc_readiness, qc_blockers)}")
    if show_gates:
        _print_status_gate_section(info, lane, gates, attested, attestation_term)
    console.print()


def _render_status_table(adrs: dict[str, dict[str, Any]], default_mode: str) -> None:
    """Render ADR status as a stable tabular summary."""
    table = Table(title="ADR Status", box=box.ASCII)
    table.add_column("ADR", overflow="ellipsis")
    table.add_column("Life", no_wrap=True)
    table.add_column("Lane", no_wrap=True)
    table.add_column("OBPI", justify="right", no_wrap=True)
    table.add_column("Unit", no_wrap=True)
    table.add_column("QC", no_wrap=True)
    table.add_column("Checks", no_wrap=True)
    table.row_styles = ["none", "dim"]

    for adr_id, info in sorted(adrs.items()):
        lane = cast(str, info.get("lane", default_mode))
        gates = cast(dict[str, str], info.get("gates", {}))
        obpi_summary = cast(dict[str, Any], info.get("obpi_summary", {}))
        lifecycle_status = cast(str, info.get("lifecycle_status", "Pending"))

        obpi_total = cast(int, obpi_summary.get("total", 0))
        obpi_completed = cast(int, obpi_summary.get("completed", 0))
        obpi_unit_status = cast(str, obpi_summary.get("unit_status", "unscoped"))
        qc_readiness, qc_blockers = _qc_readiness(gates, lane, obpi_summary)
        qc_label = "READY" if qc_readiness == "ready" else "PENDING"

        table.add_row(
            adr_id,
            lifecycle_status,
            lane.upper(),
            f"{obpi_completed}/{obpi_total}",
            obpi_unit_status.upper(),
            qc_label,
            _render_pending_checks_cell(qc_blockers),
        )

    console.print(table)
    console.print("Checks legend: O=OBPI completion, T=TDD, D=Docs, B=BDD, H=Human attestation")


def status(as_json: bool, show_gates: bool, as_table: bool) -> None:
    """Display OBPI progress, lifecycle, and gate readiness across ADRs."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    pending = ledger.get_pending_attestations()
    graph = ledger.get_artifact_graph()
    adrs = _collect_adr_statuses(project_root, config, ledger, graph)

    if as_json:
        result = {
            "mode": config.mode,
            "adrs": adrs,
            "pending_attestations": pending,
        }
        print(json.dumps(result, indent=2))
        return

    console.print(f"[bold]Lane: {config.mode}[/bold]\n")

    if not adrs:
        console.print("No ADRs found. Create one with 'gz plan'.")
        return

    if as_table:
        _render_status_table(adrs, config.mode)
        return

    for adr_id, info in sorted(adrs.items()):
        _render_status_row(adr_id, info, config.mode, show_gates)


def _markdown_label_value(content: str, label: str) -> str | None:
    pattern = rf"^\*\*{re.escape(label)}:\*\*\s*(.+)$"
    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def _has_substantive_implementation_summary(content: str) -> bool:
    match = re.search(
        r"^### Implementation Summary\s*$([\s\S]*?)(?:^### |\n---|\Z)",
        content,
        flags=re.MULTILINE,
    )
    if not match:
        return False

    section = match.group(1)
    # Keep matching line-local so empty values cannot borrow content from the next line.
    bullet_matches = re.findall(r"^- [^:\n]+:[ \t]*(.+)$", section, flags=re.MULTILINE)
    for value in bullet_matches:
        normalized = value.strip().lower()
        if normalized and normalized not in {"-", "tbd", "(none)", "n/a"}:
            return True
    return False


def _inspect_obpi_brief(
    obpi_file: Path,
    obpi_id: str | None = None,
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    content = obpi_file.read_text(encoding="utf-8")
    frontmatter_status = (parse_frontmatter_value(content, "status") or "").strip().lower()
    brief_status = (_markdown_label_value(content, "Brief Status") or "").strip().lower()

    # Ledger-First Completion Consumption
    ledger_completed = False
    if obpi_id and graph:
        info = graph.get(obpi_id, {})
        ledger_completed = bool(info.get("ledger_completed"))

    # Completion is earned via ledger proof, but also reflected in file
    file_completed = frontmatter_status == "completed" or brief_status == "completed"
    completed = ledger_completed

    evidence_ok = _has_substantive_implementation_summary(content)

    reasons: list[str] = []
    if not ledger_completed:
        reasons.append("ledger proof of completion is missing")
    if not file_completed:
        reasons.append("brief file status is not Completed")
    if not evidence_ok:
        reasons.append("implementation evidence is missing or placeholder")

    return {
        "completed": completed,
        "ledger_completed": ledger_completed,
        "file_completed": file_completed,
        "evidence_ok": evidence_ok,
        "frontmatter_status": frontmatter_status or None,
        "brief_status": brief_status or None,
        "reasons": reasons,
    }


def _collect_obpi_files_for_adr(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
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
    ]

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    obpi_files: dict[str, Path] = {}
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        obpi_id = ledger.canonicalize_id(metadata.get("id", obpi_file.stem))
        parent = metadata.get("parent", "")
        canonical_parent = ledger.canonicalize_id(parent) if parent else ""
        if canonical_parent == canonical_adr or obpi_id in expected_obpis:
            obpi_files[obpi_id] = obpi_file

    return obpi_files, expected_obpis


def _adr_obpi_status_rows(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
) -> list[dict[str, Any]]:
    """Build per-OBPI status rows for a target ADR."""
    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    rows: list[dict[str, Any]] = []

    for expected_id in sorted(expected_obpis):
        if expected_id in obpi_files:
            continue
        rows.append(
            {
                "id": expected_id,
                "linked_in_ledger": True,
                "found_file": False,
                "file": None,
                "completed": False,
                "evidence_ok": False,
                "frontmatter_status": None,
                "brief_status": None,
                "issues": ["linked in ledger but no OBPI file found"],
            }
        )

    graph = ledger.get_artifact_graph()
    for obpi_id, obpi_file in sorted(obpi_files.items()):
        inspection = _inspect_obpi_brief(obpi_file, obpi_id=obpi_id, graph=graph)
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
                "frontmatter_status": inspection["frontmatter_status"],
                "brief_status": inspection["brief_status"],
                "issues": list(inspection["reasons"]),
            }
        )

    return sorted(rows, key=lambda row: cast(str, row.get("id", "")))


def _obpi_row_complete(row: dict[str, Any]) -> bool:
    """Return True when an OBPI row is complete with implementation evidence."""
    return (
        bool(row.get("found_file")) and bool(row.get("completed")) and bool(row.get("evidence_ok"))
    )


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


def _render_obpi_unit_status(unit_status: str) -> str:
    if unit_status == "completed":
        return "[green]COMPLETED[/green]"
    if unit_status == "in_progress":
        return "[yellow]IN PROGRESS[/yellow]"
    if unit_status == "pending":
        return "[yellow]PENDING[/yellow]"
    return "[cyan]UNSCOPED[/cyan]"


def _render_obpi_row_status(row: dict[str, Any]) -> str:
    obpi_id = cast(str, row.get("id", "(unknown)"))
    if not row.get("found_file"):
        return f"{obpi_id}: [red]MISSING FILE[/red]"
    if _obpi_row_complete(row):
        return f"{obpi_id}: [green]COMPLETED[/green] + evidence"

    issues = cast(list[str], row.get("issues", []))
    status_label = "[yellow]INCOMPLETE[/yellow]"

    # Detect Drift
    if row.get("ledger_completed") and not row.get("file_completed"):
        status_label = "[red]DRIFT[/red] (ledger says Completed, file says Draft)"
    elif row.get("ledger_completed") and not row.get("evidence_ok"):
        status_label = "[red]DRIFT[/red] (ledger says Completed, evidence is placeholder)"
    elif row.get("file_completed") and not row.get("ledger_completed"):
        status_label = "[red]DRIFT[/red] (file says Completed, ledger proof missing)"

    if issues:
        issues_text = ", ".join(issues)
        return f"{obpi_id}: {status_label} ({issues_text})"
    return f"{obpi_id}: {status_label}"


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


def adr_status_cmd(adr: str, as_json: bool, show_gates: bool) -> None:
    """Display focused OBPI progress, lifecycle, and gate readiness for one ADR."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    _adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id)
    if not info or info.get("type") != "adr":
        raise GzCliError(f"ADR not found in ledger: {adr_id}")

    lane = resolve_adr_lane(info, config.mode)
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)
    gate4_na = _gate4_na_reason(project_root, lane)
    semantics = Ledger.derive_adr_semantics(info)
    result = {
        "adr": adr_id,
        "mode": config.mode,
        "lane": lane,
        "attested": bool(info.get("attested")),
        "attestation_status": info.get("attestation_status"),
        "attestation_term": semantics["attestation_term"],
        "lifecycle_status": semantics["lifecycle_status"],
        "closeout_phase": semantics["closeout_phase"],
        "closeout_initiated": bool(info.get("closeout_initiated")),
        "validated": bool(info.get("validated")),
        "gates": {
            "1": "pass",
            "2": gate_statuses.get(2, "pending"),
            "3": gate_statuses.get(3, "pending") if lane == "heavy" else "n/a",
            "4": "n/a" if gate4_na is not None else gate_statuses.get(4, "pending"),
            "5": "pass" if info.get("attested") else "pending",
        },
    }
    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    _apply_pool_adr_status_overrides(adr_id, result)
    result["obpis"] = obpi_rows
    obpi_summary = _summarize_obpi_rows(obpi_rows)
    result["obpi_summary"] = obpi_summary
    _apply_obpi_lifecycle_overrides(adr_id, result, obpi_summary)
    if gate4_na is not None:
        result["gate4_na_reason"] = gate4_na

    if as_json:
        print(json.dumps(result, indent=2))
        return

    console.print(f"[bold]{adr_id}[/bold]")
    console.print(f"  Lifecycle: {result['lifecycle_status']}")
    console.print(f"  Closeout Phase: {result['closeout_phase']}")
    obpi_summary = cast(dict[str, Any], result.get("obpi_summary", {}))
    obpi_total = cast(int, obpi_summary.get("total", 0))
    obpi_completed = cast(int, obpi_summary.get("completed", 0))
    obpi_unit_status = cast(str, obpi_summary.get("unit_status", "unscoped"))
    console.print(f"  OBPI Unit: {_render_obpi_unit_status(obpi_unit_status)}")
    console.print(f"  OBPI Completion: {obpi_completed}/{obpi_total} complete")
    console.print("  OBPIs:")
    obpi_rows = cast(list[dict[str, Any]], result.get("obpis", []))
    if not obpi_rows:
        console.print("    - none linked")
    else:
        for row in obpi_rows:
            console.print(f"    - {_render_obpi_row_status(row)}")

    gates = cast(dict[str, str], result.get("gates", {}))
    qc_readiness, qc_blockers = _qc_readiness(gates, lane, obpi_summary)
    console.print(f"  QC Readiness: {_render_qc_readiness(qc_readiness, qc_blockers)}")

    if show_gates:
        console.print("  Gate 1 (ADR):   [green]PASS[/green]")
        console.print(f"  Gate 2 (TDD):   {_render_gate_status(result['gates'].get('2'))}")
        if lane == "heavy":
            console.print(f"  Gate 3 (Docs):  {_render_gate_status(result['gates'].get('3'))}")
            console.print(f"  Gate 4 (BDD):   {_render_gate_status(result['gates'].get('4'))}")
            if result["gates"].get("4") == "n/a":
                console.print(f"                 ({gate4_na})")
            is_attested = bool(result.get("attested"))
            gate5_detail = (
                f" ({result['attestation_term']})" if result.get("attestation_term") else ""
            )
            console.print(
                "  Gate 5 (Human): "
                + ("[green]PASS[/green]" if is_attested else "[yellow]PENDING[/yellow]")
                + (gate5_detail if is_attested else "")
            )
