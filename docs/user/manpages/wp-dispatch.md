# gz wp dispatch

Record one dispatch on a commenced work package, holding the fix-cycle bound.

## Usage

```bash
gz wp dispatch <WP-id> --role <role> --model <tier> (--req <REQ> | --issue <n>) [--root <dir>] [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `WP-id` | The work package's id. Required |
| `--role` | `Implementer`, `SpecReviewer`, `QualityReviewer` or `SingleDriver`. Required |
| `--model` | The model tier. Required |
| `--req` | The frozen REQ dispatched against. Give this or `--issue` |
| `--issue` | The carried issue dispatched against. Give this or `--req` |
| `--reason` | Why the run is single-driver. Required with `SingleDriver`, refused otherwise |
| `--root` | The project root the dispatch is for, an existing directory. Defaults to this project's root |
| `--json` | Output as JSON: the booked event, `dispatch_id` and `intended_root` included |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

The verb books one `work_package_dispatched` event, and fix cycles are counted from
those rows (GHI #1200, `docs/governance/harbor-ro14-obpi-forward-migration.md`).

The bound counts against a frozen subject: a REQ of the
package's baseline at its revision, or an issue the package carries. The count
follows a REQ at its revision across packages, so a new package at that revision
starts where the last stopped, and a reopening, which raises the revision, starts
clean.

A subject's first implementing dispatch is free. After it, any review in the
package arms every subject the package has started, a review of a subject arms it
in any package, and each later implementing
dispatch on an armed subject is a fix cycle, a relaunch after a crash included.
The cycle past the bound is refused whatever was ruled, so no unblock opens a further
repair cycle. A reviewer may still look at a subject at the bound. After a
`reopen` or `terminate` exit the package takes no implementing dispatch on any
subject. A package that is not commenced, or is blocked on the operator, takes no
dispatch.

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
tool returns, measured for a foreground subagent (ruling 40). A subagent's `gz` command through the PowerShell tool is
denied, with a reason pointing to Bash (ruling 39). A dispatch meant for
another project, a throwaway one included, names it with `--root`. A relative
root is resolved against the current directory; an empty `--root`, or a root that
is not an existing directory, exits 1 and books nothing. The root is booked as one
absolute path with forward slashes, a drive-rooted Windows path included.

## Examples

Observed in a scratch project holding `WP-01-loop`, commenced, at
`/private/tmp/claude-501/wpd`:

```console
$ uv run gz wp dispatch WP-01-loop --role Implementer --model sonnet --issue 1200
Recorded Implementer on #1200 of WP-01-loop as dispatch D-d74b40917b13f4f5, for
/private/tmp/claude-501/wpd.
Put this line in the dispatched agent's prompt:
GZKIT-DISPATCH: D-d74b40917b13f4f5
$ uv run gz wp dispatch WP-01-loop --role Implementer --model sonnet --issue 1200 --root ../wpd-scratch
Recorded Implementer on #1200 of WP-01-loop as dispatch D-1edf53c694bba4ca, for
/private/tmp/claude-501/wpd-scratch.
Put this line in the dispatched agent's prompt:
GZKIT-DISPATCH: D-1edf53c694bba4ca
```

With `#1200` at the bound:

```console
$ uv run gz wp dispatch WP-01-loop --role Implementer --model sonnet --issue 1200
#1200 has used the bound of 2 fix cycles; no further repair cycle runs. Block
and take an exit: reopen, departure, hold, terminate.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The dispatch was booked |
| 1 | The work package is not in the store, or the intended root is empty or not an existing directory |
| 2 | Usage error |
| 3 | The dispatch is refused, the bound included; nothing was booked |

## See also

[`gz wp block`](wp-block.md), [`gz wp unblock`](wp-unblock.md),
[`gz wp show`](wp-show.md)
