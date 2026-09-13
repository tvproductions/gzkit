# CHORE: Test Manpage Examples (Executable Verification)

**Lane:** Heavy
**Slug:** `test-manpage-examples`

---

## Overview

Verify that examples in manpage EXAMPLES sections are executable with correct results. Ensures documentation examples actually work.

## Policy and Guardrails

- **Lane:** Heavy — external documentation contract
- Examples must be runnable on all platforms
- Exit codes must match documented expectations

## Workflow

### 1. Test

Run CLI audit to verify manpage coverage and structure.

```bash
uv run gz cli audit
```

### 2. Manual Verification

Execute example commands from manpages and verify output matches.

### 3. Validate

```bash
uv run gz cli audit
uv run -m unittest -q
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan test-manpage-examples`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz cli audit > .gzkit/chores/test-manpage-examples/proofs/cli-audit.txt
```

---

**End of CHORE: Test Manpage Examples**
