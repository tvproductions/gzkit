<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# RO-6 specification — superseded canon corrected

**2026-10-25. Status: DRAFT, being ruled one question at a time.** Operator: **g0**. Repair order RO-6 of the [harbor pilotage drydock](harbor-pilotage-candidate-2026-10-15.md#repair-orders), serving every band. Nothing of RO-6 has landed.

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

## Open questions, in the order they are being ruled

3. FR-006's timing.
4. Which glossary.
5. Which Astra rejection in DISAGREEMENTS.
6. GHI #1188's scope.
7. The four skills carrying *"Names are chosen later"* and *"An ADR in flight may be revised to take more OBPIs"*.
