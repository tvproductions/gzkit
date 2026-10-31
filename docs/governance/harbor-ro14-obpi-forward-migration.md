<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-14 specification — the forward migration from OBPI to work package

**2026-10-31. Status: scope and tranches ruled; the open points below are unruled, and tranche 1 waits on them.** Operator: **g0**. Repair order of the [harbor pilotage contract](harbor-pilotage-candidate-2026-10-15.md), which holds the binding rulings.

## Scope

Everything live moves from OBPI to the work package: the verbs, the pipeline, the skills, the rules, the docs and new event names. `gz obpi` is removed. History stays as read-only record, readable through the alias layer: old ledger rows and briefs stay as written, and carried attestations are not re-attested.

The pipeline is carried forward, not replaced. The contractor-kit record holds that the kit must leave the pipeline skill, its personas and its runtime no worse.

## Rulings

1. **Nothing is retained in OBPI** (operator, verbatim: *"we shouldn't be retaining anything in obpi, it all needs to forward migrate to wp, discuss"*).
2. **History stays as read-only record.** Put to the operator: A, everything live moves and history stays; B, A plus a work-package record wrapping each historical brief; C, full conversion of history. Operator, verbatim: *"A"*.
3. **The migration is its own order, by contract amendment, in three tranches, with an exit item.** Put to the operator: A, a new order; B, a change order on RO-5; C, a change order on RO-12. Operator, verbatim: *"a"*.

The rulings on GHI #1200, carried here because its repair lands in tranche 1:

4. **#1200 is a direct fix, not ruled into `OBPI-0.35.0-18-dispatch-outcome-recording`** (operator, verbatim: *"a"*). The placement question that followed was withdrawn by ruling 1, so this ruling now binds the route and not the surface.
5. **At the bound there is no further repair cycle.** The unblock names one exit: a changed requirement or bounded claim, a hold, or a withdrawal. A changed requirement restarts the task's count; a hold or a withdrawal clears the block and restarts nothing. Operator, verbatim: *"a"*.
6. **The changed-requirement exit is usable once per requirement, per run.** Operator, verbatim: *"A"*.
7. **An escalation at the bound may carry an agent recommendation**, beside facts the runtime writes into the block: the task's cycle count, the refutations of the requirement and the exits already used. Operator, verbatim: *"a"*.

## Starting measure

Measured 2026-10-31, a dated record. Counts of files that mention OBPI, not of machinery that must move: 374 source files (6,561 lines), 26 source files named for it, 532 test files, 109 feature files, 53 skills, 20 rules, 21 manpages and 111 lines of the `AGENTS.md` corpus. `gz obpi` carries 20 subverbs and `gz wp` carries 11, with 1 work-package record. History: 4,502 ledger rows on 975 OBPI ids, and 559 briefs.

## Tranches

**Tranche 1 — the runtime parts, before RO-12 lands.** The dispatch, block and unblock verbs on the work-package surface, and the other parts the kit reuses, each repaired as it moves: GHI #1200, #1206, #1208 and #1028. The successor to `gz obpi withdraw` lands here, accepting legacy ids, so RO-8's withdrawal does not hold `gz obpi` open.

**Tranche 2 — the pipeline, skills, rules and docs, before RO-13's retrofit.** The retrofit then puts its contracts on the surfaces that stay, and no control is done twice.

**Tranche 3 — `gz obpi` removed, last.** The exit item's baseline reads zero.

## #1200's design facts

A fix cycle is an Implementer dispatch that follows a review of the same task, since the Implementer's previous dispatch. A raw count of Implementer dispatches is wrong: Task 1 of `OBPI-0.35.0-15-pipeline-run-position` had four dispatches and one fix cycle.

Replayed over that run's ledger rows with the bound of `MAX_REVIEW_FIX_CYCLES`, the count refuses the `2026-10-11T23:35` dispatch that followed the first unblock, as #1200's acceptance (a) requires. With a changed-requirement exit taken at that first bound, Task 2's next refusal is the dispatch of `2026-10-12T09:20`. An earlier statement to the operator named the `07:38` block, which was not at the bound; ruling 6 was given with that figure in front of them.

## Open points

Each is put to the operator one at a time before tranche 1 is cut.

1. **One runtime or two.** Whether the kit is the repair mode of one work-package pipeline covering `kind: delivery` and `kind: repair`, or a separate runner beside it. The contractor-kit record's question 2 was left open (*"inclined to your 'C'"*).
2. **The names.** The new `gz wp` verbs and ledger events; the contractor brief reserves new names for the operator.
3. **What a run is.** The dispatch channel reads an OBPI's whole history on purpose, because a relaunch must not discard credit (GHI #886). Ruling 6's *"per run"* needs the same reading on a work package, or a relaunch would reset the bound.
4. **The refutation count.** Reviews are held as receipts in `acceptance_recorded` rows. Whether they yield a reliable count per requirement is unverified.
5. **The single-driver route.** A declared single-driver run records no dispatch rows, so the count sees no cycles.
6. **What the exit baseline counts.** The readers of history must still read OBPI ids and event names, so the alias layer and its legacy readers need a declared exemption, or *"zero"* cannot be reached.
7. **The other reused parts.** RO-12's row lists further defects (#1198, #1203, #1205, #1194, #1209, #1185 and a cwd-escape guard). Which move in tranche 1 is unread.
8. **#1200's same-root rule.** Its acceptance (d) asks for a witness or an advisory score for the rule at `.gzkit/skills/gz-obpi-pipeline/references/stage-4-present-evidence.md:150`.
