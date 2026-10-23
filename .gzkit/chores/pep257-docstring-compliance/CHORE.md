# CHORE: PEP 257 Docstring Compliance

**Lane:** Lite
**Slug:** `pep257-docstring-compliance`

> **Version 2.0.0 (2026-10-22, RO-9 tranche 4, GHI #1183):** interrogate is
> retired. Ruff's D-series is the one docstring gate: D100-D107 require a
> docstring on every public module, class, function and method in
> `src/gzkit/`, and the rest of the series checks PEP 257 style. The coverage
> percentage interrogate reported over private functions as well (89% on
> 2026-10-22) is no longer measured.

---

## Overview

Enforce PEP 257 docstring compliance across `src/gzkit/` with ruff's D-series rules.

## Policy and Guardrails

- **Lane:** Lite — documentation quality, no external contract changes
- **Presence:** D100-D107, every public module, class, function and method
- **Style:** the rest of the D-series (D200-D418) for PEP 257 compliance

## Workflow

### 1. Baseline — observe

```bash
uv run ruff check src/gzkit --select D --statistics
```

### 2. Plan — propose

Prioritize public API docstrings, then internal modules.

### 3. Implement — repair

Add missing docstrings, fix style violations.

### 4. Validate — observe

```bash
uv run ruff check src/gzkit --select D
```

## Checklist

- [ ] ruff D-series clean
- [ ] Tests pass unchanged

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan pep257-docstring-compliance`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run ruff check src/gzkit --select D > .gzkit/chores/pep257-docstring-compliance/proofs/ruff-d-report.txt
```

---

**End of CHORE: PEP 257 Docstring Compliance**
