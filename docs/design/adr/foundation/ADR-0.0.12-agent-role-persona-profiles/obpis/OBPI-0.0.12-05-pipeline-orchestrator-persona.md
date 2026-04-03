---
id: OBPI-0.0.12-05-pipeline-orchestrator-persona
parent: ADR-0.0.12-agent-role-persona-profiles
item: 5
lane: Lite
status: Draft
---

# OBPI-0.0.12-05-pipeline-orchestrator-persona: Pipeline Orchestrator Persona

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #5 - "Pipeline orchestrator persona (ceremony completion, stage discipline)"

**Status:** Draft

## Objective

Create `.gzkit/personas/pipeline-orchestrator.md` with a ceremony-completion and stage-discipline trait cluster that frames the orchestrator as a governance craftsperson who never shortcuts pipeline stages or summarizes prematurely.

## Lane

**Lite** - This OBPI creates an internal persona file without changing any external command, API, or schema surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/personas/pipeline-orchestrator.md` — primary deliverable (new persona file)
- `tests/test_persona_model.py` — schema validation tests
- `tests/test_persona_schema.py` — structural validation tests
- `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/` — parent ADR package

## Denied Paths

- `.gzkit/personas/implementer.md` — owned by OBPI-02
- `.gzkit/personas/main-session.md` — owned by OBPI-01
- `.gzkit/personas/narrator.md` — owned by OBPI-04
- `src/gzkit/pipeline_runtime.py` — owned by OBPI-06
- `.claude/skills/gz-obpi-pipeline/SKILL.md` — pipeline skill is read-only for this OBPI
- `AGENTS.md` — owned by OBPI-07
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Persona file MUST validate against PersonaFrontmatter schema (name, traits, anti-traits, grounding)
1. REQUIREMENT: Traits MUST activate ceremony completion, stage discipline, and governance fidelity behavioral dimensions
1. REQUIREMENT: Grounding MUST frame the orchestrator's relationship to pipeline stages as non-negotiable — every stage flows into the next, no premature summarization
1. NEVER: Use expertise claims or frame the orchestrator as "an expert in project management"
1. ALWAYS: Anti-traits explicitly suppress premature summarization, stage skipping, and "good enough" completion patterns

> STOP-on-BLOCKERS: if persona control surface `.gzkit/personas/` does not exist, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract and persona section
- [ ] Parent ADR - orchestrator persona goals in Agent Context Frame

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [ ] ADR-0.0.12 Goals — "Pipeline orchestrator persona activates governance traits"
- [ ] `.claude/skills/gz-obpi-pipeline/SKILL.md` — pipeline Iron Law and rationalization prevention table
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Persona control surface exists: `.gzkit/personas/`
- [ ] Exemplar: `.gzkit/personas/implementer.md`

**Existing Code (understand current state):**

- [ ] Pipeline skill: `.claude/skills/gz-obpi-pipeline/SKILL.md` — current behavioral rules
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
test -f .gzkit/personas/pipeline-orchestrator.md
```

## Acceptance Criteria

- [ ] REQ-0.0.12-05-01: Given the PersonaFrontmatter schema, when `.gzkit/personas/pipeline-orchestrator.md` is parsed, then validation passes with name matching filename stem
- [ ] REQ-0.0.12-05-02: Given the orchestrator trait cluster, when traits are examined, then ceremony-completion and stage-discipline are present with anti-traits suppressing premature summarization
- [ ] REQ-0.0.12-05-03: Given `uv run gz personas list`, when the pipeline-orchestrator persona exists, then it appears in the listing with its traits and grounding summary

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
