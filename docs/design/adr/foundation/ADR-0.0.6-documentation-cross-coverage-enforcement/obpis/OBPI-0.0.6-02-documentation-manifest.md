---
id: OBPI-0.0.6-02-documentation-manifest
parent: ADR-0.0.6-documentation-cross-coverage-enforcement
item: 2
lane: lite
status: attested_completed
---

# OBPI-0.0.6-02: Documentation Manifest

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/ADR-0.0.6-documentation-cross-coverage-enforcement.md`
- **Checklist Item:** #2 - "Documentation Manifest -- Declare per-command documentation obligations"

**Status:** Completed

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

- [x] **REQ-0.0.6-02-01:** `config/doc-coverage.json` exists with an entry for
  every current CLI command.
- [x] **REQ-0.0.6-02-02:** A JSON schema in `data/schemas/` validates the
  manifest structure.
- [x] **REQ-0.0.6-02-03:** A Pydantic loader in `src/gzkit/doc_coverage/`
  deserializes the manifest into typed, immutable models.
- [x] **REQ-0.0.6-02-04:** Each entry declares required surfaces and a
  `governance_relevant` flag.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in brief and parent ADR checklist item #2

### Gate 2 (TDD)

```text
Ran 47 tests in 0.218s — OK (13 manifest-specific)
Coverage: 90% on src/gzkit/doc_coverage/*
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
uv run gz test — 1605 tests OK
```

### Value Narrative

Before this OBPI, documentation obligations per CLI command were implicit — scattered
across scanner logic, the COMMAND_DOCS dict, and individual chores. When new commands
were added, there was no single source declaring which surfaces were required. Now,
`config/doc-coverage.json` is an explicit, schema-validated manifest declaring all 6
documentation surfaces and a governance_relevant flag for every CLI command, loadable
as immutable Pydantic models.

### Key Proof

```bash
uv run python3 -c "
from gzkit.doc_coverage.manifest import load_manifest, find_undeclared_commands
from gzkit.doc_coverage.scanner import scan_cli_commands
m = load_manifest(); cmds = scan_cli_commands()
print(f'{len(m.commands)} declared, {len(cmds)} discovered, '
      f'{len(find_undeclared_commands(m, {c.name for c in cmds}))} undeclared')
"
# Output: 51 declared, 51 discovered, 0 undeclared
```

### Implementation Summary

- Files created: `config/doc-coverage.json`, `data/schemas/doc_coverage_manifest.schema.json`, `src/gzkit/doc_coverage/manifest.py`
- Files modified: `src/gzkit/doc_coverage/__init__.py`, `tests/test_doc_coverage.py`
- Tests added: 30 new tests (4 classes: ManifestModels, LoadManifest, FindUndeclaredCommands, ManifestIntegration)
- Date completed: 2026-03-26
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `attest completed`
- Date: `2026-03-26`

---

**Brief Status:** Completed
**Date Completed:** 2026-03-26
**Evidence Hash:** -
