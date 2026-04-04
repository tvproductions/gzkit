---
id: OBPI-0.0.13-03-manifest-schema-persona-sync
parent: ADR-0.0.13-portable-persona-control-surface
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.13-03-manifest-schema-persona-sync: Manifest Schema Persona Sync

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #3 - "Manifest schema and `gz agent sync` persona mirroring"

**Status:** Draft

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

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full portability context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [ ] OBPI-0.0.13-01 - schema must be finalized
- [ ] OBPI-0.0.13-04 - vendor loading depends on this OBPI's sync targets

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/schemas/manifest.json` exists with current schema
- [ ] `src/gzkit/sync_surfaces.py` exists with `sync_all()` orchestrator
- [ ] `.gzkit/personas/` directory exists with persona files

**Existing Code (understand current state):**

- [ ] Pattern to follow: `sync_skill_mirrors()` in `sync_surfaces.py` - how skills are synced to vendor mirrors
- [ ] Pattern to follow: `generate_manifest()` in `sync_surfaces.py` - how manifest is built from config
- [ ] Schema: `src/gzkit/schemas/manifest.json` - current `control_surfaces` properties
- [ ] Test patterns: `tests/test_sync_surfaces.py` - existing sync tests

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/persona_sync.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.0.13-03-01: Given `src/gzkit/schemas/manifest.json`, when the `control_surfaces` object is inspected, then a `personas` string property with description exists.
- [ ] REQ-0.0.13-03-02: Given `gz agent sync control-surfaces` runs, when `.gzkit/personas/` contains persona files, then `.claude/personas/` is created with mirrored copies.
- [ ] REQ-0.0.13-03-03: Given vendor configuration disables a vendor, when `gz agent sync` runs, then that vendor's persona mirror is not created.
- [ ] REQ-0.0.13-03-04: Given `.gzkit/manifest.json` is regenerated, when inspected, then `control_surfaces.personas` equals `".gzkit/personas"`.
- [ ] REQ-0.0.13-03-05: Given the schema change, when `uv run gz validate --surfaces` runs, then it passes without errors.
- [ ] REQ-0.0.13-03-06: Given persona files in `.gzkit/personas/`, when sync runs and then a persona file is modified in `.gzkit/personas/`, then re-running sync updates the vendor mirror (not stale).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build, command docs updated
- [ ] **Gate 4 (BDD):** Persona sync scenarios pass
- [ ] **Gate 5 (Human):** Human attestation recorded
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

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

### Gate 4 (BDD)

```text
# Paste behave output here
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

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
