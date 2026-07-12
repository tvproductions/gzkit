# AUDIT — ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine

**Ceremony:** COMPLETED → VALIDATED (Gate-5 audit)
**Date:** 2026-07-12
**Driver persona:** `pipeline-orchestrator`
**Prior state:** Completed - Partial (map-shape enforcement delivered; 15k weight-halving deferred to GHI #533 / ADR-0.0.37)

## Fidelity Gate (bound — `gz adr fidelity`)

| Claim | Command | Expected | Observed | Result |
|-------|---------|----------|----------|--------|
| AGENTS.md conforms to the map-not-encyclopedia shape | `uv run gz validate --agents-md-map-conformance` | 0 | 0 | ✅ PASS |
| Fidelity Assertions block is parseable | `uv run gz adr fidelity ADR-0.0.54-… --check` | 0 | 0 | ✅ PASS |

**Summary: 2 pass, 0 fail.** The ADR's thesis (mechanically-enforced map shape) holds against the running system.

## Execution Log

| Check | Command | Result |
|-------|---------|--------|
| Ledger completeness | `gz adr audit-check ADR-0.0.54` | ✅ PASS — 4/4 OBPIs completed with evidence (exit 0) |
| Bound fidelity gate | `gz adr fidelity ADR-0.0.54` | ✅ PASS — 2/2 assertions |
| CLI/governance audit | `gz cli audit` | ✅ PASS — 125/125 commands covered |
| Lint | `gz arb ruff` | ✅ PASS — `arb-ruff-c75d8372eca94746a2719ccda00a461a` |
| Typecheck | `gz arb typecheck` | ✅ PASS — `arb-step-typecheck-b160b00c929045c7bff98ee27a2f3794` |
| Unit tests | `gz arb step --name unittest` | ✅ PASS (7015 tests) — `arb-step-unittest-48a0ef68f210402a8bb79c98c99cb279` |
| Docs build | `gz arb step --name mkdocs` | ✅ PASS — `arb-step-mkdocs-703e8f80b8e143eeab9954ee936eb790` |

## Shortfalls Identified & Resolved

1. **REQ-kind discipline (closeout-proof gate):** the pre-0.0.59 briefs lacked `[kind]` tags. Retrofitted 12 tags (11 `[BEHAVIOR]` + 1 `[STRUCTURAL-FENCE]`); added `tests/**` Allowed-Paths (closes GHI #530); added ADR `## Boundary Invariants` section. **Resolved.**
2. **Truthfulness drift (independent-review finding):** three surfaces asserted a false enforced budget; OBPI-02 carried a false "under-budget" attestation line. Repointed to live JSON (rule v0.2.0); annotated the OBPI-02 record (not overwritten). **Resolved.**
3. **covers-backfill FAIL (audit-check, 6 findings):** GHI #309 same-commit-window heuristic flagged OBPI-03's `@covers` decorators. **Investigated (git provenance):** each test body was authored @`9b295aed`; the `@covers` decorators were overlaid ~5h later @`b7b5984` (same OBPI-03 landing) — the genuine regression-invariant-overlay shape, not cosmetic backfill (assertions independently verified as real REQ-semantic checks). Applied 6 operator-attested `# audit-exempt: regression-invariant-overlay` markers per the sanctioned mechanism. **Resolved (audit-check exit 0).**

No unresolved shortfalls remain.

## Evidence Index

- Fidelity: `uv run gz adr fidelity ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine`
- Ledger: `uv run gz adr audit-check ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine` (exit 0)
- ARB receipts under `artifacts/receipts/` (IDs above)
- Independent reviews (closeout): spec-reviewer (CONCERNS→resolved), quality-reviewer (DRIFT-FOUND→resolved)

## Summary Table

| Dimension | State |
|-----------|-------|
| Completeness | 4/4 OBPIs completed + attested; deferred 15k weight tracked (GHI #533) |
| Integrity | Ledger proof complete; fidelity gate green; truthfulness surfaces corrected |
| Alignment | Docs ↔ enforced state reconciled (live-JSON pointer); code ↔ tests green |

## Attestation

Agent (audit driver) signs the audit evidence as assembled and verified. Human Gate-5 attestation for each OBPI occurred at completion; the ADR-level audit acceptance is relayed via the validated receipt's `attestation_text`.
