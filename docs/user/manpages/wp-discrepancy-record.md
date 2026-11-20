# gz wp discrepancy record

Record a line on the list of discrepancies: the coordinator's on an order, or a performer's find in the work.

## Usage

```bash
gz wp discrepancy record --slug <slug> --grade <grade> --source <source> \
  --description <text> [--due-by <text>] (--order <ORD-id> | --dispatch <D-id>) \
  [--tag <TAG-id>] [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--slug` | Lowercase words joined by hyphens, the last part of `DSC-<NN>-<slug>`. Required |
| `--grade` | `blocks-return-to-service` or `due-by-event`. Required |
| `--source` | `left-broken`, `inspector-rejection` or `found-in-work`. Required |
| `--description` | What is wrong. Required |
| `--due-by` | The event a `due-by-event` line is due by, in text; refused on a blocking line |
| `--order` | The line's order, named by the coordinator's unstamped call |
| `--dispatch` | The live performer that found it, the one this call is stamped with |
| `--tag` | A tag issued on the order, cited by the coordinator's line |
| `--json` | Output the booked `discrepancy_recorded` event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The list of discrepancies is ledger events, rendered as a view (RP-12 ruling 9):
one `discrepancy_recorded` event per line, cleared later by a
`discrepancy_cleared` event with its evidence (`gz wp discrepancy clear`).
`docs/governance/harbor-ro12-contractor-kit.md` § Rulings holds the rulings cited
here.

- A line is graded `blocks-return-to-service`, which holds the repair package's
  return to service, or `due-by-event`, due by an event `--due-by` names in text,
  such as `O9's carry`; nothing checks that the event has come (rulings 9 and 179).
- Every line is on an order of a repair package initiated and not closed, the
  order in any state but closed and never unopened; a blocked order and an order
  stopped by an exit still take lines, a discrepancy often being what holds one
  (ruling 178). A line with no order waits on O9's carry.
- The coordinator's unstamped call names `--order` and records any source but an
  inspector's rejection, which the QAI dispatch O6 lands will record; it may cite a
  `--tag` issued on that order, the carry ruling 171 reads (rulings 114 and 172).
- A performer's stamped call records a find in the work: the call is stamped with
  the live `Implementer`, `SingleDriver` or `Restoration` dispatch `--dispatch`
  names, and the order is read from that dispatch, never typed (rulings 1, 130,
  172 and 175). It names no `--order` and cites no `--tag`.
- A subagent's call stamped with no dispatch id is refused: neither the
  coordinator nor a dispatched performer makes it (rulings 1 and 172).
- The line's id is the next `DSC-<NN>-<slug>`, numbered past every line the
  ledger's history names, a voided one included (rulings 169 and 176). The open MX
  session is recorded with it; with no session open the line is refused, and a
  marker present but unreadable, unbound or exiting is refused with the repair its
  cause names.

A refusal names what failed, why and what to do, and books nothing.

## Examples

Observed 2026-11-20 in a scratch project set up as
`tests/commands/test_wp_discrepancy.py` sets one up: `ORD-01-import` frozen on
`REQ-1@1`, commenced with no isolation, a `Restoration` dispatch booked on it and
an MX marker opened by the test helper. The performer's call was stamped as the
stamp hook stamps that dispatch's subagent.

From the coordinator's call, exit 0:

```console
$ uv run gz wp discrepancy record --order ORD-01-import --source left-broken \
    --slug hook-left-off --grade blocks-return-to-service \
    --description 'The stamp hook is left off.'
Recorded DSC-01-hook-left-off on ORD-01-import.
```

A `due-by-event` line with no `--due-by`, exit 3:

```console
$ uv run gz wp discrepancy record --order ORD-01-import --source left-broken \
    --slug size-gate --grade due-by-event --description 'The size gate stays advisory.'
--due-by is required on a line graded due by a named event, and names the event
in text, such as `O9's carry` (RP-12 ruling 179). Record it again with the
event.
```

An inspector's rejection, exit 3:

```console
$ uv run gz wp discrepancy record --source inspector-rejection --order ORD-01-import \
    --slug x --grade blocks-return-to-service --description d
An inspector's rejection is recorded by the QAI dispatch O6 lands, which is not
built (RP-12 ruling 172). Record the line as `left-broken` from the
coordinator's call if the work left it broken, or wait on O6.
```

From the `Restoration` dispatch's stamped call, exit 0:

```console
$ uv run gz wp discrepancy record --dispatch D-1dfa45241f383cc1 --source found-in-work \
    --slug stale-cache --grade due-by-event --due-by 'the next order' \
    --description 'The cache is never invalidated.'
Recorded DSC-02-stale-cache on ORD-01-import.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Recorded |
| 1 | The project is not initialized |
| 2 | Usage or System/IO error |
| 3 | Refused: no MX session open or a marker present but not on (its repair named), a subagent's call with no dispatch id, a malformed slug or a blank description, a grade and `--due-by` that disagree, an inspector's rejection, the coordinator's line with no `--order` or naming `--dispatch`, a performer's call not stamped as its dispatch, not a find in the work, typing `--order` or `--tag`, or its dispatch not a live `Implementer`, `SingleDriver` or `Restoration` on an order, an order not held, never opened or closed, or of a package not initiated, or a tag not issued on the order; nothing booked |

## See also

[`gz wp discrepancy clear`](wp-discrepancy-clear.md), [`gz wp entry book`](wp-entry-book.md),
[`gz wp tag issue`](wp-tag-issue.md), [`gz wp order accept`](wp-order-accept.md)
