---
id: OBPI-0.0.6-01-ast-scanner
parent: ADR-0.0.6-documentation-cross-coverage-enforcement
item: 1
lane: heavy
status: Draft
---

# OBPI-0.0.6-01: AST Scanner

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.6-documentation-cross-coverage-enforcement/ADR-0.0.6-documentation-cross-coverage-enforcement.md`
- **Checklist Item:** #1 - "AST Scanner -- Discover CLI commands and verify documentation surfaces"

**Status:** Draft

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

- [ ] **REQ-0.0.6-01-01:** An AST scanner module discovers all CLI subcommands
  from `cli/main.py` without executing the code.
- [ ] **REQ-0.0.6-01-02:** The scanner checks all 6 documentation surfaces per
  command and produces a typed `CoverageReport`.
- [ ] **REQ-0.0.6-01-03:** Orphaned documentation (manpages for removed commands)
  is detected and reported.
- [ ] **REQ-0.0.6-01-04:** `gz cli audit` output includes the new cross-coverage
  checks.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build, cli-audit manpage updated
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
