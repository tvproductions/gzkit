"""Quality commands (lint, format, test, typecheck, check)."""

from gzkit.commands.common import _cli_main, console, get_project_root
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
    project_root = get_project_root()

    console.print("Running all quality checks...\n")
    result = _cli_main().run_all_checks(project_root)

    # Lint
    console.print("[bold]Lint:[/bold]", "PASS" if result.lint.success else "FAIL")

    # Format
    console.print("[bold]Format:[/bold]", "PASS" if result.format.success else "FAIL")

    # Typecheck
    console.print("[bold]Typecheck:[/bold]", "PASS" if result.typecheck.success else "FAIL")

    # Test
    console.print("[bold]Test:[/bold]", "PASS" if result.test.success else "FAIL")

    # Skill audit
    console.print("[bold]Skill audit:[/bold]", "PASS" if result.skill_audit.success else "FAIL")

    # Parity check
    console.print("[bold]Parity check:[/bold]", "PASS" if result.parity_check.success else "FAIL")

    # Readiness audit
    console.print(
        "[bold]Readiness audit:[/bold]", "PASS" if result.readiness_audit.success else "FAIL"
    )

    if result.success:
        console.print("\n[green]All checks passed.[/green]")
    else:
        console.print("\n[red]Some checks failed.[/red]")
        raise SystemExit(1)
