# gz wp order close

Close an order through Gate 5 at the order, on the operator's own words.

## Usage

```bash
gz wp order close <ORD-id> --decision <proceed|redirect|pause|terminate> --attestor g0 --attestation-text <words> --evidence <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `ORD-id` | The order, `ORD-<NN>-<slug>`. Required |
| `--decision` | The Gate 5 decision: `proceed`, `redirect`, `pause` or `terminate`. Required |
| `--attestor` | Who attests, `g0`. Required |
| `--attestation-text` | The operator's verbatim Gate 5 words. Required |
| `--evidence` | What justifies the close. Required |
| `--residual-risk` | The residual risk; a `proceed` carries it, and only a `proceed` |
| `--superseded-by` | The order that supersedes this one, `ORD-<NN>-<slug>`; a `redirect` carries it, and only a `redirect` |
| `--revisit-condition` | When the order is revisited; a `pause` carries it, and only a `pause` |
| `--json` | Output the booked event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Books the order's `order_transitioned` to `closed`: Gate 5 at the order
(`docs/governance/harbor-ro12-contractor-kit.md`, RP-12 rulings 30 and 73 to 77).
The event carries the decision, the attestor, the operator's verbatim words and the
evidence, and the one field the decision names (ruling 73):

- `proceed` carries `--residual-risk`: the order is delivered, and each repair REQ
  its freeze froze holds at that revision, which
  [`gz wp order show`](wp-order-show.md) and the repair package's close name
  (rulings 30 and 78). A catalog REQ's proofs counting toward its outcome's
  `validated` lands with RP-14, when orders sit on delivery packages. An order a
  stopping exit excused at acceptance delivered nothing, so its `proceed` is
  refused unless its acceptance reads ready; the order writer itself holds this
  (ruling 80).
- `redirect` carries `--superseded-by`, an order of the same package already opened
  with [`gz wp order new`](wp-order-new.md) and not yet frozen (ruling 75). Rework
  freezes this order's REQ again in that order; a remodel freezes a new REQ carrying
  `supersedes`. The REQ's fix-cycle count follows it (ruling 72).
- `pause` carries `--revisit-condition`: the order is deferred until it holds.
- `terminate` carries nothing more: the order is withdrawn, never delivered, and its
  REQs return to the package unbound.

A decision refuses another decision's field. The order closes from `accepted`,
after its final inspection, or from `opened` as a `terminate` alone: an order never
frozen holds no REQ (ruling 74). A frozen or commenced order is accepted first; a
run stopped by a `reopen` or `terminate` exit reaches `accepted` excused of its
proof through [`gz wp order accept`](wp-order-accept.md). A closed order moves no
further, holds no REQ, so a later order may freeze it (ruling 53), and holds the
production-write fence no longer (ruling 58).

Gate 5 is the operator's act, so a call the dispatch stamp marks as a subagent's
is refused (ruling 77). A booked order that lost its record refuses the close
(ruling 70), an order blocked on the operator does not move (ruling 59), and the
repair package must be initiated and not closed (rulings 2 and 44).

The tag-out log a `pause` clears or carries (ruling 30) does not exist yet, so a
pause records its revisit condition alone.

A refusal names what failed, why, and the call to re-run, and books nothing.

## Examples

Observed in a scratch project holding repair package `WP-01-stamp` (initiated),
with `ORD-01-import` frozen on `REQ-1@1` and commenced, and `ORD-02-spare` opened by
mistake:

```console
$ uv run gz wp order close ORD-01-import --decision proceed --attestor g0 --attestation-text 'the import holds' --residual-risk none --evidence 'gate 5'
Order ORD-01-import cannot move from commenced to 'closed'; the lifecycle allows
accepted from here. An order closes from accepted, or from opened as a terminate
(RP-12 ruling 74). Nothing was written; correct the call and re-run `uv run gz
wp order close <ORD-id> --decision <proceed|redirect|pause|terminate> --attestor
g0 --attestation-text <words> --evidence <text> [--residual-risk <text> |
--superseded-by <ORD-id> | --revisit-condition <text>]`.
$ uv run gz wp order close ORD-02-spare --decision proceed --attestor g0 --attestation-text 'keep it' --residual-risk none --evidence 'gate 5'
Order ORD-02-spare was never frozen and holds no REQ, so it closes only as
terminate; a frozen order closes once it is accepted (RP-12 ruling 74). Nothing
was written; correct the call and re-run `uv run gz wp order close <ORD-id>
--decision <proceed|redirect|pause|terminate> --attestor g0 --attestation-text
<words> --evidence <text> [--residual-risk <text> | --superseded-by <ORD-id> |
--revisit-condition <text>]`.
$ uv run gz wp order close ORD-02-spare --decision terminate --attestor g0 --attestation-text 'withdraw the spare order' --evidence 'opened by mistake'
ORD-02-spare: opened -> closed
```

Once `ORD-01-import` was stopped by a `terminate` exit and accepted, a `proceed`,
then the same `terminate` from a subagent's call and from the main session:

```console
$ uv run gz wp order close ORD-01-import --decision proceed --attestor g0 --attestation-text 'it holds' --residual-risk none --evidence 'gate 5'
ORD-01-import took a stopping exit and acceptance does not read ready, so it
delivered nothing to proceed with, and a proceed would hold its REQs (RP-12
rulings 78 and 80). Close it as `redirect`, `pause` or `terminate`. Nothing was
written; correct the call and re-run `uv run gz wp order close <ORD-id>
--decision <proceed|redirect|pause|terminate> --attestor g0 --attestation-text
<words> --evidence <text> [--residual-risk <text> | --superseded-by <ORD-id> |
--revisit-condition <text>]`.
$ uv run gz wp order close ORD-01-import --decision terminate --attestor g0 --attestation-text 'stop it' --evidence 'gate 5'
Gate 5 is refused from a subagent's call: it is the operator's act, recorded on
the operator's own words (RP-12 ruling 77, AGENTS.md § Attestation). Run it from
the main session.
$ uv run gz wp order close ORD-01-import --decision terminate --attestor g0 --attestation-text 'the stop stands' --evidence 'gate 5'
ORD-01-import: accepted -> closed
```

The close it booked, read from the scratch ledger:

```json
{"schema":"gzkit.ledger.v1","event":"order_transitioned","id":"ORD-01-import","ts":"2026-11-08T07:58:21.166547+00:00","modules":[],"attestation_text":"the stop stands","to_state":"closed","evidence":"gate 5","work_package":"WP-01-stamp","order":"ORD-01-import","attestor":"g0","from_state":"accepted","approved_alterations":[],"decision":"terminate","baseline":[]}
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Closed |
| 1 | The order is not in the store |
| 2 | Usage error |
| 3 | The close is refused: a subagent's call, a booked order that lost its record, the lifecycle, the order's block, the package's state, a proceed on an order that delivered nothing, missing words or decision, a decision's field missing or another's given, or a redirect's successor; nothing booked |

## See also

[`gz wp order accept`](wp-order-accept.md), [`gz wp order new`](wp-order-new.md),
[`gz wp order show`](wp-order-show.md), [`gz wp close`](wp-close.md)
