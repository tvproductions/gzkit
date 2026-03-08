# ADR-pool.per-command-persona-context: Per-Command Persona Context

## Status

Proposed

## Date

2026-03-08

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Formalize persona-specific context loading per command. When `gz plan` runs, the agent
loads architect-mode context (design patterns, tradeoff analysis, decision frameworks).
When `gz check` runs, it loads reviewer-mode context (quality criteria, common defects,
verification checklists). Not separate agents — contextual prompts per command phase.

---

## Target Scope

- Each command phase has an associated persona context (markdown prompt):
  - `gz prd` → Product Manager context (stakeholder needs, scope, success metrics)
  - `gz plan` → Architect context (tradeoffs, patterns, system impact)
  - `gz specify` → Engineer context (implementation detail, test strategy, edge cases)
  - `gz gates` → Reviewer context (quality criteria, common defects, completeness)
  - `gz closeout` → Narrator context (value summary, evidence presentation)
- Persona context files live in `.gzkit/personas/` or within skill SKILL.md files
- Context is loaded automatically when the command runs (no user action required)
- Each persona is a prompt fragment, not a separate agent or session

---

## Inspired By

[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) — agent-as-code pattern
with specialized personas (Product Manager, Architect, Developer, QA). The insight:
different tasks benefit from different AI "mindsets."

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: Skills already contain behavioral instructions — this formalizes them

---

## Notes

- Partially implemented: each skill's SKILL.md already has behavior instructions
- The gap is intentionality — current skills describe workflow, not cognitive stance
- BMAD's failure mode (12+ agent types) is the warning: keep persona count small
- Consider: should personas be user-customizable?
- Key principle: one agent, multiple hats — not multiple agents
