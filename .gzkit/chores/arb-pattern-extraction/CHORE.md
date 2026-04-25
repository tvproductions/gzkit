# CHORE: ARB Pattern Extraction (Code Style Feedback Loop)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `arb-pattern-extraction`

---

## Overview

Extract recurring anti-patterns from ARB receipts and output candidates for code style improvements. Feeds the lint/type/test feedback loop.

## Policy and Guardrails

- **Lane:** Lite — analysis only, no code changes
- Only processes receipts with findings (exit_status != 0)
- Requires 2+ occurrences to surface a pattern
- Output: Pattern candidates for review

## Workflow

### 1. Extract Patterns

```bash
uv run -m gzkit arb advise
```

### 2. Review

Assess patterns for actionability. Distinguish:
- **Auto-fixable:** Can be addressed with ruff --fix
- **Manual:** Require human judgment
- **Structural:** Need architecture discussion

### 3. Validate

```bash
uv run -m gzkit arb validate
uv run -m unittest -q
```

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |

## Evidence Commands

```bash
uv run -m gzkit arb advise > ops/chores/arb-pattern-extraction/proofs/arb-patterns.txt
```

---

**End of CHORE: ARB Pattern Extraction**
