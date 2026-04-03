---
id: OBPI-0.0.12-02-implementer-agent-persona
parent: ADR-0.0.12-agent-role-persona-profiles
item: 2
lane: Lite
status: Completed
---

# OBPI-0.0.12-02-implementer-agent-persona: Implementer Agent Persona

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #2 - "Implementer agent persona (plan-then-write, whole-file, PEP 8 as nature)"

**Status:** Completed

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

- [x] `AGENTS.md` - agent operating contract and persona section
- [x] Parent ADR - understand research grounding and PRISM constraint

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [x] ADR-0.0.12 Rationale section — "Evidence from Production Failures" subsection
- [x] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [x] Existing persona file: `.gzkit/personas/implementer.md` (from ADR-0.0.11)
- [x] Persona model: `src/gzkit/models/persona.py` (PersonaFrontmatter)

**Existing Code (understand current state):**

- [x] Current implementer persona: `.gzkit/personas/implementer.md` — read current traits, anti-traits, grounding, and body
- [x] Test patterns: `tests/test_persona_model.py`, `tests/test_persona_schema.py`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

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

- [x] REQ-0.0.12-02-01: Given the existing implementer.md, when enriched with ADR-0.0.12 traits, then schema validation passes and grounding addresses the "plan-first, whole-file, deeply-compliant" trait cluster from the ADR rationale
- [x] REQ-0.0.12-02-02: Given the PRISM constraint, when the updated persona is reviewed, then behavioral identity framing is used throughout — no expertise claims
- [x] REQ-0.0.12-02-03: Given `uv run gz personas list`, when implementer persona is listed, then enriched traits (including plan-then-write and whole-file) appear in output

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_persona_schema.TestImplementerEnrichment -v
test_implementer_enriched_traits ... ok
test_implementer_no_expertise_claims ... ok
test_implementer_schema_and_grounding ... ok
----------------------------------------------------------------------
Ran 3 tests in 0.011s
OK
```

### Code Quality

```text
uv run gz lint  -> All checks passed!
uv run gz typecheck -> All checks passed!
uv run gz test -> Ran 2366 tests in 34.839s OK
```

### Value Narrative

Before this OBPI, the implementer persona had four generic traits without the research-grounded behavioral anchors from ADR-0.0.12's "Evidence from Production Failures" analysis. The default trait cluster ("token-efficient, incremental, shallow-compliant") was not explicitly countered. Now the persona activates plan-then-write, whole-file-thinking, and pep8-as-identity with detailed behavioral anchors and anti-patterns that suppress observed failure modes.

### Key Proof

```bash
uv run gz personas list
# Shows implementer with 7 traits: methodical, test-first, atomic-edits,
# complete-units, plan-then-write, whole-file-thinking, pep8-as-identity
# and 5 anti-traits: minimum-viable-effort, token-efficiency-shortcuts,
# split-imports, partial-edits, shallow-pep8-compliance
```

### Implementation Summary

- Files modified: `.gzkit/personas/implementer.md` (enriched with 3 new traits, 2 new anti-traits, expanded grounding), `tests/test_persona_schema.py` (added TestImplementerEnrichment with 3 tests)
- Tests added: 3 (REQ-0.0.12-02-01, REQ-0.0.12-02-02, REQ-0.0.12-02-03)
- Date completed: 2026-04-03
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed
- Date: 2026-04-03

---

**Brief Status:** Completed

**Date Completed:** 2026-04-03

**Evidence Hash:** -
