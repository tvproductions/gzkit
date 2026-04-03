---
id: OBPI-0.0.12-04-narrator-agent-persona
parent: ADR-0.0.12-agent-role-persona-profiles
item: 4
lane: Lite
status: Draft
---

# OBPI-0.0.12-04-narrator-agent-persona: Narrator Agent Persona

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #4 - "Narrator agent persona (clarity, operator-value, precision)"

**Status:** Draft

## Objective

Create `.gzkit/personas/narrator.md` with a clarity-precision-operator-value trait cluster that frames the narrator as a communicator who translates implementation evidence into operator-actionable language.

## Lane

**Lite** - This OBPI creates an internal persona file without changing any external command, API, or schema surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/personas/narrator.md` — primary deliverable (new persona file)
- `tests/test_persona_model.py` — schema validation tests
- `tests/test_persona_schema.py` — structural validation tests
- `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/` — parent ADR package

## Denied Paths

- `.gzkit/personas/implementer.md` — owned by OBPI-02
- `.gzkit/personas/main-session.md` — owned by OBPI-01
- `.gzkit/personas/spec-reviewer.md` — owned by OBPI-03
- `.gzkit/personas/quality-reviewer.md` — owned by OBPI-03
- `src/gzkit/pipeline_runtime.py` — owned by OBPI-06
- `AGENTS.md` — owned by OBPI-07
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Persona file MUST validate against PersonaFrontmatter schema (name, traits, anti-traits, grounding)
1. REQUIREMENT: Traits MUST activate clarity, precision, and operator-value framing behavioral dimensions
1. REQUIREMENT: Grounding MUST frame the narrator's relationship to communication as a craft — translating evidence into decisions, not decorating output
1. NEVER: Use expertise claims or frame the narrator as "a communications expert"
1. ALWAYS: Anti-traits suppress verbosity, jargon accumulation, and implementation-detail over operator-value patterns

> STOP-on-BLOCKERS: if persona control surface `.gzkit/personas/` does not exist, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract and persona section
- [ ] Parent ADR - narrator persona goals in Agent Context Frame

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [ ] ADR-0.0.12 Goals — "Narrator persona activates communication traits"
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Persona control surface exists: `.gzkit/personas/`
- [ ] Exemplar: `.gzkit/personas/implementer.md`

**Existing Code (understand current state):**

- [ ] Agent profile: `.claude/agents/narrator.md`
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
test -f .gzkit/personas/narrator.md
```

## Acceptance Criteria

- [ ] REQ-0.0.12-04-01: Given the PersonaFrontmatter schema, when `.gzkit/personas/narrator.md` is parsed, then validation passes with name matching filename stem and non-empty traits, anti-traits, and grounding
- [ ] REQ-0.0.12-04-02: Given the narrator trait cluster, when traits are examined, then clarity, precision, and operator-value framing are present as distinct behavioral dimensions
- [ ] REQ-0.0.12-04-03: Given `uv run gz personas list`, when the narrator persona exists, then it appears in the listing with its traits and grounding summary

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
