---
id: OBPI-0.14.0-06-instruction-evals-and-readiness-checks
parent: ADR-0.14.0-multi-agent-instruction-architecture-unification
item: 6
lane: Heavy
status: attested_completed
---

# OBPI-0.14.0-06-instruction-evals-and-readiness-checks: Instruction Evals and Readiness Checks

## ADR Item

- **Source ADR:** `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- **Checklist Item:** #6 - "OBPI-0.14.0-06: Add an instruction-architecture eval suite and readiness checks with positive and negative controls across supported agent surfaces."

**Status:** Completed

## Objective

Create an instruction-architecture eval/readiness layer that exercises positive and
negative controls across supported agent surfaces so gzkit can verify behavior, not
just scaffold files.

This OBPI turns the audit recommendations into a repeatable eval harness so future
instruction changes can be checked against real multi-agent behaviors instead of only
surface presence.

## Lane

**Heavy** - Adds new quality/readiness behavior for externally consumed agent surfaces.
Heavy rather than Lite because the readiness command produces operator-facing output
and defines pass/fail criteria for externally consumed instruction surfaces.

## Prerequisites

- **OBPI-0.14.0-01** must be complete (canonical instruction model provides the
  surfaces that evals exercise).
- **OBPI-0.14.0-04** must be complete (audit detection logic provides the drift
  and defect signals that readiness checks validate against).

## Allowed Paths

- `tests/` - instruction eval fixtures and assertions
- `tests/commands/` - command-facing readiness coverage
- `src/gzkit/cli.py` or readiness modules - eval/readiness command integration if exposed
- `src/gzkit/quality.py` - readiness checks
- `docs/user/commands/readiness-audit.md` and related docs - operator guidance
- generated control surfaces and rule directories - eval subjects

## Denied Paths

- broad audit detection logic belongs to OBPI-04
- surface content refactoring belongs to OBPI-01 through OBPI-03
- local config handling belongs to OBPI-05
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The eval set MUST include positive and negative controls, not only happy-path checks.
1. REQUIREMENT: Readiness checks MUST cover outcome, process, style, and efficiency dimensions for instruction surfaces.
1. NEVER: Treat file presence alone as proof that the instruction architecture works.
1. ALWAYS: Keep eval prompts representative of real multi-agent repo tasks.
1. ALWAYS: Include both Codex-native and Claude-native loading behaviors in the eval
   model instead of assuming the tools behave identically.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- [x] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [x] Required readiness surfaces exist: generated root files and instruction/rule directories
- [x] Required test harness exists: `tests/`

**Existing Code (understand current state):**

- [x] Pattern to follow: existing readiness audit and quality command surfaces
- [x] Test patterns: command and quality tests under `tests/`

## Target Change

- Add a minimal instruction eval suite with ten prompts, including positive and
  negative controls for Codex and Claude views.
- Make readiness checks score more than existence: outcome, process, style, and
  efficiency all need explicit signal.
- Ensure future subproject-specific rules can be added to the eval set incrementally.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run -m unittest discover tests`
- [x] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [x] Lint clean: `uvx ruff check src tests`
- [x] Format clean: `uvx ruff format --check .`
- [x] Type check clean: `uvx ty check src`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uvx mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
uv run -m unittest tests/test_instruction_eval.py -v
uv run gz readiness eval
uv run gz readiness audit
```

## Acceptance Criteria

- [x] REQ-0.14.0-06-01: Given representative instruction prompts, when the eval/readiness suite runs, then it exercises both positive and negative controls across supported agent surfaces.
- [x] REQ-0.14.0-06-02: Given generated instruction architecture changes, when readiness runs, then it reports failures in outcome, process, style, or efficiency dimensions instead of only checking file existence.
- [x] REQ-0.14.0-06-03: Given future subproject-specific rules, when the eval suite is extended, then the new cases can be added without rewriting the whole readiness model.
- [x] REQ-0.14.0-06-04: Given the recommended ten-prompt baseline suite, when readiness is executed, then it covers at least one positive and one negative control for each of Codex loading, Claude loading, workflow relocation, and drift detection behavior.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 15 tests in 0.017s — OK
Coverage: src/gzkit/instruction_eval.py — 87%
Full suite: 532 tests in 12.1s — OK
```

### Code Quality

```text
Lint: All checks passed!
Typecheck: All checks passed!
Format: All files unchanged
mkdocs build --strict: Documentation built in 0.99 seconds
```

### Implementation Summary

- Files created: `src/gzkit/instruction_eval.py`, `tests/test_instruction_eval.py`, `docs/user/commands/readiness-eval.md`
- Files modified: `src/gzkit/cli.py`, `src/gzkit/commands/common.py`, `tests/commands/test_audit.py`
- Tests added: 15 (TestBaselineCases: 6, TestRunEvalSuite: 8, TestExtensibility: 1)
- Date completed: 2026-03-17

### Value Narrative

Before this OBPI, gzkit could generate instruction files but had limited proof that the
surfaces produced the intended agent behavior. After this OBPI, instruction changes can
be evaluated using a stable, extensible behavioral suite that scores across outcome,
process, style, and efficiency dimensions with both positive and negative controls.

### Key Proof

`uv run gz readiness eval` executes a baseline ten-prompt suite that catches both a
passing positive control and a failing negative control for the supported instruction
architecture. `uv run gz readiness audit` now includes an "Eval Dimensions (Behavioral)"
table alongside the existing discipline and primitive tables.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-17

**Evidence Hash:** -

## Human Attestation

- **Attestor:** Jeff (project operator)
- **Attestation:** "attest completed"
- **Date:** 2026-03-17
