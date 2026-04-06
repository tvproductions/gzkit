---
id: ADR-pool.pre-planning-interview
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: speckit, gsd
---

# ADR-pool.pre-planning-interview: Pre-Planning Interview Phase

## Status

Pool

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

### Standard Interview Mode (existing concept)

- `gz interview` runs a structured question set:
  - "Who uses this feature?" (stakeholders/personas)
  - "What's the failure mode?" (error handling strategy)
  - "What existing code does this touch?" (impact surface)
  - "What alternatives did you consider?" (decision forcing)
  - "How will you verify it works?" (test strategy)
- Output: interview transcript saved as markdown (input artifact for `gz plan`)
- Optional: `gz plan --interview` runs the interview inline before ADR generation
- Interview answers pre-populate ADR template fields (Context, Alternatives, Verification)

### Assumptions Mode (code-analysis-driven)

Alternative interview path where the agent analyzes the existing codebase and proposes decisions, asking only for corrections rather than building answers from scratch:

- `gz interview --assumptions` or `gz plan --assumptions`
- **Agent performs before asking:**
  1. Scans codebase for modules, patterns, and conventions relevant to the stated intent
  2. Identifies files that would be touched, existing abstractions that would be extended
  3. Drafts proposed answers to each interview question based on code analysis
  4. Surfaces the proposals as "here's what I'd do — correct me" rather than open-ended questions
- **Human corrects/confirms** each proposal. The human's job shifts from "answer from scratch" to "spot what the agent missed or got wrong"
- **Output:** Same interview transcript format, but annotated with `source: agent-proposed` or `source: human-corrected` per answer
- **When to use:** Incremental changes to an established codebase where the agent has enough context to make informed proposals. Not suitable for greenfield ADRs or novel architectural decisions where the agent lacks domain knowledge.
- **Value:** Faster interview cycles for experienced codebases. The agent does the research legwork; the human provides judgment. Surfaces assumptions the agent makes that the human wouldn't have noticed to challenge.

**Inspired by:** [GSD](https://github.com/gsd-build/get-shit-done) assumptions mode in `/gsd-discuss-phase` — analyzes existing code and surfaces what it would do, asking only for corrections rather than full decisions.

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No mandatory interview requirement — experienced users skip straight to `gz plan`.
- No domain-specific question sets in initial implementation.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: gz-interview skill stub already exists

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Core question set is accepted.
3. Transcript format and storage location are decided.
4. Assumptions mode: agent proposal format and source annotation schema are defined.
5. Assumptions mode: at least 3 real interviews are run in assumptions mode to validate proposal quality vs. standard mode.

---

## Inspired By

- [GitHub Spec Kit](https://github.com/github/spec-kit) — explicit clarification phase before planning where the AI asks questions to resolve ambiguity before writing the specification.
- [GSD](https://github.com/gsd-build/get-shit-done) — assumptions mode in `/gsd-discuss-phase` where the agent analyzes code and proposes decisions, shifting the human's role from author to reviewer.

---

## Notes

- The skill stub exists but the question set and output format are undefined.
- For students: this is the Socratic method applied to software design.
- Key question: should interview responses persist or be consumed by plan generation?
- Consider: domain-specific question sets (web app vs. CLI vs. library) as a future extension.
- Assumptions mode risk: agent proposals anchor the human. If the agent's analysis is wrong, the human may accept flawed proposals they wouldn't have authored. Mitigation: flag low-confidence proposals explicitly and require human drafting for those items.
- The gz-adr-create skill (v6) already implements a sophisticated "draft first, then ask" interview pattern (Step 0). Assumptions mode is a natural extension — the agent drafts from code analysis rather than conversation context alone.

## See Also

- [SPEC-agent-capability-uplift](../../briefs/SPEC-agent-capability-uplift.md) — **Subsumed by CAP-01** (structured design exploration in ADR creation). Spec integrates interview into a broader design exploration protocol with competitive analysis from superpowers and GSD patterns.
