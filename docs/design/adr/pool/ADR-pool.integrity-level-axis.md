---
id: ADR-pool.integrity-level-axis
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.integrity-level-axis: Integrity level as a second axis beside lane

## Status

Pool

## Intent

**Origin.** Proposed under row 1 of R&D run `renewing-vows` (`docs/rnd/renewing-vows.md`), signed off *fund* on 2026-10-10 and given its go on row 1 the same day (operator, verbatim: 'pool; beside it, provisional, new, now — create, then git sync'). A pool ADR is a change proposal: it books nothing and initiates nothing; promotion is the operator's (IRON LAW).

Lane answers one question, whether an external contract changes, and keeps that criterion
(operator rulings 2026-09-23 and 2026-09-25; reaffirmed 2026-10-07). A second question has no
axis: how silently and how irrecoverably a surface fails. The operator's consequence bands
C0 to C3 (2026-09-22) answer it, and on 2026-10-07 the operator ruled them a second axis
beside lane named **integrity level**, the term IEEE 1012-2024 clause 5 uses: the degree of
rigour "shall be commensurate with the integrity level" (as read in the IEEE series,
`docs/governance/ieee/01-engineering-method-2026-09-22.md`).

The bands are **PROVISIONAL** and stay so under this proposal (operator ruling 2026-10-10:
'provisional'): no surface is scored yet, and the ADR's first increment is the scoring, not
the enforcement. Prior art: `ADR-pool.agent-reliability-framework` proposes leveled
assurance appropriated from SLSA; this axis is the gzkit-native level it would need.

## Decision

Proposed, not decided. When promoted, the feature ADR would carry:

1. A scored-surface registry: each governed surface carries an integrity level derived
   from detectability and recoverability, with the derivation recorded and the operator
   attesting the first scoring.
2. An overlap floor: when a change's paths intersect a surface at a level above the lane's
   default rigour, the gates the level requires apply, in the manner the sensitivity floor
   already works for security surfaces (`.gzkit/rules/security-sensitivity.md`).
3. The bands lifted from PROVISIONAL only by an operator ruling after the first scoring
   stands.

Lane is untouched: it remains a required `lite | heavy` field, and nothing infers it from
paths.

## Alternatives Considered

- **Assurance level as the lane criterion.** Refused 2026-10-07: lane keeps its criterion;
  the bands are a second axis, not a replacement.
- **Severity of failure condition as the scale** (ARP4754B's development assurance levels).
  Dropped 2026-10-07: gzkit's scale is detectability and recoverability, not severity, and
  the ARP mapping is paid text the run did not read.
- **Lift PROVISIONAL at authoring.** Rejected 2026-10-10 ('provisional'): a band nobody has
  applied is a declaration without a measurement.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
