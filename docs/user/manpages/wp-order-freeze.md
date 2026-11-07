# gz wp order freeze

Freeze an opened order's REQ baseline and seal its repair package's footprint.

## Usage

```bash
gz wp order freeze <ORD-id> --baseline REQ-<n>@<rev> --risk-note <text> --review-receipt <id> --evidence <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `ORD-id` | The order to freeze, `ORD-<NN>-<slug>`. Required |
| `--baseline` | A REQ and the revision frozen, `REQ-<n>@<rev>` (repeatable). At least one is required |
| `--risk-note` | The short risk note. Required |
| `--review-receipt` | The reviewer's nine-criteria receipt. Required |
| `--evidence` | What justifies the freeze. Required |
| `--json` | Output the booked event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Books the order's `order_transitioned` to `frozen`
(`docs/governance/harbor-ro12-contractor-kit.md`, RP-12 O2 task 3). The order
moves one step at a time, `opened` then `frozen`, `commenced` and `accepted`;
`closed` is Gate 5 at the order, which lands with O2 task 4.

- The freeze carries the risk note, the reviewer's receipt and the baseline. Each
  baseline entry is a repair REQ held on the order's own package, at the revision
  the catalog holds (RP-12 rulings 2 and 45), and the baseline holds at least one:
  an order frozen on nothing could take no dispatch and reach no acceptance
  (ruling 61).
- A repair REQ sits in one live order's frozen baseline at a time. A REQ another
  order's freeze holds is refused until that order is accepted, stopped or closed
  (ruling 53).
- The freeze seals the repair package's footprint: the event records the
  package's paths, and from then on `gz wp show` and the acceptance fence read the
  latest order freeze plus the change orders after it, never the store, and a
  change order may no longer drop a path (ruling 56). The package must declare a
  footprint that holds, as a package's own freeze requires (RO-14 ruling 24).
- The order's repair package must be initiated and not closed (rulings 2 and 44).

A refusal names what failed, why, and the call to re-run, and writes nothing.

## Examples

Observed in a scratch project holding repair package `WP-01-stamp` (initiated,
footprint `src/stamp.py`), its repair requirement `REQ-1` at revision 1 and the
opened order `ORD-01-import`:

```console
$ uv run gz wp order freeze ORD-01-import --baseline REQ-1 --risk-note "Touches the hook." --review-receipt review-01 --evidence "nine-criteria review"
--baseline 'REQ-1' is not REQ-<n>@<revision>. Nothing was written; correct the
call and re-run `uv run gz wp order freeze <ORD-id> --baseline
REQ-<n>@<revision> --risk-note <text> --review-receipt <id> --evidence <text>`.
$ uv run gz wp order freeze ORD-01-import --baseline REQ-1@2 --risk-note "Touches the hook." --review-receipt review-01 --evidence "nine-criteria review"
REQ-1 at revision 2 is not a REQ the catalog holds. Nothing was written; correct
the call and re-run `uv run gz wp order freeze <ORD-id> --baseline
REQ-<n>@<revision> --risk-note <text> --review-receipt <id> --evidence <text>`.
$ uv run gz wp order freeze ORD-01-import --baseline REQ-1@1 --risk-note "Touches the hook." --review-receipt review-01 --evidence "nine-criteria review"
ORD-01-import: opened -> frozen
```

The freeze it booked, read from the scratch ledger:

```json
{"schema":"gzkit.ledger.v1","event":"order_transitioned","id":"ORD-01-import","ts":"2026-11-07T09:50:51.377594+00:00","from_state":"opened","evidence":"nine-criteria review","to_state":"frozen","baseline":[{"req":"REQ-1","revision":1}],"review_receipt":"review-01","work_package":"WP-01-stamp","order":"ORD-01-import","risk_note":"Touches the hook.","modules":["src/stamp.py"]}
```

A second order in the package, opened as `ORD-02-matcher`, cannot freeze the
REQ `ORD-01-import` holds, and an order in repair package `WP-03-idle`, which
declares no footprint, cannot seal one:

```console
$ uv run gz wp order freeze ORD-02-matcher --baseline REQ-1@1 --risk-note "Touches the matcher." --review-receipt review-02 --evidence "nine-criteria review"
REQ-1 is in the frozen baseline of live order ORD-01-import; a repair REQ sits
in one live order's baseline at a time, until that order is accepted, stopped or
closed (RP-12 ruling 53). Freeze without it, or split it with a REQ that
supersedes it. Nothing was written; correct the call and re-run `uv run gz wp
order freeze <ORD-id> --baseline REQ-<n>@<revision> --risk-note <text>
--review-receipt <id> --evidence <text>`.
$ uv run gz wp order freeze ORD-03-idle --baseline REQ-2@1 --risk-note "None." --review-receipt review-03 --evidence "nine-criteria review"
Repair package WP-03-idle declares no footprint. A repair package carries a
valid footprint, as a brief carries Allowed Paths (RO-14 ruling 24). Add one
with `uv run gz wp change WP-03-idle --rung change_order --approver operator
--change <text> --superseded <text> --work-stopped --module <path>`, then freeze
again. An order's freeze seals it (RP-12 ruling 56). Nothing was written;
correct the call and re-run `uv run gz wp order freeze <ORD-id> --baseline
REQ-<n>@<revision> --risk-note <text> --review-receipt <id> --evidence <text>`.
```

A freeze with no `--baseline` is refused, here on a third order opened as
`ORD-02-matcher` in a later scratch project:

```console
$ uv run gz wp order freeze ORD-02-matcher --risk-note "Touches the matcher." --review-receipt review-02 --evidence E
Order ORD-02-matcher freezes at least one repair REQ held on WP-01-stamp; an
order frozen on nothing takes no dispatch and reaches no acceptance (RP-12
ruling 61). Write one with `uv run gz wp req new`, then freeze on it. Nothing
was written; correct the call and re-run `uv run gz wp order freeze <ORD-id>
--baseline REQ-<n>@<revision> --risk-note <text> --review-receipt <id>
--evidence <text>`.
```

Once the footprint is sealed, a change order cannot drop a path:

```console
$ uv run gz wp change WP-01-stamp --rung change_order --approver operator --change "Narrow it." --superseded src/stamp.py --work-stopped --drop-module src/stamp.py
WP-01-stamp's footprint is sealed by an order's freeze (RP-12 ruling 56), and a
sealed footprint only grows, so a dropped path cannot hide what was allowed. Add
what is missing with `--module`.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Frozen |
| 1 | The order, or its work package, is not in the store |
| 2 | Usage error |
| 3 | The freeze is refused: an empty baseline or a baseline entry, the lifecycle, the package's state or footprint, or a REQ another live order holds; nothing written |

## See also

[`gz wp order commence`](wp-order-commence.md), [`gz wp order new`](wp-order-new.md),
[`gz wp order show`](wp-order-show.md), [`gz wp req new`](wp-req-new.md),
[`gz wp change`](wp-change.md)
