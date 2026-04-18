---
id: OBPI-0.0.15-04-dual-format-manifest
parent: ADR-0.0.15-ghi-driven-patch-release-ceremony
item: 4
lane: Lite
status: attested_completed
---

# OBPI-0.0.15-04: Dual-Format Release Manifest

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- **Checklist Item:** #5 - "Dual-format manifest: markdown and JSONL ledger entry with GHI list, cross-validation results, operator approval"

**Status:** Draft

## Objective

Each patch release produces a markdown manifest at `docs/releases/PATCH-vX.Y.Z.md`
and a structured JSONL ledger entry, recording which GHIs were included, their
cross-validation results, and the operator's approval decision.

## Lane

**Lite** - Internal artifact creation; no external contract change.

## Allowed Paths

- `src/gzkit/commands/patch_release.py`
- `src/gzkit/ledger_events.py` (new event type)
- `docs/releases/` (new directory, manifest files)
- `data/schemas/patch_release_manifest.schema.json` (new)
- `tests/adr/test_patch_release.py`

## Denied Paths

- `.gzkit/ledger.jsonl` — only modified by ledger.append at runtime
- `RELEASE_NOTES.md` — handled by ceremony skill (OBPI-05)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Markdown manifest MUST include: version, date, qualifying GHIs
   with cross-validation status, operator approval text, and previous version
2. REQUIREMENT: JSONL entry MUST use a new `patch-release` event type with
   structured fields for machine querying
3. REQUIREMENT: Manifest MUST be written atomically — no partial writes on failure
4. REQUIREMENT: Schema MUST be validated before ledger append

> STOP-on-BLOCKERS: if `docs/releases/` directory creation conflicts with
> mkdocs navigation, resolve nav config first.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- [ ] OBPI-0.0.15-01 through OBPI-0.0.15-03 (prerequisites)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/patch_release.py` exists with discovery logic
- [ ] `src/gzkit/ledger_events.py` exists (event factory pattern)

**Existing Code (understand current state):**

- [ ] Ledger event patterns: `src/gzkit/ledger_events.py`
- [ ] Schema validation patterns: `data/schemas/`
- [ ] Existing manifest patterns (ADR closeout forms)

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

- [ ] REQ-0.0.15-04-01: Markdown manifest written to `docs/releases/PATCH-vX.Y.Z.md`
- [ ] REQ-0.0.15-04-02: JSONL entry uses `patch-release` event type
- [ ] REQ-0.0.15-04-03: Manifest includes GHI list with cross-validation status
- [ ] REQ-0.0.15-04-04: Schema validates before ledger write

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

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


uv run -m unittest tests.adr.test_patch_release.TestPatchReleaseCmdManifest.test_manifest_and_ledger_written -v

### Implementation Summary


- Files created: data/schemas/patch_release_manifest.schema.json
- Files modified: src/gzkit/commands/patch_release.py, src/gzkit/ledger_events.py, tests/adr/test_patch_release.py
- Tests added: 7 test classes (16 tests) covering models, rendering, atomic write, event factory, integration
- Date completed: 2026-04-08
- Attestation status: Completed
- Defects noted: tvproductions/gzkit#115 (ceremony template REQ table)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: completed
- Date: 2026-04-08

---

**Brief Status:** Completed

**Date Completed:** 2026-04-08

**Evidence Hash:** -
