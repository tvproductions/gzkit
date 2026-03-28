# Reporter Architecture

The reporter module (`src/gzkit/reporter/`) is gzkit's centralized rendering layer for CLI output.

## Three-Layer Model

```text
Commands (produce data) → Reporter (render) → OutputFormatter (route)
```

| Layer | Responsibility | Owns |
|-------|---------------|------|
| Commands | Build data dicts from governance state | What data to show |
| Reporter | Convert data to Rich renderables | How it looks |
| OutputFormatter | Route to stdout/json/quiet | Where it goes |

## Presets

The reporter provides four named presets:

### status_table

Governance-style table with row striping. Used by `gz status`, `gz adr report`.

- Box style: `box.ROUNDED`
- Row styles: alternating `["none", "dim"]`
- Accepts `ColumnDef` list and row dicts

### kv_table

Two-column key-value table. Used for detail views.

- Box style: `box.ROUNDED`
- No header row
- Bold labels, plain values

### list_table

Simple catalog table. Used by `gz task list`, `gz chores list`, `gz roles`, `gz skill list`.

- Box style: `box.ROUNDED`
- No row striping
- Accepts `ColumnDef` list and row dicts

### ceremony_panel

Double-bordered panel for ceremony outputs (closeout summaries, gate status).

- Box style: `box.DOUBLE`
- Inner table with step labels and status indicators
- Rich handles all padding and alignment

## Column Definitions

Columns are defined using `ColumnDef`, a frozen Pydantic model:

```python
from gzkit.reporter import ColumnDef

col = ColumnDef(
    header="ADR",           # Display header
    key="adr_id",           # Dict key (defaults to header)
    style="cyan",           # Rich style
    justify="right",        # Alignment
    no_wrap=True,           # Prevent wrapping
    overflow="ellipsis",    # Overflow handling
)
```

## Usage

```python
from gzkit.reporter import status_table, ColumnDef

columns = [
    ColumnDef(header="ADR", style="cyan"),
    ColumnDef(header="Lane"),
    ColumnDef(header="Status"),
]
rows = [{"ADR": "ADR-0.1.0", "Lane": "heavy", "Status": "Validated"}]

table = status_table(title="ADR Status", columns=columns, rows=rows)
console.print(table)
```

## Design Constraints

- **Pure functions** — no IO, no ledger reads, no business logic
- **Data in, renderable out** — accept dicts/tuples, return Rich objects
- **Stateless** — no side effects, no caching, no global state
