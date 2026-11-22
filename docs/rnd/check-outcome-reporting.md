# R&D run — check-outcome-reporting

> Diamond 1 of the double diamond. This record defines the problem and names what is
> warranted; it produces no fan-out artifact and authorizes none. Opened 2026-11-22T19:04Z.

**Challenge.** A check that did not run, or whose failure was demoted, reports as passed, on
every enforcement surface the session swept. The operator, on being told the safe-mode alarm
switch makes pre-commit print "Passed" for a `gz check` that never ran, verbatim: *"why would
we introduce safe mode exceptions? that is going to get out of control and lost very
quickly."* and *"This is very worrying"* … *"I now suspect this behavior exists elsewhere"*.
On being offered a route: *"fix the two guards now, then run the R&D"*. The run asks why the
class keeps producing, and how the issues that carry it should be framed, consolidated or
sequenced.

---

## source · the operator's ruling against safe-mode exceptions

Session `e870dccc-bfdb-48be-baa8-a327a1e81cb8`, 2026-11-22; recorded as insight
`2026-11-22T16:18:07.471797+00:00` (scope `check-reporting`, type `improvement`) · read
2026-11-22

> A guard's report must not depend on safe mode: no safe-mode-only exception is added to make
> a switched-off hook visible; the defect is that a check that did not run, or whose failure
> was demoted, reports as passed, and it is to be found wherever it lives (operator,
> 2026-11-22: "why would we introduce safe mode exceptions? that is going to get out of
> control and lost very quickly.", "I now suspect this behavior exists elsewhere").

The operator rejected the agent's first option (`verbose: true` on the five alarm-switched
hooks, shown only in the drydock) before it was put. Any remedy this run proposes has to hold
at every mode, not as a drydock special case.

## source · the session's defect insights

`.gzkit/insights/agent-insights.jsonl`, scope `check-reporting`, records
`2026-11-22T16:31:12.130394+00:00`, `2026-11-22T16:31:12.251719+00:00`,
`2026-11-22T18:59:47.337570+00:00` · read 2026-11-22

> A check that did not run, or whose failure was demoted, reports as passed across every
> enforcement surface: the alarm switch exits 0 and pre-commit prints Passed with its notice
> hidden; gz check renders a demoted step ✓ and mints a reuse receipt with no demotion
> recorded; gz validate prints 'All validations passed' and JSON valid:true over demoted
> findings; the unit tier's zero-run refusal (exit 3) is demoted to ✓ Test, in CI too, since
> the marker is committed.

> Checks pass without checking what they guard: the authorship guard reads git config
> user.email, never the commits' author or committer; the ledger guard returns 0 when git
> fails; Behave, Test (changed), gz test --obpi and ARB step receipts trust exit 0 for a run of
> zero or all-skipped tests; closeout_proof finds zero briefs for ADR-0.0.16's ceremony;
> req-kind passes untagged REQs on unfinished briefs; commit-trailers skips every commit when
> git fails; zero findings from such a scope proves SUPPORT REQs at closeout.

> The authorship guard judges identity at commit time only: a commit created without the
> pre-commit hook (cherry-pick, rebase, a ref pushed from a clone without the hook) is never
> judged, and the pre-push gz check's Authorship policy step reads git var with no commit
> environment, so it judges config, not the pushed commits' authors.

These are the session's own observations, written before the run opened. They hold two
shapes the run must not fold together until a source shows they are one: a check that
**reports** a skip or demotion as a pass, and a check that **passes** without having read
what it guards.

## source · three sweeps of the enforcement surfaces

`docs/rnd/check-outcome-reporting/sources/sweep-git-hooks-2026-11-22.md`,
`sweep-validators-2026-11-22.md`, `sweep-ci-arb-runners-2026-11-22.md` · landed verbatim
2026-11-22

> pre-commit prints a hook's output only when it exits non-zero, modifies files, or runs
> verbose (`run.py:217`). No hook in the config sets `verbose`. So any stderr or stdout notice
> from a hook that exits 0 is NOT visible.

> The aggregate path's `✓ All validations passed (N scopes)` never says how many artifacts
> were checked, so no aggregate-path scope can tell "checked, clean" from "did not check".

> **"Did not run" is coded as exit 3.** `gz check` treats exit 3 as a policy breach, and while
> the hangar is open it demotes any exit-3 step to success. A test tier that ran nothing
> therefore passes `gz check --full` in CI today.

Three read-only subagents; 21 hook rows, 17 validator rows and 11 runner rows. Their claims
are a subagent's word until re-read. The session re-derived these by hand before the run
opened: the alarm switch's exit 0 (`src/gzkit/mx/alarms.py:49-51`, observed); the demoted
step rendered ✓ (`src/gzkit/commands/quality.py:212-219` and `:1165`, read); the reuse receipt
recording no demotion (`src/gzkit/check_fingerprint.py:176-199`, read);
`gz validate --hexagon-tests` printing "✓ All validations passed (1 scopes)", exit 0, over 143
stderr lines, and exit 3 under `GZKIT_MX_FULL_STRENGTH=1` (observed); the unit tier's zero-run
exit 3 demoted (`src/gzkit/quality.py:644-658`, read); the ledger guard and the authorship
guard (both reproduced, fixed and closed as #1339 and #1340).

## source · the canon on a demoted finding

`.gzkit/rules/mx-mode.md` § Honor the marker, rule version `1.17.0`, line 40-42 · read
2026-11-22

> **Both enforcement surfaces honor the marker (GHI #843).** Governance is enforced on two
> surfaces, and the hangar reaches both: `gz validate` scopes plus the `gz check` step layer,
> and the pre-commit guards (`gzkit.hooks.guards`). A demoted pre-commit finding is still
> printed, followed by an `[MX advisory]` line — advisory means non-grounding, never discarded.

`src/gzkit/hooks/guards.py`, `run_guards` docstring (read 2026-11-22):

> A demoted finding is ANNOUNCED, never discarded. Collecting findings and dropping them with
> nothing said is the complaint recorded on GHI #843 itself: an operator otherwise cannot tell
> a clean run from a hangar run.

Canon already rules what a demotion owes its reader: it is announced, never discarded, and a
reader must be able to tell a clean run from a demoted one. The sweeps show the announcement
going to output nobody sees (pre-commit hides a passing hook's output) and a ✓ or "Passed"
standing over it. By the operator's doctrine on correction and enhancement (`AGENTS.md`
§ Operator Doctrine: *"discovering that more is needed to fulfill the intent of a feature is
not an enhancement, it is a correction"*), the reporting half of the class is a correction to
a declared intent, not new design.

## source · the MX rulings this run does not re-open

`docs/rnd/contractor-kit.md`, entries *source · the operator on the MX system, 2026-10-26 to
2026-10-27* and *decision · the condition belongs to the repository* · read 2026-11-22

> report only, decide within #1273

> Ruled. Model question 1: does the non-operational condition belong to the repository or to
> one working copy? Options put: **A** the repository, so the marker stays committed and every
> clone, parallel session, worktree and CI is in the condition, with CI's full-strength run as
> #1263's report-only second job (recommended); … Operator: *"A"*.

The contractor-kit run also records, from its census (2026-10-26): *"The step demotion acts
only on exit code 3 … Steps that fail any other way still block"*, ruled a defect to fix and
filed as #1272. That CI runs demoted, and that its full-strength run reports without failing,
are settled rulings. This run takes them as given. Its subject is what a demoted, skipped or
vacuous check **reports**, and whether it checked at all, not whether demotion should exist.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | catalog, packages, orders and decision records | | | |
| 2 | GHI / direct fix | | | |
| 3 | chore | | | |
| 4 | control surface, rule, doc, skill, hook | | | |
| 5 | one-shot refactoring | | | |
| 6 | no action | | | |
| 7 | further research | | | |

## Close

**Challenge restated.**

**Frontier.**

**Review.**

**Sign-off.**

## What this record does not license

No ADR, OBPI, package, chore or rule is started by this run. #1339 and #1340 were fixed and
closed before the run opened, on the operator's direct go, and are sources here, not outcomes.
