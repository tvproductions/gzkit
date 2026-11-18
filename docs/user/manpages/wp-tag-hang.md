# gz wp tag hang

Hang an issued tag, as the Repair dispatch's stamped call: book the hang with the issue's line item copied.

## Usage

```bash
gz wp tag hang <TAG-id> --dispatch <D-id> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `TAG-id` | The issued tag hung, `TAG-<NN>-<slug>`. Required |
| `--dispatch` | The live `Repair` dispatch hanging it, the one this call is stamped with. Required |
| `--json` | Output the booked `tag_hung` event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The tag-out log is ledger events, its open tags a derived view (RP-12 ruling 4).
The coordinator issues a tag (`gz wp tag issue`); the Repair dispatch, the
craftsman's repair position, hangs it (ruling 6), and the verb books one
`tag_hung` event. `docs/governance/harbor-ro12-contractor-kit.md` § Rulings holds
the rulings cited here.

- A hang is the stamped call of the Repair dispatch it names (ruling 133). `gz`'s
  entry keeps the dispatch id the call was stamped with before it consumes the
  stamp (ruling 37), and the hang is refused unless that id is the one
  `--dispatch` names. An unstamped call, the main session's or a Codex session's,
  cannot hang. The limit is ruling 1's: the id stops mistakes and shortcuts, not
  forgery.
- The dispatch is a live `Repair` dispatch, booked and not voided, on the tag's
  own order (rulings 1, 42, 109 and 130), booked with
  `gz wp dispatch <WP-id> --order <ORD-id> --role Repair --model <tier>`.
- The order is frozen and not blocked (rulings 59 and 131): a tag is hung before
  the order commences, and a blocked order's acts are held.
- The tag is issued, not already hung, and open: a tag whose order closed with it
  unhung has left the open log (rulings 6 and 122).
- The event copies the issue's line item (ruling 120), carries the issue's mark as
  `issued_by_session`, and records the open MX session at the hang as its holder
  (ruling 133). With no session open the hang is refused, and a marker present
  but unreadable, unbound or exiting is refused with the repair its cause names.
- A hung tag reads open until its clear, whatever its order's state, and keeps
  its surface from a new issue (ruling 129).
- Limit: the checks read the ledger before the append takes the ledger's lock,
  so two hangs of one tag run at the same moment, from two `Repair` dispatches
  on its order, could both book. No refusal holds them apart yet.

A refusal names what failed, why and what to do, and books nothing.

## Examples

Observed 2026-11-17 in a scratch project set up as `tests/commands/test_wp_tag.py`
sets one up: `TAG-01-stamp-hook` issued on `ORD-01-import`, the order frozen and two
`Repair` dispatches booked on it. Its MX marker was opened by the test helper, and
each stamped call was stamped as the stamp hook stamps that dispatch's subagent.

From an unstamped call, exit 3:

```console
$ uv run gz wp tag hang TAG-01-stamp-hook --dispatch D-ccaaffb54630afa2
This call is not stamped, and a hang is the stamped call of the Repair dispatch
it names, D-ccaaffb54630afa2 (RP-12 ruling 133). If D-ccaaffb54630afa2 is a live
Repair dispatch, run the hang from its own subagent, its prompt carrying the
dispatch line; with none booked for the tag's order, have the coordinator book
one: `uv run gz wp dispatch <WP-id> --order <ORD-id> --role Repair --model
<tier>`.
```

From a call stamped as the other `Repair` dispatch, `D-db80c08de7493108`, exit 3:

```console
$ uv run gz wp tag hang TAG-01-stamp-hook --dispatch D-ccaaffb54630afa2
This call is stamped with D-db80c08de7493108, and a hang is the stamped call of
the Repair dispatch it names, D-ccaaffb54630afa2 (RP-12 ruling 133). If
D-db80c08de7493108 is the Repair dispatch meant, name it: `uv run gz wp tag hang
TAG-01-stamp-hook --dispatch D-db80c08de7493108`; otherwise the hang belongs to
D-ccaaffb54630afa2's own subagent.
```

From the named dispatch's stamped call, exit 0:

```console
$ uv run gz wp tag hang TAG-01-stamp-hook --dispatch D-ccaaffb54630afa2
Hung TAG-01-stamp-hook by D-ccaaffb54630afa2.
```

The same tag again, from the same dispatch's stamped call, exit 3:

```console
$ uv run gz wp tag hang TAG-01-stamp-hook --dispatch D-ccaaffb54630afa2
Tag TAG-01-stamp-hook is already hung, by dispatch D-ccaaffb54630afa2; a tag is
hung once (RP-12 ruling 6). Read it with `uv run gz wp tag show --all`; nothing
remains to hang.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Hung |
| 1 | The project is not initialized |
| 2 | Usage error: the tag id or `--dispatch` missing, or an unknown flag |
| 3 | Refused: no MX session open or a marker present but not on (its repair named), the call not stamped with the dispatch named, the tag not issued, already hung or not open, the dispatch not a live `Repair` on the tag's order, or the order not frozen, or blocked; nothing booked |

## See also

[`gz wp tag issue`](wp-tag-issue.md), [`gz wp tag show`](wp-tag-show.md),
[`gz wp dispatch`](wp-dispatch.md), [`gz wp order freeze`](wp-order-freeze.md)
