---
id: OBPI-0.0.11-02-persona-control-surface-definition
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.11-02-persona-control-surface-definition: Persona Control Surface Definition

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #2 - "Persona control surface definition (storage, schema, loading)"

**Status:** Draft

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
1. NEVER: Introduce persona mutation commands or dynamic mid-conversation
   persona switching in this OBPI
1. ALWAYS: Keep the control surface grounded in behavioral identity rather than
   expertise claims

> STOP-on-BLOCKERS: if parser registration, runtime loading points, or the
> governed directory contract cannot be located, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [ ] Research basis: `docs/design/research-persona-selection-agent-identity.md`
- [ ] Related downstream ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/pipeline_runtime.py`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/cli/parser_governance.py`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Pattern to follow: `src/gzkit/pipeline_runtime.py`
- [ ] Pattern to follow: `src/gzkit/cli/parser_governance.py`
- [ ] Test patterns: `tests/test_pipeline_runtime.py`

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

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Runbook updates explain the new control surface and read-only CLI

### Gate 4: BDD (Heavy)

- [ ] Acceptance scenarios pass: `uv run -m behave features/persona.feature`

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

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
uv run gz personas list
test -f src/gzkit/pipeline_runtime.py
test -f src/gzkit/cli/parser_governance.py
```

## Acceptance Criteria

- [ ] REQ-0.0.11-02-01: Persona files live under `.gzkit/personas/` with a documented, governed contract
- [ ] REQ-0.0.11-02-02: `uv run gz personas list` enumerates persona artifacts without mutating them
- [ ] REQ-0.0.11-02-03: Session or dispatch loading consumes persona material from the control surface at the documented lifecycle boundaries
- [ ] REQ-0.0.11-02-04: Heavy-lane evidence includes docs, BDD output, and human attestation before closure

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
# Record test output here during execution.
```

### Code Quality

```text
# Record lint/typecheck output here during execution.
```

### Gate 3 (Docs)

```text
# Record mkdocs output and runbook evidence here during execution.
```

### Gate 4 (BDD)

```text
# Record behave output for features/persona.feature here during execution.
```

### Gate 5 (Human)

```text
# Record human attestation here before closure.
```

### Value Narrative

Before this OBPI, persona behavior was only an ADR concept. After this OBPI,
gzkit has a governed on-disk persona surface, a read-only operator command, and
documented runtime loading boundaries.

### Key Proof

`uv run gz personas list`

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
