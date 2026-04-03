---
id: OBPI-0.0.12-01-main-session-persona
parent: ADR-0.0.12-agent-role-persona-profiles
item: 1
lane: Lite
status: Completed
---

# OBPI-0.0.12-01-main-session-persona: Main Session Persona

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #1 - "Main session persona frame (the "Python craftsperson" identity)"

**Status:** Completed

## Objective

Create `.gzkit/personas/main-session.md` containing the "Python craftsperson" behavioral identity frame for the main Claude Code session, following the PersonaFrontmatter schema established by ADR-0.0.11.

## Lane

**Lite** - This OBPI creates an internal persona file (`.gzkit/personas/main-session.md`). AGENTS.md integration is owned by OBPI-07. Parent ADR Heavy lane sets the attestation floor.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `.gzkit/personas/main-session.md` — primary deliverable (new persona file)
- `tests/test_persona_model.py` — schema validation tests for the new persona
- `tests/test_persona_schema.py` — structural validation tests
- `features/persona.feature` — BDD persona listing and validation scenarios
- `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/` — parent ADR package

## Denied Paths

- `.gzkit/personas/implementer.md` — owned by OBPI-02
- `src/gzkit/pipeline_runtime.py` — owned by OBPI-06
- `AGENTS.md` — owned by OBPI-07
- `.claude/agents/` — agent profile files are out of scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Persona file MUST validate against PersonaFrontmatter schema (name, traits, anti-traits, grounding fields)
1. REQUIREMENT: Persona MUST use virtue-ethics behavioral identity framing, NOT expertise claims (PRISM constraint: generic expert personas decrease accuracy by 3.6pp)
1. REQUIREMENT: Persona MUST specify both traits (what to activate) and anti-traits (what to suppress), each non-empty
1. NEVER: Frame persona as "You are an expert X developer" or any expertise-claim variant
1. ALWAYS: Grounding statement describes relationship to work, values, and craftsmanship standards — behavioral identity, not job description
1. ALWAYS: Persona name field MUST match the filename stem (`main-session`)

> STOP-on-BLOCKERS: if ADR-0.0.11 persona control surface is not complete, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - agent operating contract and persona section
- [x] Parent ADR - understand full context and research grounding

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [x] ADR-0.0.11 design principles and PRISM/PSM research constraints
- [x] Related OBPIs in same ADR (esp. OBPI-07 for downstream integration)

**Prerequisites (check existence, STOP if missing):**

- [x] Persona control surface exists: `.gzkit/personas/` directory
- [x] Persona model exists: `src/gzkit/models/persona.py` (PersonaFrontmatter)
- [x] Exemplar persona exists: `.gzkit/personas/implementer.md`

**Existing Code (understand current state):**

- [x] Pattern to follow: `.gzkit/personas/implementer.md` (ADR-0.0.11 exemplar)
- [x] Test patterns: `tests/test_persona_model.py`, `tests/test_persona_schema.py`
- [x] Composition model: `src/gzkit/personas.py` (compose_persona_frame)

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
test -f .gzkit/personas/main-session.md
```

## Acceptance Criteria

- [x] REQ-0.0.12-01-01: Given the PersonaFrontmatter schema, when `.gzkit/personas/main-session.md` is parsed, then validation passes with name matching filename stem and non-empty traits, anti-traits, and grounding
- [x] REQ-0.0.12-01-02: Given the PRISM constraint, when the persona grounding and body are reviewed, then NO expertise claims appear — only behavioral identity framing (values, relationship to work, craftsmanship standards)
- [x] REQ-0.0.12-01-03: Given `uv run gz personas list`, when the main-session persona exists, then it appears in the listing with its traits and grounding summary

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
Ran 36 tests in 0.035s — OK
tests/test_persona_schema.py: TestMainSessionValidation (3 tests)
tests/test_persona_model.py: test_main_session_parses (1 test)
Full suite: 2363 tests pass
```

### Code Quality

```text
uv run gz lint — All checks passed!
uv run gz typecheck — All checks passed!
```

### Gate 3 (Docs)

```text
N/A — Lite lane, no docs-build required
```

### Gate 4 (BDD)

```text
features/persona.feature — main-session listing scenario added
```

### Gate 5 (Human)

```text
Attestor: jeff
Attestation: "attest completed"
Date: 2026-04-03
```

### Implementation Summary

- Files created: `.gzkit/personas/main-session.md`
- Files modified: `tests/test_persona_schema.py`, `tests/test_persona_model.py`, `features/persona.feature`
- Tests added: 4 (3 schema validation + PRISM compliance + composition; 1 parse)
- Date completed: 2026-04-03
- Attestation status: Human-attested (parent ADR Heavy lane floor)
- Defects noted: None

### Key Proof

```text
$ uv run gz personas list
┃ Name         ┃ Traits             ┃ Anti-Traits        ┃ Grounding           ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ main-session │ craftsperson,      │ generic-assistant, │ I write Python the  │
│              │ governance-aware,  │ token-efficiency-… │ way it was meant to │
│              │ whole-file-reason… │ incremental-patch… │ be written. PEP 8   │
│              │ direct             │                    │ is not a checklist  │
│              │                    │                    │ I co...             │
```

### Value Narrative

Before this OBPI, the main Claude Code session operated with the default generic Assistant persona, causing token-efficient, incremental, shallow-compliant trait clusters — the direct cause of production failures like import splitting and premature summaries. Now, `.gzkit/personas/main-session.md` provides a research-grounded "Python craftsperson" behavioral identity frame with virtue-ethics traits and explicit anti-traits per the PRISM/PERSONA research.

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
