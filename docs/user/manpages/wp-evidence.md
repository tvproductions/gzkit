# gz wp evidence

Append objective quality evidence to a live work package.

## Usage

```bash
gz wp evidence <WP-id> --oqe <entry>... [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--oqe` | One evidence entry: a receipt id, a commit, a path. Repeatable; required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

A work package bundles its formal work package and its objective quality
evidence (OQE), the record of what was observed, measured or tested
(`docs/governance/harbor-ro5-work-packages.md`, amendment 1). The OQE is required
from `initiated`, so `evidence` appends to a package that is initiated and not
yet closed, writing `data/catalog/work_packages.json` through the store's one
writer. An entry is never edited or removed. An empty entry, an entry the
record already holds, or a package not initiated or already closed exits 3
and nothing is written.

The verb is the drydock RO-5 tranche 5 correction; the operator named it on
2026-10-28 ("gz wp evidence (Recommended)").

## Examples

Observed in a scratch project holding `WP-01-astral`, initiated, and
`WP-02-resume`, closed:

```console
$ uv run gz wp evidence WP-01-astral --oqe "commit abc1234" --oqe "arb-step-unittest-01"
Recorded 2 OQE entries on WP-01-astral.
$ uv run gz wp evidence WP-01-astral --oqe "commit abc1234"
Each evidence entry is non-empty and recorded once; nothing was written.
$ uv run gz wp evidence WP-02-resume --oqe "late"
Work package WP-02-resume is closed; it takes no evidence.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The entries were appended |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The package is not live, or an entry is empty or repeated; nothing was written |

## See also

[`gz wp initiate`](wp-initiate.md), [`gz wp show`](wp-show.md),
[`gz wp close`](wp-close.md)
