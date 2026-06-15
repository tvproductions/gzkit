---
id: OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index
parent: ADR-0.0.37-constitutional-invariant-composition
item: 27
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit — one behavior/support
# surface apiece (model-retire, pipeline-retire, sync-retire, substrate-refresh,
# orientation-index, disposition-finalize); none decomposes into parallel seq=02+
# sub-tasks (ADR-0.0.64 exemption).
req_atomic:
  - REQ-0.0.37-27-01
  - REQ-0.0.37-27-02
  - REQ-0.0.37-27-03
  - REQ-0.0.37-27-04
  - REQ-0.0.37-27-05
  - REQ-0.0.37-27-06
---

# OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index: Migration / Disposition + Doctrine Refresh + Orientation Index

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #27 - "OBPI-0.0.37-27 — Migration/disposition + doctrine refresh + orientation index (retire the inert density_min filter + three-static-template framing; repoint sync onto the rendition store; fold in the OBPI-16 orientation-index surface→model map; refresh the substrate doc + return-to-health plan)"

**Status:** Completed

## Objective

The capstone disposition for the 2026-06-03 re-alignment: **retire the proven-inert density-dial mechanism** and refresh the doctrine to match the landed corpus→compress→rendition→playback pipeline. Specifically: (a) remove the inert `Bullet.density_min` field + `_enforce_judgment_floor` validator (`src/gzkit/content/models/bullet.py`) and the inert `_bullet_renders` / `_project_for_temperature` filter (`src/gzkit/content/render/pipeline.py`) — empirically dead, since `render(lite) == render(medium) == render(heavy)` byte-for-byte; (b) retire the residual monolith `render_template("agents")` fallback so `sync_agents_md` reads only the committed-rendition store (OBPI-22); (c) refresh `docs/governance/agent-control-surface-rendering-substrate.md` to the corpus + setpoint-compression + invariant-tier mechanism, **folding in OBPI-16's orientation-index intent** (a routable surface→model+doctrine+load-command map); (d) refresh `docs/governance/return-to-health-plan-2026-05-30.md` and finalize the ADR-0.0.37 checklist disposition (09 and 11-17 withdrawn; 18-27 the active target).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Removing a Pydantic model field (`Bullet.density_min`) + a render-pipeline contract + retiring a sync fallback are runtime/schema-contract changes → Heavy. Gate 5 human attestation is mandatory (foundation/heavy; no self-close).

## Allowed Paths

- `src/gzkit/content/models/bullet.py` — EDIT: remove the inert `density_min` field and the `_enforce_judgment_floor` validator (the 0-Kelvin floor now lives in the corpus `tier: invariant` designation, OBPI-23, not in per-`Bullet` density)
- `src/gzkit/governance/invariants.py` — EDIT: remove the `density_min="lite"` kwarg in `reconcile_invariant` (coupled surface — `Bullet(extra="forbid")` rejects the kwarg once the field is removed) + refresh the docstring (allowlist amendment, operator-approved 2026-06-15; Gate Friction evaluator loop)
- `src/gzkit/schemas/constitutional_invariant.json` — EDIT: remove the now-dead `density_min` property (the `ConstitutionalInvariant` Pydantic model already has no such field; the JSON-schema mirror is vestigial — allowlist amendment, operator-approved 2026-06-15; Gate Friction evaluator loop)
- `src/gzkit/content/render/pipeline.py` — EDIT: remove the inert `_bullet_renders` + `_project_for_temperature` filter (lines ~23-48); render output is unchanged because the filter was proven inert
- `src/gzkit/sync_surfaces.py` — EDIT: retire the residual monolith `render_template("agents")` fallback so `sync_agents_md` reads only the committed-rendition store (coordinate with OBPI-22's repoint — see § Tracked Defects)
- `tests/content/models/test_fields.py` — EDIT: drop the `density_min` field assertions
- `tests/content/test_byte_stability.py` — EDIT: drop `density_min`-dependent byte-stability cases (byte-stability is preserved by playback, not the filter)
- `tests/content/test_render_pipeline.py` — EDIT: drop the temperature-filter cases; assert the simplified render path
- `tests/content/test_round_trip_agent_contract.py` — EDIT: drop `density_min` from the round-trip fixtures/assertions
- `tests/content/test_vendor_manifest.py` — EDIT: drop any `density_min`-coupled assertions
- `tests/commands/test_sync_cmds.py` — EDIT: add the discriminating REQ-27-03 bare-bootstrap test (package template routes through the model pipeline, no monolith fallback) — coupled surface for REQ-03, allowlist-amended 2026-06-15
- `.gzkit/insights/agent-insights.jsonl` — APPEND: `improvement` records per Behavior Rule Always #11 (operator course-corrections during this run) — allowlist-amended 2026-06-15
- `docs/governance/agent-control-surface-rendering-substrate.md` — EDIT: refresh the mechanism (retire density-dial / three-static-template framing; document corpus→compress→rendition→playback + invariant tier) AND add the Agent Orientation Index (OBPI-16 intent)
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — EDIT: record the items-18-27-active + 09/11-17-withdrawn disposition + #519 relief route on the ACTIVE plan (operator-redirected 2026-06-15; the original `return-to-health-plan-2026-05-30.md` target was frozen "retained unmodified for audit" on 2026-06-10, after this 2026-06-03 brief, and already states 18-27 active — editing it would violate its audit-freeze)
- `data/behave_coverage_waivers.json` — EDIT: OBPI-level behave-coverage waiver for the SUPPORT doc/disposition REQs
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — EDIT: finalize the checklist disposition (confirm 09 + 11-17 withdrawn markers; 18-27 active) and check this item's box at closeout
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-27-migration-disposition-doctrine-refresh-orientation-index.md` — active brief and evidence record

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/content/models/corpus.py` — the corpus model (OBPI-18) is not changed by the disposition
- `src/gzkit/content/composer.py`, `src/gzkit/content/rendition_store.py`, `src/gzkit/governance/trust_audits/rendition_freshness.py` — compose (OBPI-21) + rendition store/playback (OBPI-22) are consumed, not modified here; this OBPI removes the OLD path, it does not re-author the NEW one
- `src/gzkit/content/templates/agentcontract/claude.md.j2`, `codex.md.j2` — the playback templates emit deterministically (`pillar.lines | join`); the inert part is the pipeline filter, not the template — leave the templates unless implementation proves an edit is mechanically forced
- `.gzkit/ledger.jsonl` — never hand-edited
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT [BEHAVIOR]: The inert `Bullet.density_min` field and `_enforce_judgment_floor` validator MUST be removed from `src/gzkit/content/models/bullet.py`, and the model round-trip + byte-stability + field tests MUST pass without `density_min` (the 0-Kelvin floor is enforced by the corpus invariant tier, OBPI-23, not per-`Bullet` density).
1. REQUIREMENT [BEHAVIOR]: The inert `_bullet_renders` / `_project_for_temperature` temperature filter MUST be removed from `src/gzkit/content/render/pipeline.py`, and render output MUST be unchanged (the filter was empirically inert: `render(lite) == render(medium) == render(heavy)`).
1. REQUIREMENT [BEHAVIOR]: `sync_agents_md` MUST read only the committed-rendition store (OBPI-22) — the residual monolith `render_template("agents")` fallback MUST be retired, with no remaining code path that renders `AGENTS.md` from the monolith template.
1. REQUIREMENT [SUPPORT]: `docs/governance/agent-control-surface-rendering-substrate.md` MUST be refreshed to the corpus→compress→rendition→playback + invariant-tier mechanism (density-dial / three-static-template framing retired) — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the substrate doc.
1. REQUIREMENT [SUPPORT]: The substrate doc MUST carry an Agent Orientation Index (OBPI-16 intent): a routable surface→canonical-model→governing-doctrine→load-command map with an explicit "do not re-derive from source" instruction — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the substrate doc.
1. REQUIREMENT [SUPPORT]: `docs/governance/return-to-health-plan-2026-05-30.md` and the ADR-0.0.37 checklist disposition MUST be finalized to reflect items 18-27 active (09 + 11-17 withdrawn) and the #519 relief route — proven by `uv run gz validate --documents` plus the `artifact_edited` event for those surfaces.
1. NEVER: re-author the new compose/playback path here (OBPI-21/22 own it), change the corpus model, or remove `density_min` without updating every coupled test in the same change-set.
1. ALWAYS: reconcile the brief with the parent ADR (`uv run gz validate --brief-reconcile`) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The contract: "Migration/disposition + doctrine refresh + orientation index (retire the inert density_min filter + three-static-template framing; repoint sync onto the rendition store; fold in the OBPI-16 orientation-index surface→model map; refresh the substrate doc + return-to-health plan)" (Checklist item #27).
- [ ] Parent ADR § Decision Re-Alignment "Re-decomposed extension OBPIs" — the disposition of 11-17 (attested-complete mechanism superseded / created-only / retired) that this item finalizes.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` — the current binding claim ("nothing hand-authored at the rendered location") to make load-bearing
- [ ] `docs/governance/return-to-health-plan-2026-05-30.md` — the worklist + #519 route to refresh
- [ ] `AGENTS.md` § DO IT RIGHT 11 (surgical changes) — remove only the inert code; do not refactor adjacent rendering

**Context:**

- [ ] OBPI-0.0.37-22 (rendition store + playback) — the NEW path that supersedes the monolith fallback this OBPI retires
- [ ] OBPI-0.0.37-23 (invariant tier) — where the 0-Kelvin floor now lives (replacing per-`Bullet` density_min)
- [ ] OBPI-0.0.37-16 (withdrawn; created-only) — the orientation-index intent folded into this item's substrate-doc refresh
- [ ] Parent ADR Checklist lines ~294-303 — the withdrawn markers for 09 + 11-17 already recorded; this item confirms/finalizes them

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/models/bullet.py` exists with `density_min` + `_enforce_judgment_floor` (the inert surface to remove)
- [ ] `src/gzkit/content/render/pipeline.py` exists with `_bullet_renders` + `_project_for_temperature` (the inert filter to remove)
- [ ] `src/gzkit/sync_surfaces.py` exists with the `render_template("agents")` monolith fallback (the residual path to retire)
- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` + `docs/governance/return-to-health-plan-2026-05-30.md` exist (the docs to refresh)
- [ ] OBPI-0.0.37-22's rendition store + playback have landed (this disposition removes the OLD path only after the NEW one is in place)

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/models/bullet.py` (lines ~27-41) — `density_min` field + `_enforce_judgment_floor` validator
- [ ] `src/gzkit/content/render/pipeline.py` (lines ~23-48) — `_TEMP_RANK`, `_bullet_renders`, `_project_for_temperature`
- [ ] `src/gzkit/sync_surfaces.py` (`sync_agents_md`, ~352-381) — the `render_template("agents")` fallback to retire
- [ ] `tests/content/models/test_fields.py`, `tests/content/test_byte_stability.py`, `tests/content/test_render_pipeline.py`, `tests/content/test_round_trip_agent_contract.py`, `tests/content/test_vendor_manifest.py` — every test referencing `density_min` (verified on disk) to update in the same change-set

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Substrate doc refreshed + Agent Orientation Index added; return-to-health plan refreshed

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass / waived: REQ-01/02/03 are unit-proven code-removal behavior (round-trip/byte-stability/render tests); REQ-04/05/06 are SUPPORT (docs/disposition). Behave coverage waived per the OBPI-level waiver (no new CLI verb).

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (mandatory; foundation/heavy; no self-close)

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz validate --documents
uv run gz validate --invariant-coherence
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
uv run python -c "from gzkit.content.models.bullet import Bullet; assert 'density_min' not in Bullet.model_fields, 'density_min not removed'; print('density_min removed')"
grep -RIn "render_template(\"agents\")" src/gzkit/ && echo "FALLBACK STILL PRESENT" || echo "monolith fallback retired"
uv run -m unittest tests.content.test_render_pipeline tests.content.test_round_trip_agent_contract -v
```

## Demo

```bash
# The inert density_min field is gone; render output is unchanged (filter was inert)
uv run python -c "from gzkit.content.models.bullet import Bullet; print('density_min' in Bullet.model_fields)"   # -> False
uv run gz agent sync control-surfaces && git diff --stat AGENTS.md   # playback unchanged

# The substrate doc now carries the Agent Orientation Index
grep -n "Agent Orientation Index" docs/governance/agent-control-surface-rendering-substrate.md
```

## Acceptance Criteria

- [ ] REQ-0.0.37-27-01 [BEHAVIOR]: Given the Bullet model, when this OBPI is complete, then `density_min` and `_enforce_judgment_floor` are removed and the model field / round-trip / byte-stability tests pass without them. Proof: `@covers`-decorated assertions in `tests/content/models/test_fields.py` + `tests/content/test_round_trip_agent_contract.py`.
- [ ] REQ-0.0.37-27-02 [BEHAVIOR]: Given the render pipeline, when this OBPI is complete, then `_bullet_renders` / `_project_for_temperature` are removed and render output is unchanged. Proof: `@covers`-decorated assertions in `tests/content/test_render_pipeline.py`.
- [ ] REQ-0.0.37-27-03 [BEHAVIOR]: Given `sync_agents_md`, when this OBPI is complete, then there is no remaining `render_template("agents")` monolith fallback — sync reads only the committed-rendition store. Proof: `@covers`-decorated assertion in `tests/content/test_render_pipeline.py` (or the sync test) + the grep check in Verification.
- [ ] REQ-0.0.37-27-04 [SUPPORT]: Given the substrate doctrine doc, when this OBPI is complete, then it documents the corpus→compress→rendition→playback + invariant-tier mechanism (density-dial framing retired) — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the substrate doc.
- [ ] REQ-0.0.37-27-05 [SUPPORT]: Given the substrate doctrine doc, when this OBPI is complete, then it carries an Agent Orientation Index (surface→model→doctrine→load-command map) folding in OBPI-16's intent — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the substrate doc.
- [ ] REQ-0.0.37-27-06 [SUPPORT]: Given the recovery + disposition surfaces, when this OBPI is complete, then `docs/governance/return-to-health-plan-2026-05-30.md` and the ADR-0.0.37 checklist disposition reflect items 18-27 active (09 + 11-17 withdrawn) — proven by `uv run gz validate --documents` plus the `artifact_edited` event for those surfaces.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Behave waived for this OBPI — see Gate 4 above and data/behave_coverage_waivers.json
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


The retirement of 3 code symbols + 1 fallback leaves the rendered surface byte-identical:

    uv run python -c "from gzkit.content.models.bullet import Bullet; print('density_min' in Bullet.model_fields)"  # -> False
    uv run gz agent sync control-surfaces && git diff --stat AGENTS.md   # -> empty (AGENTS.md playback unchanged)
    grep -RIn 'render_template("agents")' src/gzkit/   # -> no match (monolith fallback retired)

Full sweep green: 6170/6170 unittests pass (receipt arb-step-unittest-df7824927c664f9b834875edb5d9a568); ruff clean (arb-ruff-87c0389a14a647a49747af0eab315e3f); typecheck clean (arb-step-typecheck-354c407751cc4cea80fe455efd85d750); mkdocs --strict clean (arb-step-mkdocs-7c996eccbeb746f78394d9aae2c3b6cb); gz validate --documents / --invariant-coherence / --cli-alignment all pass; gz covers behavior_uncovered_reqs=0.

### Implementation Summary


- Retired the inert density-dial: removed `Bullet.density_min` field + `_enforce_judgment_floor` validator (bullet.py), the `_project_for_temperature`/`_bullet_renders`/`_TEMP_RANK` render filter (pipeline.py), and the coupled `density_min="lite"` kwarg (invariants.py) + dead JSON-schema property (constitutional_invariant.json). Byte-parity proven: render WITH vs WITHOUT projection = 28176 B identical.
- Retired the residual monolith `render_template("agents")` fallback (sync_surfaces.py); `sync_agents_md` now routes every bootstrap path (project-local AND packaged template) through the deterministic model pipeline — no monolith path remains.
- Refreshed `docs/governance/agent-control-surface-rendering-substrate.md` to the corpus→compress→rendition→playback + invariant-tier mechanism and added the Agent Orientation Index (surface→canonical-model→doctrine→load-command map; "do not re-derive from source").
- Recorded the items-18-27-active / 09+11-17-withdrawn disposition + #519 relief route on the active `build-to-1.0-campaign-2026-06-10.md` (operator-redirected from the frozen `return-to-health-plan`).
- Tests: reworked 5 content test modules + added a discriminating bare-bootstrap REQ-27-03 test; 72 OBPI-scoped tests pass, full suite 6170 pass.
- Files modified: 15 (5 src, 6 tests, 3 docs/data, 1 brief); 0 created.
- Date completed: 2026-06-15.
- Attestation status: operator-attested "attest completed" (Gate 5, Heavy/foundation; no self-close).
- Defects noted: 2 in-flight allowlist amendments (operator-approved, Gate Friction loop); 1 self-introduced malformed insight record fixed (evidence list shape).

## Tracked Defects

**22 ↔ 27 sync seam.** OBPI-22 establishes the committed-rendition store + playback and points `sync_agents_md` at it (it may keep a transition fallback). This OBPI retires the residual monolith `render_template("agents")` fallback so sync reads ONLY the rendition store. The two edits to `sync_surfaces.py` are sequenced (22 then 27); this OBPI removes the OLD path, it does not re-author the NEW one. **23 ↔ 27 substrate-doc seam:** OBPI-23 adds a narrow invariant-tier subsection to the substrate doc; this OBPI does the broader mechanism refresh + orientation index. Both are sequenced edits to the same file. Confirm both seams at Stage 1 brief-reconcile.

_No further defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.37-27 capstone disposition: retired the proven-inert density-dial (Bullet.density_min field + _enforce_judgment_floor validator + the _project_for_temperature render filter + coupled invariants.py kwarg / schema property) and the residual monolith render_template("agents") sync fallback; refreshed the agent-control-surface substrate doctrine to corpus→compress→rendition→playback + invariant-tier and added the Agent Orientation Index; finalized the items-18-27-active / 09+11-17-withdrawn disposition on the active build-to-1.0-campaign doc. Render byte-identical (28176 B, AGENTS.md playback unchanged); full suite 6170/6170 pass (receipt arb-step-unittest-df7824927c664f9b834875edb5d9a568); ruff clean (arb-ruff-87c0389a14a647a49747af0eab315e3f), typecheck clean (arb-step-typecheck-354c407751cc4cea80fe455efd85d750), mkdocs --strict clean (arb-step-mkdocs-7c996eccbeb746f78394d9aae2c3b6cb); gz covers behavior_uncovered_reqs=0. Heavy/foundation Gate 5, operator-verbatim conversational.
- Date: 2026-06-15

---

**Date Completed:** 2026-06-15

**Evidence Hash:** -
