---
id: ADR-pool.adr-promote-force-bypass-attestation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: GHI #517
---

# ADR-pool.adr-promote-force-bypass-attestation: ADR Promote --force Bypass Attestation

## Status

Pool

## Intent

`gz adr promote --force` bypasses the `evaluate_adr` gate at `src/gzkit/commands/adr_promote.py:380-394` without recording why. The bypass is silent: no ledger event, no attestation text, no operator-typed reason. A non-GO evaluation verdict can be skipped with a single flag and the audit trail shows only a normal promotion. This is the smallest-surface companion to `ADR-pool.evaluation-gate-creation-time-extension` — extending the gate to creation time is moot if `--force` quietly removes it at promotion time.

Surfaced by cross-analyst diagnosis in GHI #517. See `artifacts/reports/ghi-517-cross-analyst-reconciliation.md` § Revised P3 findings (P3-r2).

### Absorbed findings

| ID | Surface | Defect | Severity |
|---|---|---|---|
| P3-r2 | `adr_promote.py:380` `if not force:` guard | `--force` bypasses the only `evaluate_adr` gate in the codebase without ledger record or attestation | 3 |

## Decision

1. **Require `--attestation-text` when `--force` is passed.** Reject `--force` invocation without operator-typed reason (exit 1). Mirrors the pattern from `gz adr emit-receipt` where attestation text is required for receipt emission.
2. **Emit `adr_promote_force_bypass` ledger event.** Distinct event name (not `adr_promoted`) cites the attestation text, operator identity, the bypassed verdict, and the parent ADR. Downstream auditing can surface the bypass count and route GHIs for review.
3. **Audit-time surface.** `gz audit ADR-X.Y.Z` reports any `adr_promote_force_bypass` event in the ADR's ledger chain in the validated receipt evidence section.

## Alternatives Considered

1. **Remove `--force` entirely.** Cleanest fix; removes the bypass class altogether. **Rejected:** legitimate operator scenarios exist (urgent promotions blocked by eval-config issues unrelated to ADR quality); attested bypass is the proportionate fix.
2. **Keep `--force` silent but require co-signing operator email/identity in commit message.** Smaller code change. **Rejected:** governance discipline lives in the ledger (Layer 2), not in commit message conventions (Layer 1 narrative). The ledger event is the mechanical surface.

## Patterns surfaced

- **Prose-vs-mechanics.** `--force` is a single-flag escape hatch in a gate-heavy ceremony; adding `--attestation-text` and a distinct ledger event makes the bypass *mechanically* visible without removing the operator capability.

## Origin

`artifacts/reports/ghi-517-cross-analyst-reconciliation.md` § Revised P3 findings (P3-r2).
