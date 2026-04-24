# CHORE: Schema Drift / Config Drift Audit

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `schema-and-config-drift-audit`

---

## Overview

Audit settings/config usage to detect drift between schema definitions and actual usage patterns. Ensures config-first discipline.

## Policy and Guardrails

- **Lane:** Lite — audit and analysis, no contract changes
- Config-First: all settings should flow from project configuration
- Document drift findings before making changes

## Workflow

### 1. Baseline

```bash
uv run gz check-config-paths
uv run gz validate --documents --surfaces
```

### 2. Analyze

Compare schema definitions with actual config usage across the codebase.

### 3. Document

Record drift findings in proofs directory.

### 4. Validate

```bash
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uv run gz check-config-paths > ops/chores/schema-and-config-drift-audit/proofs/config-drift.txt
uv run gz validate --documents --surfaces > ops/chores/schema-and-config-drift-audit/proofs/validate-report.txt
```

---

**End of CHORE: Schema Drift / Config Drift Audit**
