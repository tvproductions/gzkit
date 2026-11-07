# gz wp order accept

Accept a commenced order once its own acceptance reads ready.

## Usage

```bash
gz wp order accept <ORD-id> --evidence <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `ORD-id` | The order, `ORD-<NN>-<slug>`. Required |
| `--evidence` | The final inspection that justifies the move. Required |
| `--json` | Output the booked event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Books the order's `order_transitioned` from `commenced` to `accepted`
(`docs/governance/harbor-ro12-contractor-kit.md`, RP-12 ruling 60), after two
gates, in order:

1. The order's own acceptance reads ready. [`gz wp acceptance <ORD-id>`](wp-acceptance.md)
   runs the acceptance runtime on the order: its obligations are its frozen REQs at
   their frozen revisions, less any a `departure` exit on the order moved out, and
   its proofs and reviews are kept under the order's id, so each order carries its
   own evidence into its own Gate 5. The order's three adversarial rounds with a
   mapped finding hold here as they hold a package (GHI #1028); past them the
   refusal names `gz wp block <WP-id> --order <ORD-id>`.
2. Every file the repair package changed lies in its footprint, as the order's
   freeze sealed it (ruling 56).

An order stopped by a `reopen` or `terminate` exit is excused both gates, as a
stopped package is: it claims no delivery, and Gate 5 at the order is how it
closes. The lifecycle moves one step at a time, an order blocked on the operator
does not move (ruling 59), and its repair package must be initiated and not
closed (rulings 2 and 44).

An accepted order holds the production-write fence until it closes (ruling 58).
Its close is Gate 5 at the order, which lands with RP-12 O2 task 4.

The inspection points of rulings 14 and 15 are not read by the runtime yet, so an
order reads ready without them until a later order adds them.

A refusal names what failed, why, and the call to re-run, and books nothing.

## Examples

Observed in a scratch project holding `WP-01-stamp` initiated. `ORD-01-import`
is commenced with no acceptance; `ORD-02-matcher` was stopped by a `terminate`
exit:

```console
$ uv run gz wp order accept ORD-01-import --evidence final-inspection
Acceptance blocked: No durable acceptance contract/proof history. Required proof
and independent closure must remain bound to canon (GHI #985; T1/T2/T3). Run `gz
wp acceptance ORD-01-import status --stage stage4` and repair the named
obligation through the existing pipeline.
$ uv run gz wp order accept ORD-02-matcher --evidence "terminated; no delivery"
ORD-02-matcher: commenced -> accepted
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Accepted |
| 1 | The order, or its work package, is not in the store |
| 2 | Usage error |
| 3 | The move is refused: acceptance does not read ready, the round limit is used, a file lies outside the footprint, or the lifecycle refuses it; nothing booked |

## See also

[`gz wp acceptance`](wp-acceptance.md), [`gz wp order commence`](wp-order-commence.md),
[`gz wp order show`](wp-order-show.md), [`gz wp accept`](wp-accept.md)
