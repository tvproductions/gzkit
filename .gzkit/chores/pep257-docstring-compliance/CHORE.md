# CHORE: PEP 257 Docstring Compliance (Style + Coverage)

**Lane:** Lite
**Slug:** `pep257-docstring-compliance`

---

## Overview

Enforce PEP 257 docstring compliance across `src/gzkit/` using interrogate (>=85% coverage) and ruff D-series rules.

## Policy and Guardrails

- **Lane:** Lite — documentation quality, no external contract changes
- **Coverage target:** 85% via interrogate
- **Style:** ruff D-series (D100-D418) for PEP 257 compliance

## Workflow

### 1. Baseline

```bash
uvx interrogate -v -c pyproject.toml src/gzkit
uvx ruff check src/gzkit --select D
```

### 2. Plan

Prioritize public API docstrings, then internal modules.

### 3. Implement

Add missing docstrings, fix style violations.

### 4. Validate

```bash
uvx interrogate -v -f 85 -c pyproject.toml src/gzkit
uvx ruff check src/gzkit --select D
```

## Checklist

- [ ] interrogate coverage >=85%
- [ ] ruff D-series clean
- [ ] Tests pass unchanged

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan pep257-docstring-compliance`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uvx interrogate -v -c pyproject.toml src/gzkit > .gzkit/chores/pep257-docstring-compliance/proofs/interrogate-report.txt
uvx ruff check src/gzkit --select D > .gzkit/chores/pep257-docstring-compliance/proofs/ruff-d-report.txt
```

---

**End of CHORE: PEP 257 Docstring Compliance**
