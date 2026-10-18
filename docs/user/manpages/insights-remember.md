# gz insights remember

Append one schema-valid record to the insights store (GHI #575).

---

## Overview

`remember` builds an `InsightRecord` from the flags before it writes anything, so
a missing or malformed required field exits 1 and writes no line. Hand-appended
lines used to drift from the schema this way. Each record also gets one
`insight_recorded` ledger event: the record's `ts`, a SHA-256 of its line, whose
words it carries (`--source`), and an optional `supersedes` reference (operator
ruling 2026-10-18).

---

## Usage

```
gz insights remember --type {defect,defect-resolution,improvement,discovery}
                     --scope SCOPE --summary SUMMARY
                     [--evidence EVIDENCE] [--next-action NEXT_ACTION]
                     [--source {operator,agent}] [--supersedes SUPERSEDES]
```

| Option | Meaning |
|--------|---------|
| `--type` | Record kind |
| `--scope` | Surface or skill the record names |
| `--summary` | One-sentence record body |
| `--evidence` | Command or path witnessing the record (repeatable) |
| `--next-action` | What changes structurally to prevent recurrence |
| `--source` | Whose words the record carries: `operator` only for the operator's own words (default `agent`) |
| `--supersedes` | `ts` of an earlier record this one supersedes; refused when no record has it |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Record appended and booked |
| 1 | Invalid record, or `--supersedes` names no record; nothing written |
| 2 | Usage error |

---

## Examples

```bash
uv run gz insights remember --type improvement --scope obpi-pipeline \
  --summary "governed author verb replaces hand-authored appends"
```
