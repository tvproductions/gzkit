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

Gate 5 stays per work package (R2). `close` moves an accepted package to
`closed`, recording the decision, the attestor and the residual risk. Every
alteration is accounted as its configuration change, and each departure still
open is named. A delivery close also moves its outcome; that coupling arrives
with the outcome verbs.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp close WP-02-resume --decision proceed --attestor g0 --residual-risk none \
    --account ALT-1 --evidence closeout
WP-02-resume: accepted -> closed
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
