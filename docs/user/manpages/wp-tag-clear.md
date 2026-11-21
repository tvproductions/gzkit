# gz wp tag clear

Clear a hung tag whose clearance is authorized, as the Restoration dispatch's stamped call: book the clear with the position found, or block the order when it is found out of position.

## Usage

```bash
gz wp tag clear <TAG-id> --dispatch <D-id> --position-found <position> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `TAG-id` | The hung tag to clear, `TAG-<NN>-<slug>`. Required |
| `--dispatch` | The live `Restoration` dispatch clearing it, `D-<id>`, the one this call is stamped with. Required |
| `--position-found` | The position the surface was found in: `off`, `advisory`, `recording` or `on`. Required |
| `--json` | Output the booked event as JSON: `tag_cleared`, or `work_package_blocked` when found out of position |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The tag-out log is ledger events, its open tags a derived view (RP-12 ruling 4).
The coordinator issues a tag (`gz wp tag issue`), the Repair dispatch hangs it
(`gz wp tag hang`), the coordinator authorizes its clearance (`gz wp tag
authorize`), and the Restoration dispatch clears it, recording the position it
found the surface in (ruling 6). `docs/governance/harbor-ro12-contractor-kit.md`
§ Rulings holds the rulings cited here.

- The clear is the stamped call of the dispatch `--dispatch` names: the call must
  carry that dispatch's stamp, so the main session and any other subagent are
  refused (rulings 6 and 133). The dispatch is a live `Restoration` dispatch
  booked on the tag's order with `gz wp dispatch --role Restoration`; one that
  has ended or been voided is refused (rulings 1, 42, 115 and 132).
- The one who hung a tag never clears it (refusal 1, rulings 6, 109 and 139): a
  clear is refused when the clearing dispatch is the hanging one, or when a
  subagent that claimed the hanging dispatch also claimed the clearing one, read
  from the `dispatch_claimed` rows the stamp hook books.
- The tag is hung, its clearance authorized and not already cleared (ruling 6).
  The order is commenced and not blocked (rulings 59, 132 and 135), or paused at
  Gate 5 with the tag among those its acceptance carried (ruling 187). The open MX
  session is recorded as the holder; with none open the clear is refused.
- `--position-found` takes one of a closed set: the three positions a tag is
  hung in, or `on`, a surface found back in service (ruling 140). Found in the
  position the tag was hung in, the verb books one `tag_cleared` event naming
  both dispatches and the clearance's mark, and the tag reads closed, freeing its
  surface for a new issue (ruling 129).
- Found in any other position, `on` among them, it books no clear. It books one
  `work_package_blocked` on the tag's order instead, its reason and the decision
  owed written from the tag, its surface and both positions, prints the block and
  exits 3 with the tag still hung (ruling 137); on an order Gate 5 paused with
  the tag carried, the paused order takes that block too (ruling 188). The order's
  acts are held, its clears among them, until the operator's `gz wp unblock`. Until O5 lands the
  stop, the block holds the order alone, not the surface across every order that
  touches it.
- Limit: the checks read the ledger before the append takes the ledger's lock, so
  two clears of one tag run at the same moment could both book. No refusal holds
  them apart yet.

A refusal names what failed, why and what to do, and books nothing.

## Examples

Observed 2026-11-18 in a scratch project set up as `tests/commands/test_wp_tag.py`
sets one up: `TAG-01-stamp-hook` issued on `ORD-01-import` for
`validator:hexagon-tests` in position `off`, the order frozen, the tag hung by its
`Repair` dispatch, the order commenced, the hanging dispatch voided, the
clearance authorized, and `Restoration` dispatch `D-e11ff2aa6a9dbeb7` booked on
the order. Its MX marker was opened by the test helper.

From the main session, unstamped, exit 3 (its wording re-captured 2026-11-20):

```console
$ uv run gz wp tag clear TAG-01-stamp-hook --dispatch D-e11ff2aa6a9dbeb7 --position-found off
This call is not stamped with a dispatch id, and a clear is the stamped call of
the Restoration dispatch it names, D-e11ff2aa6a9dbeb7 (RP-12 rulings 6 and 133).
Run the clear from D-e11ff2aa6a9dbeb7's own subagent, its prompt carrying the
dispatch line.
```

From the Restoration dispatch's stamped call, the surface found back `on`, exit 3
with the order blocked and the tag still hung:

```console
$ uv run gz wp tag clear TAG-01-stamp-hook --dispatch D-e11ff2aa6a9dbeb7 --position-found on
Blocked order ORD-01-import on the operator: Tag TAG-01-stamp-hook was hung with
validator:hexagon-tests off, and its clear found it on: out of position, so
restoration stops and the discrepancy goes to the Authorizing Officer (RP-12
ruling 137, TUM 1.8.5.b(2)). The tag stays hung.
Tag TAG-01-stamp-hook was found on, out of position, so it is not cleared: order
ORD-01-import is blocked on the operator and the tag stays hung (RP-12 ruling
137). The decision owed: Rule on how validator:hexagon-tests came to be on, not
off, and what restores it; then unblock ORD-01-import and have a Restoration
dispatch clear TAG-01-stamp-hook again.
```

Again while the order is blocked, exit 3:

```console
$ uv run gz wp tag clear TAG-01-stamp-hook --dispatch D-e11ff2aa6a9dbeb7 --position-found off
Order ORD-01-import is blocked on the operator, and a blocked order's acts are
held, its clears among them (RP-12 rulings 59 and 137). Run the clear again once
`uv run gz wp unblock WP-01-stamp --order ORD-01-import --ruling <words>
--operator <who>` records the ruling.
```

The operator rules and the order is unblocked from the main session:

```console
$ uv run gz wp unblock WP-01-stamp --order ORD-01-import --ruling "The hook was re-registered by hand; set it off and clear again." --operator g0
Unblocked order ORD-01-import of WP-01-stamp.
```

From the stamped call, the surface found `off` as it was hung, exit 0:

```console
$ uv run gz wp tag clear TAG-01-stamp-hook --dispatch D-e11ff2aa6a9dbeb7 --position-found off
Cleared TAG-01-stamp-hook by D-e11ff2aa6a9dbeb7, found off.
```

The same tag again, exit 3:

```console
$ uv run gz wp tag clear TAG-01-stamp-hook --dispatch D-e11ff2aa6a9dbeb7 --position-found off --json
Tag TAG-01-stamp-hook is already cleared, by dispatch D-e11ff2aa6a9dbeb7; a tag
is cleared once (RP-12 ruling 6). `uv run gz wp tag show --all` reads it.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Cleared: the tag reads closed |
| 1 | The project is not initialized |
| 2 | Usage error: the tag id, `--dispatch` or `--position-found` missing, a position outside the set, or an unknown flag |
| 3 | Found out of position: the order's block booked, the tag still hung. Or refused, nothing booked: no MX session open or a marker present but not on (its repair named), the call not stamped with the named dispatch, the tag not hung, not authorized or already cleared, the dispatch not a live `Restoration` on the tag's order, the subagent that hung it, or the order not commenced, or blocked |

## See also

[`gz wp tag authorize`](wp-tag-authorize.md), [`gz wp tag show`](wp-tag-show.md),
[`gz wp dispatch`](wp-dispatch.md), [`gz wp unblock`](wp-unblock.md)
