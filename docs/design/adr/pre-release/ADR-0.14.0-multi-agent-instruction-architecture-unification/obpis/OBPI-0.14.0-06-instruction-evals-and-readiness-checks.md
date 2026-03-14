---
id: OBPI-0.14.0-06-instruction-evals-and-readiness-checks
parent: ADR-0.14.0
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.14.0-06-instruction-evals-and-readiness-checks: Instruction Evals and Readiness Checks

## ADR Item

- **Source ADR:** `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- **Checklist Item:** #6 - "OBPI-0.14.0-06: Add an instruction-architecture eval suite and readiness checks with positive and negative controls across supported agent surfaces."

**Status:** Draft

## Objective

Create an instruction-architecture eval/readiness layer that exercises positive and
negative controls across supported agent surfaces so gzkit can verify behavior, not
just scaffold files.

This OBPI turns the audit recommendations into a repeatable eval harness so future
instruction changes can be checked against real multi-agent behaviors instead of only
surface presence.

## Lane

**Heavy** - Adds new quality/readiness behavior for externally consumed agent surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `tests/` - instruction eval fixtures and assertions
- `tests/commands/` - command-facing readiness coverage
- `src/gzkit/cli.py` or readiness modules - eval/readiness command integration if exposed
- `src/gzkit/quality.py` - readiness checks
- `docs/user/commands/readiness-audit.md` and related docs - operator guidance
- generated control surfaces and rule directories - eval subjects

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- broad audit detection logic belongs to OBPI-04
- surface content refactoring belongs to OBPI-01 through OBPI-03
- local config handling belongs to OBPI-05
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: The eval set MUST include positive and negative controls, not only happy-path checks.
1. REQUIREMENT: Readiness checks MUST cover outcome, process, style, and efficiency dimensions for instruction surfaces.
1. NEVER: Treat file presence alone as proof that the instruction architecture works.
1. ALWAYS: Keep eval prompts representative of real multi-agent repo tasks.
1. ALWAYS: Include both Codex-native and Claude-native loading behaviors in the eval
   model instead of assuming the tools behave identically.

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

- [ ] Required readiness surfaces exist: generated root files and instruction/rule directories
- [ ] Required test harness exists: `tests/`

**Existing Code (understand current state):**

- [ ] Pattern to follow: existing readiness audit and quality command surfaces
- [ ] Test patterns: command and quality tests under `tests/`

## Target Change

- Add a minimal instruction eval suite with ten prompts, including positive and
  negative controls for Codex and Claude views.
- Make readiness checks score more than existence: outcome, process, style, and
  efficiency all need explicit signal.
- Ensure future subproject-specific rules can be added to the eval set incrementally.

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
uv run -m unittest discover tests
uv run gz readiness audit
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.14.0-06-01: Given representative instruction prompts, when the eval/readiness suite runs, then it exercises both positive and negative controls across supported agent surfaces.
- [ ] REQ-0.14.0-06-02: Given generated instruction architecture changes, when readiness runs, then it reports failures in outcome, process, style, or efficiency dimensions instead of only checking file existence.
- [ ] REQ-0.14.0-06-03: Given future subproject-specific rules, when the eval suite is extended, then the new cases can be added without rewriting the whole readiness model.
- [ ] REQ-0.14.0-06-04: Given the recommended ten-prompt baseline suite, when readiness is executed, then it covers at least one positive and one negative control for each of Codex loading, Claude loading, workflow relocation, and drift detection behavior.

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

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:

## Value Narrative

Before this OBPI, gzkit could generate instruction files but had limited proof that the
surfaces produced the intended agent behavior. After this OBPI, instruction changes can
be evaluated using a stable, extensible behavioral suite.

## Key Proof

`uv run gz readiness audit` executes a baseline ten-prompt suite that catches both a
passing positive control and a failing negative control for the supported instruction
architecture.

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -

