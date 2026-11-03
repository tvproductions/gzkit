# gz chores status

Report every registered chore's staleness band without running any chore.
Staleness announces that a chore run is due; it never gates, so every band
exits 0.

---

## Usage

```bash
gz chores status
gz chores status --check B
gz chores status --json
```

| Flag | Meaning |
|------|---------|
| `--check {A,B,C,D}` | Show one check's package: the chores at that level and every level below it |
| `--json` | Emit the board as JSON to stdout |

---

## Runtime Behavior

- Reads each registered chore's class declaration (`staleness.signal`,
  `periodDays`, `graceDays`, `paused`, `surfaces`, `artifacts`) from `registry.json`, plus
  the passing run blocks `gz chores run` appends to
  `.gzkit/chores/<slug>/proofs/CHORE-LOG.md`.
- Only a `- Status: PASS` run block counts as a run. A FAIL block and a
  hand-written heading never reset a chore's clock.
- Bands, loudest first:

| Band | Meaning |
|------|---------|
| `overdue` | Past its grace, or no passing run on record |
| `due` | Came due within its grace; announced, not yet overdue |
| `unmeasured` | The declaration gives nothing to measure: `accumulated-work` declares no counter and no `periodDays`, no declared surface has commit history, or the chore is undeclared |
| `paused` | Declared `staleness.paused`: intentional dormancy, not a failure |
| `current` | Not yet due |

- `elapsed-time`: due once `periodDays` have passed since the last passing
  run, overdue after `graceDays` more. A chore that declares
  `staleness.artifacts` is dated by the last change to that scan record
  instead, and its run blocks are not read. That is how its gate,
  `scripts/check_proof_freshness.py`, dates it, and it is what lets an overdue
  chore clear by doing its scan while a bare re-run cannot (GHI #935). An
  uncommitted edit to the record counts as a change today; a deleted record
  never does.
- `content-delta`: due from the oldest commit that touches a declared
  `staleness.surfaces` path after the last passing run, and overdue after
  `graceDays` more. Git committer dates are compared, never file mtimes, and
  uncommitted edits are not counted. A `periodDays` declared beside the
  surfaces also dates the chore: it is due at whichever comes first.
- `accumulated-work` with `periodDays`: due by date, as `elapsed-time` reads
  its passing runs; without it, `unmeasured`.
- Each chore's check level, from its declared `check`, shows in the Level
  column; `A?` marks a provisional level. A check includes every level below
  it, so `--check C` shows the A, B and C chores.
- Runs no acceptance criterion and writes no file.
- `--json` emits `{"chores": [...], "counts": {...}}` to stdout. Each chore
  record carries `slug`, `signal`, `band`, `last_run`, `due_since`,
  `reason`, `check_level` and `check_provisional`; the top level carries the
  `check` requested, or `null`.
- Session orientation (`scripts/session_orientation.py`) reads
  `gz chores status --json` and announces due and overdue chores at session
  start. It adds nothing when no chore is due or overdue.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Status reported, whatever the bands |
| 1 | Registry invalid (for example, a content-delta chore declaring no surfaces) |
| 2 | Usage error |

---

## Example

```bash
uv run gz chores status
uv run gz chores status --check B
uv run gz chores status --json
```
