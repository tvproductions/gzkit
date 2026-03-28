<!-- markdownlint-disable-file MD013 -->

# ADR Evaluation Scorecard

**ADR:** ADR-0.40.0 — Reporter Rendering Infrastructure
**Evaluator:** Claude Opus 4.6 (gz-adr-eval)
**Date:** 2026-03-28

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted |
|---|-----------|--------|-------------|----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 |
| 2 | Decision Justification | 15% | 3 | 0.45 |
| 3 | Feature Checklist | 15% | 3 | 0.45 |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 |
| 5 | Lane Assignment | 10% | 4 | 0.40 |
| 6 | Scope Discipline | 10% | 3 | 0.30 |
| 7 | Evidence Requirements | 10% | 3 | 0.30 |
| 8 | Architectural Alignment | 10% | 3 | 0.30 |

**WEIGHTED TOTAL: 3.10/4.0**
**THRESHOLD: 3.0 (GO)**

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 — Reporter module scaffold | 4 | 4 | 4 | 3 | 4 | 3.8 |
| 02 — Common rendering helpers | 3 | 4 | 3 | 4 | 3 | 3.4 |
| 03 — Status/report table migration | 3 | 3 | 4 | 3 | 3 | 3.2 |
| 04 — List table migration | 3 | 3 | 3 | 3 | 3 | 3.0 |
| 05 — Ceremony panel migration | 3 | 3 | 4 | 3 | 3 | 3.2 |

**OBPI THRESHOLD: All averages >= 3.0, no dimension scores 1. PASS**

## Scoring Rationale

### Dimension 1 — Problem Clarity (Score: 3)

The problem is well-stated: fragmented CLI output with ad-hoc Rich table construction and hand-padded Unicode box strings. Before state (inconsistent styling, alignment bugs) and after state (centralized reporter module, deterministic rendering) are clear. The "so what" passes — visual inconsistency and non-deterministic ceremony output are real operator-facing problems. Scope is explicit: rendering only, not data or business logic. Held from 4 because the problem is not quantified (no count of affected commands, no specific alignment bug examples).

### Dimension 2 — Decision Justification (Score: 3)

The rationale section cites airlineops as precedent and explicitly dismisses the alternative of appropriating the full manifest/schema/eligibility infrastructure in favor of portable rendering patterns only. The Critical Constraint section ("OutputFormatter continues to own mode routing; commands produce data dicts; reporter renders them") provides separation-of-concerns reasoning. The Anti-Pattern Warning ("reporter absorbing business logic") addresses a foreseeable counterargument. Held from 4 because there is no formal Alternatives Considered section — alternatives are implicit rather than enumerated. Decisions like box style choices (ROUNDED/DOUBLE) and module file structure are specified but not individually defended.

### Dimension 3 — Feature Checklist (Score: 3)

Five items at consistent granularity: scaffold → helpers → three migration targets by command type. Each item maps to a testable deliverable. Removal of any item leaves a visible gap — no scaffold means no presets, no helpers means migration code duplicates formatting utilities, each migration target covers a distinct command surface. Logical ordering supports incremental delivery. Held from 4 because error/progress output rendering is not addressed (arguably out of scope but not explicitly excluded).

### Dimension 4 — OBPI Decomposition (Score: 3)

Five OBPIs with clear domain boundaries. OBPI-01 is the natural prerequisite; OBPI-02 supplements it; OBPIs 03-05 are three independent migration targets that can parallelize after the foundation. Each is a 1-3 day unit. Dependency graph is acyclic with single root (01). Numbering is sequential with no gaps. Held from 4 because the three migration OBPIs (03-05) vary in surface area — status commands (03) are the largest migration surface while ceremony panels (05) are the smallest — but all receive equal treatment.

### Dimension 5 — Lane Assignment (Score: 4)

Exemplary. OBPI-02 is correctly scoped as Lite (internal helpers with no output contract change). All four remaining OBPIs are correctly Heavy — each changes external CLI output appearance. Each OBPI brief includes a Quality Gates section with the correct gate set for its lane (Gates 1-2 for Lite, Gates 1-4 for Heavy). The ADR includes lane definitions with clear criteria.

### Dimension 6 — Scope Discipline (Score: 3)

Scope is well-controlled through the Critical Constraint, Anti-Pattern Warning, and per-OBPI Non-Goals sections. Three substantive non-goals are identifiable: (1) reporter must not absorb business logic, (2) JSON/plain output stays in OutputFormatter, (3) no data or behavioral changes. The Anti-Pattern Warning provides a concrete "what wrong looks like" test. Held from 4 because non-goals are distributed across sections rather than in a dedicated Non-Goals section at the ADR level.

### Dimension 7 — Evidence Requirements (Score: 3)

The Evidence section names specific artifact paths for all four gates: unit tests, BDD features, and docs. OBPI-01's completed brief includes concrete verification ("20/20 unit tests pass, 6/6 BDD scenarios pass" + command). Other OBPI briefs list gate requirements with allowed paths but not explicit verification commands. Held from 4 because "derivable" verification is weaker than "explicitly stated" — OBPIs 02-05 would benefit from concrete commands in their Quality Gates sections.

### Dimension 8 — Architectural Alignment (Score: 3)

The ADR references airlineops `rich_renderers_common.py` as the source exemplar and names six integration points with full module paths. The Anti-Pattern Warning provides a concrete architectural boundary test. The decision to retain OutputFormatter for mode routing follows the existing separation pattern. Held from 4 because individual technical decisions (module file structure, box style choices, data dict interface) don't individually reference local precedent — the airlineops reference covers the overall approach but not every implementation detail.

### OBPI-Specific Notes

**OBPI-01 (Avg 3.8):** Strongest brief. Fully independent, clear signatures, specific box styles per preset, 6 requirements that are each testable. Completed with concrete evidence (20/20 tests, 6/6 BDD).

**OBPI-02 (Avg 3.4):** Correctly Lite. Three specific helper functions named. Small scope. "format negotiation" could be more specific — what modes does it negotiate between?

**OBPI-03 (Avg 3.2):** Largest migration surface (status, adr report, state). Value is high — these are the most frequently run governance commands. Requirement 5 ("No behavioral change") is a good guardrail.

**OBPI-04 (Avg 3.0):** Adequate but the lowest-scoring OBPI. Four commands to migrate with similar patterns — risk of being mechanical rather than domain-driven. Value is lower because list commands are less critical than status commands.

**OBPI-05 (Avg 3.2):** Eliminates the most visible quality problem (hand-padded box art). Value is high. The optional CLI command ("gz reporter ceremony-box") adds slight ambiguity — is it in scope or not?

## Overall Verdict

**[x] GO — Ready for proposal/defense review**

ADR weighted total (3.10) clears the 3.0 GO threshold. All OBPI averages >= 3.0 with no dimension scoring 1. The ADR demonstrates strong scope discipline, correct lane assignments, and well-bounded OBPI decomposition.

### Action Items (minor, non-blocking)

1. **Add Alternatives Considered section** — Explicitly enumerate and dismiss alternatives (extend OutputFormatter, Jinja templating, full airlineops reporter import) to strengthen D2 from 3 to 4
2. **Add explicit verification commands per OBPI** — Each brief should state the exact bash commands that prove completion, not just gate categories
3. **Consolidate Non-Goals** — Add a dedicated Non-Goals section at the ADR level that aggregates the distributed constraints into one scannable list
4. **Clarify OBPI-05 optional CLI command** — State whether `gz reporter ceremony-box` is in scope or deferred to future work
