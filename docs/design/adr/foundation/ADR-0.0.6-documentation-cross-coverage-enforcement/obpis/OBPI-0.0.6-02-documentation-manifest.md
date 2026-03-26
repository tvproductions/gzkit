---
id: OBPI-0.0.6-02-documentation-manifest
parent: ADR-0.0.6-documentation-cross-coverage-enforcement
item: 2
lane: lite
status: Draft
---

# OBPI-0.0.6-02: Documentation Manifest

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/ADR-0.0.6-documentation-cross-coverage-enforcement.md`
- **Checklist Item:** #2 - "Documentation Manifest -- Declare per-command documentation obligations"

**Status:** Draft

## Objective

Create `config/doc-coverage.json` declaring which documentation surfaces are
required for each CLI command, with a governance-relevant flag that triggers
additional runbook checks, so documentation obligations are explicit and
auditable rather than implied by scanner logic.

## Lane

**Lite** - Config file creation only. No CLI, API, or operator-facing changes.
The manifest is consumed by the scanner (OBPI-01) and chore (OBPI-03) but does
not itself change any external surface.

## Allowed Paths

- `config/doc-coverage.json` - manifest file
- `data/schemas/` - manifest JSON schema
- `src/gzkit/doc_coverage/` - manifest loader
- `tests/test_doc_coverage.py` - manifest validation tests

## Denied Paths

- `src/gzkit/commands/cli_audit.py` - scanner integration is OBPI-01
- `config/gzkit.chores.json` - chore registration is OBPI-03
- `docs/user/` - no documentation changes

## Requirements (FAIL-CLOSED)

1. The manifest MUST be valid JSON conforming to a schema in `data/schemas/`.
2. EVERY command discovered by the AST scanner MUST have a manifest entry.
   Commands without entries MUST be flagged as undeclared.
3. Each manifest entry MUST declare which of the 6 surfaces are required for
   that command.
4. A `governance_relevant` boolean flag MUST control whether the governance
   runbook surface is checked.
5. The manifest MUST be loadable by a typed Pydantic model (`frozen=True,
   extra="forbid"`).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] `src/gzkit/commands/common.py` lines 36-75 - existing `COMMAND_DOCS` dict
- [ ] `config/` directory - existing config file patterns
- [ ] `data/schemas/` - existing JSON schema patterns

**Prerequisites (check existence, STOP if missing):**

- [ ] `config/` directory exists
- [ ] `data/schemas/` directory exists

**Existing Code (understand current state):**

- [ ] Other `config/*.json` files - naming and structure conventions

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

# Specific verification
python -c "import json; json.load(open('config/doc-coverage.json'))"
uv run -m unittest tests/test_doc_coverage.py -v -k manifest
```

## Acceptance Criteria

- [ ] **REQ-0.0.6-02-01:** `config/doc-coverage.json` exists with an entry for
  every current CLI command.
- [ ] **REQ-0.0.6-02-02:** A JSON schema in `data/schemas/` validates the
  manifest structure.
- [ ] **REQ-0.0.6-02-03:** A Pydantic loader in `src/gzkit/doc_coverage/`
  deserializes the manifest into typed, immutable models.
- [ ] **REQ-0.0.6-02-04:** Each entry declares required surfaces and a
  `governance_relevant` flag.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
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

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft
**Date Completed:** -
**Evidence Hash:** -
