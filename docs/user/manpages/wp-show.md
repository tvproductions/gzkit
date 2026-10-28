# gz wp show

Show a work package's record, its lifecycle state and its ledger history.

## Usage

```bash
gz wp show <WP-id> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Reads the record from the store and its `work_package_transitioned` and
`work_package_changed` events from the ledger. The state is the last move's
target; a package with no move is `not initiated`. `--json` prints the record,
the state and every event.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp show WP-01-astral
WP-01-astral (repair), state: initiated
  delivers: #1183, #1184  lane: lite
  2026-10-28T07:11:48.689204+00:00  work_package_transitioned  initiated
  2026-10-28T07:11:48.689786+00:00  work_package_changed  departure
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Shown |
| 1 | The work package is not in the store |
| 2 | Usage error |

## See also

[`gz wp new`](wp-new.md), [`gz wp show`](wp-show.md),
[`gz validate --catalog`](validate.md)
