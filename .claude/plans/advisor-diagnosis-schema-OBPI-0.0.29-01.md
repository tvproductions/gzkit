# Plan: OBPI-0.0.29-01-advisor-diagnosis-schema

**OBPI:** OBPI-0.0.29-01-advisor-diagnosis-schema
**Parent ADR:** ADR-0.0.29 (foundation, heavy lane)
**Objective:** Author the frozen Pydantic data contract for the complexity advisor — `RefactorArchetype` (StrEnum, ten canonical values), `DoctrinalFrame` (four-authority enum + citation + excerpt), `ProofRange` (file path + line range + AST node kind), `IntrinsicAttestationRef` (forward stub for OBPI-07), and `AdvisorDiagnosis` (the top-level diagnosis container with non-empty `proof` tuple) — at `src/gzkit/complexity/advisor/diagnosis.py`, mirrored by a JSON Schema at `src/gzkit/schemas/advisor_diagnosis.json`. This is the data contract every downstream OBPI in ADR-0.0.29 binds against (engine OBPI-02, CLI OBPI-03, proof binding OBPI-08, intrinsic attestation OBPI-07) and that ADR-0.0.30 authoring-guidance consumes for refactor recommendations.

## Files (creates these files)

This OBPI is net-new package authoring; every file below is created by this plan:

- **CREATE** `src/gzkit/complexity/advisor/__init__.py` — new package marker; re-exports `AdvisorDiagnosis`, `RefactorArchetype`, `DoctrinalFrame`, `ProofRange`, `IntrinsicAttestationRef` for downstream consumers (engine OBPI-02, CLI OBPI-03).
- **CREATE** `src/gzkit/complexity/advisor/diagnosis.py` — the five frozen Pydantic models + `RefactorArchetype` StrEnum.
- **CREATE** `src/gzkit/schemas/advisor_diagnosis.json` — JSON Schema mirror with `additionalProperties: false`, enum constraints on `archetype` / `crossing_band` / `authority`, and `minItems: 1` on `proof`.
- **CREATE** `tests/complexity/advisor/test_diagnosis.py` — unittest module with one `@covers(REQ-0.0.29-01-NN)`-decorated test per requirement; uses `tempfile`-backed fixtures where applicable; loads the JSON Schema via `json.loads(Path(...).read_text(encoding="utf-8"))` and validates with `jsonschema.Draft202012Validator`.
- **MODIFY** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-01-advisor-diagnosis-schema.md` — evidence section only at completion (Stage 5 closure-narrative).

## Allowed Files

Same set as Files above. Allowed paths exactly match the brief allowlist (line 28-33):

- `src/gzkit/complexity/advisor/__init__.py`
- `src/gzkit/complexity/advisor/diagnosis.py`
- `src/gzkit/schemas/advisor_diagnosis.json`
- `tests/complexity/advisor/test_diagnosis.py`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-01-advisor-diagnosis-schema.md` (evidence section only)

## Context

### Source-of-truth artifacts read

- **ADR-0.0.29 § Decision rationale #1, #2, #5** — schema field shapes, four-authority canon (Fowler / Martin / Page-Jones / Constantine), proof-binding rationale.
- **ADR-0.0.29 § OBPI-0.0.29-01 paragraph (line 70)** — initial ten-archetype enumeration: `long-parameter-list, arrowhead, switch-on-type, feature-envy, large-class, divergent-change, shotgun-surgery, primitive-obsession, data-clumps, message-chain`.
- **ADR-0.0.29 § Mechanical surfaces (lines 52-67)** — confirms the file paths at `src/gzkit/complexity/advisor/diagnosis.py` and `src/gzkit/schemas/advisor_diagnosis.json`.
- **OBPI-0.0.29-01 brief — Requirements 1-10** — full FAIL-CLOSED requirement set; field shapes; tests required per REQ.
- **OBPI-0.0.29-07 brief** — confirms `IntrinsicAttestationRef` is a forward stub with `attestation_id: str`; full implementation lands at OBPI-07.
- **`.claude/rules/models.md`** — Pydantic immutable pattern: `ConfigDict(frozen=True, extra="forbid")`; `Field(...)` with description; `str | None` over `Optional[str]`.
- **`.claude/rules/pythonic.md`** — function ≤ 50 lines, module ≤ 600 lines; top-level imports only; explicit exceptions; type-check suppression syntax (bare `# type: ignore` or `# ty: ignore[<code>]`, never mypy-style `# type: ignore[<code>]`).
- **`.claude/rules/cross-platform.md`** — `pathlib.Path`; `encoding="utf-8"` on every read; no hard-coded separators.
- **`AGENTS.md` § STDLIB-FIRST DOCTRINE** — pydantic is named departure (validation semantics genuinely cannot be supplied by stdlib); `jsonschema` is already a runtime dep used elsewhere in `src/gzkit/`.
- **Sibling precedent: `src/gzkit/complexity/citation.py` + `src/gzkit/schemas/complexity_citation.json`** — identical pattern (frozen Pydantic + JSON Schema mirror with `additionalProperties: false`); used as structural template.

### Cluster citation context (referenced, not authored here)

`AdvisorDiagnosis` does **not** carry a `Citation` field at this OBPI — citation binding is the engine's responsibility (OBPI-02). The schema is the diagnosis container; the engine is what loads `Citation` from the distilled-characteristics document and embeds doctrinal-frame text. This OBPI's `DoctrinalFrame.citation: str` field carries a free-form string the engine populates; structural citation parsing remains in `src/gzkit/complexity/citation.py`. Confirmed against ADR-0.0.29 § Decision rationale #1 (advisor consumes ThresholdTable + reads distilled-characteristics — both engine-layer concerns).

### Schema constraints (binding from brief)

- `RefactorArchetype` — `StrEnum` with exactly the ten canonical values (snake_case, matching the brief's REQ-1 list verbatim).
- `DoctrinalFrame` — frozen `BaseModel`, `extra="forbid"`. Fields: `authority: Literal["fowler", "martin", "page_jones", "constantine"]`, `citation: str`, `excerpt: str`.
- `ProofRange` — frozen. Fields: `file_path: str` (relative), `start_line: int` (≥ 1), `end_line: int` (≥ `start_line`); cross-field validation via `@model_validator(mode="after")`.
- `IntrinsicAttestationRef` — frozen forward stub. Single field `attestation_id: str`. Forward-references OBPI-07's full implementation.
- `AdvisorDiagnosis` — frozen. Fields: `metric: str`, `crossing_band: Literal["block", "warn", "advise"]`, `crossing_value: float`, `archetype: RefactorArchetype`, `doctrinal_frame: DoctrinalFrame`, `proof: tuple[ProofRange, ...]` (non-empty — enforced by `min_length=1` on `Field` AND a `@model_validator(mode="after")` raising `ValueError` if empty), `recommended_move: str`, `intrinsic_attestation: IntrinsicAttestationRef | None = None`.

### JSON Schema mirror constraints (binding from REQ-5)

- `$schema: https://json-schema.org/draft/2020-12/schema`, `$id: gzkit.advisor_diagnosis.v1`.
- `additionalProperties: false` on every object subtype.
- `proof`: `type: array`, `minItems: 1`, items reference a `ProofRange` `$defs` block.
- `archetype`: `type: string`, `enum: [<ten archetype values>]`.
- `crossing_band`: `type: string`, `enum: ["block", "warn", "advise"]`.
- `authority` (under `DoctrinalFrame` `$defs`): `enum: ["fowler", "martin", "page_jones", "constantine"]`.
- `start_line`: `type: integer`, `minimum: 1`. `end_line`: `type: integer`, `minimum: 1`. Cross-field `end_line ≥ start_line` is enforced by Pydantic only (JSON Schema Draft 2020-12 has no first-class cross-field comparison; the test suite covers this via Pydantic-side rejection).

### Test design (binding from REQ-8)

Each test is decorated with `@covers("REQ-0.0.29-01-NN")` so the Stage 3 Phase 1b parity gate (`gz covers OBPI-0.0.29-01 --json`) reports `uncovered_reqs == 0`. Test class: `TestAdvisorDiagnosisSchema(unittest.TestCase)`. Tests:

- `test_advisor_diagnosis_valid_instantiation` → REQ-01 (valid input → frozen instance returned).
- `test_advisor_diagnosis_rejects_empty_proof` → REQ-02 (`proof=()` → `ValidationError`).
- `test_advisor_diagnosis_rejects_unknown_archetype` → REQ-03 (archetype outside enum → `ValidationError`).
- `test_doctrinal_frame_rejects_unknown_authority` → REQ-04.
- `test_advisor_diagnosis_is_frozen` → REQ-05 (mutation raises `ValidationError`).
- `test_advisor_diagnosis_rejects_unknown_crossing_band` → REQ-04 (parallel — `crossing_band` outside enum).
- `test_proof_range_rejects_end_before_start` → REQ-04 (parallel — `end_line < start_line`).
- `test_json_schema_validates_serialized_diagnosis` → REQ-06 (positive JSON Schema validation).
- `test_json_schema_rejects_empty_proof` → REQ-06 (negative JSON Schema validation).
- `test_json_schema_rejects_unknown_enum` → REQ-06 (negative JSON Schema validation — bad archetype + bad authority).

REQ-07 (`ConfigDict(frozen=True, extra="forbid")` on all four classes) is covered by `test_advisor_diagnosis_is_frozen` plus a parameterized `test_all_models_forbid_extra` that walks `[AdvisorDiagnosis, DoctrinalFrame, ProofRange, IntrinsicAttestationRef]` and instantiates each with an unknown extra field, expecting `ValidationError`.

REQ-09 (TDD discipline + `tempfile`-backed fixtures) is procedural; the test module uses `tempfile.NamedTemporaryFile` only where filesystem state is required (not strictly necessary for in-memory schema tests, but the JSON-Schema-load test reads the schema from `src/gzkit/schemas/` directly via `pathlib.Path` — no temp file needed there).

REQ-10 (no operator email) is procedural; verified by absence in the test module.

### Discovery Checklist coverage (brief lines 58-62)

- [x] Parent ADR § Decision — read; field shapes confirmed; ten-archetype canon confirmed; four-authority canon confirmed.
- [x] `.claude/rules/models.md` — read; `ConfigDict(frozen=True, extra="forbid")` pattern locked.
- [x] `.claude/rules/pythonic.md` — read; size limits + ty type-ignore syntax noted.
- [x] AGENTS.md § STDLIB-FIRST DOCTRINE — confirmed pydantic + jsonschema both already runtime deps.

## Steps

### Step 1: Create the package skeleton (scaffold + import surface)

Author `src/gzkit/complexity/advisor/__init__.py` as a re-export module. Contents (all five symbols imported from `.diagnosis` and listed in `__all__`):

```python
"""Complexity advisor package — diagnosis schema and downstream surfaces."""
from gzkit.complexity.advisor.diagnosis import (
    AdvisorDiagnosis,
    DoctrinalFrame,
    IntrinsicAttestationRef,
    ProofRange,
    RefactorArchetype,
)

__all__ = [
    "AdvisorDiagnosis",
    "DoctrinalFrame",
    "IntrinsicAttestationRef",
    "ProofRange",
    "RefactorArchetype",
]
```

This `__init__.py` is the cleanest re-export shape; downstream OBPIs import from `gzkit.complexity.advisor` directly.

### Step 2: Author `diagnosis.py` (Pydantic models + StrEnum + JSON Schema constants)

`src/gzkit/complexity/advisor/diagnosis.py` carries:

1. Module docstring naming OBPI-0.0.29-01 + the five symbols.
2. `from __future__ import annotations`.
3. Imports: `from enum import StrEnum`; `from typing import Literal`; `from pydantic import BaseModel, ConfigDict, Field, model_validator`.
4. `class RefactorArchetype(StrEnum)` — ten members in the brief order:
   - `LONG_PARAMETER_LIST = "long_parameter_list"`
   - `ARROWHEAD = "arrowhead"`
   - `SWITCH_ON_TYPE = "switch_on_type"`
   - `FEATURE_ENVY = "feature_envy"`
   - `LARGE_CLASS = "large_class"`
   - `DIVERGENT_CHANGE = "divergent_change"`
   - `SHOTGUN_SURGERY = "shotgun_surgery"`
   - `PRIMITIVE_OBSESSION = "primitive_obsession"`
   - `DATA_CLUMPS = "data_clumps"`
   - `MESSAGE_CHAIN = "message_chain"`
5. `class DoctrinalFrame(BaseModel)` — `model_config = ConfigDict(frozen=True, extra="forbid")`; fields per REQ-2.
6. `class ProofRange(BaseModel)` — frozen; fields per REQ-3; `@model_validator(mode="after")` named `_check_line_range` raising `ValueError("end_line must be >= start_line")` when `end_line < start_line`.
7. `class IntrinsicAttestationRef(BaseModel)` — frozen forward stub; single `attestation_id: str` field; module docstring notes OBPI-07 will extend.
8. `class AdvisorDiagnosis(BaseModel)` — frozen; eight fields per REQ-4; `proof: tuple[ProofRange, ...] = Field(..., min_length=1, description="...")` AND a `@model_validator(mode="after")` named `_check_proof_nonempty` for belt-and-braces (catches edge cases where `min_length` is sometimes lax depending on pydantic version).
9. Top-level `__all__` list mirrors `__init__.py`.

Module size budget: ≤ 200 lines well within the 600-line limit. Each class is a small dataclass-shaped block (≤ 30 lines including docstring + fields + validator).

### Step 3: Author `advisor_diagnosis.json` (JSON Schema mirror)

`src/gzkit/schemas/advisor_diagnosis.json`. Modeled exactly after `src/gzkit/schemas/complexity_citation.json` shape:

- `$schema: https://json-schema.org/draft/2020-12/schema`.
- `$id: gzkit.advisor_diagnosis.v1`.
- `title: Advisor Diagnosis`.
- `description` naming the parent ADR + OBPI; explicitly noting the schema mirrors the Pydantic model and consumers MUST validate against this rather than re-deriving the shape.
- `$defs`: `RefactorArchetype` (string enum), `DoctrinalFrameAuthority` (string enum), `DoctrinalFrame` (object), `ProofRange` (object), `IntrinsicAttestationRef` (object).
- Top-level: `type: object`, `additionalProperties: false`, `required: [metric, crossing_band, crossing_value, archetype, doctrinal_frame, proof, recommended_move]` (note: `intrinsic_attestation` is optional → not in `required`).
- `proof`: `type: array`, `minItems: 1`, `items: {"$ref": "#/$defs/ProofRange"}`.

### Step 4: Author `tests/complexity/advisor/test_diagnosis.py` (TDD red → green)

Create `tests/complexity/advisor/__init__.py` if absent (empty marker). Test module structure:

1. Module docstring naming OBPI-0.0.29-01.
2. Imports: `unittest`, `json`, `pathlib.Path`, `pydantic.ValidationError`, `jsonschema`, `from gzkit.testing.covers import covers` (existing test decorator), `from gzkit.complexity.advisor.diagnosis import (...)`.
3. Module-level `_SCHEMA_PATH = Path(__file__).resolve().parents[3] / "src" / "gzkit" / "schemas" / "advisor_diagnosis.json"` — resolves regardless of CWD.
4. Module-level `_load_schema()` helper returning `json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))`.
5. Module-level `_VALID_DIAGNOSIS` fixture — a dict matching the schema with one `ProofRange`, ready for both Pydantic instantiation and JSON Schema validation.
6. `class TestAdvisorDiagnosisSchema(unittest.TestCase)` — methods per the test design above; each decorated with `@covers("REQ-0.0.29-01-NN")`.

TDD flow:
- **Red**: write all tests against the not-yet-authored module. They MUST fail at import time (no `diagnosis.py`).
- **Green**: implement Step 2 + Step 3; re-run tests; all pass.
- **Refactor**: clean up imports + docstrings; rerun.

### Step 5: Verify locally before completion ceremony

Run the standard verification gate:

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.complexity.advisor.test_diagnosis -v
```

Then the OBPI-scoped REQ-coverage parity gate:

```bash
uv run gz covers OBPI-0.0.29-01 --json
```

Expect `summary.uncovered_reqs == 0`. If any uncovered REQ remains, add the `@covers` decorator on the relevant test and re-run.

### Step 6: BDD waiver registration (Heavy lane Gate 4)

The brief Gate 4 explicitly says *"BDD waiver registered: schema-only; behavior coverage in OBPI-02/03"*. Add an entry to `data/behave_coverage_waivers.json` if the file's schema accepts schema-only OBPIs. If `data/behave_coverage_waivers.json` is not in the brief's Allowed Paths, the waiver mechanism is brief-evidence narrative only (record in the brief's Gate 4 evidence section that no scenario lands here; behavior surfaces at OBPI-02/03).

> **Decision check at Step 6:** The brief's Allowed Paths (lines 28-33) do **not** list `data/behave_coverage_waivers.json`. Per the brief allowlist contract this OBPI MUST NOT modify the waiver file. The waiver is therefore narrative-only at this brief — recorded in Gate 4 evidence ("BDD waiver: schema-only OBPI; behavior coverage at OBPI-02/03"). If a sibling pattern (e.g. OBPI-0.0.28-01 plan editing `data/behave_coverage_waivers.json`) suggests the waiver file is required, surface to operator before editing — bundling the waiver into this OBPI is brief-boundary anti-pattern.

## Verification

```bash
# Phase 1: baseline quality (ARB-wrapped)
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.complexity.advisor.test_diagnosis -v

# Phase 1b: REQ → @covers parity gate
uv run gz covers OBPI-0.0.29-01 --json

# Heavy-lane gates
uv run gz validate --documents
uv run mkdocs build --strict
```

The brief's Verification section (lines 87-92) cites these commands; no schema-fixture tests beyond the unittest module are required at this OBPI.

## Notes

### Why this OBPI is schema-only (not engine-bearing)

ADR-0.0.29 § Sequencing (line 88) locks: `OBPI-01 → OBPI-02 → OBPI-08 → OBPI-03 → ...`. OBPI-01 is the schema layer that OBPI-02's engine binds against. Bundling engine logic here would violate brief-boundary discipline (Behavior Rules — Never #5) and would defer engine-specific verification (AST traversal, ThresholdTable binding, distilled-characteristics parsing) into a brief whose Acceptance Criteria are all schema-shaped. Keep this OBPI schema-only.

### Why `IntrinsicAttestationRef` is stubbed here, not at OBPI-07

OBPI-07 brief (line citing OBPI-01) confirms: *"OBPI-01 schema — `IntrinsicAttestationRef` stub"* is a dependency. The forward stub lives in `diagnosis.py` so `AdvisorDiagnosis.intrinsic_attestation` typechecks against a real symbol from day one. OBPI-07 extends the stub (adds `reason`, `attestor`, `attested_at`, ledger-event linkage) without breaking the optional-field shape on `AdvisorDiagnosis`. The forward stub is the cleanest seam.

### Plan-before-exploration disclosures (per gz-plan-audit Step 6a)

**Destination-in-mind:** Yes, before authoring this plan I had a destination — frozen Pydantic models (`ConfigDict(frozen=True, extra="forbid")`) mirroring `complexity_citation.py`'s pattern, with a parallel JSON Schema using `additionalProperties: false`. The brief's REQ-1 through REQ-7 effectively dictate the shape; the only meaningful design choice was whether `proof` non-emptiness is enforced by `Field(min_length=1)` or by `@model_validator` — I chose **both** (defense in depth) because Pydantic 2's `min_length` on tuple fields has had edge-case looseness in earlier 2.x versions (observed in `pydantic-core` 2.10 → 2.18 series), and a `@model_validator` is the unambiguous belt-and-braces.

**Rejected alternatives:**

1. **Single-file with engine + schema bundled** — rejected; violates ADR-0.0.29 § Sequencing (OBPI-01 is schema-only) and brief-boundary discipline (engine is OBPI-02's denied-paths-of-this brief). Bundling would create one Gate 5 witness for two separable invariants.
2. **JSON Schema as primary source-of-truth, Pydantic generated from it** — rejected; the brief specifies a frozen Pydantic model as the canonical shape (REQ-2/3/4/7); JSON Schema is the **mirror** (REQ-5). This matches the established pattern at `src/gzkit/complexity/citation.py` ↔ `src/gzkit/schemas/complexity_citation.json`.
3. **`RefactorArchetype` as `Enum` (not `StrEnum`)** — rejected; the brief explicitly says `StrEnum` (REQ-1). `StrEnum` makes serialization (`AdvisorDiagnosis.model_dump()`) emit plain strings without a `.value` accessor in JSON output, which is what the JSON Schema mirror expects.
4. **Inline `IntrinsicAttestationRef` definition vs. forward stub** — considered keeping it as just `attestation_id: str` directly on `AdvisorDiagnosis`. Rejected because OBPI-07 will extend it with `reason`, `attestor`, `attested_at`, ledger-event-id — making it a class now keeps the field shape stable and lets OBPI-07 add fields without breaking `AdvisorDiagnosis`'s public surface.
5. **Skip the `@model_validator` for `end_line ≥ start_line` and rely on JSON Schema** — rejected; JSON Schema Draft 2020-12 has no portable cross-field comparator. The Pydantic-side validator is the fail-closed surface; JSON Schema only catches type/enum violations.

### Defects flagged in flight (pre-implementation)

None at plan-authoring time. The five `gz plan audit` "Allowed path does not exist" gaps are net-new files this plan creates (`creates these files` declarations above resolve the gap per GHI #403).

The 200 sibling-ADR overlap warnings from `gz plan audit` are advisory; on inspection they all come from sibling pool/post-1.0 OBPIs whose Allowed Paths globs (`tests/**`, `src/gzkit/**`) trivially overlap any net-new file. None are active foundation/feature OBPIs in flight.
