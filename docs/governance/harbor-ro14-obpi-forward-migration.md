<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-14 specification — the forward migration from OBPI to work package

**2026-10-31. Status: scope, tranches and open points ruled; tranche 1 cut into acts; act 1 under rebuild after its independent review failed.** Operator: **g0**. Repair order of the [harbor pilotage contract](harbor-pilotage-candidate-2026-10-15.md), which holds the binding rulings.

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
<!-- gz-validate-skip: command-shape -->
12. **The exits fit the freeze rules** (amends rulings 6 and 7). The freeze lock keeps no exception, so a requirement cannot change inside a package. The exits at the bound are: **reopen**, the requirement changing through `gz catalog reopen`, this package closing and the operator initiating a new one; **departure**, a bounded claim recorded as a waiver through `gz wp change`, the REQ moving out by disposition and the package carrying on; **hold**, the block clearing with no repair dispatched; and **terminate**, the package closing through Gate 5. The once-only limit attaches to the requirement across its outcome's packages: a REQ reaching the bound again after a reopening has only departure, hold and terminate. Put to the operator: A, this mapping; B, an exception to the freeze lock; C, the count per package. Operator, verbatim: *"a"*.
<!-- gz-validate-skip: command-shape -->
13. **The names.** `gz wp dispatch`, `gz wp block`, `gz wp unblock` with `--exit reopen|departure|hold|terminate`, and `gz wp withdraw-legacy`; the events `work_package_dispatched`, `work_package_blocked`, `work_package_unblocked` and `legacy_unit_withdrawn`. Put to the operator: A, flat verbs with the existing event prefix; B, a `run` group; C, as A with the withdrawal on the catalog. Operator, verbatim: *"a"*.
14. **The bound counts against the frozen subject**, amending the task key of rulings 5 to 8: a REQ in the package's frozen baseline, or an issue the repair package carries. A caller's task number is refused as a key because a new number resets the count; `--task` is replaced by `--req` or `--issue`. Put to the operator: A, the frozen subject; B, one bound per package; C, declared task cards. Operator, verbatim: *"a"*.
15. **The count follows the REQ at its revision, across packages.** A new package at the same revision starts where the last stopped; a reopening changes the revision and starts clean. A REQ at the bound and already reopened once can only be departed from, held or terminated. Put to the operator: A, across packages; B, a new package starts clean; C, clean with the history shown. Operator, verbatim: *"a"*.

## Starting measure

Measured 2026-10-31, a dated record. Counts of files that mention OBPI, not of machinery that must move: 374 source files (6,561 lines), 26 source files named for it, 532 test files, 109 feature files, 53 skills, 20 rules, 21 manpages and 111 lines of the `AGENTS.md` corpus. `gz obpi` carries 20 subverbs and `gz wp` carries 11, with 1 work-package record. History: 4,502 ledger rows on 975 OBPI ids, and 559 briefs.

## Tranches

**Tranche 1 — the runtime parts, before RO-12 lands.** The dispatch, block and unblock verbs on the work-package surface, and the other parts the kit reuses, each repaired as it moves: GHI #1200, #1206, #1208 and #1028. The successor to `gz obpi withdraw` lands here, accepting legacy ids, so RO-8's withdrawal does not hold `gz obpi` open.

**Tranche 2 — the pipeline, skills, rules and docs, before RO-13's retrofit.** The retrofit then puts its contracts on the surfaces that stay, and no control is done twice.

**Tranche 3 — `gz obpi` removed, last.** The exit item's baseline reads zero.

## #1200's design facts

Every implementing dispatch after a subject's first review, or after its first single-driver dispatch, is a fix cycle. Several implementing dispatches may precede the first review: Task 1 of `OBPI-0.35.0-15-pipeline-run-position` had three before its review and one fix cycle after it. Repeating the Implementer after a review counts each time, so a run cannot buy a cycle by not reviewing.

Replayed over that run's ledger rows with the bound of `MAX_REVIEW_FIX_CYCLES`, the count refuses the `2026-10-11T23:35` dispatch that followed the first unblock, as #1200's acceptance (a) requires.

**Corrected 2026-10-31.** Two figures given to the operator were wrong. The `07:38` block was not at the bound, and the later figure of a `09:20` refusal relied on a restart inside a package, which ruling 12 removed. Ruling 7 was given with the first in front of them. The rulings do not depend on either figure; the `23:35` refusal is the one the replay proves.

## Settled from the record

- **A package's count is read over its whole history.** The dispatch channel reads whole history on purpose, because a relaunch must not discard credit (GHI #886), so a relaunch resets nothing. Ruling 12 carries the once-only limit across packages.
- **The refutation count is reliable, in reviews.** Read through `load_history`, not from receipts' truncated tails, `OBPI-0.35.0-15-pipeline-run-position` holds 55 reviews, 25 refuted, every refuted review carrying a mapped finding: REQ-0.35.0-15-02 13, -08 10, -09 2, -05 1. A round with two reviewers can add two, so the block states reviews, not rounds.
- **The same-root rule is scored advisory.** Comparing two rounds' weakest points is judgment, and ruling 7 now holds the mechanical part. #1200's acceptance (d) is met by the score in `docs/governance/advisory-rules-audit.md`, written when #1200 lands.
- **The other reused parts, by surface.** Move in tranche 1: #1198 and #1208 (dispatch), #1203, #1205 and #1209 (run position and markers), #1206 (the task fence), #1028 (Stage 4's bound) and #1185 (the airlock, which still targets a brief). #1194 sits in the ledger and names no OBPI surface, so it stays a direct fix in place. The cwd-escape guard has no issue yet; the contractor-kit record owes one through `ghi-author`.

## Tranche 1, cut into acts

1. **The bound.** `gz wp dispatch`, `block` and `unblock` with `gzkit.work_package_run` (#1200). The first build failed independent review on the routes rulings 14 and 15 close; rebuilt, not yet landed.
2. **Dispatch's defects.** #1198 and #1208, read against the new verb.
3. **Run position and markers.** #1203, #1205 and #1209.
4. **The fence and the stage bound.** #1206, and #1028 with its stop-and-ask boundary.
5. **Acceptance on the work package**, which gives `gz wp block` the refutation count ruling 8 requires.
6. **The airlock on the work package.** #1185.
<!-- gz-validate-skip: command-shape -->
7. **`gz wp withdraw-legacy`.**

## Mode contract

`gz wp dispatch`, `block` and `unblock` are on at the operational condition and at the hangar and drydock levels. They are ledger writers that read no marker, because a repair loop under safe mode is the case the bound exists for. MEL entry: not bypassable, no (M) or (O) limitation, no placard or deadline; accepted state, on. Self-test: `ledger_producer_probe` for each event, at the producer check's interval.

## Known limits of act 1

- The block carries no refutation count until act 5.
- A subject can take any number of reviews; only implementing dispatches are bounded.
- `reopen` names the act and is not checked against a reopening, because that verb lands with RO-5's tranche 6.
- The count sees only what is recorded.
- #1200 stays open: its exit condition has the pipeline's sentence name the mechanism, and the OBPI pipeline moves in tranche 2.
