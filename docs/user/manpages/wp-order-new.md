# gz wp order new

Write a new order's record with the next id in the one series.

## Usage

```bash
gz wp order new <WP-id> --slug <slug> --purpose <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package the order sits in. Required |
| `--slug` | Lowercase words joined by hyphens, the id's last part. Required |
| `--purpose` | What the order delivers or restores. Required |
| `--procedure` | Its procedure in prose, or `NA` (the default) |
| `--alias` | A short name such as `O2`, naming one order only (repeatable) |
| `--json` | Output the record as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

An order is the unit Gate 5 sits at, inside its work package: which REQs marry
which tasks, its own freeze, inspection and buy-back (requirements model § 12).
The verb writes its record to `data/catalog/orders.json`, the store's one writer,
checking the edit against the rules `gz validate --catalog` reads before the file
is touched, so a refusal writes nothing.

- The id is `ORD-<NN>-<slug>`, numbered past every order the store holds, one
  grammar for work and repair orders (RP-12 ruling 43).
- The order's kind is its package's, never a field of its own (ruling 43).
- The record is thin: id, package, aliases, purpose and procedure, and no REQ
  list. The order's freeze carries its REQ baseline, and its tasks bind by their
  own ledger events (ruling 46).
- It sits in a repair package. A delivery package keeps its five states until
  RP-14 moves construction onto the order, so an order on one is refused
  (ruling 44).

The lifecycle verbs (`freeze`, `commence`, `accept`, `close`) land with RP-12's
later O2 tasks (`docs/governance/harbor-ro12-contractor-kit.md`, ruling 47).

## Examples

Observed in a scratch project holding repair package `WP-01-stamp` and delivery
package `WP-02-resume`:

```console
$ uv run gz wp order new WP-01-stamp --slug import --purpose "Restore the stamp generator's public import." --alias O2
Wrote ORD-01-import in WP-01-stamp (repair).
$ uv run gz wp order new WP-02-resume --slug resume --purpose "Resume it."
The order record is refused: Order ORD-02-resume sits in delivery package
WP-02-resume; a delivery package keeps its five states until RP-14 moves
construction onto the order (RP-12 ruling 44)
(docs/governance/harbor-ro12-contractor-kit.md). The catalog's shape is ruled in
docs/governance/harbor-ro3-requirements-store.md (The store), and its families
in docs/governance/ieee/requirements-model.md (decision 8.3). Correct the file,
then re-run `uv run gz validate --catalog`.
$ uv run gz wp order new WP-09-ghost --slug x --purpose "P."
Work package 'WP-09-ghost' is not in data/catalog/work_packages.json. An order
sits in a package the catalog holds; create one with `gz wp new`.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Written |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The record is refused: its schema, a repeated alias, or a delivery package; nothing written |

## See also

[`gz wp order show`](wp-order-show.md), [`gz wp new`](wp-new.md),
[`gz validate --catalog`](validate.md)
