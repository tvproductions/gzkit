# CHORE: Validate Manpages (Call Stack Alignment)

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

### 1. Validate — observe

```bash
uv run gz cli audit
```

### 2. Fix — repair

Update manpage traces to match current code structure.

### 3. Re-validate — observe

```bash
uv run gz cli audit
uv run gz test
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan validate-manpages`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz cli audit > .gzkit/chores/validate-manpages/proofs/cli-audit.txt
```

---

**End of CHORE: Validate Manpages**
