# gz wp runs

Report what the ledger says every run in flight has reached.

## Usage

```bash
gz wp runs [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

A work package's run is in flight from `commenced` until `closed`, so a package at
`accepted`, awaiting Gate 5, is still reported. An order's run is in flight the
same way, from its own `commenced`, since its repair package stays `initiated`
(RP-12 rulings 44 and 57); its line names the order, and `blocked` reads the
order's block. For each one the verb prints the
last row the run booked (`last`), when it was booked (`at`), the subject last
dispatched against (`subject`) and whether the package awaits the operator
(`blocked`). No run in flight says so and exits 0. Text the verbs recorded, a block
reason among it, prints as written.

The position is replayed from the rows `gz wp dispatch`, `block`, `unblock`,
`change`, `resolve` and the lifecycle verbs already book. There is no position
event, so no second row can go missing, and no marker file is read or written: a
run is reported whatever its age and whatever `.claude/plans/` holds (GHI #1203,
#1208; the RO-14 specification's ruling 18). Packages come in the catalog's order,
then orders in theirs.

`--json` prints a list with one object per run: `work_package`, `kind`, `state`,
`blocked`, `event`, `move`, `at`, `subject`, which is null before the first
dispatch, and `order`, null on a package's run. The same object is the `position` of `gz wp show --json`.

The verb is a read and gates nothing, so it behaves the same at the operational
condition and at the hangar and drydock levels.

## Examples

Observed in a scratch project at `/private/tmp/gz-act5` holding `WP-02-loop`, a
delivery package commenced and held at the bound, and repair package `WP-01-stamp`,
whose order `ORD-01-import` is commenced and unblocked and whose order
`ORD-02-matcher` was accepted after a `terminate` exit:

```console
$ uv run gz wp runs
WP-02-loop (delivery), state: commenced
  last: unblocked hold
  at: 2026-11-07T12:48:17.684247+00:00
  subject: REQ-7@1
  blocked: no
order ORD-01-import of WP-01-stamp (repair), state: commenced
  last: unblocked cleared
  at: 2026-11-07T12:48:26.931538+00:00
  subject: REQ-8@1
  blocked: no
order ORD-02-matcher of WP-01-stamp (repair), state: accepted
  last: order_transitioned accepted
  at: 2026-11-07T12:49:59.038610+00:00
  subject: REQ-9@1
  blocked: no
```

A repair package itself is never in flight: it moves only `initiated` to `closed`,
and its orders carry the run (RP-12 ruling 44).

With no run in flight:

```console
$ uv run gz wp runs
No work package is in flight.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Reported, runs or none |
| 1 | The project is not initialized, or the catalog is missing or invalid |
| 2 | Usage error |

## See also

[`gz wp show`](wp-show.md), [`gz wp dispatch`](wp-dispatch.md),
[`gz wp block`](wp-block.md)
