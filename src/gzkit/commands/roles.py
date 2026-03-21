"""Roles command — list pipeline agent roles and dispatch history."""

from __future__ import annotations

import json
import sys

from rich.table import Table

from gzkit.commands.common import console, get_project_root
from gzkit.pipeline_runtime import (
    AGENT_FILE_MAP,
    load_dispatch_state,
    load_dispatch_summary,
    pipeline_plans_dir,
    validate_agent_files,
)
from gzkit.roles import ROLE_REGISTRY


def roles_cmd(*, pipeline: str | None = None, as_json: bool = False) -> None:
    """List pipeline agent roles or show dispatch history for an OBPI."""
    project_root = get_project_root()

    if pipeline:
        _show_pipeline_dispatch(project_root, pipeline, as_json=as_json)
        return

    _show_role_registry(project_root, as_json=as_json)


def _show_role_registry(project_root: object, *, as_json: bool) -> None:
    """Display the four pipeline roles with their contracts."""
    from pathlib import Path

    root = Path(str(project_root))
    roles_data = []
    for name, role_def in ROLE_REGISTRY.items():
        agent_file = AGENT_FILE_MAP.get(name, "")
        tools = ", ".join(role_def.agent_spec.tools) if role_def.agent_spec else ""
        roles_data.append(
            {
                "role": name,
                "description": role_def.description,
                "stages": ", ".join(str(s) for s in role_def.pipeline_stages),
                "agent_file": agent_file,
                "tools": tools,
                "can_write": role_def.can_write,
            }
        )

    if as_json:
        print(json.dumps(roles_data, indent=2))
        return

    table = Table(title="Pipeline Agent Roles")
    table.add_column("Role", style="bold")
    table.add_column("Description")
    table.add_column("Stages")
    table.add_column("Agent File")
    table.add_column("Write?")
    for r in roles_data:
        table.add_row(
            r["role"],
            r["description"],
            r["stages"],
            r["agent_file"],
            "yes" if r["can_write"] else "no",
        )
    console.print(table)

    # Validate agent files and warn on issues
    errors = validate_agent_files(root)
    if errors:
        console.print("")
        for err in errors:
            console.print(f"  [yellow]WARNING:[/yellow] {err}")


def _show_pipeline_dispatch(project_root: object, obpi_id: str, *, as_json: bool) -> None:
    """Show dispatch history for a specific pipeline run."""
    from pathlib import Path

    root = Path(str(project_root))
    plans_dir = pipeline_plans_dir(root)

    # Try active marker first, then persisted summary
    records_data = None
    active_records = load_dispatch_state(plans_dir, obpi_id)
    if active_records:
        records_data = {
            "source": "active",
            "obpi_id": obpi_id,
            "records": [r.model_dump() for r in active_records],
        }
    else:
        summary = load_dispatch_summary(plans_dir, obpi_id)
        if summary:
            records_data = {"source": "summary", **summary}

    if records_data is None:
        console.print(f"No dispatch data found for {obpi_id}")
        sys.exit(1)

    if as_json:
        print(json.dumps(records_data, indent=2))
        return

    raw_records = records_data.get("records", [])
    if not isinstance(raw_records, list) or not raw_records:
        console.print(f"No dispatch records for {obpi_id}")
        return

    table = Table(title=f"Dispatch History: {obpi_id}")
    table.add_column("Task", style="bold")
    table.add_column("Role")
    table.add_column("Model")
    table.add_column("Isolation")
    table.add_column("Status")
    for rec in raw_records:
        if not isinstance(rec, dict):
            continue
        table.add_row(
            str(rec.get("task_id", "?")),
            str(rec.get("role", "")),
            str(rec.get("model", "")),
            str(rec.get("isolation", "")),
            str(rec.get("status", "")),
        )
    console.print(table)
