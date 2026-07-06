# gz ontology sense

Sweep the current structural shape and surface STRUCTURAL seams (read-only).

---

## Usage

```bash
gz ontology sense [--json] [--dot]
```

---

## Runtime Behavior

- Projects the corpus domain from L1 canon + the L2 ledger (read-only).
- Renders the node shape (type, id, ownership, plane) as a table.
- Surfaces STRUCTURAL seams — edges whose endpoint is not a materialized node.
- Labels coverage as STRUCTURAL and never claims semantic completeness
  (Boundary Invariant #3).
- Persists a Tier-B derived `.gzkit/ontology/last_sweep.json` baseline for
  `gz ontology resense` to diff against. This derived cache is not graph state.
- Always exits 0 — the sonar images, it never gates (Boundary Invariant #2).

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit the machine-readable shape plus the rebuild-fidelity self-report (replay completeness + freshness) to stdout |
| `--dot` | Emit a graphviz DOT rendering of the shape to stdout |

---

## Example

```bash
uv run gz ontology sense
uv run gz ontology sense --json
uv run gz ontology sense --dot
```
