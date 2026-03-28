"""Reporter presets — four named table/panel styles for gzkit CLI output.

Pure rendering layer: data in, Rich renderables out.
No IO, no ledger reads, no business logic.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from rich import box
from rich.table import Table


class ColumnDef(BaseModel):
    """Column definition for reporter table presets."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    header: str = Field(..., description="Column header text")
    style: str | None = Field(default=None, description="Rich style string")
    justify: Literal["left", "center", "right"] | None = Field(
        default=None, description="Text alignment"
    )
    no_wrap: bool = Field(default=False, description="Prevent text wrapping")
    overflow: Literal["fold", "crop", "ellipsis"] | None = Field(
        default=None, description="Overflow handling"
    )
    key: str | None = Field(
        default=None, description="Dict key to extract from row data; defaults to header"
    )


def _add_columns(table: Table, columns: list[ColumnDef]) -> None:
    """Apply column definitions to a Rich Table."""
    for col in columns:
        kwargs: dict[str, Any] = {}
        if col.style is not None:
            kwargs["style"] = col.style
        if col.justify is not None:
            kwargs["justify"] = col.justify
        if col.no_wrap:
            kwargs["no_wrap"] = True
        if col.overflow is not None:
            kwargs["overflow"] = col.overflow
        table.add_column(col.header, **kwargs)


def _extract_rows(columns: list[ColumnDef], rows: list[dict[str, Any]]) -> list[list[str]]:
    """Extract cell values from row dicts using column definitions."""
    result: list[list[str]] = []
    for row in rows:
        cells = [str(row.get(col.key or col.header, "")) for col in columns]
        result.append(cells)
    return result


def status_table(
    *,
    title: str,
    columns: list[ColumnDef],
    rows: list[dict[str, Any]],
    empty_message: str = "No data.",
) -> Table:
    """Build a governance-style status table.

    Uses box.ROUNDED, alternating row striping, and zero padding.
    """
    if not rows:
        table = Table(title=title, box=box.ROUNDED, padding=(0, 0))
        table.add_column("")
        table.add_row(empty_message)
        return table

    table = Table(title=title, box=box.ROUNDED, padding=(0, 0))
    table.row_styles = ["none", "dim"]
    _add_columns(table, columns)
    for cells in _extract_rows(columns, rows):
        table.add_row(*cells)
    return table


def kv_table(
    *,
    title: str,
    rows: list[tuple[str, str]],
) -> Table:
    """Build a two-column key-value table.

    Uses box.ROUNDED with bold labels and no header row.
    """
    table = Table(title=title, box=box.ROUNDED, show_header=False, padding=(0, 1))
    table.add_column("Label", style="bold")
    table.add_column("Value")
    if not rows:
        table.add_row("No data.", "")
    else:
        for label, value in rows:
            table.add_row(label, value)
    return table


def list_table(
    *,
    title: str,
    columns: list[ColumnDef],
    rows: list[dict[str, Any]],
    empty_message: str = "No items found.",
) -> Table:
    """Build a simple list-style table.

    Uses box.ROUNDED with no row striping.
    """
    if not rows:
        table = Table(title=title, box=box.ROUNDED)
        table.add_column("")
        table.add_row(empty_message)
        return table

    table = Table(title=title, box=box.ROUNDED)
    _add_columns(table, columns)
    for cells in _extract_rows(columns, rows):
        table.add_row(*cells)
    return table
