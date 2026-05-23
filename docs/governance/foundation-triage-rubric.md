# Foundation Triage Rubric

**Source ADR:** `ADR-0.0.57-foundation-adr-nominal-id-triage`
**Module:** `src/gzkit/foundation/rubric.py`
**Schema:** `src/gzkit/schemas/foundation_triage_rank_input.json`

The foundation triage rubric converts in-flight foundation ADRs into ranked
structural entries using three evidence-grounded signal dimensions. Output
is purely structural — no prose rationale is generated per entry.

---

## Signal Dimensions

### `insights_signal_count`

Count of rows in `.gzkit/insights/agent-insights.jsonl` whose text contains
the foundation ADR's short identifier (e.g. `ADR-0.0.57`). Each matching
insight row represents an agent observation or course-correction linked to
a gap this foundation addresses.

**Weight:** 3 points per insight signal.

### `ghi_occurrence_count`

Count of unique GHI numbers (pattern `GHI #NNN`) found across the insights
rows that mention the foundation ID. Unique deduplication prevents a single
busy insight row from inflating the score. GHI occurrence measures operator
friction with the gap the foundation addresses.

**Weight:** 2 points per unique GHI reference.

### `feature_unblocking_count`

Count of pool or feature ADR files (under `docs/design/adr/`) whose
`depends_on` frontmatter lists the foundation's short ID. A foundation
that gates many downstream features has the highest unblocking score.

**Weight:** 5 points per dependent ADR — the highest weight because blocked
features are the most tangible evidence of a foundation's priority.

---

## Priority Score Formula

```
priority_score = insights_signal_count × 3
              + ghi_occurrence_count   × 2
              + feature_unblocking_count × 5
```

A foundation with zero signals in all three dimensions scores 0 but still
produces a valid `FoundationTriageRankEntry` — the evidence tuple always
contains one `EvidenceRef` per dimension, even when count is 0.

---

## Output Models

### `EvidenceRef`

Frozen Pydantic model (`extra="forbid"`) — the foundation-triage adaptation of
the canonical `gzkit.adr_eval.DimensionScore` shape (PRD term
`rubric-dimension`, "the basis for the structured-dimension scoring pattern
shared across `gz adr evaluate`, Optimize, and Triage skills"):

| Field | Type | Mirrors `DimensionScore`? | Description |
|-------|------|---------------------------|-------------|
| `dimension` | `Literal["insights_signal", "ghi_occurrence", "feature_unblocking"]` | `dimension: str` | Canonical signal-dimension name |
| `source` | `str` | **added** (PRD `evidence-citation`) | POSIX path of the artifact counted |
| `weight` | `int` (`ge=1`) | `weight: float` | Per-dimension weight (3 / 2 / 5) |
| `count` | `int` (`ge=0`) | `score: int` (1-4) | Raw signal count |
| `weighted` | `int` (`ge=0`) | `weighted: float` | `weight × count` — checked by model validator |
| _no `findings`_ | — | **omitted** (REQ-04-03) | Foundation-triage is structural-only; no prose findings |

**Two deliberate divergences from `DimensionScore`:**

1. **Adds `source`** per PRD `evidence-citation` term — foundation-triage
   dimensions are mechanically counted from observable artifacts (insights
   stream, GHI references, pool-ADR `depends_on`), so each dimension carries
   the path of the artifact it counted.
2. **Omits `findings: list[str]`** per REQ-0.0.57-04-03 (structural-only,
   no prose). `findings` is judgment-driven prose; foundation-triage is
   mechanical counting. Removing the field mirrors `ghi-triage` round-3
   hardening (GHI #424) where prose fields were removed to make operator-chat
   duplication structurally impossible.

**Weight type divergence:** `int` here vs `float` in `DimensionScore` because
foundation-triage emits a discrete priority score, not a 1-4 weighted average
summing to 1.0.

### `FoundationTriageRankEntry`

Frozen Pydantic model (`extra="forbid"`):

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| `id` | `str` | — | Short foundation ADR id, e.g. `ADR-0.0.57` |
| `priority_score` | `int` | `ge=0` | Non-negative weighted composite score |
| `evidence` | `tuple[EvidenceRef, ...]` | `min_length=1` **+** `_check_evidence_nonempty` model validator | One ref per signal dimension |

The `evidence` tuple minimum-length constraint mirrors the `AdvisorDiagnosis.proof`
binding from ADR-0.0.29 in **belt-and-braces** form: `Field(min_length=1)` gives
Pydantic 2 the declarative constraint; the `_check_evidence_nonempty` model
validator catches edge-case looseness observed in pydantic-core 2.10–2.18
where `min_length` on tuple fields was intermittently lax. The `signal_type`
Literal mirrors the same precedent's use of `Literal["block", "warn", "advise"]`
on `crossing_band`.

### Relationship to `ghi-triage` and `pool-triage` rank-input shape

The `ghi-triage` skill (GHI #424 round-3 hardening) and the parallel pool-triage
cognitive pass (OBPI-0.0.48-02) emit a two-field `{id, severity}` structural-only
shape consumed by the operator. This rubric module emits a different shape —
`{id, priority_score, evidence}` — because it is the **computation layer** that
feeds the foundation-triage skill; the skill in turn classifies severity from
the computed signals. The structural-only invariant (no prose, schema rejects
extras with `extra="forbid"`) is identical across all three rank-input contracts.

---

## CLI Invocation

```bash
# Score all in-flight foundations in the current project
uv run python -m gzkit.foundation.rubric --format json

# Score from a fixture backlog directory and insights file
uv run python -m gzkit.foundation.rubric \
  --foundation-root tests/fixtures/foundation_triage_rubric/backlog \
  --insights tests/fixtures/foundation_triage_rubric/insights.jsonl \
  --format json | jq '.rank_input'

# Inspect evidence citations on the top-ranked entry
uv run python -m gzkit.foundation.rubric --format json | jq '.rank_input[0].evidence'

# Confirm structural-only output (no prose fields)
uv run python -m gzkit.foundation.rubric --format json | jq '.rank_input[0] | keys'
# Expected: ["evidence", "id", "priority_score"]
```

---

## JSON Schema

The schema at `src/gzkit/schemas/foundation_triage_rank_input.json` is
emitted directly from `FoundationTriageRankEntry.model_json_schema()`. It
enforces `additionalProperties: false` and `minItems: 1` on the evidence
array. Schema and model must stay in sync — `test_schema_validates_pydantic_output`
fail-closes on drift.

---

## Relationship to Other Modules

- **`src/gzkit/foundation/triage.py`** (OBPI-0.0.57-03): the composer that
  gathers in-flight foundations and raw signal counts. The rubric is the
  scoring layer that triage.py defers to once this module is available.
- **`gz-foundation-triage` skill**: invokes the rubric via the bundled
  script for the Step-1 mechanical pre-pass; ranking falls back to raw
  signal totals when the rubric module is unavailable.
