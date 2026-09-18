# CHORE: Config Paths Remediation

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

### 1. Scan — observe

```bash
uv run gz check-config-paths
```

### 2. Plan — propose

Identify hard-coded paths and plan migration to config-driven resolution.

### 3. Implement — repair

Replace string literals with config-driven path construction.

### 4. Validate — observe

```bash
uv run gz check-config-paths
uv run gz test
```

## Checklist

- [ ] No hard-coded path strings
- [ ] Config paths validated
- [ ] Tests pass

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan config-paths-remediation`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz check-config-paths > .gzkit/chores/config-paths-remediation/proofs/config-paths.txt
```

---

**End of CHORE: Config Paths Remediation**
