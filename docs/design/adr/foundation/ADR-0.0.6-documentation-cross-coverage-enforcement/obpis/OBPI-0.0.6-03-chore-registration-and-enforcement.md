---
id: OBPI-0.0.6-03-chore-registration-and-enforcement
parent: ADR-0.0.6-documentation-cross-coverage-enforcement
item: 3
lane: heavy
status: in_progress
---

# OBPI-0.0.6-03: Chore Registration and Enforcement

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/ADR-0.0.6-documentation-cross-coverage-enforcement.md`
- **Checklist Item:** #3 - "Chore Registration and Enforcement -- Register as chore, produce actionable gap report"

**Status:** Completed

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

- [x] **REQ-0.0.6-03-01:** `doc-coverage` chore is registered in
  `config/gzkit.chores.json` with `per-release` frequency.
- [x] **REQ-0.0.6-03-02:** `gz chores run doc-coverage` produces a human-readable
  gap report listing each missing surface with the expected path.
- [x] **REQ-0.0.6-03-03:** The chore exits 1 when gaps exist and 0 when all
  surfaces are present.
- [x] **REQ-0.0.6-03-04:** `--json` flag produces machine-readable JSON output
  to stdout.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Gate 3 (Docs):** Docs build, chore documented
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 62 tests in 1.199s — OK
Coverage: 90% (src/gzkit/doc_coverage/*)
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Gate 3 (Docs)

```text
uv run gz validate --documents — All validations passed
uv run mkdocs build --strict — Built in 0.95s, no warnings
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-26
```

### Value Narrative

Before this OBPI, documentation obligations were checked piecemeal — no single
tool enforced the full documentation contract across all required surfaces for
every command. Now, `gz chores run doc-coverage` loads the manifest, invokes the
AST scanner, and produces an actionable gap report that fails closed on missing
required surfaces.

### Key Proof

```bash
$ uv run gz chores run doc-coverage
Chore criterion failed:
- chore: doc-coverage
- criterion: uv run -m gzkit.doc_coverage.runner
- detail: exit 1 != 0
# Correctly detects 77 pre-existing documentation gaps across 36 commands.

$ uv run -m gzkit.doc_coverage.runner --json | python3 -c "import json,sys; d=json.load(sys.stdin); print(f'gaps={len(d[\"gaps\"])} checked={d[\"commands_checked\"]}')"
gaps=77 checked=52
```

### Implementation Summary

- Files created: `src/gzkit/doc_coverage/runner.py`, `data/schemas/doc-coverage-report.schema.json`, `ops/chores/doc-coverage/{CHORE.md,acceptance.json,README.md,proofs/.gitkeep}`
- Files modified: `src/gzkit/doc_coverage/models.py`, `src/gzkit/doc_coverage/__init__.py`, `config/gzkit.chores.json`, `tests/test_doc_coverage.py`
- Tests added: 16 (gap report models, runner integration, chore registration)
- Date completed: 2026-03-26
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: Jeff
- Attestation: attest completed
- Date: 2026-03-26

---

**Brief Status:** Completed
**Date Completed:** 2026-03-26
**Evidence Hash:** -
