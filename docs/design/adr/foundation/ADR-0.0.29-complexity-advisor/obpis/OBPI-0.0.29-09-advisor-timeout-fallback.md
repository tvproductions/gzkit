---
id: OBPI-0.0.29-09-advisor-timeout-fallback
parent: ADR-0.0.29
item: 9
lane: Heavy
status: Completed
---

# OBPI-0.0.29-09-advisor-timeout-fallback: Pre-commit Timeout / Fallback / Failure-logging

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #9 — "Pre-commit timeout / fallback / failure-logging (default 30s; fail-open with log to `.gzkit/insights/advisor-failures.jsonl`)"

**Status:** Draft

## Objective

Implement the timeout primitive at `src/gzkit/complexity/advisor/timeout.py` consumed by OBPI-05's auto-chain hook. Default timeout is 30 seconds (configurable via `.gzkit/config`); on timeout the wrapper fails open (commit proceeds) with a logged warning at `.gzkit/insights/advisor-failures.jsonl`. The 2am Scenario-1 amelioration: the advisor never blocks an operator's commit indefinitely.

## Lane

**Heavy** — New runtime primitive consumed by the auto-chain hook; new failure-log surface; configurable timeout exposed via gzkit config. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/advisor/timeout.py` — `run_with_timeout(callable, timeout_s)` primitive + failure-log emission
- `src/gzkit/complexity/advisor/config.py` (or extend existing config surface) — `advisor_timeout_seconds` config key with 30s default
- `src/gzkit/insights/__init__.py` — extend insights module if needed for the new failure-log shape
- `src/gzkit/schemas/advisor_failure_log.json` — JSON Schema for failure-log entries
- `tests/complexity/advisor/test_timeout.py`
- `features/advisor_timeout.feature` — behave scenario tagged with REQ IDs
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces" describing timeout + log location
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-09-advisor-timeout-fallback.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is OBPI-01
- `src/gzkit/complexity/advisor/engine.py` — engine is OBPI-02
- `.gzkit/hooks/**` — auto-chain hook is OBPI-05 (consumes this primitive)
- `src/gzkit/commands/complexity_advise.py` — CLI is OBPI-03 (may also consume this primitive for its own timeout safety; that wiring lands here as a small additive change)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `run_with_timeout(callable: Callable[[], T], timeout_s: float, log_path: Path) -> TimeoutResult[T]` runs the callable with a hard timeout; on success returns `TimeoutResult.ok(value)`; on timeout returns `TimeoutResult.timed_out()` AND appends a JSONL entry to `log_path`.
2. REQUIREMENT: `TimeoutResult` is a frozen Pydantic union (or sealed dataclass-equivalent via Pydantic) with two variants: `ok(value: T)` and `timed_out(elapsed_s: float, callable_name: str)`. The caller (auto-chain hook, CLI) decides what to do based on the result; the primitive does not decide policy.
3. REQUIREMENT: The failure-log entries at `.gzkit/insights/advisor-failures.jsonl` follow a canonical JSONL schema: `{"timestamp": ISO8601, "callable_name": str, "timeout_s": float, "elapsed_s": float, "context": {file_paths: list[str], invocation: "auto-chain" | "ad-hoc"}}`.
4. REQUIREMENT: The default timeout is 30 seconds, configurable via the gzkit config key `advisor_timeout_seconds`. The config surface follows existing config conventions; no new config-loading machinery is introduced.
5. REQUIREMENT: The primitive uses stdlib `signal.SIGALRM` on POSIX OR a `threading.Timer`-based watchdog on Windows (per `.claude/rules/cross-platform.md`); the implementation is cross-platform. The primitive does NOT spawn subprocesses (the caller is already a subprocess in the hook context).
6. REQUIREMENT: Fail-open is the default policy at the primitive layer (`TimeoutResult.timed_out()` is returned, NOT raised); the caller decides whether to fail open or fail closed. The auto-chain hook's contract (OBPI-05) is to fail open with logged warning.
7. REQUIREMENT: Tests cover: callable completes within timeout returns `ok(value)`; callable exceeds timeout returns `timed_out` and logs entry; log entry validates against the JSON Schema; configurable timeout honored from config key; cross-platform tests run on Linux + macOS (Windows fixture is best-effort given CI constraints — registered in waiver if not feasible). Each test decorated with `@covers(REQ-0.0.29-09-NN)`.
8. REQUIREMENT: A behave scenario at `features/advisor_timeout.feature` tagged `@REQ-0.0.29-09-{02,03}` covers the timeout-and-log path.
9. REQUIREMENT: Runbook entry under "Complexity doctrine surfaces" documents the default timeout, the log location, the config override key, and the fail-open contract.
10. REQUIREMENT: Function-size discipline; the primitive ≤ 50 lines per function with named helpers (signal handler, log emitter, result construction).
11. REQUIREMENT: TDD discipline; `tempfile`-backed log fixtures.
12. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, runbook, or commit messages.

> STOP-on-BLOCKERS: if `.gzkit/insights/` directory convention is unclear (consult existing insights surfaces), reconcile before drafting.

## Discovery Checklist

**Prerequisites (check existence, STOP if missing):**

- [x] OBPI-03 CLI verb `gz complexity advise --auto-chain` flag registered
- [x] `.gzkit/insights/` directory exists with `agent-insights.jsonl` convention
- [x] Existing gzkit config surface at `src/gzkit/config.py` (`.gzkit.json` loader)
- [x] `.claude/rules/cross-platform.md` — POSIX signal vs Windows watchdog guidance

**Existing Code (understand current state):**

- [x] `src/gzkit/insights/__init__.py` — InsightRecord model; new failure-log is a sibling surface
- [x] `src/gzkit/config.py` — GzkitConfig with `extra="forbid"`; config reader uses raw JSON
- [x] `src/gzkit/complexity/advisor/engine.py` — diagnosis engine this timeout wraps
- [x] `.claude/rules/pythonic.md` — function-size ≤50 lines discipline
- [x] AGENTS.md § STDLIB-FIRST DOCTRINE — stdlib `signal` / `threading` confirmed

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Runbook entry

### Gate 4: BDD (Heavy)
- [ ] Behave scenario covers timeout-and-log path

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_timeout.py -v
uv run -m behave features/advisor_timeout.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.29-09-01: Given a callable that completes within 30s, when `run_with_timeout` runs, then `TimeoutResult.ok(value)` is returned and no log entry is appended.
- [ ] REQ-0.0.29-09-02: Given a callable that exceeds 30s, when `run_with_timeout` runs, then `TimeoutResult.timed_out` is returned and exactly one JSONL entry is appended to `.gzkit/insights/advisor-failures.jsonl`.
- [ ] REQ-0.0.29-09-03: Given a log entry, when validated against `src/gzkit/schemas/advisor_failure_log.json`, then validation passes; given a malformed entry, validation fails.
- [ ] REQ-0.0.29-09-04: Given the gzkit config key `advisor_timeout_seconds=10`, when the primitive is invoked without explicit timeout argument, then the 10s value is honored.
- [ ] REQ-0.0.29-09-05: Given the runbook, when read, then the default timeout, log location, config key, and fail-open contract are all documented.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean; size limits
- [ ] Gate 3: mkdocs --strict + runbook entry
- [ ] Gate 4: behave scenario passes
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict + runbook diff
```

### Gate 4 (BDD)
```text
# Paste behave output
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof


- `uv run -m unittest tests/complexity/advisor/test_timeout.py -v` — 14/14 pass (receipt `arb-step-unittest-dd377ad562b24c39b7177fa87c40f6c5`)
- `uv run -m behave features/advisor_timeout.feature` — 2/2 scenarios pass (receipt `arb-step-behave-b7aed86d1b0449feb6e2b3f2598a297f`)
- Lint clean (receipt `arb-ruff-3a3ad1f5e1944ca58d5240af122e86e8`), typecheck clean (receipt `arb-step-typecheck-0a78c47495d040debc8d031658c66251`)

### Implementation Summary


- Timeout primitive: `src/gzkit/complexity/advisor/timeout.py` — `run_with_timeout[T]()` with cross-platform implementation (POSIX `signal.SIGALRM`, Windows `threading.Timer`)
- Result model: discriminated `TimeoutOk | TimeoutTimedOut` frozen Pydantic union
- Config reader: `src/gzkit/complexity/advisor/config.py` — reads `advisor_timeout_seconds` from `.gzkit.json` (default 30s)
- Failure-log schema: `src/gzkit/schemas/advisor_failure_log.json` — canonical JSONL shape
- Tests: 14 unit tests with `@covers` decorators, 100% REQ coverage (5/5)
- BDD: 2 scenarios at `features/advisor_timeout.feature` tagged `@REQ-0.0.29-09-{02,03}`
- Docs: runbook entry documenting timeout, log location, config override, fail-open contract

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — timeout primitive implemented with TDD discipline: 14/14 unit tests + 2/2 BDD scenarios pass, 100% REQ coverage (5/5), cross-platform signal/threading implementation, configurable 30s default, JSONL failure-log emission, all ARB receipts green (lint: arb-ruff-3a3ad1f5e1944ca58d5240af122e86e8, typecheck: arb-step-typecheck-0a78c47495d040debc8d031658c66251, unittest: arb-step-unittest-dd377ad562b24c39b7177fa87c40f6c5, mkdocs: arb-step-mkdocs-53d4db926b944e869ca2bc1cafb75dce, behave: arb-step-behave-b7aed86d1b0449feb6e2b3f2598a297f)
- Date: 2026-05-07

---

**Brief Status:** Completed

**Date Completed:** 2026-05-07

**Evidence Hash:** -
