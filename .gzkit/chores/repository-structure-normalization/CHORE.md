# CHORE: Repository Structure Normalization

**Lane:** Lite
**Slug:** `repository-structure-normalization`

---

## Overview

Maintain consistent repository structure against the canonical layout. Structural repair with no functional changes.

## Policy and Guardrails

- **Lane:** Lite — structural verification, no behavioral changes
- Document deviations before remediating; remediation moves and creates, never rewrites content
- Validate against project config and governance surfaces

## Workflow

### 1. Baseline — observe

```bash
uv run gz validate --documents --surfaces
```

### 2. Analyze — propose

Document deviations from expected structure.

### 3. Remediate — repair

Fix structural issues (missing directories, misplaced files).

### 4. Validate — observe

```bash
uv run gz validate --documents --surfaces
uv run gz test
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan repository-structure-normalization`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz validate --documents --surfaces > .gzkit/chores/repository-structure-normalization/proofs/validate-report.txt
```

---

**End of CHORE: Repository Structure Normalization**
