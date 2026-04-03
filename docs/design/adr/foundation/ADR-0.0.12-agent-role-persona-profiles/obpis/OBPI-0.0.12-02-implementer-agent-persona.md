---
id: OBPI-0.0.12-02-implementer-agent-persona
parent: ADR-0.0.12-agent-role-persona-profiles
item: 2
lane: Lite
status: Draft
---

# OBPI-0.0.12-02-implementer-agent-persona: Implementer Agent Persona

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #2 - "Implementer agent persona (plan-then-write, whole-file, PEP 8 as nature)"

**Status:** Draft

## Objective

Enrich the existing `.gzkit/personas/implementer.md` with ADR-0.0.12 research-grounded behavioral anchors — adding plan-then-write, whole-file thinking, and PEP 8 as identity (not checklist) to the trait cluster while preserving the working traits from ADR-0.0.11.

## Lane

**Lite** - This OBPI enriches an existing internal persona file without changing any external command, API, or schema surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/personas/implementer.md` — primary deliverable (enrich existing persona)
- `tests/test_persona_model.py` — schema validation tests
- `tests/test_persona_schema.py` — structural validation tests
- `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/` — parent ADR package

## Denied Paths

- `.gzkit/personas/main-session.md` — owned by OBPI-01
- `.gzkit/personas/spec-reviewer.md` — owned by OBPI-03
- `.gzkit/personas/quality-reviewer.md` — owned by OBPI-03
- `src/gzkit/pipeline_runtime.py` — owned by OBPI-06
- `AGENTS.md` — owned by OBPI-07
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Updated persona MUST continue to validate against PersonaFrontmatter schema
1. REQUIREMENT: Traits MUST include plan-then-write, whole-file thinking, and PEP-8-as-identity behavioral anchors
1. REQUIREMENT: Existing working traits (methodical, test-first, atomic-edits, complete-units) MUST be preserved or refined, never removed
1. NEVER: Use expertise claims ("You are a senior Python developer with deep expertise in PEP 8")
1. ALWAYS: Anti-traits explicitly suppress observed failure modes (partial edits, import splitting, shallow PEP 8 compliance, token-efficiency shortcuts)

> STOP-on-BLOCKERS: if `.gzkit/personas/implementer.md` does not exist from ADR-0.0.11, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract and persona section
- [ ] Parent ADR - understand research grounding and PRISM constraint

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [ ] ADR-0.0.12 Rationale section — "Evidence from Production Failures" subsection
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Existing persona file: `.gzkit/personas/implementer.md` (from ADR-0.0.11)
- [ ] Persona model: `src/gzkit/models/persona.py` (PersonaFrontmatter)

**Existing Code (understand current state):**

- [ ] Current implementer persona: `.gzkit/personas/implementer.md` — read current traits, anti-traits, grounding, and body
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
test -f .gzkit/personas/implementer.md
```

## Acceptance Criteria

- [ ] REQ-0.0.12-02-01: Given the existing implementer.md, when enriched with ADR-0.0.12 traits, then schema validation passes and grounding addresses the "plan-first, whole-file, deeply-compliant" trait cluster from the ADR rationale
- [ ] REQ-0.0.12-02-02: Given the PRISM constraint, when the updated persona is reviewed, then behavioral identity framing is used throughout — no expertise claims
- [ ] REQ-0.0.12-02-03: Given `uv run gz personas list`, when implementer persona is listed, then enriched traits (including plan-then-write and whole-file) appear in output

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
