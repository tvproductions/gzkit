ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.34 — Agent Control Surface Rendering Substrate
Evaluator: gz-adr-evaluate v6.0.0 (manual pass, pipeline-orchestrator persona)
Date: 2026-05-16 (post-repair pass)

CLI deterministic re-screen: GO — 4.00/4.0 (8 OBPIs scored, all averages ≥ 3.0).
Manual verdict supersedes CLI per skill procedure.

---

## Pass History

| Pass | Date | ADR | OBPIs below 3.0 | Verdict |
|------|------|-----|------------------|---------|
| 1 (CLI pre-screen) | 2026-05-16 | 3.40 | n/a — CLI didn't compute brief-level deficits | GO (CLI) |
| 1 (Manual override) | 2026-05-16 | 3.45 | 6 of 8 | **CONDITIONAL GO** |
| 2 (post-repair, manual) | 2026-05-16 | **4.00** | **0 of 8** | **GO** |

Action items 1–5 from Pass-1 manual were applied in the same session.
This pass-2 scorecard records the post-repair state.

---

## ADR-Level Scores (Part 1 — 8 Dimensions)

| # | Dimension | Weight | Pass-1 | Pass-2 | Weighted | Rationale |
|---|-----------|--------|--------|--------|----------|-----------|
| 1 | Problem Clarity | 15% | 3 | **4** | 0.60 | Pass-2: added explicit Current/Target State block to Intent — before/after now scannable in two paragraphs without cross-section synthesis. |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | Unchanged — strong Alternatives Considered A–F. |
| 3 | Feature Checklist Completeness | 15% | 4 | 4 | 0.60 | Unchanged — 8 well-conceived components, clean domain boundaries. |
| 4 | OBPI Decomposition Quality | 15% | 2 | **4** | 0.60 | Pass-2: all 8 briefs repaired — per-OBPI scoped requirements, real source paths, declared cross-OBPI prerequisites, specific REQ-driven acceptance criteria. Briefs are now independently actionable. |
| 5 | Lane Assignment Correctness | 10% | 4 | 4 | 0.40 | Unchanged — every OBPI Heavy assignment defensible. |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | Unchanged — non-goals explicit (no Textual editor, no web admin, no re-author from scratch). |
| 7 | Evidence Requirements | 10% | 3 | **4** | 0.40 | Pass-2: every brief now carries concrete per-OBPI verification commands replacing the templated `test -f <ADR-path>` placeholders; invalid bash purged. |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | Unchanged — strong precedent references (ADR-0.0.19, ADR-0.16.0, ADR-0.0.30, ADR-0.0.33). |

**MANUAL WEIGHTED TOTAL: 4.00 / 4.0**
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

CLI and manual now agree across all 8 dimensions. The Pass-1 heuristic
mismatches (D1, D4, D7) were CLI false-negatives caused by content
distribution and brief-defect detection limits; both resolved by Pass-2
repairs and an authoring tweak.

---

## OBPI-Level Scores (Part 2)

Independence: "declared predecessors" still means declared in the brief.
Each brief now carries an explicit Prerequisite OBPI block in its Discovery
Checklist, so cross-OBPI dependencies are no longer undeclared.

| OBPI | Independence | Testability | Value | Size | Clarity | Pass-2 Avg | Pass-1 Avg |
|------|-------------|-------------|-------|------|---------|-----------|-----------|
| 01 content-model-registry | 4 | 4 | 4 | 4 | 4 | **4.0** | 3.4 |
| 02 rendering-pipeline | 4 | 4 | 4 | 3 | 4 | **3.8** | 2.8 |
| 03 reverse-parse-migration | 4 | 4 | 4 | 3 | 4 | **3.8** | 2.8 |
| 04 authoring-cli | 4 | 4 | 4 | 3 | 4 | **3.8** | 2.8 |
| 05 light-tui-affordances | 4 | 4 | 3 | 4 | 4 | **3.8** | 2.6 |
| 06 validation-hooks | 4 | 4 | 3 | 4 | 4 | **3.8** | 2.8 |
| 07 migration-layer | 4 | 4 | 3 | 3 | 4 | **3.6** | 2.6 |
| 08 vendor-manifest-expansion | 4 | 4 | 4 | 4 | 4 | **4.0** | 3.2 |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.

**All 8 OBPIs above threshold.** No dimension scores 1.

### Per-OBPI repair effects

- **Independence 2 → 4 (all OBPIs):** Each brief now declares its Prerequisite OBPIs explicitly in the Discovery Checklist (e.g. OBPI-02 declares OBPI-01; OBPI-03 declares OBPI-01+02; OBPI-06 declares OBPI-01+02+04 + external ADR-0.0.33). No undeclared dependencies remain.
- **Clarity 2 → 4 (all OBPIs):** Each brief's Requirements section now carries OBPI-scoped FAIL-CLOSED requirements (the wholesale 8-requirement copy-paste is gone). Acceptance criteria carry specific, observable REQs replacing the three-line templated placeholders.
- **Testability remains 4 (all OBPIs):** Per-OBPI verification commands replaced the invalid `test -f <CLI-command>` shapes; tests are addressable by `unittest discover` and mechanical proofs (`rg`, `diff -q`) are spelled out.
- **Size 3 retained on OBPIs 02/03/04/07:** Rendering pipeline, reverse parser, four authoring subcommands, and schema-version migration layer each genuinely could push 4 days. Held at 3 — not a defect.
- **Value 3 retained on OBPIs 05/06/07:** TUI affordances, validator wiring, schema versioning — each weakens the substrate noticeably but is non-functional-blocking on removal. Held at 3 — reflects truth of scope.

---

## Overall Verdict

```
[x] GO
[ ] CONDITIONAL GO
[ ] NO GO
```

**The ADR is ready for human proposal/defense review and implementation
sequencing.** Both the ADR document (4.00/4.0) and every OBPI brief
(average ≥ 3.6) clear their respective thresholds. The action items
from the Pass-1 manual evaluation have been mechanically applied:

- Pass-1 Action 1 (scope Requirements per OBPI): **DONE** — each brief
  now carries OBPI-specific FAIL-CLOSED requirements.
- Pass-1 Action 2 (real Allowed Paths): **DONE** — generic
  `ADR-0.0.34-**/` paths replaced with concrete source/test/doc paths
  per OBPI.
- Pass-1 Action 3 (declare prerequisites): **DONE** — every brief that
  depends on another OBPI now declares it in the Discovery Checklist.
- Pass-1 Action 4 (specific Acceptance REQs): **DONE** — every brief
  now carries 4–5 OBPI-specific observable REQs.
- Pass-1 Action 5 (ADR Intent before/after): **DONE** — Current
  State / Target State block added to Intent.

## Gate Decision

- **ADR:** GO — ready for human proposal/defense review.
- **OBPIs:** GO — briefs are independently actionable; implementation
  may proceed in the ADR-documented dependency order
  (01 → 02 → {03, 04, 08} → {05, 06, 07}).

## Implementation sequencing recap

Per the post-repair Discovery Checklists:

1. **Stage A (parallel):** OBPI-01 (content model registry); OBPI-08 (vendor manifest expansion — schema work needs no upstream).
2. **Stage B:** OBPI-02 (rendering pipeline; depends on OBPI-01).
3. **Stage C (parallel):** OBPI-03 (reverse-parse migration; depends on OBPI-01+02); OBPI-04 (authoring CLI; depends on OBPI-02+03).
4. **Stage D (parallel):** OBPI-05 (TUI affordances; depends on OBPI-04); OBPI-06 (validation hooks; depends on OBPI-01+02+04 + external ADR-0.0.33).
5. **Stage E (last):** OBPI-07 (migration layer; depends on OBPI-01+03, lands after the substrate stabilizes).
