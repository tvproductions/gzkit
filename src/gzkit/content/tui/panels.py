"""Rich panel renderer for gz content show (OBPI-0.0.34-05)."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel


def render_content_panel(*, title: str, body: str) -> None:
    """Render a plan-mode-style Rich panel to stdout.

    Only call when sys.stdout.isatty() is True and --plain is not set.
    """
    console = Console(highlight=False)
    console.print(Panel(body, title=title, expand=False))
