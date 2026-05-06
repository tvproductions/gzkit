# Plan: OBPI-0.0.28-02-threshold-loader

**OBPI:** OBPI-0.0.28-02-threshold-loader
**Parent ADR:** ADR-0.0.28 (foundation, heavy lane)
**Objective:** Implement frozen `ThresholdBand` and `ThresholdTable` Pydantic models at `src/gzkit/complexity/thresholds.py`, a parser `load_threshold_table(rule_path: Path) -> ThresholdTable` that loads `.gzkit/rules/complexity-thresholds.md` into the model, lookup methods (`band_for(metric, value)`, `bands_for_metric(metric)`), and a JSON Schema mirror at `src/gzkit/schemas/complexity_thresholds.json` enforcing the trigger-semantic enum + percentile-value constraint + mandatory-block-per-metric invariant. This is the data contract ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance bind against.

## Allowed Files

- `src/gzkit/complexity/__init__.py` — re-export new loader symbols (additive)
- `src/gzkit/complexity/thresholds.py` — new module: `ThresholdBand` + `ThresholdTable` + `load_threshold_table` + `band_for` + `bands_for_metric`
- `src/gzkit/schemas/complexity_thresholds.json` — JSON Schema mirror
- `tests/complexity/test_thresholds.py` — REQ-derived tests
- `data/behave_coverage_waivers.json` — Gate 4 BDD waiver registration
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-02-threshold-loader.md` — evidence section + Discovery Checklist (already authored)

## Context

### Rule body shape the loader parses (from OBPI-0.0.28-01)

- Top-level `## Citation` section with canonical-string form: `docs/governance/complexity/distilled-characteristics-{date}.md § {anchor} (corpus revision {N})`
- 12 per-metric sections shaped `### Metric: \`{metric_name}\`` followed by a markdown table:
  ```
  | Trigger | Corpus percentile | Absolute number | Cited section |
  |---------|-------------------|-----------------|---------------|
  | advise  | p75               | 4.00            | radon-cc      |
  | warn    | p90               | 7.00            | radon-cc      |
  | block   | p95               | 11.00           | radon-cc      |
  ```
- A bootstrap carve-out section that names exempt metrics (validator OBPI-03 skips portability checks for these)

### Schema constraints

- Pydantic models: `BaseModel` + `ConfigDict(frozen=True, extra="forbid")` (per `.gzkit/rules/models.md`)
- `ThresholdBand` fields: `metric: str`, `corpus_percentile: int` (constrained to {50, 75, 90, 95, 99}), `absolute_number: float`, `trigger_semantic: Literal["block", "warn", "advise"]`
- `ThresholdTable` fields: `corpus_revision: int`, `bands: tuple[ThresholdBand, ...]`, `citation: Citation`
- `bands` is `tuple[...]` not `list[...]` — frozen-at-construction via Pydantic
- `band_for(metric, value)` returns highest-severity band where `value >= absolute_number` (high-is-worse default; polarity-aware tracked under GHI #405 as separate work)
- `bands_for_metric(metric)` returns per-metric bands sorted by ascending percentile
- Loader fail-closes with `ValidationError` on: missing block band per metric, missing percentile/absolute, unknown trigger-semantic, malformed citation

### JSON Schema mirror

- `additionalProperties: false` (Pydantic `extra="forbid"` equivalent)
- `trigger_semantic` enum: `["block", "warn", "advise"]`
- `corpus_percentile` enum: `[50, 75, 90, 95, 99]`
- `absolute_number` numeric
- `bands` array required; per-table validation that every metric has at least one block-band entry

## Steps

### Step 1: Write failing tests — TDD RED

Create `tests/complexity/test_thresholds.py` with REQ-derived tests:

- `REQ-0.0.28-02-01` — well-formed rule body parses to a frozen `ThresholdTable` with parsed bands and citation
- `REQ-0.0.28-02-02` — rule body where any metric lacks a `block` band fails with `ValidationError` naming the metric
- `REQ-0.0.28-02-03` — band with trigger-semantic outside `{block, warn, advise}` fails with `ValidationError`
- `REQ-0.0.28-02-04` — band missing `corpus_percentile` or `absolute_number` fails with `ValidationError`
- `REQ-0.0.28-02-05` — `band_for("radon_cc", 13)` against bands `(p75=4=advise, p90=7=warn, p95=11=block)` returns block band (highest severity crossed)
- `REQ-0.0.28-02-06` — `band_for("radon_cc", 5)` returns the advise band (5 >= 4 but < 7)
- `REQ-0.0.28-02-07` — mutation attempt on `ThresholdTable` instance raises `ValidationError`
- `REQ-0.0.28-02-08` — JSON Schema validates a known-good loaded table dict and rejects an unknown trigger-semantic
- Additional tests for: `bands_for_metric` ordering, `band_for` returns None below all bands, immutable-tuple `bands` cannot be reassigned, percentile out-of-enum rejection, integration with the actual landed `.gzkit/rules/complexity-thresholds.md`

Each test decorated with `@covers("REQ-0.0.28-02-NN")`. Tests use `tempfile`-backed fixtures (synthetic well-formed and malformed rule bodies) plus one integration test against the real `.gzkit/rules/complexity-thresholds.md`.

### Step 2: Implement `src/gzkit/complexity/thresholds.py` — TDD GREEN

Module structure:

```python
"""Threshold table data contract for ADR-0.0.28's complexity-doctrine cluster."""

from __future__ import annotations
import re
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

from gzkit.complexity.citation import Citation, parse_citation
from gzkit.rules import _parse_canonical_frontmatter

CANONICAL_PERCENTILES = (50, 75, 90, 95, 99)
TRIGGER_VOCABULARY = ("block", "warn", "advise")
_SEVERITY_ORDER = {"block": 3, "warn": 2, "advise": 1}


class ThresholdBand(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    metric: str = Field(min_length=1)
    corpus_percentile: int = Field(...)
    absolute_number: float = Field(ge=0.0)
    trigger_semantic: Literal["block", "warn", "advise"]
    # validator: corpus_percentile in CANONICAL_PERCENTILES


class ThresholdTable(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    corpus_revision: int = Field(gt=0)
    bands: tuple[ThresholdBand, ...]
    citation: Citation
    # validator: every metric appearing in `bands` has at least one block band

    def band_for(self, metric: str, value: float) -> ThresholdBand | None:
        # iterate bands for `metric`; collect bands where value >= absolute_number;
        # return highest-severity match (block > warn > advise) or None
        ...

    def bands_for_metric(self, metric: str) -> tuple[ThresholdBand, ...]:
        # filter and sort by ascending corpus_percentile
        ...


def load_threshold_table(rule_path: Path) -> ThresholdTable:
    # decompose into named helpers per pythonic.md function-size rule:
    #   _extract_citation_from_body(body) -> Citation
    #   _extract_per_metric_tables(body) -> Iterator[tuple[str, list[ThresholdBand]]]
    #   _parse_band_row(metric, row_text) -> ThresholdBand
    # then construct ThresholdTable(corpus_revision=..., bands=..., citation=...)
    ...
```

Helper decomposition keeps each function ≤ 50 lines. Bootstrap rows in the rule body (under the `## Bootstrap absolutes` section) are parsed identically — no special-casing at the loader layer (the validator OBPI-03 handles bootstrap-vs-cited distinctions for portability checks).

### Step 3: Author JSON Schema at `src/gzkit/schemas/complexity_thresholds.json`

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ThresholdTable",
  "type": "object",
  "additionalProperties": false,
  "required": ["corpus_revision", "bands", "citation"],
  "properties": {
    "corpus_revision": {"type": "integer", "minimum": 1},
    "bands": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["metric", "corpus_percentile", "absolute_number", "trigger_semantic"],
        "properties": {
          "metric": {"type": "string", "minLength": 1},
          "corpus_percentile": {"type": "integer", "enum": [50, 75, 90, 95, 99]},
          "absolute_number": {"type": "number", "minimum": 0},
          "trigger_semantic": {"type": "string", "enum": ["block", "warn", "advise"]}
        }
      }
    },
    "citation": {"$ref": "complexity_citation.json"}
  }
}
```

Mirrors the Pydantic model. Validators consuming the JSON form get the same shape Pydantic enforces.

### Step 4: Update `src/gzkit/complexity/__init__.py`

Add re-exports: `ThresholdBand`, `ThresholdTable`, `load_threshold_table` so consumers (advisor, authoring-guidance) import from the package surface.

### Step 5: Register BDD waiver

Add to `data/behave_coverage_waivers.json`:

```json
"OBPI-0.0.28-02-threshold-loader": {
  "rationale": "adr-0.0.28-foundation-bdd-deferred",
  "status_at_landing": "Draft"
}
```

(Rationale already registered under OBPI-01.)

### Step 6: Validate

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.complexity.test_thresholds -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.28-02-threshold-loader --json
uv run gz plan audit OBPI-0.0.28-02-threshold-loader
```

## Verification

Heavy-lane evidence: ARB receipts for ruff, typecheck, unittest, mkdocs.

REQ→@covers parity gate: 8/8 (100%) — uncovered=0.

## Notes

- **Polarity-aware model** (GHI #405) is OUT of scope for this OBPI. The `band_for` semantics here are high-is-worse (value >= absolute → trigger). `radon_mi` (lower-is-worse, clamped above p90 = 100) is in the rule body's bootstrap carve-out; the carve-out exempts it from validator portability checks until polarity-aware lands. The right shape is: this OBPI ships the high-is-worse model; a follow-up OBPI/ADR amendment lands polarity declarations in both the rule body and the model in the same patch (coupled-surface coherence).
- **Bootstrap rows** in the rule body are parsed identically. The bootstrap section's special semantics (skip portability checks) belong to OBPI-03 validator, not this loader. The loader treats `(p99, 4.00, block)` for `lizard_nesting_depth` the same as any other band row.
- **Function-size discipline:** decompose `load_threshold_table` into ≤ 50-line helpers (citation extraction, per-metric table iteration, band row parsing).
- **No new dependencies:** pure Python + Pydantic (already present per `.claude/rules/models.md`).
