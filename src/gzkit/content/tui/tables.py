"""Rich table renderer for gz content list (OBPI-0.0.34-05)."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table


def render_content_table(rows: list[dict[str, str]]) -> None:
    """Render a Rich table of content types to stdout.

    Only call when sys.stdout.isatty() is True and --plain is not set.
    """
    console = Console(highlight=False)
    table = Table(show_header=True, header_style="bold")
    table.add_column("Type")
    table.add_column("Description")
    for row in rows:
        table.add_row(row["type"], row["description"])
    console.print(table)
