# gz ledger corrections

List every ledger row currently under a correction, and by which disposition.

Read-only. Nothing is edited; this is the census view over the net of the
append-only correction sequence.

---

## Usage

```bash
gz ledger corrections [--json]
```

---

## Why this exists

Corrections are forward events, so *what is currently corrected* is the net of
a sequence rather than a field anyone can read off a row. Without a census the
net is only visible to the code that computes it, and a governance surface
nobody can audit is not a governance surface — the operator would have to
replay the correction chain by hand to answer "what is voided right now?"

---

## PASS/FAIL Contract

Always exits 0. An empty result is reported as "No ledger corrections are in
force", never as an error: no corrections in force is the ordinary state.

---

## Example

```bash
uv run gz ledger corrections
```

```
Corrected ledger rows: 2
  void        pipeline_launched  id=OBPI-9.9.9-01-demo  ts=2026-09-02T00:00:00+00:00
  discharged  task_blocked  id=TASK-9.9.9-01-01-01  ts=2026-09-02T02:00:00+00:00
```

```bash
uv run gz ledger corrections --json
```

```json
[
  {
    "subject_event": "pipeline_launched",
    "subject_id": "OBPI-9.9.9-01-demo",
    "subject_ts": "2026-09-02T00:00:00+00:00",
    "disposition": "void"
  }
]
```

A row that was voided and later reinstated does not appear: `reinstated`
clears the entry rather than adding a third state.

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit the census as JSON to stdout |

---

## Related

- [`gz ledger correct`](ledger-correct.md) — record a corrective action
