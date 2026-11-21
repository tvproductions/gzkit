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
(`docs/governance/harbor-ro12-contractor-kit.md`, RP-12 ruling 60), after three
gates. Each is read on every order, and a refusal names every blocker it found,
a file outside the footprint and a hung tag beside the others (ruling 88):

1. The order's own acceptance reads ready. [`gz wp acceptance <ORD-id>`](wp-acceptance.md)
   runs the acceptance runtime on the order: its obligations are its frozen REQs at
   their frozen revisions, less any a `departure` exit on the order moved out, and
   its proofs and reviews are kept under the order's id, so each order carries its
   own evidence into its own Gate 5. The order's three adversarial rounds with a
   mapped finding hold here as they hold a package (GHI #1028); past them the
   refusal names `gz wp block <WP-id> --order <ORD-id>`.
2. Every file the repair package changed lies in its footprint, as the order's
   freeze sealed it (ruling 56). The order and requirement stores, which `gz wp
   order new` and `gz wp req new` write, never count, as the work-package store
   and the ledger do not (ruling 66).
3. Every tag the order hung is cleared or carried (refusal 6, rulings 129, 142
   and 171): a tag hung and not cleared would leave its surface isolated past
   acceptance unrecorded, so the refusal names each such tag and both recoveries.
   The clear is [`gz wp tag authorize`](wp-tag-authorize.md), a `Restoration`
   dispatch and its subagent's [`gz wp tag clear`](wp-tag-clear.md). The carry is
   one open line on the order, graded `due-by-event`, recorded by the
   coordinator's unstamped [`gz wp discrepancy record`](wp-discrepancy-record.md)
   and citing the tag with `--tag`; a performer's line, a blocking line and a
   cleared line carry nothing. Two such lines on one tag refuse it, each named,
   until all but one is cleared (ruling 186). The accepted move books each carry
   as `carried`, the tag with its line, and the verb prints it (ruling 184); the
   order's Gate 5 then takes a pause alone while a carried tag hangs (ruling 171,
   [`gz wp order close`](wp-order-close.md)), and the line is cleared only by
   that tag's clear (ruling 185, [`gz wp discrepancy
   clear`](wp-discrepancy-clear.md)). The rule holds whatever the order's stop.

A move that passes crosses the airlock outward on the repair package's slice: it
books one `airlock_out` and prints the verdict, as [`gz wp accept`](wp-accept.md)
does for a package (ruling 65). A stopped order crosses too, and its verdict
names any file outside the footprint.

An order stopped by a `reopen` or `terminate` exit is excused the first two
gates, as a stopped package is, and Gate 5 at the order is how it closes; a hung
tag holds it as it holds any order (ruling 142). Its readiness is
still read in full, the acceptance, the round limit and the footprint, and every
accepted move books whether it read ready as `acceptance_ready`. Gate 5 reads
that booked fact: a stopped order that read ready here may still close as
`proceed`, and one that did not never does, whatever it earns afterwards (rulings
80 and 84). The order writer refuses an accepted move that books no readiness,
and one that books an order no exit stopped as not ready (ruling 86); this verb
never supplies either. The writer holds no project root, so it cannot read
readiness itself: a stopped order booked ready is trusted from this verb, which
reads it in full. The lifecycle moves one step at a time, an order blocked on
the operator does not move (ruling 59), and its repair package must be initiated
and not closed (rulings 2 and 44).

An accepted order holds the production-write fence until it closes (ruling 58),
and keeps its frozen REQs from every other order's freeze until its Gate 5
(ruling 82).
Its close is Gate 5 at the order, [`gz wp order close`](wp-order-close.md).

The inspection points of rulings 14 and 15 are not read by the runtime yet, so an
order reads ready without them until a later order adds them.

A refusal names what failed, why, and the call to re-run, and books nothing.

## Examples

Observed in a scratch project at `/private/tmp/gz-act5` holding `WP-01-stamp`
initiated. `ORD-01-import` is commenced with no acceptance; `ORD-02-matcher` was
stopped by a `terminate` exit:

```console
$ uv run gz wp order accept ORD-01-import --evidence final-inspection
Acceptance blocked: No durable acceptance contract/proof history. Required proof
and independent closure must remain bound to canon (GHI #985; T1/T2/T3). Run `gz
wp acceptance ORD-01-import status --stage stage4` and repair the named
obligation through the existing pipeline.
$ uv run gz wp order accept ORD-02-matcher --evidence "terminated; no delivery"
ORD-02-matcher: commenced -> accepted
  airlock out: clean
```

Captured in-process from the acceptance wiring fixture
(`tests/commands/test_wp_order_acceptance.py`), `ORD-01-import` stopped by a
`terminate` exit with `TAG-01-stamp` hung on it and not cleared, then with an
open `due-by-event` line, `DSC-01-carry`, citing the tag (line breaks added to
the refusal):

```console
$ uv run gz wp order accept ORD-01-import --evidence final-inspection
Order ORD-01-import has tag(s) hung, not cleared and not carried: TAG-01-stamp.
It is accepted only once every tag it hung is cleared or carried, so no surface
is left isolated past acceptance unrecorded (refusal 6; RP-12 rulings 129, 142
and 171). To clear one, the coordinator authorizes the clearance (`uv run gz wp
tag authorize TAG-01-stamp`), books a Restoration dispatch (`uv run gz wp
dispatch WP-01-stamp --order ORD-01-import --role Restoration --model <tier>`),
and its subagent runs `uv run gz wp tag clear TAG-01-stamp --dispatch D-<id>
--position-found <position>`. To carry one, the coordinator records a line
graded due by a named event that cites it (`uv run gz wp discrepancy record
--order ORD-01-import --tag TAG-01-stamp --grade due-by-event --due-by
"<event>" --source left-broken --slug <slug> --description "<what>"`), and its
Gate 5 then takes a pause alone while the tag hangs. Then accept.
$ uv run gz wp order accept ORD-01-import --evidence final-inspection
ORD-01-import: commenced -> accepted
  carried: TAG-01-stamp on DSC-01-carry (Gate 5: pause alone)
  airlock out: unobserved
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Accepted |
| 1 | The order, or its work package, is not in the store |
| 2 | Usage error |
| 3 | The move is refused: a booked order has lost its record, the lifecycle refuses it, the order is blocked on the operator, the package is not initiated or is closed, acceptance does not read ready, the round limit is used, a file lies outside the footprint, a tag the order hung is neither cleared nor carried, or two open lines carry one tag; nothing booked |

## See also

[`gz wp acceptance`](wp-acceptance.md), [`gz wp order commence`](wp-order-commence.md),
[`gz wp order close`](wp-order-close.md), [`gz wp order show`](wp-order-show.md),
[`gz wp tag clear`](wp-tag-clear.md), [`gz wp accept`](wp-accept.md)
