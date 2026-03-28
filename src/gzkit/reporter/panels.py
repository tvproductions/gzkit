"""Reporter panels — ceremony and summary panels for gzkit CLI output.

Pure rendering layer: data in, Rich renderables out.
No IO, no ledger reads, no business logic.
"""

from __future__ import annotations

from rich import box
from rich.panel import Panel
from rich.table import Table


def ceremony_panel(
    *,
    title: str,
    items: list[tuple[str, str]],
    subtitle: str | None = None,
) -> Panel:
    """Build a ceremony-style panel with box.DOUBLE border.

    Each item is rendered as a row in an inner table with step label
    and status columns. Rich handles all padding and alignment.
    """
    if not items:
        body = "(no items)"
    else:
        inner = Table(show_header=False, box=None, padding=(0, 2))
        inner.add_column("Step", style="bold")
        inner.add_column("Status")
        for label, status in items:
            inner.add_row(label, status)
        body = inner

    return Panel(
        body,
        title=title,
        subtitle=subtitle,
        box=box.DOUBLE,
        padding=(1, 2),
    )
