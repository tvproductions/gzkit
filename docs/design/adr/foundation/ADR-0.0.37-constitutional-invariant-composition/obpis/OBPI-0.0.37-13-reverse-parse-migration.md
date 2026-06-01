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

Populate the OBPI-11 master model with the **full gzkit contract corpus** so the model — not
prose — becomes the source AGENTS.md renders *forward* from. Extend `gz content import` / the
markdown parser to read the current AGENTS.md (and the raw `.gzkit/agents.local.md`) into a
structurally-faithful `AgentContract` — every section as a `Pillar`, every binding rule as a
classified `Bullet` — **joining per-bullet classification from the advisory scorecard**
(`docs/governance/advisory-rules-audit.md`, the existing Mechanical/Promotable/Judgment/Ambiguous
source) rather than reverse-engineering it from prose. This dissolves the `agents.local.md` raw
splice into model rows. The `get_project_context` literals and the final sync wiring are OBPI-14.

**Scope correction (return-to-health, 2026-06-01).** The original brief required a *lossless
prose round-trip* (`parse(render(model)) == model`). That is unsatisfiable and was the root of
the substrate's hollowness: clean human-readable AGENTS.md cannot carry per-bullet classification
metadata, so it can never round-trip a classified model. #519 does not need it — the goal is
*forward* rendering at temperature, not bidirectional prose fidelity. The lossless source-of-truth
round-trip is **model ↔ its canonical JSON** (Pydantic `model_validate_json(model_dump_json())`,
free); the prose render is an explicitly *lossy human view*. This supersedes OBPI-09's
byte-preserving framing and corrects the OBPI-11/12/13 decomposition bug (mutual Denied-Paths split
an irreducible model+template+parser unit).

## Lane

**Heavy** — changes the parse/import contract and migrates a canonical surface source.
Foundation + heavy → Gate 5 human attestation (`assets/HEAVY_LANE_PLAN_TEMPLATE.md`).

## Allowed Paths

- `src/gzkit/content/parse/markdown_parser.py` — extend `_parse_agent_contract` to populate `pillars` (every `##` section) and join classification, not just Tech Stack / Rules
- `src/gzkit/content/models/agent_contract.py`, `src/gzkit/content/models/bullet.py` — grow the model **only as far as import fidelity requires** (e.g. a block/table representation if a section cannot be expressed as bullets); no speculative fields. The OBPI-11/12/13 decomposition treated these as separate, which is the bug this brief corrects.
- `src/gzkit/content/templates/agentcontract/*.j2`, `src/gzkit/content/render/pipeline.py` — grow the template/render so a populated model renders the **full clean contract** (all pillars/sections), not the 430-byte stub; temperature projection logic stays as OBPI-12 shipped it
- `src/gzkit/content/migration/registry.py` — migration support for the extended shape
- `src/gzkit/commands/content/` — the `gz content import` operator surface
- `.gzkit/agents.local.md` — dissolve: its content is reverse-parsed into model rows
- `tests/content/test_round_trip_agent_contract.py` — model ↔ canonical-JSON round-trip (NOT lossless prose); structural-faithfulness of the import
- `tests/content/test_render_pipeline.py`, `tests/content/test_migration_layer.py` — full-corpus render + migration coverage
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-13-reverse-parse-migration.md` — this brief
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/sync_surfaces.py` — the `get_project_context` literals and sync wiring are OBPI-14
- `src/gzkit/templates/AGENTS.md` (monolith template), `AGENTS.md` (rendered output) — the monolith retirement + sync re-point are OBPI-14; this brief makes the model *renderable*, it does not yet swap the production sync path
- New runtime dependencies; CI files; lockfiles
- Speculative model fields or template features beyond what the import's structural fidelity requires (simplicity-first; the model grows to fit the corpus, not the imagination)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz content import AGENTS.md --as AgentContract` MUST populate a structurally-faithful `AgentContract` — every `##` section as a `Pillar`, every binding rule as a `Bullet` — covering the whole contract, not the name+purpose stub the current parser yields (verified: today it loses 99.84% of a 32 KB input). Structural faithfulness, not byte-preservation.
2. REQUIREMENT: per-bullet `classification` MUST be joined from the advisory scorecard (`docs/governance/advisory-rules-audit.md`), the existing classification source — NOT inferred from prose. A bullet absent from the scorecard is `Ambiguous` (REQ-04).
3. REQUIREMENT: the content of `.gzkit/agents.local.md` MUST be reverse-parsed into model rows and the raw-splice source removed — NEVER left as a parallel hand-authored surface.
4. REQUIREMENT: the lossless round-trip contract is **model ↔ canonical JSON**: `AgentContract.model_validate_json(model.model_dump_json()) == model`. The prose render (`render(model, vendor, temperature=...)`) is an explicitly **lossy human view** — it is asserted to be *structurally* recoverable (sections/bullets/text/order), NOT to round-trip classification metadata. The old "lossless `parse(render(model))`" contract is retired as unsatisfiable on clean prose.
5. REQUIREMENT: classification defaults conservatively — unknown enforcement ⇒ `Ambiguous`, never silently `Mechanical` (which would let the dial thin an unenforced rule).
6. NEVER: swap the production sync path (`sync_agents_md` → render) or retire the monolith template in this OBPI — that is OBPI-14. This brief makes the model *populated and renderable*; OBPI-14 makes it the production source.

> STOP-on-BLOCKERS: requires OBPI-11 (model) and OBPI-12 (renderer). Both `attested_completed`. If the advisory scorecard is unreadable, print BLOCKERS and halt (REQ-02 has no classification source without it).

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

- [ ] REQ-0.0.37-13-01 [BEHAVIOR]: `gz content import AGENTS.md --as AgentContract` produces an `AgentContract` whose `pillars` cover every `##` section and whose bullets cover the binding rules — structurally faithful, not the name+purpose stub (regression floor: the current parser yields a 161-byte model from a 32 KB input). Proof: `@covers(REQ-0.0.37-13-01)` test in `tests/content/test_migration_layer.py`.
- [ ] REQ-0.0.37-13-02 [BEHAVIOR]: each imported bullet's `classification` is joined from the advisory scorecard, not inferred from prose; a scorecard entry's class appears on the matching model bullet. Proof: `@covers(REQ-0.0.37-13-02)` test.
- [ ] REQ-0.0.37-13-03 [BEHAVIOR]: the `.gzkit/agents.local.md` content appears as model rows in the imported model; the raw-splice source is gone. Proof: `@covers(REQ-0.0.37-13-03)` test.
- [ ] REQ-0.0.37-13-04 [BEHAVIOR]: the lossless round-trip is model↔JSON — `AgentContract.model_validate_json(m.model_dump_json()) == m`; and `parse(render(m))` recovers the structural model (sections/bullets/text/order), explicitly NOT classification metadata. Proof: `@covers(REQ-0.0.37-13-04)` test in `tests/content/test_round_trip_agent_contract.py`.
- [ ] REQ-0.0.37-13-05 [BEHAVIOR]: a bullet with no scorecard entry / no determinable witness is classified `Ambiguous`, never silently `Mechanical`. Proof: `@covers(REQ-0.0.37-13-05)` test.
- [ ] REQ-0.0.37-13-06 [SUPPORT]: the migration is recorded — `uv run gz validate --documents` passes after the dissolve and an `artifact_edited` ledger event is emitted for the removed `.gzkit/agents.local.md`.

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
