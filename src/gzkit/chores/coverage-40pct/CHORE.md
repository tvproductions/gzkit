# CHORE: Coverage >=40% Baseline

**Lane:** Lite
**Timeout:** 600s
**Slug:** `coverage-40pct`

---

## Overview

Periodic coverage audit to maintain >=40% line coverage floor.

## Policy and Guardrails

- **Lane:** Lite — coverage verification, no contract changes; unit-tier only, no behave/network
- **Timeout:** 600s — explicit per-chore `timeoutSeconds` calibrated to coverage instrumentation overhead (closes GHI #444; lane no longer carries duration per GHI #447). Raised from 300s under GHI #1027: the parallel coverage run measured 307 s on 2026-09-18, the serial one it replaced 493 s.
- Focus on high-ROI utility modules and public APIs
- Table-driven deterministic tests; <60s smoke budget

## Workflow

### 1. Measure — observe

```bash
uv run unittest-parallel -t . -s tests --buffer --coverage --coverage-source src/gzkit
uv run coverage report --fail-under=40
```

### 2. Identify High-ROI Targets — propose

Focus on modules with low coverage that have high public API surface.

### 3. Write Tests — repair

Table-driven, deterministic, no external dependencies.

### 4. Validate — observe

```bash
uv run gz test
uv run unittest-parallel -t . -s tests --buffer --coverage --coverage-source src/gzkit
uv run coverage report --fail-under=40
```

## Checklist

- [ ] Coverage >=40%
- [ ] Tests pass
- [ ] <60s smoke budget

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan coverage-40pct`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run unittest-parallel -t . -s tests --buffer --coverage --coverage-source src/gzkit
uv run coverage report > .gzkit/chores/coverage-40pct/proofs/coverage-report.txt
```

---

**End of CHORE: Coverage >=40% Baseline**
