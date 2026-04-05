---
id: OBPI-0.0.13-03-manifest-schema-persona-sync
parent: ADR-0.0.13-portable-persona-control-surface
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.13-03-manifest-schema-persona-sync: Manifest Schema Persona Sync

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #3 - "Manifest schema and `gz agent sync` persona mirroring"

**Status:** Completed

## Objective

Add `control_surfaces.personas` to the manifest schema, update manifest
generation to include the personas path, and extend `gz agent sync
control-surfaces` to mirror persona files from `.gzkit/personas/` to
vendor-specific directories.

## Lane

**Heavy** - Changes the manifest JSON schema contract (`additionalProperties:
false` means adding a new key is a breaking schema change), modifies
`gz agent sync` output behavior, and creates new vendor mirror directories.

## Allowed Paths

- `src/gzkit/schemas/manifest.json` - Add `personas` to control_surfaces schema
- `.gzkit/manifest.json` - Updated by manifest generation
- `src/gzkit/sync_surfaces.py` - Add persona sync function, wire into `sync_all()`
- `src/gzkit/config.py` - Add personas path to PathConfig if needed
- `tests/test_sync_surfaces.py` - Sync tests
- `tests/test_manifest.py` - Manifest schema tests
- `features/persona_sync.feature` - BDD scenarios for sync behavior
- `docs/user/commands/` - Command doc updates for `gz agent sync`
- `docs/governance/governance_runbook.md` - Governance runbook updates

## Denied Paths

- `src/gzkit/commands/personas.py` - Persona CLI is separate (OBPI-05)
- `src/gzkit/commands/init_cmd.py` - Init scaffolding is OBPI-02
- `.gzkit/personas/*.md` - Persona content files (read-only for sync)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Manifest schema MUST add `"personas"` as a string property in `control_surfaces` with description.
2. REQUIREMENT: `generate_manifest()` MUST include `"personas": ".gzkit/personas"` in the `control_surfaces` dict.
3. REQUIREMENT: `sync_all()` MUST call a persona sync function that mirrors `.gzkit/personas/*.md` to enabled vendor surfaces.
4. ALWAYS: Persona sync MUST respect vendor enablement — only mirror to vendors where `config.vendors.{vendor}.enabled` is true.
5. ALWAYS: Vendor mirror paths MUST follow the established pattern: `.claude/personas/`, `.agents/personas/`, `.github/personas/`.
6. NEVER: Persona sync MUST NOT modify canonical persona files in `.gzkit/personas/` — sync is one-directional (canon → mirrors).
7. NEVER: Do not add persona-specific flags to `gz agent sync` — persona syncing is automatic when the surface exists.
8. ALWAYS: Existing `gz validate --surfaces` MUST pass after the schema change.

> STOP-on-BLOCKERS: if OBPI-0.0.13-01 (portable schema) is not complete, print a BLOCKERS list and halt. Persona files must be schema-valid before sync.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand full portability context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [x] OBPI-0.0.13-01 - schema must be finalized
- [x] OBPI-0.0.13-04 - vendor loading depends on this OBPI's sync targets

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/schemas/manifest.json` exists with current schema
- [x] `src/gzkit/sync_surfaces.py` exists with `sync_all()` orchestrator
- [x] `.gzkit/personas/` directory exists with persona files

**Existing Code (understand current state):**

- [x] Pattern to follow: `sync_skill_mirrors()` in `sync_surfaces.py` - how skills are synced to vendor mirrors
- [x] Pattern to follow: `generate_manifest()` in `sync_surfaces.py` - how manifest is built from config
- [x] Schema: `src/gzkit/schemas/manifest.json` - current `control_surfaces` properties
- [x] Test patterns: `tests/test_sync_surfaces.py` - existing sync tests

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/persona_sync.feature`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
# Verify manifest schema accepts personas
uv run gz validate --surfaces
# Verify sync creates vendor mirrors
uv run gz agent sync control-surfaces && ls .claude/personas/ .agents/personas/
# Verify manifest includes personas
python -c "import json; m = json.load(open('.gzkit/manifest.json')); print(m['control_surfaces'].get('personas', 'MISSING'))"
```

## Acceptance Criteria

- [x] REQ-0.0.13-03-01: Given `src/gzkit/schemas/manifest.json`, when the `control_surfaces` object is inspected, then a `personas` string property with description exists.
- [x] REQ-0.0.13-03-02: Given `gz agent sync control-surfaces` runs, when `.gzkit/personas/` contains persona files, then `.claude/personas/` is created with mirrored copies.
- [x] REQ-0.0.13-03-03: Given vendor configuration disables a vendor, when `gz agent sync` runs, then that vendor's persona mirror is not created.
- [x] REQ-0.0.13-03-04: Given `.gzkit/manifest.json` is regenerated, when inspected, then `control_surfaces.personas` equals `".gzkit/personas"`.
- [x] REQ-0.0.13-03-05: Given the schema change, when `uv run gz validate --surfaces` runs, then it passes without errors.
- [x] REQ-0.0.13-03-06: Given persona files in `.gzkit/personas/`, when sync runs and then a persona file is modified in `.gzkit/personas/`, then re-running sync updates the vendor mirror (not stale).

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Gate 3 (Docs):** Docs build, command docs updated
- [x] **Gate 4 (BDD):** Persona sync scenarios pass
- [x] **Gate 5 (Human):** Human attestation recorded
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 2462 tests in 35.825s
OK
Tests passed.
```

### Code Quality

```text
All checks passed!
Lint passed.
Type check passed.
```

### Gate 3 (Docs)

```text
INFO - Documentation built in 1.15 seconds
```

### Gate 4 (BDD)

```text
14 features passed, 0 failed, 0 skipped
90 scenarios passed, 0 failed, 0 skipped
492 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Attestor: jeff
Attestation: attest completed
Date: 2026-04-05
```

### Value Narrative

Before this OBPI, persona files in `.gzkit/personas/` existed in isolation — not registered in the governance manifest, not validated against the manifest schema, and not mirrored to vendor agent surfaces. Now, `gz agent sync control-surfaces` automatically mirrors all persona files to enabled vendor surfaces, and the manifest schema formally recognizes personas as a first-class control surface.

### Key Proof

```bash
$ uv run gz agent sync control-surfaces && ls .claude/personas/
implementer.md  main-session.md  narrator.md
pipeline-orchestrator.md  quality-reviewer.md  spec-reviewer.md

$ python3 -c "import json; m = json.load(open('.gzkit/manifest.json')); print(m['control_surfaces']['personas'])"
.gzkit/personas
```

### Implementation Summary

- Files created: `features/persona_sync.feature`
- Files modified: `src/gzkit/config.py`, `src/gzkit/schemas/manifest.json`, `src/gzkit/sync_surfaces.py`, `src/gzkit/commands/config_paths.py`, `tests/test_manifest_v2.py`, `tests/test_sync_surfaces.py`, `tests/test_sync.py`, `tests/commands/test_audit.py`, `features/steps/gz_steps.py`, `docs/user/commands/agent-sync-control-surfaces.md`
- Tests added: 7 (2 manifest, 5 sync)
- Date completed: 2026-04-05
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed
- Date: 2026-04-05

---

**Brief Status:** Completed

**Date Completed:** 2026-04-05

**Evidence Hash:** -
