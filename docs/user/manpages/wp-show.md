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

Reads the record from the store and its `work_package_transitioned`,
`work_package_changed` and `work_package_issue_closed` events from the ledger.
The state is the last move's target; a package with no move is `not initiated`.
The lane is held once (ruling 4): a repair package's stored lane, or for a
delivery package `heavy` exactly when its outcome is user-facing (requirements
model decision 10; RO-5 tranche 4). `--json` prints the record, the state, the
lane and every event.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp show WP-01-astral
WP-01-astral (repair), state: initiated
  delivers: #1183, #1184  lane: lite
  2026-10-28T07:42:15.383859+00:00  work_package_transitioned  initiated
  2026-10-28T07:42:15.633870+00:00  work_package_issue_closed  #1183
  2026-10-28T07:42:15.885162+00:00  work_package_issue_closed  #1184
$ uv run gz wp show WP-02-resume
WP-02-resume (delivery), state: closed
  delivers: H1  lane: lite
  2026-10-28T08:23:19.142735+00:00  work_package_transitioned  initiated
  2026-10-28T08:23:19.392955+00:00  work_package_transitioned  frozen
  2026-10-28T08:23:19.643329+00:00  work_package_transitioned  commenced
  2026-10-28T08:23:19.894378+00:00  work_package_transitioned  accepted
  2026-10-28T08:23:20.146768+00:00  work_package_transitioned  closed
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
