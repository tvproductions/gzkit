"""State command implementation."""

import json
import re
from pathlib import Path
from typing import Any

from rich.table import Table

from gzkit.commands.closeout_form import guarded_obpi_status_write
from gzkit.commands.common import (
    _attestation_gate_snapshot,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.commands.task import _load_tasks_for_obpi
from gzkit.ledger import Ledger, parse_frontmatter_value, resolve_adr_lane
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts

_OBPI_SHORT_ID_RE = re.compile(r"(OBPI-\d+\.\d+\.\d+-\d+)")


def _enrich_obpi_with_tasks(
    graph: dict[str, dict[str, Any]],
    ledger: Ledger,
    default_mode: str,
) -> None:
    """Add task_summary to OBPI entries that have tasks."""
    for artifact_id, info in graph.items():
        if info.get("type") != "obpi":
            continue
        tasks = _load_tasks_for_obpi(ledger, artifact_id)
        if not tasks:
            continue
        counts: dict[str, int] = {
            "total": 0,
            "pending": 0,
            "in_progress": 0,
            "completed": 0,
            "blocked": 0,
            "escalated": 0,
        }
        for task_info in tasks.values():
            counts["total"] += 1
            status = task_info.get("status", "pending")
            if status in counts:
                counts[status] += 1

        parent_adr = info.get("parent", "")
        parent_info = graph.get(parent_adr, {})
        lane = resolve_adr_lane(parent_info, default_mode)
        counts["tracing_policy"] = "required" if lane == "heavy" else "advisory"  # ty: ignore[invalid-assignment]
        info["task_summary"] = counts


def _hide_withdrawn_obpis(graph: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Strip withdrawn OBPIs from graph and from each parent's children (GHI #221).

    The ledger is never mutated; this acts on the derived graph copy.
    """
    withdrawn_ids = {
        artifact_id
        for artifact_id, info in graph.items()
        if info.get("type") == "obpi" and info.get("withdrawn")
    }
    if not withdrawn_ids:
        return graph
    filtered = {k: v for k, v in graph.items() if k not in withdrawn_ids}
    for info in filtered.values():
        children = info.get("children")
        if isinstance(children, list) and any(c in withdrawn_ids for c in children):
            info["children"] = [c for c in children if c not in withdrawn_ids]
    return filtered


def state(
    as_json: bool,
    blocked: bool,
    ready: bool,
    include_withdrawn: bool = False,
    full: bool = False,
) -> None:
    """Query ledger state and artifact relationships.

    Withdrawn OBPIs (recorded via ``obpi_withdrawn`` events) are hidden from
    the graph by default so status surfaces do not conflate withdrawn
    ceremonies with active decomposition (GHI #221). The ledger is
    untouched — withdrawn events remain as legitimate history. Pass
    ``include_withdrawn=True`` / ``--include-withdrawn`` to see them.

    When ``full=True`` (``--full``) the Rich table renders identity-bearing
    columns (ID, Parent) with overflow="fold" so attestation evidence and
    bug reports retain complete artifact IDs (GHI #319).
    """
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    raw_graph = ledger.get_artifact_graph()
    graph = {artifact_id: dict(info) for artifact_id, info in raw_graph.items()}
    for _artifact_id, info in graph.items():
        if info.get("type") == "adr":
            info.update(Ledger.derive_adr_semantics(info))

    if not include_withdrawn:
        graph = _hide_withdrawn_obpis(graph)

    # Filter if requested
    if blocked:
        graph = {k: v for k, v in graph.items() if not v.get("attested")}
    if ready:
        ready_ids: set[str] = set()
        for artifact_id, info in graph.items():
            if info.get("type") != "adr" or info.get("attested"):
                continue
            snapshot = _attestation_gate_snapshot(project_root, config, ledger, artifact_id)
            if snapshot["ready"]:
                ready_ids.add(artifact_id)
        graph = {k: v for k, v in graph.items() if k in ready_ids}

    if as_json:
        _enrich_obpi_with_tasks(graph, ledger, config.mode)
        print(json.dumps(graph, indent=2))  # noqa: T201
        return

    if not graph:
        console.print("No artifacts found.")
        return

    _render_artifact_state_table(graph, full=full)


def _render_artifact_state_table(graph: dict[str, dict[str, Any]], *, full: bool = False) -> None:
    """Render the Artifact State table with optional ``--full`` fidelity.

    When ``full`` is True the ID and Parent columns fold long values
    instead of ellipsizing them (GHI #319).
    """
    table = Table(title="Artifact State")
    overflow = "fold" if full else "ellipsis"
    table.add_column("ID", style="cyan", overflow=overflow, no_wrap=not full)
    table.add_column("Type", style="green", no_wrap=True)
    table.add_column("Parent", overflow=overflow, no_wrap=not full)
    table.add_column("Attested", style="yellow", no_wrap=True)

    for artifact_id, info in sorted(graph.items()):
        attested = "[green]Yes[/green]" if info.get("attested") else "[red]No[/red]"
        table.add_row(
            artifact_id,
            info.get("type", "unknown"),
            info.get("parent") or "-",
            attested,
        )

    console.print(table)


# ---------------------------------------------------------------------------
# State repair — force-reconcile frontmatter from ledger-derived state
# ---------------------------------------------------------------------------


def _derive_expected_status(info: dict[str, Any]) -> str | None:
    """Map ledger graph info to expected frontmatter status for an OBPI.

    Returns the canonical frontmatter status the OBPI should have based on
    ledger events, or None if the ledger has no definitive state (the OBPI
    is still in-progress and frontmatter should not be changed).
    """
    if info.get("type") != "obpi":
        return None
    if info.get("withdrawn"):
        return "Abandoned"
    if info.get("ledger_completed"):
        return "Completed"
    return None


def _scan_obpi_briefs(
    project_root: Path,
    design_root: str,
) -> dict[str, dict[str, Any]]:
    """Scan OBPI brief files and return a map of short ID to file metadata.

    Returns:
        Dict mapping OBPI short IDs (e.g. ``OBPI-0.1.0-01``) to dicts
        containing ``path`` and ``frontmatter_status``.

    """
    artifacts = scan_existing_artifacts(project_root, design_root)
    result: dict[str, dict[str, Any]] = {}
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        raw_id = metadata.get("id", obpi_file.stem)
        match = _OBPI_SHORT_ID_RE.match(raw_id)
        short_id = match.group(1) if match else raw_id
        content = obpi_file.read_text(encoding="utf-8")
        fm_status = parse_frontmatter_value(content, "status") or ""
        result[short_id] = {
            "path": obpi_file,
            "frontmatter_status": fm_status.strip(),
        }
    return result


def _resolve_expected_statuses(
    graph: dict[str, dict[str, Any]],
    ledger: Ledger,
) -> dict[str, str]:
    """Build a map of OBPI short ID to expected frontmatter status.

    Handles renamed OBPIs (old slug withdrawn, new slug active) by
    collecting all graph entries per short ID and applying priority:
    active non-withdrawn entries take precedence over withdrawn ones.
    """
    # Collect all graph entries per short ID
    entries_by_short_id: dict[str, list[dict[str, Any]]] = {}
    for obpi_id, info in graph.items():
        if info.get("type") != "obpi":
            continue
        canonical_id = ledger.canonicalize_id(obpi_id)
        match = _OBPI_SHORT_ID_RE.match(canonical_id)
        short_id = match.group(1) if match else canonical_id
        entries_by_short_id.setdefault(short_id, []).append(info)

    # Resolve per short ID: non-withdrawn entries take precedence
    result: dict[str, str] = {}
    for short_id, entries in entries_by_short_id.items():
        active = [e for e in entries if not e.get("withdrawn")]
        if active:
            # Use the active (non-withdrawn) entry
            for entry in active:
                expected = _derive_expected_status(entry)
                if expected is not None:
                    result[short_id] = expected
                    break
        else:
            # All entries withdrawn
            result[short_id] = "Abandoned"
    return result


def state_repair(as_json: bool) -> None:
    """Force-reconcile all OBPI frontmatter status from ledger-derived state."""
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    graph = ledger.get_artifact_graph()
    briefs = _scan_obpi_briefs(project_root, config.paths.design_root)
    expected_statuses = _resolve_expected_statuses(graph, ledger)

    changes: list[dict[str, str]] = []

    for short_id, expected in expected_statuses.items():
        brief_info = briefs.get(short_id)
        if brief_info is None:
            continue

        current_status = brief_info["frontmatter_status"]
        if current_status == expected:
            continue

        # Update frontmatter via the guarded OBPI-status chokepoint so a terminal
        # (withdrawn/superseded) brief is never silently clobbered by a state
        # sync (GHI #668 class-fix / ADR-0.31.0 Decision item 4). A refused
        # write (or no-op) records no change.
        brief_path: Path = brief_info["path"]
        if not guarded_obpi_status_write(brief_path, expected):
            continue

        changes.append(
            {
                "obpi_id": short_id,
                "file": brief_path.relative_to(project_root).as_posix(),
                "old_status": current_status,
                "new_status": expected,
            }
        )

    if as_json:
        print(json.dumps({"changes": changes, "total": len(changes)}, indent=2))  # noqa: T201
        return

    if not changes:
        console.print("All frontmatter is aligned with ledger state. No changes.")
        return

    table = Table(title="State Repair Results")
    table.add_column("OBPI", style="cyan")
    table.add_column("Old Status", style="red")
    table.add_column("New Status", style="green")
    table.add_column("File")

    for change in changes:
        table.add_row(
            change["obpi_id"],
            change["old_status"],
            change["new_status"],
            change["file"],
        )

    console.print(table)
    console.print(f"\nRepaired {len(changes)} frontmatter status field(s).")
