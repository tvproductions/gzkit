---
id: ADR-pool.adr-layer-coherence
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.adr-layer-coherence: ADR Metadata Layer Coherence (frontmatter↔body↔ledger)

## Status

Pool

## Intent

ADR metadata (lane, kind, status, sensitivity) is asserted across three coherent surfaces — Layer 1 frontmatter, Layer 1 Decision-body prose and child-OBPI declarations, and Layer 2 ledger events. The three surfaces are authored at different times, by different actors, and currently lack a mechanical witness for cross-surface coherence. Drift between any pair is a structural-defect class with the same shape as ledger-vs-frontmatter drift the ledger-of-truth doctrine exists to mechanize, but the supporting machinery does not yet exist for ADR metadata.

Two concrete instances of this defect class were surfaced during ADR-0.0.23 evaluation on 2026-04-29:

- **Frontmatter↔body drift (GHI #365).** ADR-0.0.23 declared `lane: lite` in frontmatter while Decision item 4 body asserted "this item lifts the ADR's overall lane from lite to heavy" and child OBPIs 04–05 declared `lane: Heavy`. `gz adr evaluate` caught the symptom as a Lane Assignment heuristic warning but did not escalate the structural contradiction to a fail-closed validator scope. Manual evaluator review forced the correction; an operator skipping that review would have shipped the contradiction.
- **Layer 1↔Layer 2 drift (GHI #366).** After the GHI #365 fix corrected ADR-0.0.23's frontmatter to `lane: heavy`, Layer 2 retained the original `adr_created` event with `lane: lite`. `gz adr status ADR-0.0.23` continued displaying the stale ledger value because gzkit has no canonical `gz adr amend` verb, no `adr_amended` ledger event in the corpus, and no Layer-1↔Layer-2 coherence validator. Hand-writing a ledger entry is forbidden by AGENTS.md § Behavior Rules — Never #6.

Both are the same architectural absence at different boundaries. The defect becomes load-bearing at closeout: `gz adr audit-check` consults ledger lane to choose the attestation rigor matrix branch (AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix). An ADR whose Layer 2 says `lite` while Layer 1 says `heavy` will under-trigger Gate 5 walkthrough rigor at closeout — the GHI #290-shape failure where structural inconsistency produces under-attested closure.

This ADR opens the design conversation for a unified ADR-metadata-coherence architecture covering both boundaries with one canonical surface family: a fail-closed coherence validator on each Layer-pair boundary, plus a canonical amendment verb that emits provenance-bearing ledger events when Layer 1 metadata legitimately changes between authoring and closeout.

## Decision

_(Pool — design conversation in progress. Concrete decision items to be authored on promotion. Open surface decisions:)_

- **Single `gz adr amend` verb** covering all metadata fields (`--lane`, `--kind`, `--status`, `--sensitivity`) with one `adr_amended` event payload, **vs. per-field verbs** (`gz adr relane`, `gz adr rekind`, etc.) emitting field-specific events.
- **Validator scope folding into `gz validate --documents`** (existing scope, fewer surfaces) **vs. standalone `gz validate --layer-coherence`** (separately invocable, clearer audit narrative).
- **`gz adr status` drift indicator** ("⚠ Layer-2 lane drift: ledger=lite, canon=heavy") **vs. refuse-to-run with prescription** ("run `gz adr amend` first") on detected drift.
- **Frontmatter↔body lane-lift detection regex** scope: canonical phrases only ("lifts the ADR's overall lane from lite to heavy", "lane lift", "heavy-lane trigger") **vs. union with child-OBPI `lane:` declaration parsing** (catches the silent case where Decision body doesn't declare a lift but child OBPIs assume heavy lane).
- **Amendment provenance fields**: minimum (id, field, old, new, ts, schema, reason) **vs. extended** (operator identity per AGENTS.md § Local Agent Rules, optional GHI cross-reference, optional commit SHA at amendment time).
- **`gz register-adrs` integration**: extend to detect amendment candidates and prompt for `gz adr amend` invocation, **vs.** keep regeneration narrow to Layer-3 derived view and route amendment detection through `gz validate --layer-coherence` only.

## Alternatives Considered

_(Pool — full rejected-alternatives table to be authored on promotion. Sketch:)_

1. **Extend ADR-0.0.17 (taxonomy mechanical enforcement) in place.** Lowest ceremony cost; lane-coherence is mechanical enforcement of taxonomy invariants. Rejected at routing time: ADR-0.0.17 is `Validated/Completed`, and amending a closed ADR requires the very amendment ceremony this ADR is meant to define — circular.
2. **Two separate ADRs, one per GHI.** Strongest provenance for each invariant on its own. Rejected at routing time: the two boundaries are the same architectural concern (cross-Layer metadata coherence) at different surface pairs; separating them duplicates the Decision body and produces two ADR relationship matrices that have to be kept in sync.
3. **Skill-level enforcement only** (extend `gz-adr-evaluate` Step 2 manual review to mandate frontmatter-vs-body coherence check, extend `gz-adr-recon` to detect Layer-1↔Layer-2 drift). Rejected: skill-level enforcement is a Layer-3 derived check, not a Layer-1/Layer-2 mechanical witness; relies on agent honor-system rather than fail-closed CLI exit codes.
4. **Hand-write ledger entries to repair drift.** Rejected outright by AGENTS.md § Behavior Rules — Never #6. The amendment verb's purpose is to provide the canonical surface this rule already presumes exists.

## Notes

**Sibling routing receipts:**

- GHI #365 (frontmatter↔body lane-coherence at validate-time) closes `superseded` against this ADR.
- GHI #366 (canon↔ledger amendment surface) closes `superseded` against this ADR.

**Promotion criteria:** before `gz adr promote --kind foundation`, the open surface decisions in § Decision must be resolved with operator preference. Promotion semver candidate: `ADR-0.0.37` (next foundation slot at promotion time).

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
