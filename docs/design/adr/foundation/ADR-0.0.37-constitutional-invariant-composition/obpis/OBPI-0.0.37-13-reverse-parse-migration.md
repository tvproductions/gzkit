---
id: OBPI-0.0.37-13-reverse-parse-migration
parent: ADR-0.0.37-constitutional-invariant-composition
item: 13
lane: Heavy
status: Completed
---

# OBPI-0.0.37-13-reverse-parse-migration: Reverse-Parse Migration to the Master Model

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #13 — "OBPI-0.0.37-13 — Reverse-parse migration to master model (gz content import; dissolve agents.local.md + get_project_context literals; zero hand-authored prose; round-trip fidelity; supersedes OBPI-09 byte-preserving framing)"

**Status:** Completed

## Objective

Populate the OBPI-11 master model with the **full gzkit contract corpus** so the model — not
prose — becomes the source AGENTS.md renders *forward* from. Extend `gz content import` / the
markdown parser to read the current AGENTS.md (and the raw `.gzkit/agents.local.md`) into a
structurally-faithful `AgentContract` — every section as a `Pillar`, every binding rule as a
classified `Bullet` — **joining per-bullet classification from the advisory scorecard**
(`docs/governance/advisory-rules-audit.md`, the existing Mechanical/Promotable/Judgment/Ambiguous
source) rather than reverse-engineering it from prose. This captures the `agents.local.md`
content into model rows — the live AGENTS.md already contains it spliced, so importing AGENTS.md
reverse-parses that content into pillars. Physical removal of the raw-splice source file and the
sync rewire are OBPI-14 (the `get_project_context` literals and the final sync wiring).

**Scope correction (return-to-health, 2026-06-01).** The original brief required a *lossless
prose round-trip* (`parse(render(model)) == model`). That is unsatisfiable and was the root of
the substrate's hollowness: clean human-readable AGENTS.md cannot carry per-bullet classification
metadata, so it can never round-trip a classified model. #519 does not need it — the goal is
*forward* rendering at temperature, not bidirectional prose fidelity. The lossless source-of-truth
round-trip is **model ↔ its canonical JSON** (Pydantic `model_validate_json(model_dump_json())`,
free); the prose render is an explicitly *lossy human view*. This supersedes OBPI-09's
byte-preserving framing and corrects the OBPI-11/12/13 decomposition bug (mutual Denied-Paths split
an irreducible model+template+parser unit).

**Scope correction (build session, 2026-06-01) — agents.local.md removal deferred to OBPI-14
(operator decision, Option A).** Implementation surfaced a brief-internal contradiction: REQ-03/06
as first written demanded *physical removal* of `.gzkit/agents.local.md`, but its only consumer —
`get_project_context` / `load_local_content` in `src/gzkit/sync_surfaces.py` — and the rendered
`AGENTS.md` + monolith template `src/gzkit/templates/agents.md` are all **Denied Paths** assigned
to OBPI-14. Code trace: `gz validate --invariant-coherence` diffs committed AGENTS.md against
`render_agents_md(...)` (`src/gzkit/governance/compose.py:80`), which splices the file via the
`{local_content}` placeholder; deleting the file makes `load_local_content` return `""`, the render
drops the Local-Agent-Rules section, committed≠rendered, and the gate fails closed (exit 3). So the
physical-removal half of REQ-03/06 is unsatisfiable inside OBPI-13's allowed paths. **Resolution:**
OBPI-13 *captures* the agents.local.md content into model rows (it is already spliced into AGENTS.md,
so the AGENTS.md import reverse-parses it); **physical file removal + the sync rewire that makes the
removal coherent move to OBPI-14.** *OBPI-14 hand-off:* OBPI-14 MUST own (a) deleting
`.gzkit/agents.local.md`, (b) rewiring `render_agents_md`/`get_project_context` to source the
local-rule rows from the model instead of `{local_content}`, and (c) emitting the
`artifact_edited`-for-removed-`agents.local.md` proof. This is the concrete form of the ADR
Checklist-#13 "dissolve agents.local.md + get_project_context literals" split the plan-audit flagged.

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
3. REQUIREMENT: the content of `.gzkit/agents.local.md` MUST be reverse-parsed into model rows — captured via the AGENTS.md import, which already contains the spliced local content. (Scope correction, Option A: *physical* removal of the raw-splice source file is DEFERRED to OBPI-14, which rewires the sync render off the `{local_content}` splice; removing it here fails `gz validate --invariant-coherence`. OBPI-13 proves the content is captured, not that the file is gone.)
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
- [ ] REQ-0.0.37-13-03 [BEHAVIOR]: the `.gzkit/agents.local.md` content appears as model rows in the imported AgentContract (captured through the AGENTS.md import, which contains the spliced local content). Physical removal of the source file is OBPI-14 (scope correction, Option A). Proof: `@covers(REQ-0.0.37-13-03)` test asserting a known local-rule line is present as a model row.
- [ ] REQ-0.0.37-13-04 [BEHAVIOR]: the lossless round-trip is model↔JSON — `AgentContract.model_validate_json(m.model_dump_json()) == m`; and `parse(render(m))` recovers the structural model (sections/bullets/text/order), explicitly NOT classification metadata. Proof: `@covers(REQ-0.0.37-13-04)` test in `tests/content/test_round_trip_agent_contract.py`.
- [ ] REQ-0.0.37-13-05 [BEHAVIOR]: a bullet with no scorecard entry / no determinable witness is classified `Ambiguous`, never silently `Mechanical`. Proof: `@covers(REQ-0.0.37-13-05)` test.
- [ ] REQ-0.0.37-13-06 [SUPPORT]: the migration is recorded — `uv run gz validate --documents` passes after the model+parser+template changes (no regression), and `artifact_edited` ledger events are emitted for the edited OBPI-13 surfaces (parser, model, template). The `artifact_edited`-for-removed-`.gzkit/agents.local.md` proof moves to OBPI-14 with the physical removal (scope correction, Option A).

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


parse(AGENTS.md) reconstructs a structurally-faithful AgentContract — >5 pillars, >5000-byte serialized model (vs. the prior 161-byte stub) — with model_validate_json(model_dump_json()) == model lossless (receipt arb-step-unittestscoped-6fdbc0b0f8ee4b90ba70298cd7414335, 24/24 tests). Per-bullet classification joins the advisory scorecard ("Never prefix `uv run gz`" -> Mechanical). Full suite green: 5819/5819 (arb-step-unittest-e691d97763b1482d9bb97d499c9b9c6e); Gate-4 BDD 5/5 (arb-step-behave-2e18dc0791b24bcf9ee595e0ddf48727); docs arb-step-mkdocs-7305aa3544464476a88ebc6032033c2d.

### Implementation Summary


- Decision item implemented (verbatim): "OBPI-0.0.37-13 — Reverse-parse migration to master model (gz content import; dissolve agents.local.md + get_project_context literals; zero hand-authored prose; round-trip fidelity; supersedes OBPI-09 byte-preserving framing)."
- Parser: extended _parse_agent_contract (src/gzkit/content/parse/markdown_parser.py) to walk every ## section via _sections(), build one Pillar per section with verbatim body lines + classified bullets; classification joined from the advisory scorecard via _load_scorecard_index/_classify, defaulting to Ambiguous (never silently Mechanical).
- Model: added Pillar.lines: list[str] (src/gzkit/content/models/agent_contract.py) for full-fidelity body capture + structural round-trip; no speculative fields.
- Template: extended claude.md.j2 to emit pillar.lines verbatim when populated, bullets otherwise.
- Tests added: TestReverseParseFullContract (REQ-01/02/03/05) in test_migration_layer.py; TestReverseParseRoundTrip (REQ-04) in test_round_trip_agent_contract.py; 5 Gate-4 BDD scenarios tagged @REQ-0.0.37-13-01..05 in features/constitutional_invariants.feature.
- REQ-06 (SUPPORT): waived from behave coverage with rationale (proof channel is ledger + gz validate --documents, not behave).
- Date completed: 2026-06-01
- Attestation status: operator-attested ("attest completed")
- Defects noted: none in scope.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy/foundation OBPI-0.0.37-13 reverse-parse migration verified green: full suite 5819/5819 (receipt arb-step-unittest-e691d97763b1482d9bb97d499c9b9c6e), OBPI-scoped 24/24 (arb-step-unittestscoped-6fdbc0b0f8ee4b90ba70298cd7414335), lint/typecheck clean (arb-ruff-d6363a008fb64968bb6cc80ee2ff3cd9, arb-step-typecheck-ec6db6537b874282871abf36f843bbd7), docs strict (arb-step-mkdocs-7305aa3544464476a88ebc6032033c2d), Gate-4 BDD 5/5 (arb-step-behave-2e18dc0791b24bcf9ee595e0ddf48727). All 5 BEHAVIOR REQs @covers-tagged; REQ-06 SUPPORT waived to ledger+validator.
- Date: 2026-06-01

---

**Date Completed:** 2026-06-01

**Evidence Hash:** -
