# ADR-pool.heavy-lane: Heavy Lane

## Status

Proposed

## Date

2026-01-23

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md) — Phase 4: Heavy Lane

---

## Intent

Implement Heavy lane enforcement with Gate 3 (Docs) and Gate 4 (BDD) verification. Lane detection becomes operational, applying correct gates based on change scope.

---

## Target Scope

- Gate 3 verification: markdown lint, mkdocs build, link validation
- Gate 4 verification: Behave scenario execution for external contracts
- Lane detection from ADR metadata or interview
- Lane enforcement: Heavy lane requires Gates 1-5, Lite requires Gates 1-2
- PreToolUse hooks for constraint enforcement (optional)
- `gz closeout` command for closeout ceremony protocol

---

## Dependencies

- **Blocks on**: ADR-0.3.0
- **Blocked by**: ADR-0.3.0

---

## Notes

- Phase 4 per PRD rollout plan
- Gate 5 (Human) is Heavy-only; Lite lane stops at Gate 2
- Closeout ceremony: agent becomes passive presenter, human observes directly
- Consider: should lane be auto-detected or always explicit?
