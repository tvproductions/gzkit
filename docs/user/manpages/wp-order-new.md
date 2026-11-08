# gz wp order new

Write a new order's record with the next id in the one series, and book its opening.

## Usage

```bash
gz wp order new <WP-id> --slug <slug> --purpose <text> --operator-text <words> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package the order sits in. Required |
| `--slug` | Lowercase words joined by hyphens, the id's last part. Required |
| `--purpose` | What the order delivers or restores. Required |
| `--procedure` | Its procedure in prose, or `NA` (the default) |
| `--operator-text` | The operator's words opening the order, booked on the ledger. Required |
| `--evidence` | What justifies the opening (default `operator opening`) |
| `--alias` | A short name such as `O2`, unique within the package (repeatable) |
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

- The id is `ORD-<NN>-<slug>`, numbered past the highest number the store holds,
  one grammar for work and repair orders (RP-12 ruling 43). The series compares
  numbers, so `ORD-001` reuses `ORD-01`'s.
- The order's kind is its package's, never a field of its own (ruling 43).
- An alias is one word, a specification's short name such as `O2`, unique within
  the order's package and never shaped as an order's or a package's id (rulings
  43, 49). Orders of two packages may share one.
- The record is thin: id, package, aliases, purpose and procedure, and no REQ
  list. The order's freeze carries its REQ baseline, and its tasks bind by their
  own ledger events (ruling 46). The store only grows.
- The order is born on the ledger: the verb books `order_transitioned` to
  `opened`, carrying `--operator-text` verbatim, before it writes the record, as
  a package's `initiated` carries the operator's words (ruling 52). The ledger
  then holds the order's lifecycle (ruling 44), and `gz validate --catalog`
  refuses a store missing an order the ledger names. The next id numbers past
  every order the ledger names as well as the store's, so an id is never reused.
- It sits in a repair package that is initiated and not closed: the package stays
  open while its orders are found, and its close reads every order's Gate 5
  (rulings 2, 44). A delivery package keeps its five states until RP-14 moves
  construction onto the order, so an order on one is refused (ruling 44).

A refusal names the flag at fault, why, and the call to re-run, and writes
nothing, in the store or the ledger. A store that breaks its rules before the
call, a lost order record among them, refuses every write, this verb's and
every order move's (RP-12 ruling 70), and points to
`uv run gz validate --catalog`. The order then moves through
[`gz wp order freeze`](wp-order-freeze.md) and
[`gz wp order commence`](wp-order-commence.md); `accept` and `close` land with
RP-12's later O2 work (`docs/governance/harbor-ro12-contractor-kit.md`, ruling
47).

## Examples

Observed in a scratch project holding repair package `WP-01-stamp` (initiated),
delivery package `WP-02-resume` and repair package `WP-03-idle` (not initiated):

```console
$ uv run gz wp order new WP-01-stamp --slug import --purpose "Restore the stamp generator's public import." --operator-text "open the import order" --alias O2
Wrote ORD-01-import in WP-01-stamp (repair).
$ uv run gz wp order new WP-01-stamp --slug matcher --purpose "Fix the matcher." --operator-text "open it" --alias O2
Aliases O2 name more than one order in WP-01-stamp; an alias is unique within
its package (RP-12 ruling 49). The rulings are in
docs/governance/harbor-ro12-contractor-kit.md. Nothing was written; correct the
call and re-run `uv run gz wp order new <WP-id> --slug <slug> --purpose <text>
--operator-text <words>`.
$ uv run gz wp order new WP-01-stamp --slug matcher --purpose "Fix the matcher." --operator-text " "
--operator-text is empty. An order is opened on the operator's words and booked
on the ledger (RP-12 ruling 52). Nothing was written; correct the call and
re-run `uv run gz wp order new <WP-id> --slug <slug> --purpose <text>
--operator-text <words>`.
$ uv run gz wp order new WP-02-resume --slug resume --purpose "Resume it." --operator-text "open it"
Order ORD-02-resume sits in delivery package WP-02-resume; a delivery package
keeps its five states until RP-14 moves construction onto the order (RP-12
ruling 44). The rulings are in docs/governance/harbor-ro12-contractor-kit.md.
Nothing was written; correct the call and re-run `uv run gz wp order new <WP-id>
--slug <slug> --purpose <text> --operator-text <words>`.
$ uv run gz wp order new WP-03-idle --slug idle --purpose "Idle." --operator-text "open it"
Work package WP-03-idle is not initiated. An order is written into a repair
package that is initiated and not closed, since its close reads every order's
Gate 5 (RP-12 rulings 2 and 44); `uv run gz wp initiate WP-03-idle
--operator-text <words>` initiates one. Nothing was written; correct the call
and re-run `uv run gz wp order new <WP-id> --slug <slug> --purpose <text>
--operator-text <words>`.
$ uv run gz wp order new WP-01-stamp --slug Import --purpose "P." --operator-text "open it"
--slug 'Import' is not lowercase words joined by hyphens. It is the last part of
the order's id, ORD-<NN>-<slug> (RP-12 ruling 43). Nothing was written; correct
the call and re-run `uv run gz wp order new <WP-id> --slug <slug> --purpose
<text> --operator-text <words>`.
$ uv run gz wp order new WP-09-ghost --slug x --purpose "P." --operator-text "open it"
Work package 'WP-09-ghost' is not in data/catalog/work_packages.json. An order
sits in a package the catalog holds; create one with `gz wp new`.
```

The one opening the first call booked, read from the scratch ledger:

```json
{"schema":"gzkit.ledger.v1","event":"order_transitioned","id":"ORD-01-import","ts":"2026-11-07T09:01:31.875957+00:00","baseline":[],"evidence":"operator opening","work_package":"WP-01-stamp","to_state":"opened","operator_text":"open the import order","order":"ORD-01-import"}
```

With `ORD-01-import`'s record then removed from the store by hand:

```console
$ uv run gz wp order new WP-01-stamp --slug next --purpose "Next." --operator-text "open it"
Orders ORD-01-import have ledger events but no record; an order is born on the
ledger and its id is never reused (RP-12 rulings 43, 52).
data/catalog/orders.json breaks its rules already, before this call, so nothing
was written. Run `uv run gz validate --catalog`, which names each finding, and
repair the store before writing again.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Written |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The record or its opening is refused: the slug, an empty field or `--operator-text`, an alias, the package's kind or its state, or a store missing a booked order; nothing written |

## See also

[`gz wp order show`](wp-order-show.md), [`gz wp new`](wp-new.md),
[`gz validate --catalog`](validate.md)
