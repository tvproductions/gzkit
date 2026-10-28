# gz wp attach

Attach GitHub issues to a repair package.

## Usage

```bash
gz wp attach <WP-id> --issue <n>... [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--issue` | The issue to attach. Repeatable; required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

A repair order carries one or more GitHub issues, and each issue belongs to
exactly one repair package (RO-5 ruling 2). An issue another package already
holds, or an issue on a delivery package, exits 3 and the record is unchanged.
The `repair` label and the comment naming the package on the issue are tranche
3's.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp attach WP-01-astral --issue 1184
Attached #1184 to WP-01-astral.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The issues were attached |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | An issue already belongs to another package, or the package is not a repair package |

## See also

[`gz wp new`](wp-new.md), [`gz wp show`](wp-show.md),
[`gz validate --catalog`](validate.md)
