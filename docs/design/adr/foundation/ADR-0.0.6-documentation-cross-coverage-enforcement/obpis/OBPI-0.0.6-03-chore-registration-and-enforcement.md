---
id: OBPI-0.0.6-03-chore-registration-and-enforcement
parent: ADR-0.0.6-documentation-cross-coverage-enforcement
item: 3
lane: heavy
status: Draft
---

# OBPI-0.0.6-03: Chore Registration and Enforcement

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/ADR-0.0.6-documentation-cross-coverage-enforcement.md`
- **Checklist Item:** #3 - "Chore Registration and Enforcement -- Register as chore, produce actionable gap report"

**Status:** Draft

## Objective

Register `doc-coverage` as a `gz chores` item that runs the AST scanner against
the documentation manifest and produces a structured, actionable gap report with
pass/fail enforcement, so documentation obligations are checked as part of
regular maintenance.

## Lane

**Heavy** - Adds a new chore to the `gz chores` interface, changing the
operator-visible chore catalog. Produces a new enforcement surface.

## Allowed Paths

- `config/gzkit.chores.json` - chore registration
- `ops/chores/doc-coverage/` - chore definition (CHORE.md)
- `src/gzkit/doc_coverage/` - chore runner logic (gap report, enforcement)
- `tests/test_doc_coverage.py` - chore integration tests

## Denied Paths

- `src/gzkit/commands/cli_audit.py` - scanner extension is OBPI-01
- `config/doc-coverage.json` - manifest creation is OBPI-02
- `src/gzkit/cli/main.py` - no CLI parser changes

## Requirements (FAIL-CLOSED)

1. The chore MUST be registered in `config/gzkit.chores.json` with slug
   `doc-coverage` and frequency `per-release`.
2. `gz chores run doc-coverage` MUST produce a structured report listing every
   gap (command, missing surface, expected path).
3. The chore MUST fail (exit 1) when any required surface is missing.
4. The chore MUST succeed (exit 0) when all required surfaces are present.
5. The gap report MUST be machine-readable (JSON to stdout with `--json` flag).
6. The `--json` output MUST conform to a schema in `data/schemas/doc-coverage-report.schema.json`.
7. The chore runner MUST load the manifest (OBPI-02) and invoke the scanner
   (OBPI-01) -- not duplicate their logic.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] `config/gzkit.chores.json` - existing chore registry structure
- [ ] `ops/chores/validate-manpages/CHORE.md` - existing chore definition pattern
- [ ] `src/gzkit/commands/chores_cmd.py` - chore runner infrastructure

**Prerequisites (check existence, STOP if missing):**

- [ ] Scanner module from OBPI-01 exists in `src/gzkit/doc_coverage/`
- [ ] Manifest from OBPI-02 exists at `config/doc-coverage.json`
- [ ] `config/gzkit.chores.json` exists

**Existing Code (understand current state):**

- [ ] Other chore definitions in `ops/chores/` - CHORE.md patterns
- [ ] `src/gzkit/commands/chores_cmd.py` - how chores are dispatched

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
- [ ] Chore documented in operator runbook or chore catalog

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification
uv run gz chores list | grep doc-coverage
uv run gz chores run doc-coverage
uv run gz chores run doc-coverage --json
```

## Acceptance Criteria

- [ ] **REQ-0.0.6-03-01:** `doc-coverage` chore is registered in
  `config/gzkit.chores.json` with `per-release` frequency.
- [ ] **REQ-0.0.6-03-02:** `gz chores run doc-coverage` produces a human-readable
  gap report listing each missing surface with the expected path.
- [ ] **REQ-0.0.6-03-03:** The chore exits 1 when gaps exist and 0 when all
  surfaces are present.
- [ ] **REQ-0.0.6-03-04:** `--json` flag produces machine-readable JSON output
  to stdout.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build, chore documented
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

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

### Gate 5 (Human)

```text
# Record attestation text here
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

_No defects tracked._

## Human Attestation

- Attestor:
- Attestation:
- Date:

---

**Brief Status:** Draft
**Date Completed:** -
**Evidence Hash:** -
