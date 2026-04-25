# CHORE: Complexity Reduction (Xenon C/C/C Enforcement)

**Version:** 1.0.0
**Lane:** Lite
**Slug:** `complexity-reduction-xenon`

---

## Overview

Reduce cyclomatic complexity across `src/` to meet xenon C/C/C threshold (max-absolute C, max-modules C, max-average C).

## Policy and Guardrails

- **Lane:** Lite — internal refactoring, no external contract changes
- **Threshold:** `uvx xenon --max-absolute C --max-modules C --max-average C src/`
- Tidy-first: extract helpers, remove nesting, keep behavior unchanged
- Tests must stay green

## Workflow

### 1. Baseline

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/
```

### 2. Plan

- Tackle F-rank functions first, then E, then D
- Small batch (3-5 functions) per PR

### 3. Implement

Extract helpers, break complex functions into focused helpers.

### 4. Validate

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/
uv run -m unittest -q
```

## Checklist

- [ ] F-rank functions eliminated
- [ ] E-rank count reduced
- [ ] Xenon gate passes
- [ ] Tests pass unchanged

## Acceptance Criteria

| Type | Command | Expected |
|------|---------|----------|
| exitCodeEquals | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uvx xenon --max-absolute C --max-modules C --max-average C src/` | 0 |

## Evidence Commands

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/ > ops/chores/complexity-reduction-xenon/proofs/xenon-report.txt
```

---

**End of CHORE: Complexity Reduction (Xenon)**
