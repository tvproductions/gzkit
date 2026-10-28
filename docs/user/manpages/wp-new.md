# gz wp new

Write a new work-package record to `data/catalog/work_packages.json`, with the next id in the one series.

## Usage

```bash
gz wp new --kind {delivery,repair} --slug <slug> [--outcome <code>] [--issue <n>]... [--lane {lite,heavy}] [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--kind` | `delivery` (names an outcome) or `repair` (names GitHub issues). Required |
| `--slug` | Lowercase words joined by hyphens; the id becomes `WP-<NN>-<slug>`. Required |
| `--outcome` | The outcome code a delivery package delivers |
| `--issue` | A GitHub issue a repair package carries. Repeatable |
| `--lane` | `lite` or `heavy`; stored on a repair package only, since a delivery package derives its lane from its outcome |
| `--alias` | A drydock name such as `RO-9`. Repeatable |
| `--initial-conditions`, `--procedure`, `--test-and-inspection`, `--system-restoration` | The formal work package's four sections. Each defaults to `NA` |
| `--alteration` | A planned remodel as `ID:reconnected\|replaced\|retired:description`. Repeatable |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The store is edited only through `gz` verbs (RO-5 ruling 3, `docs/governance/harbor-ro5-work-packages.md`). `new`
numbers the package past every one the store holds, so an id is never reused
(ruling 6). The record is checked against the rules `gz validate --catalog` reads
before it is written: a delivery package names an outcome the catalog holds and
no issue or lane; a repair package names at least one issue, stores its lane and
names no outcome; an issue belongs to one package. A record the rules refuse
exits 3 and nothing is written. No lifecycle state is stored: `gz wp initiate`
books the first move in the ledger.

The verbs are drydock RO-5 tranche 2; the operator named them on 2026-10-28.

## Examples

Observed in a scratch project seeded with one family, outcome `H1` and `REQ-1`
at revision 2:

```console
$ uv run gz wp new --kind repair --slug astral --issue 1183 --lane lite --alias RO-9
Wrote WP-01-astral (repair).
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The record was written |
| 2 | Usage error |
| 3 | The record breaks a store rule; nothing was written |

## See also

[`gz wp new`](wp-new.md), [`gz wp show`](wp-show.md),
[`gz validate --catalog`](validate.md)
