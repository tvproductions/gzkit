# CHORE: Test Isolation & Health Compliance

**Lane:** Lite
**Slug:** `test-isolation-compliance`

---

## Overview

Guard test suite isolation, performance, and output cleanliness. Catches:
- Tests leaking to real files instead of temp dirs
- Slow tests (>3s) and a smoke tier over its budget
- Noisy stdout leaks (Rich console, CLI output)

## Policy and Guardrails

- **Lane:** Lite — analysis + targeted fixes, no external contract changes
- Thresholds are hardcoded in the profiler; adjust as suite grows
- Do not add `sleep` or `time.time()` hacks to mask slow tests — fix the root cause

## Thresholds

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| Smoke tier | within the budget `uv run gz smoke` enforces | `.gzkit/rules/tests.md` § General Rules: the budget binds the `@smoke` subset; the full unit tier has no fixed ceiling, so the profiler reports its wall clock and never gates it |
| Slowest single test | <3s | Any test >3s has a design problem |
| Stdout noise lines | 0 | Tests should produce dots only |

## Workflow

### 1. Profile — observe

Run the health profiler to check all thresholds at once:

```bash
uv run python tests/tools/test_health_profiler.py
```

This produces a JSON report at `.gzkit/chores/test-isolation-compliance/proofs/health-report.json`.

### 2. Diagnose — propose

For each violation, identify the root cause category:

| Symptom | Typical cause | Fix pattern |
|---------|---------------|-------------|
| Single test >3s | git clone, `uv sync`, full repo scan | Mock/fixture/`setUpClass` |
| Module >5s total | `setUp` runs expensive ops per test | Template + `copytree` or `setUpClass` |
| Stdout noise | Rich `console.print` leaking | Patch console with `Console(file=StringIO())` |
| Slow subprocess churn | `git init` + config per test | Shared template repo |
| Repeated CLI invocation | Same command in N tests | Run once in `setUpClass`, share result |
| Real file mutation | `get_project_root()` returns CWD | Mock project root to temp dir |
| No temp dir isolation | Direct file writes | `tempfile.TemporaryDirectory()` context manager |

### 3. Fix — repair

Apply the lightest fix that addresses the root cause. Prefer:
1. `setUpClass` sharing over per-test setup
2. Template + copy over regeneration
3. Console patching over output capture hacks
4. `commit=False` / skipping git where Draft-only validation doesn't need it
5. Context managers for all temp resources (Windows-safe cleanup)

### 4. Validate — observe

```bash
uv run python tests/tools/test_health_profiler.py
uv run gz smoke
uv run -m unittest -q
```

## Checklist

- [ ] No tests use persistent file paths
- [ ] No tests touch production databases
- [ ] All temp resources cleaned via context managers
- [ ] No single test >3s
- [ ] Smoke tier within budget (`uv run gz smoke` exits 0)
- [ ] Zero stdout noise lines
- [ ] Tests pass

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan test-isolation-compliance`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run python tests/tools/test_health_profiler.py
```

---

**End of CHORE: Test Isolation & Health Compliance**
