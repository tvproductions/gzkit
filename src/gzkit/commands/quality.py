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

    def _sym(ok: bool) -> str:
        return "[green]✓[/green]" if ok else "[red]❌[/red]"

    console.print(f"  {_sym(result.lint.success)} [bold]Lint[/bold]")
    console.print(f"  {_sym(result.format.success)} [bold]Format[/bold]")
    console.print(f"  {_sym(result.typecheck.success)} [bold]Typecheck[/bold]")
    console.print(f"  {_sym(result.test.success)} [bold]Test[/bold]")
    console.print(f"  {_sym(result.skill_audit.success)} [bold]Skill audit[/bold]")
    console.print(f"  {_sym(result.parity_check.success)} [bold]Parity check[/bold]")
    console.print(f"  {_sym(result.readiness_audit.success)} [bold]Readiness audit[/bold]")

    if result.success:
        console.print("\n[green]✓ All checks passed.[/green]")
    else:
        console.print("\n[red]❌ Some checks failed.[/red]")
        raise SystemExit(1)
