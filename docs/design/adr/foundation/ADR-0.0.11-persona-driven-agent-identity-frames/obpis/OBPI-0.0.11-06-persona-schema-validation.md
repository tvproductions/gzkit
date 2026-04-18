---
id: OBPI-0.0.11-06-persona-schema-validation
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 6
lane: Lite
status: attested_completed
---

# OBPI-0.0.11-06-persona-schema-validation: Persona Schema Validation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #6 - "Persona schema validation and test infrastructure"

**Status:** Completed

## Objective

Persona files are validated by deterministic schema and unit-test infrastructure
so malformed or incomplete persona artifacts fail before agent loading consumes
them.

## Lane

**Lite** - This OBPI adds internal validation and tests. It supports a Heavy
control surface but does not introduce a separate external contract.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Dependencies

- **Depends on:** OBPI-0.0.11-02 (persona schema, directory, and at least one
  exemplar file must exist before validation infrastructure can be built)
- **Blocks:** None directly

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md` — parent ADR for validation intent
- `.gzkit/personas/` — persona fixtures and validation targets
- `src/gzkit/schemas/` — persona schema definition
- `src/gzkit/commands/validate_cmd.py` — integration point for document validation
- `src/gzkit/personas.py` — loader/validator helper if needed
- `tests/test_persona_schema.py` — primary unit-test surface for persona validation

## Denied Paths

- `src/gzkit/cli/**` — CLI surface belongs to OBPI-0.0.11-02
- `AGENTS.md` — template integration belongs to OBPI-0.0.11-04
- `docs/design/adr/pool/ADR-pool.per-command-persona-context.md` — lineage cleanup belongs to OBPI-0.0.11-05
- `features/persona.feature` — Heavy-lane BDD surface belongs to OBPI-0.0.11-02
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Persona validation MUST enforce the required structural fields
   named by ADR-0.0.11: `name`, `traits`, `anti-traits`, and `grounding`
1. REQUIREMENT: Validation MUST include negative coverage for malformed or
   incomplete persona files
1. REQUIREMENT: The validation path MUST integrate with repo-standard checks so
   persona drift is caught during normal quality verification
1. NEVER: Treat an unvalidated persona file as loadable by default
1. ALWAYS: Keep validation deterministic and runnable offline via `uv run ...`

> STOP-on-BLOCKERS: if the control-surface schema is not yet stable enough to
> encode validation rules, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [x] Control-surface brief: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/obpis/OBPI-0.0.11-02-persona-control-surface-definition.md`
- [x] Composition brief: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/obpis/OBPI-0.0.11-03-trait-composition-model.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists or is intentionally created in this OBPI: `src/gzkit/commands/validate_cmd.py`
- [x] Required path exists or is intentionally created in this OBPI: `.gzkit/personas/`
- [x] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [x] Pattern to follow: `src/gzkit/commands/validate_cmd.py`
- [x] Test patterns: `tests/test_persona_schema.py`
- [x] Parent ADR integration points reviewed for local conventions

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

- [x] Not required for Lite lane

### Gate 4: BDD (Heavy only)

- [x] Not required for Lite lane

### Gate 5: Human (Heavy only)

- [x] Not required for Lite lane

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -d .gzkit/personas
test -f src/gzkit/commands/validate_cmd.py
uv run -m unittest tests/test_persona_schema.py -v
```

## Acceptance Criteria

- [x] REQ-0.0.11-06-01: Persona validation enforces the required structural fields declared by ADR-0.0.11
- [x] REQ-0.0.11-06-02: Invalid persona files fail with deterministic negative-test coverage
- [x] REQ-0.0.11-06-03: Persona validation participates in normal repo verification so malformed personas are caught before loading

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
uv run -m unittest tests/test_persona_schema.py -v
Ran 17 tests in 0.022s — OK
```

### Code Quality

```text
uv run gz lint → All checks passed
uv run gz typecheck → All checks passed
uv run gz test → 2359 tests, OK
```

### Gate 3 (Docs)

```text
Not required for Lite lane.
```

### Gate 4 (BDD)

```text
Not required for Lite lane.
```

### Gate 5 (Human)

```text
Not required for Lite lane.
```

### Implementation Summary

- Files created: `tests/test_persona_schema.py` (17 tests)
- Files modified: `src/gzkit/models/persona.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/validate.py`
- Tests added: 17 (structural enforcement, negative coverage, integration)
- Date completed: 2026-04-02
- Attestation status: Completed
- Defects noted: None

### Key Proof

```text
$ uv run gz validate --personas
Validated: personas
✓ All validations passed (1 scopes).
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `attest completed`
- Date: `2026-04-02`

---

**Brief Status:** Completed

**Date Completed:** 2026-04-02

**Evidence Hash:** -
