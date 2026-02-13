# ADR-pool.audit-system: Audit System

## Status

Proposed

## Date

2026-01-23

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) — Phase 5: Audit

---

## Intent

Implement audit generation (`gz analyze`) that produces post-attestation audit artifacts. Audits reconcile records after human attestation—they are not proof of completion.

---

## Target Scope

- `gz analyze` — generate audit artifact from ADR and gate evidence
- Audit includes attestation record, gate results, evidence links
- `audit_generated` event appended to ledger
- Audit templates
- Evidence aggregation from ledger
- ADR status transition: Completed → Validated (after audit)

---

## Dependencies

- **Blocks on**: ADR-pool.heavy-lane
- **Blocked by**: ADR-pool.heavy-lane

---

## Notes

- Phase 5 per PRD rollout plan
- Audit runs AFTER attestation (reconciliation, not proof)
- Audit directory: `docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/audit/`
- Consider: audit artifact format (markdown vs structured data)
