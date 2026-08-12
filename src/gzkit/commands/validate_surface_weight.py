"""Command surface for `gz validate --surface-weight --recalibrate` (GHI #791).

Split out of ``validate_cmd.py`` for the module-size discipline in
``.claude/rules/pythonic.md``, matching the ``validate_task_envelope`` /
``validate_req_kind`` sibling pattern — ``validate_cmd.py`` carries a shrink-only
grandfather ceiling, so a new handler lands beside it rather than inside it.

The recalibration is the producer ADR-0.0.33 § Anti-Patterns item 3 requires —
*"Band changes are ledger events, not config tweaks"* — and that no registered
verb supplied until this issue. ``OBPI-0.0.33-02`` REQ 4 named
``gz adr emit-receipt``, whose ``--event`` is a closed enum of
``{completed, validated, closed}``; the ledger consequently carried zero
recalibration events and the bands moved once as an unwitnessed tweak.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.commands.common import console


def run_surface_weight_recalibrate(
    project_root: Path, *, scoped: bool, attestor: str, reason: str, as_json: bool
) -> None:
    """Re-snapshot the surface-weight floor and emit its witnessing event (exit 0/1)."""
    from gzkit.governance.trust_audits.surface_weight import (  # noqa: PLC0415
        recalibrate_surface_weight,
    )

    if not scoped:
        console.print(
            "[red]❌ --recalibrate requires --surface-weight.[/red]\n\n"
            "It re-snapshots the surface-weight floor and emits the witnessing ledger "
            "event, so it is meaningless outside that scope.\n"
            "Re-run: [bold]uv run gz validate --surface-weight --recalibrate "
            '--attestor "<name>" --reason "<evidence>"[/bold]'
        )
        raise SystemExit(1)

    try:
        outcome = recalibrate_surface_weight(project_root, attestor=attestor, reason=reason)
    except ValueError as exc:
        console.print(f"[red]❌ {exc}[/red]")
        raise SystemExit(1) from exc

    if as_json:
        print(json.dumps(outcome.model_dump(), indent=2))  # noqa: T201
        raise SystemExit(0)

    delta = outcome.floor_lines - outcome.previous_floor_lines
    console.print("[bold]Recalibrated:[/bold] surface-weight\n")
    console.print(
        f"[green]✓ Floor {outcome.previous_floor_lines} → {outcome.floor_lines} "
        f"({delta:+d}); bands green ≤ {outcome.green_ceiling}, "
        f"yellow ≤ {outcome.yellow_ceiling}.[/green]"
    )
    console.print(f"   Witnessed on the ledger by [bold]{attestor}[/bold].")
    raise SystemExit(0)
