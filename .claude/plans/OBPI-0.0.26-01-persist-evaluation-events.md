# Plan: OBPI-0.0.26-01-persist-evaluation-events

**OBPI:** OBPI-0.0.26-01-persist-evaluation-events
**Parent ADR:** ADR-0.0.26-evaluation-feedback-loop-doctrine
**Lane:** Heavy
**Objective:** Emit a canonical `adr-evaluation` ledger event from every successful `gz-adr-evaluate` invocation; extend `gz validate --documents` to recognize the new event shape.

## Context

The evaluate command (`adr_eval_cmd` in `src/gzkit/commands/adr_promote.py`) already emits `adr_eval_completed` — a sparse summary event. This OBPI adds a richer `adr-evaluation` event that captures per-dimension scores, red-team challenge results, and evaluator identity, binding evaluation data to T2 ledger truth per ADR-0.0.26 Decision item 1.

Existing event chain:
- `adr_eval_cmd` (adr_promote.py) → `adr_eval_completed_event` (ledger_events.py) → `adr_eval_completed` ledger event
- `AdrEvalResult` has: `adr_dimensions: list[DimensionScore]`, `red_team_results: list[RedTeamChallengeResult]`, `adr_weighted_total`, `adr_id`, `timestamp`

Path note: brief lists `src/gzkit/governance/ledger_events.py` but actual file is `src/gzkit/ledger_events.py`. Brief's escape clause "or wherever the evaluate command lives" covers the actual path.

## Files

### New files
- `tests/governance/test_evaluation_event.py` — event factory + schema tests
- `tests/commands/test_adr_evaluate_emission.py` — adr_eval_cmd emission tests

### Modified files
- `src/gzkit/ledger_events.py` — add `adr_evaluation_event` factory
- `src/gzkit/events.py` — add `AdrEvaluationEvent` typed class + union entry
- `src/gzkit/schemas/ledger.json` — add `adr-evaluation` schema entry
- `src/gzkit/governance/trust_audits/events.py` — add `adr-evaluation` to `_NO_GRAPH_IMPACT`
- `src/gzkit/commands/adr_promote.py` — wire `adr_evaluation_event` emission in `adr_eval_cmd`
- `src/gzkit/ledger.py` — re-export `adr_evaluation_event`

## Steps

### Step 1: Write failing tests (RED)

**`tests/governance/test_evaluation_event.py`:**
- `TestAdrEvaluationEventFactory.test_event_has_canonical_name` — factory returns event with `event="adr-evaluation"` (`@covers("REQ-0.0.26-01-01")`)
- `TestAdrEvaluationEventFactory.test_payload_contains_required_fields` — payload has `artifact_id`, `artifact_type`, `dimensions`, `scores`, `weighted_total`, `red_team_challenges_fired`, `evaluator_persona`, `timestamp` (`@covers("REQ-0.0.26-01-01")`)
- `TestAdrEvaluationEventFactory.test_dimensions_is_name_to_score_map` — `dimensions` is `dict[str, float]` (`@covers("REQ-0.0.26-01-01")`)
- `TestAdrEvaluationEventFactory.test_red_team_challenges_fired_is_list` — `red_team_challenges_fired` is `list[str]` (`@covers("REQ-0.0.26-01-01")`)
- `TestAdrEvaluationEventSchema.test_schema_entry_exists` — `adr-evaluation` key in `ledger.json` events map (`@covers("REQ-0.0.26-01-03")`)
- `TestAdrEvaluationEventSchema.test_schema_required_fields` — schema's `required` list matches payload (`@covers("REQ-0.0.26-01-03")`)
- `TestAdrEvaluationMultipleAppend.test_multiple_evaluations_append_not_upsert` — two `adr-evaluation` events for the same artifact produce two distinct ledger entries with distinct timestamps (`@covers("REQ-0.0.26-01-04")`)

**`tests/commands/test_adr_evaluate_emission.py`:**
- `TestAdrEvalCmdEmission.test_successful_eval_emits_exactly_one_adr_evaluation_event` — `adr_eval_cmd` with mocked `evaluate_adr` returning a passing result emits exactly one `adr-evaluation` event to a tempfile-backed ledger (`@covers("REQ-0.0.26-01-01")`)
- `TestAdrEvalCmdEmission.test_failed_eval_does_not_emit_adr_evaluation_event` — `adr_eval_cmd` with mocked `evaluate_adr` raising an exception emits no `adr-evaluation` event (`@covers("REQ-0.0.26-01-02")`)
- `TestAdrEvalCmdEmission.test_event_not_emitted_on_validator_error` — when `evaluate_adr` raises `SystemExit(3)` (NO GO verdict), no `adr-evaluation` event is emitted — NOTE: needs design clarification; the brief says "failed evaluation MUST NOT emit" but the current `adr_eval_cmd` still emits `adr_eval_completed` on any verdict; the brief's requirement applies only to the NEW event.

### Step 2: Add `adr_evaluation_event` to `src/gzkit/ledger_events.py` (GREEN)

```python
def adr_evaluation_event(
    *,
    artifact_id: str,
    artifact_type: str,
    dimensions: dict[str, float],
    scores: dict[str, float],
    weighted_total: float,
    red_team_challenges_fired: list[str],
    evaluator_persona: str,
    timestamp: str,
) -> LedgerEvent:
    """Create an adr-evaluation event (ADR-0.0.26 Decision item 1)."""
    return LedgerEvent(
        event="adr-evaluation",
        id=artifact_id,
        extra={
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "dimensions": dimensions,
            "scores": scores,
            "weighted_total": weighted_total,
            "red_team_challenges_fired": red_team_challenges_fired,
            "evaluator_persona": evaluator_persona,
            "timestamp": timestamp,
        },
    )
```

Note: `dimensions` = dimension-name → raw score; `scores` = dimension-name → weighted score. Both are derived from `AdrEvalResult.adr_dimensions`.

### Step 3: Add `AdrEvaluationEvent` to `src/gzkit/events.py` (GREEN)

Add typed class after `AdrEvalCompletedEvent`:

```python
class AdrEvaluationEvent(_EventBase):
    """adr-evaluation event — full per-dimension scores (ADR-0.0.26-01)."""

    event: Literal["adr-evaluation"]
    artifact_id: str
    artifact_type: str
    dimensions: dict[str, float]
    scores: dict[str, float]
    weighted_total: float
    red_team_challenges_fired: list[str]
    evaluator_persona: str
    timestamp: str
```

Add `| AdrEvaluationEvent` to the union type.

### Step 4: Extend `src/gzkit/schemas/ledger.json` (GREEN)

Add entry in `events` object:
```json
"adr-evaluation": {
  "required": ["artifact_id", "artifact_type", "dimensions", "scores", "weighted_total", "red_team_challenges_fired", "evaluator_persona", "timestamp"],
  "properties": {
    "artifact_id": { "type": "string", "min_length": 1 },
    "artifact_type": { "type": "string", "min_length": 1 },
    "dimensions": { "type": "object" },
    "scores": { "type": "object" },
    "weighted_total": { "type": "number" },
    "red_team_challenges_fired": { "type": "array" },
    "evaluator_persona": { "type": "string", "min_length": 1 },
    "timestamp": { "type": "string", "min_length": 1 }
  }
}
```

### Step 5: Add `_NO_GRAPH_IMPACT` entry in `src/gzkit/governance/trust_audits/events.py` (GREEN)

```python
"adr-evaluation": (
    "Full per-dimension evaluation scores (ADR-0.0.26-01). "
    "Consumed by eval-feedback-cluster chore and gz validate --evaluation-justify-binding; "
    "not a direct artifact graph node."
),
```

### Step 6: Wire emission in `src/gzkit/commands/adr_promote.py` (GREEN)

In `adr_eval_cmd`, after computing `result = evaluate_adr(project_root, adr_input)`:

```python
from gzkit.ledger_events import adr_evaluation_event  # noqa: PLC0415

# Build dimensions and scores maps from result
dimensions = {d.dimension: float(d.score) for d in result.adr_dimensions}
scores = {d.dimension: d.weighted for d in result.adr_dimensions}
challenges_fired = [
    r.challenge_name
    for r in (result.red_team_results or [])
    if not r.passed
]
ledger.append(
    adr_evaluation_event(
        artifact_id=adr_input,
        artifact_type="ADR",
        dimensions=dimensions,
        scores=scores,
        weighted_total=result.adr_weighted_total,
        red_team_challenges_fired=challenges_fired,
        evaluator_persona="gz-adr-evaluate",
        timestamp=result.timestamp,
    )
)
```

Emit this BEFORE the existing `adr_eval_completed_event` call; guard with try/except so a failure to build the new event does not suppress the existing summary event (fail-safe).

Actually: the brief says "A failed evaluation (validator error, malformed input) MUST NOT emit the event." This means the event should only be emitted when `evaluate_adr` succeeds. The current code only reaches the ledger append if `evaluate_adr` returns without raising. So no try/except needed — only emit after successful return from `evaluate_adr`.

### Step 7: Re-export from `src/gzkit/ledger.py` (GREEN)

Add `adr_evaluation_event` to the re-export block.

### Step 8: Verify (GREEN → stable)

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests/governance/test_evaluation_event.py tests/commands/test_adr_evaluate_emission.py -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_evaluation_event.py tests/commands/test_adr_evaluate_emission.py -v
```

## Notes

- `evaluator_persona`: static value `"gz-adr-evaluate"` — the evaluator tool identity. Not a human persona.
- Score range: existing `DimensionScore.score` is `int` 1–4 (not 0–5 as brief suggests). Schema uses `"type": "number"` without strict range enforcement — records what the evaluator produces, range is evaluator-dependent.
- No try/except around new emission — brief's "MUST NOT emit on failed evaluation" is enforced by natural code flow (emission only reached after `evaluate_adr` returns successfully).
- `dimensions` vs `scores`: `dimensions` maps name → raw score (1–4); `scores` maps name → weighted score. This interprets "scores" as the weighted contribution, "dimensions" as the raw per-dimension reading.
