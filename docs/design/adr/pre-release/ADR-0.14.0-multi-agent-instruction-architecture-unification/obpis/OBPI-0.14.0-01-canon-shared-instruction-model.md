---
id: OBPI-0.14.0-01-canon-shared-instruction-model
parent: ADR-0.14.0-multi-agent-instruction-architecture-unification
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.14.0-01-canon-shared-instruction-model: Canonical Shared Instruction Model

## ADR Item

- **Source ADR:** `docs\design\adr\pre-release\ADR-0.14.0-multi-agent-instruction-architecture-unification\ADR-0.14.0-multi-agent-instruction-architecture-unification.md`
- **Checklist Item:** #1 - "OBPI-0.14.0-01: Establish the canonical instruction data model with `AGENTS.md` as shared source and thin vendor adapter renders."

**Status:** Completed

## Objective

Refactor gzkit's control-surface generation so one shared instruction canon feeds
`AGENTS.md`, `CLAUDE.md`, and other vendor adapters without duplicating durable rules.

This OBPI addresses the current duplication between root `AGENTS.md` and `CLAUDE.md`
and establishes the product contract that Codex-facing and Claude-facing root files are
renders of the same shared model, not peer-authored policy trees.

## Lane

**Heavy** - Changes the generated instruction contract consumed by external agent tools.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/templates/` - shared canon and adapter template changes
- `src/gzkit/sync.py` - control-surface render pipeline
- `src/gzkit/config.py` - canonical/adaptor path model if needed
- `tests/test_sync.py` - render and sync behavior coverage
- `tests/test_templates.py` - template/render regression coverage
- `AGENTS.md` - generated shared root surface
- `CLAUDE.md` - generated Claude adapter surface
- `.github/copilot-instructions.md` - generated Copilot adapter surface

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/skills/**` - skill lifecycle changes belong to later OBPIs unless required for references
- `.claude/settings*.json` - config separation belongs to OBPI-05
- `.claude/rules/**` - native path rule work belongs to OBPI-02
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Shared durable repo instructions MUST originate from one canonical model.
1. REQUIREMENT: Vendor root files MUST be rendered as thin adapters, not peer-authored contracts.
1. NEVER: Reintroduce duplicated full skill catalogs or repeated workflow prose into root surfaces.
1. ALWAYS: Preserve existing gzkit governance semantics unless a deliberate contract change is documented.
1. ALWAYS: Keep the canonical model rich enough to render Codex, Claude, and Copilot
   surfaces without re-entering the same durable rules in multiple templates.

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
- [ ] Required templates exist: `src/gzkit/templates/agents.md`, `src/gzkit/templates/claude.md`

**Existing Code (understand current state):**

- [ ] Pattern to follow: existing generated control surfaces in repo root
- [ ] Test patterns: `tests/test_sync.py`, `tests/test_templates.py`

## Target Change

- Introduce a single canonical instruction data structure or render context that owns
  shared repo rules.
- Make `src/gzkit/templates/agents.md`, `src/gzkit/templates/claude.md`, and
  `src/gzkit/templates/copilot.md` consume that shared model instead of embedding
  overlapping policy blocks separately.
- Preserve adapter-only orientation where required, but forbid those adapters from
  becoming alternate governance sources.

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
uv run -m unittest tests.test_sync tests.test_templates
uv run gz agent sync control-surfaces --dry-run
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.14.0-01-01: Given canonical shared instruction content, when control surfaces are rendered, then `AGENTS.md` contains the shared rules and vendor files reference the same canon without duplicating long policy blocks.
- [ ] REQ-0.14.0-01-02: Given unchanged canonical inputs, when sync runs repeatedly, then generated root control surfaces remain deterministic.
- [ ] REQ-0.14.0-01-03: Given adapter-specific fields, when Claude or Copilot surfaces are generated, then tool-specific orientation is preserved without becoming an alternate source of truth.
- [ ] REQ-0.14.0-01-04: [doc] Given the current root skill inventory, when the canonical model renders adapters, then shared durable rules are emitted once and skill discovery is referenced instead of inlined as a second policy body.

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
uv run -m unittest tests.test_sync.TestSyncControlSurfaces tests.test_templates
...
OK
```

Key proof: `uv run -m unittest tests.test_templates.TestAdapterTemplatesReferenceCanon` — 3 tests confirm adapters reference canon, agents keeps full catalog.

### Code Quality

```text
uv run ruff check src tests — All checks passed
uv run ruff format --check . — clean
```

### Implementation Summary

- Files modified: `src/gzkit/templates/copilot.md`, `src/gzkit/sync.py`, `tests/test_sync.py`, `tests/test_templates.py`
- Tests added: `TestAdapterTemplatesReferenceCanon` (3 tests — adapters reference canon, agents keeps full catalog)
- Date completed: 2026-03-15
- Anchor commit: `8e93918`

### Value Narrative

Before this OBPI, gzkit generated overlapping root instruction contracts that were easy
to drift apart and expensive for agents to load. After this OBPI, shared repo rules
will exist once and vendor files will become cheaper, clearer adapter surfaces.

### Key Proof

One canonical instruction input renders `AGENTS.md`, `CLAUDE.md`, and
`.github/copilot-instructions.md` with identical shared governance content and only
minimal adapter-specific framing differences.

### Human Attestation

- Attestor: human:jeff
- Attestation: accept, proceed git sync
- Date: 2026-03-15

---

**Brief Status:** Completed

**Date Completed:** 2026-03-15

**Evidence Hash:** -
