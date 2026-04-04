---
id: OBPI-0.0.13-01-portable-persona-schema
parent: ADR-0.0.13-portable-persona-control-surface
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.13-01-portable-persona-schema: Portable Persona Schema

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #1 - "Portable persona schema specification (project-agnostic)"

**Status:** Draft

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

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context and portability constraint

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [ ] ADR-0.0.11 (persona schema) and ADR-0.0.12 (persona profiles) - upstream dependencies
- [ ] Related OBPIs in same ADR (especially OBPI-03 manifest integration)

**Prerequisites (check existence, STOP if missing):**

- [ ] `.gzkit/personas/` directory exists with persona files
- [ ] `src/gzkit/models/persona.py` exists with `PersonaFrontmatter` model

**Existing Code (understand current state):**

- [ ] Pattern to follow: `src/gzkit/schemas/manifest.json` - existing JSON schema exemplar
- [ ] Pydantic model: `src/gzkit/models/persona.py` - current field definitions
- [ ] Test patterns: `tests/commands/test_personas_cmd.py` - existing persona tests

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
python -c "import json; s = json.load(open('src/gzkit/schemas/persona.json')); print(s.get('title', 'MISSING'))"
uv run gz personas validate
```

## Acceptance Criteria

- [ ] REQ-0.0.13-01-01: Given `src/gzkit/schemas/persona.json` exists, when loaded as JSON, then it is a valid JSON Schema document with `$schema`, `title`, and `properties` keys.
- [ ] REQ-0.0.13-01-02: Given the schema defines `name`, `traits`, `anti_traits`, and `grounding` as required properties, when any field is omitted from a persona file, then validation fails.
- [ ] REQ-0.0.13-01-03: Given all 6 existing persona files in `.gzkit/personas/`, when validated against the schema, then all pass without modification.
- [ ] REQ-0.0.13-01-04: Given the schema, when inspected for gzkit-specific references (pipeline stages, skill names, module paths), then none are found.
- [ ] REQ-0.0.13-01-05: Given `PersonaFrontmatter` in `src/gzkit/models/persona.py`, when compared to the JSON schema required fields, then they match exactly.

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
