# Plan: OBPI-0.0.29-09 — Pre-commit Timeout / Fallback / Failure-logging

## Context

OBPI-0.0.29-09 implements the timeout primitive consumed by OBPI-05's auto-chain
hook. The primitive wraps a callable with a configurable timeout (default 30s),
returns a discriminated result type, and logs failures to
`.gzkit/insights/advisor-failures.jsonl`. It uses stdlib `signal.SIGALRM` on
POSIX and `threading.Timer` on Windows. The primitive itself is policy-free —
callers decide whether to fail open or closed based on the result.

**Parent ADR:** ADR-0.0.29 (Complexity Advisor)
**Lane:** Heavy | **Kind:** foundation
**OBPI slug:** OBPI-0.0.29-09-advisor-timeout-fallback

## Files

### Create

- `src/gzkit/complexity/advisor/timeout.py` — `run_with_timeout()` + `TimeoutResult`
- `src/gzkit/complexity/advisor/config.py` — `get_advisor_timeout_seconds()` config reader
- `src/gzkit/schemas/advisor_failure_log.json` — JSON Schema for failure-log entries
- `tests/complexity/advisor/test_timeout.py` — unit tests with `@covers` decorators
- `features/advisor_timeout.feature` — BDD scenarios tagged `@REQ-0.0.29-09-{02,03}`

### Modify

- `src/gzkit/insights/__init__.py` — export failure-log model if needed
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"

## Steps

### Step 1: TDD RED — Test scaffolding

Create `tests/complexity/advisor/test_timeout.py` with failing tests:

- `test_callable_completes_within_timeout_returns_ok` — `@covers("REQ-0.0.29-09-01")`
- `test_callable_exceeds_timeout_returns_timed_out` — `@covers("REQ-0.0.29-09-01")`
- `test_timed_out_result_logs_entry_to_jsonl` — `@covers("REQ-0.0.29-09-03")`
- `test_log_entry_validates_against_schema` — `@covers("REQ-0.0.29-09-03")`
- `test_configurable_timeout_from_config_key` — `@covers("REQ-0.0.29-09-04")`
- `test_timeout_result_ok_is_frozen` — `@covers("REQ-0.0.29-09-02")`
- `test_timeout_result_timed_out_is_frozen` — `@covers("REQ-0.0.29-09-02")`
- `test_default_timeout_30s` — `@covers("REQ-0.0.29-09-04")`
- `test_no_subprocess_spawned` — `@covers("REQ-0.0.29-09-05")`
- `test_function_size_under_50_lines` — `@covers("REQ-0.0.29-09-10")`

All tests use `tempfile`-backed fixtures for log paths. Tests import from
`gzkit.complexity.advisor.timeout` (which doesn't exist yet → RED).

### Step 2: Implement `TimeoutResult` model

In `src/gzkit/complexity/advisor/timeout.py`:

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Generic, TypeVar, Literal

T = TypeVar("T")

class TimeoutOk(BaseModel, Generic[T]):
    model_config = ConfigDict(frozen=True, extra="forbid")
    status: Literal["ok"] = "ok"
    value: T = Field(..., description="Return value of the callable")

class TimeoutTimedOut(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    status: Literal["timed_out"] = "timed_out"
    elapsed_s: float = Field(..., description="Elapsed seconds before timeout")
    callable_name: str = Field(..., description="Name of the timed-out callable")

TimeoutResult = TimeoutOk[T] | TimeoutTimedOut
```

### Step 3: Implement `run_with_timeout()`

In the same file, implement the core primitive:

- Accept `callable: Callable[[], T]`, `timeout_s: float`, `log_path: Path`
- Platform detection: `os.name == "nt"` → threading path; else → signal path
- POSIX: set `signal.alarm(timeout_s)`, run callable, clear alarm
- Windows: start `threading.Timer`, run callable, cancel timer
- On timeout: construct `TimeoutTimedOut`, emit log entry, return result
- On success: return `TimeoutOk(value=result)`
- Named helpers: `_run_with_signal()`, `_run_with_timer()`, `_emit_failure_log()`
- Each function ≤50 lines

### Step 4: Implement config reader

Create `src/gzkit/complexity/advisor/config.py`:

- `get_advisor_timeout_seconds(config_path: Path | None = None) -> float`
- Reads `.gzkit.json`, extracts `advisor_timeout_seconds` key (top-level)
- Returns 30.0 if key absent or file missing
- No new config machinery — just reads the JSON directly with `json.loads`

### Step 5: Implement failure-log schema

Create `src/gzkit/schemas/advisor_failure_log.json`:

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "title": "AdvisorFailureLogEntry",
  "type": "object",
  "required": ["timestamp", "callable_name", "timeout_s", "elapsed_s", "context"],
  "properties": {
    "timestamp": { "type": "string", "format": "date-time" },
    "callable_name": { "type": "string" },
    "timeout_s": { "type": "number" },
    "elapsed_s": { "type": "number" },
    "context": {
      "type": "object",
      "required": ["file_paths", "invocation"],
      "properties": {
        "file_paths": { "type": "array", "items": { "type": "string" } },
        "invocation": { "enum": ["auto-chain", "ad-hoc"] }
      }
    }
  },
  "additionalProperties": false
}
```

### Step 6: TDD GREEN — Tests pass

Run `uv run -m unittest tests/complexity/advisor/test_timeout.py -v`.
Fix any failures. Ensure lint/type clean after.

### Step 7: BDD — Behave scenarios

Create `features/advisor_timeout.feature`:

- `@REQ-0.0.29-09-02` Scenario: callable times out and result carries elapsed_s + callable_name
- `@REQ-0.0.29-09-03` Scenario: timeout logs failure entry to advisor-failures.jsonl

Step implementations in `features/steps/` (reuse existing step patterns).

### Step 8: Docs — Runbook entry

Add entry to `docs/user/runbook.md` under "Complexity doctrine surfaces":

- Default timeout: 30s
- Config override: `advisor_timeout_seconds` key in `.gzkit.json`
- Log location: `.gzkit/insights/advisor-failures.jsonl`
- Fail-open contract: timeout never blocks; commit proceeds with logged warning

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_timeout.py -v
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/advisor_timeout.feature
```

## Notes

- The `GzkitConfig` model has `extra="forbid"` — the config reader reads `.gzkit.json`
  raw JSON and extracts the key independently, avoiding a model change outside
  allowed paths. When a future OBPI adds `advisor_timeout_seconds` to `GzkitConfig`
  proper, the reader becomes a thin wrapper. This is not new machinery — it's one
  `json.loads` + `.get()` call.
- The primitive does NOT decide policy. `TimeoutResult` is returned to callers.
  OBPI-05's hook will call `run_with_timeout()` and choose to fail open on
  `timed_out` status. Other callers could choose differently.
- Generic Pydantic models (`TimeoutOk[T]`) may require `__class_getitem__` handling
  for runtime use vs. type-checking use. If Pydantic generics prove friction,
  fall back to `value: Any` with a type annotation comment — the brief says
  "sealed dataclass-equivalent via Pydantic" which permits simplification.
