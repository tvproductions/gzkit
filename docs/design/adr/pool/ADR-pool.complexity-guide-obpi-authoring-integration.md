---
id: ADR-pool.complexity-guide-obpi-authoring-integration
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: ADR-0.0.27
inspired_by: ADR-0.0.27
---

# ADR-pool.complexity-guide-obpi-authoring-integration: Complexity Guide → OBPI Authoring Integration

## Status

Pool

## Date

2026-05-04

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Future feature question on integrating `gz complexity-guide` (the authoring-time guidance surface from ADR-0.0.30, separate from the post-commit advisor in ADR-0.0.29) directly into the OBPI authoring workflow. Today, OBPI brief authoring is a `gz obpi specify` ceremony that captures intent, scope, requirements, and acceptance criteria; it does not yet consult complexity-doctrine boundaries to flag, at brief-authoring time, whether the planned implementation surface is likely to cross a refactor-band threshold (per the distilled-characteristics document). This ADR-pool entry holds the forward-reference for the integration: at brief-authoring time, the agent and operator see corpus-grounded warnings on planned modules predicted to land at p90+ complexity, and can adjust scope before implementation begins rather than after the advisor flags them post-commit.

Booked at OBPI-0.0.27-02 as a forward-reference in the citation graph. Activates after ADR-0.0.30 (Complexity Authoring Guidance) lands and the authoring-time guidance surface is operator-stable.
