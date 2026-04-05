---
id: ADR-pool.constitution-invariants
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: speckit
---

# ADR-pool.constitution-invariants: Project Constitution for Immutable Invariants

## Status

Pool

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Formalize `gz constitute` to produce a `CONSTITUTION.md` that declares immutable project
invariants — rules that never change regardless of which ADR is active. Currently
AGENTS.md mixes governance workflow instructions with project-level invariants. A
constitution separates "this is how we use the tool" from "these are the laws of
this codebase."

---

## Target Scope

- `gz constitute` generates `CONSTITUTION.md` with sections:
  - **Language and Runtime**: e.g., "Python 3.13+, uv for dependency management"
  - **Code Style**: e.g., "Ruff defaults, 4-space indent, 100-char lines"
  - **Security**: e.g., "No secrets in source, no force-push to main"
  - **Testing**: e.g., "All public functions must have unit tests"
  - **Architecture**: e.g., "CLI commands are thin wrappers over service functions"
- Optional: `gz check --constitution` validates current code against declared invariants
- Constitution is referenced by AGENTS.md but not contained within it

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No runtime enforcement engine (constitution is declarative, not executable).
- No changes to existing AGENTS.md structure until constitution is proven.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: gz-constitute skill stub already exists

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Constitution template sections are accepted.
3. Relationship between CONSTITUTION.md and AGENTS.md is clarified.

---

## Inspired By

[GitHub Spec Kit](https://github.com/github/spec-kit) — `constitution.md` concept:
immutable project principles that all generated code must satisfy. The specification
is separate from the workflow.

---

## Notes

- The skill stub exists but the ceremony and template are undefined.
- Constitution should be bootstrapped during `gz init` with sensible defaults.
- Key question: should constitutions be enforced (validation) or advisory (documentation)?
- For students: constitution is the "coding standards" document they're already familiar with.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Subsumed by CAP-12** (constitution as executable gate). Spec extends this by integrating constitution checks into the gz-plan-audit loop.
