# Audit Template: Agent Readiness

## Applying the Four-Discipline Taxonomy

This audit applies the four-discipline taxonomy:

- Prompt craft
- Context engineering
- Intent engineering
- Specification engineering

It also applies the five specification primitives.

Use this template to compare two active projects or to audit one project by leaving the other column as `N/A`.

Each item is scored 0-3:

- 0: Not present. No artifact, no practice, no awareness.
- 1: Informal. The knowledge exists in a maintainer's head but is not encoded for agents.
- 2: Partial. Documentation exists but is incomplete, inconsistent, or not structured for agent use.
- 3: Agent-ready. A competent agent can execute reliably without additional human context.

The normal baseline: many items will score 1 or 2.

---

## Discipline 1: Prompt Craft

### Project A: __________________

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Standard prompts for common tasks | | | |
| Examples of good and bad output for recurring work | | | |
| Explicit output format expectations | | | |
| Guardrails for known failure modes | | | |
| Ambiguity resolution rules | | | |

### Project B: __________________

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Standard prompts for common tasks | | | |
| Examples of good and bad output for recurring work | | | |
| Explicit output format expectations | | | |
| Guardrails for known failure modes | | | |
| Ambiguity resolution rules | | | |

---

## Discipline 2: Context Engineering

### Project A: __________________

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Project-level agent instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) | | | |
| `.github/copilot-instructions.md` (or equivalent) | | | |
| Architecture docs an agent can read | | | |
| ADR index and decision history | | | |
| README that orients a new agent session | | | |
| Schema/domain docs current enough for safe implementation | | | |
| Known conventions documented (naming, file placement, test patterns) | | | |
| Context rot mitigation (stale docs cleaned/flagged) | | | |

### Project B: __________________

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Project-level agent instructions (`AGENTS.md`, `CLAUDE.md`, or equivalent) | | | |
| `.github/copilot-instructions.md` (or equivalent) | | | |
| Architecture docs an agent can read | | | |
| ADR index and decision history | | | |
| README that orients a new agent session | | | |
| Schema/domain docs current enough for safe implementation | | | |
| Known conventions documented (naming, file placement, test patterns) | | | |
| Context rot mitigation (stale docs cleaned/flagged) | | | |

---

## Discipline 3: Intent Engineering

### Project A: __________________

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Project purpose statement an agent can read | | | |
| Trade-off hierarchy (rigor vs. speed) | | | |
| Quality bar definition | | | |
| Scope boundaries (in vs. out) | | | |
| Relationship to upstream/canonical sources defined | | | |
| Decision escalation rules | | | |
| Self-application of governance (dogfooding) | | | |

### Project B: __________________

| Item | Score | Current State | Gap |
|------|-------|---------------|-----|
| Project purpose statement an agent can read | | | |
| Trade-off hierarchy (rigor vs. speed) | | | |
| Quality bar definition | | | |
| Scope boundaries (in vs. out) | | | |
| Relationship to upstream/canonical sources defined | | | |
| Decision escalation rules | | | |
| Self-application of governance (dogfooding) | | | |

---

## Discipline 4: Specification Engineering

### Primitive 1: Self-Contained Problem Statements

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| Project A: Are tasks/issues written with full context? | | | |
| Project A: Do tasks specify environment, schema/version, and test expectations? | | | |
| Project B: Are tasks/issues written with full context? | | | |
| Project B: Do tasks specify environment, schema/version, and test expectations? | | | |

### Primitive 2: Acceptance Criteria

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| Project A: Do tasks have explicit "done looks like" statements? | | | |
| Project A: Are outputs independently verifiable? | | | |
| Project B: Do tasks have explicit "done looks like" statements? | | | |
| Project B: Are outputs independently verifiable? | | | |

### Primitive 3: Constraint Architecture

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| Project A: Musts | | | |
| Project A: Must-nots | | | |
| Project A: Preferences | | | |
| Project A: Escalation triggers | | | |
| Project B: Musts | | | |
| Project B: Must-nots | | | |
| Project B: Preferences | | | |
| Project B: Escalation triggers | | | |

### Primitive 4: Decomposition

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| Project A: Work decomposed into independent milestones | | | |
| Project A: Typical units are sub-2-hour agent tasks | | | |
| Project A: Input/output boundaries are explicit | | | |
| Project B: Work decomposed into independent milestones | | | |
| Project B: Typical units are sub-2-hour agent tasks | | | |
| Project B: Input/output boundaries are explicit | | | |

### Primitive 5: Evaluation Design

| Project | Score | Current State | Gap |
|---------|-------|---------------|-----|
| Project A: TDD evidence (unit-test gate or equivalent) is required and auditable | | | |
| Project A: BDD evidence (behavior/acceptance gate or equivalent) is required and auditable | | | |
| Project A: Eval cases for recurring workflows | | | |
| Project A: Regression checks run after model/instruction changes | | | |
| Project B: TDD evidence (unit-test gate or equivalent) is required and auditable | | | |
| Project B: BDD evidence (behavior/acceptance gate or equivalent) is required and auditable | | | |
| Project B: Eval cases for recurring workflows | | | |
| Project B: Regression checks run after model/instruction changes | | | |

---

## Summary and Next Actions

After scoring, identify the three highest-impact gaps (largest score improvement for lowest effort) per project.

### Project A: Top 3 gaps

1.
2.
3.

### Project B: Top 3 gaps

1.
2.
3.

### Cross-project observations

(Patterns that appear in both projects, indicating a systematic gap rather than a project-specific one.)

---

## Audit Metadata

- Date:
- Auditor:
- Taxonomy source:
- Corroborating sources:
- Framework version:
