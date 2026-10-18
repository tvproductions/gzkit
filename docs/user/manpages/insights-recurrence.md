# gz insights recurrence

Check whether cited records qualify a failure to become a rule (drydock RO-1).

---

## Overview

Maxim 13 (tampering): a single failure is recorded as an insight. It becomes a
rule only when it recurs. The operator's rulings of 2026-10-18 set what
recurrence means:

- **Threshold** (*"3 occurrences (Rec.)"*): the number of cited records required,
  read from `data/recurrence_threshold.json` (`min_occurrences`). A project
  without that file uses 3.
- **Unit** (*"Cited records (Rec.)"*): a proposal cites insight records (by `ts`)
  or GHIs (`#N`) of one class of failure. The proposer judges the class, and this
  verb checks only the count and the separation.
- **Separation** (*"One lease apart (Rec.)"*): every pair of cited records must be
  at least one session lease apart by full timestamp. The lease is
  `lock_manager.DEFAULT_LOCK_TTL_MINUTES`. Records written inside one lease count
  as one occurrence.

A GHI resolves to its `createdAt` through `gh issue view`. A citation that names
no insight record, or a GHI that cannot be resolved, exits 1.

---

## Usage

```
gz insights recurrence [--json] CITE [CITE ...]
```

| Option | Meaning |
|--------|---------|
| `CITE` | An insight record's `ts`, or a GHI number as `#N` or `N` |
| `--json` | Emit the verdict as JSON to stdout |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Met: enough citations, every pair at least a lease apart |
| 1 | A citation names no insight record or resolvable GHI |
| 2 | Usage error |
| 3 | Not met: too few citations, or a pair inside one lease |

---

## Examples

Two GHIs filed the same day as the insight they cite count as one occurrence
(captured 2026-10-18):

```bash
uv run gz insights recurrence 2026-10-18T21:15:21.627886+00:00 '#1257' '#1258' --json
```

```json
{
  "met": false,
  "cited": 3,
  "required": 3,
  "separation_hours": 24.0,
  "too_close": [
    [
      "2026-10-18T21:15:21.627886+00:00",
      "#1257"
    ],
    [
      "2026-10-18T21:15:21.627886+00:00",
      "#1258"
    ],
    [
      "#1257",
      "#1258"
    ]
  ]
}
```

The command exits 3.
