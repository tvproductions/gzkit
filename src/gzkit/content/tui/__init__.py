"""Light TUI affordances for gz content commands (OBPI-0.0.34-05)."""

from __future__ import annotations

from gzkit.content.tui.panels import render_content_panel
from gzkit.content.tui.status import render_status_line
from gzkit.content.tui.tables import render_content_table

__all__ = ["render_content_panel", "render_status_line", "render_content_table"]
