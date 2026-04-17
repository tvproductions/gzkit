"""Quality commands (lint, format, test, typecheck, check).

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-05-advisory-gate-integration
"""

from __future__ import annotations

from gzkit.commands.common import console, get_project_root
from gzkit.quality import (
    DriftAdvisoryResult,
    run_behave,
    run_format,
    run_lint,
    run_tests,
    run_typecheck,
)


def lint() -> None:
    """Run code linting (ruff + pymarkdown)."""
    project_root = get_project_root()

    console.print("Running linters...")
    result = run_lint(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Lint passed.[/green]")
    else:
        console.print("[red]Lint failed.[/red]")
        raise SystemExit(result.returncode)


def format_cmd() -> None:
    """Auto-format code with ruff."""
    project_root = get_project_root()

    console.print("Formatting code...")
    result = run_format(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Format complete.[/green]")
    else:
        console.print("[red]Format failed.[/red]")
        raise SystemExit(result.returncode)


def test(*, integration: bool = False) -> None:
    """Run the test tier (unit by default, integration with --integration).

    Unit tier runs unittest over ``tests/`` (excluding ``tests/integration/``)
    then behave scenarios — the fast pre-commit floor. Integration tier runs
    only ``tests/integration/`` (subprocess-spawning, real-filesystem tests)
    and skips behave.
    """
    project_root = get_project_root()

    if integration:
        console.print("Running integration tier...")
        result = run_tests(project_root, integration=True)
        if result.stdout:
            console.print(result.stdout)
        if result.stderr:
            console.print(result.stderr)
        if not result.success:
            console.print("[red]Integration tests failed.[/red]")
            raise SystemExit(result.returncode)
        console.print("[green]Integration tests passed.[/green]")
        return

    console.print("Running unit tests...")
    unit = run_tests(project_root)
    if unit.stdout:
        console.print(unit.stdout)
    if unit.stderr:
        console.print(unit.stderr)
    if not unit.success:
        console.print("[red]Unit tests failed.[/red]")
        raise SystemExit(unit.returncode)
    console.print("[green]Unit tests passed.[/green]")

    console.print("Running behave scenarios...")
    bdd = run_behave(project_root)
    if bdd.stdout:
        console.print(bdd.stdout)
    if bdd.stderr:
        console.print(bdd.stderr)
    if bdd.success:
        console.print("[green]Behave scenarios passed.[/green]")
    else:
        console.print("[red]Behave scenarios failed.[/red]")
        raise SystemExit(bdd.returncode)


def typecheck() -> None:
    """Run type checking with ty."""
    project_root = get_project_root()

    console.print("Running type checker...")
    result = run_typecheck(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Type check passed.[/green]")
    else:
        console.print("[red]Type check failed.[/red]")
        raise SystemExit(result.returncode)


def check(as_json: bool = False) -> None:
    """Run all quality checks (lint + format + typecheck + test + governance audits)."""
    import json
    import sys

    from gzkit.cli.formatters import OutputFormatter
    from gzkit.quality import (
        run_cli_audit,
        run_drift_advisory,
        run_format_check,
        run_parity_check,
        run_preflight,
        run_readiness_audit,
        run_skill_audit,
    )

    project_root = get_project_root()
    fmt = OutputFormatter()

    steps = [
        ("Lint", run_lint),
        ("Format", run_format_check),
        ("Typecheck", run_typecheck),
        ("Test", run_tests),
        ("Behave", run_behave),
        ("Skill audit", run_skill_audit),
        ("Parity check", run_parity_check),
        ("Readiness audit", run_readiness_audit),
        ("CLI audit", run_cli_audit),
        ("Preflight", run_preflight),
    ]

    results: list[tuple[str, bool]] = []
    with fmt.progress_context(len(steps), "Running quality checks") as progress:
        for name, runner in steps:
            progress.advance(name)
            result = runner(project_root)
            results.append((name, result.success))

    drift: DriftAdvisoryResult = run_drift_advisory(project_root)

    # Flag health (advisory — warnings only, does not block)
    from gzkit.flags.diagnostics import FlagHealthSummary, get_flag_health
    from gzkit.flags.registry import load_registry

    flag_health: FlagHealthSummary | None = None
    try:
        registry = load_registry()
        flag_health = get_flag_health(registry)
    except Exception:  # noqa: BLE001 — flag health is advisory
        pass

    if as_json:
        payload: dict[str, object] = {
            "success": all(s for _, s in results),
            "checks": dict(results),
            "drift": drift.to_dict(),
        }
        if flag_health is not None:
            payload["flag_health"] = flag_health.model_dump()
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        if not all(s for _, s in results):
            raise SystemExit(1)
        return

    def _sym(ok: bool) -> str:
        return "[green]✓[/green]" if ok else "[red]❌[/red]"

    for name, success in results:
        console.print(f"  {_sym(success)} [bold]{name}[/bold]")

    all_passed = all(s for _, s in results)
    if all_passed:
        console.print("\n[green]✓ All checks passed.[/green]")
    else:
        console.print("\n[red]❌ Some checks failed.[/red]")

    _render_drift_advisory(drift)
    _render_flag_health(flag_health)

    if not all_passed:
        raise SystemExit(1)


def _render_drift_advisory(drift: DriftAdvisoryResult) -> None:
    """Render advisory drift findings after blocking checks."""
    if not drift.has_drift:
        return

    console.print("\n[yellow]⚠ Advisory: spec-test-code drift detected[/yellow]")

    if drift.unlinked_specs:
        console.print("  Unlinked specs (REQs with no test):")
        for req_id in drift.unlinked_specs:
            console.print(f"    [yellow]advisory[/yellow]  {req_id}")

    if drift.orphan_tests:
        console.print("  Orphan tests (covering absent REQs):")
        for req_id in drift.orphan_tests:
            console.print(f"    [yellow]advisory[/yellow]  {req_id}")

    if drift.unjustified_code_changes:
        console.print("  Unjustified code changes:")
        for code_id in drift.unjustified_code_changes:
            console.print(f"    [yellow]advisory[/yellow]  {code_id}")

    console.print(
        f"  Total: {drift.total_drift_count} finding(s) "
        f"[dim](advisory — does not affect exit code)[/dim]"
    )


def _render_flag_health(health: object | None) -> None:
    """Render flag health warnings after quality checks."""
    from gzkit.flags.diagnostics import FlagHealthSummary

    if not isinstance(health, FlagHealthSummary):
        return
    if health.stale_count == 0 and health.approaching_count == 0:
        return

    console.print("\n[yellow]⚠ Flag health warnings[/yellow]")

    if health.stale_keys:
        console.print("  Stale flags (past deadline):")
        for key in health.stale_keys:
            console.print(f"    [red]stale[/red]  {key}")

    if health.approaching_keys:
        console.print("  Approaching deadline (within 14 days):")
        for key in health.approaching_keys:
            console.print(f"    [yellow]warning[/yellow]  {key}")

    console.print(
        f"  Total: {health.stale_count} stale, "
        f"{health.approaching_count} approaching "
        f"[dim](advisory — does not affect exit code)[/dim]"
    )
