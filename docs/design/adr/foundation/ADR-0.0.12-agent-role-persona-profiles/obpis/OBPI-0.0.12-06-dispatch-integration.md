---
id: OBPI-0.0.12-06-dispatch-integration
parent: ADR-0.0.12-agent-role-persona-profiles
item: 6
lane: Lite
status: Draft
---

# OBPI-0.0.12-06-dispatch-integration: Dispatch Integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #6 - "Dispatch integration (pipeline_runtime.py loads persona at dispatch)"

**Status:** Draft

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
1. NEVER: Hard-code persona content in pipeline_runtime.py — all persona content lives in `.gzkit/personas/`
1. ALWAYS: Persona loading MUST be deterministic — same persona file always produces same prompt prefix

> STOP-on-BLOCKERS: if OBPIs 01-05 persona files do not exist yet, dispatch integration can still be tested with the existing `implementer.md` file. Full integration requires all persona files.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - dispatch integration goals

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [ ] ADR-0.0.11 OBPIs — what persona loading infrastructure exists
- [ ] Depends on OBPIs 01-05 for persona file content (but can proceed with existing implementer.md)

**Prerequisites (check existence, STOP if missing):**

- [ ] `load_persona` function exists: `src/gzkit/models/persona.py`
- [ ] `compose_implementer_prompt` exists: `src/gzkit/pipeline_runtime.py`
- [ ] At least one persona file exists: `.gzkit/personas/implementer.md`

**Existing Code (understand current state):**

- [ ] Pipeline dispatch: `src/gzkit/pipeline_runtime.py` — AGENT_FILE_MAP, compose_implementer_prompt
- [ ] Persona loading: `src/gzkit/models/persona.py` — load_persona function
- [ ] Test patterns: `tests/test_pipeline_runtime.py` — existing dispatch tests

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
uv run -m unittest tests/test_pipeline_runtime.py -v
uv run gz personas list
```

## Acceptance Criteria

- [ ] REQ-0.0.12-06-01: Given a pipeline dispatch for the implementer role, when the dispatch prompt is composed, then the implementer persona body text is prepended to the prompt
- [ ] REQ-0.0.12-06-02: Given a pipeline dispatch for a role whose persona file does not exist, when the dispatch prompt is composed, then dispatch succeeds without error (graceful fallback)
- [ ] REQ-0.0.12-06-03: Given `uv run -m unittest tests/test_pipeline_runtime.py -v`, when persona dispatch tests run, then persona material flows through compose_*_prompt functions

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
