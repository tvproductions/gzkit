"""Plan command implementation."""

from datetime import date

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.ledger import Ledger, adr_created_event
from gzkit.templates import render_template


def plan_cmd(
    name: str,
    parent_obpi: str | None,
    semver: str,
    lane: str,
    title: str | None,
    dry_run: bool,
) -> None:
    """Create a new ADR (optionally linked to an OBPI)."""
    config = ensure_initialized()
    project_root = get_project_root()

    adr_id = f"ADR-{semver}" if not name.startswith("ADR-") else name
    adr_title = title or name.replace("-", " ").title()

    content = render_template(
        "adr",
        id=adr_id,
        title=adr_title,
        semver=semver,
        lane=lane,
        parent=parent_obpi or "",
        status="Draft",
        date=date.today().isoformat(),
    )

    adr_dir = project_root / config.paths.adrs
    adr_file = adr_dir / f"{adr_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create ADR: {adr_file}")
        console.print(f"  Would append ledger event: adr_created ({adr_id})")
        return

    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file.write_text(content)

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(adr_created_event(adr_id, parent_obpi or "", lane))

    console.print(f"Created ADR: {adr_file}")
