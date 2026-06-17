---
id: security-sensitivity
paths:
  - "docs/design/adr/**/obpis/**"
  - "data/security_surfaces.json"
description: Security-sensitivity third axis of attestation rigor (ADR-0.0.22).
---

<!-- rule-version: 0.4.0 -->

# Security Sensitivity (gzkit)

> **Rule version:** `0.4.0` — GHI #625: the auto-detect floor now fails closed (`sensitivity-floor-violation`, exit 3) on an *omitted* declaration over a registered overlap, not only on a *wrong* one; pre-cutover briefs are grandfathered via `data/sensitivity_floor_grandfather.json`. Prior `0.3.2` — renamed prohibited `## Anti-patterns` heading → `## Do Not` (OBPI-0.0.54-04 shape conformance pass).

## Invariant

**Security work needs heightened review regardless of lane or kind.** A brief carrying `sensitivity: security` always requires human attestation for completion — consistent with the universal attestation rule in ADR-0.0.36. The axis is additive: heavy lane, foundation kind, and security sensitivity each independently determine which gates fire; Gate 5 brief-level human attestation is universal for every OBPI regardless of kind, lane, or sensitivity.

## Registry contract

Security surfaces are named in [`data/security_surfaces.json`](../../data/security_surfaces.json). The registry is self-bootstrapping: edits require the editing brief to declare `sensitivity: security`.

## `gz validate --sensitivity` (binding)

1. **Auto-detect floor.** Briefs whose allowed-paths overlap a registered security surface MUST declare `sensitivity: security` (exit 3 on violation).
2. **Escalate-not-escape.** A brief MAY declare sensitivity without overlap (escalation). A brief MAY NOT omit sensitivity while overlapping (escape is fail-closed). Both an *omitted* declaration (`sensitivity-floor-violation`) and a *wrong* declaration (`sensitivity-escape-attempt`) over an overlap fail closed at exit 3 (GHI #625).

### Grandfather cutover (GHI #625)

The omitted-declaration floor was tightened from informational (`sensitivity-floor-info`, exit 0) to fail-closed (`sensitivity-floor-violation`, exit 3) after 87 pre-existing briefs were found overlapping a registered surface without a declaration — most overlaps incidental (e.g. an additive audit-wrapper touching `src/gzkit/quality.py`), not unflagged security work. Those briefs are grandfathered in [`data/sensitivity_floor_grandfather.json`](../../data/sensitivity_floor_grandfather.json); they remain at the informational floor. Every **new** brief that overlaps a registered surface MUST declare `sensitivity: security` or it fails closed. If the overlap is an incidental false positive, narrow the Allowed Paths or discharge at completion via `gz obpi complete --accept-security-floor`. Do not add new entries to the grandfather file to silence a fresh violation — that is the escape the cutover exists to close.

## Heightened walkthrough

`gz obpi complete` on a `sensitivity: security` brief fires an extended Gate 5 walkthrough: surface enumeration, `arb-step-security-scan-*` receipt confirmation, classification confirmation, and co-presence proxy gate. Scanner-unavailable is fail-closed (no degradation).

## Do Not

- Declaring `sensitivity: absent` while touching a registered surface
- Editing `data/security_surfaces.json` without declaring `sensitivity: security`
- Narrative substitution for the security-scan receipt
- Bundling security work into a non-security parent OBPI

> See [`docs/governance/security-sensitivity-rationale.md`](../../docs/governance/security-sensitivity-rationale.md) for walkthrough enumeration details, scanner-unavailable failure mode rationale, and related references.
