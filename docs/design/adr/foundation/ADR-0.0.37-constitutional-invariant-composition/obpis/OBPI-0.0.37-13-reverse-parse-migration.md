---
id: OBPI-0.0.37-13-reverse-parse-migration
parent: ADR-0.0.37-constitutional-invariant-composition
item: 13
lane: Heavy
status: Draft
---

# OBPI-0.0.37-13-reverse-parse-migration: Reverse-Parse Migration to the Master Model

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #13 — "OBPI-0.0.37-13 — Reverse-parse migration to master model (gz content import; dissolve agents.local.md + get_project_context literals; zero hand-authored prose; round-trip fidelity; supersedes OBPI-09 byte-preserving framing)"

**Status:** Draft

## Objective

Reverse-parse the live agent contract into the OBPI-11 master model so the model — not
prose — becomes the source: extend `gz content import` / the markdown parser to read the
current AGENTS.md content (and the raw `.gzkit/agents.local.md`) into a fully-populated
`AgentContract`, classify each bullet, and assert round-trip fidelity. This dissolves the
`agents.local.md` raw splice into model rows. The `get_project_context` literals and the
final sync wiring are OBPI-14. This brief supersedes OBPI-09's byte-preserving framing.

## Lane

**Heavy** — changes the parse/import contract and migrates a canonical surface source.
Foundation + heavy → Gate 5 human attestation (`assets/HEAVY_LANE_PLAN_TEMPLATE.md`).

## Allowed Paths

- `src/gzkit/content/parse/markdown_parser.py` — extend to parse the agent contract into a full `AgentContract` with classification/witness/density fields
- `src/gzkit/content/migration/registry.py` — migration support for the extended shape
- `src/gzkit/commands/content/` — the `gz content import` operator surface
- `.gzkit/agents.local.md` — dissolve: its content is reverse-parsed into model rows
- `tests/content/test_round_trip_agent_contract.py` — round-trip fidelity for the full contract
- `tests/content/test_migration_layer.py` — migration coverage
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-13-reverse-parse-migration.md` — this brief
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/content/models/` — model is OBPI-11
- `src/gzkit/content/render/`, `src/gzkit/content/templates/` — renderer is OBPI-12
- `src/gzkit/sync_surfaces.py` — the `get_project_context` literals and sync wiring are OBPI-14
- `src/gzkit/templates/agents.md`, `AGENTS.md` — the monolith retirement is OBPI-14
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz content import` MUST read the current agent-contract prose into a fully-populated `AgentContract` (sections, bullets, classification, witness, rationale_ref, density_min) — not a lossy subset.
2. REQUIREMENT: the content of `.gzkit/agents.local.md` MUST be reverse-parsed into model rows (project-local bullets/sections), and the raw-splice source removed — NEVER left as a parallel hand-authored surface.
3. REQUIREMENT: round-trip fidelity MUST hold — `parse(render(imported_model))` reconstructs an equivalent model (the substrate doctrine's binding round-trip contract).
4. REQUIREMENT: classification of migrated bullets MUST default conservatively — a bullet whose enforcement is unknown is `Ambiguous`, never silently `Mechanical` (which would let the dial thin an unenforced rule).
5. NEVER: edit `src/gzkit/sync_surfaces.py`, the root template, or any rendered surface in this OBPI — import + dissolve only; the wiring is OBPI-14.

> STOP-on-BLOCKERS: requires OBPI-11 (model) and OBPI-12 (renderer for the round-trip assertion). If absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (quote verbatim into Implementation Summary):** "OBPI-0.0.37-13 — Reverse-parse migration to master model (gz content import; dissolve agents.local.md + get_project_context literals; zero hand-authored prose; round-trip fidelity; supersedes OBPI-09 byte-preserving framing)."
- [ ] Parent ADR § "Decision Extension (2026-05-30)" — the dissolve-to-model-rows intent.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` § Round-trip fidelity contract.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/parse/markdown_parser.py` exists
- [ ] `src/gzkit/content/migration/registry.py` exists
- [ ] `.gzkit/agents.local.md` exists
- [ ] `tests/content/test_round_trip_agent_contract.py` and `tests/content/test_migration_layer.py` exist

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/parse/markdown_parser.py` — current `AgentContract` reverse-parse (`parse(...) -> AgentContract`)
- [ ] `src/gzkit/sync_surfaces.py` `load_local_content` — how `.gzkit/agents.local.md` is currently spliced (read-only context)

## Quality Gates

### Gate 1: ADR
- [ ] Decision item quoted into Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)
- [ ] Import + dissolve + round-trip tests RED before, GREEN after
- [ ] `uv run gz test` passes

### Code Quality
- [ ] `uv run gz lint` and `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict` clean

### Gate 4: BDD (Heavy)
- [ ] `features/constitutional_invariants.feature` scenario tagged `@REQ-0.0.37-13-*`

### Gate 5: Human (Heavy + Foundation)
- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.test_round_trip_agent_contract -v
uv run -m unittest tests.content.test_migration_layer -v
```

## Demo

```bash
uv run python -c "print('import AGENTS.md to a master AgentContract, render it back, assert round-trip equality')"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-13-01 [BEHAVIOR]: `gz content import` produces a full `AgentContract` whose sections/bullets/classification cover the current agent contract without loss. Proof: `@covers(REQ-0.0.37-13-01)` test in `tests/content/test_migration_layer.py`.
- [ ] REQ-0.0.37-13-02 [BEHAVIOR]: the `.gzkit/agents.local.md` content appears as model rows in the imported model; the raw-splice source is gone. Proof: `@covers(REQ-0.0.37-13-02)` test.
- [ ] REQ-0.0.37-13-03 [BEHAVIOR]: round-trip — `parse(render(imported_model))` equals the imported model. Proof: `@covers(REQ-0.0.37-13-03)` test in `tests/content/test_round_trip_agent_contract.py`.
- [ ] REQ-0.0.37-13-04 [BEHAVIOR]: a bullet with no determinable witness is classified `Ambiguous`, not `Mechanical`. Proof: `@covers(REQ-0.0.37-13-04)` test.
- [ ] REQ-0.0.37-13-05 [SUPPORT]: the migration is recorded — `uv run gz validate --documents` passes after the dissolve and an `artifact_edited` ledger event is emitted for the removed `.gzkit/agents.local.md`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision item quoted
- [ ] **Gate 2 (TDD):** RGR followed; tests derive from REQs
- [ ] **Code Quality:** lint, format, typecheck clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** import + round-trip equality
- [ ] **Gate 5:** human attestation recorded

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
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

Before: AGENTS.md is hand-authored prose and `.gzkit/agents.local.md` is a raw splice — two
undisciplined sources. After: both are dissolved into the master model via reverse-parse,
with round-trip fidelity, so the model is the single source.

### Key Proof

`gz content import` of the current contract reconstructs byte-equivalently through the
renderer, and `agents.local.md` content is present as classified model rows.

### Implementation Summary

- Decision item implemented (verbatim): "OBPI-0.0.37-13 — Reverse-parse migration to master model (gz content import; dissolve agents.local.md + get_project_context literals; zero hand-authored prose; round-trip fidelity; supersedes OBPI-09 byte-preserving framing)."
- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
