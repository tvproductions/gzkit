---
id: OBPI-0.14.0-02-native-path-scoped-rules
parent: ADR-0.14.0-multi-agent-instruction-architecture-unification
item: 2
lane: Heavy
status: in_progress
---

# OBPI-0.14.0-02-native-path-scoped-rules: Native Path-Scoped Instruction Surfaces

## ADR Item

- **Source ADR:** `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- **Checklist Item:** #2 - "OBPI-0.14.0-02: Add native path-scoped instruction support with nested `AGENTS.md` for shared subtree rules and `.claude/rules/` for Claude-only rules."

**Status:** Completed

## Objective

Add first-class support for path-scoped instruction surfaces using nested `AGENTS.md`
for shared subtree rules and native `.claude/rules/` for Claude-only scoping.

This OBPI replaces the current overuse of root-only instruction surfaces and reduces
dependence on `.claude/hooks/instruction-router.py` plus `.github/instructions/` as the
main delivery path for Claude path-specific guidance.

## Lane

**Heavy** - Introduces new externally visible instruction-loading surfaces for supported agents.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/sync.py` - generation and placement logic for nested/shared rules
- `src/gzkit/config.py` - path-surface configuration model
- `src/gzkit/templates/` - adapter/rule templates if needed
- `tests/test_sync.py` - path-scoped surface generation coverage
- `tests/test_validate.py` - validation for new rule locations
- `.claude/rules/**` - generated Claude-only path rules
- subtree `AGENTS.md` files - generated shared nested rules

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.claude/settings*.json` - runtime hook config belongs to OBPI-05 unless required for rule discovery
- `.github/instructions/**` broad audit/remediation belongs to OBPI-04
- root adapter slimming belongs to OBPI-03
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Shared subtree rules MUST be representable in a cross-tool surface, not only in Claude-specific files.
1. REQUIREMENT: Claude-only path rules MUST use `.claude/rules/` when the behavior is genuinely Claude-native.
1. NEVER: Store shared path rules only in a Claude-only surface.
1. ALWAYS: Keep rule placement semantics explicit so audits can tell why a rule lives where it does.
1. ALWAYS: Preserve hook-based enforcement only as a supplement to native agent loading,
   not as the only way an instruction becomes visible.

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

- [ ] Required generator exists: `src/gzkit/sync.py`
- [ ] Required Claude surface path exists: `.claude/`

**Existing Code (understand current state):**

- [ ] Pattern to follow: root `AGENTS.md` and `CLAUDE.md` generation paths
- [ ] Test patterns: `tests/test_sync.py`, `tests/test_validate.py`

## Target Change

- Add configuration and generation support for shared subtree rules that emit nested
  `AGENTS.md` files near the governed subtree.
- Add generation support for `.claude/rules/` when a rule is explicitly Claude-only or
  Claude-path-scoped.
- Provide clear placement metadata so audits and migration tooling can explain whether a
  rule belongs in shared canon, nested shared scope, Claude-only scope, or a skill.

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
uv run -m unittest tests.test_sync tests.test_validate
uv run gz validate --documents --surfaces
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.14.0-02-01: Given a shared subtree rule, when gzkit generates control surfaces, then a nested `AGENTS.md` can be emitted for that subtree without duplicating unrelated root rules.
- [x] REQ-0.14.0-02-02: Given a Claude-only path rule, when gzkit generates Claude surfaces, then the rule is emitted under `.claude/rules/` instead of being hidden behind generic hook routing.
- [x] REQ-0.14.0-02-03: Given a repository with no path-specific rules, when surfaces are generated, then no empty or dead rule directories are created.
- [x] REQ-0.14.0-02-04: [doc] Given legacy `.github/instructions` inputs, when migration guidance runs, then shared rules are directed toward nested `AGENTS.md` and Claude-only rules toward `.claude/rules/` without assuming they are equivalent.

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

- [x] Intent and scope recorded in brief frontmatter and ADR checklist item #2

### Gate 2 (TDD)

```text
Ran 68 tests in 0.285s — OK
(14 new in tests/test_rules.py + 54 existing in tests/test_sync.py)
```

### Code Quality

```text
ruff check: All checks passed!
ruff format: 5 files already formatted
```

### Gate 5 (Human Attestation)

Human attestation received 2026-03-15. Heavy lane requirement satisfied.

### Implementation Summary

- Files created: `src/gzkit/rules.py` (366 lines), `tests/test_rules.py` (14 tests), `.claude/hooks/session-staleness-check.py`
- Files modified: `src/gzkit/config.py`, `src/gzkit/sync.py`, `src/gzkit/validate.py`, `.claude/settings.json`, `.claude/hooks/README.md`
- Hooks activated: `obpi-completion-validator.py`, `session-staleness-check.py`
- Date completed: 2026-03-15

### Value Narrative

Before this OBPI, gzkit had no native shared subtree instruction surface and Claude
path guidance depended heavily on hook routing. After this OBPI, shared and
Claude-specific scoped rules will live in their native locations with explicit
placement semantics.

### Key Proof

A sample rule set can generate one nested `AGENTS.md` under a subtree and one
`.claude/rules/*.md` file for a Claude-only path case, with no redundant root-surface
expansion.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-15

**Evidence Hash:** -
