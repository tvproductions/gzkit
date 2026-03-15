<!-- markdownlint-disable-file MD013 MD036 -->

# ADR Evaluation Scorecard

**ADR:** ADR-0.14.0 - Multi-Agent Instruction Architecture Unification
**Evaluator:** Claude Opus 4.6
**Date:** 2026-03-15
**Revision:** R1 - re-scored after addressing action items

---

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 4 | 0.60 |
| 5 | Lane Assignment | 10% | 3 | 0.30 |
| 6 | Scope Discipline | 10% | 4 | 0.40 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

**WEIGHTED TOTAL: 3.25 / 4.0**
**THRESHOLD:** 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

### Dimension Rationale

**1. Problem Clarity (3/4):** Intent section names five concrete defects (context
bloat, duplication, stale instructions, inconsistent cross-agent behavior,
local-config leakage). Q&A transcript provides repo-specific audit evidence.
Before/after state is clear. Not exemplary because the "before" state is
qualitative rather than quantified with metrics.

**2. Decision Justification (3/4):** Seven numbered decisions form a coherent
layered architecture. Three alternatives are rejected with specific rationale.
Dependencies section names integration points with module paths. Not exemplary
because individual decisions share an umbrella justification rather than each
citing independent precedent or exemplar.

**3. Feature Checklist Completeness (3/4):** All 6 items deliver distinct capability.
No obvious gaps; migration guidance is addressed within OBPI-02. Items are at
consistent granularity and logically ordered from foundational (01) through
extensions (02-03) to observability (04-06).

**4. OBPI Decomposition Quality (4/4 - raised from 3):** Six OBPIs follow domain
boundaries with explicit Allowed/Denied Paths preventing overlap. Sequential
numbering with no gaps. The ADR now includes an explicit dependency graph and
parallelization section showing the critical path (01 → 04 → 06), parallel
stages (02+03+04+05 after 01), and theoretical minimum of 3 stages.

**5. Lane Assignment Correctness (3/4):** All OBPIs are Heavy with stated
justification referencing external contract changes. All briefs include Gate
3/4/5 sections. OBPI-05 and OBPI-06 now include explicit rationale for why
Heavy was chosen over Lite.

**6. Scope Discipline (4/4):** Five explicit non-goals are specific and tested
against plausible creep scenarios. Each OBPI has a Denied Paths section as a
guardrail. Migration Principles section further constrains scope expansion.

**7. Evidence Requirements (3/4):** Every OBPI has verification commands, REQ IDs,
and Gate 1-5 sections. OBPI-specific commands include `gz agent sync
control-surfaces --dry-run`, `gz validate --documents --surfaces`, and `gz
readiness audit`. Not exemplary because some verification is generic alongside
the specific commands.

**8. Architectural Alignment (3/4):** Dependencies section lists module paths
(`sync.py`, `hooks/claude.py`, `quality.py`, `validate.py`). Q&A transcript
describes current anti-patterns with evidence. Each OBPI names existing test
files as patterns to follow. Not exemplary because anti-patterns are described
narratively rather than formally labeled with "what wrong looks like" examples.

---

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 | 4 | 3 | 4 | 3 | 3 | 3.4 |
| 02 | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 03 | 3 | 3 | 3 | 3 | 3 | 3.0 |
| 04 | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 05 | 3 | 3 | 3 | 3 | 3 | 3.0 |
| 06 | 3 | 3 | 3 | 3 | 3 | 3.0 |

**OBPI THRESHOLD:** Average >= 3.0 per OBPI. Any OBPI scoring 1 on any
dimension must be revised.

### OBPI Rationale

**OBPI-01 (3.4):** Foundational with no incoming dependencies. High value as the
canonical model that all other OBPIs build on. Clear acceptance criteria with 4
REQ IDs. Testable via sync dry-run and template tests.

**OBPI-02 (3.2):** Depends on OBPI-01's canonical model (declared context). High
value replacing hook-only path delivery with native surfaces. Well-scoped with
migration guidance in REQ-0.14.0-02-04.

**OBPI-03 (3.0):** Meets threshold. Depends on OBPI-01 to know what moves vs stays.
Value is meaningful but the repo still functions with bloated root files.
"Recurring workflows" requires implementation judgment calls.

**OBPI-04 (3.2):** Strong value detecting stale/foreign/conflicting instructions.
Can run in parallel with 02/03 after 01. Acceptance criteria cite specific defect
types with concrete verification commands.

**OBPI-05 (3.0):** Meets threshold. Focused on config separation and sync
determinism. Testable (run sync twice, compare output). Lane justification now
explicit: operator-visible settings contract and agent policy discovery.

**OBPI-06 (3.0 - raised from 2.8):** Independence raised from 2 to 3 after
declaring explicit prerequisites on OBPI-01 and OBPI-04. Dependencies are now
formal rather than implied. The eval suite sequences correctly after the
canonical model and audit detection logic it exercises.

---

## Red-Team Challenges

Not requested for this evaluation.

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | - | Not run |
| 2 | Scope | - | Not run |
| 3 | Alternative | - | Not run |
| 4 | Dependency | - | Not run |
| 5 | Gold Standard | - | Not run |
| 6 | Timeline | - | Not run |
| 7 | Evidence | - | Not run |
| 8 | Consumer | - | Not run |
| 9 | Regression | - | Not run |
| 10 | Parity | - | Not run |

---

## Overall Verdict

- [x] GO - Ready for proposal/defense review
- [ ] CONDITIONAL GO - Address items below, then re-evaluate
- [ ] NO GO - Structural revision required

### Strengths

- Scope discipline is exemplary (4/4): five specific non-goals plus per-OBPI
  Denied Paths sections prevent creep effectively.
- OBPI decomposition raised to exemplary (4/4): explicit dependency graph with
  critical path, parallelization stages, and minimum wall-clock estimate.
- All dimensions at ADR level score 3+, with a weighted total of 3.25.
- Q&A transcript provides concrete audit-based evidence grounding the problem
  statement in observable repo defects rather than aspirational claims.
- OBPI briefs are consistently structured with REQ IDs, Allowed/Denied Paths,
  NEVER/ALWAYS requirements, and verification commands.
- The Decomposition Scorecard provides transparent sizing rationale.
- All 6 OBPIs meet the >= 3.0 per-OBPI threshold.

### Resolved Action Items (R1)

1. **OBPI-06 independence (was blocking):** RESOLVED. Added explicit Prerequisites
   section declaring OBPI-01 and OBPI-04 as required. Independence raised from
   2 to 3, OBPI average from 2.8 to 3.0.

2. **Dependency graph (was recommended):** RESOLVED. Added Dependency Graph and
   Parallelization section to the ADR with ASCII diagram, critical path, parallel
   stages, and minimum stage count. OBPI Decomposition raised from 3 to 4.

3. **Lane justification for 05/06 (was recommended):** RESOLVED. Added explicit
   rationale to both OBPI-05 and OBPI-06 briefs explaining why Heavy was chosen
   over Lite.

### Remaining Observations (non-blocking)

- Problem Clarity could reach 4 with quantified before/after metrics (e.g.,
  root file line counts, duplication percentage). Not required for GO.
- Decision Justification could reach 4 if individual decisions each cited a
  specific local precedent. Not required for GO.
