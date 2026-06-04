---
id: OBPI-0.0.37-12-temperature-renderer-templates
parent: ADR-0.0.37-constitutional-invariant-composition
item: 12
lane: Heavy
status: Abandoned
# req_atomic exemption (GHI #563, return-to-health 2026-06-01): each REQ is one
# indivisible behavioral contract on render() — no labor subdivision was needed
# or performed, so a single seq=01 TASK per REQ is honest, not a coarse bucket.
req_atomic:
  - REQ-0.0.37-12-01  # temperature accept/reject: one fail-closed validation guard
  - REQ-0.0.37-12-02  # per-bullet density floor + Judgment-always: one projection rule
  - REQ-0.0.37-12-03  # section withhold-by-tier/enabled + ordering: one projection rule
  - REQ-0.0.37-12-04  # byte-determinism across calls/processes: one invariant
  - REQ-0.0.37-12-05  # three tiers as one parameterized template set: one structural constraint
---

# OBPI-0.0.37-12-temperature-renderer-templates: Temperature Renderer + lite/medium/heavy Templates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #12 — "OBPI-0.0.37-12 — Temperature renderer + lite/medium/heavy templates (per-bullet density floor; Judgment always renders; deterministic byte-stable)"

**Status:** Completed

## Objective

Extend the ADR-0.0.34 render pipeline (`render(model, vendor)`) to take a **temperature**
(lite / medium / heavy) and a section-inclusion set, and project the OBPI-11 master model
to deterministic bytes: a bullet renders iff `temperature >= bullet.density_min`; a
`Judgment` bullet renders at every temperature (the 0-Kelvin floor); a section with
`enabled = False` or `tier` above the temperature is withheld. Defines the three named
templates as the canonical density tiers. Renderer only — wiring is OBPI-14.

## Lane

**Heavy** — changes the `render()` runtime signature/contract and template behavior.
Foundation + heavy → Gate 5 human attestation required (`assets/HEAVY_LANE_PLAN_TEMPLATE.md`).

## Allowed Paths

- `src/gzkit/content/render/pipeline.py` — add the `temperature` + section-set parameters; density-aware projection
- `src/gzkit/content/templates/agentcontract/` — the AgentContract Jinja2 templates that iterate bullets/sections with density logic
- `tests/content/test_render_pipeline.py` — temperature-rendering behavior tests
- `tests/content/test_byte_stability.py` — byte-stability across repeated renders at each temperature
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-12-temperature-renderer-templates.md` — this brief
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/content/models/` — the model is OBPI-11 (consumed read-only here)
- `src/gzkit/content/parse/` — reverse-parse is OBPI-13
- `src/gzkit/sync_surfaces.py`, `src/gzkit/governance/compose.py` — sync wiring is OBPI-14
- `src/gzkit/content/vendors.py`, `data/vendor-manifest.json` — per-vendor selection is OBPI-15
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `render()` MUST accept a `temperature` value constrained to `lite | medium | heavy`; an unknown temperature is rejected before any template lookup (fail-closed).
2. REQUIREMENT: a bullet MUST render iff its `density_min` is at or below the requested temperature; a `Judgment`-classified bullet MUST render at EVERY temperature regardless of `density_min` (the 0-Kelvin floor; ADR § Decision Extension).
3. REQUIREMENT: a section MUST be withheld when `enabled = False` or when its `tier` is above the requested temperature; section ordering MUST follow `order`.
4. REQUIREMENT: rendering MUST remain byte-deterministic — identical (model, vendor, temperature) inputs produce identical bytes across calls and processes (substrate byte-stability invariant; OBPI-0.0.37-02 precedent).
5. REQUIREMENT: the three named tiers (lite, medium, heavy) MUST be a render parameter over one template set, not three forked template files.
6. NEVER: rewrite, sync, or migrate any agent-control surface in this OBPI — renderer only.

> STOP-on-BLOCKERS: requires OBPI-11 landed (`density_min`, `classification`, section `tier`/`enabled`/`order`). If absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (quote verbatim into Implementation Summary):** "OBPI-0.0.37-12 — Temperature renderer + lite/medium/heavy templates (per-bullet density floor; Judgment always renders; deterministic byte-stable)."
- [ ] Parent ADR § "Decision Extension (2026-05-30)" — the temperature/floor semantics.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` — byte-stability and prompt-assembly-order constraints the renderer must preserve.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/render/pipeline.py` exists
- [ ] `src/gzkit/content/templates/agentcontract/` exists
- [ ] `tests/content/test_render_pipeline.py` and `tests/content/test_byte_stability.py` exist
- [ ] OBPI-11 fields are present on the model

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/render/pipeline.py` — current `render(model, vendor)` (Jinja2, StrictUndefined, `model_dump()` byte-stable)
- [ ] `src/gzkit/governance/compose.py` — the ADR-0.0.37-02 registry renderer (byte-deterministic precedent)

## Quality Gates

### Gate 1: ADR
- [ ] Decision item quoted into Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)
- [ ] Temperature + floor + byte-stability tests RED before, GREEN after
- [ ] `uv run gz test` passes

### Code Quality
- [ ] `uv run gz lint` and `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict` clean

### Gate 4: BDD (Heavy)
- [ ] `features/constitutional_invariants.feature` scenario tagged `@REQ-0.0.37-12-*`

### Gate 5: Human (Heavy + Foundation)
- [ ] Human attestation recorded (`assets/HEAVY_LANE_PLAN_TEMPLATE.md`)

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.test_render_pipeline -v
uv run -m unittest tests.content.test_byte_stability -v
```

## Demo

```bash
uv run python -c "print('render an AgentContract at lite vs heavy and diff the byte length')"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-12-01 [BEHAVIOR]: `render(model, vendor, temperature='lite')` omits bullets whose `density_min` exceeds lite, but never a `Judgment` bullet. Proof: `@covers(REQ-0.0.37-12-01)` test in `tests/content/test_render_pipeline.py`.
- [ ] REQ-0.0.37-12-02 [BEHAVIOR]: an unknown `temperature` raises before template lookup (fail-closed). Proof: `@covers(REQ-0.0.37-12-02)` test.
- [ ] REQ-0.0.37-12-03 [BEHAVIOR]: a section with `enabled=False` or `tier` above the temperature is absent from output; section order follows `order`. Proof: `@covers(REQ-0.0.37-12-03)` test.
- [ ] REQ-0.0.37-12-04 [BEHAVIOR]: repeated `render()` of the same (model, vendor, temperature) yields byte-identical output. Proof: `@covers(REQ-0.0.37-12-04)` test in `tests/content/test_byte_stability.py`.
- [ ] REQ-0.0.37-12-05 [BEHAVIOR]: the heavy temperature renders a strict superset of lite content for the same model (monotonic density). Proof: `@covers(REQ-0.0.37-12-05)` test.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision item quoted
- [ ] **Gate 2 (TDD):** RGR followed; tests derive from REQs
- [ ] **Code Quality:** lint, format, typecheck clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** lite-vs-heavy render diff
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

Before: one fixed render shape; density is hand-managed in prose. After: density is a render
parameter over one template set — lite/medium/heavy fall out of the same model, and the
Judgment floor is structurally guaranteed.

### Key Proof


Same AgentContract (Judgment + lite + medium + heavy bullets; lite-tier "Core" pillar + heavy-tier "Deep Dive" pillar) rendered at each temperature:
  lite: 131 bytes / medium: 159 bytes / heavy: 231 bytes
  heavy contains everything lite has: True
  byte-stable (lite x2): True
At lite the Judgment and lite-floor bullets render and the "Core" section renders; the medium/heavy bullets and the heavy-tier "Deep Dive" section are withheld — density dials monotonically. Receipts: arb-step-unittest-9093b259d9b34f2b8e4a69a8e623bba2 (5810/5810 pass), arb-step-unittest-0e9fe083a0ba47188b73102dc218fd14 (19/19 scoped), arb-ruff-1a98e4e545bb4540b84aa304fa790db4, arb-step-typecheck-6ef6ec0f39f04a8a8fb3f12e694dd6ec, arb-step-mkdocs-93f27079619b4d2baa3a2b0b4873a0f8.

### Implementation Summary


- Decision item implemented (verbatim): "OBPI-0.0.37-12 — Temperature renderer + lite/medium/heavy templates (per-bullet density floor; Judgment always renders; deterministic byte-stable)."
- render() gains temperature: str = "heavy"; fail-closed ValueError on unknown temperature before template lookup (REQ-02).
- _bullet_renders() predicate: Judgment always renders (0-Kelvin floor); density_min=None never thinned; else density_min <= temperature (REQ-01, REQ-05).
- _project_for_temperature(): withholds disabled/above-tier sections, sorts by order, filters bullets within kept pillars — section-withholding wins over the Judgment floor (REQ-03), pinned by test_judgment_bullet_in_withheld_section_is_dropped.
- Byte-deterministic via model_copy + stable sort (REQ-04). Template agentcontract/claude.md.j2 now renders pillars.
- Files modified: src/gzkit/content/render/pipeline.py, src/gzkit/content/templates/agentcontract/claude.md.j2, tests/content/test_render_pipeline.py, tests/content/test_byte_stability.py. 8 tests added.
- Date completed: 2026-06-01. Behave waived (no CLI surface; deferred to ADR-0.0.37 closeout per OBPI-11 sibling precedent).

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.37-12 temperature renderer accepted at Heavy+Foundation Gate 5: render() projects the AgentContract master model at lite/medium/heavy with the Judgment 0-Kelvin floor and section-withholding-wins resolution; 5/5 REQs covered (parity uncovered_reqs=0), full suite 5810 pass (arb-step-unittest-9093b259d9b34f2b8e4a69a8e623bba2), lint/typecheck/mkdocs clean (arb-ruff-1a98e4e545bb4540b84aa304fa790db4, arb-step-typecheck-6ef6ec0f39f04a8a8fb3f12e694dd6ec, arb-step-mkdocs-93f27079619b4d2baa3a2b0b4873a0f8); behave waived (no CLI surface, deferred to ADR-0.0.37 closeout). Brick 1 of 4 in the #519 remediation chain.
- Date: 2026-06-01

---

**Date Completed:** 2026-06-01

**Evidence Hash:** -
