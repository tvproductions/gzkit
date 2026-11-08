# gz wp order commence

Record that work has commenced on a frozen order.

## Usage

```bash
gz wp order commence <ORD-id> --evidence <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `ORD-id` | The order, `ORD-<NN>-<slug>`. Required |
| `--evidence` | What justifies the move. Required |
| `--json` | Output the booked event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Books the order's `order_transitioned` from `frozen` to `commenced`
(`docs/governance/harbor-ro12-contractor-kit.md`, RP-12 O2 task 3). The lifecycle
moves one step at a time, so an order that is not frozen is refused, and its
repair package must be initiated and not closed (rulings 2 and 44).

Commencing crosses the airlock inward on the repair package's slice: it books one
`airlock_in` for the package and prints what it read, as
[`gz wp commence`](wp-commence.md) does for a package (ruling 65). The airlock
reports and refuses nothing here.

A refusal names what failed, why, and the call to re-run, and writes nothing.

## Examples

Observed in a scratch project holding the order `ORD-01-import`, first opened,
then frozen:

```console
$ uv run gz wp order commence ORD-01-import --evidence tags-hung
Order ORD-01-import cannot move from opened to 'commenced'; the lifecycle allows
frozen from here. Nothing was written; correct the call and re-run `uv run gz wp
order commence <ORD-id> --evidence <text>`.
$ uv run gz wp order commence ORD-01-import --evidence tags-hung
ORD-01-import: frozen -> commenced
  airlock in: proceed
$ uv run gz wp order commence ORD-09-ghost --evidence tags-hung
Order 'ORD-09-ghost' is not in data/catalog/orders.json. Write one with `uv run
gz wp order new <WP-id> --slug <slug> --purpose <text> --operator-text <words>`.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Commenced |
| 1 | The order, or its work package, is not in the store |
| 2 | Usage error |
| 3 | The move is refused: a booked order has lost its record, the lifecycle, the order's block, or the package's state; nothing written |

## See also

[`gz wp order freeze`](wp-order-freeze.md), [`gz wp order show`](wp-order-show.md)
