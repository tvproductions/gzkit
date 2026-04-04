---
id: OBPI-0.0.13-02-gz-init-persona-scaffolding
parent: ADR-0.0.13-portable-persona-control-surface
item: 2
lane: Lite
status: Draft
---

# OBPI-0.0.13-02-gz-init-persona-scaffolding: Gz Init Persona Scaffolding

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #2 - "`gz init` persona scaffolding (default persona set)"

**Status:** Draft

## Objective

Extend `gz init` to create `.gzkit/personas/` with a minimal default persona set
so that any newly initialized GovZero repository has persona scaffolding from
day one.

## Lane

**Lite** - Adds an internal scaffolding step to `gz init` that creates a new
directory with default files. Does not change existing CLI output format, exit
codes, or flags. The init command already creates multiple directories; this
adds one more following the same pattern.

> Note: Borderline case. `gz init` output will mention the new directory, but
> the command contract (flags, exit codes, error format) is unchanged. If the
> default persona set becomes an external contract (e.g., other tools depend on
> specific default persona names), this should be re-evaluated as Heavy.

## Allowed Paths

- `src/gzkit/commands/init_cmd.py` - Add persona directory scaffolding to init flow
- `src/gzkit/templates/personas/` - Default persona templates (if template-based)
- `.gzkit/personas/` - Read existing files to understand default set
- `tests/commands/test_init_cmd.py` - Init command tests
- `tests/test_persona_scaffolding.py` - New scaffolding-specific tests

## Denied Paths

- `src/gzkit/sync_surfaces.py` - Sync is OBPI-03
- `src/gzkit/schemas/` - Schema is OBPI-01
- `src/gzkit/commands/personas.py` - Persona commands are separate
- `.gzkit/manifest.json` - Manifest changes are OBPI-03

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz init` MUST create `.gzkit/personas/` directory if it does not exist.
2. REQUIREMENT: Default persona set MUST contain at least one persona file that validates against the portable schema (OBPI-01).
3. NEVER: Default personas MUST NOT contain project-specific content — they are starter templates that projects customize.
4. ALWAYS: If `.gzkit/personas/` already exists with files, `gz init` MUST NOT overwrite or delete existing persona files.
5. ALWAYS: Persona scaffolding MUST follow the same idempotent pattern as existing `gz init` directory creation.
6. NEVER: Do not add new CLI flags to `gz init` for persona scaffolding — it should be automatic.

> STOP-on-BLOCKERS: if OBPI-0.0.13-01 (portable schema) is not complete, print a BLOCKERS list and halt. Default personas must validate against the schema.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full portability context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [ ] OBPI-0.0.13-01 - schema must be finalized before defaults can be validated
- [ ] Related OBPIs: OBPI-03 (manifest), OBPI-04 (loading)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/init_cmd.py` exists
- [ ] `src/gzkit/schemas/persona.json` exists (from OBPI-01)
- [ ] `.gzkit/personas/` directory exists with current persona files (study as exemplar)

**Existing Code (understand current state):**

- [ ] Pattern to follow: `src/gzkit/commands/init_cmd.py` - existing scaffolding for skills, rules, schemas
- [ ] Pattern to follow: `scaffold_core_skills()` - how default skills are bootstrapped
- [ ] Test patterns: `tests/commands/test_init_cmd.py` - existing init tests

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
# In a temp directory, verify init creates personas
cd $(mktemp -d) && uv run gz init && ls .gzkit/personas/
# Verify idempotency — running init again doesn't overwrite
uv run gz init && ls .gzkit/personas/
```

## Acceptance Criteria

- [ ] REQ-0.0.13-02-01: Given a fresh directory with no `.gzkit/`, when `gz init` runs, then `.gzkit/personas/` is created with at least one default persona file.
- [ ] REQ-0.0.13-02-02: Given `.gzkit/personas/` already exists with custom files, when `gz init` runs, then existing files are preserved and not overwritten.
- [ ] REQ-0.0.13-02-03: Given the default persona files created by `gz init`, when validated against `src/gzkit/schemas/persona.json`, then all pass.
- [ ] REQ-0.0.13-02-04: Given the default persona files, when inspected for project-specific content (gzkit references, specific skill names, pipeline stages), then none is found.

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

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
