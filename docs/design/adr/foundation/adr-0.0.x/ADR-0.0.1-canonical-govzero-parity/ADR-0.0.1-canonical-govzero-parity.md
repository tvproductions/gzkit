# ADR-0.0.1: Canonical GovZero Parity with AirlineOps

<!--
ADR TEMPLATE: ADR_TEMPLATE_SEMVER.md
Foundational ADR (0.0.z)
This ADR authorizes work; it does not implement it.
-->

---

## Tidy First Plan

Behavior-preserving tidyings required before any feature-level change:

1. Inventory existing governance and tooling surfaces in `gzkit` and classify each as:
   `{canonical | derived | incomplete | divergent}` relative to AirlineOps.
2. Identify all places where governance intent is expressed implicitly rather than
   enforced mechanically.
3. Freeze AirlineOps governance artifacts as read-only canonical inputs.

**No external behavior changes occur in this phase.**

STOP / BLOCKERS:

- If any governance concept in AirlineOps lacks a discoverable source artifact,
  stop and surface it for explicit designation before proceeding.
- If parity work requires inventing new governance abstractions, stop and re-scope.

---

## Status & Metadata

**Date Added:** 2026-01-25
**Status:** Draft
**SemVer:** 0.0.1
**Series:** adr-0.0.x
**Area:** Governance Foundation — Canon Lock
**Lane:** Foundational

> **gzkit Extension:** Foundational lane is a gzkit addition to canon. AirlineOps COPILOT_BRIEF-template.md
> defines Lite (internal code) and Heavy (external contract) but not pure doctrine work.
> Foundational lane addresses 0.0.x ADRs/OBPIs that produce documentation requiring human attestation, not code.
> Gates: 1 (ADR), 3 (Docs), 5 (Human). No Gate 2 (TDD) or Gate 4 (BDD).

---

## Feature Checklist — Appraisal of Completeness

Each item below is an **execution authorization** and MUST decompose into exactly
one OBPI. Order is intentional.

### Canon & Source of Truth

1. Designate AirlineOps as the canonical GovZero implementation.
2. Freeze canonical governance artifacts as non-reinterpretible inputs.

### OBPI System Parity

3. Establish canonical Agent Brief structure parity with AirlineOps.
4. Enforce OBPI ⇄ ADR source-of-truth and drift-detection semantics.

### Discovery & Verification Machinery

5. Introduce a discovery-index control surface equivalent to AirlineOps.
6. Enforce ADR → tests traceability semantics for Gate 2.

### Lane & Gate Semantics

7. Encode lane-correct gate semantics for Foundational, Lite, and Heavy lanes.
8. Prohibit non-canonical or generic governance abstractions in `gzkit`.

---

## Intent

Lock AirlineOps as the **canonical reference implementation of GovZero** and define
the constraints by which `gzkit` must derive, enforce, and remain aligned with that canon.

This ADR exists to prevent governance erosion caused by translation, simplification,
or agent-optimized reinterpretation.

---

## Decision

### AirlineOps Is Canonical

AirlineOps is the authoritative implementation of GovZero.

For any governance concept present in AirlineOps, `gzkit` MUST:
- treat AirlineOps as the source of truth
- preserve both structure *and* enforcement machinery
- reject divergent or weakened translations

Where AirlineOps has no corresponding concept, `gzkit` may introduce one only
explicitly and additively.

---

### Governance Is Defined by Machinery

Governance is defined by the mechanisms that prevent, detect, and correct drift,
including (but not limited to):

- source-of-truth rules
- sync and verification tooling
- lane-specific gate semantics
- explicit STOP / WAIT points
- agent output discipline

Preserving document shape without preserving machinery is invalid.

---

### Foundational ADR Scope

This ADR:
- authorizes work
- defines invariants
- constrains future implementation

This ADR does **not**:
- prescribe commands or steps
- define tooling behavior
- embed acceptance or verification logic

All implementation work MUST occur in OBPIs derived from the Feature Checklist.

---

## Rationale

GovZero emerged inside AirlineOps under operational pressure, not as a designed
framework. Its durability comes from enforcement machinery, not documentation.

Treating AirlineOps as precedent rather than canon produces silent drift and
false confidence. Locking canon restores trust by making parity falsifiable.

---

## Consequences

### Positive

- Single, enforceable GovZero mental model
- Mechanical rather than narrative parity
- Reduced agent-induced erosion of intent

### Negative

- Increased upfront extraction cost
- Reduced flexibility to "simplify" governance
- Ongoing obligation to track AirlineOps evolution

These tradeoffs are intentional.

---

## Evidence (Foundational Gates)

- **Gate 1 (ADR):** This document records intent and constraints.
- **Gate 3 (Docs):** Canon and constraints are explicitly documented.
- **Gate 5 (Human):** Attests documentation sufficiency and doctrinal coherence.

No behavior attestation occurs at this layer.

---

## Evidence Ledger (Authoritative)

### Canonical Sources

- AirlineOps governance artifacts under `.github/skills/`
- `docs/governance/GovZero/*`

### Produced Outputs

- None (enablement ADR)

### Related Work

- OBPIs derived from this ADR will reference this document as their sole authorizer.

---

## OBPIs

Work items derived from this ADR (One Brief Per Item):

| ID | Description | Status |
|----|-------------|--------|
| [OBPI-0.0.1-01](obpis/OBPI-0.0.1-01-designate-airlineops-canonical.md) | Designate AirlineOps as canonical | Pending |
| [OBPI-0.0.1-02](obpis/OBPI-0.0.1-02-freeze-canonical-artifacts.md) | Freeze canonical governance artifacts | Pending |
| [OBPI-0.0.1-03](obpis/OBPI-0.0.1-03-agent-brief-parity.md) | Agent Brief structure parity | Pending |
| [OBPI-0.0.1-04](obpis/OBPI-0.0.1-04-obpi-adr-drift-detection.md) | OBPI ⇄ ADR drift-detection semantics | Pending |
| [OBPI-0.0.1-05](obpis/OBPI-0.0.1-05-discovery-index.md) | Discovery-index control surface | Pending |
| [OBPI-0.0.1-06](obpis/OBPI-0.0.1-06-adr-tests-traceability.md) | ADR → tests traceability (Gate 2) | Pending |
| [OBPI-0.0.1-07](obpis/OBPI-0.0.1-07-lane-gate-semantics.md) | Lane-correct gate semantics | Pending |
| [OBPI-0.0.1-08](obpis/OBPI-0.0.1-08-prohibit-non-canonical.md) | Prohibit non-canonical abstractions | Pending |

---

## Gate 5 — Foundational Attestation

Human attests that:

- the doctrine is coherent
- the constraints are sufficient
- future feature work can safely proceed

This is inspection of the **kitchen**, not the **meal**.

---

## Attestation Block

| Field | Value |
|-------|-------|
| Attestation Term | — |
| Attested By | — |
| Attested At | — |
| Evidence | — |

Human attestation required before status changes to Completed.
