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
A repair package never freezes, since its orders carry the run (RP-12 ruling 44),
so it takes issues while it is initiated; a closed package takes no new issue, and
another issue is a new package. An issue is never a run's subject or obligation
(ruling 64): an order's REQ cites it as its problem report. Each issue
attached is labeled `repair` and commented with the package id,
aliases in parentheses (ruling 7); the label is created when the repository
lacks it. The edit is checked first, then GitHub is tagged, then the record is
written, so a failed `gh` call exits 2 and writes nothing (RO-5 tranche 3,
operator rulings of 2026-10-28).

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2, with a stub `gh` on `PATH` so no real issue was touched:

```console
$ uv run gz wp attach WP-01-astral --issue 1184
Attached #1184 to WP-01-astral.
```

With no `gh` on `PATH`, nothing is written:

```console
$ uv run gz wp new --kind repair --slug astral --issue 1183 --lane lite --alias RO-9
gh is not on PATH; install the GitHub CLI and run `gh auth login`. Nothing was
written; re-run once gh works.
```

Once the package is closed, in a scratch project at `/private/tmp/gz-act5` with
the same stub `gh`:

```console
$ uv run gz wp attach WP-01-stamp --issue 1302
Work package WP-01-stamp is closed; it carries no further issue. Another issue
is a new package.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The issues were attached |
| 1 | The work package is not in the store |
| 2 | Usage error, or a `gh` call failed; nothing was written |
| 3 | An issue already belongs to another package, the package is not a repair package, or it is closed |

## See also

[`gz wp new`](wp-new.md), [`gz wp resolve`](wp-resolve.md), [`gz wp show`](wp-show.md),
[`gz validate --catalog`](validate.md)
