---
id: ADR-pool.release-governed-construction
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.release-governed-construction: Release-governed construction: the last release governs the builders

## Status

Pool

## Intent

**Origin.** Proposed under row 1 of R&D run `renewing-vows` (`docs/rnd/renewing-vows.md`), signed off *fund* on 2026-10-10 and given its go on row 1 the same day (operator, verbatim: 'pool; beside it, provisional, new, now — create, then git sync'). A pool ADR is a change proposal: it books nothing and initiates nothing; promotion is the operator's (IRON LAW).

The operator ruled on 2026-10-10 (frontier item 22, 'C') that gzkit is built with a released
gzkit: the governor of construction is the last release, not the working tree, and doctrine
and positions under construction are product until released and proven on another project
before they bind their own making (statement of command, line 7). Today the governor and the
governed are one tree: `gz` imports from `src/gzkit` in this checkout, 200 commits past
`v0.34.8` when measured, and a rule, skill or validator edited this hour binds the work of
this hour. The surfaces a session loads from the tree (`AGENTS.md`, `.claude/rules/**`, the
skills, the hooks) would have to be pinned to the release too.

The sizing of that pin is unknown and is this ADR's first deliverable (operator ruling
2026-10-10: 'now', authored unsized). Prior art: `ADR-pool.release-hardening` and
`ADR-pool.first-release-ceremony` concern shipping; this concerns what governs the builders.

## Decision

Proposed, not decided. When promoted, the feature ADR would carry, in this order:

1. The sizing: which surfaces a session loads from the tree, which of them govern, and what
   pinning each to a release means in mechanism (a released wheel's `src/gzkit/{rules,
   skills,personas,templates}` copies are the obvious source; hooks and `AGENTS.md` are the
   open cases).
2. The pin: construction runs under the last release's surfaces and `gz`; the working tree's
   copies are product until released.
3. The proof: a change to a governing surface binds gzkit's own construction only after it
   is released and has governed one sortie on another project (`ADR-0.38.0`).
4. The operator's patch release as the first step, from the current tree.

## Alternatives Considered

- **Stay as now** (the working tree governs itself). Rejected by the operator 2026-10-10 ('C'
  over A).
- **Abandon self-use** for a lighter, model-direct method. Rejected the same day ('C' over
  B): gzkit would then govern nothing until a sortie flew.
- **Author after the patch release**, when a tag exists to pin against. Rejected 2026-10-10
  ('now'): the release needs a destination to point at.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
