---
id: OBPI-0.0.37-11-density-aware-master-model
parent: ADR-0.0.37-constitutional-invariant-composition
item: 11
lane: Heavy
status: Abandoned
---

# OBPI-0.0.37-11-density-aware-master-model: Density-Aware Master Content Model

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #11 — "OBPI-0.0.37-11 — Density-aware master content model (reconcile ConstitutionalInvariant into AgentContract/Pillar/Bullet; classification + witness + rationale_ref + density_min; section order/enabled/tier)"

**Status:** Completed

## Objective

Extend the ADR-0.0.34 content-model substrate so a single `AgentContract` model can
hold the agent contract at MAX fidelity and be rendered at any density: add the
`Bullet` fields `classification`, `witness`, `rationale_ref`, `density_min`; add a
`Pillar`/section primitive carrying `order`, `enabled`, `tier`; and reconcile the
ADR-0.0.37 `ConstitutionalInvariant` registry into that model so it is the
foundation-classified subset, not a parallel substrate. This OBPI delivers the
**schema only** — the renderer (OBPI-12), migration (OBPI-13), and wiring (OBPI-14)
consume it.

## Lane

**Heavy** — adds Pydantic model fields and JSON Schema surface (a schema/runtime
contract). Foundation kind + heavy lane → Gate 5 human attestation is required before
completion (ADR-0.0.36; `assets/HEAVY_LANE_PLAN_TEMPLATE.md` governs the implementation
plan).

## Allowed Paths

- `src/gzkit/content/models/bullet.py` — add `classification`, `witness`, `rationale_ref`, `density_min` fields to `Bullet`
- `src/gzkit/content/models/agent_contract.py` — restructure `AgentContract` to carry sections at full fidelity, and add the `Pillar`/`Section` primitive (`order`, `enabled`, `tier`) co-located here, per the substrate doctrine's worked example
- `src/gzkit/content/models/__init__.py` — export the extended models
- `src/gzkit/governance/invariants.py` — reconcile `ConstitutionalInvariant` to the bullet form (claim→text, structural_witness→witness, classification carried)
- `src/gzkit/schemas/constitutional_invariant.json` — extend the JSON Schema mirror to match the reconciled model
- `tests/content/models/test_fields.py` — field-validation tests for the new fields and the classification enum
- `tests/content/test_round_trip_agent_contract.py` — round-trip preservation of the new fields
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-11-density-aware-master-model.md` — this brief
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/governance/compose.py` and `src/gzkit/content/render/**` — the temperature renderer is OBPI-12
- `src/gzkit/content/parse/**` — reverse-parse migration is OBPI-13
- `src/gzkit/sync_surfaces.py` — sync wiring is OBPI-14
- `src/gzkit/templates/agents.md`, `AGENTS.md`, `.gzkit/agents.local.md` — surface migration is OBPI-13/14; this OBPI does not render or rewrite any surface
- New runtime dependencies; CI workflow files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `Bullet` MUST gain `classification` (one of `Mechanical | Promotable | Judgment | Ambiguous`), `witness` (the enforcing gate command, `str | None`), `rationale_ref` (a docs pointer, `str | None`), and `density_min` (the lowest temperature at which the bullet renders). Invalid `classification` values MUST be rejected at construction (frozen, `extra="forbid"` already inherited from `BaseContentModel`).
2. REQUIREMENT: A `Pillar`/section primitive MUST carry `order: int`, `enabled: bool`, and `tier` (the section's lowest-temperature membership), so sections are data-driven (add/withhold a section = add/flip a row, never edit a template).
3. REQUIREMENT: The `density_min` floor MUST be expressible such that `Judgment`-classified bullets are pinned to render at every temperature — the model MUST make "render a Judgment bullet only above some temperature" unrepresentable or invariant-violating (the 0-Kelvin floor; ADR § Decision Extension).
4. REQUIREMENT: A reconciliation function MUST map an existing `ConstitutionalInvariant` (`id`, `claim`, `structural_witness`, `composition_targets`) into the bullet form so the registry is the foundation-classified subset of the master model — NEVER a second parallel model.
5. REQUIREMENT: Round-trip fidelity MUST hold for the extended model: `parse(render(model)) == model` including all new fields (the substrate doctrine's binding round-trip contract).
6. ALWAYS: Reconcile this brief against the parent ADR § Decision Extension before implementation.
7. NEVER: render, rewrite, or migrate any agent-control surface in this OBPI — schema only.

> STOP-on-BLOCKERS: requires `src/gzkit/content/models/base.py` (`BaseContentModel`), `agent_contract.py`, `bullet.py`, and `src/gzkit/governance/invariants.py` present. If any is absent, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item this OBPI implements (quote verbatim into Implementation Summary):** "OBPI-0.0.37-11 — Density-aware master content model (reconcile ConstitutionalInvariant into AgentContract/Pillar/Bullet; classification + witness + rationale_ref + density_min; section order/enabled/tier)."
- [ ] Parent ADR § "Decision Extension (2026-05-30): CIC-1 Density-Dial Composition" — the temperature/density/0-Kelvin-floor mechanism this schema must support.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` — the substrate doctrine; its worked `AgentContract`/`Pillar`/`Bullet` example is the target shape for this OBPI. Read before designing the model.
- [ ] `.claude/rules/models.md` — Pydantic model policy (frozen, `extra="forbid"`, `Field(...)` descriptions, `str | None`).

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/models/base.py` exists (`BaseContentModel`)
- [ ] `src/gzkit/content/models/agent_contract.py` and `src/gzkit/content/models/bullet.py` exist
- [ ] `src/gzkit/governance/invariants.py` and `src/gzkit/schemas/constitutional_invariant.json` exist
- [ ] `tests/content/models/test_fields.py` and `tests/content/test_round_trip_agent_contract.py` exist

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/models/base.py` — `BaseContentModel` (frozen, `extra="forbid"`, `schema_version`)
- [ ] `src/gzkit/content/models/agent_contract.py` — current `AgentContract` (name/purpose/tech_stack/rules)
- [ ] `src/gzkit/content/models/bullet.py` — current `Bullet` (text/indent)
- [ ] `src/gzkit/governance/invariants.py` and `src/gzkit/schemas/constitutional_invariant.json` — the registry model to reconcile
- [ ] `tests/content/test_round_trip_agent_contract.py` — the round-trip pattern to extend

## Quality Gates

### Gate 1: ADR

- [ ] Decision item quoted into Implementation Summary
- [ ] Scope recorded in this brief

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from the acceptance REQs below, not from the implementation
- [ ] Field-validation tests RED before model changes, GREEN after
- [ ] `uv run gz test` passes

### Code Quality

- [ ] `uv run gz lint` clean
- [ ] `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)

- [ ] `uv run mkdocs build --strict` clean
- [ ] Substrate doctrine cross-reference updated if the realized model diverges from its worked example

### Gate 4: BDD (Heavy)

- [ ] `features/constitutional_invariants.feature` scenario tagged `@REQ-0.0.37-11-*` for the reconciliation behavior

### Gate 5: Human (Heavy + Foundation)

- [ ] Human attestation recorded (mandatory; see `assets/HEAVY_LANE_PLAN_TEMPLATE.md`)

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.models.test_fields -v
uv run -m unittest tests.content.test_round_trip_agent_contract -v
```

## Demo

```bash
# A Judgment bullet is pinned to render at every temperature (0-Kelvin floor);
# a Mechanical bullet carries its witness and thins out at low temperature.
uv run python -c "from gzkit.content.models.bullet import Bullet; b = Bullet(text='Surface assumptions before implementing.', classification='Judgment'); print(b.classification, b.density_min)"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-11-01 [BEHAVIOR]: `Bullet` accepts and validates `classification`, `witness`, `rationale_ref`, `density_min`; an invalid `classification` raises at construction. Proof: `@covers(REQ-0.0.37-11-01)` test in `tests/content/models/test_fields.py`.
- [ ] REQ-0.0.37-11-02 [BEHAVIOR]: a `Pillar`/section model validates `order`, `enabled`, `tier`; `enabled=False` and `tier` are honored as data (no template edit needed to withhold a section). Proof: `@covers(REQ-0.0.37-11-02)` test in `tests/content/models/test_fields.py`.
- [ ] REQ-0.0.37-11-03 [BEHAVIOR]: the model makes a `Judgment` bullet render-floor structural — a constructed model cannot express a `Judgment` bullet that is droppable below the floor. Proof: `@covers(REQ-0.0.37-11-03)` test asserting the floor invariant.
- [ ] REQ-0.0.37-11-04 [BEHAVIOR]: `reconcile_invariant(ConstitutionalInvariant) -> Bullet` maps `claim→text`, `structural_witness→witness`, and assigns a foundation `classification`; the registry round-trips through the master model. Proof: `@covers(REQ-0.0.37-11-04)` test in `tests/content/test_round_trip_agent_contract.py`.
- [ ] REQ-0.0.37-11-05 [SUPPORT]: `src/gzkit/schemas/constitutional_invariant.json` is updated to mirror the reconciled model — `uv run gz validate --documents` passes and the edit emits an `artifact_edited` ledger event.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision item quoted in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR followed; tests derive from the REQs above
- [ ] **Code Quality:** lint, format, typecheck clean
- [ ] **Value Narrative:** before (skeletal AgentContract, parallel registry) vs now (one density-aware master model) documented
- [ ] **Key Proof:** the Demo invocation runs
- [ ] **Gate 5:** human attestation recorded (heavy + foundation)

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

Before: `AgentContract` is a four-field skeleton and the ADR-0.0.37 invariant registry
is a parallel, orphaned model; the agent contract lives as hand-authored prose. After:
one density-aware master model holds the contract at full fidelity with the classification,
witness, rationale-pointer, density-floor, and section metadata the temperature renderer
(OBPI-12) needs.

### Key Proof


reconcile_invariant + the Judgment 0-Kelvin floor proven live:

    $ uv run python -c "from gzkit.governance.invariants import ConstitutionalInvariant, reconcile_invariant; b=reconcile_invariant(ConstitutionalInvariant(id='CIC-1', claim='Every claim originates from the registry.', structural_witness=['gz validate --invariant-coherence'], composition_targets=['AGENTS.md'])); print(b.text,'|',b.classification,'|',b.density_min)"
    Every claim originates from the registry. | Mechanical | lite

    $ uv run python -c "from gzkit.content.models import Bullet; b=Bullet(text='Surface assumptions before implementing.', classification='Judgment'); print(b.classification, b.density_min)"
    Judgment lite

OBPI-scoped suite 22/22 green — receipt arb-step-unittestobpi11-e97345a2f82f4b93a531e974c04db99c. Full suite 5790 pass — arb-step-unittest-ca37476312944e72afb8baa2a69872f8.

### Implementation Summary


- Decision item (ADR-0.0.37 Decision Extension, 2026-05-30): density-aware master content model — reconcile ConstitutionalInvariant into AgentContract/Pillar/Bullet; classification + witness + rationale_ref + density_min; section order/enabled/tier.
- Bullet extended: classification (Mechanical|Promotable|Judgment|Ambiguous), witness (str|None), rationale_ref (str|None), density_min (lite|medium|heavy|None); model_validator pins Judgment bullets to density_min='lite' (the 0-Kelvin floor) and rejects any other value.
- Pillar section primitive added (id, title, order, enabled, tier, bullets); AgentContract gains pillars: list[Pillar] with backward-compat default [].
- reconcile_invariant(ConstitutionalInvariant) -> Bullet: claim->text, structural_witness[0]->witness, classification=Mechanical, density_min=lite — registry is the foundation-classified subset of the master model, not a parallel store.
- constitutional_invariant.json schema mirrors the reconciled model (optional classification + density_min hint fields).
- Files modified: src/gzkit/content/models/{bullet.py, agent_contract.py, __init__.py}; src/gzkit/governance/invariants.py; src/gzkit/schemas/constitutional_invariant.json; tests/content/models/test_fields.py; tests/content/test_round_trip_agent_contract.py.
- Tests added: 22 (TestDensityBulletFields 8; TestPillarFields 9 incl. frozen/extra=forbid + no-untyped-field checks; TestReconcileInvariant 5). Full suite 5790 pass.
- Spec-review + quality-review (two-stage) cleared; F-01 (Pillar registry) and F-04 (test-name over-claim) resolved in-flight.
- Date completed: 2026-05-31. Attestor: g0 ("attest completed").

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.37-11 density-aware master content model: Bullet gains classification/witness/rationale_ref/density_min with the Judgment 0-Kelvin floor, the Pillar section primitive is added, and reconcile_invariant bridges the constitutional-invariant registry into the ADR-0.0.34 content substrate (one spine, not two). 22 OBPI-scoped tests green (arb-step-unittestobpi11-e97345a2f82f4b93a531e974c04db99c), full suite 5790 pass (arb-step-unittest-ca37476312944e72afb8baa2a69872f8), lint/typecheck/docs clean (arb-ruff-b2dfa561e53743178ea5dca14147a469, arb-step-typecheck-029f95ed1e07479b9cb0d41ae43fa3b0, arb-step-mkdocs-5d89b25cd4354577879a018950d0c51c). Behave coverage waived (schema-only; BDD deferred to ADR-0.0.37 closeout per sibling-OBPI precedent).
- Date: 2026-05-31

---

**Date Completed:** 2026-05-31

**Evidence Hash:** -
