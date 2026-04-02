---
id: OBPI-0.0.11-02-persona-control-surface-definition
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.11-02-persona-control-surface-definition: Persona Control Surface Definition

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #2 - "Persona control surface definition (storage, schema, loading)"

**Status:** Completed

## Objective

`.gzkit/personas/{role}.md`, the persona loading flow, and the read-only
`uv run gz personas list` surface are defined and implemented as the canonical
persona control surface for gzkit.

## Lane

**Heavy** - This OBPI defines a new governed storage surface, adds a CLI read
contract, and changes dispatch/session loading behavior.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Dependencies

- **Depends on:** OBPI-0.0.11-01 (research synthesis informs design principles)
- **Blocks:** OBPI-0.0.11-03, OBPI-0.0.11-04, OBPI-0.0.11-06 (all require the
  persona directory, file format, and schema defined here)

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md` — parent ADR for contract intent
- `.gzkit/personas/` — canonical persona storage location
- `src/gzkit/commands/personas.py` — read-only CLI surface for persona enumeration
- `src/gzkit/cli/parser_governance.py` — CLI registration for `gz personas list`
- `src/gzkit/pipeline_runtime.py` — dispatch/session loading integration
- `tests/test_pipeline_runtime.py` — loading behavior regression surface
- `tests/commands/test_personas_cmd.py` — command verification surface
- `features/persona.feature` — Heavy-lane behavior contract for loading and listing
- `docs/governance/governance_runbook.md` — operator-facing control-surface documentation

## Denied Paths

- `AGENTS.md` — template integration belongs to OBPI-0.0.11-04
- `docs/design/adr/pool/ADR-pool.per-command-persona-context.md` — supersession belongs to OBPI-0.0.11-05
- `tests/test_persona_schema.py` — validation infrastructure belongs to OBPI-0.0.11-06
- Persona mutation commands such as `create`, `edit`, or `delete` are out of scope
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Persona files MUST live under `.gzkit/personas/` and remain
   markdown artifacts with the contract defined by ADR-0.0.11
1. REQUIREMENT: `uv run gz personas list` MUST enumerate defined personas
   without mutating any persona file
1. REQUIREMENT: The main session and dispatched subagents MUST load persona
   material from the control surface at startup/dispatch boundaries
1. REQUIREMENT: This OBPI MUST own the BDD surface for persona loading and the
   read-only CLI listing contract
1. REQUIREMENT: This OBPI MUST deliver at least one exemplar persona file
   (`.gzkit/personas/implementer.md`) as proof-of-concept that the control
   surface works end-to-end — architecture without a payload is incomplete
1. NEVER: Introduce persona mutation commands or dynamic mid-conversation
   persona switching in this OBPI
1. ALWAYS: Keep the control surface grounded in behavioral identity rather than
   expertise claims

> STOP-on-BLOCKERS: if parser registration, runtime loading points, or the
> governed directory contract cannot be located, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [x] Research basis: `docs/design/research-persona-selection-agent-identity.md`
- [x] Related downstream ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists or is intentionally created in this OBPI: `src/gzkit/pipeline_runtime.py`
- [x] Required path exists or is intentionally created in this OBPI: `src/gzkit/cli/parser_governance.py`
- [x] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [x] Pattern to follow: `src/gzkit/pipeline_runtime.py`
- [x] Pattern to follow: `src/gzkit/cli/parser_governance.py`
- [x] Test patterns: `tests/test_pipeline_runtime.py`

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

### Gate 3: Docs (Heavy)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Runbook updates explain the new control surface and read-only CLI

### Gate 4: BDD (Heavy)

- [x] Acceptance scenarios pass: `uv run -m behave features/persona.feature`

### Gate 5: Human (Heavy)

- [x] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/persona.feature

# Specific verification for this OBPI
test -d .gzkit/personas
test -f .gzkit/personas/implementer.md
uv run gz personas list
test -f src/gzkit/pipeline_runtime.py
test -f src/gzkit/cli/parser_governance.py
```

## Acceptance Criteria

- [x] REQ-0.0.11-02-01: Persona files live under `.gzkit/personas/` with a documented, governed contract
- [x] REQ-0.0.11-02-02: `uv run gz personas list` enumerates persona artifacts without mutating them
- [x] REQ-0.0.11-02-03: Session or dispatch loading consumes persona material from the control surface at the documented lifecycle boundaries
- [x] REQ-0.0.11-02-04: At least one exemplar persona file (`.gzkit/personas/implementer.md`) exists, passes schema validation, and is returned by `gz personas list`
- [x] REQ-0.0.11-02-05: Heavy-lane evidence includes docs, BDD output, and human attestation before closure

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
Ran 2327 tests in 31.397s
OK
```

### Code Quality

```text
Lint: All checks passed!
Typecheck: All checks passed!
```

### Gate 3 (Docs)

```text
uv run gz validate --documents: All validations passed (1 scopes).
uv run mkdocs build --strict: build passes (pre-existing plan.md nav warning only)
Governance runbook updated with persona control surface section.
```

### Gate 4 (BDD)

```text
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
14 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Attestor: jeff
Attestation: attest completed
Date: 2026-04-01
```

### Implementation Summary

- Files created: src/gzkit/models/persona.py, src/gzkit/commands/personas.py, .gzkit/personas/implementer.md, tests/test_persona_model.py, tests/commands/test_personas_cmd.py, features/persona.feature, features/steps/persona_steps.py
- Files modified: src/gzkit/cli/parser_governance.py, tests/commands/test_parsers.py, tests/test_pipeline_runtime.py, docs/governance/governance_runbook.md, config/doc-coverage.json
- Tests added: 24 (15 model, 6 CLI, 2 pipeline integration, 1 parser)
- Date completed: 2026-04-01
- Attestation status: Human attested
- Defects noted: None

### Key Proof

```bash
$ uv run gz personas list --json
[
  {
    "name": "implementer",
    "traits": ["methodical", "test-first", "atomic-edits", "complete-units"],
    "anti_traits": ["minimum-viable-effort", "token-efficiency-shortcuts", "split-imports"],
    "grounding": "I approach implementation as a craftsperson..."
  }
]
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: jeff
- Attestation: attest completed
- Date: 2026-04-01

---

**Brief Status:** Completed

**Date Completed:** 2026-04-01

**Evidence Hash:** -
