# gz wp order show

Show an order's record, the kind of the package it sits in, and its state and baseline.

## Usage

```bash
gz wp order show <ORD-id> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `ORD-id` | The order's id, `ORD-<NN>-<slug>`. Required |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Reads the order's record from `data/catalog/orders.json` and the kind of its
package from `data/catalog/work_packages.json`: an order's kind is its
package's, never a field of its own (RP-12 ruling 43).

The order's lifecycle lives only in the ledger (ruling 44), as
`order_transitioned`, so its state and its frozen baseline are read from there:
`opened` from `gz wp order new` (ruling 52), then `frozen` and `commenced` from
[`gz wp order freeze`](wp-order-freeze.md) and
[`gz wp order commence`](wp-order-commence.md). Before a freeze the baseline is
empty. `--json` prints the record, the kind, the state and the baseline.

## Examples

Observed in a scratch project holding repair package `WP-01-stamp`, after
`gz wp order new` wrote `ORD-01-import` and it was frozen on `REQ-1` and
commenced:

```console
$ uv run gz wp order show ORD-01-import
ORD-01-import in WP-01-stamp (repair)
  state: commenced
  baseline: REQ-1@1
  aliases: O2
  purpose: Restore the stamp generator's public import.
  procedure: NA
$ uv run gz wp order show ORD-01-import --json
{
  "baseline": {
    "REQ-1": 1
  },
  "kind": "repair",
  "record": {
    "aliases": [
      "O2"
    ],
    "id": "ORD-01-import",
    "procedure": "NA",
    "purpose": "Restore the stamp generator's public import.",
    "work_package": "WP-01-stamp"
  },
  "state": "commenced"
}
$ uv run gz wp order show ORD-09-ghost
Order 'ORD-09-ghost' is not in data/catalog/orders.json. Write one with `uv run
gz wp order new <WP-id> --slug <slug> --purpose <text> --operator-text <words>`.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Shown |
| 1 | The order, or its package, is not in the store |
| 2 | Usage error |

## See also

[`gz wp order new`](wp-order-new.md), [`gz wp show`](wp-show.md)
