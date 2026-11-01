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
`accepted`, awaiting Gate 5, is still reported. For each one the verb prints the
last row the run booked (`last`), when it was booked (`at`), the subject last
dispatched against (`subject`) and whether the package awaits the operator
(`blocked`). No run in flight says so and exits 0. Text the verbs recorded, a block
reason among it, prints as written.

The position is replayed from the rows `gz wp dispatch`, `block`, `unblock`,
`change`, `resolve` and the lifecycle verbs already book. There is no position
event, so no second row can go missing, and no marker file is read or written: a
run is reported whatever its age and whatever `.claude/plans/` holds (GHI #1203,
#1208; the RO-14 specification's ruling 18). Packages come in the catalog's order.

`--json` prints a list with one object per run: `work_package`, `kind`, `state`,
`blocked`, `event`, `move`, `at` and `subject`, which is null before the first
dispatch. The same object is the `position` of `gz wp show --json`.

The verb is a read and gates nothing, so it behaves the same at the operational
condition and at the hangar and drydock levels.

## Examples

Observed in a scratch project with two repair packages commenced, one dispatched
against and one blocked:

```console
$ uv run gz wp runs
WP-01-older (repair), state: commenced
  last: dispatched Implementer #1203
  at: 2026-11-01T05:43:08.256952+00:00
  subject: #1203
  blocked: no
WP-02-later (repair), state: commenced
  last: blocked the REQ is ambiguous
  at: 2026-11-01T05:43:08.749669+00:00
  subject: #1208
  blocked: yes
```

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
