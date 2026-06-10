---
id: ADR-pool.command-doctrine-internalization
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.command-doctrine-internalization: Command-doctrine internalization worklist

## Status

Pool

## Intent

Carry the implementation worklist of the
[GovZero command doctrine](../../../governance/GovZero/command-doctrine.md)
(canonized 2026-06-10, operator-ratified) as a tracked backlog item. The
doctrine's § "What changes in gzkit" names six concrete mechanisms; its
Appendix A traces which articles are already implemented and which are gaps.
This pool entry is the trackable home for the gaps so the doctrine's intent
cannot silently evaporate (AGENTS.md Prime Directive #6: untrackable defect =
nonexistent defect — the same holds for untrackable doctrine).

## Decision

Backlog the six worklist items, each named with the article it implements:

1. **Briefing template** (Articles 2, 4, 10) — captain's-brief structure:
   scope manifest, stop conditions, expected artifacts, explicit prohibitions
   on out-of-scope change. Everything removed from the prompt either moves
   into the harness or is retired by the Article 10 audit.
2. **Refusal and substitution handling** (Article 5) — attestation/receipt
   records gain a served-model field; a substitution policy file states
   acceptable fallbacks per gate class; the gate runner enforces it.
   Touches `src/gzkit/schemas/` — heavy lane on promotion.
3. **Scope-conformance report** (Article 4) — post-run diff of delivered
   changes against the commanded scope manifest; every unrequested artifact
   annunciated; report is a gate precondition, not advice.
4. **Autonomy span parameter** (Article 6) — configured cap on change volume
   per attestation unit, re-decided at model transitions, recorded in the
   attestation record. Must reconcile with the OBPI Decomposition Matrix,
   which currently sizes by intrinsic complexity, not attestation capacity
   (named tension in Appendix A of the doctrine).
5. **Proficiency log** (Article 9) — scheduled, recorded unassisted-work
   sessions scoped to skills the practice cannot afford to lose.
6. **Coherence audit** (Article 10) — standing checklist at each major model
   transition: trace every gzkit item to an article, benchmark compensation
   items against the current release, record retirements and retained costs.
   Likely implementation: extend the advisory-rules scorecard with a
   traces-to-article column. Doctrine Appendix A is the seed baseline.

## Alternatives Considered

- **Six separate pool ADRs** — finer promotion granularity, but six backlog
  surfaces for one doctrine's worklist invites drift between them; the items
  share one ratification provenance and one trace appendix. Rejected
  (operator ruling, 2026-06-10).
- **Leave the worklist embedded in the doctrine only** — untracked intent;
  rejected for the same reason untrackable defects are rejected.

## Promotion constraints

- Architectural Boundary 2: this entry does not join the runtime track by
  existing. Promotion (whole or per-item, via `gz adr promote`) is a later
  operator ruling; the Magna Carta campaign governs sequencing until 1.0.
- Items 2 and 3 add/change schema or runtime contract — heavy lane and the
  OBPI pipeline mandate apply on promotion.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
