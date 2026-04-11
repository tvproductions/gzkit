# Plan: OBPI-0.25.0-19 — ADR Audit Ledger Pattern

## Context

OBPI-0.25.0-19 evaluates `airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines) against
gzkit's audit ledger surface. The airlineops module is a Layer 2 Gate 5 completeness checker that
reads an ADR-local `obpi-audit.jsonl` ledger to determine if all OBPIs have passing proof. gzkit's
equivalent functionality is distributed across 3 modules totaling ~800+ lines.

## Decision: Confirm

gzkit's audit surface already surpasses what the airlineops module provides.

### Comparison Summary

| Dimension | airlineops | gzkit |
|-----------|-----------|-------|
| Purpose | Gate 5 pre-attestation completeness | Same, plus REQ traceability |
| Data source | ADR-local `obpi-audit.jsonl` | Central ledger graph + brief inspection |
| Result model | `LedgerCheckResult` (stdlib dataclass) | Dict-based + Rich console |
| Completeness check | missing/incomplete/complete classification | findings-based (gaps vs complete) |
| REQ coverage | Not present | `@covers` annotation verification |
| Lines | 249 | ~800+ (broader scope) |

### Why Confirm (not Absorb)

1. **Architecture**: gzkit reads the central ledger graph (State Doctrine L1/L2), not a local audit
   JSONL file. This is architecturally superior — single source of truth.
2. **Evidence depth**: gzkit's `_inspect_obpi_brief()` checks brief file content (Implementation
   Summary, Key Proof, Human Attestation sections), not just ledger status values.
3. **REQ traceability**: `adr_audit_check()` also verifies `@covers` annotations — a dimension
   airlineops doesn't check at all.
4. **Convention compliance**: airlineops uses stdlib `dataclass` (violates gzkit model policy).
   Absorbing would require a full rewrite to Pydantic, defeating the purpose.
5. **Dependency isolation**: airlineops module depends on `adr_recon` helpers. gzkit has its own
   ADR resolution (`resolve_adr_file`, `resolve_adr_ledger_id`, ledger graph queries).

## Implementation Steps

### Step 1: Update OBPI brief with comparison and decision

File: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-19-adr-audit-ledger-pattern.md`

- Update frontmatter `status: Pending` to `status: In Progress`
- Add `## Comparison Analysis` section documenting the dimension-by-dimension comparison
- Record `## Decision: Confirm` section with the rationale above
- Add `## Gate 4 (BDD): N/A` — no operator-visible behavior change (Confirm outcome)
- Populate the Closing Argument from delivered evidence

### Step 2: Write a confirmation test

File: `tests/test_obpi_0_25_0_19_adr_audit_ledger.py`

Write a minimal test that confirms gzkit's audit surface covers the airlineops module's
capabilities. Test will:
- Verify `adr_audit_check` function exists and is importable
- Verify `validate_ledger` function exists and is importable
- Verify `obpi_audit_cmd` function exists and is importable
- Use `@covers("OBPI-0.25.0-19")` decorator

### Step 3: Run verification

```bash
uv run gz test
uv run gz lint
uv run gz typecheck
```

## Key Files

- airlineops source: `../airlineops/src/opsdev/lib/adr_audit_ledger.py`
- gzkit audit-check: `src/gzkit/commands/adr_audit.py` (lines 59-158)
- gzkit ledger validation: `src/gzkit/validate_pkg/ledger_check.py`
- gzkit OBPI audit: `src/gzkit/commands/obpi_audit_cmd.py`
- gzkit brief inspection: `src/gzkit/commands/status_obpi_inspect.py` (lines 263-304)
- OBPI brief: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-19-adr-audit-ledger-pattern.md`

## Verification

```bash
uv run -m unittest tests/test_obpi_0_25_0_19_adr_audit_ledger.py -v
uv run gz lint
uv run gz typecheck
uv run gz test
```
