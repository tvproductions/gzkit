---
id: OBPI-0.0.6-01-ast-scanner
parent: ADR-0.0.6-documentation-cross-coverage-enforcement
item: 1
lane: heavy
status: Completed
---

# OBPI-0.0.6-01: AST Scanner

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/ADR-0.0.6-documentation-cross-coverage-enforcement.md`
- **Checklist Item:** #1 - "AST Scanner -- Discover CLI commands and verify documentation surfaces"

**Status:** Completed

## Objective

Build an AST-driven scanner that discovers every CLI subcommand from argparse
`add_parser()` registrations in `cli/main.py` and verifies each command has all
six required documentation surfaces, producing a structured coverage report.

## Lane

**Heavy** - Extends operator-visible `gz cli audit` output with new verification
checks. Changes command output contract.

## Allowed Paths

- `src/gzkit/commands/cli_audit.py` - extend scanner logic
- `src/gzkit/doc_coverage/` - new module for AST scanning and surface verification
- `tests/commands/test_cli_audit.py` - extend existing tests
- `tests/test_doc_coverage.py` - new scanner tests

## Denied Paths

- `config/doc-coverage.json` - manifest creation is OBPI-02
- `config/gzkit.chores.json` - chore registration is OBPI-03
- `src/gzkit/cli/main.py` - scanner reads this, does not modify it
- `docs/user/` - scanner checks docs, does not create them

## Requirements (FAIL-CLOSED)

1. The scanner MUST discover commands by parsing `cli/main.py` AST, not by
   reading a manual list.
2. The scanner MUST check all six surfaces per command: manpage, index entry,
   operator runbook reference, governance runbook reference, docstring, and
   COMMAND_DOCS mapping.
3. The scanner MUST detect orphaned documentation (docs referencing removed
   commands).
4. The scanner MUST produce a structured `CoverageReport` (Pydantic,
   `frozen=True, extra="forbid"`) with per-command, per-surface pass/fail.
5. The scanner MUST NOT modify any files -- read-only operation.
6. The scanner MUST complete within 10 seconds.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] `src/gzkit/commands/cli_audit.py` - existing scanner logic
- [ ] `src/gzkit/commands/common.py` lines 36-75 - `COMMAND_DOCS` dict
- [ ] `src/gzkit/cli/main.py` - argparse registration structure
- [ ] `docs/user/runbook.md` - operator runbook to scan for references
- [ ] `docs/governance/governance_runbook.md` - governance runbook to scan

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/cli_audit.py` exists
- [ ] `src/gzkit/cli/main.py` uses argparse `add_parser()` calls

**Existing Code (understand current state):**

- [ ] OBPI-0.0.3-09 AST policy tests - prior art for AST scanning
- [ ] `tests/commands/test_cli_audit.py` - existing test patterns

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
- [ ] `docs/user/commands/cli-audit.md` updated with new checks

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification — independent scanner invocation (not gz cli audit)
uv run python -c "from gzkit.doc_coverage.scanner import scan_cli_commands; print(len(scan_cli_commands()))"
uv run python -c "from gzkit.doc_coverage.scanner import check_surfaces; print(check_surfaces().model_dump_json(indent=2))"
uv run -m unittest tests/test_doc_coverage.py -v

# Integration verification (after extending gz cli audit)
uv run gz cli audit
```

## Acceptance Criteria

- [x] **REQ-0.0.6-01-01:** An AST scanner module discovers all CLI subcommands
  from `cli/main.py` without executing the code.
- [x] **REQ-0.0.6-01-02:** The scanner checks all 6 documentation surfaces per
  command and produces a typed `CoverageReport`.
- [x] **REQ-0.0.6-01-03:** Orphaned documentation (manpages for removed commands)
  is detected and reported.
- [x] **REQ-0.0.6-01-04:** `gz cli audit` output includes the new cross-coverage
  checks.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Gate 3 (Docs):** Docs build, cli-audit manpage updated
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 30 tests in 1.211s — OK
Coverage: 86% (threshold: 40%)
```

### Code Quality

```text
Lint: All checks passed
Typecheck: All checks passed
```

### Gate 3 (Docs)

```text
mkdocs build --strict: Documentation built in 0.85 seconds
docs/user/commands/cli-audit.md updated with Cross-Coverage section
```

### Gate 5 (Human)

```text
Attestation: "attest completed" — 2026-03-26
```

### Value Narrative

Before this OBPI, `gz cli audit` only checked COMMAND_DOCS entries against file existence — a manually maintained dict that drifted from reality. Four QC commands were merged without runbook or manpage coverage, caught only by manual audit. Now an AST-driven scanner discovers all 51 CLI subcommands directly from source and verifies six documentation surfaces per command, detecting both gaps and orphaned documentation automatically.

### Key Proof

```bash
$ uv run python -c "from gzkit.doc_coverage.scanner import scan_cli_commands; print(len(scan_cli_commands()))"
51
$ uv run python -c "from gzkit.doc_coverage.scanner import check_surfaces_report; r = check_surfaces_report(); print(f'{r.commands_discovered} commands, {r.commands_fully_covered} covered')"
51 commands, 15 covered
```

### Implementation Summary

- Files created/modified: src/gzkit/doc_coverage/{__init__,models,scanner}.py, src/gzkit/commands/cli_audit.py, docs/user/commands/cli-audit.md
- Tests added: tests/test_doc_coverage.py (25 tests), tests/commands/test_cli_audit.py (5 tests)
- Date completed: 2026-03-26
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: jeff
- Attestation: attest completed
- Date: 2026-03-26

---

**Brief Status:** Completed
**Date Completed:** 2026-03-26
**Evidence Hash:** -
