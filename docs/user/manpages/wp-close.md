# gz wp close

Close an accepted work package through Gate 5.

## Usage

```bash
gz wp close <WP-id> --decision <decision> --attestor <id> --residual-risk <text> --evidence <text> [--account <id>]... [--open-departure <id>]... [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--decision` | `proceed`, `redirect`, `pause` or `terminate`. Required |
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

Gate 5 stays per work package (R2). `close` moves an accepted delivery package,
or an initiated repair package, to `closed`, recording the decision, the attestor
and the residual risk. A repair package moves only `initiated` to `closed`, its
orders carrying the run (RP-12 ruling 44), and its close carries the same payload
(ruling 62). Reading every order's Gate 5 lands with Gate 5 at the order (O2
task 4), and the operator's words for return to service with O5 (ruling 32), so
until then the close records a Gate 5 decision of its own. Every
alteration is accounted as its configuration change, and each departure still
open is named. The event also records the package's lane, which the writer
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

A repair package, in a scratch project at `/private/tmp/gz-act5` holding
`WP-01-stamp` initiated with the alteration `ALT-1`:

```console
$ uv run gz wp close WP-01-stamp --decision proceed --attestor g0 --residual-risk none --evidence closeout
Every alteration of WP-01-stamp is accounted at close as a configuration change.
$ uv run gz wp close WP-01-stamp --decision proceed --attestor g0 --residual-risk none --account ALT-1 --evidence closeout
WP-01-stamp: initiated -> closed
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The move was booked |
| 1 | The work package is not in `data/catalog/work_packages.json` |
| 2 | Usage error |
| 3 | The lifecycle or the move's own rules refuse it; nothing was written |

## See also

[`gz wp new`](wp-new.md), [`gz wp show`](wp-show.md),
[`gz validate --catalog`](validate.md)
