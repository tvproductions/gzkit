---
id: OBPI-0.0.13-04-vendor-neutral-persona-loading
parent: ADR-0.0.13-portable-persona-control-surface
item: 4
lane: Lite
status: in_progress
---

# OBPI-0.0.13-04-vendor-neutral-persona-loading: Vendor Neutral Persona Loading

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #4 - "Vendor-neutral persona loading (Claude, Codex, Copilot adapters)"

**Status:** Completed

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

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand vendor neutrality constraint

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [x] OBPI-0.0.13-01 - schema and PersonaFrontmatter model
- [x] OBPI-0.0.13-03 - sync pipeline that will call these adapters

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/models/persona.py` exists with stable `PersonaFrontmatter`
- [x] `src/gzkit/personas.py` exists with `compose_persona_frame()`
- [x] `.gzkit/personas/` has persona files to test against

**Existing Code (understand current state):**

- [x] Pattern to follow: `compose_persona_frame()` in `src/gzkit/personas.py` - existing composition logic
- [x] Pattern to follow: vendor-specific rendering in `sync_surfaces.py` - how rules/skills are formatted per vendor
- [x] Test patterns: `tests/test_personas.py` or `tests/commands/test_personas_cmd.py`

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

- [x] REQ-0.0.13-04-01: Given a `PersonaFrontmatter` with traits `[methodical, test-first]` and body markdown, when the Claude adapter runs, then the output contains traits as behavioral instructions and anti-traits as constraints.
- [x] REQ-0.0.13-04-02: Given the same persona, when the Codex adapter runs, then the output is a valid AGENTS.md instruction block.
- [x] REQ-0.0.13-04-03: Given the same persona, when the Copilot adapter runs, then the output is compatible with `.github/copilot-instructions.md` format.
- [x] REQ-0.0.13-04-04: Given a vendor with no adapter registered, when sync attempts to render a persona for that vendor, then the raw canonical markdown is copied as fallback.
- [x] REQ-0.0.13-04-05: Given any adapter function, when called with the same input twice, then the output is identical (pure function, deterministic).

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
Ran 21 tests in 0.001s — OK (tests/test_persona_loading.py)
Ran 2483 tests in 35.006s — OK (full suite)
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Value Narrative

Before this OBPI, persona sync copied raw canonical markdown to all vendor mirrors identically. Now, vendor adapter functions translate each canonical persona frame into the vendor's native format (Claude system prompt fragments, Codex AGENTS.md instruction blocks, Copilot inline fragments), with fallback to raw markdown for unknown vendors.

### Key Proof

```python
from gzkit.models.persona import PersonaFrontmatter
from gzkit.personas import render_persona_claude, render_persona_codex, render_persona_copilot

fm = PersonaFrontmatter(name="tester", traits=["methodical"], anti_traits=["scope-creep"], grounding="I verify claims.")
render_persona_claude(fm)   # "I verify claims.\n\nYou are methodical.\n\nWhat this persona does NOT do:\n- scope-creep"
render_persona_codex(fm)    # "# Persona: tester\n\nI verify claims.\n\n## Behavioral Traits\n\n- methodical\n\n## Anti-Patterns\n\n- scope-creep"
render_persona_copilot(fm)  # "## Persona: tester\n\nI verify claims.\n\nBehavioral traits: methodical\n\nBehaviors to avoid: scope-creep"
```

### Implementation Summary

- Files created: `tests/test_persona_loading.py` (21 tests)
- Files modified: `src/gzkit/personas.py` (adapters + registry + dispatcher), `src/gzkit/sync_surfaces.py` (adapter-aware sync), `tests/test_sync_surfaces.py` (updated fixtures)
- Tests added: 21 new tests in `test_persona_loading.py`
- Date completed: 2026-04-05
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeff`
- Attestation: keep as is, we haven't progressed to feature flags yet.
- Date: 2026-04-05

---

**Brief Status:** Completed

**Date Completed:** 2026-04-05

**Evidence Hash:** -
