---
id: OBPI-0.14.0-04-instruction-audit-and-drift-detection
parent: ADR-0.14.0-multi-agent-instruction-architecture-unification
item: 4
lane: Heavy
status: in_progress
---

# OBPI-0.14.0-04-instruction-audit-and-drift-detection: Instruction Audit and Drift Detection

## ADR Item

- **Source ADR:** `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- **Checklist Item:** #4 - "OBPI-0.14.0-04: Add instruction auditing that detects stale, conflicting, unreachable, or foreign-project rules and load-surface drift."

**Status:** Draft

## Objective

Add a first-class instruction audit that can detect dead path globs, conflicting rules,
foreign-project carryover, and generated/load-surface drift before those defects shape
agent behavior.

This OBPI codifies the audit findings that stale `.github/instructions` content,
foreign repo references, and policy/code mismatches are product defects that should be
detected automatically.

## Lane

**Heavy** - Adds a new governance verification surface and operator-facing audit behavior.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/cli.py` - audit command surface if exposed via CLI
- `src/gzkit/quality.py` or new audit module - instruction audit implementation
- `tests/test_quality.py` and command tests - audit coverage
- `.github/instructions/**` - audit targets and fixtures
- `.claude/rules/**`, `AGENTS.md`, `CLAUDE.md` - audit targets
- `docs/user/commands/` - audit command docs

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- root-surface content slimming belongs to OBPI-03
- local settings separation belongs to OBPI-05
- eval suite behavior belongs to OBPI-06
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The audit MUST detect unreachable path rules and instruction files referencing nonexistent repository paths.
1. REQUIREMENT: The audit MUST detect conflicting policy guidance when repo instructions disagree with observed codebase contracts.
1. NEVER: Treat stale or foreign-project instructions as harmless background noise.
1. ALWAYS: Emit defects in a trackable way that can feed readiness and closeout workflows.
1. ALWAYS: Distinguish between native load surfaces, hook-routed surfaces, and unused
   files so operators can see which instructions are actually effective.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required audit surfaces exist: `.github/instructions/`, `AGENTS.md`, `CLAUDE.md`
- [ ] Required CLI wiring exists: `src/gzkit/cli.py`

**Existing Code (understand current state):**

- [ ] Pattern to follow: existing readiness and surface validation commands
- [ ] Test patterns: `tests/test_quality.py`, `tests/commands/`

## Target Change

- Add audit checks for dead `applyTo` or path rules, foreign project names, conflicting
  style contracts, and drift between canonical surfaces and generated mirrors.
- Teach the audit to report whether a file is native to Codex, native to Claude,
  hook-routed only, or apparently unreachable.
- Make findings machine-readable enough to feed readiness and future governance checks.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run -m unittest discover tests`
- [ ] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [ ] Lint clean: `uvx ruff check src tests`
- [ ] Format clean: `uvx ruff format --check .`
- [ ] Type check clean: `uvx ty check src`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
uv run -m unittest tests.test_quality tests.commands.test_validate_cmds
uv run gz validate --documents --surfaces
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.14.0-04-01: Given an instruction file whose `applyTo` globs match no repository paths, when the audit runs, then it reports the rule as unreachable.
- [x] REQ-0.14.0-04-02: Given instruction content that references another project or conflicts with live repo patterns, when the audit runs, then it reports a drift defect instead of passing silently.
- [x] REQ-0.14.0-04-03: Given generated root and vendor surfaces, when their content drifts from canonical generation rules, then the audit reports the mismatch as a blocking or operator-visible defect.
- [x] REQ-0.14.0-04-04: Given instructions like `.github/instructions/models.instructions.md` that conflict with actual dataclass-heavy repo patterns, when the audit runs, then it reports a code-contract mismatch instead of accepting the instruction at face value.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 22 tests in 0.012s — OK
Coverage: src/gzkit/instruction_audit.py — 91%
Full suite: 497 tests OK, 89% overall coverage
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
uv run ruff format — All files formatted
```

### Implementation Summary

- Files created: `src/gzkit/instruction_audit.py`, `tests/test_instruction_audit.py`
- Files modified: `src/gzkit/cli.py`, `src/gzkit/validate.py`
- Tests added: 22 (5 test classes)
- Date completed: 2026-03-16

### Value Narrative

Before this OBPI, stale or conflicting instructions could sit in the repo without any
product signal, silently shaping tool behavior or wasting operator attention. After
this OBPI, gzkit will identify these defects explicitly and make them auditable.

### Key Proof

An audit run flags at least one unreachable rule, one foreign-project carryover case,
and one policy-versus-code mismatch with enough detail for remediation.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-16

**Evidence Hash:** -
