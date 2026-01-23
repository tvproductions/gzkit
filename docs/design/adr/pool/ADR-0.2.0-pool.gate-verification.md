# ADR-0.2.0: pool.gate-verification

## Status

Proposed

## Date

2026-01-23

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) — Phase 2: Gates

---

## Intent

Implement gate verification commands (`gz implement`, `gz gates`) that run quality checks and report results. Gate 2 (TDD) enforcement becomes operational.

---

## Target Scope

- `gz implement` — run Gate 2 (test suite), report coverage
- `gz gates` — run all applicable gates for current lane, display results
- `gz gates --gate 2` — run specific gate
- `gate_checked` events appended to ledger
- Gate failures with file:line evidence
- Exit non-zero on gate failure

---

## Dependencies

- **Blocks on**: ADR-0.1.0 (MVP foundation must be complete)
- **Blocked by**: None beyond ADR-0.1.0

---

## Notes

- Phase 2 per PRD rollout plan
- Lite lane only needs Gate 2
- Heavy lane gate verification (3/4) deferred to ADR-0.3.0
- Consider: should `gz implement` run tests directly or defer to configured command?
