"""Unit tests for gzkit.reporter presets and panels."""

from __future__ import annotations

import io
import unittest

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gzkit.reporter import ColumnDef, ceremony_panel, kv_table, list_table, status_table


def _render(renderable: object) -> str:
    """Render a Rich renderable to plain text."""
    buf = io.StringIO()
    console = Console(file=buf, no_color=True, width=120)
    console.print(renderable)
    return buf.getvalue()


class TestColumnDef(unittest.TestCase):
    """Tests for ColumnDef Pydantic model."""

    def test_minimal_construction(self) -> None:
        col = ColumnDef(header="Name")
        self.assertEqual(col.header, "Name")
        self.assertIsNone(col.style)
        self.assertIsNone(col.justify)
        self.assertFalse(col.no_wrap)
        self.assertIsNone(col.overflow)
        self.assertIsNone(col.key)

    def test_full_construction(self) -> None:
        col = ColumnDef(
            header="ADR",
            style="cyan",
            justify="right",
            no_wrap=True,
            overflow="ellipsis",
            key="adr_id",
        )
        self.assertEqual(col.header, "ADR")
        self.assertEqual(col.style, "cyan")
        self.assertEqual(col.justify, "right")
        self.assertTrue(col.no_wrap)
        self.assertEqual(col.overflow, "ellipsis")
        self.assertEqual(col.key, "adr_id")

    def test_frozen(self) -> None:
        from pydantic import ValidationError

        col = ColumnDef(header="Name")
        with self.assertRaises(ValidationError):
            col.header = "Changed"  # type: ignore[misc]

    def test_extra_field_rejected(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            ColumnDef(header="Name", bogus="value")  # type: ignore[call-arg]


class TestStatusTable(unittest.TestCase):
    """Tests for status_table preset."""

    def test_basic_rendering(self) -> None:
        cols = [
            ColumnDef(header="ADR"),
            ColumnDef(header="Lane"),
            ColumnDef(header="Status"),
        ]
        rows = [
            {"ADR": "ADR-0.1.0", "Lane": "heavy", "Status": "Validated"},
            {"ADR": "ADR-0.2.0", "Lane": "lite", "Status": "Pending"},
        ]
        table = status_table(title="ADR Status", columns=cols, rows=rows)
        self.assertIsInstance(table, Table)
        output = _render(table)
        self.assertIn("ADR Status", output)
        self.assertIn("ADR-0.1.0", output)
        self.assertIn("ADR-0.2.0", output)
        self.assertIn("heavy", output)
        self.assertIn("Validated", output)

    def test_row_striping(self) -> None:
        cols = [ColumnDef(header="Name")]
        rows = [{"Name": "a"}, {"Name": "b"}]
        table = status_table(title="T", columns=cols, rows=rows)
        self.assertEqual(table.row_styles, ["none", "dim"])

    def test_empty_state(self) -> None:
        cols = [ColumnDef(header="Name")]
        table = status_table(title="Empty", columns=cols, rows=[], empty_message="Nothing here.")
        output = _render(table)
        self.assertIn("Nothing here.", output)

    def test_column_key_decoupling(self) -> None:
        cols = [ColumnDef(header="Life", key="lifecycle_status")]
        rows = [{"lifecycle_status": "Validated"}]
        table = status_table(title="T", columns=cols, rows=rows)
        output = _render(table)
        self.assertIn("Life", output)
        self.assertIn("Validated", output)

    def test_column_overflow(self) -> None:
        cols = [ColumnDef(header="ADR", overflow="ellipsis")]
        rows = [{"ADR": "ADR-0.1.0"}]
        table = status_table(title="T", columns=cols, rows=rows)
        self.assertIsInstance(table, Table)


class TestKvTable(unittest.TestCase):
    """Tests for kv_table preset."""

    def test_basic_rendering(self) -> None:
        pairs = [("Lane", "heavy"), ("Status", "Proposed"), ("OBPIs", "0/5")]
        table = kv_table(title="ADR Overview", rows=pairs)
        self.assertIsInstance(table, Table)
        output = _render(table)
        self.assertIn("ADR Overview", output)
        self.assertIn("Lane", output)
        self.assertIn("heavy", output)
        self.assertIn("Proposed", output)

    def test_no_header(self) -> None:
        table = kv_table(title="T", rows=[("k", "v")])
        self.assertFalse(table.show_header)

    def test_empty_rows(self) -> None:
        table = kv_table(title="Empty", rows=[])
        output = _render(table)
        self.assertIn("No data.", output)


class TestListTable(unittest.TestCase):
    """Tests for list_table preset."""

    def test_basic_rendering(self) -> None:
        cols = [
            ColumnDef(header="Slug", style="cyan"),
            ColumnDef(header="Title"),
        ]
        rows = [
            {"Slug": "chore-a", "Title": "First chore"},
            {"Slug": "chore-b", "Title": "Second chore"},
        ]
        table = list_table(title="Chores Registry", columns=cols, rows=rows)
        self.assertIsInstance(table, Table)
        output = _render(table)
        self.assertIn("Chores Registry", output)
        self.assertIn("chore-a", output)
        self.assertIn("Second chore", output)

    def test_no_row_striping(self) -> None:
        cols = [ColumnDef(header="Name")]
        rows = [{"Name": "a"}, {"Name": "b"}]
        table = list_table(title="T", columns=cols, rows=rows)
        self.assertFalse(table.row_styles)

    def test_empty_state(self) -> None:
        cols = [ColumnDef(header="Name")]
        table = list_table(title="Empty", columns=cols, rows=[])
        output = _render(table)
        self.assertIn("No items found.", output)

    def test_custom_empty_message(self) -> None:
        cols = [ColumnDef(header="Name")]
        table = list_table(title="T", columns=cols, rows=[], empty_message="No tasks found.")
        output = _render(table)
        self.assertIn("No tasks found.", output)


class TestCeremonyPanel(unittest.TestCase):
    """Tests for ceremony_panel."""

    def test_basic_rendering(self) -> None:
        items = [
            ("Step 1: Trigger recognized", "✓"),
            ("Step 2: Evidence presented", "✓"),
            ("Step 3: Attestation received", "pending"),
        ]
        panel = ceremony_panel(title="ADR-0.22.0 CLOSEOUT CEREMONY", items=items)
        self.assertIsInstance(panel, Panel)
        output = _render(panel)
        self.assertIn("ADR-0.22.0 CLOSEOUT CEREMONY", output)
        self.assertIn("Trigger recognized", output)
        self.assertIn("pending", output)

    def test_double_box(self) -> None:
        from rich import box

        panel = ceremony_panel(title="T", items=[("a", "b")])
        self.assertEqual(panel.box, box.DOUBLE)

    def test_empty_items(self) -> None:
        panel = ceremony_panel(title="Empty", items=[])
        output = _render(panel)
        self.assertIn("(no items)", output)

    def test_subtitle(self) -> None:
        panel = ceremony_panel(title="T", items=[("a", "b")], subtitle="v0.22.0")
        output = _render(panel)
        self.assertIn("v0.22.0", output)


if __name__ == "__main__":
    unittest.main()
