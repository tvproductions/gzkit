# gz wp entry book

Book a maintenance-record entry, as the stamped call of the dispatch that did the work.

## Usage

```bash
gz wp entry book --dispatch <D-id> --slug <slug> --description <text> \
  --before <text> --after <text> --witness <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--dispatch` | The live dispatch that did the work, the one this call is stamped with. Required |
| `--slug` | Lowercase words joined by hyphens, the last part of `ENT-<NN>-<slug>`. Required |
| `--description` | What was done. Required |
| `--before` | The measurement before. Required |
| `--after` | The measurement after. Required |
| `--witness` | The command or receipt that measured them. Required |
| `--json` | Output the booked `entry_booked` event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The maintenance record is ledger events, rendered as a view (RP-12 ruling 8):
one `entry_booked` event per act of maintenance, each element of 14 CFR
§ 43.9(a) a field. `docs/governance/harbor-ro12-contractor-kit.md` § Rulings
holds the rulings cited here.

- The performer books its own entry (ruling 167). The entry is the stamped call
  of the dispatch `--dispatch` names: `gz`'s entry keeps the dispatch id the call
  was stamped with before it consumes the stamp, and the entry is refused unless
  that id is the one named (ruling 133's form). An unstamped call, the main
  session's or a Codex session's, cannot book; the coordinator relays nothing.
- The dispatch is a live `Implementer`, `SingleDriver` or `Restoration` dispatch,
  booked and neither ended nor voided, bound to an order (rulings 1, 160 and
  175). The order and the package are read from the dispatch record, never
  typed (rulings 1 and 130).
- The order is commenced, where its performers are dispatched, and not blocked
  (rulings 57, 59 and 132). An order stopped by an exit still takes entries: the
  stop ends new work, not the record of the work done (ruling 177).
- The entry says what was done and the measurement before and after, with the
  witness that measured them, none blank (ruling 173). Its id is the next
  `ENT-<NN>-<slug>`, numbered past every entry the ledger's history names, a
  voided one included, so a number never returns (rulings 169 and 176), and the
  commit that lands the work names it in its subject (ruling 170), so the event
  cites no commit.
- The open MX session is recorded with the entry (ruling 8). With no session
  open the entry is refused, and a marker present but unreadable, unbound or
  exiting is refused with the repair its cause names.

A refusal names what failed, why and what to do, and books nothing.

## Examples

Observed 2026-11-20 in a scratch project set up as
`tests/commands/test_wp_entry.py` sets one up: `ORD-01-import` frozen on
`REQ-1@1`, commenced with no isolation, and a `Restoration` dispatch booked on
it. Its MX marker was opened by the test helper, and the stamped call was
stamped as the stamp hook stamps that dispatch's subagent. Each call ran with
`--slug stamp-import --description 'The stamp generator imports its template
again.' --before 'tests.test_stamp fails: ImportError on the template' --after
'tests.test_stamp passes, 12 tests' --witness 'uv run -m unittest
tests.test_stamp'`, shown below as `...`.

From an unstamped call, exit 3 (its wording re-captured 2026-11-20):

```console
$ uv run gz wp entry book --dispatch D-8e6d349499f21f8f ...
This call is not stamped with a dispatch id, and a maintenance-record entry is
the stamped call of the dispatch that did the work, D-8e6d349499f21f8f (RP-12
ruling 167). The entry is booked from D-8e6d349499f21f8f's own subagent, its
prompt carrying the dispatch line; the coordinator relays nothing (14 CFR
43.9(a)).
```

From the `Restoration` dispatch's stamped call, exit 0:

```console
$ uv run gz wp entry book --dispatch D-8e6d349499f21f8f ...
Booked ENT-01-stamp-import on ORD-01-import by D-8e6d349499f21f8f.
```

The same call with `--before ' '`, exit 3:

```console
$ uv run gz wp entry book --dispatch D-8e6d349499f21f8f ... --before ' '
--before is blank. An entry says what was done and the measurement before and
after, with the command or receipt that measured them (RP-12 rulings 8 and 173;
14 CFR 43.9(a)). Book it again with each written out.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Booked |
| 1 | The project is not initialized |
| 2 | Usage or System/IO error |
| 3 | Refused: no MX session open or a marker present but not on (its repair named), the call not stamped with the dispatch named, a malformed slug or a blank field, the dispatch not a live `Implementer`, `SingleDriver` or `Restoration` on an order, or the order not commenced, or blocked; nothing booked |

## See also

[`gz wp dispatch`](wp-dispatch.md), [`gz wp order commence`](wp-order-commence.md),
[`gz wp tag hang`](wp-tag-hang.md), [`gz wp tag clear`](wp-tag-clear.md)
