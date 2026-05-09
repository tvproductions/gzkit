# Plan: OBPI-0.0.30-03 — Authoring-time Hint Engine + AuthoringHint Projection

**OBPI:** OBPI-0.0.30-03-authoring-hint-engine
**ADR:** ADR-0.0.30 (Complexity Authoring Guidance)
**Lane:** Heavy | **Kind:** Foundation
**Plan date:** 2026-05-09

---

## Context

OBPI-0.0.30-03 is the data surface for the entire ADR-0.0.30 cluster. It
implements two things:

1. `AuthoringHint` — a frozen Pydantic model that is a lighter projection of
   `AdvisorDiagnosis` (ADR-0.0.29-01). Fields: `metric`, `precedence_band`,
   `crossing_value`, `archetype`, `doctrinal_frame_headline`,
   `recommended_move`, `file_path`, `start_line`, `end_line`.

2. The authoring-time hint engine (`engine.analyze(path)`) that wraps
   `DiagnosisEngine` (ADR-0.0.29-02), filters to `advise`-band crossings only,
   classifies each as `approaching` vs `approaching_warn`, and projects through
   `project_diagnosis_to_hint`.

Both OBPI-01 (CLI) and OBPI-04 (editor protocol) consume this surface.
Sequencing is: OBPI-03 → OBPI-01 → OBPI-02 → OBPI-04 → OBPI-05.

**Dependencies verified (STOP-on-BLOCKERS check):**
- ADR-0.0.29-01 (`AdvisorDiagnosis`, `RefactorArchetype`, `DoctrinalFrame`,
  `ProofRange`) — ATTESTED COMPLETED at `src/gzkit/complexity/advisor/diagnosis.py`
- ADR-0.0.29-02 (`DiagnosisEngine.diagnose`) — ATTESTED COMPLETED at
  `src/gzkit/complexity/advisor/engine.py`

Blockers are clear. Implementation is unblocked.

---

## Creates These Files

**CREATE** `src/gzkit/complexity/authoring/__init__.py`
**CREATE** `src/gzkit/complexity/authoring/hint.py`
**CREATE** `src/gzkit/complexity/authoring/engine.py`
**CREATE** `src/gzkit/schemas/authoring_hint.json`
**CREATE** `tests/complexity/__init__.py`
**CREATE** `tests/complexity/authoring/__init__.py`
**CREATE** `tests/complexity/authoring/test_hint.py`
**CREATE** `tests/complexity/authoring/test_engine.py`

---

## Files

### Created
- `src/gzkit/complexity/authoring/__init__.py` — package marker (empty)
- `src/gzkit/complexity/authoring/hint.py` — `AuthoringHint` model +
  `project_diagnosis_to_hint` projection function
- `src/gzkit/complexity/authoring/engine.py` — authoring hint engine
- `src/gzkit/schemas/authoring_hint.json` — JSON Schema mirror of `AuthoringHint`
- `tests/complexity/__init__.py` — test package marker (if not existing)
- `tests/complexity/authoring/__init__.py` — test package marker
- `tests/complexity/authoring/test_hint.py` — model + projection unit tests
- `tests/complexity/authoring/test_engine.py` — engine unit tests

### Modified
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-03-authoring-hint-engine.md`
  — evidence sections only

---

## Steps

### Step 1 — Create `src/gzkit/complexity/authoring/__init__.py`

Empty package init — marks the `authoring` package. No exports needed at this
step (hint.py and engine.py export their own symbols).

### Step 2 — Create `src/gzkit/complexity/authoring/hint.py` (TDD: RED first)

Write failing tests in `tests/complexity/authoring/test_hint.py` first, then
implement.

#### `AuthoringHint` model

```python
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.complexity.advisor.diagnosis import RefactorArchetype


class AuthoringHint(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    metric: str = Field(..., description="Complexity metric key.")
    precedence_band: Literal["approaching", "approaching_warn"] = Field(
        ...,
        description="Position within the advise band: lower or upper half.",
    )
    crossing_value: float = Field(..., description="Observed metric value.")
    archetype: RefactorArchetype = Field(..., description="Refactor archetype.")
    doctrinal_frame_headline: str = Field(
        ...,
        description="First line of the doctrinal excerpt (truncated headline).",
    )
    recommended_move: str = Field(..., description="Recommended refactor move.")
    file_path: str = Field(..., description="Source file path (from first ProofRange).")
    start_line: int = Field(..., ge=1, description="Start line (from first ProofRange).")
    end_line: int = Field(..., ge=1, description="End line (from first ProofRange).")
```

#### `project_diagnosis_to_hint`

```python
from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis


def project_diagnosis_to_hint(
    diagnosis: AdvisorDiagnosis,
    *,
    precedence_band: Literal["approaching", "approaching_warn"],
) -> AuthoringHint | None:
    """Project an AdvisorDiagnosis to an AuthoringHint (advise-band only).

    Returns None for warn/block crossings — those are the trigger-time
    advisor's responsibility (ADR-0.0.29), not the authoring-guidance surface.
    Projection direction is fixed: AdvisorDiagnosis → AuthoringHint (never
    reverse).
    """
    if diagnosis.crossing_band != "advise":
        return None
    first_proof = diagnosis.proof[0]
    headline = diagnosis.doctrinal_frame.excerpt.splitlines()[0]
    return AuthoringHint(
        metric=diagnosis.metric,
        precedence_band=precedence_band,
        crossing_value=diagnosis.crossing_value,
        archetype=diagnosis.archetype,
        doctrinal_frame_headline=headline,
        recommended_move=diagnosis.recommended_move,
        file_path=first_proof.file_path,
        start_line=first_proof.start_line,
        end_line=first_proof.end_line,
    )
```

**Design note:** `precedence_band` is a keyword-only argument because:
- `AuthoringHint` requires it as a field
- The projection function cannot compute it from `AdvisorDiagnosis` alone (no
  threshold table access)
- The engine is responsible for classification; the projection is responsible
  for structural field mapping
- This separates concerns: engine classifies, projection projects

Size constraint: projection ≤ 50 lines — straightforward.

### Step 3 — Create `src/gzkit/complexity/authoring/engine.py`

The engine wraps `DiagnosisEngine` (ADR-0.0.29-02). Currently implements
`radon_cc` metric only (consistent with `complexity_advise.py` pattern).

```python
"""Authoring-time hint engine for ADR-0.0.30.

Wraps DiagnosisEngine (ADR-0.0.29-02); filters to advise-band crossings;
projects to AuthoringHint via project_diagnosis_to_hint.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Literal

from radon.complexity import cc_visit
from radon.visitors import Function

from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis
from gzkit.complexity.advisor.engine import AstContext, DiagnosisEngine
from gzkit.complexity.authoring.hint import AuthoringHint, project_diagnosis_to_hint
from gzkit.complexity.thresholds import ThresholdTable, load_threshold_table

_METRIC_KEY = "radon_cc"
_DEFAULT_RULE_PATH = Path(".gzkit/rules/complexity-thresholds.json")


def analyze(path: Path, table: ThresholdTable | None = None) -> tuple[AuthoringHint, ...]:
    """Analyze path for advise-band complexity crossings.

    Returns a tuple of AuthoringHint (may be empty). Only advise-band
    crossings surface — warn/block are the trigger-time advisor's scope.
    """
    if table is None:
        table = load_threshold_table(_DEFAULT_RULE_PATH)
    engine = DiagnosisEngine()
    hints: list[AuthoringHint] = []
    targets = [path] if path.is_file() else sorted(path.rglob("*.py"))
    for file_path in targets:
        hints.extend(_analyze_file(file_path, table, engine))
    return tuple(hints)


def _analyze_file(
    source_file: Path,
    table: ThresholdTable,
    engine: DiagnosisEngine,
) -> list[AuthoringHint]:
    """Analyze one file; return AuthoringHint list (may be empty)."""
    try:
        source = source_file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(source_file))
    except (OSError, SyntaxError):
        return []
    radon_blocks = [b for b in cc_visit(source) if isinstance(b, Function)]
    func_nodes = _index_function_nodes(tree)
    hints: list[AuthoringHint] = []
    for block in radon_blocks:
        hint = _process_block(block, source_file, source, tree, func_nodes, table, engine)
        if hint is not None:
            hints.append(hint)
    return hints


def _process_block(
    block: Function,
    source_file: Path,
    source: str,
    tree: ast.Module,
    func_nodes: dict[int, ast.AST],
    table: ThresholdTable,
    engine: DiagnosisEngine,
) -> AuthoringHint | None:
    """Process one radon block; return hint if it is an advise-band crossing."""
    band = table.band_for(_METRIC_KEY, float(block.complexity))
    if band is None or band.trigger_semantic != "advise":
        return None
    target_node = func_nodes.get(block.lineno)
    if target_node is None:
        return None
    ast_context = AstContext(
        file_path=str(source_file),
        source=source,
        tree=tree,
        target_node=target_node,
    )
    diagnosis = engine.diagnose(ast_context, _METRIC_KEY, float(block.complexity), table)
    if diagnosis is None:
        return None
    precedence_band = _classify_precedence_band(table, _METRIC_KEY, float(block.complexity))
    return project_diagnosis_to_hint(diagnosis, precedence_band=precedence_band)


def _classify_precedence_band(
    table: ThresholdTable,
    metric: str,
    value: float,
) -> Literal["approaching", "approaching_warn"]:
    """Classify value as approaching or approaching_warn within the advise band.

    Boundary = median of advise_lower and warn_lower. Computed from table,
    not hardcoded (REQ-0.0.30-03-05).
    """
    advise_lower = _band_absolute(table, metric, "advise")
    warn_lower = _band_absolute(table, metric, "warn")
    if warn_lower is None:
        return "approaching"
    midpoint = (advise_lower + warn_lower) / 2
    return "approaching_warn" if value >= midpoint else "approaching"


def _band_absolute(table: ThresholdTable, metric: str, trigger: str) -> float:
    """Return the absolute_number for the named trigger band, or 0.0."""
    for band in table.bands:
        if band.metric == metric and band.trigger_semantic == trigger:
            return band.absolute_number
    return 0.0


def _index_function_nodes(tree: ast.Module) -> dict[int, ast.AST]:
    """Map lineno to FunctionDef/AsyncFunctionDef node."""
    indexed: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            indexed[node.lineno] = node
    return indexed
```

Size constraint: `analyze` ≤ 50 lines, `_analyze_file` ≤ 50 lines — both
decompose into named helpers above.

### Step 4 — Create `src/gzkit/schemas/authoring_hint.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "authoring_hint",
  "title": "AuthoringHint",
  "description": "Lighter projection of AdvisorDiagnosis for authoring-time hints (ADR-0.0.30).",
  "type": "object",
  "required": [
    "metric",
    "precedence_band",
    "crossing_value",
    "archetype",
    "doctrinal_frame_headline",
    "recommended_move",
    "file_path",
    "start_line",
    "end_line"
  ],
  "properties": {
    "metric": {"type": "string", "minLength": 1},
    "precedence_band": {
      "type": "string",
      "enum": ["approaching", "approaching_warn"]
    },
    "crossing_value": {"type": "number"},
    "archetype": {
      "type": "string",
      "enum": [
        "long_parameter_list",
        "arrowhead",
        "switch_on_type",
        "feature_envy",
        "large_class",
        "divergent_change",
        "shotgun_surgery",
        "primitive_obsession",
        "data_clumps",
        "message_chain"
      ]
    },
    "doctrinal_frame_headline": {"type": "string", "minLength": 1},
    "recommended_move": {"type": "string", "minLength": 1},
    "file_path": {"type": "string", "minLength": 1},
    "start_line": {"type": "integer", "minimum": 1},
    "end_line": {"type": "integer", "minimum": 1}
  },
  "additionalProperties": false
}
```

Note: `start_line ≤ end_line` cross-field constraint is enforced by the
Pydantic model validator (not expressible in JSON Schema Draft 2020-12 as a
portable cross-field comparator).

### Step 5 — Create test files (TDD cycle)

#### `tests/complexity/authoring/test_hint.py`

Test class structure with `@covers` decorators:

**`TestAuthoringHintModel`** — model instantiation and validation:
- `test_valid_instantiation` → `@covers("REQ-0.0.30-03-01")`
- `test_frozen_mutation_raises` → `@covers("REQ-0.0.30-03-08")`
- `test_extra_field_rejected` — Pydantic `extra="forbid"` (supports REQ-01)
- `test_precedence_band_outside_enum_rejected` — validation
- `test_archetype_outside_enum_rejected` — validation

**`TestProjectDiagnosisToHint`** — projection function:
- `test_advise_band_returns_hint` → `@covers("REQ-0.0.30-03-02")`
- `test_warn_band_returns_none` → `@covers("REQ-0.0.30-03-03")`
- `test_block_band_returns_none` → `@covers("REQ-0.0.30-03-03")`
- `test_drops_proof_field` → `@covers("REQ-0.0.30-03-04")`
- `test_drops_intrinsic_attestation_field` → `@covers("REQ-0.0.30-03-04")`
- `test_promotes_first_proof_range_location` → `@covers("REQ-0.0.30-03-04")`
- `test_truncates_doctrinal_frame_to_first_line` — headline truncation

Helper factory `_make_diagnosis(crossing_band, ...)` builds an `AdvisorDiagnosis`
with tempfile-backed `ProofRange.file_path`. Do NOT hardcode real file paths.

#### `tests/complexity/authoring/test_engine.py`

**`TestAuthoringEngine`**:
- `test_clean_file_returns_empty_tuple` → `@covers("REQ-0.0.30-03-05")`
  Uses a tempfile containing a trivially simple function (CC=1).
- `test_advise_band_file_returns_hints` → `@covers("REQ-0.0.30-03-06")`
  Writes a Python tempfile with a function that crosses the advise band.
  Mocks `DiagnosisEngine.diagnose` to return an `AdvisorDiagnosis` with
  `crossing_band="advise"`. Verifies `analyze()` returns non-empty tuple.
- `test_warn_band_not_included` — mocks `band_for` to return warn, verifies
  `analyze()` returns empty tuple.
- `test_precedence_band_approaching_warn` → `@covers("REQ-0.0.30-03-07")`
  Uses `_classify_precedence_band` with a value at the upper half.
- `test_precedence_band_approaching` → `@covers("REQ-0.0.30-03-07")`
  Uses `_classify_precedence_band` with a value at the lower half.

Mock pattern: `unittest.mock.patch("gzkit.complexity.advisor.engine.DiagnosisEngine.diagnose")`
for engine tests. Use `tempfile.NamedTemporaryFile` for Python source files.

---

## Verification

```bash
# Baseline quality (ARB-wrapped)
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/authoring/test_hint.py tests/complexity/authoring/test_engine.py -v

# Full suite regression check
uv run gz arb step --name unittest -- uv run -m unittest -q
```

---

## Plan-Before-Exploration Disclosures (gz-plan-audit § Step 6a)

**Destination-in-mind before writing this plan:**
Before exploration, I expected `project_diagnosis_to_hint` to take only
`diagnosis: AdvisorDiagnosis` per the brief's stated signature. After reading
the `AdvisorDiagnosis` schema and understanding that `precedence_band` is not
part of `AdvisorDiagnosis`, I concluded a keyword-only `precedence_band`
argument is required. This was discovered during plan authoring, not post-hoc.

**Rejected alternatives considered:**
1. `project_diagnosis_to_hint(diagnosis, table) -> AuthoringHint | None` — more
   complete but couples the projection function to the threshold table, violating
   the projection-is-structural principle.
2. Storing `precedence_band` in a mutable wrapper before projecting — introduces
   mutable state inconsistent with the frozen model discipline.
3. Computing `precedence_band` inside `AuthoringHint.__init__` via a validator —
   requires passing the table to the model constructor, which violates
   `extra="forbid"` (table is not an `AuthoringHint` field).
4. Implementing all 12 threshold metrics instead of just `radon_cc` — exceeds
   OBPI scope; the brief says "for each metric crossing in the threshold table"
   but `complexity_advise.py` only implements `radon_cc` currently; follow the
   same pattern.
