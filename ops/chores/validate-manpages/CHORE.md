# CHORE: Validate Manpages (Call Stack Alignment)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `validate-manpages`

---

## Overview

Validate that manpage IMPLEMENTATION TRACE references match actual functions in the codebase. Ensures manpages reflect the real code structure.

## Policy and Guardrails

- **Lane:** Lite — documentation verification, no contract changes
- Every function referenced in a manpage trace must exist in the codebase
- Uses `gz cli audit` for comprehensive CLI documentation validation

## Workflow

### 1. Validate

```bash
uv run gz cli audit
```

### 2. Fix

Update manpage traces to match current code structure.

### 3. Re-validate

```bash
uv run gz cli audit
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run gz cli audit` | 0 |

## Evidence Commands

```bash
uv run gz cli audit > ops/chores/validate-manpages/proofs/cli-audit.txt
```

---

**End of CHORE: Validate Manpages**
