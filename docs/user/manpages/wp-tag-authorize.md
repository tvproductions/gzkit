# gz wp tag authorize

Authorize a hung tag's clearance, as the coordinator: book the clearance with the repair activity marked not available.

## Usage

```bash
gz wp tag authorize <TAG-id> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `TAG-id` | The hung tag whose clearance is authorized, `TAG-<NN>-<slug>`. Required |
| `--json` | Output the booked `tag_clearance_authorized` event as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The tag-out log is ledger events, its open tags a derived view (RP-12 ruling 4).
The coordinator issues a tag (`gz wp tag issue`), the Repair dispatch hangs it
(`gz wp tag hang`), and once the work is done the coordinator authorizes its
clearance (ruling 6); the verb books one `tag_clearance_authorized` event. The
Restoration dispatch then clears it (`gz wp tag clear`). `docs/governance/harbor-ro12-contractor-kit.md`
§ Rulings holds the rulings cited here.

- Clearance authorized is the coordinator's act as Authorizing Officer, so a call
  the dispatch stamp marks as a subagent's is refused (rulings 6 and 114). The
  open MX session is recorded as the coordinator's mark; with no session open the
  clearance is refused, and a marker present but unreadable, unbound or exiting is
  refused with the repair its cause names.
- The hanging dispatch's state is read from the ledger, never typed (ruling 7). It
  must be over: ended, which the stamp hook books when its subagent stops (ruling
  115), or voided, how a dispatch killed by `TaskStop` ends (ruling 118). A live
  hanging dispatch is refused, its concurrence not recorded (ruling 138); the
  refusal names both routes. So every clearance records the repair activity *not
  available*, beside the hanging dispatch whose concurrence was absent and whether
  it read ended or voided.
- The tag is issued and hung, and its clearance not already authorized (ruling 6).
- The order is commenced, where the Restoration dispatch that clears is booked,
  a stopped order included, and not blocked: a blocked order's acts are held
  (rulings 59, 132, 135 and 137).
- The tag stays hung and open after its clearance, until the Restoration dispatch
  clears it (ruling 129). `gz wp tag show` names the clearance in its block and
  its `--json` record.
- Limit: the checks read the ledger before the append takes the ledger's lock, so
  two clearances of one tag run at the same moment could both book. No refusal
  holds them apart yet.

A refusal names what failed, why and what to do, and books nothing.

## Examples

Observed 2026-11-18 in a scratch project set up as `tests/commands/test_wp_tag.py`
sets one up: `TAG-01-stamp-hook` issued on `ORD-01-import`, the order frozen, the
tag hung by its `Repair` dispatch's stamped call, then the order commenced. Its MX
marker was opened by the test helper, so the session id below is that fixture's.

With the hanging dispatch still live, exit 3:

```console
$ uv run gz wp tag authorize TAG-01-stamp-hook
Dispatch D-317e698b50648627, which hung TAG-01-stamp-hook, is still live: it has
neither ended nor been voided, and its concurrence is not recorded, so the
clearance is refused (RP-12 rulings 7 and 138). Let its subagent finish, which
books its end, or, if it was killed or abandoned, have the coordinator void it:
`uv run gz wp dispatch WP-01-stamp --void D-317e698b50648627 --reason "<why>"`.
```

The coordinator voids it after a kill:

```console
$ uv run gz wp dispatch WP-01-stamp --void D-317e698b50648627 --reason "killed by TaskStop"
Voided dispatch D-317e698b50648627 on WP-01-stamp: killed by TaskStop.
```

From a call stamped as a subagent's, exit 3:

```console
$ uv run gz wp tag authorize TAG-01-stamp-hook
A clearance is refused from a subagent's call: clearance authorized is the
coordinator's act as Authorizing Officer (RP-12 ruling 6), and the coordinator
is the unstamped operator-facing session (RP-12 ruling 114). Run `uv run gz wp
tag authorize` from the main session.
```

From the main session, exit 0:

```console
$ uv run gz wp tag authorize TAG-01-stamp-hook
Clearance of TAG-01-stamp-hook authorized; D-317e698b50648627 voided, repair
activity not available.
```

The same tag again, exit 3:

```console
$ uv run gz wp tag authorize TAG-01-stamp-hook
Tag TAG-01-stamp-hook's clearance is already authorized, by MX session
test-session; it is authorized once (RP-12 ruling 6). The Restoration dispatch
clears it next.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Authorized |
| 1 | The project is not initialized |
| 2 | Usage error: the tag id missing, or an unknown flag |
| 3 | Refused: a subagent's call, no MX session open or a marker present but not on (its repair named), the tag not issued, not hung or already authorized, the order not commenced, or blocked, or the hanging dispatch still live; nothing booked |

## See also

[`gz wp tag hang`](wp-tag-hang.md), [`gz wp tag clear`](wp-tag-clear.md), [`gz wp tag show`](wp-tag-show.md),
[`gz wp dispatch`](wp-dispatch.md), [`gz wp order commence`](wp-order-commence.md)
