---
id: OBPI-0.0.13-04-vendor-neutral-persona-loading
parent: ADR-0.0.13-portable-persona-control-surface
item: 4
lane: Lite
status: Draft
---

# OBPI-0.0.13-04-vendor-neutral-persona-loading: Vendor Neutral Persona Loading

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #4 - "Vendor-neutral persona loading (Claude, Codex, Copilot adapters)"

**Status:** Draft

## Objective

Create vendor adapter functions that translate canonical persona frames into
vendor-specific formats (system prompt fragments for Claude, instruction blocks
for Codex, instruction file entries for Copilot), so persona identity is
consumed correctly regardless of which agent runtime loads it.

## Lane

**Lite** - Creates internal adapter functions consumed by the sync pipeline
(OBPI-03). Does not add CLI commands, change APIs, or modify operator-facing
contracts. Vendor mirror files are an implementation detail of sync, not a
user-facing surface.

## Allowed Paths

- `src/gzkit/personas.py` - Add vendor adapter functions alongside existing `compose_persona_frame()`
- `src/gzkit/sync_surfaces.py` - Wire adapters into persona sync (if not already done in OBPI-03)
- `tests/test_persona_loading.py` - Adapter unit tests
- `tests/test_personas.py` - Existing persona tests (extend if needed)

## Denied Paths

- `src/gzkit/commands/` - No CLI changes
- `src/gzkit/schemas/` - Schema is OBPI-01
- `.gzkit/personas/` - Canon files are read-only
- `.claude/`, `.agents/`, `.github/` - Vendor mirrors written by sync, not by adapters directly

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Each vendor adapter MUST accept a `PersonaFrontmatter` + body markdown and return a formatted string in the vendor's native format.
2. REQUIREMENT: Claude adapter MUST produce a system prompt fragment that includes traits, grounding, and anti-traits as behavioral constraints.
3. REQUIREMENT: Codex adapter MUST produce an AGENTS.md-compatible instruction block.
4. REQUIREMENT: Copilot adapter MUST produce a `.github/copilot-instructions.md`-compatible fragment.
5. ALWAYS: Adapters MUST be pure functions — no file I/O, no side effects, no vendor API calls.
6. NEVER: Adapters MUST NOT modify or interpret persona content — they translate format, not meaning.
7. ALWAYS: If a vendor has no adapter, sync MUST fall back to copying the raw canonical markdown file.
8. NEVER: Do not add vendor-specific persona variants — one canonical source, multiple format translations.

> STOP-on-BLOCKERS: if OBPI-0.0.13-01 (schema) is not complete, print a BLOCKERS list and halt. Adapters depend on the PersonaFrontmatter model being stable.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand vendor neutrality constraint

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [ ] OBPI-0.0.13-01 - schema and PersonaFrontmatter model
- [ ] OBPI-0.0.13-03 - sync pipeline that will call these adapters

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/models/persona.py` exists with stable `PersonaFrontmatter`
- [ ] `src/gzkit/personas.py` exists with `compose_persona_frame()`
- [ ] `.gzkit/personas/` has persona files to test against

**Existing Code (understand current state):**

- [ ] Pattern to follow: `compose_persona_frame()` in `src/gzkit/personas.py` - existing composition logic
- [ ] Pattern to follow: vendor-specific rendering in `sync_surfaces.py` - how rules/skills are formatted per vendor
- [ ] Test patterns: `tests/test_personas.py` or `tests/commands/test_personas_cmd.py`

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

# Specific verification for this OBPI
python -c "from gzkit.personas import render_persona_claude, render_persona_codex, render_persona_copilot; print('All adapters importable')"
uv run -m unittest tests.test_persona_loading -v
```

## Acceptance Criteria

- [ ] REQ-0.0.13-04-01: Given a `PersonaFrontmatter` with traits `[methodical, test-first]` and body markdown, when the Claude adapter runs, then the output contains traits as behavioral instructions and anti-traits as constraints.
- [ ] REQ-0.0.13-04-02: Given the same persona, when the Codex adapter runs, then the output is a valid AGENTS.md instruction block.
- [ ] REQ-0.0.13-04-03: Given the same persona, when the Copilot adapter runs, then the output is compatible with `.github/copilot-instructions.md` format.
- [ ] REQ-0.0.13-04-04: Given a vendor with no adapter registered, when sync attempts to render a persona for that vendor, then the raw canonical markdown is copied as fallback.
- [ ] REQ-0.0.13-04-05: Given any adapter function, when called with the same input twice, then the output is identical (pure function, deterministic).

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
