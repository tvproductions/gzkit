# gz wp block

Record that a work package, or one of its orders alone, awaits the operator.

## Usage

```bash
gz wp block <WP-id> [--order <ORD-id>] --reason <text> --next-action <text> [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--reason` | Why the package cannot proceed. Required |
| `--next-action` | The decision the operator owes. Required |
| `--order` | The order held alone, `ORD-<NN>-<slug>`, one of the package's, opened and neither accepted nor closed |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The verb books one `work_package_blocked` event. The runtime writes the facts into
it from the ledger: each subject's fix cycles, the bound, the subjects newly at the
bound, the subjects a hold left open, the exits the package has used, and any baseline REQ already reopened in
any package. An escalation may carry the agent's recommendation, and these
facts sit beside it. A blocked package takes no dispatch until `gz wp unblock`.
An accepted package or order takes no block (RP-12 ruling 69): its final
inspection is done, so it closes through Gate 5's own outcomes, not an exit.

With `--order` the block holds that order alone (RP-12 ruling 59,
`docs/governance/harbor-ro12-contractor-kit.md`). Its facts are the order's own:
the subjects of its frozen baseline, and the exits its own unblocks took. The
event's `id` is the order's, and it names the order in `order`. While the order is
blocked its dispatches and its lifecycle moves are refused, and only
`gz wp unblock --order` lifts it; the package's other orders are still dispatched
and moved. A repair package's run is its orders' (ruling 44), so its block names
the order, and one that does not is refused with exit 3.

While a package is blocked, the production-write fence applies across the whole tree, because a package names no paths (GHI #1206). The pre-commit guard refuses a commit that adds or changes a file under `src/`, and it is on in the hangar and in safe mode. The write hook refuses an edit tool's write there, and is advisory in those two modes. Deletions and `tests/**` stay open. A package stopped by an exit holds the same fence. A subject at the fix-cycle bound does not, because the last admitted cycle must still land, and neither does a hold, which stops only the held subjects; `gz wp dispatch` still refuses both. The state is read from the ledger, and a ledger that cannot be read fences the tree.

An order holds the same fence (ruling 58): one commenced or accepted that is
blocked, accepted, or stopped by an exit on it fences the whole tree, and the
refusal names the order and its recovery. An order closed, or not yet commenced,
does not fence, even blocked. So while one order's block stands, the package's other
orders gain only their steps that write no production code.

## Examples

Observed in a scratch project at `/private/tmp/gz-act5` holding `WP-02-loop`, a
delivery package, with `REQ-7@1` at the bound:

```console
$ uv run gz wp block WP-02-loop --reason "REQ refuted again" --next-action "rule on the exit"
Blocked WP-02-loop on the operator: rule on the exit
  fix cycles (bound 2): REQ-7@1: 2
  refutations: REQ-7@1: 0
  at the bound: REQ-7@1
  held: none
  exits used: none
  reopened: none
```

Holding one order, in the same project holding `WP-01-stamp` initiated and
`ORD-01-import` commenced on `REQ-8@1`:

```console
$ uv run gz wp block WP-01-stamp --order ORD-01-import --reason "The review refuted REQ-8." --next-action "rule on REQ-8"
Blocked order ORD-01-import of WP-01-stamp on the operator: rule on REQ-8
  fix cycles (bound 2): REQ-8@1: 0
  refutations: REQ-8@1: 0
  at the bound: none
  held: none
  exits used: none
  reopened: none
$ uv run gz wp dispatch WP-01-stamp --order ORD-01-import --role Implementer --model sonnet --req REQ-8
Order ORD-01-import is blocked on the operator; it takes no dispatch until `uv
run gz wp unblock WP-01-stamp --order ORD-01-import --ruling <words> --operator
<who>` records the ruling (RP-12 ruling 59).
$ uv run gz wp block WP-01-stamp --reason "R" --next-action "N"
WP-01-stamp is a repair package; its run is its orders' (RP-12 ruling 44). Name
the order: `uv run gz wp block WP-01-stamp --order <ORD-id> ...`.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The block was booked |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The block is refused: the package or order is not live, is already blocked, the order is not one of the package's, a repair package's block names no order, or a field is empty |

## See also

[`gz wp dispatch`](wp-dispatch.md), [`gz wp unblock`](wp-unblock.md)
