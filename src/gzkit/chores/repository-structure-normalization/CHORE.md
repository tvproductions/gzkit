# CHORE: Repository Structure Normalization

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

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan repository-structure-normalization`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz validate --documents --surfaces > .gzkit/chores/repository-structure-normalization/proofs/validate-report.txt
```

---

**End of CHORE: Repository Structure Normalization**
