---
id: OBPI-0.14.0-05-local-vs-repo-config-and-sync-determinism
parent: ADR-0.14.0-multi-agent-instruction-architecture-unification
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.14.0-05-local-vs-repo-config-and-sync-determinism: Local vs Repo Config and Sync Determinism

## ADR Item

- **Source ADR:** `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- **Checklist Item:** #5 - "OBPI-0.14.0-05: Separate machine-local from repo-local agent config and enforce deterministic generated-surface sync across adapters and mirrors."

**Status:** Draft

## Objective

Separate machine-local agent configuration from repo-tracked control surfaces and
make generated adapter sync deterministic enough that checked-in surfaces can be trusted.

This OBPI addresses the current tracked `.claude/settings.local.json` surface and the
observed drift between checked-in `.claude/settings.json` and the visible
generator/test contract.

## Lane

**Heavy** - Changes tracked agent config policy and sync guarantees seen by operators.
Heavy rather than Lite because the sync determinism guarantee and local-config
separation change operator-visible `.claude/settings.json` contract behavior and
affect how external agent tools discover project policy.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `.gitignore` - local config ignore rules
- `.claude/settings.json` - tracked project settings contract
- `.claude/settings.local.json` or example files - local-only handling
- `src/gzkit/hooks/claude.py` - Claude settings generation
- `src/gzkit/sync.py` - deterministic sync integration
- `tests/test_hooks.py` and `tests/test_sync.py` - generator and sync coverage
- `docs/user/commands/agent-sync-control-surfaces.md` - operator guidance

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- instruction-audit feature work belongs to OBPI-04
- path-scoped rule architecture belongs to OBPI-02
- full eval suite belongs to OBPI-06
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Machine-local config MUST have an explicit non-tracked home or example-file pattern.
1. REQUIREMENT: Generated tracked settings MUST match the current generator and tests.
1. NEVER: Check in `.local` agent permission/config files as if they were shared policy.
1. ALWAYS: Surface-sync commands MUST verify deterministic outputs for unchanged inputs.
1. ALWAYS: Separate shared project settings from per-machine allowances so repository
   policy and workstation convenience do not drift together.

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

- [ ] Required generator exists: `src/gzkit/hooks/claude.py`
- [ ] Required sync integration exists: `src/gzkit/sync.py`

**Existing Code (understand current state):**

- [ ] Pattern to follow: current hook generation tests
- [ ] Test patterns: `tests/test_hooks.py`, `tests/test_sync.py`

## Target Change

- Move local-only Claude settings toward ignore-listed or example-file handling.
- Make `.claude/settings.json` a deterministic render of current hook generation logic.
- Add sync or validation checks that fail when tracked surfaces drift from generator
  output.

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
uv run -m unittest tests.test_hooks tests.test_sync
uv run gz agent sync control-surfaces --dry-run
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.14.0-05-01: Given machine-local Claude permissions or settings, when gzkit initializes or syncs a repo, then local-only config is kept out of tracked shared policy surfaces.
- [ ] REQ-0.14.0-05-02: Given the checked-in Claude settings surface, when tests and generation run, then the generated output matches the tracked file exactly.
- [ ] REQ-0.14.0-05-03: Given unchanged canonical inputs, when surface sync runs repeatedly, then tracked adapter files and mirrors remain deterministic and drift is reported when not.
- [ ] REQ-0.14.0-05-04: Given a repository bootstrap or sync, when local config scaffolding is generated, then operators receive a safe local example pattern rather than a tracked `.local` policy file.

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

Before this OBPI, machine-local permissions and checked-in settings could blur
together, weakening trust in generated surfaces. After this OBPI, repo policy and
local workstation state will be separated and deterministic sync will become
enforceable.

## Key Proof

Running surface generation reproduces the tracked `.claude/settings.json` exactly while
leaving local-only settings untracked or example-based.

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
