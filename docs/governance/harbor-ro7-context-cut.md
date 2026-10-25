<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-7 specification — the rest of the context cut

**2026-10-25. Status: specified; every open question ruled the same day.** Operator: **g0**. Repair order RO-7 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving the control plane. Every stage is measured by [RO-1's protocol](harbor-ro1-cut-measurement.md); each binding loss stops for the operator's ruling.

## Already ruled in the record

- The cut (operator, 2026-10-16): *"A (in safe mode - make backups!!! - help me test how much we can cut and remain effective…)"*; the backup is the tag `control-plane-baseline-2026-10-16`; canon is reset *"against the trimmed state"* through `gz content retire` and `land`.
- Exit numbers (GHIs #1250 and #1251, ruled A): at most 40 skills; descriptions at most 6,000 chars (met by RO-1 act (c)); every skill model-invoked or `disable-model-invocation: true`; bodies under ceiling; nested `AGENTS.md` at most 60 KB, agents 6 KB, personas 12 KB, hook text 4 KB per turn.
- The merge plan goes to the operator *"before the first deletion"*; a retired skill is deleted from every surface root in the same commit as its successor (#1250). *"most 'obpi' skills will change to work package skills"* (#1250, 2026-10-18).
- Rules: *"no binding clause is removed or reworded"* (#1246).
- Which skills become `disable-model-invocation` is the operator's choice (passage log, RO-1 act (c)).
- Cuts are chosen by cause; a clause kept as common cause cites records that pass `gz insights recurrence` (threshold 3).

## Settled by the record and the register order, not asked

- **Stage 1 is the rules narrative lift** (#1246), measured by RO-1 before the next stage begins.
- **Nested `AGENTS.md` is measured after the rules cut** (#1251: *"measure after those … before cutting rule bodies for it"*).
- **Rationalizations go to each skill's `references/`** (the row), lowering its grandfather ceiling in `skill_body_grandfather.json`.
- **The catalogue merge comes last,** after RO-5 (work-package skills replace OBPI skills) and RO-6 (which corrects four skills' meaning first); `gz-release` subsuming `gz-patch-release` (RO-4) counts as one merge.
- **AGENTS.md is cut only by the operator** retiring or re-tiering named corpus entries; no contractor cut.

## Current state (research of 2026-10-25)

73 skills, bodies 635,996 B; 11 bodies over 300 lines, each within its grandfather ceiling; descriptions 5,938 of 6,000 chars. Rules 150,889 B in 26 files against 60,000 B, 20 files over 4,000 chars. Agents 10,794 B against 6,000; personas 24,879 B against 12,000; nested `AGENTS.md` 210,505 B against 60,000; AGENTS.md 24,785 B against 25,000 (103 invariant entries). `CLAUDE.md` imports only the root `AGENTS.md`; no nested `CLAUDE.md` exists. No stage report exists yet.

## Rulings of 2026-10-25

1. **Nested `AGENTS.md` files are no longer generated** (operator, verbatim: *"A (also, let's at least see if both have rules files, those are more precise)"*). Documented reading (code.claude.com/docs/en/memory; the Codex AGENTS.md guide): Claude reads `AGENTS.md` only through the root `CLAUDE.md` import when a `CLAUDE.md` exists, and gets scoped rules from `.claude/rules` `paths:`; Codex reads only the chain from the project root to its starting directory, at startup. In normal use the 33 nested files (210,505 B) are read by neither. The generator stops writing them and `gz validate --instructions-files-budget` drops the surface; the lost case is scoped rule text for a Codex session started in a subdirectory. Codex has no path-scoped instruction facility (its `.rules` files are command-execution policy; skills load by description; the `AGENTS.md` chain is directory-scoped; the configuration reference has no conditional instructions).
2. **Codex gets the root `AGENTS.md` only; no injection hook** (operator, verbatim: *"I don't think a hook that constantly interrupts and churns is the way. Hooks should enforce important process/loop actions in main workflows. … For now, C is the best answer other than removing those 33 nested AGENTS.md throughout the filesystem."*). Path-scoped rule text stays Claude-only. Hooks enforce process and loop actions in main workflows; they do not inject context per edit.

3. **Demotions are one list, ruled once** (selection *"A"*): the contractor drafts which of the 73 skills become `disable-model-invocation: true`, with a reason each, and the operator rules the list as one batch before the skill stages begin.

## Stages (for the contractor)

Each stage is measured by RO-1's protocol before the next begins; the contractor stops on every structural question and on every binding loss.

1. **Rules** (#1246): narrative, dated history and worked examples lifted from `.gzkit/rules/*.md` to `rule-version-history.md` and rationale pages; no binding clause removed or reworded; each rule's version bumped and mirrors synced.
2. **Nested `AGENTS.md`** (ruling 1): the generator stops writing them, the 33 files are removed, and `gz validate --instructions-files-budget` drops the surface.
3. **Demotion list** (ruling 3): drafted and ruled as one batch.
4. **Skill bodies:** rationalizations and doctrine restatements to each skill's `references/`, lowering its grandfather ceiling; the four skills RO-6 corrects are cut after RO-6 lands.
5. **Agents and personas** to budget (#1251).
6. **Catalogue merge toward 40** (#1250): the merge plan to the operator before the first deletion, drafted after RO-5 so OBPI skills map to work-package skills; `gz-release` subsuming `gz-patch-release` (RO-4) counts as one merge.
7. **AGENTS.md:** only entries the operator names for retirement or re-tiering, through `gz content retire` and `land`.

## Restoration (RO-7's punch-list lines)

Each stage adds a § Punch list line for what it disconnects, reroutes or changes: at least the generator's nested-file tests and the budget validator's scope (stage 2), `skill_body_grandfather.json` and `gz skill audit` (stage 4), and every test or validator that names a merged or deleted skill (stage 6). RO-7 closes when those lines are cleared.

## Witness

`gz validate --instructions-files-budget`; the stage reports under `docs/evals/` (RO-1's protocol).

## Leads, after the drydock

- Prior art on Claude and Codex instruction parity (operator: *"we can't be alone here, this is not the first project to seek parity"*).
- A mature progressive-disclosure system (operator: *"if we had a mature progressive disclosure system, most of these rules would not be needed"*).
