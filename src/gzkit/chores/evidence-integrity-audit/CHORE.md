# CHORE: OBPI Evidence Integrity Audit

**Lane:** Lite
**Slug:** `evidence-integrity-audit`

---

## Overview

Cross-reference OBPI brief evidence claims against actual state. Verify that evidence sections in briefs are consistent and complete. Produces a structured audit report.

## Policy and Guardrails

- **Lane:** Lite — read-only audit, no side effects
- Scope: All Completed/Validated OBPIs
- Does not modify briefs or any files
- Output: Report artifact saved to `proofs/`

## Workflow

### 1. Run Audit

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
```

### 2. Save Evidence

Record findings in proofs directory.

### 3. Assess

Review findings for consistency and completeness.

### 4. Validate

```bash
uv run -m unittest -q
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan evidence-integrity-audit`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz status --table > .gzkit/chores/evidence-integrity-audit/proofs/status-report.txt
```

---

**End of CHORE: OBPI Evidence Integrity Audit**
