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

## source · the population: 15 issues read, and the F2 family

`docs/rnd/check-outcome-reporting/sources/population-read-2026-11-22.md` (landed verbatim);
#919's lines re-read by the agent with `gh issue view 919` · read 2026-11-22

From #919 (open), its class of failure:

> **A two-valued verdict over a three-valued world: `caught` / `did not catch` / `could not
> observe`.**

From #919's cross-link comment:

> Common root: no channel separates "the thing under test is wrong" from "I could not test the
> thing", so the second is reported in the vocabulary of the first.

From #919, the ruling it has waited on:

> Open design question for the operator: whether an inconclusive control should **fail** the
> gate (safe, but a network blip blocks every push) or **warn and abstain** (push proceeds; an
> unobserved control is not evidence of enforcement).

From `docs/rnd/ghi-landscape-reorganization.md`, line 215:

> | F2 a gate reports green over a state it cannot see | 6 — #808, #919, #969, #983, #998,
> #1032 | The control passes, but the question it answers is not the one its consumers read it
> for |

15 of 15 listed issues were read in full, bodies and comments. The reader's tally: 5 report a
skip or demotion as a pass (R), 5 pass without reading their subject (P), 3 do both, 3 neither,
and #919 has R's mechanism with the opposite polarity: an unrun control reported as a FAIL. 8
are open. A further 7 open issues met in comments look like members (#1135, #1155, #1224,
#1266, #1289, #907, #1262); their bodies were not read, so their membership is a hypothesis.
The landscape run named F2 and ruled no disposition for it.

## source · the outcome rule gzkit already binds for one check

`.gzkit/rules/tests.md` § Red-Green-Refactor, *Mutation-sweep integrity (binding, GHI #963)*,
line 62 · read 2026-11-22

> A failing mutant run is NOT a kill. Report four outcomes: `killed` and `survived` are claims
> about the guard, `invalid` and `inconclusive` about the run.

gzkit already rules, for the mutation sweep alone, that a check's outcome separates claims
about its subject from claims about its run. #919 states the same split for the QC controls.
Nothing states it for every check.

## decision · one class, one outcome contract

Ruled. Question: is this one class with one outcome contract, or something else? Options put:
**A** one class, *a claim about the run is reported in the vocabulary of a claim about the
subject*, remedied by one outcome contract every check carries (passed and failed speak of the
subject; not run, demoted and not observed speak of the run), on every surface: exit code, ✓,
JSON, receipt, ledger row (recommended); **B** two classes, reporting and fail-open, routed
separately; **C** no model, each surface fixed as found. Operator, by selection: *"One class,
one contract (Rec.)"*.

- Both shapes the sweeps found are one mechanism. A skip or demotion shown as a pass (R), and
  a check passing over input it never read (P), each report a run-state as a subject-state.
  #919's unrun control reported as FAIL is the same collapse with the opposite polarity.
- The contract generalises what `tests.md` binds for the mutation sweep and what #919 names
  for the QC controls. It is not a new idea in gzkit, only a rule never stated for all checks.
- Under the operator's ruling against safe-mode exceptions, the contract holds in every mode.
  Demotion is one of its run-states, not a special display.

## decision · term: run-state, beside subject-state

The two halves of the contract need names a reader can hold. Taken from the sources' own
words: `tests.md`'s *"claims about the guard"* and *"about the run"*, and #919's *"the thing
under test is wrong"* against *"I could not test the thing"*. **Subject-state**: what a check
found about what it guards (passed, failed). **Run-state**: what happened to the check itself
(not run, demoted, not observed). _Avoid_: *skip* for the family, since a skip is one
run-state; *inconclusive* for the family, since `tests.md` uses it for one member. Held here as
a `decision` until the project glossary has a home (`rnd-discipline.md` § `term` and `insight`
are not entry kinds).

## decision · a run-state grounds at the check's own level

Ruled. Question: what should a run-state do to the gate? It also settles #919's open ruling.
Options put: **A** a run-state grounds exactly as the check's failure would, at the check's
declared level; outside the hangar an ERROR check that could not observe blocks (#919's *"fail
the gate"*), inside it the hangar demotes it like any finding and the report reads *demoted:
not observed*, never ✓ (recommended); **B** a run-state warns and never blocks (#919's *"warn
and abstain"*); **C** each control declares its run-state behaviour in its MEL entry. Operator,
by selection: *"Grounds at its own level (Rec.)"*.

- One rule in every mode: the hangar's demotion applies to a run-state as to any finding, so
  there is no safe-mode exception (the operator's ruling of 2026-11-22).
- An alarm switched off in the drydock is a run-state, *not run*, at its own level, demoted
  there, and reported as demoted. It no longer reads "Passed".
- The accepted cost is #919's: an ERROR check that cannot observe (an unreachable index, a
  missing tool) blocks outside the hangar until its environment is restored.
- #919's open ruling is answered by this entry.

**commissions:** 2 — #919 takes this ruling as its answer (a comment citing this record).

## source · the drydock's frozen work scope

`docs/governance/harbor-pilotage-candidate-2026-10-15.md` § Repair orders, the paragraph
amended 2026-10-29 · read 2026-11-22

> **The work scope is frozen at induction** (amended 2026-10-29, § Rulings of 2026-10-29): the
> orders are RP-0 to RP-13 as the table stood, with RP-14 and RP-15 added by the operator's
> amendment. A finding raised from then on is graded, not added: one that blocks return to
> service is worked under its owning order or a change order the operator issues; one that
> does not is a deferred finding, carried into civil rule with a named holder and a revisit
> condition, and never a new order.

The same table, RP-13's row: *"the two-way mode contract across every control: each control
onboards its MEL entry, takes the standby level from the central condition signal at its place
of call, and reports suitability for function through its built-in self-test."*

This run cannot propose a new repair package. The class is graded, then worked under its
owning order or deferred. RP-13 already carries the standby level taken *"at its place of
call"* and each control reporting *"suitability for function"*. That is the nearest existing
home of a run-state, though not of a report carried on every surface.

## decision · it blocks return to service, and RP-13 owns it through a change order

Ruled. Question: how is the outcome contract graded, and who owns it? Options put: **A** it
blocks return to service, since a sea trial read through false-green reports proves nothing;
RP-13 owns it through a change order the operator issues, the contract joining RP-13's
foundation tranche beside the MEL model and the place-of-call reader, and every surface
retrofitted with the controls; the existing members attach to RP-13 (recommended); **B** it
blocks return to service, each member worked under the order owning its surface as a direct GHI
fix, with no shared carrier; **C** a deferred finding carried into civil rule. Operator, by
selection: *"Blocks RTS; RP-13 (Rec.)"*.

- The change order is the operator's own act. RP-12 ruling 32 keeps it for the operator alone,
  gated on verbatim words. This run proposes it under disposition 1 and issues nothing.
- `gz mx exit` and the sea trial read the same reports, so the class has to close before return
  to service. #1271 (the exit re-runs the change scope, not `--full`) is a member and attaches
  with the rest.
- No new order is opened, as the frozen work scope requires.

**commissions:** 1 — a change order on RP-13 adding the outcome contract to its foundation
tranche, proposed for the operator to issue.

## decision · the questions confirmed

The operator had taken the recommended option on all three questions. Put as the skill
requires: is a question missing that would change a disposition? Operator, by selection:
*"Right questions, continue"*.

## decision · the unfiled findings are filed by mechanism

Ruled. Question: how are the roughly 30 unfiled sweep findings filed, each attaching to RP-13's
change order? Options put: **A** three new GHIs through `ghi-author`, one per mechanism: a
run-state rendered as a pass on the reporting surfaces; a vacuous population or proxy passing a
validator, the closeout amplifier included; the pre-push range. The runner rows go to #1154 and
the missing-file rows to #1224 as evidence comments, each linked to the change order
(recommended). **B** one GHI per sweep row. **C** none now, the change order carrying the
landed reports as evidence. Operator, by selection: *"By mechanism (Rec.)"*.

- Each new GHI runs `ghi-author`'s Step 0 before it is filed. A mechanism an open issue already
  carries joins that issue as a comment instead.
- The three mechanisms are cuts of the one class (*one class, one outcome contract*). Their
  `## Related` sections name the class and this record once, not every sibling.

**commissions:** 2 — three GHIs by mechanism and evidence comments on #1154 and #1224, on the
operator's go on this row.

## decision · no rule text until RP-13 lands it with its witness

Ruled. Question: where does the outcome contract's binding text live? Options put: **A** a
fourth clause in `.gzkit/rules/mode-contract.md`, advisory until RP-13's witness lands
(recommended); **B** a new rule file; **C** no text now, RP-13's change order landing the clause
with its witness in one commit. Operator, by selection: *"No text until RP-13"*.

- The operator declined the recommendation. Doctrine and its mechanism arrive together, so no
  rule states a contract nothing yet enforces (`AGENTS.md` § Make LLM stochastic vibes inert:
  *"Change doctrine only with a recorded witness"*).
- The accepted cost: a control written before RP-13's change order lands is not told the
  contract by a rule. This record, the change order and the three GHIs carry it until then.
- Row 4 is therefore not pursued here. Its text is part of what the RP-13 change order lands.

## decision · rows 3, 5 and 6, recorded with their reasons

Agent's dispositions, each within the skill's authority for its row:

- **Row 3, chore: not pursued.** A periodic sweep for false-green sites would report the class
  without removing its cause, and RP-13's shrink-only baseline, *"closed at zero"*
  (`.gzkit/rules/mode-contract.md`), is the planned witness for every control. Revisit if RP-13
  lands and run-states still escape on a surface its witness does not read.
- **Row 5, one-shot refactoring: not pursued.** Replacing `QualityResult.success: bool` and the
  other two-valued carriers with the outcome type is the retrofit RP-13's change order carries
  (row 1). A second program for the same edit would be a parallel model
  (`.gzkit/rules/hexagonal-architecture.md` rule 8).
- **Row 6, no action: commissioned, as a record.** The settled MX rulings are not re-opened: the
  condition belongs to the repository, so CI runs demoted, and CI's full-strength run reports
  without failing (*"report only, decide within #1273"*). Under this run's contract, a demotion
  in CI reads as *demoted* rather than ✓. The documented adopter-absence skips (no
  `mkdocs.yml`, no canary registry) stay deliberate; under the contract they report *not run*
  instead of a pass.

## decision · the vocabulary research waits for RP-13

Ruled. Question put: should a follow-on R&D run read the outcome vocabularies of established
reporters (JUnit XML, TAP, SARIF) before RP-13 designs the type? Options: **A** open it before
RP-13 (recommended); **B** not pursued. The operator answered neither, verbatim: *"I am
interested in those specifications and wonder if they are compliant with some standard. Why
would we not wait for RP-13? I had already expressed a desire to do so"*.

- The question re-put a matter already settled (*no rule text until RP-13 lands it with its
  witness*). The correction is recorded as insight scope `rnd-check-outcome-reporting`.
- Row 7 names the run and places it with RP-13. **The outcome vocabularies of established check
  reporters, and whether each is held to a standard**, is opened when RP-13's change order is
  planned, by the operator. It is opened by this run's *run-state* term and by the operator's
  interest in standards compliance.
- The agent's recollection, unread and so a hypothesis only: SARIF v2.1.0 is an OASIS Standard;
  TAP 14 is a community specification; JUnit XML has no formal standard, only competing
  schemas. That run reads each from its own text before any of it is relied on.

**commissions:** 7 — the reporter-vocabulary run, opened when RP-13's change order is planned.

---

## Disposition map

| # | Disposition | State | What | Reason |
|---|---|---|---|---|
| 1 | catalog, packages, orders and decision records | commissioned | A change order on RP-13 adding the outcome contract to its foundation tranche: every check reports a subject-state (passed, failed) or a run-state (not run, demoted, not observed); a run-state grounds at the check's own level; every surface (exit code, ✓, JSON, receipt, ledger row) carries it; the rule clause lands with its witness. The class's open members attach to RP-13. Proposed only; the operator issues it (RP-12 ruling 32). | *it blocks return to service, and RP-13 owns it through a change order* |
| 2 | GHI / direct fix | commissioned | Three GHIs through `ghi-author`, one per mechanism: a run-state rendered as a pass on the reporting surfaces; a vacuous population or proxy passing a validator, the closeout amplifier included; the pre-push range. Evidence comments on #1154 (runner rows) and #1224 (missing-file rows), and a comment on #919 citing its answered ruling. Each linked to the RP-13 change order. Awaits the operator's go on this row. | *the unfiled findings are filed by mechanism*; *a run-state grounds at the check's own level* |
| 3 | chore | not pursued | A periodic false-green sweep. | It reports the class without removing its cause; RP-13's shrink-only baseline is the planned witness. Revisit if run-states still escape on a surface RP-13's witness does not read. |
| 4 | control surface, rule, doc, skill, hook | not pursued | The contract's rule clause. | Operator: *"No text until RP-13"*. The clause lands with its witness in the RP-13 change order (row 1). |
| 5 | one-shot refactoring | not pursued | Replacing two-valued outcome carriers (`QualityResult.success: bool` and kin) with the outcome type. | That is the retrofit row 1 carries; a second program would be a parallel model. |
| 6 | no action | commissioned | The settled MX rulings stand: the condition belongs to the repository, so CI runs demoted, and CI's full-strength run reports without failing. The documented adopter-absence skips stay deliberate. | Settled by the operator (contractor-kit record; *"report only, decide within #1273"*). Under the contract both read as *demoted* or *not run*, never ✓. |
| 7 | further research | commissioned | **The outcome vocabularies of established check reporters (JUnit XML, TAP, SARIF), and whether each is held to a standard**, read from their texts. | Opened by the *run-state* term and the operator's interest in standards compliance; the operator opens it when RP-13's change order is planned (*the vocabulary research waits for RP-13*). |

## Close

**Challenge restated.** The run opened on *why does a check that did not run, or whose failure
was demoted, keep reporting as passed?* Restated at the close, on purpose: gzkit's checks carry
their outcome on two-valued channels (an exit code, a ✓, `success: bool`, `valid: true`), so a
claim about the run is reported in the vocabulary of a claim about the subject, in either
polarity. The class closes when every check reports a subject-state or a run-state, with a
run-state grounding at the check's own level, on every surface. RP-13 carries that before
return to service, under a change order the operator issues.

**Frontier.** Empty. The core model, the run-state's consequence, the grade and owner, the
filing shape, the rule text's timing and the follow-on research are each ruled; rows 3, 5 and 6
are recorded with their reasons.

**Review.** `docs/rnd/check-outcome-reporting/review.md`. Awaiting the operator's words that
they have read it.

**Sign-off.**

## What this record does not license

No ADR, OBPI, package, chore or rule is started by this run. #1339 and #1340 were fixed and
closed before the run opened, on the operator's direct go, and are sources here, not outcomes.
