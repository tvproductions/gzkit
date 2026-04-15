---
id: OBPI-0.27.0-05-arb-patterns
parent: ADR-0.27.0-arb-receipt-system-absorption
item: 5
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.27.0-05: ARB Patterns

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.27.0-arb-receipt-system-absorption/ADR-0.27.0-arb-receipt-system-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.27.0-05 — "Evaluate and absorb arb/patterns.py (253 lines) — pattern detection across receipt history"`

## OBJECTIVE

Evaluate `opsdev/arb/patterns.py` (253 lines) against gzkit's current approach to QA trend analysis and determine: Absorb (opsdev adds governance value), Confirm (gzkit's existing approach is sufficient), or Exclude (environment-specific). The opsdev module is the largest in the ARB subsystem and performs cross-receipt pattern detection: identifying recurring violations by rule, file, and category; tracking violation trends over time; computing frequency and severity metrics. gzkit currently has no equivalent — each QA run is independent with no cross-run analysis. The comparison must determine whether pattern detection across receipt history provides governance value that justifies the 253-line complexity.

## SOURCE MATERIAL

- **opsdev:** `../opsdev/src/opsdev/arb/patterns.py` (253 lines)
- **gzkit equivalent:** No direct equivalent — QA runs are independent

## ASSUMPTIONS

- The governance value question governs: does cross-receipt pattern detection surface insights that single-run output cannot?
- opsdev wins where trend analysis identifies systemic issues invisible in individual runs
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 253 lines, this is the most complex ARB module — complexity-vs-value ratio is critical
- This module is consumed by advise (OBPI-04) and likely depends on receipt storage (OBPI-10)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Building statistical analysis beyond deterministic pattern matching

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: pattern detection algorithms, trend metrics, dependency chain, complexity cost
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why independent QA runs are sufficient for governance
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

- `src/gzkit/arb/patterns.py` — port of `opsdev/arb/patterns.py` (253L source, the largest ARB module). Converts `@dataclass(frozen=True)` for `PatternCandidate` and `PatternReport` to Pydantic `BaseModel(frozen=True, extra="forbid")`. Preserves the `RULE_GUIDANCE` dict (14 entries mapping ruff codes to human-readable anti-pattern labels + correct-approach text). Preserves the prefix-matching guidance fallback (`UP*`/`SIM*`/`PERF*`/`COM*`). Keeps the ≥2 occurrence threshold for candidate elevation and the top-20 aggregation. Exposes both `render_patterns_markdown()` (full report) and `render_patterns_compact()` (one-line summary) for different operator moments.
- `tests/arb/test_patterns.py` — 6 Red→Green tests: empty directory, recurring rule becomes candidate, single-occurrence ignored, prefix-guidance-for-UP/SIM/PERF, report-is-frozen-pydantic, render-markdown-produces-table.

**Comparison evidence:** See OBPI-0.25.0-33-arb-analysis-pattern.md § Comparison Evidence — "Pattern extraction — `patterns.py:130-194` — `collect_patterns()` maps recurring rules through `RULE_GUIDANCE` dict to `PatternCandidate` + `PatternReport`" against gzkit pre-absorption "None — `instruction_eval.py` and `instruction_audit.py` audit instruction surfaces, not lint findings."

**Dog-fooding proof:** During the Stage 4 demonstration, `uv run gz arb patterns --limit 20` against 3 demo receipts emitted a ready-to-paste Markdown table mapping each recurring rule (F841, F401, I001, E501, SIM105) to its anti-pattern guidance and sample file paths. The output shape matches the intended "drop rows into CLAUDE.md/AGENTS.md" use case. Compact mode (`--compact`) emits a one-line summary suitable for dashboards.

**Complexity-vs-value note:** The brief correctly flagged "At 253 lines, this is the most complex ARB module — complexity-vs-value ratio is critical." The dog-fooding demonstration showed that the ready-to-paste pattern catalog is the single highest-leverage output of the entire ARB surface — it's the closing half of the feedback loop (collect receipts → advise → extract patterns → update agent guardrails → reduce defects). The complexity is justified.

**Status:** `status: Pending` in frontmatter preserved; work executed under OBPI-0.25.0-33.

## Closing Argument

Absorb executed under OBPI-0.25.0-33 on 2026-04-14. See OBPI-0.25.0-33-arb-analysis-pattern.md § Implementation Summary and § Key Proof for the end-to-end evidence trail.
