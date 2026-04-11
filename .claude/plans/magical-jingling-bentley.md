# OBPI-0.25.0-22: ADR Traceability Pattern — Execution Plan

## Context

OBPI-0.25.0-22 is a Heavy-lane comparison/evaluation OBPI under ADR-0.25.0 (Core Infrastructure Pattern Absorption, Phase 2). The task: compare airlineops `adr_traceability.py` (277 lines — heuristic ADR-to-artifact keyword inference) against gzkit's traceability surface (`triangle.py` 372 lines + `traceability.py` 418 lines — declarative `@covers` annotations, AST scanning, coverage rollup, drift detection).

**Preliminary decision: Confirm** — gzkit's declarative traceability is architecturally superior to heuristic inference. The airlineops module's domain-specific scoring bonuses (econ, ops, market) fail the subtraction test.

## Plan

Edit one file only:
`docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-22-adr-traceability-pattern.md`

No code changes. No test changes. (Confirm decision = no absorption.)

### Steps

1. **Check Gate 1 checkbox** — `[x] Intent recorded`
2. **Insert `## Comparison` section** with three tables:
   - Table A: airlineops function-level analysis (7 rows: `load_adrs`, `collect_artifacts`, `infer`, `generate_text_report`, `_score_artifact`, dataclasses, path resolution)
   - Table B: gzkit traceability surface (4 rows: `triangle.py`, `traceability.py`, `gz-adr-map` skill, CLI commands)
   - Table C: Capability comparison (8 dimensions: approach, mapping, coverage, test discovery, drift, domain specificity, data model, path resolution)
3. **Insert `## Decision: Confirm`** with 6 rationale points (declarative vs heuristic, coverage depth, drift detection, subtraction test failure, AST precision, convention compliance)
4. **Insert Gate 4 N/A rationale** — no operator-visible behavior change
5. **Check all gate and acceptance criteria checkboxes** (except Gate 5 Human)
6. **Write Closing Argument** — single paragraph summarizing why Confirm
7. **Write Implementation Summary + Key Proof** blocks (matching OBPI-21 format)

### Critical File

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-22-adr-traceability-pattern.md`

### Verification

```bash
rg -n 'Decision: Confirm' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-22-adr-traceability-pattern.md
uv run gz test
uv run gz lint
```
