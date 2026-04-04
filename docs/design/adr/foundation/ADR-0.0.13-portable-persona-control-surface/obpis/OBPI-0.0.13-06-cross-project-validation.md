---
id: OBPI-0.0.13-06-cross-project-validation
parent: ADR-0.0.13-portable-persona-control-surface
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.0.13-06-cross-project-validation: Cross Project Validation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #6 - "Cross-project validation (apply to airlineops)"

**Status:** Draft

## Objective

Validate persona portability by applying the full persona stack (schema, init
scaffolding, manifest registration, vendor sync, and loading) to the airlineops
repository, proving that the portable persona surface works outside of gzkit.

## Lane

**Heavy** - Cross-project validation affects the airlineops repository's
governance surfaces and contracts. Requires human attestation to confirm the
portability claim holds in a real external consumer.

## Allowed Paths

**In gzkit (this repository):**

- `tests/test_persona_portability.py` - Portability integration tests
- `features/persona_sync.feature` - Cross-project BDD scenarios
- `docs/governance/governance_runbook.md` - Document cross-project persona workflow

**In airlineops (external repository, requires coordination):**

- `../airlineops/.gzkit/personas/` - Persona files bootstrapped by `gz init`
- `../airlineops/.gzkit/manifest.json` - Manifest with personas entry
- `../airlineops/.claude/personas/` - Vendor mirror (Claude)

## Denied Paths

- `src/gzkit/` - No gzkit source changes in this OBPI
- `.gzkit/personas/` - gzkit's own persona files are not the subject
- Any airlineops source code changes beyond governance surface scaffolding

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz init` in airlineops MUST create `.gzkit/personas/` with default persona set.
2. REQUIREMENT: `gz agent sync control-surfaces` in airlineops MUST mirror personas to vendor surfaces.
3. REQUIREMENT: Persona files created in airlineops MUST validate against the portable schema (OBPI-01).
4. ALWAYS: airlineops persona content MUST be project-specific — not copies of gzkit personas.
5. NEVER: gzkit-specific persona content (pipeline-orchestrator references, gzkit skill names) MUST NOT appear in airlineops persona files.
6. ALWAYS: The validation MUST be reproducible — documented as a sequence of commands that anyone can run.
7. NEVER: Do not modify gzkit source to accommodate airlineops-specific needs. If the portable surface doesn't work, the surface is broken, not airlineops.

> STOP-on-BLOCKERS: if OBPIs 01-04 are not complete, print a BLOCKERS list and halt. Cross-project validation requires the full portability stack.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand portability constraint and anti-pattern warning

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [ ] OBPIs 01-04 - all must be complete before this starts
- [ ] airlineops AGENTS.md - understand airlineops governance state

**Prerequisites (check existence, STOP if missing):**

- [ ] `../airlineops/` directory exists and is a gzkit-governed repository
- [ ] gzkit persona portability stack is complete (OBPIs 01-04)
- [ ] airlineops has gzkit installed or available via `uv`

**Existing Code (understand current state):**

- [ ] airlineops `.gzkit/` directory - current governance surfaces
- [ ] airlineops AGENTS.md - persona-like language (catalog per ADR Tidy First plan)
- [ ] gzkit test patterns for cross-project: check if parity scan patterns exist

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
- [ ] Governance runbook updated with cross-project persona workflow

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/persona_sync.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded — portability claim validated in airlineops

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI (run in airlineops)
cd ../airlineops
uv run gz init
ls .gzkit/personas/
uv run gz personas validate
uv run gz agent sync control-surfaces
ls .claude/personas/
uv run gz validate --surfaces
```

## Acceptance Criteria

- [ ] REQ-0.0.13-06-01: Given airlineops with no `.gzkit/personas/`, when `gz init` runs, then `.gzkit/personas/` is created with default persona files.
- [ ] REQ-0.0.13-06-02: Given airlineops persona files, when `gz personas validate` runs, then all pass schema validation.
- [ ] REQ-0.0.13-06-03: Given airlineops with personas, when `gz agent sync control-surfaces` runs, then vendor mirrors are created (`.claude/personas/`).
- [ ] REQ-0.0.13-06-04: Given airlineops persona files, when inspected for gzkit-specific content, then none is found.
- [ ] REQ-0.0.13-06-05: Given the cross-project validation sequence, when documented as a runnable command list, then a human can reproduce the validation from scratch.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Governance runbook updated
- [ ] **Gate 4 (BDD):** Cross-project scenarios pass
- [ ] **Gate 5 (Human):** Human attests portability claim holds
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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here — must confirm portability claim
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
