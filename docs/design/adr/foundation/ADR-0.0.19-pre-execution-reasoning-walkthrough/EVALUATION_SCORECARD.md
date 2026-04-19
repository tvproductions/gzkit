# ADR Evaluation Scorecard — ADR-0.0.19

**ADR:** ADR-0.0.19 — Pre-execution reasoning walkthrough (gz justify)
**Evaluator:** Manual review (main-session agent) superseding `gz adr evaluate` CLI pre-screen
**Date:** 2026-04-19
**CLI pre-screen verdict:** GO (weighted 3.75/4.0)
**Manual verdict:** GO (weighted 3.85/4.0)

---

## ADR Quality — 8 Dimensions

| # | Dimension | Weight | CLI | Manual | Weighted | Rationale |
|---|-----------|--------|-----|--------|----------|-----------|
| 1 | Problem Clarity | 15% | 4 | 4 | 0.60 | Intent states the invariant being unenforced (Prime Directive 11), cites the forcing case (`chores.md:19` correction during 4.7 audit), names before/after state. |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | Decision articulates tool/agent split rationale, anchor-scope boundary, dependency graph of 5 OBPIs, and rejects 5 alternatives by name with specific reasons. |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | 5 items; each maps 1:1 to a named OBPI; numbering sequential 01-05 with no gaps. |
| 4 | OBPI Decomposition | 15% | 3 | 3 | 0.45 | **CLI finding confirmed.** OBPI Allowed Paths currently overlap because briefs were produced by `gz specify` defaults and have not yet been semantically authored. Expected pre-authoring state; refined via `gz-obpi-specify` pass before Stage 2 (next pipeline step). Score held at 3 honestly — will lift to 4 after authoring. |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | Heavy is correct: new CLI surface (two subcommands), new skill, manpage + command doc + runbook entries, BDD scenarios, Gate 5 attestation. Lite would miss the external contract changes. |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | Explicit NOT list with 5 items (no mechanical gate, no ARB integration, no ADR anchors, no LLM in CLI, no receipt JSON schema). Scope-minimization forcing function applied; drop-order explicit. |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | Closeout form lists all 5 gates with concrete commands; Heavy-lane OBPI-05 names ARB receipt requirements for lint/typecheck/tests/coverage/mkdocs plus `gz attest`. |
| 8 | Architectural Alignment | 10% | 3 | **4** | 0.40 | **CLI finding overridden.** CLI flagged "No anti-pattern guidance" because it pattern-matches for an "Anti-Pattern Warning" subsection label. This ADR distributes anti-pattern guidance across legitimate sections: scope-boundary NOT list in Decision, pre-mortem failure modes (template-bending, fabrication, structural-not-semantic completeness), and Persona's tool/agent split framing. Same authoring pattern as ADR-0.0.16 (Foundation exemplar). False negative. |

**Weighted total:** 0.60 + 0.60 + 0.60 + 0.45 + 0.40 + 0.40 + 0.40 + 0.40 = **3.85 / 4.0**

**Threshold:** ≥3.0 GO · 2.5-3.0 CONDITIONAL · <2.5 NO GO

**ADR-level verdict:** **GO**

---

## OBPI Quality — 5 Dimensions

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|--------------|-------------|-------|------|---------|-----|
| OBPI-0.0.19-01 anchor-resolution-and-evidence | 4 | 4 | 4 | 4 | 3 | 3.8 |
| OBPI-0.0.19-02 scaffold-rendering | 4 | 4 | 4 | 4 | 4 | 4.0 |
| OBPI-0.0.19-03 validate-subcommand | 4 | 4 | 4 | 4 | 3 | 3.8 |
| OBPI-0.0.19-04 skill-and-upstream-integrations | 4 | 4 | 4 | 4 | 3 | 3.8 |
| OBPI-0.0.19-05 docs-bdd-closeout | 4 | 4 | 4 | 4 | 3 | 3.8 |

**CLI scores held without manual override.** Clarity 3 on four briefs is honest: the briefs were produced by `gz specify` with default content and require semantic authoring. No dimension scores 1 (no blocker). Threshold average ≥3.0 met on all five.

**OBPI-level verdict:** pass threshold; refine Clarity during `gz-obpi-specify` authoring pass.

---

## CLI Reconciliation Summary

| Dimension | CLI | Manual | Divergence |
|-----------|-----|--------|------------|
| 1-3, 5-7 | 4 | 4 | None |
| 4 | 3 | 3 | CLI finding confirmed — pre-authoring state |
| 8 | 3 | 4 | CLI false negative — heuristic looked for missing subsection label; anti-pattern guidance distributed across Decision scope-boundary + pre-mortem + Persona per exemplar pattern (ADR-0.0.16) |

---

## Red-Team Protocol

Not invoked on this run (`--red-team` not passed). Scorecard reflects 8-dimension rubric + OBPI 5-dimension rubric only. The 7 design-phase forcing functions (pre-mortem, WWHTBT, constraint archaeology, assumption surfacing, 2am operator, reversibility, scope minimization) were executed during `gz-design` authoring and are recorded in the Decision section — those constitute an in-band red-team pass.

---

## Action Items

1. **OBPI authoring pass (next pipeline step):** `gz-obpi-specify` refines Allowed Paths and acceptance criteria for all 5 briefs. Expected lift: dimension 4 (OBPI decomposition) from 3 to 4, OBPI Clarity from 3 to 4 on four briefs. No structural revision to the ADR.
2. **Operator review:** confirm ADR package before proceeding to `gz-obpi-specify`.

---

## Overall Verdict

**GO** — ready for operator review and OBPI authoring pass.

No dimension scored 1; no blockers. Findings are pre-authoring state that the next pipeline step addresses.
