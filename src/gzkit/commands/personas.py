"""Persona commands — list and drift check for persona identity frames."""

from __future__ import annotations

import json
import sys

from rich.table import Table

from gzkit.commands.common import console, get_project_root
from gzkit.models.persona import PersonaDriftReport, discover_persona_files, parse_persona_file


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
            ", ".join(p["traits"]),  # ty: ignore[no-matching-overload]
            ", ".join(p["anti_traits"]),  # ty: ignore[no-matching-overload]
            grounding[:80] + "..." if len(grounding) > 80 else grounding,
        )
    console.print(table)


def _format_drift_table(report: PersonaDriftReport) -> None:
    """Render drift report as Rich tables to console."""
    if report.drift_count == 0:
        console.print("No persona drift detected.")
        _print_drift_summary(report)
        return

    for persona_result in report.personas:
        table = Table(title=f"Persona: {persona_result.persona}")
        table.add_column("Trait", style="bold")
        table.add_column("Type")
        table.add_column("Proxy")
        table.add_column("Status")
        table.add_column("Detail")

        for check in persona_result.checks:
            trait_type = "anti-trait" if check.is_anti_trait else "trait"
            style = (
                "green" if check.status == "pass" else "red" if check.status == "fail" else "yellow"
            )
            detail = check.detail
            if len(detail) > 60:
                detail = detail[:57] + "..."
            status_cell = f"[{style}]{check.status}[/{style}]"
            table.add_row(check.trait, trait_type, check.proxy, status_cell, detail)
        console.print(table)
        console.print()

    _print_drift_summary(report)


def _print_drift_summary(report: PersonaDriftReport) -> None:
    """Print aggregate drift summary line."""
    console.print(
        f"Summary: {report.total_personas} personas, "
        f"{report.total_checks} checks, "
        f"{report.drift_count} drift findings"
    )


def persona_drift_cmd(*, persona: str | None = None, as_json: bool = False) -> None:
    """Report persona trait adherence from behavioral proxies.

    Scans local governance artifacts (ledger, OBPI audit logs) for
    evidence of trait-aligned behavior.  Reports per-trait pass/fail
    for each persona.

    Exit code 0 when no drift detected, exit code 3 on policy breach.
    """
    from gzkit.cli.helpers.exit_codes import EXIT_POLICY_BREACH  # noqa: PLC0415
    from gzkit.personas import evaluate_persona_drift  # noqa: PLC0415

    project_root = get_project_root()
    report = evaluate_persona_drift(project_root, persona_name=persona)

    if as_json:
        sys.stdout.write(report.model_dump_json(indent=2) + "\n")
    else:
        _format_drift_table(report)

    if report.drift_count > 0:
        raise SystemExit(EXIT_POLICY_BREACH)
