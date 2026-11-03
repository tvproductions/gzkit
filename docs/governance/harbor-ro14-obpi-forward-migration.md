<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RP-14 specification — the forward migration from OBPI to work package

> Named `RO-14` until 2026-11-03; `RP-14` replaces it in live text and `RO-14` stays its alias (contract § Rulings of 2026-11-03). The dated rulings below keep the name they were written with.


**2026-10-31. Status: scope, tranches and open points ruled; tranche 1 cut into acts; acts 1 to 7 landed; tranche 1 is complete.** Operator: **g0**. Repair order of the [harbor pilotage contract](harbor-pilotage-candidate-2026-10-15.md), which holds the binding rulings.

**Amended 2026-11-03** (contract § Rulings of 2026-11-03, operator, verbatim: *"the obpi to work package alignment is right on. exactly ==> "RO-14's migration really runs from OBPI to work order.""*, and *"work package is the mADR successor, the WO is the OBPI successor"*; `docs/rnd/repair-work-organization.md`): the forward migration runs from the OBPI to the **work order**, its successor; the work package succeeds the mADR. Tranche 1's landed acts stand on the work-package surface; tranches 2 and 3 take the work order as the destination once RP-12 lands its record.

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
16. **What counts as a fix cycle.** A subject's first implementing dispatch is free. After it, any review anywhere in the package arms every subject already started, and each later implementing dispatch on an armed subject counts. Put to the operator: A, this definition; B, a review required on each subject; C, one cap per package. Operator, verbatim: *"a"*.
17. **A hold stops only the subjects at the bound.** Other subjects of the package continue, a held subject stays open to a later exit, and `terminate` is the full stop. Put to the operator: A, the subjects at the bound; B, the whole package until lifted; C, a fifth exit. Operator, verbatim: *"a"*.

The ruling on run position, put at act 3:

18. **A work package's run position is a read of the rows its verbs already book.** No position event: `work_package_dispatched` is the successor of the transition row #1208 protects, and the position is replayed from the package's ledger rows. `gz wp runs` lists every run in flight, answering #1203, and `gz wp show` carries the position. A, this reading; B, a new position event with a stage table per `kind`; C, A now and a stage record at tranche 2. Operator, by selection: *"A: Read existing rows (Recommended)"*, on the statement that #1205 and #1209 are repaired in place.

The ruling at act 5's close:

19. **`terminate` is open on any block** (amends ruling 12). The review-round limit can stop a package with no subject at the fix-cycle bound, where ruling 12's exits did not reach, so the full stop of ruling 17 is the operator's on every block; the other three exits stay at the bound. Put to the operator: keep it on any block; narrow it to the bound and the round limit; or open all four exits at the limit. Operator, verbatim: *"ok"*, to the recommendation to keep it.

20. **Past the round limit, only an unblock restarts the count.** `human-review` refuses there and names `gz wp block`, so every ruling at the limit follows the runtime's facts and no route walks past it. Operator, verbatim: *"yes"*, to the recommendation.

## Starting measure

Measured 2026-10-31, a dated record. Counts of files that mention OBPI, not of machinery that must move: 374 source files (6,561 lines), 26 source files named for it, 532 test files, 109 feature files, 53 skills, 20 rules, 21 manpages and 111 lines of the `AGENTS.md` corpus. `gz obpi` carries 20 subverbs and `gz wp` carries 11, with 1 work-package record. History: 4,502 ledger rows on 975 OBPI ids, and 559 briefs.

## Tranches

**Tranche 1 — the runtime parts, before RO-12 lands.** The dispatch, block and unblock verbs on the work-package surface, and the other parts the kit reuses, each repaired as it moves: GHI #1200, #1206, #1208 and #1028. The successor to `gz obpi withdraw` lands here, accepting legacy ids, so RO-8's withdrawal does not hold `gz obpi` open.

**Tranche 2 — the pipeline, skills, rules and docs, before RO-13's retrofit.** The retrofit then puts its contracts on the surfaces that stay, and no control is done twice.

**Tranche 3 — `gz obpi` removed, last.** The exit item's baseline reads zero.

## #1200's design facts

Ruling 16 defines the count. Several implementing dispatches may precede a subject's first review: Task 1 of `OBPI-0.35.0-15-pipeline-run-position` had three before its review and one fix cycle after it. Repeating the Implementer after a review counts each time, so a relaunch after a crash spends a cycle. A review arms every subject its package has started, and a review of a subject arms it in any package (the agent's reading of ruling 15, tightening the bound, stated to the operator 2026-10-31), so splitting reviews from fixes on true labels buys nothing.

Replayed over that run's ledger rows with the bound of `MAX_REVIEW_FIX_CYCLES`, the count refuses the `2026-10-11T23:35` dispatch that followed the first unblock, as #1200's acceptance (a) requires.

**Corrected 2026-10-31.** An interim build counted every implementing dispatch from a subject's own first review; that definition was the agent's, and the second independent review showed it left an unbounded route through a sibling subject. Ruling 16 replaced it. Two figures given to the operator were wrong. The `07:38` block was not at the bound, and the later figure of a `09:20` refusal relied on a restart inside a package, which ruling 12 removed. Ruling 7 was given with the first in front of them. The rulings do not depend on either figure; the `23:35` refusal is the one the replay proves.

## Settled from the record

- **A package's count is read over its whole history.** The dispatch channel reads whole history on purpose, because a relaunch must not discard credit (GHI #886), so a relaunch resets nothing. Ruling 12 carries the once-only limit across packages.
- **The refutation count is reliable, in reviews.** Read through `load_history`, not from receipts' truncated tails, `OBPI-0.35.0-15-pipeline-run-position` holds 55 reviews, 25 refuted, every refuted review carrying a mapped finding: REQ-0.35.0-15-02 13, -08 10, -09 2, -05 1. A round with two reviewers can add two, so the block states reviews, not rounds.
- **The same-root rule is scored advisory.** Comparing two rounds' weakest points is judgment, and ruling 7 now holds the mechanical part. #1200's acceptance (d) is met by the score in `docs/governance/advisory-rules-audit.md`, written when #1200 lands.
- **The other reused parts, by surface.** Move in tranche 1: #1198 and #1208 (dispatch), #1203, #1205 and #1209 (run position and markers), #1206 (the task fence), #1028 (Stage 4's bound) and #1185 (the airlock, which still targets a brief). #1194 sits in the ledger and names no OBPI surface, so it stays a direct fix in place. The cwd-escape guard is #1296.

## Tranche 1, cut into acts

1. **The bound.** `gz wp dispatch`, `block` and `unblock` with `gzkit.work_package_run` (#1200). Three builds failed independent review; the routes are closed by rulings 14 to 17 and a same-subject arming clause; the fourth passed and landed.
2. **Dispatch's defects.** #1198 and #1208, read against the new verb. See § Act 2's reading.
3. **Run position and markers.** #1203, #1205 and #1209, and the half of #1208 that act 2 leaves open.
4. **The fence.** #1206, landed. #1028 moved to act 5 (operator, by selection: *"Lift, fold into act 5 (Recommended)"*).
5. **Acceptance on the work package**, which gives `gz wp block` the refutation count ruling 8 requires, and #1028's remainder: a reachable exit and a runtime bound for review rounds, at the ruled N=2, with its stop-and-ask boundary.
6. **The airlock on the work package.** #1185.
7. **`gz wp withdraw-legacy`.**

## Act 7's reading

**`gz wp withdraw-legacy` is `gz obpi withdraw`'s successor, at full parity.** One rule, `gzkit.legacy_units`, serves both verbs until `gz obpi` is removed, so they cannot differ on what may be withdrawn: the model's declared transitions, a required human witness, a dry run. `legacy_unit_withdrawn` joins `obpi_withdrawn` in `WITHDRAWN_EVENTS`, which the artifact graph, run position, the closeout proof and the park replay read, so a unit withdrawn by either verb reads as withdrawn to all of them. It adds a machine-readable `--json` and refuses a blank `--reason`, which `gz obpi withdraw` does not.

Limits. `--attestor` is a typed name, as on every human-act verb. RO-8 names where a brief's REQs went in `--reason`, in prose, because the catalog REQs do not exist yet. `gz obpi withdraw` itself leaves with tranche 3.

**Mode contract.** The refusals are on at the operational condition and at both standby levels, reading no marker. MEL: (M) none, the recovery is the refusal's own text; no (O) limitation, placard or restore deadline; self-test `tests/commands/test_wp_withdraw_legacy.py`, every change that touches it; accepted state, on.

## Act 6's reading

Three rulings, put to the operator on 2026-11-01 with `modules` not yet landed and #1185's attribution question open:

21. **A repair package declares its footprint.** It has no outcome to read one from, so `modules` lands on the work-package record; a delivery package reads its outcome's, and until RO-11 tranche 2 lands that field its exit reports `undeclared`. Put to the operator: A, repair declares; B, pull the outcome's field forward as well; C, hold the act until RO-11; D, derive from the issues. Operator, by selection: *"Repair declares (Recommended)"*.
22. **A commit is the package's when its `Task:` trailer starts with the lowercased package id.** Anything uncommitted counts too. The trailer set is closed, so a `Transit:` trailer was never an option. Put to the operator: A, the trailer; B, a ledger time window; C, the working tree alone. Operator, by selection: *"Task trailer (Recommended)"*.
23. **`gz wp accept` refuses a file outside a declared footprint.** The airlock still only reports, as doctrine requires; the refusal is the same finding's at `gz obpi complete` (#1181), carried forward under ruling 1. An undeclared footprint is reported and not refused. Put to the operator with the obligation, the defect and the false-refusal cost: A, refuse at accept; B, report only; C, refuse at close. Operator, by selection: *"Refuse at accept (Recommended)"*.

24. **A repair package is held to the brief's standard at freeze** (amends ruling 23 for repair packages). Operator, verbatim: *"recall that the objective is near-parity (if not full) for a wp and an obpi."* A brief must carry valid Allowed Paths, so `gz wp freeze` refuses a repair package with no `modules` and the same check holds a module against vendor mirrors and absent paths. Put to the operator: A, hold at freeze; B, check paths only; C, leave as ruled. Operator, by selection: *"Hold at freeze (Recommended)"*.

**One primitive, two declarers.** A brief and a package each supply a `TransitSlice`, and `enter_slice` and `exit_slice` run over it, so the doors do not fork (`ADR-0.33.0` § Boundary Invariants 3). `gz wp commence` and `gz wp accept` cross the airlock themselves, because #1185's other half was an exit nothing reached. A change order with `--module` moves the footprint; no other rung does, since scope is the operator's and a change order keeps what it supersedes. `undeclared` and `unobserved` are verdicts of their own, because `clean` claims a comparison that did not run. Independent review refuted the first build: a declared package whose changes could not be read exited clean, a rename hid the path it left, and the footprint was read from a store file the refusal exempts. The freeze now books the footprint and the ledger is what is read, as the fence reads no catalog; renames and non-ASCII paths are read whole, which also corrects `collect_changed_files` at the brief door. The event seals `changed_files`, as a completion receipt does. Review refuted the repair too: the bad-path recovery could not work, because a change order only added, which stranded a package; `?*` covered the tree past a character test; a store edit made before the freeze was sealed by it; the accept recovery failed for a file moved away; a revert was offered that could not clear a committed file; and two tests passed with their guards removed. A change order now drops a path before the freeze, `gz wp new` takes the path check, coverage is tested by matching a path nobody declares, the freeze runs the store's rule, and a path the package changed may be added though it is gone. A revert is no recovery for a committed file, which differs from `gz obpi complete`, whose comparison reads only the working tree.

The third review, the last the bound allows, refuted that too, and two findings were confirmed by running them: `*.*` and `s*` passed the coverage probe yet reach nearly every file, and a committed vendor mirror could not be accepted by the printed recovery. Put to the operator as an exit: fix the two and land; fix and review again; land as it stands; hold. Operator, by selection: *"Fix the two, land (Recommended)"*. A module now needs a literal first segment, a rule about the module that replaces a sample of what it matches, and a generated mirror of a file inside the footprint follows that file. **This last repair had no independent review.**

Limits. Parity with the OBPI's scope controls stands as follows: required and checked paths at freeze (ruling 24), the refusal at acceptance, the sealed file list, and both airlock edges. `gz obpi precomplete`'s warning before attestation has no separate verb because `gz wp accept` already falls before Gate 5. A package has no CREATE marker, so a new file is declared by its parent directory. A delivery package reads `undeclared` until the outcome's `modules` land. A commit carrying another trailer is unseen, so package work under the wrong trailer escapes the comparison; that follows ruling 22 and `observed_commits` is what shows it. The route around the refusal through `--approver operator`, and through a block and `--exit terminate`, rests on a typed name, as every human-act verb's does, and no code tells the operator from an agent. The ontology holds no work-package node, so reach is empty and the slice is compared by path alone: the record's repair D5, which reads *a transit whose reach exceeds the contract's modules is refused*, is met by the refusal at acceptance and not by the airlock, which operator doctrine holds is not a verification gate. #1185 stays open: its exit condition names one outcome at a real package completion, and no package has run since this landed, so the first real package or the sea trial supplies it.

**Mode contract.** The refusal is on at the operational condition and at both standby levels, reading no marker, as the acceptance gate does; the bookings refuse nothing and are on at all three. MEL: (M) none, the governed recovery is the refusal's own next step; no (O) limitation, placard or restore deadline; self-test `tests/commands/test_wp_airlock.py`, every change that touches it; accepted state, on.

## Act 5's reading

Independent review refuted two builds. The first refused truthful findings at import and dead-ended the departure exit. The second could not prove a catalog REQ at all and repaired departure only for a REQ with no history. The third read of the repair bound found a block writing zero for a departed REQ's refutations; put to the operator as an exit: fix the count and land; land as it stands; or hold. Operator, by selection: *"Fix the count, land (Recommended)"*.

**Acceptance moves to the work package by adapting the pipeline.** Operator, verbatim: *"we will adapt, as much as possible, the current gz-obpi-pipeline"*. A package supplies the contract a brief supplies, so proofs, reviews, closures and readiness run unchanged through the same store and reducer, and `gz wp acceptance` reaches them. A delivery package owes its frozen REQs, less any a `departure` exit moved out (ruling 12); a repair package owes one obligation per carried issue, named as the bound names it. An issue or a catalog REQ has no `@covers` scan, so its proof binds by killing the named mutants. The contract holds the whole record but its evidence.

**`gz wp accept` refuses until the reducer reads ready**, as the pipeline's completion does. A package stopped by an exit is excused: it claims no delivery and closes through Gate 5 (ruling 12), and requiring proof would leave it fenced for good. Unless its acceptance reads ready, it cannot then close as `proceed`.

**#1028's remainder lands here.** A package gets three adversarial rounds with a mapped finding, the first and the ruled N=2 follow-ups, the limit being one more than the fix-cycle bound. A review is recorded past the limit, so a truthful finding is never lost: the bound stands at `gz wp dispatch`, `gz wp accept` and `human-review`, which refuse past the limit and name `gz wp block`, the exit #1028 found unreachable. A mapped finding counts and the verdict token does not, because a mapped finding is what blocks readiness. The operator's ruling through `gz wp unblock` restarts the count, after the block has shown the facts, and the fix-cycle bound still holds any repair. `gz wp block` carries the refutations per subject, which ruling 8 required, written by the runtime from the whole replay, so a departed REQ's refutations stay facts; a malformed acceptance row costs the count, said in the reason, and not the block; a line the ledger itself cannot read stops every verb. The pipeline skill's Stage 4 text moves with the pipeline in tranche 2.

Limits. The count reads one package, though fix cycles follow a REQ across packages (ruling 15). It sees only imported receipts. Parallel adversarial reviews spend a round each. A package whose every REQ departed owes nothing and reads unready, so it leaves by `terminate`, which the operator now holds on any block: the limit can stop a package with no subject at the fix-cycle bound, which ruling 12's exits did not reach. A departed REQ's proofs and findings stay on the ledger and leave the package's acceptance. A malformed review row counts no round, so it never stops a dispatch, and `gz wp accept` refuses that history. Catalog `STRUCTURAL-FENCE` REQs cannot yet be proved, because their resolver reads the legacy id grammar, and a catalog `SUPPORT` REQ proves only through a witness clause in its statement; no catalog REQ has those kinds. An issue is always a `BEHAVIOR` obligation, so a docs or chore issue has no honest proof and needs a discrepancy until repair kinds are ruled. The reconcile-receipt and plan-audit gates stay with tranche 2.

**Mode contract.** The gate and the round bound are on at the operational condition and at both standby levels: they read no marker, and a review loop under safe mode is the case they exist for. MEL: (M) none, the governed recovery is the refusal's own next step; no (O) limitation, placard or restore deadline; self-test `tests/commands/test_wp_acceptance.py`, every change that touches it; accepted state, on.

## Act 4's reading

**#1206 is repaired on the work-package surface.** Put to the operator: a fence on the surface; the launcher's gates added to `gz task start`; or closing on the dispatch's own refusal. Operator, by selection: *"Fence on the WP surface (Recommended)"*. The fence read only the OBPI marker, so a write without a dispatch went unrefused in any state `gz wp dispatch` refuses. `gzkit.work_package_fence` holds the rule for the hook and the pre-commit guard, from the ledger alone. It fences a package that is blocked, accepted or stopped by an exit, across the whole tree, because a package names no paths. A ledger that cannot be read fences the tree.

Independent review refuted three builds, and the repair bound was spent on the third. The first missed the stopped state and failed open on a ledger fault. The second read a subject at the bound from its own package only, and printed recovery commands that could not run. The third showed that a fence at the bound refuses the last fix cycle dispatch admits, because dispatch refuses past the bound and the ledger shows the same rows while that cycle runs and after it ends. Put to the operator as an exit: drop the bound state and land; land the two ruled states only; or hold. Operator, by selection: *"Drop bound state, land (Recommended)"*.

Limits. A subject at the bound and a held subject are unfenced, since neither can be told from admitted work; `gz wp dispatch` still refuses both. Before commencement a package is fenced only while it is blocked or stopped. The `reopen` exit shares `terminate`'s constant but no fence test reaches it, because that needs catalog REQs. The hook binds edit tools only, so the commit guard is the arm that binds. The reconcile-receipt and plan-audit gates have no work-package equivalent yet and stay with tranche 2.

**Mode contract.** Commit arm: on at the operational condition and at both standby levels, under the `post-authoring-src-commits` pin. Write arm: on at the operational condition, advisory at both standby levels, under the `pipeline-gate` demotion. MEL: (M) none, the governed recovery is the refusal's own next step; (O) a write through a shell is seen at the commit; placard, the demotion notice; restore at the exit re-run; self-test `tests/commands/test_wp_fence.py`, every change that touches it; accepted state, no package fenced.

## Act 2's reading

**#1198 is repaired at its cause, not on `gz obpi`.** `cli.main` discarded every handler's returned code. It now carries a returned int to the shell, so the class is closed for every verb, `gz wp` included. Measured over the 134 handlers the parsers name, two lost a refusal: `gz obpi dispatch` and `gz obpi adversary-workspace`. The two adapters that worked around the discard, for `gz arb` and `gz obpi acceptance`, went with it.

**#1208 is half answered.** `gz wp dispatch` reads and writes no marker, so a marker fault cannot cost it its row; `test_a_marker_fault_costs_the_dispatch_no_row` holds that. The work-package surface has no run position yet, so the transition row #1208 protects has no successor until act 3, and #1208 stays open for it. Act 3 records position ledger first, with no cache in front of it.

**`gz obpi dispatch` is not repaired.** `record_dispatch` keeps its uncontained cache refresh, the command keeps printing refusals on stdout, and `--role` still records and exits 0 on a marker file naming another OBPI, which `--single-driver` refuses. The contract moved these repairs to tranche 1 because a repair to `gz obpi` would guard no run (§ Rulings of 2026-10-31); tranche 3 removes the surface. A repair of `record_dispatch` was built and withdrawn in this act, before landing, when that sentence was read.

## Act 3's reading

**A run's position is replayed, not recorded twice (ruling 18).** The row that books a dispatch is the row that records the boundary, so no cache stands in front of it and there is no second row to lose. A stage table per `kind` waits for tranche 2 and RO-12, which define the procedures it would name; recording one here would have fixed them first. A run is in flight from `commenced` until `closed`, so `accepted`, awaiting Gate 5, is still reported, as a pipeline run stayed in flight until its completion receipt.

**#1203 and #1208 are read on the successor.** #1208's exit condition names `gz obpi dispatch`, and #1203's boundary names `_launches_in_flight`, the OBPI runs. `gz wp runs` reports every run in flight with no marker, and #1203's four cases hold there: an older run beside a later one, a run past any age, a marker on disk moving nothing, and no run reporting nothing. Left on `gz obpi` until tranche 3 removes it: an OBPI run with no marker that `gz state --repair` declines still has no operator reader, and neither the session orientation nor `gz obpi status` replays one; `record_dispatch` keeps its uncontained cache refresh and `declare_single_driver` its raise. No OBPI run was in flight when this landed (measured by `runs_in_flight`, 2026-11-01). The contract suspends OBPI initiation under safe mode, but that is a ruling and not a control: nothing in the launch path refuses, so a run launched anyway would carry these.

**#1205 and #1209 are repaired in place.** The contract's sentence that a repair to `gz obpi` would guard no run names RO-12's four preconditions and not these, and the zoneless marker also stopped `gz preflight`, which outlives `gz obpi`. The stale rule now exists once, as `marker_time_is_stale` in `gzkit.pipeline_markers`, read by the sweep and by the rebuild. Independent review refuted the first build against #1205's invariant, *"complete for any marker file content"*: an integer past the conversion limit and nesting past the decoder's depth still raised out of the loader, and a marker naming `[/x]` stopped both commands in Rich's markup parser. `load_pipeline_json` now reads both as unreadable, both commands escape marker text, and `OutputFormatter.emit` prints a string as text for every verb, which the same review found in `gz wp block`'s reason. The second review refuted the second build: a lone surrogate stopped `--apply` at the console, and the first repair of a zoneless lock claim had only moved its crash from the scan to `--apply`. The CLI's streams now escape what they cannot encode, and `read_claim_time` in `gzkit.lock_manager` reads a zoneless claim as UTC for the scan and the reap alike, so such a lock is booked and stays held as any other does. OBPI-0.35.0-15's Tracked Defects entry *"The stale rule has two copies"* is answered here, because that brief is sealed history (ruling 2). The review question #1205 left open, whether Requirement 6 froze a crash, is settled by the operator's ruling that the repair goes in place. For #1209's items 1 to 3 the docstrings were corrected and the code left as it is, the first of the two repairs its boundary allows.

## Mode contract

`gz wp runs` and the position on `gz wp show` are reads of the ledger and the catalog, on at the operational condition and at the hangar and drydock levels. They gate nothing, so they have no level to apply and no bypass. MEL entry: no (M) or (O) limitation, no placard or deadline; accepted state, on. Self-test: none of its own, because they write nothing for `ledger_producer_probe` to prove; the rows they replay are proved there.

`gz wp dispatch`, `block` and `unblock` are on at the operational condition and at the hangar and drydock levels. They are ledger writers that read no marker, because a repair loop under safe mode is the case the bound exists for. MEL entry: not bypassable, no (M) or (O) limitation, no placard or deadline; accepted state, on. Self-test: `ledger_producer_probe` for each event, at the producer check's interval.

## Known limits of act 1

- A subject can take any number of reviews; only implementing dispatches are bounded.
- `reopen` names the act and is not checked against a reopening, because that verb lands with RO-5's tranche 6.
- The count sees only what is recorded and what its labels say: a review booked falsely against another package's subject arms nothing, and an Implementer falsely labelled on a sibling subject takes that subject's dispatches, about three per subject.
- A subject with no review and no single-driver declaration has no bound: ruling 16 counts only after a review, and nothing in act 1 requires one.
- A subject that passed on its last fix cycle reads as at the bound at the next block, because the bound reads dispatches and not reviews; a hold clears it.
- An issue added to a frozen package by hand is a new subject, as a hand-raised revision is.
- Raising a REQ's revision by hand resets its count, because the freeze lock lands with RO-5's tranche 6.
- A package can reach acceptance with a subject at the bound and no exit taken; escalation is procedure, and Gate 5 still sees the package.
- A new repair package on a new issue has no link to any earlier REQ or issue; only the operator initiates one.
- #1200 stays open: its exit condition has the pipeline's sentence name the mechanism, and the OBPI pipeline moves in tranche 2.
