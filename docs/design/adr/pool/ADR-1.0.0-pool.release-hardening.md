# ADR-1.0.0: pool.release-hardening

## Status

Proposed

## Date

2026-01-23

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) — Phase 5: Release

---

## Intent

Harden gzkit for 1.0.0 release. All 11 commands functional, templates hardened, ledger and hooks fully operational, documentation complete, graduate course validated.

---

## Target Scope

- All commands functional: init, prd, constitute, specify, plan, obpi, closeout, implement, gates, state, status, attest, analyze
- Templates hardened based on usage feedback
- Ledger fully operational with all event types
- Hooks fully operational (PostToolUse, PreToolUse)
- Documentation complete and validated
- Graduate course demo completable unassisted
- Test coverage ≥40%
- Type check passes (ty strict)

---

## Dependencies

- **Blocks on**: ADR-0.4.0 (audit system)
- **Blocked by**: ADR-0.4.0

---

## Notes

- Phase 5 per PRD rollout plan
- This is the release gate—no 1.0.0 without completing this ADR
- Success metric: student can complete demo workflow unassisted
- Consider: should 1.0.0 require BDD scenarios for CLI contract?
