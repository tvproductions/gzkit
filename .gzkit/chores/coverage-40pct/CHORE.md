# CHORE: Coverage >=40% Baseline

**Version:** 1.1.0
**Lane:** Lite
**Timeout:** 300s
**Slug:** `coverage-40pct`

---

## Overview

Periodic coverage audit to maintain >=40% line coverage floor.

## Policy and Guardrails

- **Lane:** Lite — coverage verification, no contract changes; unit-tier only, no behave/network
- **Timeout:** 300s — explicit per-chore `timeoutSeconds` calibrated to coverage instrumentation overhead (closes GHI #444; lane no longer carries duration per GHI #447)
- Focus on high-ROI utility modules and public APIs
- Table-driven deterministic tests; <60s smoke budget

## Workflow

### 1. Measure

```bash
uv run coverage run -m unittest discover -s tests -t . -q
uv run coverage report --fail-under=40
```

### 2. Identify High-ROI Targets

Focus on modules with low coverage that have high public API surface.

### 3. Write Tests

Table-driven, deterministic, no external dependencies.

### 4. Validate

```bash
uv run -m unittest -q
uv run coverage run -m unittest discover -s tests -t . -q
uv run coverage report --fail-under=40
```

## Checklist

- [ ] Coverage >=40%
- [ ] Tests pass
- [ ] <60s smoke budget

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uv run coverage run -m unittest discover -s tests -t . -q` | 0 |
| exitCodeEquals | `uv run coverage report --fail-under=40` | 0 |

## Evidence Commands

```bash
uv run coverage run -m unittest discover -s tests -t . -q
uv run coverage report > .gzkit/chores/coverage-40pct/proofs/coverage-report.txt
```

---

**End of CHORE: Coverage >=40% Baseline**
