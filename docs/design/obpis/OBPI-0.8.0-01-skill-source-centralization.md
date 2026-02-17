---
id: OBPI-0.8.0-01-skill-source-centralization
parent: ADR-pool.skill-capability-mirroring
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.8.0-01-skill-source-centralization: Centralize canonical skills in .gzkit and mirror to Claude/Codex/Copilot

## ADR Item

- **Source ADR:** `docs/design/adr/pool/ADR-pool.skill-capability-mirroring.md`
- **Checklist Item:** #1 -- "Define and maintain skill coverage for core gz command surfaces."

**Status:** Completed

## Objective

Shift the canonical skills root to `.gzkit/skills`, mirror skills to `.claude/skills`,
`.codex/skills`, and `.github/skills`, and keep generated control surfaces aligned.

## Lane

**Heavy** -- Changes control-surface contracts and repository path semantics used by agents.

## Allowed Paths

- `src/gzkit/config.py` -- path model and defaults
- `src/gzkit/sync.py` -- canonical + mirror sync behavior
- `src/gzkit/cli.py` -- path audits and sync UX
- `src/gzkit/schemas/manifest.json` -- control-surface schema contract
- `src/gzkit/templates/agents.md` -- generated governance contract content
- `src/gzkit/templates/claude.md` -- generated Claude surface
- `src/gzkit/templates/copilot.md` -- generated Copilot surface
- `tests/test_config.py` -- config defaults/round-trip
- `tests/test_sync.py` -- mirror behavior and catalog rendering
- `tests/test_validate.py` -- manifest schema fixture
- `.gzkit/skills/**` -- canonical skill source
- `.claude/skills/**`, `.codex/skills/**`, `.github/skills/**` -- mirrored outputs

## Denied Paths

- `src/gzkit/ledger.py`
- `src/gzkit/quality.py`
- `features/**`
- External dependencies or lockfile churn unrelated to control-surface migration

## Requirements (FAIL-CLOSED)

1. ALWAYS keep `.gzkit/skills` as canonical skill source for generation and cataloging.
1. ALWAYS mirror canonical skills into Claude, Codex, and Copilot skill paths.
1. ALWAYS preserve backward compatibility by bootstrapping canonical skills from legacy mirror paths when canonical is empty.
1. NEVER require manual copying between agent skill directories.
1. NEVER bypass `gz agent sync control-surfaces` as the source of generated surfaces.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

- [x] Parent ADR reviewed: `docs/design/adr/pool/ADR-pool.skill-capability-mirroring.md`
- [x] Existing sync architecture reviewed in `src/gzkit/sync.py`
- [x] Config path defaults reviewed in `src/gzkit/config.py`
- [x] Manifest schema + path audit behavior reviewed

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run -m unittest discover tests`
- [x] Full quality suite passes: `uv run gz check`

### Code Quality

- [x] Lint clean: `uvx ruff check src tests`
- [x] Format clean: `uvx ruff format --check .`
- [x] Type check clean: `uvx ty check src`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [x] Docs build: `uvx mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] N/A if `features/` absent; explicit rationale captured in status outputs

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run gz check

# Specific verification for this OBPI
uv run gz agent sync control-surfaces
uv run gz check-config-paths
uv run gz status
```

## Acceptance Criteria

<!-- Specific, testable criteria for completion. Checkbox list. -->

- [x] Config defaults place canonical skills under `.gzkit/skills`.
- [x] Sync mirrors canonical skills to Claude, Codex, and Copilot paths.
- [x] Manifest schema and CLI path audits enforce new mirror topology.
- [x] Generated AGENTS/CLAUDE/Copilot surfaces show canonical + three mirrors.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run -m unittest tests.test_config tests.test_validate tests.test_sync tests.test_cli
Ran 124 tests in 1.741s
OK

uv run gz check
Lint: PASS
Format: PASS
Typecheck: PASS
Test: PASS
All checks passed.
```

### Code Quality

```text
uv run gz lint
All checks passed!

uv run gz check
Lint: PASS
Format: PASS
Typecheck: PASS
Test: PASS
All checks passed.

uv run gz check-config-paths
Config-path audit passed.
```

### Implementation Summary

- Files created/modified:
  - `src/gzkit/config.py`
  - `src/gzkit/sync.py`
  - `src/gzkit/cli.py`
  - `src/gzkit/schemas/manifest.json`
  - `src/gzkit/templates/agents.md`
  - `src/gzkit/templates/claude.md`
  - `src/gzkit/templates/copilot.md`
  - `tests/test_config.py`
  - `tests/test_sync.py`
  - `tests/test_validate.py`
  - `tests/test_cli.py`
  - `.gzkit/manifest.json`
  - `AGENTS.md`
  - `CLAUDE.md`
  - `.github/copilot-instructions.md`
- Tests added:
  - `test_sync_mirrors_skills_into_all_tool_directories`
  - `test_sync_bootstraps_canonical_from_legacy_copilot_mirror`
- Date completed: 2026-02-17

---

**Brief Status:** Completed

**Date Completed:** 2026-02-17

**Evidence Hash:** —
