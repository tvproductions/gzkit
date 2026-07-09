"""gz test-shape — advisory inventory of test-shape debt (GHI #571).

Read-only and advisory by construction: it always exits 0. The fail-closed gate for
tautological *growth* is `gz validate --tautological-test-audit`; this command answers
the question that gate cannot — what debt remains, and in what shape.
"""

from __future__ import annotations

import json

from gzkit.commands.common import console, get_project_root
from gzkit.test_shape import build_inventory

_ADVISORY_EXIT = 0


def _render_tautological(inventory: object) -> None:
    ops = inventory.tautological  # ty: ignore
    console.print(f"\n[bold]Tautological-shaped operations[/bold] ({len(ops)})")
    if not ops:
        console.print("  [green]none[/green]")
        return
    for disposition, count in sorted(inventory.by_disposition.items()):  # ty: ignore
        console.print(f"  {disposition:<22} {count}")
    console.print("\n  [dim]Growth is gated by `gz validate --tautological-test-audit`.[/dim]")


def _render_output(inventory: object, undeclared_only: bool) -> None:
    all_assertions = inventory.output_assertions  # ty: ignore
    undeclared = inventory.undeclared_output_assertions  # ty: ignore
    shown = undeclared if undeclared_only else all_assertions
    console.print(
        f"\n[bold]Output/render assertions[/bold] "
        f"({len(all_assertions)} total, {len(undeclared)} undeclared)"
    )
    if not shown:
        console.print("  [green]none[/green]")
        return
    by_file: dict[str, int] = {}
    for assertion in shown:
        by_file[assertion.file_path] = by_file.get(assertion.file_path, 0) + 1
    for path, count in sorted(by_file.items(), key=lambda kv: (-kv[1], kv[0]))[:10]:
        console.print(f"  {count:>4}  {path}")
    if len(by_file) > 10:
        console.print(f"  [dim]... {len(by_file) - 10} more files[/dim]")
    console.print(
        "\n  [dim]Advisory only. Most are legitimate render-contract tests "
        "(.gzkit/rules/tests.md § Output-form fixture carve-out).\n"
        "  Declare the carve-out with `# output-contract: <reason>` inside the test, "
        "or name the class *OutputForm / *OutputContract / *Rendering.[/dim]"
    )


def test_shape_cmd(
    *,
    kind: str = "all",
    undeclared_only: bool = False,
    as_json: bool = False,
) -> int:
    """Report advisory test-shape debt: tautological operations and output assertions.

    Always exits 0. This is a reporting surface, never a gate — 824 of today's 832
    output assertions are undeclared, and most are legitimate render-contract tests.
    """
    project_root = get_project_root()
    inventory = build_inventory(project_root)

    if as_json:
        payload: dict[str, object] = {"by_disposition": inventory.by_disposition}
        if kind in ("tautological", "all"):
            payload["tautological"] = [op.model_dump() for op in inventory.tautological]
        if kind in ("output", "all"):
            source = (
                inventory.undeclared_output_assertions
                if undeclared_only
                else inventory.output_assertions
            )
            payload["output_assertions"] = [a.model_dump() for a in source]
            payload["undeclared_count"] = len(inventory.undeclared_output_assertions)
        print(json.dumps(payload, indent=2))
        return _ADVISORY_EXIT

    console.print("[bold]Test-shape inventory[/bold] [dim](advisory; never gates)[/dim]")
    if kind in ("tautological", "all"):
        _render_tautological(inventory)
    if kind in ("output", "all"):
        _render_output(inventory, undeclared_only)
    console.print()
    return _ADVISORY_EXIT
