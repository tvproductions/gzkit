# gz wp discrepancy show

Show the list of discrepancies: the open lines, or every line with `--all`.

## Usage

```bash
gz wp discrepancy show [--all] [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--all` | Every line recorded, open and cleared, each marked which |
| `--json` | Output the list as JSON, each line its record's fields with `clear` |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The list of discrepancies is ledger events, rendered as a view (RP-12 rulings 9 and
168): this verb renders it, read-only, from the `discrepancy_recorded` and
`discrepancy_cleared` events, oldest first. `docs/governance/harbor-ro12-contractor-kit.md`
§ Rulings holds the rulings cited here.

- By default it shows the open lines, those with no clear; `--all` shows every
  line, each marked `open` or `cleared`, as `gz wp tag show` renders the tag-out
  log (ruling 110's form).
- Each line is a block of labelled lines (ruling 126's form): its id, order and
  package, then its grade, the event a `due-by-event` line is due by, its source,
  what is wrong, the tag it cites, when and by whom it was recorded (the
  coordinator, or the performer's dispatch), the MX session, and its clear: `open`,
  or when it was cleared and the evidence cited, with its root cause, corrective
  action and recurrence citations where it carries them (rulings 172, 180 and 181).
- `--json` prints the list, each line its `discrepancy_recorded` fields with
  `clear`, the `discrepancy_cleared` event or `null`.
- It writes nothing, needs no MX session and is not refused from a subagent's
  call: a read is no one's act. A discrepancy row that does not parse is refused
  with the void that recovers it.

## Examples

Observed 2026-11-20 in the scratch project of
[`gz wp discrepancy record`](wp-discrepancy-record.md), with
`DSC-01-hook-left-off` recorded blocking and cleared on `ENT-01-stamp-import`, and
`DSC-02-size-gate` recorded due by an event and open.

With no line recorded, exit 0:

```console
$ uv run gz wp discrepancy show
No discrepancy is open.
```

Every line, exit 0:

```console
$ uv run gz wp discrepancy show --all
DSC-01-hook-left-off on ORD-01-import (WP-01-stamp) (cleared)
  Grade:       blocks-return-to-service
  Source:      left-broken
  Description: The hook is left off.
  Recorded:    2026-11-20T11:05:53.717783+00:00 by the coordinator
  MX session:  test-session
  Cleared:     2026-11-20T11:05:53.719007+00:00 on ENT-01-stamp-import
  Root cause:  Disabled for the repair.
  Corrective:  Restored.

DSC-02-size-gate on ORD-01-import (WP-01-stamp) (open)
  Grade:       due-by-event
  Due by:      O9's carry
  Source:      left-broken
  Description: The size gate stays advisory.
  Recorded:    2026-11-20T11:05:53.719804+00:00 by the coordinator
  MX session:  test-session
  Cleared:     open
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Shown, an empty list included |
| 1 | The project is not initialized |
| 2 | Usage or System/IO error |
| 3 | A discrepancy row does not parse; void it with the command the refusal names |

## See also

[`gz wp discrepancy record`](wp-discrepancy-record.md), [`gz wp discrepancy clear`](wp-discrepancy-clear.md),
[`gz wp tag show`](wp-tag-show.md), [`gz wp entry show`](wp-entry-show.md)
