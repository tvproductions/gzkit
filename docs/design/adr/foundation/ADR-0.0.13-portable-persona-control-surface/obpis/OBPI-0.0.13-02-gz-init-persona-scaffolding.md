---
id: OBPI-0.0.13-02-gz-init-persona-scaffolding
parent: ADR-0.0.13-portable-persona-control-surface
item: 2
lane: Lite
status: Completed
---

# OBPI-0.0.13-02-gz-init-persona-scaffolding: Gz Init Persona Scaffolding

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #2 - "`gz init` persona scaffolding (default persona set)"

**Status:** Completed

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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full portability context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [x] OBPI-0.0.13-01 - schema must be finalized before defaults can be validated
- [x] Related OBPIs: OBPI-03 (manifest), OBPI-04 (loading)

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/commands/init_cmd.py` exists
- [x] `src/gzkit/schemas/persona.json` exists (from OBPI-01)
- [x] `.gzkit/personas/` directory exists with current persona files (study as exemplar)

**Existing Code (understand current state):**

- [x] Pattern to follow: `src/gzkit/commands/init_cmd.py` - existing scaffolding for skills, rules, schemas
- [x] Pattern to follow: `scaffold_core_skills()` - how default skills are bootstrapped
- [x] Test patterns: `tests/commands/test_init_cmd.py` - existing init tests

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
# In a temp directory, verify init creates personas
cd $(mktemp -d) && uv run gz init && ls .gzkit/personas/
# Verify idempotency — running init again doesn't overwrite
uv run gz init && ls .gzkit/personas/
```

## Acceptance Criteria

- [x] REQ-0.0.13-02-01: Given a fresh directory with no `.gzkit/`, when `gz init` runs, then `.gzkit/personas/` is created with at least one default persona file.
- [x] REQ-0.0.13-02-02: Given `.gzkit/personas/` already exists with custom files, when `gz init` runs, then existing files are preserved and not overwritten.
- [x] REQ-0.0.13-02-03: Given the default persona files created by `gz init`, when validated against `src/gzkit/schemas/persona.json`, then all pass.
- [x] REQ-0.0.13-02-04: Given the default persona files, when inspected for project-specific content (gzkit references, specific skill names, pipeline stages), then none is found.

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
Ran 2455 tests in 35.225s
OK
```

### Code Quality

```text
Lint: All checks passed!
Typecheck: All checks passed!
```

### Implementation Summary

- Files created: `tests/test_persona_scaffolding.py` (11 unit tests for scaffolding + schema validation)
- Files modified: `src/gzkit/personas.py` (DEFAULT_PERSONAS dict + scaffold_default_personas function), `src/gzkit/commands/init_cmd.py` (scaffolding call in init flow), `tests/commands/test_init.py` (3 integration tests), `tests/commands/test_personas_cmd.py` (updated for _quick_init persona creation), `tests/commands/common.py` (persona scaffolding in _quick_init)
- Date completed: 2026-04-05
- Attestation status: Human attested
- Defects noted: None

### Key Proof

```bash
$ uv run -m unittest tests/test_persona_scaffolding.py -v
test_at_least_one_default_persona ... ok
test_each_default_validates_against_schema ... ok
test_each_default_parses_with_pydantic ... ok
test_defaults_contain_no_project_specific_content ... ok
test_name_matches_filename_stem ... ok
test_creates_personas_directory ... ok
test_creates_expected_files ... ok
test_returns_empty_when_all_exist ... ok
test_does_not_overwrite_existing_file ... ok
test_creates_missing_files_when_some_exist ... ok
test_idempotent_directory_creation ... ok
Ran 11 tests in 0.012s OK
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: jeff
- Attestation: attest completed
- Date: 2026-04-05

---

**Brief Status:** Completed

**Date Completed:** 2026-04-05

**Evidence Hash:** -
