"""gz adr fidelity command (ADR-0.0.73, OBPI-0.0.73-03).

Parses the ``## Fidelity Assertions`` block from an ADR Decision, runs each
command, and reports observed-vs-expected exit with pass/fail per assertion.
Exits non-zero when any assertion fails.  ``--check`` parses the block without
running any commands.
"""

from __future__ import annotations

import sys

from gzkit.commands.common import (
    GzCliError,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
)
from gzkit.fidelity import parse_fidelity_assertions, run_fidelity_gate


def adr_fidelity_cmd(adr: str, check_only: bool = False) -> None:
    """Run the fidelity gate for an ADR (or check block parseability with --check)."""
    config = ensure_initialized()
    project_root = get_project_root()

    try:
        adr_path, _ = resolve_adr_file(project_root, config, adr)
    except (GzCliError, FileNotFoundError) as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(2)

    try:
        assertions = parse_fidelity_assertions(adr_path)
    except ValueError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(3)

    if check_only:
        console.print(
            f"[green]Fidelity block parseable:[/green] "
            f"{len(assertions)} assertion(s) in {adr_path.name}"
        )
        sys.exit(0)

    console.print(f"[bold]gz adr fidelity:[/bold] {adr}")
    console.print(f"  Assertions: {len(assertions)}")
    console.print("")

    results = run_fidelity_gate(assertions, adr_id=adr)

    any_fail = False
    for r in results:
        status = "[green]PASS[/green]" if r.result == "pass" else "[red]FAIL[/red]"
        console.print(f"  {status}  {r.claim}")
        console.print(f"        command:  {r.command}")
        console.print(f"        expected: {r.expected_exit}  observed: {r.observed}")
        console.print("")
        if r.result == "fail":
            any_fail = True

    passed = sum(1 for r in results if r.result == "pass")
    failed = sum(1 for r in results if r.result == "fail")
    console.print(f"  Summary: {passed} pass, {failed} fail")

    if any_fail:
        sys.exit(1)
