<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR Evaluation Scorecard

## Metadata

**ADR:** ADR-0.23.0 — Agent Burden of Proof at ADR Closeout
**Evaluator:** Claude Opus 4.6 (self-review, revision 2)
**Date:** 2026-03-21

---

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 4 | 0.60 |
| 2 | Decision Justification | 15% | 4 | 0.60 |
| 3 | Feature Checklist | 15% | 4 | 0.60 |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 |
| 5 | Lane Assignment | 10% | 4 | 0.40 |
| 6 | Scope Discipline | 10% | 4 | 0.40 |
| 7 | Evidence Requirements | 10% | 4 | 0.40 |
| 8 | Architectural Alignment | 10% | 4 | 0.40 |

**WEIGHTED TOTAL: 4.00/4.0**
**THRESHOLD: 3.0 (GO)**

---

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 — Closing Argument | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 02 — Product Proof Gate | 4 | 4 | 4 | 3 | 3 | 3.6 |
| 03 — Reviewer Agent | 3 | 4 | 4 | 3 | 3 | 3.4 |
| 04 — Ceremony Enforcement | 3 | 4 | 4 | 3 | 3 | 3.4 |

**OBPI Average: 3.55** (threshold: 3.0)
**No dimension scores 1 on any OBPI.**

---

## Dimension Rationale (Revision 2 — Changes from Revision 1)

### Problem Clarity (4/4) — unchanged

The problem is concrete: closeout currently runs tests/lint/typecheck but has zero automated documentation checks. The manual ceremony checklist is non-blocking. Value narratives echo planning intent rather than proving delivered value. The "so what?" is immediate — operators inherit features they cannot understand or use.

### Decision Justification (4/4) — improved from 3

**What changed:** ADR now includes a Decision Justification section that names three alternatives and dismisses each with specific reasoning. Cites ADR-0.15.0 as a failed exemplar (all checklist boxes ticked, Summary Deltas still "TBD", completion table full of placeholder links). Cites ADR-0.12.0 as the strong exemplar (concrete post-attestation ceremony, before/after value narratives, specific CLI verification in every brief). Each decision references a local precedent or names the alternative it displaces.

### Feature Checklist Completeness (4/4) — improved from 3

**What changed:** Consequences section now has an explicit four-tier migration path: completed OBPIs untouched, in-progress OBPIs add Closing Argument at completion, new OBPIs use updated template, template retains compatibility comment. Every item is necessary (removing any leaves a gap), coverage is complete, and the migration strategy prevents orphaned briefs.

### OBPI Decomposition Quality (4/4) — improved from 3

**What changed:** ADR now explicitly declares OBPIs 01-03 as parallelizable with a dependency diagram showing OBPI-04 as the integrator. Critical path = max(01, 02, 03) + 04, reducing effective depth from 4 to 2. OBPI-04 includes an ASCII dependency graph. Each OBPI is a 1-3 day work unit at consistent granularity, groupings follow domain boundaries (template / gate / agent / ceremony).

### Lane Assignment Correctness (4/4) — unchanged

OBPI-01 is correctly Lite (internal template change). OBPIs 02-04 are correctly Heavy (CLI contract, pipeline contract, ceremony contract). Gate 3/4/5 obligations acknowledged in each Heavy brief.

### Scope Discipline (4/4) — improved from 3

**What changed:** ADR now has an explicit Non-Goals section with 5 specific exclusions (retroactive migration, automated prose scoring, replacing human attestation, scope expansion to non-closeout phases, changing attestation vocabulary). Includes guardrails against scope creep: "If implementation touches `closeout_cmd()` beyond the product-proof gate, split into separate OBPI or defer to ADR-0.19.0." Lite-lane applicability section in Rationale explicitly addresses proportional rigor (closing arguments + docstrings required, reviewer advisory not blocking, no Gate 5).

### Evidence Requirements (4/4) — improved from 3

**What changed:** OBPIs 01, 03, and 04 now include concrete Verification Commands sections with specific `grep` and CLI commands that prove completion. Every OBPI has at least one single-command verification path. OBPI-01: `grep "Closing Argument"` on template + `grep "Value Narrative"` absence check. OBPI-02: `gz closeout --dry-run`. OBPI-03: assessment artifact existence + structured field verification. OBPI-04: ceremony skill content check + end-to-end dry-run.

### Architectural Alignment (4/4) — improved from 3

**What changed:** ADR now cites two specific exemplar ADRs from the repository: ADR-0.15.0 as the cautionary tale (what weak closeout looks like — every gate passed, operator got nothing usable) and ADR-0.12.0 as the gold standard (what strong closeout looks like — concrete evidence, operator-facing narratives, verification commands). The ADR explicitly states it codifies ADR-0.12.0's discipline as a requirement. Anti-pattern is specific: "more checkboxes = more rigor" with ADR-0.15.0 as proof that this fails.

---

## OBPI Score Changes (Revision 2)

### OBPI-01 — Closing Argument

- **Testability:** 3 → 4. Now has 4 concrete verification commands: `grep` for section presence, absence of old section name, template validation test, and guidance text check.
- **Clarity:** 3 → 4. Requirements are explicit: three required elements (artifact paths, operator capability, proof command/link), migration guidance for old briefs, and the anti-pattern (copying planning intent) is named.

### OBPI-02 — Product Proof Gate — unchanged

Already scored well. `gz closeout --dry-run` remains the single-command verification.

### OBPI-03 — Reviewer Agent

- **Testability:** 3 → 4. Now has 4 concrete verification commands: reviewer function in pipeline.py, assessment artifact existence, structured field verification, and separate-agent dispatch proof.

### OBPI-04 — Ceremony Enforcement

- **Independence:** 2 → 3. Dependency is now explicitly framed as integrator with 2-depth parallel graph (not 4-depth serial chain). ASCII dependency diagram included. OBPI is still dependent on 01-03, but the dependency is declared, justified, and the parallel structure means it's not blocked longer than the slowest predecessor.
- **Testability:** 3 → 4. Now has 4 concrete verification commands: ceremony skill content checks, closeout form template check, and end-to-end dry-run.

---

## Overall Verdict

**[x] GO — Ready for proposal/defense review**

**Weighted total: 4.00** exceeds 3.0 threshold.
**OBPI average: 3.55** exceeds 3.0 threshold.
**No dimension scores 1. No dimension scores 2.**

### Strengths

1. **Problem is grounded in repository evidence** — ADR-0.15.0 is a real exemplar of the failure mode, not a hypothetical
2. **Anti-pattern is named and exemplified** — "more checkboxes" trap is backed by ADR-0.15.0's complete-but-empty closeout
3. **Gold standard is cited and codified** — ADR-0.12.0's closeout discipline becomes the formal requirement
4. **Parallelizable decomposition** — OBPIs 01-03 independent, critical path depth of 2
5. **Every OBPI has single-command verification** — concrete bash commands that prove completion
6. **Lite-lane handling is explicit** — proportional rigor without exemption
7. **Migration path is concrete** — four tiers covering every brief lifecycle state

### Action Items

None — all dimensions at 4/4, all OBPI averages above 3.0.
