# Plan: OBPI-0.0.37-11-density-aware-master-model

## OBPI

OBPI-0.0.37-11-density-aware-master-model

## Objective

Extend the ADR-0.0.34 content-model substrate so a single `AgentContract` model can
hold the agent contract at MAX fidelity and be rendered at any density. Deliverables:

1. Extend `Bullet` with `classification`, `witness`, `rationale_ref`, `density_min`
2. Create `Pillar` model with `order`, `enabled`, `tier`; extend `AgentContract` to carry pillars
3. Add `reconcile_invariant(ConstitutionalInvariant) -> Bullet` in `invariants.py`
4. Update `constitutional_invariant.json` schema to mirror reconciled model
5. Update `__init__.py` exports
6. Write field-validation and round-trip tests (TDD RED → GREEN)

**Schema only — no renderer, no migration, no sync-wiring (those are OBPI-12/13/14).**

## Destination-in-mind (disclosure, gz-plan-audit Step 6a)

Before exploration I had already concluded: extend `Bullet`, create `Pillar`,
add `reconcile_invariant`. All three were specified literally in the ADR's Decision
Extension section. The plan is a direct forward-trace from that specification.

## Rejected alternatives (disclosure, gz-plan-audit Step 6a)

- **Parallel `DensityBullet` subclass** — rejected; ADR Decision Extension explicitly says
  "one spine, not two parallel ones." Subclassing produces a parallel substrate.
- **Adding `density_min` to `ConstitutionalInvariant` directly** — rejected; the invariant
  model is the registry input format, not the master content model. Mixing registry fields
  with rendering fields inverts the reconciliation direction.
- **`density_min` as a plain string** — rejected; a typed Literal enum makes invalid
  temperatures unrepresentable at construction, which is more Pydantic-idiomatic.

## Files

**Modified:**
- `src/gzkit/content/models/bullet.py` — add `classification`, `witness`, `rationale_ref`, `density_min` fields and `model_validator` enforcing Judgment floor
- `src/gzkit/content/models/agent_contract.py` — add `pillars: list[Pillar]` field; import Pillar; Pillar defined here per brief allowlist
- `src/gzkit/content/models/__init__.py` — export `Pillar`
- `src/gzkit/governance/invariants.py` — add `reconcile_invariant()` function
- `src/gzkit/schemas/constitutional_invariant.json` — add optional `classification` and `density_min` hint fields

**Modified (tests):**
- `tests/content/models/test_fields.py` — add `TestDensityBulletFields` and `TestPillarFields` classes
- `tests/content/test_round_trip_agent_contract.py` — add round-trip tests with new fields

## Steps

### Step 1 — Write failing tests for Bullet extension (RED)

**MODIFY** `tests/content/models/test_fields.py`

Add `TestDensityBulletFields` class with tests derived from REQ-0.0.37-11-01 and REQ-0.0.37-11-03:

```python
# REQ-0.0.37-11-01: Bullet accepts/validates classification, witness, rationale_ref, density_min
# REQ-0.0.37-11-03: Judgment bullet cannot express a density_min above "lite" (0-Kelvin floor)
class TestDensityBulletFields(unittest.TestCase):

    @covers("REQ-0.0.37-11-01")
    def test_bullet_accepts_classification_enum_values(self):
        # Each of the four valid classification values constructs without error
        for cls in ("Mechanical", "Promotable", "Judgment", "Ambiguous"):
            b = Bullet(text="x", classification=cls)
            self.assertEqual(b.classification, cls)

    @covers("REQ-0.0.37-11-01")
    def test_bullet_rejects_invalid_classification(self):
        # An invalid classification raises ValidationError at construction
        with self.assertRaises(ValidationError):
            Bullet(text="x", classification="Invalid")

    @covers("REQ-0.0.37-11-01")
    def test_bullet_accepts_witness_and_rationale_ref(self):
        b = Bullet(text="x", witness="gz validate --foo", rationale_ref="docs/foo.md")
        self.assertEqual(b.witness, "gz validate --foo")
        self.assertEqual(b.rationale_ref, "docs/foo.md")

    @covers("REQ-0.0.37-11-01")
    def test_bullet_accepts_none_fields(self):
        b = Bullet(text="x")
        self.assertIsNone(b.classification)
        self.assertIsNone(b.witness)
        self.assertIsNone(b.rationale_ref)
        self.assertIsNone(b.density_min)

    @covers("REQ-0.0.37-11-03")
    def test_judgment_bullet_density_min_is_lite(self):
        # A Judgment bullet constructed without explicit density_min gets "lite"
        b = Bullet(text="x", classification="Judgment")
        self.assertEqual(b.density_min, "lite")

    @covers("REQ-0.0.37-11-03")
    def test_judgment_bullet_cannot_have_density_min_above_lite(self):
        # A Judgment bullet with density_min="heavy" raises ValidationError
        with self.assertRaises(ValidationError):
            Bullet(text="x", classification="Judgment", density_min="heavy")

    @covers("REQ-0.0.37-11-01")
    def test_density_min_accepts_temperature_values(self):
        for temp in ("lite", "medium", "heavy"):
            b = Bullet(text="x", density_min=temp)
            self.assertEqual(b.density_min, temp)

    @covers("REQ-0.0.37-11-01")
    def test_density_min_rejects_invalid_temperature(self):
        with self.assertRaises(ValidationError):
            Bullet(text="x", density_min="ultra")
```

Run `uv run -m unittest tests.content.models.test_fields.TestDensityBulletFields -v`
and confirm each test fails (ImportError / AttributeError expected, confirming RED).

### Step 2 — Extend Bullet model (GREEN for Step 1 tests)

**MODIFY** `src/gzkit/content/models/bullet.py`

Add `classification`, `witness`, `rationale_ref`, `density_min` fields with a
`model_validator` that enforces the Judgment 0-Kelvin floor:

```python
from typing import Literal
from pydantic import Field, model_validator
from .base import BaseContentModel

_TEMPERATURE = Literal["lite", "medium", "heavy"]
_CLASSIFICATION = Literal["Mechanical", "Promotable", "Judgment", "Ambiguous"]

class Bullet(BaseContentModel):
    text: str
    indent: int = 0
    classification: _CLASSIFICATION | None = Field(None, description="...")
    witness: str | None = Field(None, description="...")
    rationale_ref: str | None = Field(None, description="...")
    density_min: _TEMPERATURE | None = Field(None, description="...")

    @model_validator(mode="after")
    def _enforce_judgment_floor(self) -> "Bullet":
        if self.classification == "Judgment":
            if self.density_min is None:
                # Auto-set to lite (the floor)
                object.__setattr__(self, "density_min", "lite")
            elif self.density_min != "lite":
                raise ValueError("Judgment bullets must have density_min='lite'")
        return self
```

Run `uv run -m unittest tests.content.models.test_fields.TestDensityBulletFields -v`
to confirm GREEN. Then run `uv run ruff check . --fix && uv run ruff format .`.

### Step 3 — Write failing tests for Pillar model (RED)

**MODIFY** `tests/content/models/test_fields.py`

Add `TestPillarFields` class with tests derived from REQ-0.0.37-11-02:

```python
# REQ-0.0.37-11-02: Pillar validates order, enabled, tier
class TestPillarFields(unittest.TestCase):

    @covers("REQ-0.0.37-11-02")
    def test_pillar_constructs_with_required_fields(self):
        p = Pillar(id="behavior-rules", title="Behavior Rules", order=1)
        self.assertEqual(p.order, 1)
        self.assertTrue(p.enabled)      # default True
        self.assertEqual(p.tier, "lite")  # default "lite"

    @covers("REQ-0.0.37-11-02")
    def test_pillar_enabled_false_honored(self):
        p = Pillar(id="x", title="X", order=1, enabled=False)
        self.assertFalse(p.enabled)

    @covers("REQ-0.0.37-11-02")
    def test_pillar_tier_heavy_accepted(self):
        p = Pillar(id="x", title="X", order=1, tier="heavy")
        self.assertEqual(p.tier, "heavy")

    @covers("REQ-0.0.37-11-02")
    def test_pillar_tier_rejects_invalid(self):
        with self.assertRaises(ValidationError):
            Pillar(id="x", title="X", order=1, tier="ultra")

    @covers("REQ-0.0.37-11-02")
    def test_pillar_bullets_field_accepts_list_of_bullets(self):
        p = Pillar(id="x", title="X", order=1,
                   bullets=[Bullet(text="rule one"), Bullet(text="rule two")])
        self.assertEqual(len(p.bullets), 2)

    @covers("REQ-0.0.37-11-02")
    def test_agent_contract_accepts_pillars(self):
        p = Pillar(id="x", title="X", order=1)
        ac = AgentContract(name="A", purpose="P", pillars=[p])
        self.assertEqual(len(ac.pillars), 1)
```

Run failing: `uv run -m unittest tests.content.models.test_fields.TestPillarFields -v`

### Step 4 — Create Pillar model + extend AgentContract (GREEN for Step 3 tests)

**MODIFY** `src/gzkit/content/models/agent_contract.py`

Add `Pillar` co-located (per brief allowlist, which does not include a separate pillar.py):

```python
from typing import Literal
from pydantic import Field
from .base import BaseContentModel
from .bullet import Bullet

_TEMPERATURE = Literal["lite", "medium", "heavy"]

class Pillar(BaseContentModel):
    id: str = Field(..., description="Unique section identifier (kebab-case)")
    title: str = Field(..., description="Display title")
    order: int = Field(..., description="Render order (ascending)")
    enabled: bool = Field(True, description="Whether the section renders")
    tier: _TEMPERATURE = Field("lite", description="Lowest temperature that renders this section")
    bullets: list[Bullet] = Field(default_factory=list, description="Bullets in this section")

class AgentContract(BaseContentModel):
    name: str
    purpose: str
    tech_stack: list[str] = Field(default_factory=list)
    rules: list[Bullet] = Field(default_factory=list)
    pillars: list[Pillar] = Field(default_factory=list)
```

**MODIFY** `src/gzkit/content/models/__init__.py` — add `Pillar` to imports and `__all__`.

Run `uv run -m unittest tests.content.models.test_fields.TestPillarFields -v` → GREEN.
Run `uv run ruff check . --fix && uv run ruff format .`.

### Step 5 — Write failing reconciliation + round-trip tests (RED)

**MODIFY** `tests/content/test_round_trip_agent_contract.py`

Add `TestReconcileInvariant` and `TestRoundTripDensityFields` derived from
REQ-0.0.37-11-04 and REQ-0.0.37-11-05:

```python
# REQ-0.0.37-11-04: reconcile_invariant maps claim->text, structural_witness->witness, foundation classification
class TestReconcileInvariant(unittest.TestCase):

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_maps_claim_to_text(self):
        inv = ConstitutionalInvariant(id="CIC-1", claim="Every claim...",
                                      structural_witness=["gz validate --foo"],
                                      composition_targets=["AGENTS.md"])
        bullet = reconcile_invariant(inv)
        self.assertEqual(bullet.text, "Every claim...")

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_maps_witness_first_structural_witness(self):
        inv = ConstitutionalInvariant(id="CIC-1", claim="x",
                                      structural_witness=["gz validate --a", "gz validate --b"],
                                      composition_targets=[])
        bullet = reconcile_invariant(inv)
        self.assertEqual(bullet.witness, "gz validate --a")

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_assigns_mechanical_classification(self):
        inv = ConstitutionalInvariant(id="CIC-1", claim="x",
                                      structural_witness=["gz validate --foo"],
                                      composition_targets=[])
        bullet = reconcile_invariant(inv)
        self.assertEqual(bullet.classification, "Mechanical")

    @covers("REQ-0.0.37-11-04")
    def test_reconcile_bullet_round_trips_through_model(self):
        inv = ConstitutionalInvariant(id="CIC-2", claim="Every OBPI brief...",
                                      structural_witness=["gz brief reconcile"],
                                      composition_targets=["AGENTS.md"])
        bullet = reconcile_invariant(inv)
        # Round-trip: model_dump -> re-construct -> equal
        dumped = bullet.model_dump()
        rebuilt = Bullet(**dumped)
        self.assertEqual(bullet, rebuilt)

# REQ-0.0.37-11-05 is SUPPORT kind — proof is ledger + validate --documents,
# not a @covers test. No test class needed for REQ-05.
```

Also add `TestRoundTripDensityFields` extending existing round-trip pattern:

```python
# REQ-0.0.37-11-05 (partial): round-trip fidelity for the extended model
class TestRoundTripDensityFields(unittest.TestCase):

    @covers("REQ-0.0.37-11-04")
    def test_round_trip_preserves_new_bullet_fields(self):
        model = AgentContract(
            name="Test", purpose="P",
            rules=[Bullet(text="Rule", classification="Mechanical",
                          witness="gz validate --foo", density_min="medium")],
            pillars=[Pillar(id="x", title="X", order=1, tier="heavy",
                            bullets=[Bullet(text="b")])]
        )
        rendered = render(model, "claude").decode("utf-8")
        parsed = parse(rendered, "AgentContract")
        self.assertEqual(parsed, model)
```

Run failing: `uv run -m unittest tests.content.test_round_trip_agent_contract.TestReconcileInvariant -v`

### Step 6 — Add reconcile_invariant + update schema (GREEN for Step 5 tests)

**MODIFY** `src/gzkit/governance/invariants.py`

Add `reconcile_invariant()` after the existing `load_invariants()`:

```python
from gzkit.content.models.bullet import Bullet

def reconcile_invariant(invariant: ConstitutionalInvariant) -> Bullet:
    """Map a ConstitutionalInvariant registry entry into a density-aware Bullet.

    Reconciliation contract (OBPI-0.0.37-11):
    - claim -> text
    - structural_witness[0] -> witness (first entry; witnesses the enforcement gate)
    - classification = "Mechanical" (constitutional invariants are mechanically enforced)
    - density_min = "lite" (invariants render at every temperature)
    - rationale_ref = None (pointers added at composition time by OBPI-12)
    """
    return Bullet(
        text=invariant.claim,
        witness=invariant.structural_witness[0],
        classification="Mechanical",
        density_min="lite",
    )
```

**MODIFY** `src/gzkit/schemas/constitutional_invariant.json`

Add optional `classification` and `density_min` hint fields so operators can
override defaults in the registry:

```json
"classification": {
  "type": "string",
  "enum": ["Mechanical", "Promotable", "Judgment", "Ambiguous"],
  "description": "Optional override for bullet classification (default: Mechanical)."
},
"density_min": {
  "type": "string",
  "enum": ["lite", "medium", "heavy"],
  "description": "Optional override for minimum render temperature (default: lite)."
}
```

Run `uv run -m unittest tests.content.test_round_trip_agent_contract -v` → GREEN.

### Step 7 — Full verification

```bash
uv run ruff check . --fix && uv run ruff format .
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz covers OBPI-0.0.37-11-density-aware-master-model --json
```

All checks must pass before advancing to Stage 3.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.content.models.test_fields -v
uv run -m unittest tests.content.test_round_trip_agent_contract -v
uv run gz covers OBPI-0.0.37-11-density-aware-master-model --json
```

## Notes

- REQ-0.0.37-11-05 is SUPPORT kind — proof is `gz validate --documents` passing after
  schema edit + the ledger `artifact_edited` event. No `@covers` test needed or correct.
- Existing round-trip tests in `test_round_trip_agent_contract.py` must continue to pass
  (backward compat: `pillars` defaults to `[]`, new `Bullet` fields default to `None`).
- `Pillar` is co-located in `agent_contract.py` per the brief's Allowed Paths (no
  separate `pillar.py` is in the allowlist).
- The `_TEMPERATURE` type alias is private to each module; once OBPI-12 (renderer) lands,
  a shared location can be extracted if needed.
