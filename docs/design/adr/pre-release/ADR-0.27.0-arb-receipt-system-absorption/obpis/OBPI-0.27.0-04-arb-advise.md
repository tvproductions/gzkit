---
id: OBPI-0.27.0-04-arb-advise
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 4
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-04: ARB Advise

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-04 — "Evaluate and absorb arb/advise.py (196 lines) — receipt analysis and recurring pattern advice"`

## OBJECTIVE

Evaluate `opsdev/arb/advise.py` (196 lines) against gzkit's current approach to QA feedback and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module analyzes receipt history, identifies recurring violations and patterns, categorizes findings by severity and frequency, and generates actionable advice. gzkit currently has no equivalent — QA feedback comes from raw command output. The comparison must determine whether structured advice from receipt analysis provides governance value beyond what developers can derive from reading raw lint/test output.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/advise.py` (196 lines)
- **gzkit equivalent:** No direct equivalent — raw QA command output only

## ASSUMPTIONS

- The governance value question governs: does receipt-based advice surface patterns that raw output cannot?
- opsdev wins where pattern analysis across receipt history reveals recurring issues invisible in single-run output
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- This module depends on receipt storage (OBPI-10) and likely patterns (OBPI-05) — evaluation should note dependencies

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building an AI-powered advice engine — this is deterministic pattern analysis

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: analysis depth, pattern categorization, advice quality, dependency chain
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why raw QA output is sufficient for governance
1. If Exclude: document why the module is environment-specific

## ALLOWED PATHS

- `src/gzkit/arb/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Decision rationale documented
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Decision: Absorb (executed under OBPI-0.25.0-33)

**Decision:** Absorb.

**Executed under:** `OBPI-0.25.0-33-arb-analysis-pattern` (closed 2026-04-14). Cross-referenced to preserve per-module audit trail.

**Gzkit implementation:**

- `src/gzkit/arb/advisor.py` — port of `opsdev/arb/advise.py` (196L source). Converts `@dataclass(frozen=True) ArbAdvice` to Pydantic `BaseModel(frozen=True, extra="forbid")`. Keeps the rule-categorization heuristic (`F/B` → correctness, `E/W/I/UP/COM` → style, `PERF/SIM` → quality) and the recommendation logic (style-dominant → tighten agent loop, correctness → smaller diffs and more tests, quality → refactor pattern). Rewrites the retention nudge text from `uv run -m opsdev arb tidy` to `uv run gz arb tidy --keep-last 200 --apply` (gzkit form, even though `gz arb tidy` is out of scope for OBPI-0.25.0-33 and remains pending under OBPI-0.27.0-06).
- `tests/arb/test_advisor.py` — 6 Red→Green tests: empty-directory zero-state, style-dominant recommendation, correctness-rules recommendation, tidy-nudge-references-gz-arb-form (regression guard preventing reversion to `opsdev`), limit honored, frozen Pydantic.

**Comparison evidence:** See OBPI-0.25.0-33-arb-analysis-pattern.md § Comparison Evidence — "Advice aggregation — `advise.py:100-165` — `collect_arb_advice()` aggregates recent lint receipts, categorizes rules, emits `ArbAdvice`" against gzkit pre-absorption "None — `chores_advise()` in `chores.py:267` is dry-run chore criteria, unrelated to lint telemetry."

**Dog-fooding proof:** During the Stage 4 demonstration, `uv run gz arb advise --limit 20` was run against a demo set of 3 receipts containing real lint violations (F841, F401, I001, E501, SIM105, UP035, UP006, E402, F811). The output produced a ranked "Top rules" table, a "Top paths" hotspot list, and conditional recommendations that matched the rule distribution (`F841`/`F401` correctness-class present → correctness recommendation; `SIM105` quality rule present → quality recommendation; tidy nudge in gzkit form). This is the concrete evidence that `advise` is not just a printer — it produces actionable, data-conditional agent guidance.

**Dependency note:** This brief correctly noted dependency on receipt storage (OBPI-0.27.0-10) and patterns (OBPI-0.27.0-05). Both were absorbed under OBPI-0.25.0-33 in the same implementation pass.

**Status:** `status: Pending` in frontmatter preserved; work executed under OBPI-0.25.0-33.

## Closing Argument

Absorb executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail.
