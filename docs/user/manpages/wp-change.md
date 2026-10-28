# gz wp change

Record one change to a live work package on the change ladder, or an alteration or a departure from specification.

## Usage

```bash
gz wp change <WP-id> --rung <rung> --approver {operator,coordinator} --change <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--rung` | `pen_and_ink`, `change_order`, `attachment`, `supplement`, `alteration` or `departure`. Required |
| `--approver` | `coordinator` for pen and ink; `operator` for every other rung. Required |
| `--change` | The change made (a new item's description). Required |
| `--superseded` | The superseded content, kept. Required for pen and ink and a change order |
| `--work-stopped` | Work stopped. Required on a change order, refused on any other rung |
| `--supplement` | The supplement's work package id (supplement only) |
| `--item` | The alteration or departure id the change records |
| `--configuration-change` | A new alteration's configuration change: `reconnected`, `replaced` or `retired` |
| `--form`, `--duration`, `--clear-by`, `--req` | A new departure: `deviation` or `waiver`; `temporary` (with a clear-by condition) or `permanent`; the REQ it departs on |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Books one `work_package_changed` event (the change ladder, `docs/governance/harbor-ro5-work-packages.md`
amendments 3 and 4). A package must be initiated and not closed. A departure or
alteration not yet in the record joins the store together with the event that
records it; when the change is refused, neither the record nor the ledger
changes. A departure's form, duration and clear-by condition on the event are
copied from the store.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp change WP-01-astral --rung pen_and_ink --approver coordinator \
    --change "Resequence the cards" --superseded "Cards 2, 1"
WP-01-astral: pen_and_ink recorded (coordinator).

$ uv run gz wp change WP-01-astral --rung departure --approver operator \
    --change "No Windows runner" --item DFS-1 --form waiver --duration temporary \
    --clear-by "the runner lands"
WP-01-astral: departure recorded (operator).
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The change was booked |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The rung, approver or package state refuses it; nothing was written |

## See also

[`gz wp new`](wp-new.md), [`gz wp show`](wp-show.md),
[`gz validate --catalog`](validate.md)
