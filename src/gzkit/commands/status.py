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
    resolve_adr_ledger_id,
    resolve_obpi,
)
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    derive_obpi_semantics,
    parse_frontmatter_value,
    resolve_adr_lane,
)
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts

ADR_SEMVER_STATUS_ID_RE = re.compile(
    r"^ADR-(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>(?:[.-][A-Za-z0-9][A-Za-z0-9.-]*)?)$"
)


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
    obpi_index: list[tuple[str, str, Path]] | None = None,
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

    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id, obpi_index=obpi_index)
    entry.update(Ledger.derive_adr_semantics(entry))
    _apply_pool_adr_status_overrides(adr_id, entry)
    entry["obpis"] = obpi_rows
    obpi_summary = _summarize_obpi_rows(obpi_rows)
    entry["obpi_summary"] = obpi_summary
    closeout_readiness = _adr_closeout_readiness(obpi_rows)
    entry["closeout_ready"] = bool(closeout_readiness["ready"])
    entry["closeout_blockers"] = list(closeout_readiness["blockers"])
    _apply_obpi_lifecycle_overrides(adr_id, entry, obpi_summary)
    return entry


def _adr_status_sort_key(adr_id: str) -> tuple[int, int, int, int, int, str]:
    """Sort ADR ids semver-first so 0.10.0 correctly follows 0.9.0."""
    match = ADR_SEMVER_STATUS_ID_RE.match(adr_id)
    if match:
        suffix = match.group("suffix")
        return (
            0,
            int(match.group("major")),
            int(match.group("minor")),
            int(match.group("patch")),
            0 if not suffix else 1,
            suffix,
        )
    if _is_pool_adr_id(adr_id):
        return (1, 0, 0, 0, 0, adr_id)
    return (2, 0, 0, 0, 0, adr_id)


def _collect_adr_statuses(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    graph: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Collect enriched status payload for each ADR in the graph."""
    obpi_index = _build_obpi_index(project_root, config, ledger)
    adrs: dict[str, dict[str, Any]] = {}
    for adr_id, info in graph.items():
        if info.get("type") != "adr":
            continue
        adrs[adr_id] = _build_adr_status_entry(
            project_root, config, ledger, adr_id, info, obpi_index=obpi_index
        )
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
    """Render ADR status as a stable tabular summary with pool ADRs in a separate table."""
    versioned: list[tuple[str, dict[str, Any]]] = []
    pool: list[tuple[str, dict[str, Any]]] = []
    for adr_id, info in sorted(adrs.items(), key=lambda item: _adr_status_sort_key(item[0])):
        if _is_pool_adr_id(adr_id):
            pool.append((adr_id, info))
        else:
            versioned.append((adr_id, info))

    _render_adr_table("ADR Status", versioned, default_mode)
    if pool:
        console.print()
        _render_adr_table("Pool ADRs", pool, default_mode)
    console.print("Checks legend: O=OBPI completion, T=TDD, D=Docs, B=BDD, H=Human attestation")


def _render_adr_table(
    title: str,
    rows: list[tuple[str, dict[str, Any]]],
    default_mode: str,
) -> None:
    """Render a single ADR status table with the given title and rows."""
    table = Table(title=title, box=box.ROUNDED, padding=(0, 0))
    table.add_column("ADR", overflow="ellipsis")
    table.add_column("Life", no_wrap=True)
    table.add_column("Lane", no_wrap=True)
    table.add_column("OBPI", justify="right", no_wrap=True)
    table.add_column("Unit", no_wrap=True)
    table.add_column("QC", no_wrap=True)
    table.add_column("Checks", no_wrap=True)
    table.row_styles = ["none", "dim"]

    for adr_id, info in rows:
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


def status(as_json: bool, show_gates: bool, as_table: bool) -> None:
    """Display OBPI progress, lifecycle, and gate readiness across ADRs."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    pending = ledger.get_pending_attestations()
    graph = ledger.get_artifact_graph()
    adrs = _collect_adr_statuses(project_root, config, ledger, graph)
    adrs = dict(sorted(adrs.items(), key=lambda item: _adr_status_sort_key(item[0])))

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

    for adr_id, info in adrs.items():
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


def _section_body(content: str, heading: str) -> str | None:
    lines = content.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        if line.strip() in {f"## {heading}", f"### {heading}"}:
            start_index = index + 1
            break

    if start_index is None:
        return None

    end_index = len(lines)
    for index in range(start_index, len(lines)):
        stripped = lines[index].strip()
        if stripped == "---" or re.match(r"^(##|###) ", stripped):
            end_index = index
            break

    body = "\n".join(lines[start_index:end_index]).strip()
    if body:
        return body
    return None


def _section_body_with_prefix(content: str, heading_prefix: str) -> str | None:
    lines = content.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"## {heading_prefix}") or stripped.startswith(
            f"### {heading_prefix}"
        ):
            start_index = index + 1
            break

    if start_index is None:
        return None

    end_index = len(lines)
    for index in range(start_index, len(lines)):
        stripped = lines[index].strip()
        if stripped == "---" or re.match(r"^(##|###) ", stripped):
            end_index = index
            break

    body = "\n".join(lines[start_index:end_index]).strip()
    if body:
        return body
    return None


def _has_substantive_section(content: str, heading: str) -> bool:
    body = _section_body(content, heading)
    if not body:
        return False
    normalized = body.strip().lower()
    return normalized not in {"", "-", "...", "tbd", "(none)", "n/a", "paste test output here"}


def _has_substantive_body(body: str | None) -> bool:
    if not body:
        return False
    normalized = body.strip().lower()
    return normalized not in {"", "-", "...", "tbd", "(none)", "n/a", "paste test output here"}


def _implementation_summary_validation_commands(content: str) -> str | None:
    body = _section_body(content, "Implementation Summary")
    if not body:
        return None

    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("- Validation commands run:"):
            continue

        collected = [line.removeprefix("- Validation commands run:").strip()]
        for follow_line in lines[index + 1 :]:
            if follow_line.startswith("- "):
                break
            collected.append(follow_line.rstrip())

        candidate = "\n".join(part for part in collected if part.strip()).strip()
        if _has_substantive_body(candidate):
            return candidate
    return None


def _resolved_key_proof_body(content: str) -> str | None:
    for heading in ("Key Proof", "Verification", "Gate Evidence"):
        body = _section_body(content, heading)
        if body and _has_substantive_section(content, heading):
            return body
    prefixed_verification = _section_body_with_prefix(content, "Verification")
    if _has_substantive_body(prefixed_verification):
        return prefixed_verification
    validation_commands = _implementation_summary_validation_commands(content)
    if _has_substantive_body(validation_commands):
        return validation_commands
    return None


def _extract_human_attestation(content: str) -> dict[str, Any]:
    body = _section_body(content, "Human Attestation")
    if not body:
        return {"present": False, "valid": False}

    attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
    attestation_match = re.search(r"^- Attestation:\s*(.+)$", body, flags=re.MULTILINE)
    date_match = re.search(r"^- Date:\s*`?(\d{4}-\d{2}-\d{2})`?$", body, flags=re.MULTILINE)

    attestor_raw = attestor_match.group(1).strip() if attestor_match else None
    # Strip markdown backticks and trailing annotations (e.g. "— required ...")
    attestor = (
        attestor_raw.strip("`").split("—")[0].split(" — ")[0].strip() if attestor_raw else None
    )
    attestation_text = attestation_match.group(1).strip() if attestation_match else None
    attestation_date = date_match.group(1).strip() if date_match else None
    placeholder_names = {"n/a", "tbd", "todo", "none", "-", "...", ""}
    valid = bool(
        attestor
        and attestor.lower() not in placeholder_names
        and attestation_text
        and attestation_date
    )
    return {
        "present": True,
        "valid": valid,
        "attestor": attestor,
        "attestation_text": attestation_text,
        "date": attestation_date,
    }


def _extract_tracked_defects(content: str) -> list[dict[str, Any]]:
    """Parse brief-local tracked GitHub defects from a dedicated section."""
    body = _section_body(content, "Tracked Defects")
    if not body:
        return []

    defects: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue

        candidate = stripped[2:].strip()
        if candidate.startswith(("[ ] ", "[x] ", "[X] ")):
            candidate = candidate[4:].strip()
        candidate = re.sub(r"^\[(?P<label>[^\]]+)\]\([^)]+\)", r"\g<label>", candidate)
        candidate = re.sub(
            r"^https?://github\.com/[^/]+/[^/]+/issues/(?P<number>\d+)",
            r"#\g<number>",
            candidate,
        )

        match = re.search(r"(?P<prefix>GHI-|#)(?P<number>\d+)", candidate, flags=re.IGNORECASE)
        if not match:
            continue

        issue_id = f"GHI-{int(match.group('number'))}"
        if issue_id in seen_ids:
            continue

        state_match = re.search(r"\((open|closed)\)", candidate, flags=re.IGNORECASE)
        state = state_match.group(1).lower() if state_match else "unknown"
        summary_match = re.match(
            r".*?(?:GHI-|#)\d+(?:\s*\((?:open|closed)\))?\s*(?::|-)\s*(?P<summary>.+)$",
            candidate,
            flags=re.IGNORECASE,
        )
        summary = summary_match.group("summary").strip() if summary_match else None
        defects.append(
            {
                "id": issue_id,
                "number": int(match.group("number")),
                "state": state,
                "summary": summary,
            }
        )
        seen_ids.add(issue_id)
    return defects


def _tracked_defect_refs(tracked_defects: list[dict[str, Any]]) -> str:
    """Render one compact tracked-defect reference list."""
    refs: list[str] = []
    for defect in tracked_defects:
        issue_id = str(defect.get("id", "")).strip()
        if not issue_id:
            continue
        state = str(defect.get("state", "")).strip().lower()
        refs.append(f"{issue_id} ({state})" if state and state != "unknown" else issue_id)
    return ", ".join(refs)


def _issue_details(issues: list[str], tracked_defects: list[dict[str, Any]]) -> list[str]:
    """Attach brief-local defect linkage to human-facing issue strings."""
    refs = _tracked_defect_refs(tracked_defects)
    if not refs:
        return list(issues)
    return [f"{issue} [tracked defects: {refs}]" for issue in issues]


def _inspect_obpi_brief(
    project_root: Path,
    obpi_file: Path,
    obpi_id: str | None = None,
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    content = obpi_file.read_text(encoding="utf-8")
    frontmatter_status = (parse_frontmatter_value(content, "status") or "").strip().lower()
    brief_status = (_markdown_label_value(content, "Brief Status") or "").strip().lower()
    file_completed = frontmatter_status == "completed" or brief_status == "completed"
    implementation_evidence_ok = _has_substantive_implementation_summary(content)
    key_proof_body = _resolved_key_proof_body(content)
    key_proof_ok = key_proof_body is not None
    human_attestation = _extract_human_attestation(content)
    tracked_defects = _extract_tracked_defects(content)
    info = graph.get(obpi_id, {}) if obpi_id and graph else {}
    semantics = derive_obpi_semantics(
        info,
        obpi_id=obpi_id,
        artifact_graph=graph,
        found_file=True,
        file_completed=file_completed,
        implementation_evidence_ok=implementation_evidence_ok,
        key_proof_ok=key_proof_ok,
        fallback_key_proof=key_proof_body,
        human_attestation=human_attestation,
        project_root=project_root,
    )

    return {
        "file_completed": file_completed,
        "implementation_evidence_ok": implementation_evidence_ok,
        "key_proof_ok": key_proof_ok,
        "human_attestation": human_attestation,
        "frontmatter_status": frontmatter_status or None,
        "brief_status": brief_status or None,
        "reflection_issues": list(semantics["reflection_issues"]),
        "tracked_defects": tracked_defects,
        "issue_details": _issue_details(list(semantics["issues"]), tracked_defects),
        "reasons": list(semantics["issues"]),
        **semantics,
    }


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
    """Return True when an OBPI row is complete with implementation evidence."""
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


def obpi_status_cmd(obpi: str, as_json: bool) -> None:
    """Display focused runtime status for one OBPI."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    obpi_id, _obpi_file = resolve_obpi(project_root, config, ledger, obpi)
    result = _build_obpi_status_entry(project_root, config, ledger, obpi_id)
    if as_json:
        print(json.dumps(result, indent=2))
        return
    _render_obpi_status_details(result)


def obpi_reconcile_cmd(obpi: str, as_json: bool) -> None:
    """Fail-closed reconciliation for one OBPI runtime unit."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    obpi_id, _obpi_file = resolve_obpi(project_root, config, ledger, obpi)
    result = _build_obpi_status_entry(project_root, config, ledger, obpi_id)
    blockers = cast(list[str], result.get("issues", []))
    payload = {
        "passed": not blockers,
        "blockers": blockers,
        **result,
    }

    if as_json:
        print(json.dumps(payload, indent=2))
    else:
        console.print(f"[bold]OBPI reconcile:[/bold] {obpi_id}")
        if isinstance(result.get("parent_adr"), str) and result.get("parent_adr"):
            console.print(f"  Parent ADR: {result['parent_adr']}")
        console.print(f"  File: {result.get('file') or '(missing)'}")
        console.print(
            "  Runtime State: "
            + _render_obpi_runtime_state(
                str(result.get("runtime_state", "pending")),
                bool(result.get("found_file")),
            )
        )
        console.print(f"  Proof State: {result.get('proof_state', 'missing')}")
        console.print(f"  Attestation State: {result.get('attestation_state', 'not_required')}")
        if blockers:
            console.print("BLOCKERS:")
            for blocker in blockers:
                console.print(f"- {blocker}")
        else:
            console.print("[green]PASS[/green] OBPI runtime state and proof evidence are coherent.")

    if blockers:
        raise SystemExit(1)


def _build_adr_status_result(adr: str) -> dict[str, Any]:
    """Build the status result dict for a single ADR."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    try:
        adr_file, adr_id = resolve_adr_file(project_root, config, adr_input)
    except GzCliError:
        canonical_adr = ledger.canonicalize_id(adr_input)
        adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id)
    if not info or info.get("type") != "adr":
        raise GzCliError(f"ADR not found in ledger: {adr_id}")

    lane = resolve_adr_lane(info, config.mode)
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)
    gate4_na = _gate4_na_reason(project_root, lane)
    semantics = Ledger.derive_adr_semantics(info)
    result: dict[str, Any] = {
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
    closeout_readiness = _adr_closeout_readiness(obpi_rows)
    result["closeout_ready"] = bool(closeout_readiness["ready"])
    result["closeout_blockers"] = list(closeout_readiness["blockers"])
    _apply_obpi_lifecycle_overrides(adr_id, result, obpi_summary)
    if gate4_na is not None:
        result["gate4_na_reason"] = gate4_na
    return result


def adr_status_cmd(adr: str, as_json: bool, show_gates: bool) -> None:
    """Display focused OBPI progress, lifecycle, and gate readiness for one ADR."""
    result = _build_adr_status_result(adr)
    lane = cast(str, result["lane"])

    if as_json:
        print(json.dumps(result, indent=2))
        return

    console.print(f"[bold]{result['adr']}[/bold]")
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
    closeout_label = "[green]READY[/green]" if result["closeout_ready"] else "[red]BLOCKED[/red]"
    console.print(f"  Closeout Readiness: {closeout_label}")
    if result["closeout_blockers"]:
        console.print("  Closeout Blockers:")
        for blocker in cast(list[str], result["closeout_blockers"]):
            console.print(f"    - {blocker}")

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
                console.print(f"                 ({result.get('gate4_na_reason', '')})")
            is_attested = bool(result.get("attested"))
            gate5_detail = (
                f" ({result['attestation_term']})" if result.get("attestation_term") else ""
            )
            console.print(
                "  Gate 5 (Human): "
                + ("[green]PASS[/green]" if is_attested else "[yellow]PENDING[/yellow]")
                + (gate5_detail if is_attested else "")
            )


def _render_adr_report(result: dict[str, Any]) -> None:
    """Render deterministic ASCII table report for a single ADR."""
    obpi_summary = cast(dict[str, Any], result.get("obpi_summary", {}))
    obpi_total = cast(int, obpi_summary.get("total", 0))
    obpi_completed = cast(int, obpi_summary.get("completed", 0))
    gates = cast(dict[str, str], result.get("gates", {}))
    lane = cast(str, result.get("lane", "lite"))
    qc_readiness, _qc_blockers = _qc_readiness(gates, lane, obpi_summary)
    closeout_label = "READY" if result.get("closeout_ready") else "BLOCKED"
    qc_label = "READY" if qc_readiness == "ready" else "PENDING"

    # --- ADR Overview ---
    adr_full = cast(str, result["adr"])
    m = ADR_SEMVER_STATUS_ID_RE.match(adr_full)
    adr_short = f"ADR-{m['major']}.{m['minor']}.{m['patch']}" if m else adr_full

    overview = Table(title="ADR Overview", box=box.ROUNDED, padding=(0, 1))
    overview.add_column("ADR", no_wrap=True)
    overview.add_column("Lane", no_wrap=True)
    overview.add_column("Life", no_wrap=True)
    overview.add_column("Phase", no_wrap=True)
    overview.add_column("OBPI", no_wrap=True)
    overview.add_column("Closeout", no_wrap=True)
    overview.add_column("QC", no_wrap=True)
    overview.add_row(
        adr_short,
        lane,
        cast(str, result.get("lifecycle_status", "Pending")),
        cast(str, result.get("closeout_phase", "pre_closeout")),
        f"{obpi_completed}/{obpi_total}",
        closeout_label,
        qc_label,
    )
    console.print(overview)

    # --- OBPIs ---
    obpi_rows = cast(list[dict[str, Any]], result.get("obpis", []))
    obpi_table = Table(title="OBPIs", box=box.ROUNDED, padding=(0, 1))
    obpi_table.add_column("#", no_wrap=True)
    obpi_table.add_column("OBPI ID", overflow="fold")
    obpi_table.add_column("State", no_wrap=True)
    obpi_table.add_column("Brief", no_wrap=True)
    obpi_table.add_column("Done", no_wrap=True)
    for idx, row in enumerate(obpi_rows, 1):
        obpi_table.add_row(
            f"{idx:02d}",
            cast(str, row.get("id", "")),
            cast(str, row.get("runtime_state", "pending")),
            cast(str, row.get("brief_status", "draft")),
            "yes" if row.get("completed") else "no",
        )
    console.print(obpi_table)

    # --- Issues ---
    issues: list[str] = []
    for idx, row in enumerate(obpi_rows, 1):
        prefix = f"{idx:02d}"
        for issue in cast(list[str], row.get("issues", [])):
            issues.append(f"{prefix} {issue}")
        for issue in cast(list[str], row.get("reflection_issues", [])):
            issues.append(f"{prefix} {issue}")
    if issues:
        console.print("Issues")
        for line in issues:
            console.print(line)


def adr_report_cmd(adr: str | None) -> None:
    """Render deterministic tabular report — summary when no ADR given, detail for one ADR."""
    if adr is None:
        config = ensure_initialized()
        project_root = get_project_root()
        ledger = Ledger(project_root / config.paths.ledger)
        graph = ledger.get_artifact_graph()
        adrs = _collect_adr_statuses(project_root, config, ledger, graph)
        _render_status_table(adrs, config.mode)
        return
    result = _build_adr_status_result(adr)
    _render_adr_report(result)
