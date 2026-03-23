<!-- markdownlint-disable MD013 -->

# ADR Evaluation Scorecard

**ADR:** ADR-0.0.3-hexagonal-architecture-tune-up
**Evaluator:** Claude Opus 4.6
**Date:** 2026-03-23

---

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|:-----------:|:--------:|
| 1 | Problem Clarity | 15% | 2 | 0.30 |
| 2 | Decision Justification | 15% | 2 | 0.30 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 2 | 0.20 |
| 6 | Scope Discipline | 10% | 2 | 0.20 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

**WEIGHTED TOTAL: 2.50 / 4.0**
**THRESHOLD:** 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

---

## ADR Dimension Rationale

### 1. Problem Clarity (Score: 2)

The "Intent" section lists 7 desirable capabilities but no concrete problem statement. There is
no "before" state with evidence of current pain (e.g., "tests use 47 mock.patch calls that
broke during the config refactor" or "three commands format output differently"). The
"Consequences" section is generic boilerplate — "Governance visibility for superpowers work"
is unrelated to hexagonal architecture. A reader cannot answer "why now?" from the ADR alone.

### 2. Decision Justification (Score: 2)

The Decision section describes the three-layer model and four Protocol ports clearly, but never
justifies the choices:

- Why hexagonal over clean architecture or vertical slices?
- Why exactly four ports? (What about a `NotificationSink` or `SchemaStore`?)
- Why structural subtyping (`typing.Protocol`) over explicit ABC inheritance?
- Why structlog over stdlib logging with JSON formatter?

The "Alternatives Considered" section says "Manual gz plan + gz specify (two-step)" which
describes the ADR *authoring process*, not architectural alternatives. No counterarguments
are addressed.

### 3. Feature Checklist (Score: 3)

All 9 items are necessary and independently valuable. Each maps to a testable deliverable.
Granularity is consistent (1-3 day units). Items are logically ordered (skeleton → content →
enforcement). No visible redundancy or padding.

Gap: the checklist creates infrastructure but never wires it into existing commands. This is
acknowledged as incremental work but not tracked as a follow-on ADR or non-goal.

### 4. OBPI Decomposition (Score: 3)

Clear dependency graph: OBPI-01 is the foundation; 02, 03, 04, 05, 06, 09 can parallelize
after it; 07 and 08 depend on 06. All are reasonably sized. Domain boundaries are clean —
each OBPI owns distinct files. Numbering is sequential with no gaps.

### 5. Lane Assignment (Score: 2)

All 9 OBPIs are Heavy. Two are debatable:

- **OBPI-04 (Test Fakes):** Creates test infrastructure directories and in-memory fakes. No
  external contract changes. Could be Lite.
- **OBPI-09 (Policy Tests):** Creates AST-scanning test files. The brief states "changes a
  command/API/schema/runtime contract surface" which is factually incorrect — policy tests
  scan source but change no contracts. Could be Lite.

Under parent-lane-attestation-floor (Heavy ADR → Lite OBPIs still require human attestation),
the practical impact is low, but the lane justification text is inaccurate.

### 6. Scope Discipline (Score: 2)

The ADR has no "Non-Goals" section. Scope is implied through OBPI denied paths but the
ADR-level document never explicitly states boundaries:

- Does not say: "will not migrate existing commands to use the new patterns"
- Does not say: "will not change the public CLI surface"
- Does not say: "will not add new CLI flags"
- No guardrails against scope expansion

### 7. Evidence Requirements (Score: 3)

Each OBPI has a `## Verification` section with concrete commands (`python -c` import checks,
`uv run -m unittest` invocations). Quality gates 1-5 are specified per OBPI with clear
criteria. Heavy gate obligations (3/4/5) are acknowledged per OBPI.

### 8. Architectural Alignment (Score: 3)

Port designs reference existing modules (`lifecycle.py`, `config.py`, `quality.py`) as
informing sources. The target project structure is explicit and fits within the existing
`src/gzkit/` layout. OBPI-level NEVER rules serve as anti-pattern guardrails.

---

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|:-----------:|:-----------:|:-----:|:----:|:-------:|:---:|
| 01 - Hexagonal Skeleton | 4 | 4 | 4 | 4 | 4 | **4.0** |
| 02 - Domain Extraction | 3 | 3 | 4 | 3 | 3 | **3.2** |
| 03 - Exception Hierarchy | 3 | 4 | 3 | 4 | 4 | **3.6** |
| 04 - Test Fakes & Separation | 3 | 3 | 3 | 3 | 4 | **3.2** |
| 05 - Config Precedence | 3 | 3 | 3 | 3 | 3 | **3.0** |
| 06 - Output Formatter | 3 | 3 | 3 | 3 | 3 | **3.0** |
| 07 - Structured Logging | 3 | 3 | 3 | 3 | 3 | **3.0** |
| 08 - Progress Indication | 3 | 3 | 2 | 4 | 3 | **3.0** |
| 09 - Policy Tests | 3 | 4 | 4 | 4 | 3 | **3.6** |

**OBPI THRESHOLD:** Average >= 3.0 per OBPI, no dimension scoring 1. **PASS.**

---

## Overall Verdict

- [ ] GO - Ready for proposal/defense review
- [x] CONDITIONAL GO - Address items below, then re-evaluate
- [ ] NO GO - Structural revision required

**ADR score (2.50) is at the boundary.** OBPIs pass individually but the ADR document has
structural gaps in problem framing, decision justification, and scope discipline.

---

## Action Items

1. **Add a Problem Statement section** with concrete before-state evidence (e.g., mock.patch
   count, inconsistent output patterns, scattered ENV reads) and a testable after-state.
   Currently the ADR jumps straight to solutions without establishing why the current
   architecture is insufficient. *(Targets: Dimension 1 → 3)*

2. **Justify architectural decisions** in the Decision section. Why hexagonal? Why these four
   ports? Why structural subtyping? Why structlog? Name and dismiss at least one concrete
   alternative per major decision. Replace the "Alternatives Considered" section with actual
   architectural alternatives. *(Targets: Dimension 2 → 3)*

3. **Add explicit Non-Goals and Scope Boundaries** at the ADR level. State what this effort
   will NOT do (command migration, CLI surface changes, new flags) and add guardrails against
   scope expansion. *(Targets: Dimension 6 → 3)*

4. **Fix lane assignment justifications** for OBPI-04 and OBPI-09. Either downgrade to Lite
   (with note that parent-lane attestation floor still applies) or provide accurate Heavy
   justification. Remove the incorrect "changes a command/API/schema/runtime contract surface"
   from OBPI-09. *(Targets: Dimension 5 → 3)*

Addressing items 1-3 would raise the weighted total to approximately **3.10** (GO threshold).
