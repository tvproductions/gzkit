"""Quality commands (lint, format, test, typecheck, check)."""

from gzkit.commands.common import console, get_project_root
from gzkit.quality import run_format, run_lint, run_tests, run_typecheck


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


def test() -> None:
    """Run unit tests."""
    project_root = get_project_root()

    console.print("Running tests...")
    result = run_tests(project_root)

    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Tests passed.[/green]")
    else:
        console.print("[red]Tests failed.[/red]")
        raise SystemExit(result.returncode)


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


def check() -> None:
    """Run all quality checks (lint + format + typecheck + test + governance audits)."""
    from gzkit.cli.formatters import OutputFormatter
    from gzkit.quality import (
        run_format_check,
        run_parity_check,
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
        ("Skill audit", run_skill_audit),
        ("Parity check", run_parity_check),
        ("Readiness audit", run_readiness_audit),
    ]

    results: list[tuple[str, bool]] = []
    with fmt.progress_context(len(steps), "Running quality checks") as progress:
        for name, runner in steps:
            progress.advance(name)
            result = runner(project_root)
            results.append((name, result.success))

    def _sym(ok: bool) -> str:
        return "[green]✓[/green]" if ok else "[red]❌[/red]"

    for name, success in results:
        console.print(f"  {_sym(success)} [bold]{name}[/bold]")

    all_passed = all(s for _, s in results)
    if all_passed:
        console.print("\n[green]✓ All checks passed.[/green]")
    else:
        console.print("\n[red]❌ Some checks failed.[/red]")
        raise SystemExit(1)
