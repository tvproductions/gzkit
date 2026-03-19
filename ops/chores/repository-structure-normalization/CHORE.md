# CHORE: Repository Structure Normalization

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `repository-structure-normalization`

---

## Overview

Maintain consistent repository structure against the canonical layout. Structural audit with no functional changes.

## Policy and Guardrails

- **Lane:** Lite — structural verification, no behavioral changes
- Audit only; document deviations before making changes
- Validate against project config and governance surfaces

## Workflow

### 1. Baseline

```bash
uv run gz validate --documents --surfaces
```

### 2. Analyze

Document deviations from expected structure.

### 3. Remediate

Fix structural issues (missing directories, misplaced files).

### 4. Validate

```bash
uv run gz validate --documents --surfaces
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uv run gz validate --documents --surfaces` | 0 |

## Evidence Commands

```bash
uv run gz validate --documents --surfaces > ops/chores/repository-structure-normalization/proofs/validate-report.txt
```

---

**End of CHORE: Repository Structure Normalization**
