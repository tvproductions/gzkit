# gz ontology reach

Return one node's downstream blast-radius — transitive dependents (read-only).

---

## Usage

```bash
gz ontology reach <ID> [--json] [--dot]
```

---

## Runtime Behavior

- Returns the transitive-dependent set reachable from the node (its downstream
  blast-radius) via the projection's directed edges.
- Exits 1 if the node id is unknown.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `ID` | The node id to expand (e.g. `ADR-0.32.0-gzkit-ontology`) |

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit the reachable-node set as JSON to stdout |
| `--dot` | Emit a graphviz DOT rendering of the shape to stdout |

---

## Example

```bash
uv run gz ontology reach ADR-0.32.0-gzkit-ontology
uv run gz ontology reach ADR-0.32.0-gzkit-ontology --json
```
