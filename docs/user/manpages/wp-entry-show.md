# gz wp entry show

Show the maintenance record: every entry booked, oldest first, with the commits that landed it and its order's Gate 5.

## Usage

```bash
gz wp entry show [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output the entries as JSON, each the `entry_booked` event's fields with `gate5` and `landed` |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The maintenance record is ledger events, and the record is a Layer 3 view
rendered from them, never edited (RP-12 rulings 8 and 168). `gz wp entry show`
renders it. `docs/governance/harbor-ro12-contractor-kit.md` § Rulings holds the
rulings cited here.

- Each entry is a block of labelled lines, the form ruling 126 gave the tag-out
  log: its id, order and package, then when it was booked, the performer (the
  dispatch that booked it with [`gz wp entry book`](wp-entry-book.md)), what was
  done, the measurement before and after, the witness that measured them, the MX
  session, the commits that landed it and its Gate 5, one line each. The block is
  the record's one block: the MX log that [`gz mx exit`](mx-exit.md) renders
  writes each entry with it too (ruling 191).
- The Landed line names each commit whose subject names the entry,
  `(ENT-<NN>-<slug>)` (ruling 170), as `<sha12> <subject>`, a second commit on
  the line under the first, read from git's history; an entry no commit names
  reads `not landed` (rulings 167 and 192), and so does every entry outside a git
  working tree. The MX log joins the same way, so the two views agree.
- The Gate 5 line is the signature 14 CFR § 43.9(a) asks of the approver: the
  order's close at Gate 5, as `<attestor>, <decision>, <when>`, once
  [`gz wp order close`](wp-order-close.md) closes the order, and `not signed`
  until then (ruling 8). The decision is printed as booked, so a `terminate` or
  `pause` reads as one.
- With no entry booked, it prints `No entry has been booked.`
- `--json` prints a list, oldest first: each entry's `entry_booked` event, as
  `gz wp entry book` booked it, with `gate5`, the order's `order_transitioned`
  event to `closed` or `null`, and `landed`, a list of the landing commits, each
  its `commit_sha` and `subject`, empty when not landed. An empty record prints
  `[]`.

The verb writes nothing and needs no MX session, and it is not refused from a
subagent's call: a read is no one's act.

## Examples

Observed 2026-11-21 in a scratch project set up as
`tests/commands/test_wp_entry.py` sets one up: `ORD-01-import` commenced and a
`Restoration` dispatch booked on it, the project a git repository. Its MX marker
was opened by the test helper, so the session id below is that fixture's.

Before any entry is booked:

```console
$ uv run gz wp entry show
No entry has been booked.
```

After the `Restoration` dispatch booked `ENT-01-stamp-import` and the commit
`fix(stamp): the template imports again (ENT-01-stamp-import)` landed it, the
order not yet closed:

```console
$ uv run gz wp entry show
ENT-01-stamp-import on ORD-01-import (WP-01-stamp)
  Booked:      2026-11-21T08:57:53.030919+00:00
  Performer:   D-7b33cf373c3bfc9a
  Description: The stamp generator imports its template again.
  Before:      tests.test_stamp fails: ImportError on the template
  After:       tests.test_stamp passes, 12 tests
  Witness:     uv run -m unittest tests.test_stamp
  MX session:  test-session
  Landed:      bc048dec67af fix(stamp): the template imports again (ENT-01-stamp-import)
  Gate 5:      not signed
```

Before the commit landed, the same entry's Landed line read `not landed`.

The same record as JSON:

```console
$ uv run gz wp entry show --json
[
  {
    "after": "tests.test_stamp passes, 12 tests",
    "before": "tests.test_stamp fails: ImportError on the template",
    "description": "The stamp generator imports its template again.",
    "dispatch_id": "D-7b33cf373c3bfc9a",
    "entry_id": "ENT-01-stamp-import",
    "event": "entry_booked",
    "gate5": null,
    "id": "ENT-01-stamp-import",
    "landed": [
      {
        "commit_sha": "bc048dec67af1b14bd0e06e28c32c662354e941c",
        "subject": "fix(stamp): the template imports again (ENT-01-stamp-import)"
      }
    ],
    "mx_session_id": "test-session",
    "order": "ORD-01-import",
    "schema": "gzkit.ledger.v1",
    "ts": "2026-11-21T08:57:53.030919+00:00",
    "witness": "uv run -m unittest tests.test_stamp",
    "work_package": "WP-01-stamp"
  }
]
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Shown, an empty record included |
| 1 | The project is not initialized |
| 2 | Usage or System/IO error |
| 3 | An `entry_booked` row, or an order's closing `order_transitioned` row, does not parse; the refusal names the row and the `gz ledger correct` void that recovers it |

## See also

[`gz wp entry book`](wp-entry-book.md), [`gz wp order close`](wp-order-close.md),
[`gz wp tag show`](wp-tag-show.md), [`gz mx exit`](mx-exit.md)
