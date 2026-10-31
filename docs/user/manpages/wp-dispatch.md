# gz wp dispatch

Record one dispatch on a commenced work package, holding the fix-cycle bound.

## Usage

```bash
gz wp dispatch <WP-id> --role <role> --model <tier> (--req <REQ> | --issue <n>) [OPTIONS]
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
| `--json` | Output as JSON |
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

## Examples

Observed in a scratch project holding `WP-01-loop`, commenced, with `#1200` at the
bound:

```console
$ uv run gz wp dispatch WP-01-loop --role SpecReviewer --model sonnet --issue 1200
Recorded SpecReviewer on #1200 of WP-01-loop.
$ uv run gz wp dispatch WP-01-loop --role Implementer --model sonnet --issue 1200
#1200 has used the bound of 2 fix cycles; no further repair cycle runs. Block
and take an exit: reopen, departure, hold, terminate.
```

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | The dispatch was booked |
| 1 | The work package is not in the store |
| 2 | Usage error |
| 3 | The dispatch is refused, the bound included; nothing was booked |

## See also

[`gz wp block`](wp-block.md), [`gz wp unblock`](wp-unblock.md),
[`gz wp show`](wp-show.md)
