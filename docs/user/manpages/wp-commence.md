# gz wp commence

Record that work has commenced on a frozen work package.

## Usage

```bash
gz wp commence <WP-id> --evidence <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--evidence` | What justifies the move. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Moves a frozen package to `commenced` (C1 of the contractor-kit record: once
every surface the package works has its tag hung). The tag-out log is RO-12's;
until it lands, `--evidence` names what was checked. A move that skips a step
exits 3.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp commence WP-02-resume --evidence tags-hung
WP-02-resume: frozen -> commenced

$ uv run gz wp commence WP-01-astral --evidence early
Work package WP-01-astral cannot move from nothing to 'commenced'; the lifecycle
allows initiated from here.
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
