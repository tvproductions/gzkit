"""Dedicated handlers for the disclosure-inventory `gz validate` scopes.

One family, lifted here together: each answers *what exists that nothing
covers?* over a shrink-only accepted-list, and each reports COUNTS on a green
run rather than a bare tick — a green that hides the number restores exactly
the silence these inventories exist to break.

They live outside ``validate_cmd`` because that module is at its shrink-only
size ceiling (``data/module_size_grandfather.json``). Raising the entry to fit
a new handler is the laundering ADR-0.0.73 Boundary Invariant #8 forbids;
extracting a coherent family is the precedented answer (``c3d9a99a0``).
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.commands.common import console


def run_exemption_controls_scope(project_root: Path, *, as_json: bool) -> None:
    """Dedicated handler for ``gz validate --exemption-controls`` (exit 0/3).

    The green line reports the COUNTS, on the `--gate-callers` precedent: the
    point of GHI #797 is that "nobody has stated whether this gate has an
    exemption" becomes a visible, counted fact, and a green run hiding the
    number would restore the silence the inventory exists to break.
    """
    from gzkit.governance.trust_audits.exemption_controls import (  # noqa: PLC0415
        _registry_declarations,
        audit_exemption_controls,
    )

    errors = audit_exemption_controls(project_root)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))  # noqa: T201
        raise SystemExit(3 if errors else 0)
    console.print("[bold]Validated:[/bold] exemption-controls\n")
    if not errors:
        declared = _registry_declarations()
        undeclared = sum(1 for v in declared.values() if v is None)
        console.print(
            f"[green]✓ {len(declared)} enforcement claims inventoried; "
            f"{len(declared) - undeclared} declare their exemption half, "
            f"{undeclared} disclosed as undeclared.[/green]"
        )
        raise SystemExit(0)
    console.print(f"[red]❌ {len(errors)} exemption-control finding(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {e.artifact}: {e.message}")
    raise SystemExit(3)


def run_gate_callers_scope(project_root: Path, *, as_json: bool) -> None:
    """Dedicated handler for `gz validate --gate-callers` (exit 0/3).

    The green line reports the accepted COUNT rather than a bare tick: the whole
    point of GHI #785 is that "this gate has no automatic caller" becomes a
    visible, counted fact, and a green run that hides the number would restore
    exactly the silence the inventory exists to break.
    """
    from gzkit.governance.trust_audits.gate_callers import (  # noqa: PLC0415
        audit_gate_callers,
        uncalled_gates,
    )

    errors = audit_gate_callers(project_root)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))  # noqa: T201
        raise SystemExit(3 if errors else 0)
    console.print("[bold]Validated:[/bold] gate-callers\n")
    if not errors:
        report = uncalled_gates(project_root)
        accepted = sum(1 for g in report if not g.called)
        console.print(
            f"[green]✓ {len(report)} gates inventoried; "
            f"{len(report) - accepted} have an automatic caller, "
            f"{accepted} accepted as uncalled.[/green]"
        )
        raise SystemExit(0)
    console.print(f"[red]❌ {len(errors)} gate-caller finding(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {e.artifact}: {e.message}")
    raise SystemExit(3)
