# OBPI-0.0.10-02: Identity Surfaces — Implementation Plan

## Recommendation: Approach B (Create all 5 fresh in core/models.py)

### Decision Rationale

After thorough codebase analysis, **Approach B** is the correct choice. Here is the detailed reasoning:

---

### Why NOT Approach A (Re-export existing + create missing 3)

1. **Schema mismatch is real and consequential.** The existing `ReqId` (triangle.py:25) and `TaskId` (tasks.py:26) store `semver` as a single string field (`"0.15.0"`). The identity surface contract defined in storage-tiers.md describes these IDs as *portable identifiers* — opaque strings that parse and reconstruct identically across tiers. The existing models serve a *decomposition* purpose (triangle linkage, task lifecycle) and expose internal structure (obpi_item, criterion_index, seq as separate fields). An identity surface model should hold the *complete raw identifier string* as its primary datum, with `parse()` as the constructor and `__str__()` as the round-trip. Re-exporting the existing models would conflate two distinct responsibilities: entity lifecycle decomposition vs. identity surface portability.

2. **ConfigDict divergence.** The frontmatter models in core/models.py use `extra="allow"` (they must tolerate unknown YAML keys). The identity surface models require `extra="forbid"` (strict identifier schemas). Importing ReqId/TaskId from triangle.py/tasks.py into core/models.py would mix models with different `extra` policies within the same module's conceptual layer. However, the existing ReqId/TaskId already use `extra="forbid"`, so this is actually consistent. This point is neutral.

3. **Coupling risk.** If the triangle or task modules evolve their ID models (e.g., adding fields for lifecycle tracking), the identity surface contract in core/models.py would silently change. Identity surfaces should be stable, minimal, and independently versioned.

4. **The brief is explicit:** "Pydantic models MUST exist in `core/models.py`" — not "must be importable from". The ADR's Non-Goals section states: "No identity model behavior. This ADR creates Pydantic models for all five identity surfaces... It does not add CLI commands, resolvers, or runtime behavior that consumes these models — that belongs to downstream ADRs." This is a contract definition, not a re-export.

### Why Approach B is correct

1. **Single responsibility.** The identity surface models in core/models.py define *what a valid ID looks like* — nothing more. They are the Pydantic equivalent of the table in storage-tiers.md, lines 120-127. The existing ReqId/TaskId in triangle.py/tasks.py continue to serve entity decomposition and lifecycle — a different concern.

2. **Uniform schema across all five surfaces.** All five models follow an identical pattern: `raw` string field, `surface` literal, regex-validated `raw` field, `parse()` classmethod, `__str__()` method. This uniformity is exactly what "portable across tiers" means.

3. **No breakage.** The existing `ReqId` in triangle.py and `TaskId` in tasks.py are not touched. All 20+ import sites continue working. The `@covers` decorator, drift engine, task lifecycle, CLI commands — all unaffected.

4. **The "two models" concern is a feature, not a bug.** `gzkit.triangle.ReqId` = entity decomposition model (fields: semver, obpi_item, criterion_index). `gzkit.core.models.ReqId` (or better: `ReqIdentity`) = identity surface model (field: raw string, validated by regex). They serve different layers. Downstream ADRs that need to *consume* identity surfaces will import from core/models.py. Existing code that needs to *decompose* REQ entities continues importing from triangle.py. This is standard layered architecture.

5. **Naming convention resolves ambiguity.** Use `AdrId`, `ObpiId`, `ReqId`, `TaskId`, `EvidenceId` as names in core/models.py. If the name collision with triangle.py's `ReqId` and tasks.py's `TaskId` is a concern, the alternative names `ReqIdentity`/`TaskIdentity` could be used — but since these live in different modules and the brief explicitly says models must be in core/models.py, the same names in different namespaces is Pythonic and standard. I recommend keeping the natural names (`ReqId`, `TaskId`, etc.) because: (a) they match the governance doc's identity surface table, (b) consumers will qualify imports when needed (`from gzkit.core.models import ReqId as CoreReqId`), and (c) the ADR's Non-Goals section makes clear these models are not consumed by current code — they are a contract definition for future tiers.

---

## Implementation Plan

### Step 0: Verify the ID patterns from governance docs

From `docs/governance/storage-tiers.md` lines 120-127:

| Surface | Pattern | Example |
|---------|---------|---------|
| ADR | `ADR-X.Y.Z` | `ADR-0.0.10` |
| OBPI | `OBPI-X.Y.Z-NN` | `OBPI-0.0.10-01` |
| REQ | `REQ-X.Y.Z-NN-MM` | `REQ-0.0.10-01-01` |
| TASK | `TASK-*` | `TASK-0.0.10-01-001` |
| Evidence | `EV-*` | `EV-0.0.10-01-001` |

**Important discrepancy noted:** The governance doc shows `TASK-0.0.10-01-001` (3 segments after semver), but the actual `TaskId` in tasks.py uses `TASK-0.20.0-01-01-01` (4 segments: obpi_item-req_index-seq). The governance doc's pattern uses `TASK-*` as a wildcard, suggesting the exact pattern was left intentionally open. The identity surface model should match the *actual implemented pattern* (`TASK-X.Y.Z-NN-MM-SS`), and the governance doc table should be updated to be precise.

Similarly, `EV-0.0.10-01-001` needs a definitive pattern. Based on the hierarchy (EV sits below OBPI, parallel to TASK), the likely pattern is `EV-X.Y.Z-NN-SSS` where NN is the OBPI item and SSS is a sequence number.

### Step 1: Create identity surface models in `src/gzkit/core/models.py`

Add five new model classes after the existing frontmatter models section but before `SCHEMA_TO_MODEL`. Each follows the identical pattern:

```python
# ---------------------------------------------------------------------------
# Identity surface models (ADR-0.0.10, OBPI-0.0.10-02)
# ---------------------------------------------------------------------------

class AdrId(BaseModel):
    """Portable ADR identity surface.

    Pattern: ``ADR-X.Y.Z``  Example: ``ADR-0.0.10``
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    raw: str = Field(..., pattern=r"^ADR-\d+\.\d+\.\d+$")

    @classmethod
    def parse(cls, value: str) -> AdrId:
        return cls(raw=value.strip())

    def __str__(self) -> str:
        return self.raw


class ObpiId(BaseModel):
    """Portable OBPI identity surface.

    Pattern: ``OBPI-X.Y.Z-NN``  Example: ``OBPI-0.0.10-01``
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    raw: str = Field(..., pattern=r"^OBPI-\d+\.\d+\.\d+-\d+$")

    @classmethod
    def parse(cls, value: str) -> ObpiId:
        return cls(raw=value.strip())

    def __str__(self) -> str:
        return self.raw


class ReqId(BaseModel):
    """Portable REQ identity surface.

    Pattern: ``REQ-X.Y.Z-NN-MM``  Example: ``REQ-0.0.10-01-01``
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    raw: str = Field(..., pattern=r"^REQ-\d+\.\d+\.\d+-\d+-\d+$")

    @classmethod
    def parse(cls, value: str) -> ReqId:
        return cls(raw=value.strip())

    def __str__(self) -> str:
        return self.raw


class TaskId(BaseModel):
    """Portable TASK identity surface.

    Pattern: ``TASK-X.Y.Z-NN-MM-SS``  Example: ``TASK-0.20.0-01-01-01``
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    raw: str = Field(..., pattern=r"^TASK-\d+\.\d+\.\d+-\d+-\d+-\d+$")

    @classmethod
    def parse(cls, value: str) -> TaskId:
        return cls(raw=value.strip())

    def __str__(self) -> str:
        return self.raw


class EvidenceId(BaseModel):
    """Portable Evidence identity surface.

    Pattern: ``EV-X.Y.Z-NN-SSS``  Example: ``EV-0.0.10-01-001``
    """
    model_config = ConfigDict(frozen=True, extra="forbid")
    raw: str = Field(..., pattern=r"^EV-\d+\.\d+\.\d+-\d+-\d+$")

    @classmethod
    def parse(cls, value: str) -> EvidenceId:
        return cls(raw=value.strip())

    def __str__(self) -> str:
        return self.raw
```

Add an `IDENTITY_MODELS` mapping after the models:

```python
IDENTITY_MODELS: dict[str, type[BaseModel]] = {
    "ADR": AdrId,
    "OBPI": ObpiId,
    "REQ": ReqId,
    "TASK": TaskId,
    "EV": EvidenceId,
}
```

**Placement:** Insert after line 114 (the `SCHEMA_TO_MODEL` dict) and before line 122 (`_literal_values`). This keeps identity models grouped together and separate from frontmatter models.

**Key design decisions:**
- Single `raw` field (the canonical string) rather than decomposed components. This is the *identity* model, not the *entity* model.
- `parse()` classmethod for consistency with existing ReqId/TaskId patterns.
- `__str__()` returns `raw` for round-trip fidelity.
- Regex on the `raw` field enforces format at construction time.
- `ConfigDict(frozen=True, extra="forbid")` per data model policy.

### Step 2: Create test file `tests/test_identity_surfaces.py`

The OBPI brief verification section explicitly names this file: `uv run -m unittest tests.test_identity_surfaces -v`

Test structure:

```
class TestAdrId(unittest.TestCase):
    - test_parse_valid: AdrId.parse("ADR-0.0.10") succeeds
    - test_str_roundtrip: str(AdrId.parse("ADR-0.0.10")) == "ADR-0.0.10"
    - test_frozen: assignment raises ValidationError
    - test_extra_forbid: extra kwarg raises ValidationError
    - test_invalid_prefix: "XDR-0.0.10" raises ValidationError
    - test_invalid_semver: "ADR-abc" raises ValidationError
    - test_strips_whitespace: "  ADR-0.0.10  " parses to "ADR-0.0.10"

class TestObpiId(unittest.TestCase):
    - test_parse_valid: ObpiId.parse("OBPI-0.0.10-01") succeeds
    - test_str_roundtrip
    - test_frozen
    - test_extra_forbid
    - test_invalid_prefix
    - test_strips_whitespace

class TestReqIdSurface(unittest.TestCase):
    - test_parse_valid: ReqId.parse("REQ-0.0.10-01-01") succeeds
    - test_str_roundtrip
    - test_frozen
    - test_extra_forbid
    - test_invalid_format
    - test_strips_whitespace

class TestTaskIdSurface(unittest.TestCase):
    - test_parse_valid: TaskId.parse("TASK-0.20.0-01-01-01") succeeds
    - test_str_roundtrip
    - test_frozen
    - test_extra_forbid
    - test_invalid_format
    - test_strips_whitespace

class TestEvidenceId(unittest.TestCase):
    - test_parse_valid: EvidenceId.parse("EV-0.0.10-01-001") succeeds
    - test_str_roundtrip
    - test_frozen
    - test_extra_forbid
    - test_invalid_prefix
    - test_strips_whitespace

class TestIdentityModelsMapping(unittest.TestCase):
    - test_all_five_surfaces_present: len(IDENTITY_MODELS) == 5
    - test_mapping_keys: set(IDENTITY_MODELS.keys()) == {"ADR", "OBPI", "REQ", "TASK", "EV"}

class TestTierPortability(unittest.TestCase):
    """Verify same ID string parses identically regardless of construction path."""
    - test_adr_portability: same string -> same model -> same str, multiple examples
    - test_obpi_portability
    - test_req_portability
    - test_task_portability
    - test_evidence_portability
    - test_all_surfaces_roundtrip_from_table: for each (surface, example) from governance doc table, parse and verify round-trip
```

Imports:
```python
from gzkit.core.models import (
    AdrId, ObpiId, ReqId, TaskId, EvidenceId, IDENTITY_MODELS,
)
```

Note: These tests import `ReqId` and `TaskId` from `gzkit.core.models`, NOT from `gzkit.triangle` or `gzkit.tasks`. This is correct — we are testing the identity surface models, not the entity models.

Use `@covers` decorators for REQ-0.0.10-02-01, REQ-0.0.10-02-02, REQ-0.0.10-02-03 from the brief's acceptance criteria.

### Step 3: Update governance docs

**File: `docs/governance/storage-tiers.md`**

Update the Identity Surfaces table (lines 120-127) to have precise patterns instead of wildcards:

| Surface | Pattern | Example |
|---------|---------|---------|
| ADR | `ADR-X.Y.Z` | `ADR-0.0.10` |
| OBPI | `OBPI-X.Y.Z-NN` | `OBPI-0.0.10-01` |
| REQ | `REQ-X.Y.Z-NN-MM` | `REQ-0.0.10-01-01` |
| TASK | `TASK-X.Y.Z-NN-MM-SS` | `TASK-0.0.10-01-01-01` |
| Evidence | `EV-X.Y.Z-NN-SSS` | `EV-0.0.10-01-001` |

Replace the `TASK-*` and `EV-*` wildcards with explicit patterns.

Add a new section after the table (before "Anti-Patterns") documenting the Pydantic model contract:

```markdown
### Identity Surface Models

Each surface has a corresponding Pydantic model in `src/gzkit/core/models.py`:

| Surface | Model | ConfigDict |
|---------|-------|------------|
| ADR | `AdrId` | `frozen=True, extra="forbid"` |
| OBPI | `ObpiId` | `frozen=True, extra="forbid"` |
| REQ | `ReqId` | `frozen=True, extra="forbid"` |
| TASK | `TaskId` | `frozen=True, extra="forbid"` |
| Evidence | `EvidenceId` | `frozen=True, extra="forbid"` |

All models provide `parse(raw: str)` and `__str__()` for lossless round-trip.
These are identity-only models. Entity decomposition (e.g., extracting semver
components) belongs to domain-specific models in `triangle.py` and `tasks.py`.
```

### Step 4: Verify no breakage

Run the full test suite to confirm:
- Existing `ReqId`/`TaskId` imports from `triangle.py`/`tasks.py` still work
- New identity surface tests pass
- No naming collision at import time (different modules, different namespaces)

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest -q
uv run -m unittest tests.test_identity_surfaces -v
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Name collision: `ReqId` in both `core/models.py` and `triangle.py` | Different modules, different namespaces. No file imports both. The ADR Non-Goals section explicitly states these models have no runtime consumers yet. |
| EV-* pattern not yet used anywhere in code | The governance doc defines `EV-0.0.10-01-001`. The model validates this format. Downstream ADRs will consume it. |
| TASK pattern discrepancy in governance doc | Update the doc to match the implemented 4-segment pattern. |
| Future code mistakenly imports identity ReqId where entity ReqId is needed | Module docstrings and class docstrings clearly distinguish identity surface models from entity decomposition models. |

## Sequencing

1. Write tests first (TDD gate requirement): `tests/test_identity_surfaces.py`
2. Add models to `src/gzkit/core/models.py`
3. Update `docs/governance/storage-tiers.md`
4. Run verification suite
5. Record evidence in OBPI brief

## Files Changed

| File | Action | Nature |
|------|--------|--------|
| `src/gzkit/core/models.py` | Modified | Add 5 identity models + IDENTITY_MODELS mapping |
| `tests/test_identity_surfaces.py` | Created | Test all 5 surfaces + portability + mapping |
| `docs/governance/storage-tiers.md` | Modified | Precise patterns, model contract section |

## Files NOT Changed

| File | Reason |
|------|--------|
| `src/gzkit/triangle.py` | Existing ReqId stays untouched — different concern |
| `src/gzkit/tasks.py` | Existing TaskId stays untouched — different concern |
| `src/gzkit/traceability.py` | Continues importing from triangle.py as before |
| `src/gzkit/commands/*` | Denied path per brief |
| `.gzkit/*` | Denied path per brief |
