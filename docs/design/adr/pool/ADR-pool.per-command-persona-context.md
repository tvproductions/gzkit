---
id: ADR-pool.per-command-persona-context
status: Superseded
superseded_by: ADR-0.0.11-persona-driven-agent-identity-frames
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: bmad
---

# ADR-pool.per-command-persona-context: Per-Command Persona Context

## Status

Superseded — subsumed into [ADR-0.0.11-persona-driven-agent-identity-frames](../foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md) as part of a three-ADR series (0.0.11, 0.0.12, 0.0.13) establishing persona as a first-class control surface.

## Lineage (Carried-Forward Ideas)

All design material from this pool ADR has been absorbed into [ADR-0.0.11](../foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md) and its lineage documents:

| Pool ADR Idea | Canonical Destination |
|---|---|
| Per-command persona context loading | ADR-0.0.11 Decision: "per-command cognitive stance is a subset of the persona control surface" |
| `.gzkit/personas/` storage location | ADR-0.0.11 Decision + Interfaces |
| Cognitive stance vs workflow distinction | [Research doc](../../research-persona-selection-agent-identity.md) §Synthesis Principle 2; ADR-0.0.11 Intent |
| One agent, multiple hats (BMAD lesson) | ADR-0.0.11 Non-Goals (no multiple concurrent agents) |
| BMAD inspiration | [Research doc](../../research-persona-selection-agent-identity.md) §7 Production Agent Patterns |
| Automatic context loading per command | ADR-0.0.11 Interfaces: loaded at dispatch time |

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

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No multiple concurrent agents (BMAD's complexity trap).
- No user-facing persona selection UI.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: Skills already contain behavioral instructions — this formalizes them

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Persona set and storage format are accepted.
3. Skill SKILL.md vs. standalone persona file decision is made.

---

## Inspired By

[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) — agent-as-code pattern
with specialized personas (Product Manager, Architect, Developer, QA). The insight:
different tasks benefit from different AI "mindsets."

---

## Notes

- Partially implemented: each skill's SKILL.md already has behavior instructions.
- The gap is intentionality — current skills describe workflow, not cognitive stance.
- BMAD's failure mode (12+ agent types) is the warning: keep persona count small.
- Key principle: one agent, multiple hats — not multiple agents.
- Consider: should personas be user-customizable?
