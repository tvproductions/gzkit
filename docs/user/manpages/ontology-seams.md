# gz ontology seams

Fast contacts-only STRUCTURAL seam check (read-only).

---

## Usage

```bash
gz ontology seams [--json] [--dot]
```

---

## Runtime Behavior

- Projects the corpus domain and lists STRUCTURAL seams only — edges whose
  source or target is not a materialized node — without full per-node lineage.
- On a healthy tree, surfaces no seam (the false-positive floor that keeps the
  sonar trustworthy).
- Always exits 0 — the sonar never gates (Boundary Invariant #2).

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit the seam list as JSON to stdout |
| `--dot` | Emit a graphviz DOT rendering of the shape to stdout |

---

## Example

```bash
uv run gz ontology seams
uv run gz ontology seams --json
```
