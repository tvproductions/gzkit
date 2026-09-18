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

### 1. Run Audit — observe

```bash
uv run gz adr audit-check ADR-<X.Y.Z>
```

### 2. Save Evidence — observe

Record findings in proofs directory.

### 3. Assess and recommend — propose

Review findings for consistency and completeness, and recommend a disposition per finding:

- **Evidence proved invalid** — the operator considers `gz obpi repudiate --cause verification-invalid`
- **Receipt missing or stale** — the operator re-emits it (`gz adr emit-receipt`)
- **Cosmetic** — none

Briefs are sealed records and OBPI briefs are operator-only; this chore recommends and never acts.

### 4. Validate — observe

```bash
uv run gz test
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan evidence-integrity-audit`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
uv run gz status --table > .gzkit/chores/evidence-integrity-audit/proofs/status-report.txt
```

---

**End of CHORE: OBPI Evidence Integrity Audit**
