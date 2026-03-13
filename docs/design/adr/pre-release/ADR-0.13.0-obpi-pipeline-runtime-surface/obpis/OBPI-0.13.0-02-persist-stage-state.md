---
id: OBPI-0.13.0-02-persist-stage-state
parent: ADR-0.13.0-obpi-pipeline-runtime-surface
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.13.0-02-persist-stage-state: Persist Pipeline Stage State

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- **Checklist Item:** #2 - "OBPI-0.13.0-02: Persist pipeline stage state in a repository-local, machine-readable form"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Persist pipeline stage state in a repository-local, machine-readable form.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/module/` - Reason this is in scope
- `tests/test_module.py` - Reason

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `docs/design/**` - ADR changes out of scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: First constraint
1. REQUIREMENT: Second constraint
1. NEVER: What must not happen
1. ALWAYS: What must always be true

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/ADR-0.13.0-obpi-pipeline-runtime-surface.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required file/module exists: `path/to/prerequisite`
- [ ] Required config exists: `config/file.json`

**Existing Code (understand current state):**

- [ ] Pattern to follow: `path/to/exemplar`
- [ ] Test patterns: `tests/path/to/similar_tests.py`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
command --to --verify
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.13.0-02-01: Given/When/Then behavior criterion 1
- [ ] REQ-0.13.0-02-02: Given/When/Then behavior criterion 2
- [ ] REQ-0.13.0-02-03: Given/When/Then behavior criterion 3

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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

## Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

## Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Human Attestation

- Attestor: `human:<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
