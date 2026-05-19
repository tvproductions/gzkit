# Plan: OBPI-0.0.37-01-invariant-schema-and-registry

**OBPI:** OBPI-0.0.37-01-invariant-schema-and-registry
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy | **Kind:** Foundation
**Audit verdict:** PASS (no plan-to-brief gaps)

## Context

Land the foundation primitive of CIC-1: a frozen Pydantic `ConstitutionalInvariant`
model, a JSON Schema mirror, and three seed JSON invariants. The registry is the
structural witness layer on which OBPI-02 (renderer) and OBPI-03 (drift validator)
both depend. No CLI verbs, no renderer, no validator scopes are introduced here.

The `governance/__init__.py` currently exports nothing (one-line docstring only).

## Files

### New
- `src/gzkit/governance/invariants.py` — `ConstitutionalInvariant` Pydantic model + `load_invariants`
- `src/gzkit/schemas/constitutional_invariant.json` — JSON Schema mirror
- `.gzkit/invariants/CIC-1.json` — composition invariant
- `.gzkit/invariants/CIC-2.json` — brief↔reality coherence invariant
- `.gzkit/invariants/foundation-adr-registers-invariant.json` — self-referential check
- `tests/governance/test_invariants.py` — REQ-derived test cases

### Modified
- `src/gzkit/governance/__init__.py` — export `ConstitutionalInvariant` and `load_invariants`

## Steps

### Step 1: Red — write failing tests (REQ-0.0.37-01-01 through 04)

Create `tests/governance/test_invariants.py` with test classes derived from the
four REQs. Tests MUST fail before implementation. Use `@covers` decorators.

Test structure:
- `TestConstitutionalInvariantModel` — REQ-0.0.37-01-01 (frozen, structural_witness min_length=1)
- `TestConstitutionalInvariantSchema` — REQ-0.0.37-01-02 (JSON Schema mirror strictness)
- `TestLoadInvariants` — REQ-0.0.37-01-03 + REQ-0.0.37-01-04 (loader returns seeds, raises on invalid)

### Step 2: Green — implement ConstitutionalInvariant model

Create `src/gzkit/governance/invariants.py`:
- `ConstitutionalInvariant(BaseModel)` with `ConfigDict(frozen=True, extra="forbid")`
- Fields: `id: str`, `claim: str`, `structural_witness: list[str]` with `Field(min_length=1)`,
  `composition_targets: list[str]`
- `load_invariants(root: Path) -> dict[str, ConstitutionalInvariant]` walks `.gzkit/invariants/*.json`,
  validates each against the JSON Schema, raises on validation failure, no silent skip

### Step 3: JSON Schema mirror

Create `src/gzkit/schemas/constitutional_invariant.json`:
- `additionalProperties: false`
- Required keys: `id`, `claim`, `structural_witness`, `composition_targets`
- `structural_witness`: `{"type": "array", "minItems": 1, "items": {"type": "string"}}`
- `composition_targets`: `{"type": "array", "items": {"type": "string"}}`

### Step 4: Update __init__.py

Add exports in `src/gzkit/governance/__init__.py`:
- `from gzkit.governance.invariants import ConstitutionalInvariant, load_invariants`
- `__all__` listing both names

### Step 5: Seed JSON invariants

Create three files under `.gzkit/invariants/`:
- `CIC-1.json`: claim text from ADR § Decision CIC-1 paragraph; structural_witness includes
  `gz validate --invariant-coherence` (forward-ref per brief note); composition_targets: `["AGENTS.md"]`
- `CIC-2.json`: claim text from ADR § Decision CIC-2 paragraph; structural_witness includes
  `gz validate --brief-reconcile`, `gz obpi pipeline (stage 1)`, `gz obpi complete (stage 5)`;
  composition_targets: `[]`
- `foundation-adr-registers-invariant.json`: claim = "Every foundation-kind ADR registers ≥1
  invariant in .gzkit/invariants/"; structural_witness: `["gz validate --foundation-registers-invariant"]`;
  composition_targets: `[]`

All three seed JSONs must pass `load_invariants` validation.

### Step 6: Verify

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_invariants -v
uv run gz covers OBPI-0.0.37-01-invariant-schema-and-registry --json
```

Run the three brief verification snippets from § Verification.

### Step 7: Present OBPI Acceptance Ceremony (Stage 4 human gate)

Wait for operator attestation before Stage 5.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_invariants -v
```

## Notes

- JSON via stdlib `json` module; `jsonschema` 4.26.0 confirmed available
- `pyyaml` removed from `invariants.py` per AGENTS.md "No YAML for gzkit data files" rule (2026-05-19 operator course-correction)
- Forward-references in seed JSON `structural_witness` fields are intentional per brief note:
  `gz validate --invariant-coherence` (OBPI-03), `gz validate --brief-reconcile` (OBPI-05),
  `gz validate --foundation-registers-invariant` (future) — unresolvable until those OBPIs land
- Advisory scope collisions with OBPI-0.0.42-* and OBPI-0.15.0-04 are non-blocking (no locks)
- Gate 3 (Docs): explicitly deferred to OBPI-02/06 per brief; no operator-facing CLI introduced here
- Gate 4 (BDD): explicitly deferred to OBPI-02 per brief; unit tests are the right fidelity here
