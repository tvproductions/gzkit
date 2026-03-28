"""BDD step definitions for reporter rendering feature."""

from __future__ import annotations

import io

from behave import given, then, when  # type: ignore[import-untyped]
from rich.console import Console

from gzkit.reporter import ColumnDef, ceremony_panel, kv_table, list_table, status_table


@given('a status_table with title "{title}" and columns "{col_csv}" and {n:d} rows')
def step_given_status_table(context, title, col_csv, n):
    columns = [ColumnDef(header=h.strip()) for h in col_csv.split(",")]
    rows = []
    for i in range(n):
        row = {}
        for col in columns:
            if col.header == "ADR":
                row[col.header] = f"ADR-0.{i + 1}.0"
            elif col.header == "Lane":
                row[col.header] = "heavy" if i % 2 == 0 else "lite"
            elif col.header == "Status":
                row[col.header] = "Validated" if i % 2 == 0 else "Pending"
            else:
                row[col.header] = f"val-{i}"
        rows.append(row)
    context.renderable = status_table(title=title, columns=columns, rows=rows)


@given('a kv_table with title "{title}" and {n:d} pairs')
def step_given_kv_table(context, title, n):
    pairs = [("Lane", "heavy"), ("Status", "Proposed"), ("OBPIs", "0/5")][:n]
    context.renderable = kv_table(title=title, rows=pairs)


@given('a ceremony_panel with title "{title}" and {n:d} items')
def step_given_ceremony_panel(context, title, n):
    items = [
        ("Step 1: Trigger recognized", "✓"),
        ("Step 2: Evidence presented", "✓"),
    ][:n]
    context.renderable = ceremony_panel(title=title, items=items)


@given('a list_table with title "{title}" and columns "{col_csv}" and {n:d} rows')
def step_given_list_table(context, title, col_csv, n):
    columns = [ColumnDef(header=h.strip()) for h in col_csv.split(",")]
    rows = []
    for i in range(n):
        row = {}
        for col in columns:
            if col.header == "Slug":
                row[col.header] = f"chore-{chr(97 + i)}"
            elif col.header == "Title":
                row[col.header] = f"Chore {i + 1}"
            elif col.header == "Name":
                row[col.header] = f"skill-{i + 1}"
            else:
                row[col.header] = f"val-{i}"
        rows.append(row)
    context.renderable = list_table(title=title, columns=columns, rows=rows)


@when("the table is rendered to text")
@when("the panel is rendered to text")
def step_when_rendered(context):
    buf = io.StringIO()
    console = Console(file=buf, no_color=True, width=120)
    console.print(context.renderable)
    context.rendered_output = buf.getvalue()


@then('the rendered output contains "{text}"')
def step_then_output_contains(context, text):
    assert text in context.rendered_output, (
        f"Expected '{text}' in output:\n{context.rendered_output}"
    )
