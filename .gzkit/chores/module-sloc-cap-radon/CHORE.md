# CHORE: Module SLOC Cap (Radon)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `module-sloc-cap-radon`

---

## Overview

Enforce module size limits using radon. Hard cap: <=1000 SLOC. Soft cap: <=600 SLOC per the pythonic standards policy.

## Policy and Guardrails

- **Lane:** Lite — internal structural refactoring, no external contract changes
- No behavioral changes; public imports via `__init__.py` re-exports
- Split by cohesion, not by arbitrary line count

## Workflow

### 1. Baseline

```bash
uvx radon raw src/ -s -j > ops/chores/module-sloc-cap-radon/proofs/radon-baseline.json
```

### 2. Plan

- Identify modules exceeding 600 SLOC soft cap
- Plan cohesive splits preserving public API

### 3. Implement

Split modules by responsibility. Maintain backwards-compatible imports.

### 4. Validate

```bash
uv run -m unittest -q
uvx radon raw src/ -s -j
```

## Checklist

- [ ] No modules exceed 1000 SLOC hard cap
- [ ] Modules approaching 600 SLOC documented
- [ ] Tests pass unchanged

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uvx radon raw src/ -s -j > ops/chores/module-sloc-cap-radon/proofs/radon-report.json
```

---

**End of CHORE: Module SLOC Cap (Radon)**
