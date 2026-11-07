# gz chores record-processed

Book one `chore_decommission_processed` ledger event for a test file the
`decommission-tautological-tests` chore processed (GHI #1305).

---

## Usage

```bash
gz chores record-processed <slug> --file <path> --disposition <disposition> (--obpi <OBPI-ID> | --task <TASK-ID>) [--json]
```

---

## Runtime Behavior

- Writes one `chore_decommission_processed` event through the ledger writer, never by editing
  `.gzkit/ledger.jsonl`.
- Every input is checked before anything is written; a refusal exits 1 and writes nothing:
  - `<slug>` must be `decommission-tautological-tests`, the one chore that processes items.
  - Exactly one work order: `--obpi OBPI-…` for a batch under an OBPI, or `--task TASK-…` for a
    chore batch outside one (operator ruling 2026-11-07).
  - `--disposition` must be one the ledger schema admits: `convert`, `replace-with-ledger`,
    `fold-to-validator`, `keep-as-fixture`, `fold-to-validator+keep-as-fixture`,
    `fold-to-validator-whole-file-delete`, `no-op-already-clean`.
  - `--file` must hold an op in `data/tautological_test_baseline.json`, so a file the chore never
    flagged cannot be booked as processed.
- One event per processed file, as the first sweep wave booked them (OBPI-0.0.59-05).

---

## Options

| Flag | Description |
|------|-------------|
| `--file` | Repo-relative path of the test file processed (required) |
| `--disposition` | Disposition applied to it (required) |
| `--obpi` | OBPI id the batch ran under |
| `--task` | TASK id the batch ran under, for a batch outside an OBPI |
| `--json` | Print the booked fields as JSON |

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | The event was booked |
| 1 | A refusal: another slug, no or two work orders, an unknown disposition, or a file not in the baseline |

---

## Example

Booking the file the chore's 2026-11-07 batch converted (`ed92076a0`):

```bash
uv run gz chores record-processed decommission-tautological-tests \
  --file tests/commands/test_upgrade_resources.py --disposition convert \
  --task TASK-chore-decommission-tautological-tests
```

```text
Recorded chore_decommission_processed: tests/commands/test_upgrade_resources.py
(convert) under TASK-chore-decommission-tautological-tests
```
