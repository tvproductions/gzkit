# gz ontology resense

Diff the current shape versus the last sweep — the airlock re-sense gate (read-only).

---

## Usage

```bash
gz ontology resense [--json] [--dot]
```

---

## Runtime Behavior

- Reads the Tier-B derived baseline persisted by `gz ontology sense` at
  `.gzkit/ontology/last_sweep.json`.
- Projects a fresh live sweep and reports the diff: added and removed nodes and
  edges since the baseline — so drift against a prior point in time is
  detectable (not merely a two-live-rebuild comparison).
- If no baseline exists, prints a hint to run `gz ontology sense` first.
- Always exits 0 — the sonar never gates (Boundary Invariant #2).

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit the diff (added/removed nodes and edges) as JSON to stdout |
| `--dot` | Emit a graphviz DOT rendering of the current shape to stdout |

---

## Example

```bash
uv run gz ontology sense       # seed the baseline
uv run gz ontology resense     # later: report drift since the baseline
uv run gz ontology resense --json
```
