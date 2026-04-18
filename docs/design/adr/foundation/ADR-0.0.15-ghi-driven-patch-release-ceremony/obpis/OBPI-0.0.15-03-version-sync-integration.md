---
id: OBPI-0.0.15-03-version-sync-integration
parent: ADR-0.0.15-ghi-driven-patch-release-ceremony
item: 3
lane: Lite
status: attested_completed
---

# OBPI-0.0.15-03: Version Sync Integration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- **Checklist Item:** #4 - "Version sync integration: call `sync_project_version` for patch increment"

**Status:** Draft

## Objective

`gz patch release` computes the next patch version from the current version,
calls `sync_project_version` to update all version locations atomically, and
reports what changed.

## Lane

**Lite** - Reuses existing version sync infrastructure; no new external contract.

## Allowed Paths

- `src/gzkit/commands/patch_release.py`
- `src/gzkit/commands/closeout.py` (read `sync_project_version`; refactor to
  shared location if needed)
- `src/gzkit/commands/version_sync.py` (new, if extraction needed)
- `tests/adr/test_patch_release.py`

## Denied Paths

- `pyproject.toml` — only modified by `sync_project_version` at runtime
- `src/gzkit/__init__.py` — only modified by `sync_project_version` at runtime

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Version bump MUST call `sync_project_version` — NEVER directly
   edit pyproject.toml or `__init__.py`
2. REQUIREMENT: Patch increment MUST compute `X.Y.(Z+1)` from the current
   version in pyproject.toml
3. REQUIREMENT: If `sync_project_version` is tightly coupled to closeout,
   it MUST be extracted to a shared module before use
4. REQUIREMENT: `--dry-run` MUST show the proposed version without modifying
   any files

> STOP-on-BLOCKERS: if `sync_project_version` cannot accept arbitrary version
> strings, refactor it first.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- [ ] OBPI-0.0.15-01 and OBPI-0.0.15-02 (prerequisites)

**Prerequisites (check existence, STOP if missing):**

- [ ] `sync_project_version` exists in `src/gzkit/commands/closeout.py`
- [ ] `src/gzkit/commands/patch_release.py` exists (from OBPI-01)

**Existing Code (understand current state):**

- [ ] `sync_project_version` signature and behavior: `src/gzkit/commands/closeout.py`
- [ ] Current version reading pattern in closeout

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
uv run gz patch release --dry-run
```

## Acceptance Criteria

- [ ] REQ-0.0.15-03-01: Calls `sync_project_version` for version bump
- [ ] REQ-0.0.15-03-02: Computes correct patch increment (X.Y.Z+1)
- [ ] REQ-0.0.15-03-03: `--dry-run` shows version without modifying files
- [ ] REQ-0.0.15-03-04: No second version-sync code path exists

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief

### Gate 2 (TDD)

```text
Ran 31 tests in 0.097s — OK
10 new tests for OBPI-03 (compute_patch_increment, dry-run version, execute sync, no-version handling)
```

### Code Quality

```text
Lint: All checks passed
Typecheck: Type check passed (1 pre-existing warning in personas.py)
Tests: 2672 pass
```

### Value Narrative

Before this OBPI, `gz patch release` could discover GHIs but had no version bump capability. The non-dry-run path printed a placeholder message. Now the command computes X.Y.(Z+1) from pyproject.toml and atomically updates all version locations via `sync_project_version`, preventing the version drift pattern that motivated ADR-0.0.15.

### Key Proof


`uv run gz patch release --dry-run` shows current version, proposed patch version, and discovered GHIs without modifying files. Non-dry-run calls `sync_project_version` atomically.

### Implementation Summary


- Files modified: `src/gzkit/commands/version_sync.py` (added `compute_patch_increment`), `src/gzkit/commands/patch_release.py` (integrated version sync), `tests/adr/test_patch_release.py` (10 new tests, 3 existing tests updated)
- Tests added: TestComputePatchIncrement, TestPatchReleaseDryRunVersion, TestPatchReleaseExecutesVersionSync, TestPatchReleaseNoVersion
- Date completed: 2026-04-08
- Attestation status: Pending
- Defects noted: #113 (pipeline REQ coverage table), #114 (resolve_obpi slug mismatch)

## Tracked Defects

- #113: Pipeline skill should verify @covers decorators on REQ tests
- #114: resolve_obpi prefix match creates short-vs-full slug mismatch

## Human Attestation

- Attestor: `Jeffry`
- Attestation: ok
- Date: 2026-04-08

---

**Brief Status:** Completed

**Date Completed:** 2026-04-08

**Evidence Hash:** -
