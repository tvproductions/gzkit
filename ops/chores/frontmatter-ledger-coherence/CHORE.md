# CHORE: Frontmatter-Ledger Coherence Audit

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `frontmatter-ledger-coherence`

---

## Overview

Validate that YAML frontmatter fields (`id`, `parent`, `lane`) in ADR and OBPI
files match the ledger's artifact graph. Frontmatter is a derived cache of
ledger truth; this chore detects drift.

## Policy and Guardrails

- **Lane:** Lite — read-only validation, no mutations
- **Tool:** `gz validate --frontmatter` compares every on-disk artifact's
  frontmatter against the ledger's artifact graph
- **Authority:** The ledger is the source of truth. When drift is found, the
  ledger value is correct and the frontmatter value is stale.
- **Related GHIs:** #167 (umbrella), #168, #169, #170

## Workflow

### 1. Run validation

```bash
uv run gz validate --frontmatter
```

### 2. Interpret results

Each error names the drifted file, field, frontmatter value, and ledger value.

### 3. Fix drift (when errors found)

For each drifted file, update the frontmatter field to match the ledger value.
The ledger always wins.

```bash
# Confirm ledger value for a specific artifact
uv run gz state --json | python -m json.tool
```

### 4. Re-validate

```bash
uv run gz validate --frontmatter
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz validate --frontmatter` | 0 |

## Evidence Commands

```bash
uv run gz validate --frontmatter --json > ops/chores/frontmatter-ledger-coherence/proofs/validation.json
```

---

**End of CHORE: Frontmatter-Ledger Coherence Audit**
