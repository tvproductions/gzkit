---
id: OBPI-0.0.13-01-portable-persona-schema
parent: ADR-0.0.13-portable-persona-control-surface
item: 1
lane: Lite
status: attested_completed
---

# OBPI-0.0.13-01-portable-persona-schema: Portable Persona Schema

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #1 - "Portable persona schema specification (project-agnostic)"

**Status:** Completed

## Objective

Formalize the persona file format as a versioned JSON schema that any
GovZero-compliant repository can validate against, ensuring persona files are
structurally portable without coupling to gzkit-specific content.

## Lane

**Lite** - Defines an internal schema document and updates the existing Pydantic
model. Does not change CLI commands, external APIs, or operator-facing contracts.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `src/gzkit/schemas/persona.json` - New JSON schema for persona file validation
- `src/gzkit/models/persona.py` - Update PersonaFrontmatter to align with portable schema
- `tests/test_persona_schema.py` - Schema validation tests
- `.gzkit/personas/` - Existing persona files (read-only, validate against schema)

## Denied Paths

- `src/gzkit/commands/` - CLI changes are separate OBPIs
- `src/gzkit/sync_surfaces.py` - Sync is OBPI-03
- `.gzkit/manifest.json` - Manifest changes are OBPI-03
- New dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: JSON schema MUST be project-agnostic — no references to gzkit pipeline stages, skill names, or internal module paths.
2. REQUIREMENT: Schema MUST define required fields (`name`, `traits`, `anti_traits`, `grounding`) and their types matching current `PersonaFrontmatter`.
3. ALWAYS: Schema version field MUST be present (e.g., `"schema": "gzkit.persona.v1"`).
4. NEVER: Schema MUST NOT prescribe trait content — it validates structure, not semantics.
5. ALWAYS: All 6 existing persona files in `.gzkit/personas/` MUST validate against the new schema without modification.
6. NEVER: Do not add optional fields that have no current consumer.

> STOP-on-BLOCKERS: if ADR-0.0.11 (persona schema definition) or ADR-0.0.12 (persona profiles) are not complete, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context and portability constraint

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [x] ADR-0.0.11 (persona schema) and ADR-0.0.12 (persona profiles) - upstream dependencies
- [x] Related OBPIs in same ADR (especially OBPI-03 manifest integration)

**Prerequisites (check existence, STOP if missing):**

- [x] `.gzkit/personas/` directory exists with persona files
- [x] `src/gzkit/models/persona.py` exists with `PersonaFrontmatter` model

**Existing Code (understand current state):**

- [x] Pattern to follow: `src/gzkit/schemas/manifest.json` - existing JSON schema exemplar
- [x] Pydantic model: `src/gzkit/models/persona.py` - current field definitions
- [x] Test patterns: `tests/commands/test_personas_cmd.py` - existing persona tests

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
python -c "import json; s = json.load(open('src/gzkit/schemas/persona.json')); print(s.get('title', 'MISSING'))"
uv run gz personas validate
```

## Acceptance Criteria

- [x] REQ-0.0.13-01-01: Given `src/gzkit/schemas/persona.json` exists, when loaded as JSON, then it is a valid JSON Schema document with `$schema`, `title`, and `properties` keys.
- [x] REQ-0.0.13-01-02: Given the schema defines `name`, `traits`, `anti_traits`, and `grounding` as required properties, when any field is omitted from a persona file, then validation fails.
- [x] REQ-0.0.13-01-03: Given all 6 existing persona files in `.gzkit/personas/`, when validated against the schema, then all pass without modification.
- [x] REQ-0.0.13-01-04: Given the schema, when inspected for gzkit-specific references (pipeline stages, skill names, module paths), then none are found.
- [x] REQ-0.0.13-01-05: Given `PersonaFrontmatter` in `src/gzkit/models/persona.py`, when compared to the JSON schema required fields, then they match exactly.

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
Ran 2441 tests in 34.552s — OK
OBPI-specific: 50 tests in tests/test_persona_schema.py — 8 new REQ-0.0.13-01-* tests
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Implementation Summary

- Files created: `src/gzkit/schemas/persona.json` (portable JSON Schema `gzkit.persona.v1`)
- Files modified: `src/gzkit/models/persona.py` (added `SCHEMA_NAME` constant), `tests/test_persona_schema.py` (added 5 test classes, 8 tests)
- Tests added: `TestPortableSchemaStructure`, `TestSchemaRequiredFields`, `TestExistingPersonasValidate`, `TestSchemaPortability`, `TestSchemaModelAlignment`
- Date completed: 2026-04-05
- Attestation status: Human attested
- Defects noted: None

### Key Proof

```bash
$ uv run python -c "from gzkit.schemas import load_schema; s = load_schema('persona'); print(s['$id'], '—', s['properties']['frontmatter']['required'])"
gzkit.persona.v1 — ['name', 'traits', 'anti-traits', 'grounding']
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed
- Date: 2026-04-05

---

**Brief Status:** Completed

**Date Completed:** 2026-04-05

**Evidence Hash:** -
