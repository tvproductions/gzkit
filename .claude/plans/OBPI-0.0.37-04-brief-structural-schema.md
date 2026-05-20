# OBPI-0.0.37-04-brief-structural-schema: Implementation Plan

**OBPI:** OBPI-0.0.37-04-brief-structural-schema
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy
**Kind:** Foundation

## Destination-in-mind (Plan-Before-Exploration disclosure)

Before exploration, the approach was clear: a standalone Pydantic `BriefStructure`
model + JSON Schema mirror + `parse_brief()` loader with permissive/strict mode.
No rejected alternative at the architecture level — the brief's scope is precise.

## Rejected Alternatives

1. **Extend trust_audits/briefs.py** — rejected because `brief_structure.py` is
   a new model/parser surface (Layer 1 schema), not a trust audit (Layer 2 validation).
   The two modules serve different abstraction levels; commingling them would couple
   schema definition to audit logic.
2. **Stdlib `dataclass` for LegacyBriefShape** — rejected per `.gzkit/rules/models.md`:
   "no stdlib `dataclasses`" for governance data. LegacyBriefShape is a Pydantic
   BaseModel (non-frozen, no `extra="forbid"` needed since it's a legacy container).
3. **Parse structured fields from markdown body sections** — rejected because
   `parse_brief` must be deterministic and mechanical. YAML frontmatter is the
   machine-readable surface; markdown section bodies are prose. Extracting
   structured data from prose requires heuristics that will drift.

## Context (gathered)

- `pyyaml>=6.0.3`, `jsonschema>=4.26`, `pydantic>=2.13.3` are all in `pyproject.toml`
- `src/gzkit/governance/briefs.py` does NOT exist — `brief_structure.py` is standalone
- `src/gzkit/governance/trust_audits/briefs.py` exists but is trust-audit scope (different layer)
- `features/constitutional_invariants.feature` EXISTS (created by OBPI-02)
- OBPI-01, 02, 03 all `Completed`
- `src/gzkit/schemas/obpi.json` EXISTS (companion schema; same package convention)
- Pydantic conventions: `BaseModel`, `ConfigDict(frozen=True, extra="forbid")`, Field(...)
- Test pattern: `unittest.TestCase` + `@covers("REQ-X.Y.Z-NN-MM")` decorator

## Files

### New
- `src/gzkit/governance/brief_structure.py`
- `src/gzkit/schemas/obpi_brief_structure.json`
- `tests/governance/test_brief_structure.py`
- `tests/fixtures/brief_structure/compliant.md`
- `tests/fixtures/brief_structure/legacy.md`
- `tests/fixtures/brief_structure/malformed.md`

### Modified
- `features/constitutional_invariants.feature` — add `@REQ-0.0.37-04-*` scenarios
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-04-brief-structural-schema.md` — add structured YAML frontmatter fields for REQ-05

## Steps

### Step 1: Write failing tests + create fixtures (TDD — RED)

**1a. Create `tests/fixtures/brief_structure/` directory and three brief files:**

`compliant.md` — YAML frontmatter includes all structured fields as typed arrays:
```yaml
---
id: OBPI-0.0.1-01-test-fixture
parent: ADR-0.0.1-test-fixture
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/brief_structure.py
reqs:
  - REQ-0.0.1-01-01
verification:
  - uv run gz lint
citations: []
---
# Test Compliant Brief
A fixture brief with all structured fields.
```

`legacy.md` — only standard frontmatter, no structured fields (triggers LegacyBriefShape):
```yaml
---
id: OBPI-0.0.2-02-test-legacy
parent: ADR-0.0.2-test-legacy
lane: Heavy
status: Draft
---
# Test Legacy Brief
## Allowed Paths
- src/gzkit/some_file.py

## Requirements (FAIL-CLOSED)
1. REQUIREMENT: Some requirement text
```

`malformed.md` — has structured fields but with invalid values (empty reqs for strict-mode test):
```yaml
---
id: OBPI-0.0.3-03-test-malformed
parent: ADR-0.0.3-test-malformed
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/some_file.py
reqs: []
verification:
  - uv run gz lint
citations: []
---
# Test Malformed Brief
```

**1b. Create `tests/governance/test_brief_structure.py`:**

```python
"""Tests for BriefStructure model and parse_brief loader (OBPI-0.0.37-04).

REQ-derived assertions for:
  REQ-0.0.37-04-01: frozen Pydantic BriefStructure model with all named fields
  REQ-0.0.37-04-02: JSON Schema mirror with additionalProperties: false
  REQ-0.0.37-04-03: parse_brief permissive mode → BriefStructure or LegacyBriefShape+warning
  REQ-0.0.37-04-04: parse_brief strict=True → ValueError on legacy brief
  REQ-0.0.37-04-05: round-trip parse of OBPI-0.0.37-04 brief → BriefStructure, no warning
"""

from __future__ import annotations

import json
import warnings
import unittest
from pathlib import Path

import jsonschema
from pydantic import ValidationError

from gzkit.governance.brief_structure import BriefStructure, LegacyBriefShape, parse_brief
from gzkit.traceability import covers

FIXTURES = Path(__file__).parent.parent / "fixtures" / "brief_structure"
SCHEMA_PATH = Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "obpi_brief_structure.json"
THIS_BRIEF = Path(__file__).parent.parent.parent / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.37-constitutional-invariant-composition" / "obpis" / "OBPI-0.0.37-04-brief-structural-schema.md"


class TestBriefStructureModel(unittest.TestCase):
    """REQ-0.0.37-04-01: frozen model with all named fields."""

    @covers("REQ-0.0.37-04-01")
    def test_model_is_frozen(self):
        b = BriefStructure(
            id="OBPI-0.0.37-04-brief-structural-schema",
            parent="ADR-0.0.37-constitutional-invariant-composition",
            lane="Heavy",
            status="Draft",
            allowlist=["src/x.py"],
            reqs=["REQ-0.0.37-04-01"],
            verification=["uv run gz lint"],
            citations=[],
        )
        with self.assertRaises((ValueError, TypeError)):
            b.id = "MUTATED"  # type: ignore

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_allowlist(self):
        with self.assertRaises(ValidationError):
            BriefStructure(
                id="OBPI-0.0.37-04-brief-structural-schema",
                parent="ADR-0.0.37-constitutional-invariant-composition",
                lane="Heavy", status="Draft",
                allowlist=[],
                reqs=["REQ-0.0.37-04-01"],
                verification=["uv run gz lint"],
                citations=[],
            )

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_reqs(self):
        with self.assertRaises(ValidationError):
            BriefStructure(
                id="OBPI-0.0.37-04-brief-structural-schema",
                parent="ADR-0.0.37-constitutional-invariant-composition",
                lane="Heavy", status="Draft",
                allowlist=["src/x.py"],
                reqs=[],
                verification=["uv run gz lint"],
                citations=[],
            )

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_verification(self):
        with self.assertRaises(ValidationError):
            BriefStructure(
                id="OBPI-0.0.37-04-brief-structural-schema",
                parent="ADR-0.0.37-constitutional-invariant-composition",
                lane="Heavy", status="Draft",
                allowlist=["src/x.py"],
                reqs=["REQ-0.0.37-04-01"],
                verification=[],
                citations=[],
            )

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_extra_fields(self):
        with self.assertRaises(ValidationError):
            BriefStructure(
                id="OBPI-0.0.37-04-brief-structural-schema",
                parent="ADR-0.0.37-constitutional-invariant-composition",
                lane="Heavy", status="Draft",
                allowlist=["src/x.py"],
                reqs=["REQ-0.0.37-04-01"],
                verification=["uv run gz lint"],
                citations=[],
                unexpected_field="bad",  # type: ignore
            )

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_invalid_id(self):
        with self.assertRaises(ValidationError):
            BriefStructure(
                id="not-a-valid-id",
                parent="ADR-0.0.37-constitutional-invariant-composition",
                lane="Heavy", status="Draft",
                allowlist=["src/x.py"],
                reqs=["REQ-0.0.37-04-01"],
                verification=["uv run gz lint"],
                citations=[],
            )

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_invalid_req_format(self):
        with self.assertRaises(ValidationError):
            BriefStructure(
                id="OBPI-0.0.37-04-brief-structural-schema",
                parent="ADR-0.0.37-constitutional-invariant-composition",
                lane="Heavy", status="Draft",
                allowlist=["src/x.py"],
                reqs=["bad-req-format"],
                verification=["uv run gz lint"],
                citations=[],
            )


class TestBriefStructureJsonSchema(unittest.TestCase):
    """REQ-0.0.37-04-02: JSON Schema mirror."""

    def _load_schema(self):
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    @covers("REQ-0.0.37-04-02")
    def test_schema_has_additional_properties_false(self):
        schema = self._load_schema()
        self.assertIs(schema.get("additionalProperties"), False)

    @covers("REQ-0.0.37-04-02")
    def test_schema_validates_compliant_fixture(self):
        schema = self._load_schema()
        instance = {
            "id": "OBPI-0.0.1-01-test-fixture",
            "parent": "ADR-0.0.1-test-fixture",
            "lane": "Heavy",
            "status": "Draft",
            "allowlist": ["src/x.py"],
            "reqs": ["REQ-0.0.1-01-01"],
            "verification": ["uv run gz lint"],
            "citations": [],
        }
        jsonschema.validate(instance, schema)  # must not raise

    @covers("REQ-0.0.37-04-02")
    def test_schema_rejects_missing_reqs(self):
        schema = self._load_schema()
        instance = {
            "id": "OBPI-0.0.1-01-test-fixture",
            "parent": "ADR-0.0.1-test-fixture",
            "lane": "Heavy",
            "status": "Draft",
            "allowlist": ["src/x.py"],
            "verification": ["uv run gz lint"],
            "citations": [],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


class TestParseBriefPermissive(unittest.TestCase):
    """REQ-0.0.37-04-03: permissive mode behavior."""

    @covers("REQ-0.0.37-04-03")
    def test_compliant_brief_returns_brief_structure(self):
        result = parse_brief(FIXTURES / "compliant.md")
        self.assertIsInstance(result, BriefStructure)

    @covers("REQ-0.0.37-04-03")
    def test_compliant_brief_no_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(FIXTURES / "compliant.md")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertEqual(deprecations, [])

    @covers("REQ-0.0.37-04-03")
    def test_legacy_brief_returns_legacy_shape(self):
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = parse_brief(FIXTURES / "legacy.md")
        self.assertIsInstance(result, LegacyBriefShape)

    @covers("REQ-0.0.37-04-03")
    def test_legacy_brief_emits_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(FIXTURES / "legacy.md")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertGreater(len(deprecations), 0)


class TestParseBriefStrict(unittest.TestCase):
    """REQ-0.0.37-04-04: strict=True raises ValueError on legacy brief."""

    @covers("REQ-0.0.37-04-04")
    def test_strict_raises_on_legacy_brief(self):
        with self.assertRaises(ValueError):
            parse_brief(FIXTURES / "legacy.md", strict=True)

    @covers("REQ-0.0.37-04-04")
    def test_strict_succeeds_on_compliant_brief(self):
        result = parse_brief(FIXTURES / "compliant.md", strict=True)
        self.assertIsInstance(result, BriefStructure)


class TestParseBriefRoundTrip(unittest.TestCase):
    """REQ-0.0.37-04-05: round-trip on OBPI-0.0.37-04 brief itself."""

    @covers("REQ-0.0.37-04-05")
    def test_this_brief_parses_as_brief_structure(self):
        result = parse_brief(THIS_BRIEF)
        self.assertIsInstance(result, BriefStructure)

    @covers("REQ-0.0.37-04-05")
    def test_this_brief_no_deprecation_warning(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(THIS_BRIEF)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertEqual(deprecations, [])


if __name__ == "__main__":
    unittest.main()
```

### Step 2: Implement `src/gzkit/governance/brief_structure.py`

Models policy: `BaseModel`, `ConfigDict(frozen=True, extra="forbid")`, no dataclasses.
`LegacyBriefShape` is a non-frozen BaseModel (legacy container, no validation intent).

```python
"""OBPI brief structural schema — BriefStructure Pydantic model and parser.

Introduces the machine-readable schema for OBPI briefs (OBPI-0.0.37-04).
Ships in permissive mode: briefs lacking structured frontmatter fields load
as LegacyBriefShape with a DeprecationWarning rather than raising.
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

_OBPI_ID_RE = re.compile(r"^OBPI-\d+\.\d+\.\d+-\d{2}(-[a-z0-9-]+)?$")
_ADR_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+-[a-z0-9-]+$")
_REQ_ID_RE = re.compile(r"^REQ-\d+\.\d+\.\d+-\d{2}-\d{2}$")


class LegacyBriefShape(BaseModel):
    """Container for an OBPI brief that lacks structured frontmatter fields."""
    model_config = ConfigDict(extra="forbid")

    path: Path
    raw_frontmatter: dict
    raw_body: str


class BriefStructure(BaseModel):
    """Machine-readable OBPI brief schema (OBPI-0.0.37-04)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="OBPI identifier matching OBPI-X.Y.Z-NN pattern")
    parent: str = Field(..., description="Parent ADR identifier matching ADR-X.Y.Z-slug pattern")
    lane: Literal["Lite", "Heavy"] = Field(..., description="Execution lane")
    status: Literal["Draft", "Validated", "Completed"] = Field(..., description="Brief lifecycle status")
    allowlist: list[str] = Field(..., min_length=1, description="Allowed paths for this OBPI")
    reqs: list[str] = Field(..., min_length=1, description="REQ-ID array (each matches REQ-X.Y.Z-NN-MM)")
    verification: list[str] = Field(..., min_length=1, description="Verification commands")
    citations: list[tuple[str, str]] = Field(default_factory=list, description="Citation tuples (artifact_path, anchor)")

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not _OBPI_ID_RE.match(v):
            raise ValueError(f"id must match OBPI-X.Y.Z-NN[-slug] pattern: {v!r}")
        return v

    @field_validator("parent")
    @classmethod
    def _validate_parent(cls, v: str) -> str:
        if not _ADR_ID_RE.match(v):
            raise ValueError(f"parent must match ADR-X.Y.Z-slug pattern: {v!r}")
        return v

    @field_validator("reqs", mode="before")
    @classmethod
    def _validate_reqs(cls, v: list) -> list:
        for req in v:
            if not _REQ_ID_RE.match(str(req)):
                raise ValueError(f"req must match REQ-X.Y.Z-NN-MM pattern: {req!r}")
        return v


def _extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a markdown file string."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5:]
    return fm, body


def parse_brief(
    path: Path, *, strict: bool = False
) -> BriefStructure | LegacyBriefShape:
    """Parse an OBPI brief file into BriefStructure or LegacyBriefShape.

    In permissive mode (default), briefs lacking structured frontmatter fields
    (allowlist, reqs, verification) are returned as LegacyBriefShape with a
    DeprecationWarning. In strict mode, missing or invalid structured fields
    raise ValueError.
    """
    text = path.read_text(encoding="utf-8")
    fm, body = _extract_frontmatter(text)

    required = {"allowlist", "reqs", "verification"}
    if not required.issubset(fm.keys()):
        if strict:
            missing = required - fm.keys()
            raise ValueError(
                f"Brief {path.name!r} missing structured frontmatter fields: "
                f"{sorted(missing)}. "
                "Set strict=False to load as LegacyBriefShape."
            )
        warnings.warn(
            f"Brief {path.name!r} lacks structured frontmatter fields "
            f"(allowlist, reqs, verification); loading as LegacyBriefShape. "
            "Migrate to structured frontmatter per OBPI-0.0.37-04.",
            DeprecationWarning,
            stacklevel=2,
        )
        return LegacyBriefShape(path=path, raw_frontmatter=fm, raw_body=body)

    return BriefStructure(**fm)
```

### Step 3: Create `src/gzkit/schemas/obpi_brief_structure.json`

JSON Schema mirror of BriefStructure. Pattern reference: existing `obpi.json` shape.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "gzkit.obpi_brief_structure.v1",
  "title": "gzkit OBPI Brief Structure Schema",
  "description": "Machine-readable structured fields for OBPI briefs (OBPI-0.0.37-04). Mirrors BriefStructure Pydantic model. Permissive-mode: briefs without these fields load as LegacyBriefShape.",
  "type": "object",
  "additionalProperties": false,
  "required": ["id", "parent", "lane", "status", "allowlist", "reqs", "verification", "citations"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^OBPI-\\d+\\.\\d+\\.\\d+-\\d{2}(-[a-z0-9-]+)?$",
      "description": "OBPI identifier"
    },
    "parent": {
      "type": "string",
      "pattern": "^ADR-\\d+\\.\\d+\\.\\d+-[a-z0-9-]+$",
      "description": "Parent ADR identifier"
    },
    "lane": {
      "type": "string",
      "enum": ["Lite", "Heavy"],
      "description": "Execution lane"
    },
    "status": {
      "type": "string",
      "enum": ["Draft", "Validated", "Completed"],
      "description": "Brief lifecycle status"
    },
    "allowlist": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "Allowed paths for this OBPI"
    },
    "reqs": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^REQ-\\d+\\.\\d+\\.\\d+-\\d{2}-\\d{2}$"
      },
      "minItems": 1,
      "description": "REQ-ID array"
    },
    "verification": {
      "type": "array",
      "items": {"type": "string"},
      "minItems": 1,
      "description": "Verification commands"
    },
    "citations": {
      "type": "array",
      "items": {
        "type": "array",
        "prefixItems": [{"type": "string"}, {"type": "string"}],
        "minItems": 2,
        "maxItems": 2
      },
      "description": "Citation tuples (artifact_path, anchor)"
    }
  }
}
```

### Step 4: Run tests (RED → GREEN verification)

After creating fixtures and test file (Step 1), run:
```bash
uv run -m unittest tests.governance.test_brief_structure -v
```
Expect: ImportError (module not yet created). Then implement Steps 2+3, re-run, expect: PASS.

### Step 5: Update OBPI-0.0.37-04.md frontmatter for REQ-05

Add structured YAML frontmatter fields to this brief's frontmatter block:
```yaml
allowlist:
  - src/gzkit/governance/brief_structure.py
  - src/gzkit/schemas/obpi_brief_structure.json
  - tests/governance/test_brief_structure.py
  - tests/fixtures/brief_structure/
  - features/constitutional_invariants.feature
  - docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-04-brief-structural-schema.md
reqs:
  - REQ-0.0.37-04-01
  - REQ-0.0.37-04-02
  - REQ-0.0.37-04-03
  - REQ-0.0.37-04-04
  - REQ-0.0.37-04-05
verification:
  - uv run gz lint
  - uv run gz typecheck
  - uv run -m unittest tests.governance.test_brief_structure -v
  - uv run mkdocs build --strict
citations: []
```

After this edit, `test_this_brief_parses_as_brief_structure` must pass.

### Step 6: Add BDD scenarios to features/constitutional_invariants.feature

Add 5 scenarios tagged `@REQ-0.0.37-04-01` through `@REQ-0.0.37-04-05`:

```gherkin
  @REQ-0.0.37-04-01
  Scenario: BriefStructure model is frozen and rejects empty fields
    Given a compliant OBPI brief fixture
    When I construct a BriefStructure with valid fields
    Then the model is frozen and rejects mutation
    And empty allowlist raises ValidationError
    And empty reqs raises ValidationError

  @REQ-0.0.37-04-02
  Scenario: JSON Schema mirror has additionalProperties false
    Given the obpi_brief_structure.json schema is loaded
    When I validate a compliant brief instance
    Then the schema validates without error
    And the schema rejects an instance missing reqs

  @REQ-0.0.37-04-03
  Scenario: parse_brief returns LegacyBriefShape for legacy brief with warning
    Given a legacy OBPI brief without structured frontmatter fields
    When I call parse_brief in permissive mode
    Then I receive a LegacyBriefShape instance
    And a DeprecationWarning is emitted

  @REQ-0.0.37-04-04
  Scenario: parse_brief strict mode raises ValueError for legacy brief
    Given a legacy OBPI brief without structured frontmatter fields
    When I call parse_brief with strict=True
    Then a ValueError is raised

  @REQ-0.0.37-04-05
  Scenario: This OBPI brief round-trips as BriefStructure
    Given the OBPI-0.0.37-04 brief file
    When I call parse_brief on it
    Then I receive a BriefStructure instance
    And no DeprecationWarning is emitted
```

### Step 7: Run lint + typecheck + full test suite

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_brief_structure -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers OBPI-0.0.37-04-brief-structural-schema --json
```

## Verification

Per the brief:
```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_brief_structure -v
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature --tags=REQ-0.0.37-04
```

## Notes

- `citations` field: allowed to be empty list (no `min_length` constraint unlike allowlist/reqs/verification)
- LegacyBriefShape uses `ConfigDict(extra="forbid")` but NOT `frozen=True` — legacy container holds runtime data
- `_extract_frontmatter` must handle missing `---` terminators gracefully
- The `malformed.md` fixture has empty `reqs: []` which will fail Pydantic validation in strict mode
- Scope collisions with ADR-0.0.42 / ADR-0.0.11 are ADVISORY — proceed; these are sibling OBPIs that haven't landed
- Heavy lane + Foundation kind = Full gate set (Gate 1-5)
