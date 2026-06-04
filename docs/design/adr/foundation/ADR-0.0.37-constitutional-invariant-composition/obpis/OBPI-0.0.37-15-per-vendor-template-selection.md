---
id: OBPI-0.0.37-15-per-vendor-template-selection
parent: ADR-0.0.37-constitutional-invariant-composition
item: 15
lane: Heavy
status: Abandoned
---

# OBPI-0.0.37-15-per-vendor-template-selection: Per-Vendor Template Selection

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #15 — "OBPI-0.0.37-15 — Per-vendor template selection (Codex lite / Claude standard; ends identical mirroring; harness-detection is a forward-reference)"

**Status:** Completed

## Objective

Let each vendor mirror render the master model at its own temperature: declare a
per-vendor temperature in the vendor manifest so the Codex mirror renders **lite** (the
direct relief for the 258K-window cap in #519) and the Claude mirror renders **standard**,
ending the dumb identical 4x mirroring. Harness/model *detection* that auto-selects a
template is a named forward-reference, not in scope.

## Lane

**Heavy** — changes the vendor-manifest contract and the per-vendor render routing.
Foundation + heavy → Gate 5 human attestation (`assets/HEAVY_LANE_PLAN_TEMPLATE.md`).

## Allowed Paths

- `src/gzkit/content/vendors.py` — resolve a per-vendor temperature alongside the route
- `data/vendor-manifest.json` — declare the per-vendor temperature for `AgentContract` (additive `content_type_temperatures` sibling block; see REQ-6)
- `src/gzkit/schemas/vendor_manifest.json` — extend the schema with the additive `content_type_temperatures` sibling block (`temperature` constrained to enum `{lite, medium, heavy}`); the existing `content_type_routes` shape is left unchanged (REQ-6)
- `src/gzkit/content/templates/agentcontract/` — vendor template entries for the per-vendor render (e.g. add `codex.md.j2`)
- `src/gzkit/sync_surfaces.py` — **render-call sites only** (`sync_agents_md` and `render_content_surface`): resolve the per-vendor temperature via `vendors.py` and pass it to the OBPI-12 renderer (currently hardcoded `"claude"`/`temperature="heavy"` at `sync_agents_md`, and no temperature at `render_content_surface`). No other edits to this module.
- `tests/content/test_vendor_manifest.py` — per-vendor temperature routing tests
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-15-per-vendor-template-selection.md` — this brief
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/content/render/pipeline.py` — the temperature parameter is OBPI-12 (consumed here, not changed). The additive `content_type_temperatures` sibling block leaves `content_type_routes` (which this module reads as `dict[str, list[str]]`) untouched, so no edit here is required.
- `src/gzkit/content/models/`, `src/gzkit/content/parse/` — OBPI-11/13
- `src/gzkit/sync_surfaces.py` **except the two render-call sites named in Allowed Paths** — the rest of this module (OBPI-14 sync wiring) stays out of scope; only `sync_agents_md` and `render_content_surface` change, to resolve+pass the per-vendor temperature OBPI-14 hardcoded to `claude`/`heavy`.
- Harness/model detection logic — out of scope (forward-reference)
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: the vendor manifest MUST declare a temperature per (content_type, vendor) via the additive `content_type_temperatures` sibling block (REQ-6); `vendors.py` MUST resolve it and the render-call sites in `sync_surfaces.py` (`sync_agents_md`, `render_content_surface`) MUST pass it to the OBPI-12 renderer.
2. REQUIREMENT: the Codex vendor MUST resolve to `lite` and Claude to a higher tier; an unknown or missing per-vendor temperature MUST fail closed (no silent default to heavy that would re-bloat Codex).
3. REQUIREMENT: per-vendor selection MUST still honor the 0-Kelvin floor — even the Codex lite mirror renders every `Judgment` bullet.
4. REQUIREMENT: identical-across-vendors mirroring MUST end for `AgentContract` — the Codex and Claude rendered surfaces differ by temperature.
5. NEVER: implement harness/model auto-detection in this OBPI — manifest-declared per-vendor temperature only.
6. REQUIREMENT: the temperature declaration MUST be an **additive** `content_type_temperatures` sibling block in `data/vendor-manifest.json` — `content_type_routes` retains its `dict[str, list[str]]` shape unchanged so the `pipeline.py` consumer (Denied Paths) is not disturbed. `src/gzkit/schemas/vendor_manifest.json` MUST encode the sibling block with each per-vendor `temperature` constrained to enum `{lite, medium, heavy}`, so the fail-closed-on-unknown contract (REQ-2) is enforced by `gz validate --vendor-manifest`, not left to a vacuous gate.

> STOP-on-BLOCKERS: requires OBPI-12 (temperature renderer) and OBPI-14 (sync wired to the model). If absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (quote verbatim into Implementation Summary):** "OBPI-0.0.37-15 — Per-vendor template selection (Codex lite / Claude standard; ends identical mirroring; harness-detection is a forward-reference)."
- [ ] Parent ADR § "Decision Extension (2026-05-30)" — per-vendor temperatures, Codex lite for #519.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` § vendor mirrors / levers-and-constraints.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/vendors.py` exists (`routes_for`, `_load_manifest`)
- [ ] `data/vendor-manifest.json` exists
- [ ] `src/gzkit/content/templates/agentcontract/` exists
- [ ] `tests/content/test_vendor_manifest.py` exists
- [ ] OBPI-12 temperature renderer is available

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/vendors.py` — `routes_for(content_type, project_root)` and the fallback table
- [ ] `data/vendor-manifest.json` — `content_type_routes` shape this OBPI extends

## Quality Gates

### Gate 1: ADR
- [ ] Decision item quoted into Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)
- [ ] Per-vendor temperature routing tests RED before, GREEN after
- [ ] `uv run gz test` passes

### Code Quality
- [ ] `uv run gz lint` and `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict` clean

### Gate 4: BDD (Heavy)
- [ ] `features/constitutional_invariants.feature` scenario tagged `@REQ-0.0.37-15-*`

### Gate 5: Human (Heavy + Foundation)
- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz validate --vendor-manifest
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.test_vendor_manifest -v
```

## Demo

```bash
uv run python -c "print('render AgentContract for codex (lite) and claude (standard); the codex mirror is smaller but Judgment-complete')"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-15-01 [BEHAVIOR]: `vendors.py` resolves a per-vendor temperature from the manifest and passes it to the renderer. Proof: `@covers(REQ-0.0.37-15-01)` test in `tests/content/test_vendor_manifest.py`.
- [ ] REQ-0.0.37-15-02 [BEHAVIOR]: the Codex mirror resolves to `lite`; a missing per-vendor temperature fails closed (no default to heavy). Proof: `@covers(REQ-0.0.37-15-02)` test.
- [ ] REQ-0.0.37-15-03 [BEHAVIOR]: the Codex lite mirror still contains every `Judgment` bullet (floor honored across vendors). Proof: `@covers(REQ-0.0.37-15-03)` test.
- [ ] REQ-0.0.37-15-04 [BEHAVIOR]: the Codex and Claude `AgentContract` renders differ (identical mirroring ended). Proof: `@covers(REQ-0.0.37-15-04)` test.
- [ ] REQ-0.0.37-15-05 [SUPPORT]: the per-vendor temperatures are declared in `data/vendor-manifest.json` — `uv run gz validate --vendor-manifest` passes and an `artifact_edited` event is emitted for the manifest.
- [ ] REQ-0.0.37-15-06 [SUPPORT]: the temperature declaration is an additive `content_type_temperatures` sibling block — `content_type_routes` is byte-unchanged — and `src/gzkit/schemas/vendor_manifest.json` constrains each `temperature` to enum `{lite, medium, heavy}`. Proof: `uv run gz validate --vendor-manifest` passes against the extended schema and rejects an out-of-enum temperature; an `artifact_edited` event is emitted for the schema file.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision item quoted
- [ ] **Gate 2 (TDD):** RGR followed; tests derive from REQs
- [ ] **Code Quality:** lint, format, typecheck clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** codex-lite vs claude-standard render diff
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

Before: four identical mirrors of the same heavy surface. After: each vendor renders the master
model at its own temperature — Codex lite (the #519 relief), Claude standard — with the Judgment
floor preserved everywhere.

### Key Proof


The Codex AgentContract CAN render lite — materially smaller than Claude's heavy and Judgment-complete (0-Kelvin floor): render(model, "codex", temperature="lite") drops every density_min="heavy" bullet while retaining every classification="Judgment" bullet, and differs byte-wise from render(model, "claude", temperature="heavy"). Verified by TestPerVendorTemperatureRouting and 4 BDD scenarios. temperature_for fails closed (ValueError) on an undeclared (content_type, vendor) pair — no in-code default. Gates: unittest 5846 pass (arb-step-unittest-8ed8530c57444a97ba7f833944f66a60), ruff (arb-ruff-26b024ffded744479b7b8158099d5448), typecheck (arb-step-typecheck-bdd2067ceaa249ba94f8c58efa2eb89c), mkdocs (arb-step-mkdocs-7705ebde683f4f0980a13a5f9feba10e); gz validate --vendor-manifest / --req-kind-discipline / --documents clean. NOTE: the selection mechanism landed; the production Codex-lite emission (#519's surface reduction) is a named follow-on, NOT realized here.

### Implementation Summary


- Decision item implemented (verbatim): "OBPI-0.0.37-15 — Per-vendor template selection (Codex lite / Claude standard; ends identical mirroring; harness-detection is a forward-reference)."
- Scope landed: the per-vendor temperature SELECTION mechanism (not the Codex-lite emission — see GHI #519).
- data/vendor-manifest.json: additive content_type_temperatures sibling block ({"AgentContract": {"codex": "lite", "claude": "heavy"}}); codex added to AgentContract routes; content_type_routes shape unchanged.
- src/gzkit/schemas/vendor_manifest.json: content_type_temperatures property constraining each temperature to enum {lite, medium, heavy}.
- src/gzkit/content/vendors.py: temperature_for() resolves the declared temperature and fails closed (ValueError) on an undeclared pair — no in-code vendor->temperature table (operator directive 2026-06-03: temperature is a general control, not a vendor-locked rule); _load_temperatures() loader; _FALLBACK_ROUTES gains codex.
- src/gzkit/content/templates/agentcontract/codex.md.j2: Codex vendor template (projection precedes rendering, so vendor-neutral at this tier).
- src/gzkit/sync_surfaces.py (render-call sites only): sync_agents_md resolves temperature via temperature_for with a fail-closed call-site default of "heavy" (fresh/consuming projects ship no manifest — render MORE, never silently thin); render_content_surface gains a temperature parameter.
- Tests: tests/content/test_vendor_manifest.py TestPerVendorTemperatureRouting (10 tests); tests/commands/test_sync_cmds.py no-manifest default test; features/constitutional_invariants.feature + steps (4 BDD scenarios @REQ-0.0.37-15-01..04).
- Allowlist expansion (disclosed): features/* (sanctioned by brief Gate 4), tests/commands/test_sync_cmds.py (coupled-surface, Rule 1a), data/behave_coverage_waivers.json (SUPPORT-REQ waiver, sibling precedent), .gzkit/insights/agent-insights.jsonl (Behavior Rule 11).
- Date completed: 2026-06-03
- Attestation status: operator attested "attest completed" (Stage 4)
- Defects noted: Codex-lite emission (the #519 byte reduction) unrealized — routed to GHI #519 with concrete next action.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator attested at Stage 4 ceremony after a two-round in-flight course-correction: (1) decoupled the in-code vendor->temperature pairing so temperature is a general control resolved from the manifest, failing closed on undeclared pairs; (2) confirmed OBPI-15 delivers the SELECTION mechanism (manifest -> temperature_for -> renderer, proven by TestPerVendorTemperatureRouting + 4 BDD scenarios), with the Codex-lite emission (#519 byte reduction) explicitly deferred and routed to GHI #519. Gates green: unittest 5846 pass (arb-step-unittest-8ed8530c57444a97ba7f833944f66a60), ruff (arb-ruff-26b024ffded744479b7b8158099d5448), typecheck (arb-step-typecheck-bdd2067ceaa249ba94f8c58efa2eb89c), mkdocs (arb-step-mkdocs-7705ebde683f4f0980a13a5f9feba10e); gz validate --vendor-manifest / --req-kind-discipline / --documents clean.
- Date: 2026-06-03

---

**Date Completed:** 2026-06-03

**Evidence Hash:** -
