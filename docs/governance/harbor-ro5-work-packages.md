<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-5 specification — work packages, task cards and repair orders

**2026-10-25. Status: DRAFT, being ruled one question at a time.** Operator: **g0**. Repair order RO-5 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving labor and maintenance. Sequenced before RO-4 (operator, 2026-10-25: *"yes"*), because the Release Package ships work packages.

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

## Open questions, in the order they are being ruled

6. The repair order's id: `WP-<NN>-<slug>` like every work package, or its own `RO-<n>` series.
7. The repair tagging scheme on GitHub.
8. The legacy checklist link: frozen as is, or a stored id added to live legacy ADRs.
9. The decomposition matrix: retired under RO-6, or rekeyed to size work packages and task cards.
10. The meaning of "`ghi-close` carrying the PR-closeout distinctions".

## Current state (research of 2026-10-25)

Lane is stored in four places (ADR frontmatter, the WBS rows, OBPI frontmatter, the brief's `## Lane` section); checklist items link to briefs by position (`specify_cmd.py:700-713`); no code models a work package or repair order; no repair label exists; no repair-order template exists. The only RO-5 act landed is the never-evict lock act of 2026-10-18.
