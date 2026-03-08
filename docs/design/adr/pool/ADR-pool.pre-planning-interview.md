# ADR-pool.pre-planning-interview: Pre-Planning Interview Phase

## Status

Proposed

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Formalize `gz interview` as an optional pre-planning step that asks structured questions
before ADR creation. Currently `gz plan` goes straight to ADR generation. Students
(and professionals) often don't know what they don't know — an interview surfaces
assumptions, constraints, and unknowns before committing to a design decision.

---

## Target Scope

- `gz interview` runs a structured question set:
  - "Who uses this feature?" (stakeholders/personas)
  - "What's the failure mode?" (error handling strategy)
  - "What existing code does this touch?" (impact surface)
  - "What alternatives did you consider?" (decision forcing)
  - "How will you verify it works?" (test strategy)
- Output: interview transcript saved as markdown (input artifact for `gz plan`)
- Optional: `gz plan --interview` runs the interview inline before ADR generation
- Interview answers pre-populate ADR template fields (Context, Alternatives, Verification)

---

## Inspired By

[GitHub Spec Kit](https://github.com/github/spec-kit) — explicit clarification phase
before planning where the AI asks questions to resolve ambiguity before writing the
specification.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: gz-interview skill stub already exists

---

## Notes

- The skill stub exists but the question set and output format are undefined
- Interview is optional — experienced users can skip straight to `gz plan`
- For students: this is the Socratic method applied to software design
- Key question: should interview responses persist or be consumed by plan generation?
- Consider: domain-specific question sets (web app vs. CLI vs. library)?
