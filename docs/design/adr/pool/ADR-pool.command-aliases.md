---
id: ADR-pool.command-aliases
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: bmad
---

# ADR-pool.command-aliases: Human-Readable Command Aliases

## Status

Pool

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add intuitive command aliases so newcomers can use gzkit without memorizing governance
jargon. The canonical names stay, but plain-language alternatives make the CLI
approachable. `gz decide` is immediately understood; `gz plan` requires knowing that
an ADR is a "plan."

---

## Target Scope

- Alias mapping:
  - `gz decide` → `gz plan` (create an ADR / record a decision)
  - `gz task` → `gz specify` (create a task / work item)
  - `gz verify` → `gz gates` (run quality verification)
  - `gz signoff` → `gz attest` (human sign-off)
  - `gz check-in` → `gz status` (where am I?)
  - `gz wrap-up` → `gz closeout` (prepare for sign-off)
- Aliases registered in Click CLI group (trivial implementation)
- `--help` output uses plain language first, canonical name in parentheses
- Aliases are documented in glossary and quickstart

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No replacement of canonical command names — aliases are sugar, not substitutes.
- No user-configurable alias mappings in initial implementation.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Alias set is finalized and accepted.
3. Help text format for alias display is agreed upon.

---

## Inspired By

[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) — uses familiar Agile
vocabulary (user stories, acceptance criteria, sprint) that students already know.
The insight: jargon is a barrier to adoption, not a feature.

---

## Notes

- Smallest effort, highest adoption impact of all proposed improvements.
- Risk: alias proliferation. Keep the set small and stable.
- `--help` improvement is the real win: "gz decide — Record a design decision (alias for gz plan)"
- Consider: should aliases be configurable or hardcoded?
