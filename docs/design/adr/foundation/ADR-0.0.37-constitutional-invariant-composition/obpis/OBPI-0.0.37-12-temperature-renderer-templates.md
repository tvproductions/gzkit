---
id: OBPI-0.0.37-12-temperature-renderer-templates
parent: ADR-0.0.37-constitutional-invariant-composition
item: 12
lane: Heavy
status: Draft
---

# OBPI-0.0.37-12-temperature-renderer-templates: Temperature Renderer + lite/medium/heavy Templates

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #12 — "OBPI-0.0.37-12 — Temperature renderer + lite/medium/heavy templates (per-bullet density floor; Judgment always renders; deterministic byte-stable)"

**Status:** Draft

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

Rendering the same AgentContract at lite vs heavy yields a smaller-but-Judgment-complete
surface vs the full-fidelity surface, byte-stably.

### Implementation Summary

- Decision item implemented (verbatim): "OBPI-0.0.37-12 — Temperature renderer + lite/medium/heavy templates (per-bullet density floor; Judgment always renders; deterministic byte-stable)."
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
