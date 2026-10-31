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
4. **One runtime, with `kind` selecting the procedure.** `kind: delivery` serves the pipeline's stages and persona; `kind: repair` serves the kit's positions, procedures and refusals; dispatch, the bound, block and unblock, acceptance and locks are shared, and the boundary between the two procedures is tested. Put to the operator: A, one runtime; B, two runtimes over shared parts; C, two separate runtimes. Operator, verbatim: *"A"*. This settles the contractor-kit record's question 2.

The rulings on GHI #1200, carried here because its repair lands in tranche 1:

5. **#1200 is a direct fix, not ruled into `OBPI-0.35.0-18-dispatch-outcome-recording`** (operator, verbatim: *"a"*). The placement question that followed was withdrawn by ruling 1, so this ruling now binds the route and not the surface.
6. **At the bound there is no further repair cycle.** The unblock names one exit: a changed requirement or bounded claim, a hold, or a withdrawal. A changed requirement restarts the task's count; a hold or a withdrawal clears the block and restarts nothing. Operator, verbatim: *"a"*.
7. **The changed-requirement exit is usable once per requirement, per run.** Operator, verbatim: *"A"*.
8. **An escalation at the bound may carry an agent recommendation**, beside facts the runtime writes into the block: the task's cycle count, the refutations of the requirement and the exits already used. Operator, verbatim: *"a"*.
9. **The single-driver route splits by `kind`.** A `delivery` run may declare single-driver and records each fix cycle through the same verb, so the bound applies. A `repair` run cannot be single-driver, because nobody inspects their own work. The count sees only what is recorded, and the precomplete refusal of silent single-driver runs moves with the pipeline. Put to the operator: A, split by `kind`; B, removed everywhere; C, left as it is. Operator, verbatim: *"a"*.
10. **The exit baseline has one seam.** All code that reads history goes through a single alias module, the only code allowed OBPI ids or event names; `src`, tests, skills, rules and live docs read zero. The ledger, briefs, handoffs, rulings, passage logs and dated snapshots are exempt as history. Put to the operator: A, one seam; B, a declared exemption list; C, surface names only. Operator, verbatim: *"a"*.
11. **Tranche 2 splits by owner.** The operator and a working session move the pipeline itself: the delivery procedure, its stages, its persona and the pipeline skill. The rest of tranche 2 and all of tranche 3 run under the kit as repair packages. Put to the operator: A, split; B, everything under the kit; C, everything by the operator and a working session. Operator, verbatim: *"a"*.
12. **The exits fit the freeze rules** (amends rulings 6 and 7). The freeze lock keeps no exception, so a requirement cannot change inside a package. The exits at the bound are: **reopen**, the requirement changing through `gz catalog reopen`, this package closing and the operator initiating a new one; **departure**, a bounded claim recorded as a waiver through `gz wp change`, the REQ moving out by disposition and the package carrying on; **hold**, the block clearing with no repair dispatched; and **terminate**, the package closing through Gate 5. The once-only limit attaches to the requirement across its outcome's packages: a REQ reaching the bound again after a reopening has only departure, hold and terminate. Put to the operator: A, this mapping; B, an exception to the freeze lock; C, the count per package. Operator, verbatim: *"a"*.

## Starting measure

Measured 2026-10-31, a dated record. Counts of files that mention OBPI, not of machinery that must move: 374 source files (6,561 lines), 26 source files named for it, 532 test files, 109 feature files, 53 skills, 20 rules, 21 manpages and 111 lines of the `AGENTS.md` corpus. `gz obpi` carries 20 subverbs and `gz wp` carries 11, with 1 work-package record. History: 4,502 ledger rows on 975 OBPI ids, and 559 briefs.

## Tranches

**Tranche 1 — the runtime parts, before RO-12 lands.** The dispatch, block and unblock verbs on the work-package surface, and the other parts the kit reuses, each repaired as it moves: GHI #1200, #1206, #1208 and #1028. The successor to `gz obpi withdraw` lands here, accepting legacy ids, so RO-8's withdrawal does not hold `gz obpi` open.

**Tranche 2 — the pipeline, skills, rules and docs, before RO-13's retrofit.** The retrofit then puts its contracts on the surfaces that stay, and no control is done twice.

**Tranche 3 — `gz obpi` removed, last.** The exit item's baseline reads zero.

## #1200's design facts

A fix cycle is an Implementer dispatch that follows a review of the same task, since the Implementer's previous dispatch. A raw count of Implementer dispatches is wrong: Task 1 of `OBPI-0.35.0-15-pipeline-run-position` had four dispatches and one fix cycle.

Replayed over that run's ledger rows with the bound of `MAX_REVIEW_FIX_CYCLES`, the count refuses the `2026-10-11T23:35` dispatch that followed the first unblock, as #1200's acceptance (a) requires. With a changed-requirement exit taken at that first bound, Task 2's next refusal is the dispatch of `2026-10-12T09:20`. An earlier statement to the operator named the `07:38` block, which was not at the bound; ruling 7 was given with that figure in front of them.

## Settled from the record

- **A package's count is read over its whole history.** The dispatch channel reads whole history on purpose, because a relaunch must not discard credit (GHI #886), so a relaunch resets nothing. Ruling 12 carries the once-only limit across packages.
- **The refutation count is reliable, in reviews.** Read through `load_history`, not from receipts' truncated tails, `OBPI-0.35.0-15-pipeline-run-position` holds 55 reviews, 25 refuted, every refuted review carrying a mapped finding: REQ-0.35.0-15-02 13, -08 10, -09 2, -05 1. A round with two reviewers can add two, so the block states reviews, not rounds.
- **The same-root rule is scored advisory.** Comparing two rounds' weakest points is judgment, and ruling 7 now holds the mechanical part. #1200's acceptance (d) is met by the score in `docs/governance/advisory-rules-audit.md`, written when #1200 lands.
- **The other reused parts, by surface.** Move in tranche 1: #1198 and #1208 (dispatch), #1203, #1205 and #1209 (run position and markers), #1206 (the task fence), #1028 (Stage 4's bound) and #1185 (the airlock, which still targets a brief). #1194 sits in the ledger and names no OBPI surface, so it stays a direct fix in place. The cwd-escape guard has no issue yet; the contractor-kit record owes one through `ghi-author`.

## Open points

Each is put to the operator one at a time before tranche 1 is cut.

1. **The names.** The new `gz wp` verbs and ledger events; the contractor brief reserves new names for the operator. Put last, once the parts are known.
