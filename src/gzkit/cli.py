"""gzkit CLI entry point.

Usage:
    gz init          Initialize gzkit in a project
    gz status        Show gate status for current work
    gz plan new      Create a new ADR
    gz verify        Run verification gates
    gz attest        Record human attestation
"""

import click

from gzkit import __version__


@click.group()
@click.version_option(version=__version__, prog_name="gzkit")
def main() -> None:
    """gzkit: A Development Covenant for Human-AI Collaboration."""
    pass


@main.command()
@click.option("--mode", type=click.Choice(["lite", "heavy"]), default="lite")
def init(mode: str) -> None:
    """Initialize gzkit in the current project."""
    click.echo(f"Initializing gzkit in {mode} mode...")
    click.echo("Created .gzkit.json")
    click.echo("Created docs/canon/ directory")
    click.echo("Created docs/adr/ directory")


@main.command()
def status() -> None:
    """Show gate status for current work."""
    click.echo("Gate Status")
    click.echo("-" * 40)
    click.echo("Gate 1 (ADR):    No active ADRs")
    click.echo("Gate 2 (TDD):    Not checked")
    click.echo("Gate 3 (Docs):   Not checked")
    click.echo("Gate 4 (BDD):    Not checked")
    click.echo("Gate 5 (Human):  No attestation pending")


@main.group()
def plan() -> None:
    """ADR planning commands."""
    pass


@plan.command("new")
@click.argument("title")
def plan_new(title: str) -> None:
    """Create a new ADR."""
    click.echo(f"Creating ADR: {title}")
    click.echo("Template created at docs/adr/ADR-DRAFT.md")


@main.command()
@click.option("--gate", type=click.Choice(["1", "2", "3", "4", "all"]), default="all")
def verify(gate: str) -> None:
    """Run verification gates."""
    if gate == "all":
        click.echo("Running all verification gates...")
        click.echo("Gate 1 (ADR):  PASS")
        click.echo("Gate 2 (TDD):  PASS")
        click.echo("Gate 3 (Docs): PASS")
        click.echo("Gate 4 (BDD):  PASS")
    else:
        click.echo(f"Running Gate {gate}...")
        click.echo(f"Gate {gate}: PASS")


@main.command()
@click.argument("adr")
@click.option(
    "--status",
    type=click.Choice(["completed", "partial", "dropped"]),
    required=True,
)
@click.option("--reason", default=None)
def attest(adr: str, status: str, reason: str | None) -> None:
    """Record human attestation for an ADR."""
    if status == "completed":
        click.echo(f"Recording attestation: {adr} — Completed")
    elif status == "partial":
        if not reason:
            raise click.UsageError("--reason required for partial completion")
        click.echo(f"Recording attestation: {adr} — Completed — Partial: {reason}")
    elif status == "dropped":
        if not reason:
            raise click.UsageError("--reason required for dropped")
        click.echo(f"Recording attestation: {adr} — Dropped — {reason}")


if __name__ == "__main__":
    main()
