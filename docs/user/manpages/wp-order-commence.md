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
| `--no-isolation` | With no tag issued on the order, why the repair isolates nothing; recorded on the event. Refused with a tag issued |
| `--json` | Output the booked event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Books the order's `order_transitioned` from `frozen` to `commenced`
(`docs/governance/harbor-ro12-contractor-kit.md`, RP-12 O2 task 3). The lifecycle
moves one step at a time, so an order that is not frozen is refused, and its
repair package must be initiated and not closed (rulings 2 and 44).

Commencement waits on the tag-out log. The order commences only once every tag
issued on it (`gz wp tag issue`) is hung by its Repair dispatch (`gz wp tag
hang`), so no work runs on a surface not yet isolated; the refusal names each tag
not hung (ruling 108). An order with no tag issued commences only on the
coordinator's stated reason, `--no-isolation "<why>"`, recorded on the
`commenced` event; with a tag issued the option is refused (ruling 117). An order
a `terminate` or `reopen` exit stopped does no work, so it commences without its
tags or a statement (ruling 143). Commencing lifts the frozen order's fence on
its footprint (ruling 116). Commencement is the coordinator's act from the
main session: a call stamped as a subagent's is refused before anything is read
(ruling 144).

Commencing crosses the airlock inward on the repair package's slice: it books one
`airlock_in` for the package and prints what it read, as
[`gz wp commence`](wp-commence.md) does for a package (ruling 65). The airlock
reports and refuses nothing here.

A refusal names what failed, why, and the call to re-run, and writes nothing.

## Examples

Observed 2026-11-18 in two scratch projects set up as `tests/commands/test_wp_order.py`
and `tests/commands/test_wp_tag.py` set them up. In the first, `ORD-01-import` is
opened and then frozen with no tag issued:

```console
$ uv run gz wp order commence ORD-01-import --evidence tags-hung
Order ORD-01-import cannot move from opened to 'commenced'; the lifecycle allows
frozen from here. Nothing was written; correct the call and re-run `uv run gz wp
order commence <ORD-id> --evidence <text> [--no-isolation <why>]`.
$ uv run gz wp order commence ORD-01-import --evidence tags-hung
Order ORD-01-import has no tag issued. An order commences once every surface it
isolates has its tag hung, or on the coordinator's stated reason that it
isolates nothing (RP-12 rulings 108 and 117). Issue its tags with `uv run gz wp
tag issue ORD-01-import`, or commence it with `--no-isolation "<why>"`. Nothing
was written; correct the call and re-run `uv run gz wp order commence <ORD-id>
--evidence <text> [--no-isolation <why>]`.
$ uv run gz wp order commence ORD-01-import --evidence no-isolation --no-isolation "The repair edits a doc; no control is disconnected."
ORD-01-import: frozen -> commenced
  airlock in: proceed
$ uv run gz wp order commence ORD-09-ghost --evidence tags-hung
Order 'ORD-09-ghost' is not in data/catalog/orders.json. Write one with `uv run
gz wp order new <WP-id> --slug <slug> --purpose <text> --operator-text <words>`.
```

In the second, `TAG-01-stamp-hook` is issued on the frozen order and a Repair
dispatch booked on it. Before the hang, and after it:

```console
$ uv run gz wp order commence ORD-01-import --evidence tags-hung
Order ORD-01-import has tag(s) issued and not hung: TAG-01-stamp-hook. It
commences only once every tag issued on it is hung, so no work runs on a surface
not yet isolated (RP-12 ruling 108). Book a Repair dispatch on the frozen order
(`uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Repair --model
<tier>`) and have its subagent run `uv run gz wp tag hang <TAG-id> --dispatch
D-<id>` for each, then commence. Nothing was written; correct the call and
re-run `uv run gz wp order commence <ORD-id> --evidence <text> [--no-isolation
<why>]`.
$ uv run gz wp order commence ORD-01-import --evidence tags-hung
ORD-01-import: frozen -> commenced
  airlock in: proceed
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Commenced |
| 1 | The order, or its work package, is not in the store |
| 2 | Usage error |
| 3 | The move is refused: a subagent's call, a booked order has lost its record, the lifecycle, the order's block, the package's state, a tag issued and not hung, no tag and no `--no-isolation`, or `--no-isolation` with a tag issued; nothing written |

## See also

[`gz wp order freeze`](wp-order-freeze.md), [`gz wp tag hang`](wp-tag-hang.md),
[`gz wp order show`](wp-order-show.md)
