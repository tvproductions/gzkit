# gzkit Design Roadmap

## Status

Active

## Date

2026-02-11

## Source of Truth

- PRD: [PRD-GZKIT-1.0.0](../prd/PRD-GZKIT-1.0.0.md)
- ADR pool index: [ADR Pool](../adr/pool/README.md)

This roadmap is the execution view of PRD Section 12. The PRD defines intent; this file maps intent to staged ADR work.

---

## Capability Tracks

1. Governance foundation and release hardening (`0.1.0` through `1.0.0`)
2. AI runtime reliability under non-determinism (`1.1.0` through `1.3.0`)

---

## Phase Map

| Phase | Version | Capability | Planned Artifact |
|------|---------|------------|------------------|
| 1 | 0.1.0 | MVP governance core | [ADR-0.1.0](../adr/pre-release/ADR-0.1.0-enforced-governance-foundation/ADR-0.1.0-enforced-governance-foundation.md) |
| 2 | 0.2.0 | Gate verification | [ADR-0.2.0](../adr/pre-release/ADR-0.2.0-gate-verification/ADR-0.2.0-gate-verification.md) |
| 3 | 0.3.0 | Canon extraction and parity | [ADR-0.3.0](../adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md) |
| 4 | 0.4.0 | Skill capability mirroring | [ADR-0.4.0](../adr/pre-release/ADR-0.4.0-skill-capability-mirroring/ADR-0.4.0-skill-capability-mirroring.md) |
| 5 | 0.5.0 | Skill lifecycle governance | [ADR-0.5.0](../adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md) |
| 6 | 0.6.0 | Audit system | [ADR-pool.audit-system](../adr/pool/ADR-pool.audit-system.md) |
| 7 | 1.0.0 | Release hardening | [ADR-pool.release-hardening](../adr/pool/ADR-pool.release-hardening.md) |
| 8 | 1.1.0 | AI runtime foundations | [ADR-pool.ai-runtime-foundations](../adr/pool/ADR-pool.ai-runtime-foundations.md) |
| 9 | 1.2.0 | Evaluation infrastructure | [ADR-pool.evaluation-infrastructure](../adr/pool/ADR-pool.evaluation-infrastructure.md) |
| 10 | 1.3.0 | Controlled agency and recovery | [ADR-pool.controlled-agency-recovery](../adr/pool/ADR-pool.controlled-agency-recovery.md) |

---

## AI Capability Acceptance Intent (Phases 8-10)

- Phase 7: observability, prompt/policy version traceability, and runtime guardrail telemetry are first-class.
- Phase 8: reference datasets and offline eval harnesses are required release evidence for AI workflows.
- Phase 9: explicit human control handoffs, retry/escalation taxonomy, and progressive agency thresholds are enforced.

---

## Governance Rules

- All roadmap items trace to `PRD-GZKIT-1.0.0`.
- Planned phases are represented as pool ADRs first.
- Promotion follows: pool ADR -> full ADR -> OBPIs -> implementation -> attestation.
- Gate 5 attestation remains non-bypassable for completion claims.
