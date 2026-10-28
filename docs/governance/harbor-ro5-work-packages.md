<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-5 specification — work packages, task cards and repair orders

**2026-10-25. Status: specified; every open question ruled the same day.** Operator: **g0**. Repair order RO-5 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving labor and maintenance. Sequenced before RO-4 (operator, 2026-10-25: *"yes"*), because the Release Package ships work packages. **Amended 2026-10-28** (§ Amended 2026-10-28): the work-package record carries the bundle, the change ladder, alteration and departure from specification; RO-5 lands before RO-12, the contractor kit.

## Already ruled in the record

- R1 (2026-10-17): *"the repair order mirrors the work package and the work order stays retired"*. R2: *"Gate 5 stays per work package with a release attestation on top"*.
- Operator, 2026-10-17: *"I use GitHub issues largely for repair … I don't do it for feature work or requirements work at all"*; *"I'd like maintenance mode and GitHub issues to be very tightly coupled."*
- Requirements model (`ieee/requirements-model.md`): a work package is *"One dated attempt to deliver one outcome: the frozen REQ baseline, the closing test, the task cards"*, id *"sequential, `WP-<NN>-<slug>`"* (line 34); it *"delivers exactly one outcome … closes by the 100% rule"* (§ 6); *"No version appears in any outcome, work package or REQ id"* (§ 7); an ADR carries *"no checklist, no work packages, no release"* and *"Legacy ADR checklists and OBPIs stay as frozen history"* (§ 9); the operator *"initiates a work package, not each slice"*, the independent reviewer checks each baselined REQ against BABOK's nine criteria, a short risk note at freeze and the residual at validation, and Gate 5 records *"proceed … redirect … pause … or terminate"* (§ 11); *"nothing legacy is backfilled"* (line 184).
- RO-3 left to RO-5: the catalog-editing verbs, freeze and outcome moves, reopening and withdrawal, the freeze lock with its baseline event, and the forward rule turning fail-closed once RO-5's verbs supply an outcome id (`harbor-ro3-requirements-store.md`).

## Rulings of 2026-10-25

1. **A repair order is a work package** (selection *"A"*): one work-package record with `kind: delivery | repair`. A delivery package names its outcome; a repair package names its GitHub issues in the outcome's place. One set of verbs, one freeze-and-close lifecycle.
2. **A repair order carries one or more GitHub issues** (operator: *"ROs can still be associated with a GHI"*; selection *"A"*): a list, with each issue belonging to exactly one repair order, as RO-9 already absorbs #1183 and #1184. An order with no issue today (RO-0, RO-6) is given one when the register moves to issues (doctrine § Records: *"the register is the set of repair-order issues"*).

3. **Work packages live in `data/catalog/work_packages.json`, edited only through `gz` verbs** (operator: *"JSON, through verbs"*), so the freeze lock is a verb that refuses.
4. **Lane is held once** (selection *"A"*): a delivery package derives it from its outcome's `user_facing` (requirements model decision 10), with nothing stored; a repair package, which has no outcome, stores it, set by the heavy-lane test against the surfaces it touches.

5. **One `work_package_transitioned` event** (selection *"A"*), on RO-3's `outcome_transitioned` pattern: `initiated` carries the operator's words; `frozen` carries the baselined REQ ids and revisions, the risk note and the reviewer's nine-criteria receipt; `closed` carries the Gate 5 decision and the residual risk. Closing a delivery package also moves its outcome, each subject with its own event.

6. **One id series** (selection *"A"*): every work package, repair or delivery, is `WP-<NN>-<slug>`; kind lives in the `kind` field, never the id's spelling; the drydock's `RO-n` names stay as aliases resolved through RO-2's identity seam.

7. **The repair tagging scheme** (selection *"A"*): one `repair` label on every issue attached to a repair package; the `gz` verb that attaches an issue also comments the package id on it (`WP-07-astral-toolchain (RO-9)`). The `runtime` label, patch eligibility, is unchanged.
8. **The legacy checklist link is not built; it is settled by the record, not asked.** The row's "checklist to brief link by stored id, not position" (2026-10-17) is superseded by the requirements model of 2026-10-18: an ADR carries *"no checklist, no work packages, no release"*, *"Legacy ADR checklists and OBPIs stay as frozen history behind the aliases"*, and *"nothing legacy is backfilled"*. New work links a work package to its outcome by stored id; the positional link survives only in frozen legacy.

9. **The decomposition matrix is rekeyed, settled by the row:** *"the decomposition matrix detached from lane and kind"*. Its five dimensions and the single-narrative rule size an outcome and a task card instead of an ADR checklist; the Lite, Heavy and Foundation columns and the checklist-count step (`specify_cmd.py:731-738`) go.

10. **`ghi-close` and the repair package** (operator: *"yes"*): the register row's "`ghi-close` carrying the PR-closeout distinctions" is dropped; it entered in the agent rewrite `6a77de411` with no ruling behind it, and gzkit works on main with no pull requests. In its place: `ghi-close` records an issue's close against the issue's repair package, and the close of a package's last issue never closes the package, which closes only through Gate 5 (`work_package_transitioned` to `closed`) once its list-of-discrepancies lines are cleared and its safeguards restored.

## Amended 2026-10-28: the bundle, the change ladder, alteration and departure from specification

A record of that day's amendment; the rulings above are otherwise kept. Authority: the contractor-kit R&D's sign-off, row 4 (operator, 2026-10-28, verbatim: *"fund, yes to 2 and 4"*), which commissions this amendment from three record decisions in [`docs/rnd/contractor-kit.md`](../rnd/contractor-kit.md), each cited below by its heading. The terms are the vocabulary matrix's (`docs/rnd/contractor-kit/vocabulary-matrix.md`, rows B2 to B5, B9, B10). RO-5 lands before RO-12, the kit (`docs/rnd/contractor-kit/review.md` § The order this sets). No code models a work package yet (§ Current state), so every field and event below is specification only.

1. **A work package is the bundle** (decision *"a work package bundles its formal work package and its objective quality evidence"*; option A, operator: *"okay, A. Looking at the matrix, that appears to be the strongest?"*). For both kinds, the record holds its **formal work package** and its **objective quality evidence (OQE)**. The formal work package has four sections: **initial conditions**, as tag-out line items; **procedure**, as the task cards; **test and inspection**, holding the frozen REQ baseline, the closing test and the dock trial; and **system restoration**. A section that does not apply is marked `NA`, never left out. The OQE is the package's record of what was observed, measured or tested, so that the record "will be understood without additional explanation" (JFMM I-10.2, matrix row B4). *System restoration* here is the package's own section. It is not this specification's § Restoration, which lists the safeguards RO-5 itself disconnects.
2. **Every work package is a controlled work package from opening** (decision *"every work package is a controlled work package from opening"*; operator: *"yes to your correction"*). The OQE is required from `initiated`, not acquired at `closed`; no field or state marks a package controlled or uncontrolled. This is the liberty marked at matrix row B4: JFMM requires a CWP only *"when higher authority requires a record"*.
3. **The change ladder, each rung a recorded event on the package** (decision *"the change ladder: pen and ink, change order, attachment, supplement"*; option B, operator: *"B avoids collision and fits"*). Every change to a package records its rung, its approver, the change made, and the superseded content, which is kept (JFMM I-2.3.7.3.c(2)):
    - **pen and ink**: administrative changes and resequencing, including the repairer's in-scope reordering of task cards and tranches; approved by the coordinator.
    - **change order**: a change to scope, boundary or test; work stops when the need is found; issued only by the operator, who approved the original.
    - **attachment**: added work inside the boundary with no new tag-outs; approved by the operator.
    - **supplement**: a new formal work package within the package.

    Work outside the package's *"general scope"* is a new work package. A change order never changes the contract (DFARS 217.7103-6(b); matrix row B1). *Revision* stays the REQ's word, and *job order* is retired as gzkit's name (matrix row B3).
4. **Alteration and departure from specification, both measured against the package's own approved specification** (decision *"alteration and departure from specification, both against the package's own spec"*; option A, operator: *"okay, A is it - make sure the agents/personas/skills are well-versed in these details"*). The package record carries two lists, for repair and delivery packages alike:
    - **alteration**: the planned remodel. It is approved in the formal work package before work starts and accounted for at close as a **configuration change**, in the maintenance record's *reconnected*, *replaced* and *retired* lines, with canon and docs updated.
    - **departure from specification (DFS)**: recorded only where the work cannot meet its own approved specification. Each DFS records its form, a **deviation** (requested before the work) or a **waiver** (after the nonconformance is found); its duration, **temporary** with a clear-by condition or **permanent**; and the operator's approval, which only the operator can give. A DFS never changes the work.

    A difference from the prior shape is not a DFS (option B was declined). The operator's rider is carried by the crosswalk and the kit's personas and skill (RO-12), not by this record.

**What the store and events gain** (amending tranches 1, 2 and 5). The `data/catalog/work_packages.json` record gains `initial_conditions`, `procedure`, `test_and_inspection` and `system_restoration` (each content or `NA`), `oqe`, `alterations` and `departures`. The change ladder is recorded as package events, each naming its rung (`pen_and_ink | change_order | attachment | supplement`), its approver, and the superseded content. A change order also records that work stopped. A DFS is recorded as a package event naming its form, its duration, its clear-by condition when temporary, and the operator's approval. At `closed`, the event's payload also accounts for each alteration as its configuration change and lists each DFS still open. The schema's field names and event names are the contractor's to propose, and the operator rules on them at tranche 1, as the verb names are ruled at tranche 2.

**Held for the operator** (conflicts between the record and this specification; none is resolved here):

- **One event or more.** Ruling 5 rules *one* `work_package_transitioned` event, for lifecycle states. The ladder and the DFS are records of change, not state transitions. Either they ride that event as payloads on a non-transition entry, or they need a second event, which ruling 5's "one" does not allow as written.
- **A change order against a frozen baseline.** Test and inspection holds the frozen REQ baseline (amendment 1), and a change order can change the test (amendment 3). The freeze verb refuses an edit to a baselined REQ *"except a reopening"* (tranche 2), and the requirements model says a reopening *"opens a new work package"*. A test change by change order inside this package is therefore unrouted: it is either a reopening (a new package) or an exception to the freeze lock.
- **Who approves an alteration.** The record says the alteration is "approved in the formal work package before work". It does not name the approver or the event. The freeze event, which already carries the baseline and the reviewer's receipt, is the nearest carrier, but nothing rules it.
- **DFS and the requirements model's scope disposition.** The requirements model has *"A deferral or exclusion is a scope disposition with an approver and a revisit condition, never a satisfaction result"* (matrix row B9). A temporary DFS with a clear-by condition has the same shape, and nothing rules whether a DFS on a REQ is that disposition or a separate record.
- **The lifecycle states.** Ruling 5's grammar is `initiated`, `frozen`, `closed`. The record's life of a package (`review.md` § The life of a work package) adds commencement of work (C1) and final inspection and acceptance (C10). Those decisions are not part of this amendment's three. The state grammar is unamended until the operator rules on them.
- **Configuration-change lines and the punch list.** The alteration decision names the maintenance record's *reconnected*, *replaced* and *retired* lines. The contract's § Punch list, which § Restoration below writes to, uses *reconnected*, *replaced* and *restored*, and the record retires *punch list* as a term (matrix row B8, renamed the list of discrepancies). This specification keeps its 2026-10-25 wording until the contract's renamed section lands.

## Tranches (for the contractor)

The contractor stops and waits on every structural question (operator, 2026-10-25: *"A"*); the names of new `gz` verbs are one, asked at the start of tranche 2.

1. **Store and event.** `data/catalog/work_packages.json` and its schema: `id` (`WP-<NN>-<slug>`), `kind`, `outcome` (delivery) or `issues` (repair, one or more, each in one package only), `lane` (repair only), aliases (`RO-n`). `work_package_transitioned` with its state grammar and payloads, registered with the forward rule; `gz validate --catalog` reads both. Amended 2026-10-28: plus the bundle's sections, OQE, alterations and departures, and the ladder and DFS events (amendments 1 to 4).
2. **Verbs.** Initiate (the operator's words), freeze (the baseline, the risk note, the reviewer's receipt; refuses an edit to a baselined REQ except a reopening), close (the Gate 5 decision and the residual; a delivery close also moves its outcome), attach an issue. The forward rule turns fail-closed once these supply an outcome id (RO-3 ruling 4). Amended 2026-10-28: record a change on its ladder rung (a change order stops work), and record a DFS on the operator's approval.
3. **GitHub.** The `repair` label; the attach verb's comment naming the package; `ghi-close` recording an issue's close against its package (ruling 10).
4. **Realignment.** The decomposition matrix rekeyed (ruling 9); lane read from the outcome or the repair package for new work, with ADR and OBPI lane left as frozen legacy; the `release_package.md` template's `lane` field removed (its outcome entries are RO-4's).
5. **Witness.** One repair order of this drydock run through the new structure end to end, as the row requires: RO-9 as a repair package carrying #1183 and #1184, aliased `RO-9`. Amended 2026-10-28: flown with its formal work package, its sections marked `NA` where they do not apply, and its OQE.

## Restoration (RO-5's list-of-discrepancies lines)

Each tranche adds a § List of discrepancies line for every safeguard it disconnects, reroutes or changes: at least the brief-lane validators (`hooks/obpi.py:507`, `validate_briefs.py:48`) and `specify_cmd.py`'s checklist-count check, which tranche 4 changes. RO-5 closes when those lines are cleared.

## Witness

Schema validation of `work_packages.json`; the tranche-5 repair order flown end to end; the register row's witness.

## Current state (research of 2026-10-25)

Lane is stored in four places (ADR frontmatter, the WBS rows, OBPI frontmatter, the brief's `## Lane` section); checklist items link to briefs by position (`specify_cmd.py:700-713`); no code models a work package or repair order; no repair label exists; no repair-order template exists. The only RO-5 act landed is the never-evict lock act of 2026-10-18. Re-read 2026-10-28 for the amendment: `data/catalog/` holds no `work_packages.json`, and no source, test or data file names a work package, so no code carries the amended fields.
