<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-6 specification — superseded canon corrected

**2026-10-25. Status: specified; every open question ruled the same day.** Operator: **g0**. Repair order RO-6 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving every band. Nothing of RO-6 has landed.

## Settled by the record, not asked

- **The engineering-order rung retires** (operator, 2026-10-17: *"A, no separate document — retire the engineering order rung"*): in `identifier-migration-program.md:16`, `doctrine-merge.md:430` and `design-candidates.md:114,126`, with the same ladder rows' *"release → block"*, which the Release Package replaces.
- **PRD metadata is repaired, not rewritten** (Q-02): the frontmatter `date` and version brought in line with § 1 (*"Last Updated: 2026-10-18"*, *"Version: 0.4"*).
- **FR-006's wording** is ruled by the requirements model (line 271): *"'(Heavy only)' becomes 'for user-facing outcomes'"*.
- **INV-013 stays and leaves RO-6:** *"PRDs MUST be bound to Major versions"* is restated by today's semver ruling (RO-4: *"prd drives major"*), so nothing contradicts it.
- **Pool entries are intentions, not ADRs** (operator, 2026-10-25: *"they just aren't ADRs any longer … they live just fine as intentions, we can bring one down, and then parse it into the new forms as-needed"*): the requirements model's family D (*"pool and promotion"*, line 220) and its worked example (line 304) are corrected to say so: a pulled entry is parsed into the catalog's requirement forms, outcomes and REQs, on demand (operator: *"they can be parsed into what we use for requirements on deand and as needed"*). The pool's files and ids are not renamed; the ruling delays that work.
- **Items other orders now own leave RO-6:** `GovZero/releases/*` and `adr-lifecycle.md` (RO-4 tranche 4); `obpi-decomposition-matrix.md` (RO-5 ruling 9); `ADR-pool.identifier-ladder-migration.md` (a pool entry: an intention, left as is). The safe-mode doctrine's § The Release Package and `doctrine-merge.md` Part 0's Release Package term, which RO-4 ruling 1 contradicts, go to RO-4 tranche 4.

## Items RO-6 retires or corrects

INV-017 (*"Each ADR checklist item MUST map to exactly one OBPI"*, PRD:1122) against RO-5 ruling 8; INV-023 (*"Intent (ADR/OBPI) ↔ Code ↔ Docs"*, PRD:1128) against the general arrangement; FR-005a (PRD:387-406), frozen now rather than "at migration"; the IEEE README's § Currently prohibited (README:639-657) and phase table (:196-201), which predate Q-19 and RO-3; Q-18's *"Names are chosen later"* (OPEN-QUESTIONS:604); the GovZero docs of GHI #1188; a DISAGREEMENTS entry; a glossary.

## Rulings of 2026-10-25

1. **Purpose** (operator questions *"what are we retiring from those resources, and why would we retire anything?"* and *"why not just version the documents and move those documents to an archive or a branch?"*): nothing is deleted. RO-6 corrects documents agents read as canon where a newer ruling replaced what they say, so agents stop following the replaced rule.
2. **Undated live documents, dated archives** (operator, verbatim: *"yes, the link never going stale seems to be a strong argument - anything dated implies archival status"*): a live document keeps its undated path, so every link to it stays good, and carries a last-updated line; its superseded text is saved as a dated snapshot beside it (`<name>-<YYYY-MM-DD>.md`), and any dated document is archival. No branch (the standing no-branch directive). A wholly obsolete document becomes a dated snapshot with nothing live in its place. This replaces striking text in place.
3. **Docs consolidation is a separate tidy chore** (operator: *"we probably need some docs consolidation, which is another chore I think we need"*): it moves dated snapshots to the archive location, checks that no live document cites a snapshot as authority, and merges documents on one subject. Migrating the campaign editions, dated today and steered by `data/active_campaign.json`, is its first job, not RO-6's. Tracked as an insight until the chore is authored.

4. **The PRD is Approved** (operator, verbatim: *"B, it should have never stayed in draft for that long. Also, PRDs are always next-version targets: PRD-1.0, PRD-2.0, etc."*): `PRD-GZKIT-1.0.0` moves from `Draft` to `Approved` (the schema's enum is Draft, Review, Approved, Superseded), with its date and version repaired (Q-02). A PRD names the next major version it targets, as INV-013 and RO-4's semver rule already hold.

5. **FR-006 is reworded after RO-5's lane change, settled by sequencing:** RO-6 runs after RO-5 in the register, so the reword to *"for user-facing outcomes"* lands once lane is derived from the outcome.
6. **The glossary is `docs/examples/glossary.md`, settled by the research:** its *"Lite: 1 (ADR) + 2 (TDD)"* (:73) contradicts universal Gate 5, its OBPI-to-checklist tie (:91-92) and ADR-sized scorecard (:132) predate the catalog, and its *"Python 3.13+"* (:47) predates the 3.14 floor; the other candidate's one contradicted term moved to RO-4.
7. **DISAGREEMENTS: D-02 only** (selection *"A"*): its *"A0 CONCEDES"* (REQ identity sound under the hierarchical grammar) is noted as settled the other way by the requirements model and RO-2/RO-3 (sequential REQ ids independent of any ADR). D-01 and D-05 stay open research debates.

8. **GovZero: only what the drydock contradicts** (selection *"A"*): RO-6 corrects GovZero text today's rulings make wrong; GHI #1188, stale docs as a class with its per-file table and freshness witness, goes to the docs-consolidation chore and stays open until that chore exists (routing comment on the issue).

9. **The four skills are in scope** (selection *"A"*): `gz-status`, `gz-design`, `gz-plan` and `gz-adr-create` lose *"Names are chosen later"* and *"An ADR in flight may be revised to take more OBPIs"*, with `obpi-pipeline-control-rationale.md:114` and the control inventory JSON that carry the same sentence; each skill edit bumps its version and is followed by `gz agent sync control-surfaces`.

## Tranches (for the contractor)

The contractor stops and waits on every structural question. Every correction follows ruling 2: the live document keeps its undated path and gains a last-updated line; the replaced text is saved first as a dated snapshot beside it.

1. **PRD.** INV-017, INV-023 and FR-005a corrected to the RO-5 structure; FR-006 reworded once RO-5 tranche 4 has landed; frontmatter date and version repaired and status set to `Approved` (ruling 4).
2. **IEEE and ladder records.** The IEEE README's § Currently prohibited and phase table brought up to Q-19 and RO-3; Q-18's *"Names are chosen later"*; the engineering-order rung and *"release → block"* in the ladder records; DISAGREEMENTS D-02 (ruling 7); the requirements model's pool wording (pool entries are intentions).
3. **Skills, glossary and GovZero.** The four skills (ruling 9); `docs/examples/glossary.md` (ruling 6); the GovZero text the drydock contradicts (ruling 8).

## Restoration (RO-6's punch-list lines)

RO-6 changes text, not controls, so it expects few lines: any validator or test that pins a sentence RO-6 changes (the control inventory JSON is one) is a line, cleared before RO-6 closes.

## Witness

`mkdocs build --strict`; `gz validate --adr-status-fresh`; for each corrected document, its dated snapshot and last-updated line (ruling 2, in place of the row's retention maps).
