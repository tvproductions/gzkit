"""Persona listing command — enumerate persona identity frames (read-only)."""

from __future__ import annotations

import json

from rich.table import Table

from gzkit.commands.common import console, get_project_root
from gzkit.models.persona import discover_persona_files, parse_persona_file


def personas_list_cmd(*, as_json: bool = False) -> None:
    """List persona files from ``.gzkit/personas/``."""
    project_root = get_project_root()
    personas_dir = project_root / ".gzkit" / "personas"

    if not personas_dir.is_dir():
        if as_json:
            print(json.dumps([], indent=2))  # noqa: T201
        else:
            console.print("No personas directory found.")
        return

    files = discover_persona_files(personas_dir)
    if not files:
        if as_json:
            print(json.dumps([], indent=2))  # noqa: T201
        else:
            console.print("No persona files found.")
        return

    personas_data: list[dict[str, object]] = []
    for f in files:
        try:
            fm, _body = parse_persona_file(f)
            personas_data.append(
                {
                    "name": fm.name,
                    "traits": fm.traits,
                    "anti_traits": fm.anti_traits,
                    "grounding": fm.grounding,
                }
            )
        except ValueError:
            console.print(f"  [yellow]WARNING:[/yellow] {f.name}: parse error, skipping")

    if as_json:
        print(json.dumps(personas_data, indent=2))  # noqa: T201
        return

    table = Table(title="Agent Personas")
    table.add_column("Name", style="bold")
    table.add_column("Traits")
    table.add_column("Anti-Traits")
    table.add_column("Grounding")
    for p in personas_data:
        grounding = str(p["grounding"])
        table.add_row(
            str(p["name"]),
            ", ".join(p["traits"]),  # type: ignore[arg-type]
            ", ".join(p["anti_traits"]),  # type: ignore[arg-type]
            grounding[:80] + "..." if len(grounding) > 80 else grounding,
        )
    console.print(table)
