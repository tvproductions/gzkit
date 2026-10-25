<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-5 specification — work packages, task cards and repair orders

**2026-10-25. Status: specified; every open question ruled the same day.** Operator: **g0**. Repair order RO-5 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving labor and maintenance. Sequenced before RO-4 (operator, 2026-10-25: *"yes"*), because the Release Package ships work packages.

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

10. **`ghi-close` and the repair package** (operator: *"yes"*): the register row's "`ghi-close` carrying the PR-closeout distinctions" is dropped; it entered in the agent rewrite `6a77de411` with no ruling behind it, and gzkit works on main with no pull requests. In its place: `ghi-close` records an issue's close against the issue's repair package, and the close of a package's last issue never closes the package, which closes only through Gate 5 (`work_package_transitioned` to `closed`) once its punch-list lines are cleared and its safeguards restored.

## Tranches (for the contractor)

The contractor stops and waits on every structural question (operator, 2026-10-25: *"A"*); the names of new `gz` verbs are one, asked at the start of tranche 2.

1. **Store and event.** `data/catalog/work_packages.json` and its schema: `id` (`WP-<NN>-<slug>`), `kind`, `outcome` (delivery) or `issues` (repair, one or more, each in one package only), `lane` (repair only), aliases (`RO-n`). `work_package_transitioned` with its state grammar and payloads, registered with the forward rule; `gz validate --catalog` reads both.
2. **Verbs.** Initiate (the operator's words), freeze (the baseline, the risk note, the reviewer's receipt; refuses an edit to a baselined REQ except a reopening), close (the Gate 5 decision and the residual; a delivery close also moves its outcome), attach an issue. The forward rule turns fail-closed once these supply an outcome id (RO-3 ruling 4).
3. **GitHub.** The `repair` label; the attach verb's comment naming the package; `ghi-close` recording an issue's close against its package (ruling 10).
4. **Realignment.** The decomposition matrix rekeyed (ruling 9); lane read from the outcome or the repair package for new work, with ADR and OBPI lane left as frozen legacy; the `release_package.md` template's `lane` field removed (its outcome entries are RO-4's).
5. **Witness.** One repair order of this drydock run through the new structure end to end, as the row requires: RO-9 as a repair package carrying #1183 and #1184, aliased `RO-9`.

## Restoration (RO-5's punch-list lines)

Each tranche adds a § Punch list line for every safeguard it disconnects, reroutes or changes: at least the brief-lane validators (`hooks/obpi.py:507`, `validate_briefs.py:48`) and `specify_cmd.py`'s checklist-count check, which tranche 4 changes. RO-5 closes when those lines are cleared.

## Witness

Schema validation of `work_packages.json`; the tranche-5 repair order flown end to end; the register row's witness.

## Current state (research of 2026-10-25)

Lane is stored in four places (ADR frontmatter, the WBS rows, OBPI frontmatter, the brief's `## Lane` section); checklist items link to briefs by position (`specify_cmd.py:700-713`); no code models a work package or repair order; no repair label exists; no repair-order template exists. The only RO-5 act landed is the never-evict lock act of 2026-10-18.
