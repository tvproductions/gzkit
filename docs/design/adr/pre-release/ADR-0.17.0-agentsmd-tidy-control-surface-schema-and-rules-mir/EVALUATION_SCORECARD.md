<!-- markdownlint-disable-file MD013 MD041 -->

ADR EVALUATION SCORECARD
========================

ADR: ADR-0.17.0 — AGENTS.md Tidy: Control Surface Schema and Rules Mirroring
Evaluator: Claude Opus 4.6
Date: 2026-03-17
Context: Retroactive eval — ADR was booked via gz superbook without evaluation

--- ADR-Level Scores ---

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 2 | 0.30 | Four numbered intent points are clear directionally ("reduce context window bloat", "maintain guardrails") but none are quantified. No concrete before/after state. No "so what?" evidence. "~80% token reduction" is asserted without measurement. |
| 2 | Decision Justification | 15% | 3 | 0.45 | Three-layer control surface model is well-articulated with concrete path mappings. Vendor projection map is specific. However, Alternatives Considered is a single line ("Manual gz plan + gz specify") with no reasoning. No counterarguments addressed. |
| 3 | Feature Checklist | 15% | 2 | 0.30 | Five checklist items exist but none are elaborated beyond a title. No "if removed, what breaks?" reasoning. Items appear to be at consistent granularity but this is hard to verify without substance. Checklist items are unchecked despite attestation claiming completion. |
| 4 | OBPI Decomposition | 15% | 1 | 0.15 | **Structural defect.** All 5 OBPI briefs are unresolved templates with placeholder content. Objectives are bare titles. Requirements say "First constraint." Allowed/Denied paths are generic examples. Acceptance criteria are empty. No agent could implement these briefs as written. |
| 5 | Lane Assignment | 10% | 2 | 0.20 | ADR is Heavy (correct — changes control surface contracts). All OBPIs marked Heavy, but with no substantive content it's impossible to verify whether each individual OBPI actually touches an external contract. Some (e.g., "Manifest Update and Final Sync") might be Lite. |
| 6 | Scope Discipline | 10% | 1 | 0.10 | **Structural defect.** No Non-Goals section. No scope boundaries stated. No guardrails against scope creep. Consequences section is two lines ("Governance visibility for superpowers work" / "Additional booking step"). |
| 7 | Evidence Requirements | 10% | 1 | 0.10 | **Structural defect.** Evidence section contains unchecked placeholders (`- [ ] Tests: tests/`, `- [ ] Docs: docs/`). No specific test files, no verification commands, no completion criteria. OBPI briefs have empty acceptance criteria. "Done" is undefined. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | The three-layer model and vendor projection map reference specific paths and follow established codebase patterns. Integration points are implicit in the path mappings. No anti-pattern warning. No exemplar reference. |

**WEIGHTED TOTAL: 1.90/4.0**
**THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)**

--- OBPI-Level Scores ---

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 — Categorized Skill Catalog | 3 | 1 | 3 | 2 | 1 | 2.0 |
| 02 — Rules Mirroring | 3 | 1 | 3 | 2 | 1 | 2.0 |
| 03 — Slim CLAUDE.md Template | 3 | 1 | 3 | 2 | 1 | 2.0 |
| 04 — JSON Schemas and Validation | 3 | 1 | 3 | 2 | 1 | 2.0 |
| 05 — Manifest Update and Final Sync | 2 | 1 | 2 | 2 | 1 | 1.6 |

**OBPI THRESHOLD: FAILED.** All OBPIs score 1 on Testability and Clarity (structural defects). No OBPI has concrete verification commands or enough detail for an agent to implement without ambiguity.

**OBPI Notes:**

- All briefs are unresolved template instances. YAML frontmatter contains `{parent_adr_path}` and `{checklist_item_text}` as literal uninterpolated placeholders.
- All Requirements sections contain example text ("First constraint", "Second constraint") not actual constraints.
- All Allowed/Denied Paths use generic examples (`src/module/`, `tests/test_module.py`), not actual repo paths.
- All Acceptance Criteria, Evidence, and Value Narrative sections are empty.
- Independence scores 3 because the titles suggest independent work domains, but without content this is speculative.

--- Governance Concern ---

**The attestation block claims "Completed" with "all quality gates passing (447 tests OK)" but:**

1. All 5 checklist items in the ADR remain unchecked (`- [ ]`)
2. All 5 OBPI briefs are Draft status with empty acceptance criteria
3. Evidence section contains unchecked placeholders
4. No OBPI has a completion date or evidence hash

This is a disconnect between the attestation claim and the artifact state. The implementation work may have been done correctly via superpowers, but the governance artifacts were not updated to reflect completion. The superbook booking created the ADR package structure but did not instantiate the OBPI briefs with actual scope or record completion evidence.

--- Overall Verdict ---

[x] **NO GO** — Structural revision required.

Three dimensions score 1 (OBPI Decomposition, Scope Discipline, Evidence Requirements). All OBPI briefs are template placeholders. The ADR cannot proceed to defense review in this state.

**ACTION ITEMS (ranked by impact):**

1. **Instantiate all 5 OBPI briefs** with actual objectives, allowed/denied paths, requirements, acceptance criteria, and verification commands. This is the highest-impact fix — it addresses Dimensions 4, 7, and all OBPI scores.
2. **Add Non-Goals and scope boundaries** to the ADR. What is explicitly excluded? What guardrails prevent scope creep?
3. **Reconcile attestation with artifact state.** Either update the checklist and briefs to reflect completed work (with evidence), or revise the attestation to acknowledge the governance gap.
4. **Expand Alternatives Considered** beyond the single line. Why three layers instead of two? Why vendor mirrors instead of vendor-specific canonical files?
5. **Quantify the problem.** "~80% token reduction" needs measurement evidence. What was the before token count? What is the after?
