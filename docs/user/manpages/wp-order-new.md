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
- It sits in a repair package that is initiated and not closed: the package stays
  open while its orders are found, and its close reads every order's Gate 5
  (rulings 2, 44). A delivery package keeps its five states until RP-14 moves
  construction onto the order, so an order on one is refused (ruling 44).

A refusal names the flag at fault, why, and the call to re-run, and writes
nothing. A store that breaks its rules before the call refuses every write and
points to `uv run gz validate --catalog`. The lifecycle verbs (`freeze`, `commence`, `accept`, `close`) land with
RP-12's later O2 tasks (`docs/governance/harbor-ro12-contractor-kit.md`, ruling
47).

## Examples

Observed in a scratch project holding repair package `WP-01-stamp` (initiated),
delivery package `WP-02-resume` and repair package `WP-03-idle` (not initiated):

```console
$ uv run gz wp order new WP-01-stamp --slug import --purpose "Restore the stamp generator's public import." --alias O2
Wrote ORD-01-import in WP-01-stamp (repair).
$ uv run gz wp order new WP-01-stamp --slug matcher --purpose "Fix the matcher." --alias O2
Aliases O2 name more than one order in WP-01-stamp; an alias is unique within
its package (RP-12 ruling 49). The rulings are in
docs/governance/harbor-ro12-contractor-kit.md. Nothing was written; correct the
call and re-run `uv run gz wp order new <WP-id> --slug <slug> --purpose <text>`.
$ uv run gz wp order new WP-02-resume --slug resume --purpose "Resume it."
Order ORD-02-resume sits in delivery package WP-02-resume; a delivery package
keeps its five states until RP-14 moves construction onto the order (RP-12
ruling 44). The rulings are in docs/governance/harbor-ro12-contractor-kit.md.
Nothing was written; correct the call and re-run `uv run gz wp order new <WP-id>
--slug <slug> --purpose <text>`.
$ uv run gz wp order new WP-03-idle --slug idle --purpose "Idle."
Work package WP-03-idle is not initiated. An order is written into a repair
package that is initiated and not closed, since its close reads every order's
Gate 5 (RP-12 rulings 2 and 44); `uv run gz wp initiate WP-03-idle
--operator-text <words>` initiates one. Nothing was written; correct the call
and re-run `uv run gz wp order new <WP-id> --slug <slug> --purpose <text>`.
$ uv run gz wp order new WP-01-stamp --slug Import --purpose "P."
--slug 'Import' is not lowercase words joined by hyphens. It is the last part of
the order's id, ORD-<NN>-<slug> (RP-12 ruling 43). Nothing was written; correct
the call and re-run `uv run gz wp order new <WP-id> --slug <slug> --purpose
<text>`.
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
| 3 | The record is refused: the slug, an empty field, an alias, the package's kind or its state; nothing written |

## See also

[`gz wp order show`](wp-order-show.md), [`gz wp new`](wp-new.md),
[`gz validate --catalog`](validate.md)
