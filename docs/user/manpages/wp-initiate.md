# gz wp initiate

Initiate a work package on the operator's words.

## Usage

```bash
gz wp initiate <WP-id> --operator-text "<words>" [--evidence <text>] [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--operator-text` | The operator's words initiating the package. Required |
| `--evidence` | What justifies the move. Defaults to `operator initiation` |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The operator initiates a work package, not each slice (requirements model §
11). `initiate` books the first `work_package_transitioned` event, from no state
to `initiated`, carrying the operator's words. A package already initiated
refuses with exit 3.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp initiate WP-02-resume --operator-text "start the resume package"
WP-02-resume: nothing -> initiated
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
