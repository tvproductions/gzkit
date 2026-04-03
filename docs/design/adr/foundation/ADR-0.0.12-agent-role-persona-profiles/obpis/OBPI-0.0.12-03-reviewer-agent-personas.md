---
id: OBPI-0.0.12-03-reviewer-agent-personas
parent: ADR-0.0.12-agent-role-persona-profiles
item: 3
lane: Lite
status: Draft
---

# OBPI-0.0.12-03-reviewer-agent-personas: Reviewer Agent Personas

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #3 - "Reviewer agent personas (spec-reviewer: independent skeptic; quality-reviewer: architectural rigor)"

**Status:** Draft

## Objective

Create `.gzkit/personas/spec-reviewer.md` and `.gzkit/personas/quality-reviewer.md` with orthogonal trait clusters — independent skepticism and evidence-based assessment for spec-reviewer, architectural rigor and maintainability assessment for quality-reviewer.

## Lane

**Lite** - This OBPI creates internal persona files without changing any external command, API, or schema surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/personas/spec-reviewer.md` — new persona file (spec-reviewer)
- `.gzkit/personas/quality-reviewer.md` — new persona file (quality-reviewer)
- `tests/test_persona_model.py` — schema validation tests
- `tests/test_persona_schema.py` — structural validation tests
- `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/` — parent ADR package

## Denied Paths

- `.gzkit/personas/implementer.md` — owned by OBPI-02
- `.gzkit/personas/main-session.md` — owned by OBPI-01
- `src/gzkit/pipeline_runtime.py` — owned by OBPI-06
- `AGENTS.md` — owned by OBPI-07
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Both persona files MUST validate against PersonaFrontmatter schema (name, traits, anti-traits, grounding)
1. REQUIREMENT: Spec-reviewer MUST activate independent judgment, skepticism, and evidence-based assessment traits
1. REQUIREMENT: Quality-reviewer MUST activate architectural rigor, SOLID principles, and maintainability assessment traits
1. NEVER: Let both reviewer personas share the same trait cluster — they address orthogonal review concerns
1. NEVER: Use expertise claims in either persona grounding or body
1. ALWAYS: Anti-traits suppress rubber-stamping, optimistic bias, and surface-level review patterns

> STOP-on-BLOCKERS: if persona control surface `.gzkit/personas/` does not exist, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract and persona section
- [ ] Parent ADR - research grounding on reviewer trait clusters

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [ ] ADR-0.0.12 Agent Context Frame — reviewer goals
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Persona control surface exists: `.gzkit/personas/`
- [ ] Persona model: `src/gzkit/models/persona.py`
- [ ] Exemplar: `.gzkit/personas/implementer.md`

**Existing Code (understand current state):**

- [ ] Agent profiles: `.claude/agents/spec-reviewer.md`, `.claude/agents/quality-reviewer.md`
- [ ] Test patterns: `tests/test_persona_model.py`, `tests/test_persona_schema.py`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz personas list
uv run -m unittest tests/test_persona_schema.py -v
test -f .gzkit/personas/spec-reviewer.md
test -f .gzkit/personas/quality-reviewer.md
```

## Acceptance Criteria

- [ ] REQ-0.0.12-03-01: Given the PersonaFrontmatter schema, when both reviewer persona files are parsed, then validation passes for each with name matching filename stem
- [ ] REQ-0.0.12-03-02: Given the spec-reviewer persona, when traits are examined, then independent judgment and skepticism traits are present with anti-traits suppressing rubber-stamping
- [ ] REQ-0.0.12-03-03: Given the quality-reviewer persona, when traits are examined, then architectural rigor and SOLID assessment traits are present with anti-traits suppressing surface-level review

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
