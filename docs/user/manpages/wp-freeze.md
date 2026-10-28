# gz wp freeze

Freeze a work package's REQ baseline after the independent reviewer's nine-criteria check.

## Usage

```bash
gz wp freeze <WP-id> --risk-note <text> --review-receipt <id> --evidence <text> [--baseline REQ-<n>@<rev>]... [--approve-alteration <id>]... [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--baseline` | A REQ frozen at its revision, `REQ-<n>@<revision>`. Repeatable; a delivery package needs at least one |
| `--risk-note` | The short risk note. Required |
| `--review-receipt` | The reviewer's nine-criteria receipt. Required |
| `--approve-alteration` | An alteration the operator approves. Repeatable; every planned alteration must be approved |
| `--evidence` | What justifies the freeze. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Moves an initiated package to `frozen`. Each baseline entry must be a REQ the
catalog holds at that revision and, for a delivery package, a member of its
outcome. The operator approves each planned alteration at freeze (ruling of
2026-10-28), so the approved set must equal the package's alterations.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp freeze WP-02-resume --baseline REQ-1@2 --risk-note "touches the chain" \
    --review-receipt review-01 --approve-alteration ALT-1 --evidence review-01
WP-02-resume: initiated -> frozen
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
