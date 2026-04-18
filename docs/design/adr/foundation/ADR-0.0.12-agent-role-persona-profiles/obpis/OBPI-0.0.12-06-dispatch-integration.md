---
id: OBPI-0.0.12-06-dispatch-integration
parent: ADR-0.0.12-agent-role-persona-profiles
item: 6
lane: Lite
status: attested_completed
---

# OBPI-0.0.12-06-dispatch-integration: Dispatch Integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #6 - "Dispatch integration (pipeline_runtime.py loads persona at dispatch)"

**Status:** Completed

## Objective

Modify `src/gzkit/pipeline_runtime.py` to load the appropriate persona frame from `.gzkit/personas/` and prepend it to the subagent dispatch prompt for each role (implementer, spec-reviewer, quality-reviewer, narrator), using the `load_persona` function from ADR-0.0.11.

## Lane

**Lite** - This OBPI wires existing internal infrastructure (persona loading from ADR-0.0.11) into existing dispatch paths. The pipeline_runtime.py dispatch mechanism is an internal implementation detail, not an external operator-facing contract.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/pipeline_runtime.py` — primary deliverable (persona loading in dispatch)
- `tests/test_pipeline_runtime.py` — dispatch integration tests
- `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/` — parent ADR package

## Denied Paths

- `.gzkit/personas/*.md` — persona files owned by OBPIs 01-05
- `AGENTS.md` — owned by OBPI-07
- `.claude/agents/` — agent profiles are not modified here
- `src/gzkit/models/persona.py` — persona model is read-only for this OBPI
- `src/gzkit/personas.py` — composition model is read-only for this OBPI
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Dispatch MUST use `load_persona()` from `src/gzkit/models/persona.py` to load persona body text — no inline persona content in pipeline_runtime.py
1. REQUIREMENT: Each dispatched role MUST receive its corresponding persona frame prepended to the prompt when the persona file exists
1. REQUIREMENT: Missing persona files MUST NOT cause dispatch failure — graceful fallback to no-persona dispatch
1. REQUIREMENT: Persona files with parse errors (malformed YAML frontmatter) MUST raise `ValueError` at dispatch time — parse errors are defects, not graceful-degradation cases
1. NEVER: Hard-code persona content in pipeline_runtime.py — all persona content lives in `.gzkit/personas/`
1. ALWAYS: Persona loading MUST be deterministic — same persona file always produces same prompt prefix
1. ALWAYS: Dispatch MUST log or record which persona was loaded per role — enabling future observability and effectiveness measurement (ADR-0.0.13 scope)

> STOP-on-BLOCKERS: if OBPIs 01-05 persona files do not exist yet, dispatch integration can still be tested with the existing `implementer.md` file. Full integration requires all persona files.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - dispatch integration goals

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [x] ADR-0.0.11 OBPIs — what persona loading infrastructure exists
- [x] Depends on OBPIs 01-05 for persona file content (but can proceed with existing implementer.md)

**Prerequisites (check existence, STOP if missing):**

- [x] `load_persona` function exists: `src/gzkit/models/persona.py`
- [x] `compose_implementer_prompt` exists: `src/gzkit/pipeline_runtime.py`
- [x] At least one persona file exists: `.gzkit/personas/implementer.md`

**Existing Code (understand current state):**

- [x] Pipeline dispatch: `src/gzkit/pipeline_runtime.py` — AGENT_FILE_MAP, compose_implementer_prompt
- [x] Persona loading: `src/gzkit/models/persona.py` — load_persona function
- [x] Test patterns: `tests/test_pipeline_runtime.py` — existing dispatch tests

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
uv run -m unittest tests/test_pipeline_runtime.py -v
uv run gz personas list
```

## Acceptance Criteria

- [x] REQ-0.0.12-06-01: Given a pipeline dispatch for the implementer role, when the dispatch prompt is composed, then the implementer persona body text is prepended to the prompt
- [x] REQ-0.0.12-06-02: Given a pipeline dispatch for a role whose persona file does not exist, when the dispatch prompt is composed, then dispatch succeeds without error (graceful fallback)
- [x] REQ-0.0.12-06-03: Given `uv run -m unittest tests/test_pipeline_runtime.py -v`, when persona dispatch tests run, then persona material flows through compose_*_prompt functions
- [x] REQ-0.0.12-06-04: Given a pipeline dispatch for a role whose persona file has malformed YAML, when the dispatch prompt is composed, then a ValueError is raised (parse errors are defects, not graceful degradation)

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
uv run -m unittest tests/test_pipeline_runtime.py -v
Ran 34 tests in 0.020s — OK
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
uv run gz test — 2403 tests passed
```

### Value Narrative

Before this OBPI, pipeline dispatch composed prompts without any persona framing — subagents defaulted to generic Assistant behavior, causing production failures like import splitting, rubber-stamp reviews, and premature summarization. Now, `pipeline_runtime.py` provides `load_persona_for_dispatch()` and `prepend_persona_to_prompt()` that wire each role's persona frame from `.gzkit/personas/` into the dispatch prompt, activating the right behavioral trait cluster per role.

### Key Proof

```bash
uv run -m unittest tests.test_pipeline_runtime.TestPersonaPipelineIntegration.test_prepend_persona_to_prompt_with_compose -v
# test_prepend_persona_to_prompt_with_compose ... ok
```

### Implementation Summary

- Files modified: `src/gzkit/pipeline_runtime.py` (ROLE_PERSONA_MAP, load_persona_for_dispatch, prepend_persona_to_prompt, persona_loaded field), `tests/test_pipeline_runtime.py` (9 new tests)
- Tests added: test_load_persona_for_dispatch_implementer, test_prepend_persona_to_prompt_with_compose, test_load_persona_for_dispatch_missing_file, test_prepend_persona_passthrough_none, test_load_persona_for_dispatch_malformed, test_load_persona_for_dispatch_unknown_role, test_role_persona_map_covers_agent_file_map, test_prepend_persona_deterministic, test_dispatch_record_persona_field
- Date completed: 2026-04-04
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed
- Date: 2026-04-04

---

**Brief Status:** Completed

**Date Completed:** 2026-04-04

**Evidence Hash:** -
