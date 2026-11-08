# gz wp close

Close an accepted delivery package through Gate 5, or a repair package once its orders have closed.

## Usage

```bash
gz wp close <WP-id> [--decision <decision>] --attestor <id> --residual-risk <text> --evidence <text> [--account <id>]... [--open-departure <id>]... [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--decision` | `proceed`, `redirect`, `pause` or `terminate`. Required for a delivery package; refused for a repair package, whose Gate 5 is its orders' |
| `--attestor` | The Gate 5 attestor. Required and never defaulted: closing is the operator's own act |
| `--residual-risk` | The residual risk. Required |
| `--account` | An alteration accounted as its configuration change. Repeatable; every alteration must be accounted |
| `--open-departure` | A departure from specification still open at close. Repeatable |
| `--evidence` | What justifies the close. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

`close` moves an accepted delivery package to `closed` through Gate 5 (R2),
recording the decision, the attestor and the residual risk. A repair package moves
only `initiated` to `closed`, its orders carrying the run (RP-12 ruling 44). Gate 5
sits at each of its orders, [`gz wp order close`](wp-order-close.md), so the
package's close is refused while any order is not closed, carries no `--decision`
of its own, and records each order's decision as the ledger holds it in
`order_decisions` (ruling 76) and each repair REQ a `proceed` holds in `held_reqs`
(ruling 78); it keeps the attestor, the residual risk, the
alterations and the departures (ruling 62). Return to service, on the operator's
words, lands with O5 (ruling 32). Gate 5 is the operator's act, so a call the
dispatch stamp marks as a subagent's is refused (ruling 77). Every alteration is
accounted as its configuration change, and each departure still open is named. The event also records the package's lane, which the writer
derives and the caller never supplies (RO-5 tranche 4): the stored lane of a
repair package, or `heavy` for a delivery package whose outcome is user-facing.
Lane-specific gate enforcement at close is RO-12's. A delivery close also moves
its outcome; that coupling arrives with the outcome verbs.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp close WP-02-resume --decision proceed --attestor g0 --residual-risk none \
    --account ALT-1 --evidence closeout
WP-02-resume: accepted -> closed
```

A repair package, in a scratch project holding `WP-01-stamp` initiated with no
alterations. `ORD-02-spare` is closed as `terminate`; `ORD-01-import` is still
accepted:

```console
$ uv run gz wp close WP-01-stamp --attestor g0 --residual-risk none --evidence closeout
Repair package WP-01-stamp closes once every order is closed; ORD-01-import
still stands open. Close each through Gate 5 with `uv run gz wp order close
<ORD-id>` first (RP-12 ruling 76).
```

Once `ORD-01-import` is closed through Gate 5 too:

```console
$ uv run gz wp close WP-01-stamp --decision proceed --attestor g0 --residual-risk none --evidence closeout
Repair package WP-01-stamp books no Gate 5 decision of its own: Gate 5 sits at
each order, `uv run gz wp order close` (RP-12 rulings 30 and 76). Close it
without --decision.
$ uv run gz wp close WP-01-stamp --attestor g0 --residual-risk none --evidence closeout
WP-01-stamp: initiated -> closed
```

The close it booked, read from the scratch ledger:

```json
{"schema":"gzkit.ledger.v1","event":"work_package_transitioned","id":"WP-01-stamp","ts":"2026-11-08T08:24:20.888579+00:00","to_state":"closed","work_package":"WP-01-stamp","attestor":"g0","configuration_changes":[],"baseline":[],"modules":[],"open_departures":[],"lane":"lite","from_state":"initiated","held_reqs":[],"evidence":"closeout","approved_alterations":[],"residual_risk":"none","order_decisions":{"ORD-01-import":"terminate","ORD-02-spare":"terminate"}}
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The move was booked |
| 1 | The work package is not in `data/catalog/work_packages.json` |
| 2 | Usage error |
| 3 | A subagent's call, or the lifecycle or the move's own rules refuse it, a repair package's open order or decision among them; nothing was written |

## See also

[`gz wp new`](wp-new.md), [`gz wp show`](wp-show.md), [`gz wp order close`](wp-order-close.md),
[`gz validate --catalog`](validate.md)
