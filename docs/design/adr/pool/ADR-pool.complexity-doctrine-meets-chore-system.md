---
id: ADR-pool.complexity-doctrine-meets-chore-system
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: ADR-0.0.27
inspired_by: ADR-0.0.27
---

# ADR-pool.complexity-doctrine-meets-chore-system: Complexity Doctrine Meets Chore System

## Status

Pool

## Date

2026-05-04

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Open foundation-kind question on the chore system as a broader doctrine-consumer. The complexity-doctrine cluster (ADR-0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) names the chore system as one of several runtime consumers of distilled-characteristics doctrine — `complexity-reduction-xenon`, `pythonic-design-pattern-detection`, `pythonic-design-pattern-application` are existing chores whose verdicts already pattern-match against complexity boundaries. The question this ADR-pool entry holds: should the chore system formalize doctrine-consumption as a first-class contract (every chore declares which distilled-characteristic boundaries it cites; `gz validate --complexity-doctrine-links` extends to chore declarations; chore registry tracks doctrine-revision dependency), or should it remain implicit (chores reference doctrine in their `CHORE.md` prose, validated only at chore execution time)? The first-class contract is more rigorous; the implicit posture is lower ceremony. ADR-0.0.27 surfaced this without resolving it.

Booked at OBPI-0.0.27-02 as a forward-reference in the citation graph. Activates when chore-system doctrine-consumption surfaces a defect that the implicit posture cannot catch.
