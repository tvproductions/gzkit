<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR EVALUATION SCORECARD

**ADR:** ADR-0.0.11 — Persona-Driven Agent Identity Frames
**Evaluator:** Claude Haiku 4.5 (manual red-team audit)
**Date:** 2026-04-01
**Prior eval:** Deterministic eval (2026-04-01) scored 2.70 CONDITIONAL GO. This
manual red-team supersedes it with deeper analysis.

---

## ADR-Level Scores

| # | Dimension | Weight | Score (1-4) | Weighted | Rationale |
|---|-----------|--------|-------------|----------|-----------|
| 1 | Problem Clarity | 15% | 3 | 0.45 | Problem is concrete (import-split failure traced to default Assistant persona). Before/after states are clear. The "so what?" is compelling. Loses a point because behavioral improvement is not quantifiably measurable — "measurably different outcomes" is claimed but no metric is defined. |
| 2 | Decision Justification | 15% | 3 | 0.45 | Five peer-reviewed sources ground each decision. The PRISM anti-pattern (expertise claims degrade accuracy) directly justifies the critical constraint. However, **alternatives are not explicitly named and dismissed** — why markdown files over JSON config? Why a separate `.gzkit/personas/` directory rather than inline sections in existing agent profiles? Why not embed persona directly in AGENTS.md instead of a separate control surface? These are plausible alternatives that go unaddressed. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | All 6 items are independently valuable and logically ordered (research -> definition -> composition -> integration -> cleanup -> validation). Consistent granularity. **Gap:** No checklist item delivers an actual usable persona file. The architecture is fully defined but the ADR could complete all gates and produce zero working personas. OBPI-03 mentions "exemplar persona files" in allowed paths but the checklist item is "composition model," not "create example persona." |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | 6 OBPIs with domain-driven boundaries. Each is a reasonable 1-3 day unit. **Weakness:** Multiple undeclared dependencies — OBPI-03 (composition) and OBPI-06 (validation) both require the persona file format and directory from OBPI-02, but neither declares this dependency. OBPI-04 (AGENTS.md) needs the persona surface to reference. The briefs contain no dependency declarations despite a real sequencing graph. |
| 5 | Lane Assignment | 10% | 2 | 0.20 | **DEFECT:** ADR document says `Lane: Heavy` (line 33) but the ledger recorded `lane: lite` at creation time (2026-03-30T12:18:35). The `gz adr report` shows "lite" — the system treats this ADR as Lite. This is a data integrity defect. Additionally, OBPI-03 is Lite but writes exemplar persona files to `.gzkit/personas/`, a governed directory. Individual OBPI lanes (02/04 as Heavy, rest as Lite) are otherwise defensible. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | Four explicit, well-reasoned non-goals: runtime persona switching, activation-space manipulation, effectiveness measurement, concrete persona content. The ADR-0.0.12/0.0.13 lineage boundaries are precisely drawn. Best-in-class for this dimension. |
| 7 | Evidence Requirements | 10% | 3 | 0.30 | Every OBPI has concrete bash-scriptable verification commands. Quality gates are specified per-OBPI with appropriate Heavy/Lite distinctions. Minor weakness: OBPI-01 verification is keyword-grep which proves presence but not quality of synthesis. |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | References existing patterns (`.gzkit/` directory structure, AGENTS.md template, CLI registration, `sync_surfaces.py`). Integration points are listed with module paths. Anti-patterns explicitly named with examples (job-description framing, motivational-poster language). |

**WEIGHTED TOTAL: 3.00 / 4.0**

**Threshold:** >= 3.0 = GO | 2.5-3.0 = CONDITIONAL GO | < 2.5 = NO GO

**ADR-level verdict:** GO (at threshold boundary)

---

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|-------------|-------------|-------|------|---------|-----|
| 01 - Research Synthesis | 4 | 2 | 3 | 3 | 3 | 3.0 |
| 02 - Control Surface Definition | 3 | 4 | 4 | 3 | 3 | 3.4 |
| 03 - Trait Composition Model | 2 | 3 | 3 | 3 | 2 | **2.6** |
| 04 - AGENTS.md Persona Section | 2 | 4 | 4 | 4 | 3 | 3.4 |
| 05 - Supersede Pool ADR | 3 | 3 | 2 | 4 | 4 | 3.2 |
| 06 - Schema Validation | 2 | 4 | 3 | 3 | 3 | 3.0 |

### OBPI Notes

**OBPI-01:** Fully independent (can start immediately). Testability is weak —
keyword grep proves presence but not synthesis quality. Value is real: removes
need for downstream OBPIs to re-derive research.

**OBPI-02:** Core deliverable — removing it eliminates the entire ADR.
Multi-surface scope (storage, schema, CLI, loading, BDD) is ambitious but
well-specified. Moderate dependency on OBPI-01 research informing design.

**OBPI-03 (BELOW THRESHOLD):** Independence is weak — needs the persona file
format from OBPI-02 but doesn't declare it. Clarity is the critical weakness:
"orthogonal composition" is theoretically described via the PERSONA/ICLR paper
but operationally vague. What does a composition helper actually DO at the prompt
level? If two traits are "combined orthogonally," what concrete text is emitted?
The brief says "deterministic enough that two implementers would derive the same
result" but doesn't provide enough specificity for that standard.

**OBPI-04:** Undeclared dependency on OBPI-02 (needs the persona surface to
exist before referencing it). Otherwise strong — clear deliverable, concrete
verification, high value.

**OBPI-05:** Lowest individual value — administrative bookkeeping. Could be
absorbed into OBPI-01 during the research phase (reviewing the pool ADR is
already in OBPI-01's scope). A full OBPI for marking one file as superseded is
overengineered.

**OBPI-06:** Undeclared dependency on OBPI-02 for schema definition and persona
file fixtures. Can partially self-bootstrap from the ADR's schema description,
but the brief's prerequisite check (`test -d .gzkit/personas`) fails if OBPI-02
hasn't run.

**OBPI threshold:** Average >= 3.0 per OBPI. **OBPI-03 at 2.6 is below
threshold — revision required.**

**OBPI-level verdict:** CONDITIONAL GO

---

## Red-Team Challenges

| # | Challenge | Result | Notes |
|---|-----------|--------|-------|
| 1 | So What? | **FAIL** | Items 1, 2, 4, 5, 6 pass. **Item 3 (trait composition) fails.** Zero persona files exist in the repository. Composition rules for a system with no personas to compose is premature abstraction. The "so what" answer — "ADR-0.0.12 needs it" — is a dependency on future work, not a concrete capability gap today. |
| 2 | Scope | **FAIL** | **Missing from scope:** (a) No OBPI delivers an actual usable persona file — the ADR could complete all gates and produce zero working personas; (b) No migration path for the 5 existing agent profiles in `.claude/agents/`; (c) Effectiveness measurement is deferred but without it the entire effort is unfalsifiable. **Shouldn't be in scope:** OBPI-05 is a single-commit task inflated to a full OBPI. |
| 3 | Alternative | **FAIL** | **Merge candidates:** OBPI-05 into OBPI-01 (research phase already reviews the pool ADR). OBPI-03 and OBPI-06 into OBPI-02 — defining a control surface includes its composition rules and validation. Current count of 6 could be reduced to 3-4 without losing capability. |
| 4 | Dependency | **FAIL** | **OBPI-02 is a single point of failure** with undeclared downstream impact on OBPI-03, OBPI-04, and OBPI-06. If OBPI-02 is blocked: OBPI-03 cannot create exemplar personas, OBPI-04 cannot reference the surface, OBPI-06 cannot validate. Zero briefs declare dependencies despite a real DAG: `01 -> 02 -> {03, 04, 06} -> 05`. |
| 5 | Gold Standard | **PASS** | Compared against ADR-0.1.0 (enforced-governance-foundation, Validated, 10/10 OBPIs). Structural parity. Research grounding (5 peer-reviewed sources) exceeds typical. Tidy First section is a structural improvement not present in earlier ADRs. |
| 6 | Timeline | **PASS** | Critical path: `01 -> 02 -> {03, 04, 06} -> 05`. Three sequential stages with parallelization in stage 3. Reasonable. |
| 7 | Evidence | **PASS** | All 6 OBPIs have concrete verification commands: `test -f`, `rg`, `uv run gz personas list`, `uv run -m unittest`, `rg "^## Persona$"`, `rg "Superseded"`. Bash-scriptable and CI-ready. |
| 8 | Consumer | **FAIL** | A maintainer would ask: (1) "Where is an actual persona file I can look at?" — none delivered. (2) "How do I write a new persona?" — no authoring guide. (3) "What happens if I don't add a persona section?" — no enforcement mechanism described. (4) "Does this make the agent behave differently?" — deferred, unfalsifiable. |
| 9 | Regression | **PASS** | Schema validation (OBPI-06) participates in normal repo checks. Template sync via `sync_surfaces.py` ensures AGENTS.md consistency. Research citations preserved in synthesis document. BDD surface provides ongoing contract enforcement. |
| 10 | Parity | **PASS** | Weakest claim: the "operating system view" elevates a PSM research finding to a design axiom. The paper describes persona selection as a mechanism, not an ontological claim. However, the practical architecture is sound regardless — the control surface works whether or not the OS metaphor is literally true. |

**Red-team results: 5 FAIL, 5 PASS**

**Red-team threshold:** <= 2 = GO | 3-4 = CONDITIONAL GO | >= 5 = **NO GO**

**Red-team verdict: NO GO**

---

## Overall Verdict

| Gate | Score | Threshold | Result |
|------|-------|-----------|--------|
| ADR Quality | 3.00 | >= 3.0 = GO | GO (at boundary) |
| OBPI Quality | OBPI-03 = 2.6 | Avg >= 3.0 | CONDITIONAL GO |
| Red-Team | 5 failures | <= 2 = GO | **NO GO** |

### VERDICT: NO GO — Structural revision required before proposal/defense review

---

## Action Items (Ranked by Severity)

### 1. No OBPI delivers a usable persona (Challenges 2, 8)

The ADR defines architecture for persona files but no OBPI ensures one gets
created. After completing all 6 OBPIs, the repository could have: a governed
directory, a CLI command, a composition model, validation infrastructure, and a
template update — but zero working persona files. This is architecture without
a payload. ADR-0.0.12 writes the profiles, but ADR-0.0.11 should deliver at
least one exemplar as proof-of-concept.

**Fix:** Add an exemplar persona deliverable to OBPI-02 or OBPI-03 (a minimal
valid `.gzkit/personas/implementer.md` that passes schema validation and
demonstrates the composition model).

### 2. Undeclared dependency graph with single point of failure (Challenges 3, 4)

OBPI-02 is the critical dependency for OBPI-03, OBPI-04, and OBPI-06, but no
brief declares this. The decomposition also contains artificially separate OBPIs
(OBPI-05 is a single-commit task, OBPI-03 and OBPI-06 are inseparable from
OBPI-02's surface definition).

**Fix:** Either (a) declare dependencies explicitly in each brief, or (b)
consolidate: merge OBPI-05 into OBPI-01, merge OBPI-06 into OBPI-02, and
consider merging OBPI-03 into OBPI-02. This yields a tighter 3-4 OBPI
decomposition with honest independence.

### 3. Lane discrepancy between ADR document and ledger (Dimension 5)

ADR document states `Lane: Heavy` (line 33) but ledger recorded `lane: lite`.
The `gz adr report` treats the ADR as Lite. This is a data integrity defect.
Given that OBPI-02 and OBPI-04 are Heavy (new CLI surface, AGENTS.md contract),
the parent ADR lane should be Heavy. The parent lane sets the attestation floor
for Lite children.

**Fix:** Correct the ledger to `lane: heavy` or re-register with the correct
lane. This is a blocking defect affecting gate obligations for all 6 OBPIs.

### 4. OBPI-03 (Trait Composition) needs operational clarity

Scored 2.6/4.0 (below threshold). "Orthogonal composition" is theoretically
described but operationally vague. The brief should specify what a composition
helper concretely produces — given specific trait/anti-trait inputs, what
concrete output is emitted?

**Fix:** Add a concrete example to the brief showing input traits, anti-traits,
and the resulting composed persona text. Define the operation precisely enough
that two implementers would produce the same result.

### 5. Missing alternative analysis in Decision section

Decisions are research-grounded but never name and dismiss alternatives. Key
alternatives to address: why separate persona files vs. inline in agent
profiles? Why markdown vs. structured JSON/YAML? Why a governed directory vs.
embedding in AGENTS.md?

**Fix:** Add an "Alternatives Considered" section to the Decision.
