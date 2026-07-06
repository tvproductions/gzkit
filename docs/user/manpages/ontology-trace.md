# gz ontology trace

Walk one node's vertical lineage and lateral proof with edge provenance (read-only).

---

## Usage

```bash
gz ontology trace <ID> [--json] [--dot]
```

---

## Runtime Behavior

- Returns the node's **vertical lineage**: transitive ancestors and descendants
  along the CHILD hierarchy.
- Returns the node's **lateral anchors/proof**: non-hierarchy edges touching the
  node (supersession, validation, attestation).
- Reports **edge provenance** — why each edge touching the node is present.
- Exits 1 if the node id is unknown.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `ID` | The node id to trace (e.g. `ADR-0.31.0-obpi-state-machine`) |

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit the trace (ancestors, descendants, lateral, provenance) as JSON to stdout |
| `--dot` | Emit a graphviz DOT rendering of the shape to stdout |

---

## Example

```bash
uv run gz ontology trace ADR-0.31.0-obpi-state-machine
uv run gz ontology trace ADR-0.31.0-obpi-state-machine --json
```
