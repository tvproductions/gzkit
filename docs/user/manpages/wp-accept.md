# gz wp accept

Record final inspection of a commenced work package.

## Usage

```bash
gz wp accept <WP-id> --evidence <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--evidence` | What justifies the move, such as the final inspection. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Moves a commenced package to `accepted` (C10 of the contractor-kit record:
final inspection with no tag still hung). RO-12's refusals read this state.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp accept WP-02-resume --evidence final-inspection
WP-02-resume: commenced -> accepted
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
