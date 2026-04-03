---
id: OBPI-0.0.12-07-agents-md-persona-reference
parent: ADR-0.0.12-agent-role-persona-profiles
item: 7
lane: Heavy
status: Draft
---

# OBPI-0.0.12-07-agents-md-persona-reference: AGENTS.md Persona Reference Integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #7 - "AGENTS.md and CLAUDE.md persona reference integration"

**Status:** Draft

## Objective

Integrate the main session persona frame into AGENTS.md by expanding the Persona section (established by ADR-0.0.11) with the main-session persona's grounding and trait summary, and ensure the AGENTS.md template in `src/gzkit/templates/agents.md` renders persona references for `gz agent sync control-surfaces`.

## Lane

**Heavy** - This OBPI modifies AGENTS.md, an external operator-facing governance contract surface, and the AGENTS template used by the sync command.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `AGENTS.md` — primary deliverable (persona reference integration)
- `src/gzkit/templates/agents.md` — AGENTS template for sync surface
- `src/gzkit/sync_surfaces.py` — sync command if persona reference needs dynamic loading
- `tests/test_sync_surfaces.py` — sync integration tests
- `features/persona.feature` — BDD persona integration scenarios
- `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/` — parent ADR package

## Denied Paths

- `.gzkit/personas/*.md` — persona files owned by OBPIs 01-05
- `src/gzkit/pipeline_runtime.py` — owned by OBPI-06
- `.claude/agents/` — agent profiles are not modified in this OBPI
- `src/gzkit/models/persona.py` — persona model is read-only
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: AGENTS.md Persona section MUST reference the main-session persona's grounding text and trait summary
1. REQUIREMENT: AGENTS.md template MUST render persona references so `gz agent sync control-surfaces` produces consistent output
1. REQUIREMENT: Persona section MUST list all available persona files with their role mapping
1. NEVER: Inline full persona content in AGENTS.md — reference the `.gzkit/personas/` control surface
1. ALWAYS: Persona reference MUST survive `gz agent sync control-surfaces` regeneration
1. ALWAYS: When main-session persona exists (OBPI-01), include its grounding in the Persona section; when absent, reference the control surface without inline grounding
1. NEVER: Modify sync_surfaces.py beyond what is needed to render the persona role-mapping table — template engine changes are out of scope for this OBPI
1. NEVER: Add dynamic persona content loading to the sync command — AGENTS.md persona references are static text updated by this OBPI, not dynamically generated at sync time

> STOP-on-BLOCKERS: if AGENTS.md Persona section does not exist (from ADR-0.0.11), print a BLOCKERS list and halt. Note: OBPI-01 (main-session persona) is NOT a blocker — this OBPI can proceed with existing persona files and add main-session references later.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - current Persona section (from ADR-0.0.11)
- [ ] Parent ADR - integration goals

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [ ] ADR-0.0.11 OBPI-04 — how AGENTS.md persona section was established
- [ ] Depends on OBPI-01 (main-session persona file)

**Prerequisites (check existence, STOP if missing):**

- [ ] AGENTS.md Persona section exists (from ADR-0.0.11)
- [ ] AGENTS template exists: `src/gzkit/templates/agents.md`
- [ ] Sync surface: `src/gzkit/sync_surfaces.py`

**Existing Code (understand current state):**

- [ ] Current AGENTS.md Persona section — what's already there
- [ ] Template rendering: `src/gzkit/templates/agents.md`
- [ ] Sync tests: `tests/test_sync_surfaces.py`

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
rg -n "^## Persona$" AGENTS.md
uv run gz agent sync control-surfaces --dry-run
uv run -m behave features/persona.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.12-07-01: Given AGENTS.md, when the Persona section is read, then it references the main-session persona grounding and lists all available persona files with role mappings
- [ ] REQ-0.0.12-07-02: Given `gz agent sync control-surfaces`, when AGENTS.md is regenerated, then the Persona section survives regeneration with persona references intact
- [ ] REQ-0.0.12-07-03: Given `uv run -m behave features/persona.feature`, when persona integration scenarios run, then all pass

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build clean
- [ ] **Gate 4 (BDD):** Persona integration scenarios pass
- [ ] **Gate 5 (Human):** Human attestation recorded
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

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
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
