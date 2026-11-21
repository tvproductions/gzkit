# gz wp dispatch

Record one dispatch on a commenced work package or order, holding the fix-cycle
bound, or a craftsman's on a repair package's frozen or commenced order, or void
one the coordinator abandoned.

## Usage

```bash
gz wp dispatch <WP-id> --role <role> --model <tier> --req <REQ> [--root <dir>] [OPTIONS]
gz wp dispatch <WP-id> --order <ORD-id> --role <role> --model <tier> --req <REQ> [--root <dir>] [OPTIONS]
gz wp dispatch <WP-id> --order <ORD-id> --role Repair|Restoration --model <tier> [--root <dir>] [OPTIONS]
gz wp dispatch <WP-id> --void <D-id> --reason <why> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--role` | `Implementer`, `SpecReviewer`, `QualityReviewer` or `SingleDriver`; on a repair package's order also `Repair` (a frozen order) or `Restoration` (a commenced order, or a paused one still holding a carried tag, ruling 187). Required to book |
| `--model` | The model tier. Required to book |
| `--req` | The frozen REQ dispatched against. Required to book, except that `Repair` and `Restoration` name none |
| `--reason` | Why the run is single-driver: required with `SingleDriver`, refused otherwise. With `--void`, why the dispatch is abandoned, required |
| `--void` | Abandon this booked dispatch, `D-` and 16 hex digits, instead of booking one; takes none of booking's flags |
| `--root` | The project root the dispatch is for, an existing directory. Defaults to this project's root |
| `--order` | The order dispatched on, `ORD-<NN>-<slug>`, one of the package's. Required on a repair package. It must be commenced, and `--req` must name a REQ its freeze holds; a `Repair` dispatch takes it frozen instead and a `Restoration` dispatch commenced, each naming no REQ. Taken by no `--void` |
| `--json` | Output as JSON: the booked event, `dispatch_id`, `intended_root` and `order` included |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The verb books one `work_package_dispatched` event, and fix cycles are counted from
those rows (GHI #1200, `docs/governance/harbor-ro14-obpi-forward-migration.md`).

The bound counts against a frozen subject: a REQ of the package's or the order's
baseline at its revision. A carried issue is never a subject; `--issue` is retired
and is a usage error (RP-12 ruling 64). The count
follows a REQ at its revision across packages, so a new package or order at that
revision starts where the last stopped. No verb raises a REQ's revision (RP-12
ruling 83), so past the bound new work is a REQ that supersedes it, whose count
starts clean (rulings 50 and 89).

A subject's first implementing dispatch is free. After it, any review (`SpecReviewer` or `QualityReviewer`) in the
package arms every subject the package has started, a review of a subject arms it
in any package, and each later implementing
dispatch on an armed subject is a fix cycle, a relaunch after a crash included.
The cycle past the bound is refused whatever was ruled, so no unblock opens a further
repair cycle. A reviewer may still look at a subject at the bound. After a
`reopen` or `terminate` exit the package takes no implementing dispatch on any
subject. A package that is not commenced, or is blocked on the operator, takes no
dispatch.

A repair package's run is its orders' (RP-12 ruling 44,
`docs/governance/harbor-ro12-contractor-kit.md`), so its dispatch names the order
with `--order`, and one that does not is refused with exit 3. With `--order` the
dispatch is on an order of a repair package (ruling 57). It takes a subject only
when the REQ is in the order's frozen baseline, at the revision frozen, and only
while the order is commenced and its package initiated (rulings 2 and 44). A REQ
held on the package but not frozen by this order, and an order of another package,
are refused, so a REQ found mid-repair waits for a new order or a re-freeze. The
fix-cycle bound counts against that subject as it does on a package. An order
blocked on the operator takes no dispatch until `gz wp unblock --order` (ruling
59), and after a `reopen` or `terminate` exit on the order it takes no
implementing dispatch. The
booked row names the order, so the guard on an open dispatch reads the order's
run: a dispatch on an order is open while that order is frozen, commenced or
accepted, though its package stays initiated (rulings 40 and 134).

The craftsman's two positions are two roles, taken only on a repair package's order
and refused anywhere else (RP-12 ruling 109). Each names no REQ, and its subject is
the order, so it is bound to the order and not to a requirement (ruling 130). A
`Repair` dispatch, the one that hangs the order's tags, takes a frozen order alone,
not blocked, and is refused once the order is commenced (rulings 108 and 131). A
`Restoration` dispatch, the one that clears them, takes a commenced order (ruling
132), or a paused one whose acceptance carried a tag that still hangs (ruling 187). Neither is a review, so neither arms a fix cycle, and neither is
held to the bound. A dispatch on a frozen order is open to the guard as one on a
commenced order is (ruling 134). A stopping exit on the order holds neither role,
since restoring what the order isolated must still happen (ruling 135).

A delivery package may declare `SingleDriver` with its reason. Its first dispatch
arms the count, and a later change of role keeps it, so the same bound applies. A
repair package cannot be single-driver, because nobody inspects their own work.

The count sees only what is recorded, under the labels recorded: a dispatch nobody
books is not counted. A subject with no review and no single-driver declaration
has no bound, because the count starts at a review.

Each dispatch is its own record (RP-12 ruling 1,
`docs/governance/harbor-ro12-contractor-kit.md`): the runtime mints a dispatch id,
binds it to the role, the subject and the intended root, and prints the line that
names it. Put that line in the dispatched agent's prompt. The stamp hook reads it
from the subagent's own transcript to learn which dispatch, and so which root, a
subagent's `gz` command belongs to (rulings 17, 34 and 35). Every `gz` verb run
under that stamp from any directory but the intended root, or under a stamp that
names no root, is refused with exit 3 before it writes (ruling 36). A call
that passes drops the stamp, so what it runs, a test or a nested `gz`, is not
refused (ruling 37). A subagent with no dispatch line is held to the project's
own root (ruling 38), unless a dispatch is open: booked for another root, on a
package whose run is in flight, and claimed by no subagent. The hooks book a
claim as `dispatch_claimed` at a subagent's first `gz` call and when the Agent
tool returns: a foreground subagent's at its finish, a background one's at
launch (ruling 40; measured in the dock trial). A subagent's `gz` command
through the PowerShell tool is denied, with a reason pointing to Bash (ruling
39). A dispatch meant for another project, a throwaway one included, names it with `--root`. A relative
root is resolved against the current directory; an empty `--root`, or a root that
is not an existing directory, exits 1 and books nothing. The root is booked as one
absolute path with forward slashes, a drive-rooted Windows path included.

`--void` abandons a booked dispatch: one never spawned, handed to a harness with
no hooks, or whose subagent stopped before it ran `gz`. It books one
`dispatch_voided` event with its reason, and a voided dispatch is no dispatch: it
is never open, and a subagent carrying its line is stamped no root (ruling 42).
Only the coordinator voids: a call stamped as a subagent's is refused with exit
3, as far as the stamp reaches; a subagent's `gz` run through `gz arb step`, `coverage`
or `ty` keeps its stamp (ruling 37). `--void` takes none of booking's flags. A dispatch already voided, never
booked, or booked on another package is refused with exit 3.

## Examples

Observed in a scratch project at `/private/tmp/gz-act5` holding `WP-02-loop`, a
delivery package commenced on `REQ-7@1`:

```console
$ uv run gz wp dispatch WP-02-loop --role Implementer --model sonnet --req REQ-7
Recorded Implementer on REQ-7@1 of WP-02-loop as dispatch D-479347538505df73,
for /private/tmp/gz-act5.
Put this line in the dispatched agent's prompt:
GZKIT-DISPATCH: D-479347538505df73
$ uv run gz wp dispatch WP-02-loop --role Implementer --model sonnet --req REQ-7 --root ../gz-act5-scratch
Recorded Implementer on REQ-7@1 of WP-02-loop as dispatch D-1cb6a87eacd9ad34,
for /private/tmp/gz-act5-scratch.
Put this line in the dispatched agent's prompt:
GZKIT-DISPATCH: D-1cb6a87eacd9ad34
```

Voiding an abandoned dispatch, then the refusals, in the same project:

```console
$ uv run gz wp dispatch WP-02-loop --void D-1cb6a87eacd9ad34 --reason "never spawned"
Voided dispatch D-1cb6a87eacd9ad34 on WP-02-loop: never spawned.
$ uv run gz wp dispatch WP-02-loop --void D-1cb6a87eacd9ad34 --reason "again"
No live dispatch D-1cb6a87eacd9ad34 is booked; nothing to void.
$ uv run gz wp dispatch WP-02-loop --void D-1cb6a87eacd9ad34
--void needs --reason, why the dispatch is abandoned.
```

On a repair package, in the same project, holding `WP-01-stamp` initiated and
`ORD-01-import` commenced on `REQ-8@1`:

```console
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Implementer --model sonnet --req REQ-8
Recorded Implementer on REQ-8@1 of order ORD-01-import of WP-01-stamp as
dispatch D-155d7b71611281cf, for /private/tmp/gz-act5.
Put this line in the dispatched agent's prompt:
GZKIT-DISPATCH: D-155d7b71611281cf
$ uv run gz wp dispatch WP-01-stamp --role Implementer --model sonnet --req REQ-8
WP-01-stamp is a repair package; its run is its orders' (RP-12 ruling 44). Name
the order: `uv run gz wp dispatch WP-01-stamp --order <ORD-id> ...`.
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Implementer --model sonnet --issue 1301
BLOCKERS: gz: error: unrecognized arguments: --issue 1301
```

On the same repair package's order, its craftsman's two roles (rulings 108, 109
and 130 to 132), observed 2026-11-17 in a temporary project set up as
`tests/commands/test_wp_tag.py` sets one up, `ORD-01-import` frozen. While the
order is frozen, Restoration is refused, Repair is booked, and a Repair naming a
REQ is refused:

```console
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Restoration --model sonnet
Order ORD-01-import is frozen; a Restoration dispatch takes a commenced order
alone (RP-12 ruling 132). Commence the order first: `uv run gz wp order commence
ORD-01-import --evidence <ref>`.
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Repair --model sonnet
Recorded Repair on order ORD-01-import of WP-01-stamp as dispatch
D-4e0c7d9be3e770dd, for
/private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpo3_3j8qn.
Put this line in the dispatched agent's prompt:
GZKIT-DISPATCH: D-4e0c7d9be3e770dd
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Repair --model sonnet --req REQ-1
A Repair dispatch is bound to its order and names no REQ (RP-12 ruling 130 and
rulings 108 and 131). Re-run the call without --req REQ-1.
```

Once the order is commenced, Repair is refused and Restoration is booked:

```console
$ uv run gz wp order commence ORD-01-import --evidence E
ORD-01-import: frozen -> commenced
  airlock in: proceed
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Repair --model sonnet
Order ORD-01-import is commenced; a Repair dispatch takes a frozen order alone
(RP-12 rulings 108 and 131). Read the order's state with `uv run gz wp order
show ORD-01-import`.
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Restoration --model sonnet
Recorded Restoration on order ORD-01-import of WP-01-stamp as dispatch
D-3c727265288aded0, for
/private/var/folders/7y/cvcpqqnj2_52yy4wl780kmqc0000gn/T/tmpo3_3j8qn.
Put this line in the dispatched agent's prompt:
GZKIT-DISPATCH: D-3c727265288aded0
```

With `REQ-7@1` at the bound:

```console
$ uv run gz wp dispatch WP-02-loop --role Implementer --model sonnet --req REQ-7
REQ-7@1 has used the bound of 2 fix cycles; no further repair cycle runs. Block
and take an exit: reopen, departure, hold, terminate.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The dispatch was booked, or voided |
| 1 | The work package is not in the store, the intended root is empty or not an existing directory, or `--void` has no `--reason` |
| 2 | Usage error: `--role` or `--model` missing to book, a booking flag, `--order` included, given with `--void`, or the retired `--issue` |
| 3 | The dispatch or the void is refused, the bound, a subagent's call, a repair package's dispatch with no `--order`, a subject outside the order's freeze, and a `Repair` or `Restoration` dispatch off a repair package's order, on an order not in its state, or naming a REQ included; nothing was booked |

## See also

[`gz wp block`](wp-block.md), [`gz wp unblock`](wp-unblock.md),
[`gz wp show`](wp-show.md), [`gz wp order commence`](wp-order-commence.md)
