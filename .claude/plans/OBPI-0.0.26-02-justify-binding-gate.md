# Plan: OBPI-0.0.26-02-justify-binding-gate

**OBPI:** `OBPI-0.0.26-02-justify-binding-gate`
**Parent ADR:** `ADR-0.0.26-evaluation-feedback-loop-doctrine`
**Lane:** Heavy — new validate scope, lifecycle gate

## Plan-Before-Exploration Disclosures (Step 6a)

**Destination-in-mind:** Before exploration I intended to add a new `evaluation_justify_binding.py`
module under the `trust_audits/` package, wiring it into `validate_cmd.py` following the
`sensitivity` scope pattern, and adding a lifecycle gate before `Pending` advancement.

**Rejected alternatives:**
1. Implementing as a hook — the brief requires `gz validate --evaluation-justify-binding` as the CLI surface.
2. Placing logic directly in `validate_cmd.py` — violates the trust_audits package separation pattern.
3. Hardcoding thresholds — explicitly rejected by REQ-05 (`data/eval_feedback_thresholds.json` required).
4. Running gate at ADR-closeout only — REQ-04 requires gate fires before advancing past `Pending` lifecycle state.

## Path Alignment Notes

The brief lists `src/gzkit/governance/trust_audits.py` but `trust_audits` is a package directory.
The implementation places the new function at
`src/gzkit/governance/trust_audits/evaluation_justify_binding.py`.

The brief lists `src/gzkit/commands/lifecycle.py` but the lifecycle state machine lives at
`src/gzkit/lifecycle.py`. The gate integration point is there.

## Files

- `data/eval_feedback_thresholds.json` — NEW threshold config
- `src/gzkit/governance/trust_audits/evaluation_justify_binding.py` — NEW validator module
- `src/gzkit/governance/trust_audits/__init__.py` — add re-export
- `src/gzkit/commands/validate_cmd.py` — add scope flag + dispatch
- `src/gzkit/cli/parser_artifacts.py` — register `--evaluation-justify-binding` flag
- `src/gzkit/lifecycle.py` — call gate before advancing past Pending
- `tests/governance/test_justify_binding_gate.py` — NEW test module

## Steps

### Step 1 — Create threshold config

Create `data/eval_feedback_thresholds.json`:
```json
{
  "low_score_threshold": 3.0,
  "red_team_count_threshold": 3
}
```

### Step 2 — Write failing tests (TDD RED)

Create `tests/governance/test_justify_binding_gate.py`.

Test class `TestEvaluationJustifyBindingGate` with:
- `test_low_score_no_justify_artifact_exits_3` — one dimension score < 3.0, no justify artifact → ValidationError returned (exit 3)
- `test_red_team_count_no_justify_artifact_exits_3` — ≥3 red_team_challenges_fired, no justify artifact → ValidationError
- `test_trigger_fires_justify_artifact_present_exits_0` — trigger condition met, qualify justify artifact at `artifacts/justify/<id>*.md` → empty list
- `test_no_trigger_all_scores_high_exits_0` — all dimensions ≥ 3.0, < 3 red-team fires → empty list (no gate)
- `test_threshold_config_reflected` — update threshold to 4.0, same scores that previously passed now fail

All tests use `tempfile`-backed ledger fixture (write `adr-evaluation` events directly without touching `.gzkit/ledger.jsonl`).
All tests decorate test methods with `@covers("REQ-0.0.26-02-NN")`.

### Step 3 — Implement `validate_evaluation_justify_binding`

New file `src/gzkit/governance/trust_audits/evaluation_justify_binding.py`:

```python
def validate_evaluation_justify_binding(
    artifact_id: str,
    project_root: Path,
    *,
    ledger_path: Path | None = None,
) -> list[ValidationError]:
    """Fail-closed gate: require gz-justify artifact when evaluation scores are low."""
```

Logic:
1. Load `data/eval_feedback_thresholds.json` for `low_score_threshold` and `red_team_count_threshold`
2. Read ledger (default `project_root / ".gzkit" / "ledger.jsonl"`), find most recent `adr-evaluation` event for `artifact_id`
3. If no event → return [] (no trigger; no evaluation has run)
4. Check: any dimension score < `low_score_threshold` OR `len(red_team_challenges_fired) >= red_team_count_threshold`
5. If trigger fires: scan `project_root / "artifacts" / "justify"` for files matching `<artifact-id>*`
6. If no qualifying file: return ValidationError with type `"evaluation-justify-binding"`, naming the failing dimensions and the missing artifact path
7. If file found or no trigger: return []

### Step 4 — Export from trust_audits `__init__.py`

Add import:
```python
from gzkit.governance.trust_audits.evaluation_justify_binding import (
    validate_evaluation_justify_binding,
)
```
Add `"validate_evaluation_justify_binding"` to `__all__`.

### Step 5 — Register `--evaluation-justify-binding` in `parser_artifacts.py`

Add `--evaluation-justify-binding` argument to the validate parser, following the `--sensitivity` pattern:
```python
validate_parser.add_argument(
    "--evaluation-justify-binding",
    nargs="?",
    const="__all__",
    metavar="ARTIFACT_ID",
    help="Verify gz-justify artifact exists when evaluation scores are low (exit 3 on miss).",
)
```

### Step 6 — Wire scope into `validate_cmd.py`

1. Add `check_evaluation_justify_binding: str | None = None` to the `validate_all_checks` function signature.
2. Add `"evaluation_justify_binding": check_evaluation_justify_binding is not None` to `explicit_scopes`.
3. Add runner to `_explicit_scope_runners`:
   ```python
   "evaluation_justify_binding": lambda: _evaluation_justify_binding_runner(
       project_root, check_evaluation_justify_binding
   ),
   ```
4. Add `"evaluation_justify_binding"` to `opt_in_scopes` list.
5. Implement `_evaluation_justify_binding_runner(project_root, artifact_id_or_sentinel)`:
   - If `artifact_id_or_sentinel == "__all__"`: scan all artifacts with adr-evaluation events
   - Else: call `trust_audits.validate_evaluation_justify_binding(artifact_id, project_root)`

### Step 7 — Wire gate into lifecycle advancement

In `src/gzkit/lifecycle.py`, in the `LifecycleStateMachine.advance(...)` method (or wherever the lifecycle transition is validated), before allowing transition from Draft/Pending to the next state:

```python
from gzkit.governance.trust_audits.evaluation_justify_binding import (
    validate_evaluation_justify_binding,
)
# ...
gate_errors = validate_evaluation_justify_binding(artifact_id, project_root)
if gate_errors:
    raise GatingError(gate_errors[0].message)
```

### Step 8 — Run tests (TDD GREEN)

```bash
uv run -m unittest tests/governance/test_justify_binding_gate.py -v
```

All tests must pass. Fix implementation until green.

### Step 9 — Run quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

### Step 10 — Present OBPI Acceptance Ceremony

Present Stage 4 evidence per gz-obpi-pipeline skill template.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_justify_binding_gate.py -v
uv run gz validate --evaluation-justify-binding ADR-0.0.26
```

## Notes

- `adr-evaluation` event payload confirmed: `{artifact_id, artifact_type, dimensions, scores, weighted_total, red_team_challenges_fired, evaluator_persona, timestamp}` — where `dimensions` is a map of dimension-name → score (0.0–5.0).
- `gz-justify` writes artifacts to `artifacts/justify/<slug>-<timestamp>.md` (confirmed from gz-justify SKILL.md line 77).
- No existing `adr-evaluation` events in ledger yet (OBPI-01 landed the emission code; no evaluations have been run since).
- The `trust_audits` brief path drift (`trust_audits.py` vs package dir) is advisory — scoped to this implementation.
