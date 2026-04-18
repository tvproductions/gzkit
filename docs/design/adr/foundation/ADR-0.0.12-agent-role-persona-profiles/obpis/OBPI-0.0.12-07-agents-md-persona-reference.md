---
id: OBPI-0.0.12-07-agents-md-persona-reference
parent: ADR-0.0.12-agent-role-persona-profiles
item: 7
lane: Heavy
status: in_progress
---

# OBPI-0.0.12-07-agents-md-persona-reference: AGENTS.md Persona Reference Integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- **Checklist Item:** #7 - "AGENTS.md and CLAUDE.md persona reference integration"

**Status:** Completed

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

- [x] `AGENTS.md` - current Persona section (from ADR-0.0.11)
- [x] Parent ADR - integration goals

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`
- [x] ADR-0.0.11 OBPI-04 — how AGENTS.md persona section was established
- [x] Depends on OBPI-01 (main-session persona file)

**Prerequisites (check existence, STOP if missing):**

- [x] AGENTS.md Persona section exists (from ADR-0.0.11)
- [x] AGENTS template exists: `src/gzkit/templates/agents.md`
- [x] Sync surface: `src/gzkit/sync_surfaces.py`

**Existing Code (understand current state):**

- [x] Current AGENTS.md Persona section — what's already there
- [x] Template rendering: `src/gzkit/templates/agents.md`
- [x] Sync tests: `tests/test_sync_surfaces.py`

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

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

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

- [x] REQ-0.0.12-07-01: Given AGENTS.md, when the Persona section is read, then it references the main-session persona grounding and lists all available persona files with role mappings
- [x] REQ-0.0.12-07-02: Given `gz agent sync control-surfaces`, when AGENTS.md is regenerated, then the Persona section survives regeneration with persona references intact
- [x] REQ-0.0.12-07-03: Given `uv run -m behave features/persona.feature`, when persona integration scenarios run, then all pass

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Gate 3 (Docs):** Docs build clean
- [x] **Gate 4 (BDD):** Persona integration scenarios pass
- [x] **Gate 5 (Human):** Human attestation recorded
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 2408 tests in 35.489s — OK
TestAgentsPersonaReference: 5/5 pass
```

### Code Quality

```text
uv run gz lint — All checks passed!
uv run gz typecheck — All checks passed!
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict — Documentation built in 1.15 seconds
uv run gz validate --documents — All validations passed (1 scopes)
```

### Gate 4 (BDD)

```text
uv run -m behave features/persona.feature
6 scenarios passed, 0 failed, 0 skipped
30 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Attestor: jeff
Attestation: attest completed
Date: 2026-04-04
```

### Implementation Summary

- Files modified: src/gzkit/templates/agents.md, AGENTS.md, tests/test_sync_surfaces.py, features/persona.feature
- Tests added: 5 unit tests (TestAgentsPersonaReference), 2 BDD scenarios
- Date completed: 2026-04-04
- Attestation status: Human attested
- Defects noted: None

### Key Proof

```bash
$ rg "main-session.*Primary operator" AGENTS.md
| `main-session` | Primary operator session | craftsperson, governance-aware, whole-file-reasoning, direct |

$ rg "Available personas" AGENTS.md
**Available personas:**
```

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
