# Plan: OBPI-0.25.0-20 ADR Governance Pattern

## Context

OBPI-0.25.0-20 compares airlineops's `adr_governance.py` (535 lines — evidence audit, autolink, verification report) against gzkit's equivalent governance surface (`traceability.py` + `commands/covers.py` + `commands/adr_audit.py`, ~1010 lines). The task is to decide: Absorb, Confirm, or Exclude.

**Recommended decision: Confirm.** gzkit's surface is architecturally superior across all three capabilities — AST-based parsing vs regex, multi-level coverage rollups vs flat mapping, central ledger graph vs local files, brief content inspection vs section-presence checks, Pydantic models vs stdlib dataclass.

## Steps

### 1. Create confirmation test file (Gate 2 — Red first)

**File:** `tests/test_adr_governance_confirm.py`

Four tests in a single `unittest.TestCase`:
- `test_scan_test_tree_importable` → `@covers("REQ-0.25.0-20-01")` — AST-based scanning exists
- `test_compute_coverage_importable` → `@covers("REQ-0.25.0-20-02")` — multi-level rollups exist
- `test_adr_audit_check_importable` → `@covers("REQ-0.25.0-20-02")` — evidence audit exists
- `test_confirm_decision_no_absorption_needed` → `@covers("REQ-0.25.0-20-04")` — enumerate surface superiority

Pattern: follow the prior confirmation test file exactly.

### 2. Update the OBPI-20 brief (Gate 3 — Docs)

**File:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-20-adr-governance-pattern.md`

Add these sections (following the prior completed brief format):
- **Comparison Analysis** — subsections for airlineops (3 capabilities), gzkit (3 modules table), dimension comparison table
- **DECISION: Confirm** — with 5-point Rationale (parsing fidelity, coverage depth, evidence audit, convention compliance, auto-writing is workflow-specific)
- **Gate 4 (BDD): N/A** — no operator-visible behavior change
- **Implementation Summary** — bullet-point recap
- **Key Proof** — test command + expected output
- **Closing Argument** — single dense paragraph

### 3. Verify

```bash
uv run -m unittest tests/test_adr_governance_confirm.py -v
uv run gz lint
uv run gz typecheck
uv run gz test
```

## Critical Files

| File | Action |
|------|--------|
| `tests/test_adr_governance_confirm.py` | Create (4 tests) |
| `docs/.../obpis/OBPI-0.25.0-20-adr-governance-pattern.md` | Edit (add comparison + decision) |
| `tests/test_adr_audit_ledger_confirm.py` | Reference pattern only |
| Prior completed brief (item 19) | Reference pattern only |
