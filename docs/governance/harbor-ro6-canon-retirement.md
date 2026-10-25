<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-6 specification — contradicted canon retired

**2026-10-25. Status: DRAFT, being ruled one question at a time.** Operator: **g0**. Repair order RO-6 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving every band. Nothing of RO-6 has landed.

## Settled by the record, not asked

- **The engineering-order rung retires** (operator, 2026-10-17: *"A, no separate document — retire the engineering order rung"*): in `identifier-migration-program.md:16`, `doctrine-merge.md:430` and `design-candidates.md:114,126`, with the same ladder rows' *"release → block"*, which the Release Package replaces.
- **PRD metadata is repaired, not rewritten** (Q-02): the frontmatter `date` and version brought in line with § 1 (*"Last Updated: 2026-10-18"*, *"Version: 0.4"*).
- **FR-006's wording** is ruled by the requirements model (line 271): *"'(Heavy only)' becomes 'for user-facing outcomes'"*.
- **Retirement keeps the text visible, struck**, on the FR-004 precedent (PRD:351-354).
- **INV-013 stays and leaves RO-6:** *"PRDs MUST be bound to Major versions"* is restated by today's semver ruling (RO-4: *"prd drives major"*), so nothing contradicts it.
- **Pool entries are intentions, not ADRs** (operator, 2026-10-25: *"they just aren't ADRs any longer … they live just fine as intentions, we can bring one down, and then parse it into the new forms as-needed"*): the requirements model's family D (*"pool and promotion"*, line 220) and its worked example (line 304) are corrected to say so: a pulled entry is parsed into the catalog's requirement forms, outcomes and REQs, on demand (operator: *"they can be parsed into what we use for requirements on deand and as needed"*). The pool's files and ids are not renamed; the ruling delays that work.
- **Items other orders now own leave RO-6:** `GovZero/releases/*` and `adr-lifecycle.md` (RO-4 tranche 4); `obpi-decomposition-matrix.md` (RO-5 ruling 9); `ADR-pool.identifier-ladder-migration.md` (a pool entry: an intention, left as is). The safe-mode doctrine's § The Release Package and `doctrine-merge.md` Part 0's Release Package term, which RO-4 ruling 1 contradicts, go to RO-4 tranche 4.

## Items RO-6 retires or corrects

INV-017 (*"Each ADR checklist item MUST map to exactly one OBPI"*, PRD:1122) against RO-5 ruling 8; INV-023 (*"Intent (ADR/OBPI) ↔ Code ↔ Docs"*, PRD:1128) against the general arrangement; FR-005a (PRD:387-406), frozen now rather than "at migration"; the IEEE README's § Currently prohibited (README:639-657) and phase table (:196-201), which predate Q-19 and RO-3; Q-18's *"Names are chosen later"* (OPEN-QUESTIONS:604); the GovZero docs of GHI #1188; a DISAGREEMENTS entry; a glossary.

## Rulings of 2026-10-25

(none yet)

## Open questions, in the order they are being ruled

1. The retention-map form for documents outside the content corpus.
2. The PRD's status field.
3. FR-006's timing.
4. Which glossary.
5. Which Astra rejection in DISAGREEMENTS.
6. GHI #1188's scope.
7. The four skills carrying *"Names are chosen later"* and *"An ADR in flight may be revised to take more OBPIs"*.
