# CHORE: Config Paths Remediation

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `config-paths-remediation`

---

## Overview

Remediate hard-coded paths in favor of config-driven resolution. All file paths should flow from the project configuration, not be scattered as string literals.

## Policy and Guardrails

- **Lane:** Lite — internal refactoring, no external contract changes
- All paths should be derived from config or `pathlib.Path` construction
- No hard-coded path separators (`/` or `\\`)
- Use `gz check-config-paths` to validate

## Workflow

### 1. Scan

```bash
uv run gz check-config-paths
```

### 2. Plan

Identify hard-coded paths and plan migration to config-driven resolution.

### 3. Implement

Replace string literals with config-driven path construction.

### 4. Validate

```bash
uv run gz check-config-paths
uv run -m unittest -q
```

## Checklist

- [ ] No hard-coded path strings
- [ ] Config paths validated
- [ ] Tests pass

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uv run gz check-config-paths` | 0 |

## Evidence Commands

```bash
uv run gz check-config-paths > ops/chores/config-paths-remediation/proofs/config-paths.txt
```

---

**End of CHORE: Config Paths Remediation**
