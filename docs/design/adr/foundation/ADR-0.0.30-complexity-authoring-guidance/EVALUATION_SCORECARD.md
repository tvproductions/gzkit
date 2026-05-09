ADR EVALUATION SCORECARD
========================

ADR: ADR-0.0.30 — Complexity Authoring Guidance
Evaluator: Claude (manual — supersedes CLI pre-screen)
Date: 2026-05-09

CLI Pre-screen (for traceability): 3.85/4.0 — GO
(CLI flagged D1 at 3; manual review upgrades to 4 — see reconciliation notes)

---

## ADR-Level Scores

| # | Dimension | Weight | CLI | Manual | Weighted | Rationale |
|---|-----------|--------|-----|--------|----------|-----------|
| 1 | Problem Clarity | 15% | 3 | **4** | 0.60 | See reconciliation note below |
| 2 | Decision Justification | 15% | 4 | 4 | 0.60 | Six numbered rationale points each with an independent "because"; 12 alternatives with specific rejections; decisions cross-reference ADR-0.0.28 §AC#5, `.claude/rules/cli.md`, ADR-0.0.19 |
| 3 | Feature Checklist | 15% | 4 | 4 | 0.60 | Five items, each independently necessary; the Decomposition Scorecard derives the count mechanically; no redundancy; no visible gap |
| 4 | OBPI Decomposition | 15% | 4 | 4 | 0.60 | Sequencing declared (03→01→{02‖04}→05); acyclic dependency graph with explicit parallelization; Denied Paths enforce domain boundaries |
| 5 | Lane Assignment | 10% | 4 | 4 | 0.40 | All five OBPIs Heavy: CLI subcommand, operator-facing skill, runtime data contract, editor-facing protocol spec, skill amendment — all touch external contracts; BDD waivers in OBPI-02 and OBPI-03 correctly registered |
| 6 | Scope Discipline | 10% | 4 | 4 | 0.40 | Seven explicit non-goals with named responsible ADRs; three pool-stub forward references named; OBPI Denied Paths mechanically enforce scope at implementation time |
| 7 | Evidence Requirements | 10% | 4 | 4 | 0.40 | Every OBPI brief carries a Verification command block; bash-script-verifiable acceptance criteria with REQ IDs; Gate 1–5 completion checklists |
| 8 | Architectural Alignment | 10% | 4 | 4 | 0.40 | Mechanical surfaces list specific file paths; integration points call out module paths; anti-patterns named (projection direction invariant, TCP/HTTP rejection, separate-schema rejection); STOP-on-BLOCKERS gates prevent sequencing drift |

**MANUAL WEIGHTED TOTAL: 4.0/4.0**
THRESHOLD: 3.0 (GO), 2.5 (CONDITIONAL GO), <2.5 (NO GO)

### Dimension 1 — CLI Reconciliation (false negative)

CLI score: **3**. Finding: "No after/target-state language in Intent."
Manual score: **4**.

The CLI heuristic searched for explicit "before:" / "after:" keyword tokens. The ADR
carries the content in different phrasing:

- *Before*: "without ADR-0.0.30, the advise band of ADR-0.0.28 has no consumer surface
  — the band exists but does nothing" (Intent §2 and Decision rationale #2) with
  precedent evidence from ADR-0.0.28 §AC#5 rejection.
- *After*: "surfaces complexity hints to the developer while they are authoring code,
  before the metric crosses any band, so refactor decisions land at design time rather
  than at gate time" (Intent §1).

All five Problem Clarity checklist items pass with path-level evidence:

1. One-sentence statement without jargon: "The advise band of ADR-0.0.28 has no
   consumer surface; the developer receives no complexity signal before gate time." ✓
2. Concrete "before" state with evidence: "the band exists but does nothing" + cited
   ADR-0.0.28 §AC#5 rejection as foundation for the claim. ✓
3. Concrete "after" state that is testable: three pathways (CLI, editor protocol,
   `gz justify` integration) with acceptance criteria per OBPI. ✓
4. "So what?" test: "refactor decisions land at design time rather than at gate time"
   — compelling developer-facing consequence. ✓
5. Problem explicitly scoped: "the fourth and closing foundation in the four-ADR
   complexity-doctrine cluster" bounds the problem to the cluster's remaining gap. ✓

**Note on "quantified" (D1 framework criterion):** The `4` criterion requires "quantified"
problem statement. This ADR's quantification is structural, not numerical: "the advise
band has no consumer" is a precise, verifiable structural fact, not a vague concern. For
governance/tooling ADRs where numerical developer-impact data is not available, structural
quantification ("band X has zero consumers") satisfies the intent of the criterion. If
"quantified" is read strictly as requiring a number (e.g. "X% of developers hit gate-time
surprises"), the correct score is 3 — which still gives 3.85/4.0 and a GO verdict.
This manual scorecard holds at 4; readers may apply 3 without changing the verdict.

---

## OBPI-Level Scores

| OBPI | Independence | Testability | Value | Size | Clarity | Avg | Notes |
|------|-------------|-------------|-------|------|---------|-----|-------|
| 01 — CLI verb | **3** | 4 | 4 | 4 | 4 | **3.8** | CLI scored Independence=4 (false positive — see note) |
| 02 — skill | **3** | 4 | 4 | 4 | 4 | **3.8** | CLI scored Independence=4 (false positive) |
| 03 — hint engine | **3** | 4 | 4 | 3 | 4 | **3.6** | CLI scored Independence=4 (false positive) |
| 04 — editor protocol | **3** | 4 | 4 | 3 | 4 | **3.6** | CLI scored Independence=4 (false positive) |
| 05 — justify integration | **3** | 4 | 4 | 3 | 4 | **3.6** | CLI scored Independence=4 (false positive) |

OBPI THRESHOLD: Average >= 3.0 per OBPI. Any dimension scoring 1 must be revised.
All five OBPIs pass. No dimension scored below 3.

### OBPI Independence — CLI Reconciliation (systematic false positive)

CLI scored all five OBPIs at Independence=4 (fully independent). Manual scores
all at 3 (depends on declared predecessors).

The framework defines:
- 4 = Fully independent
- 3 = Depends only on declared predecessors

Every brief carries a STOP-on-BLOCKERS gate documenting predecessor dependencies:

- OBPI-01: STOP if OBPI-03's hint engine is not landed
- OBPI-02: STOP if OBPI-01's CLI verb is not registered
- OBPI-03: STOP if ADR-0.0.29-01 schema and ADR-0.0.29-02 engine are not landed
- OBPI-04: STOP if OBPI-03's `AuthoringHint` model and engine are not landed
- OBPI-05: STOP if OBPI-03's `engine.analyze` interface is not landed

These are *declared* dependencies, which is the correct discipline — they earn a 3,
not a 4. The CLI heuristic did not detect STOP-on-BLOCKERS prose as a dependency
marker, producing a false positive of 4 across the board.

### OBPI Size scores — rationale

- OBPI-01 (CLI verb): Size=4. One command file (~80-100 lines), test file, manpage,
  feature file, runbook entry. Clearly 1-2 days.
- OBPI-02 (skill): Size=4. One SKILL.md + vendor mirrors + test file. 1 day.
- OBPI-03 (hint engine): Size=3. `hint.py` + `engine.py` + JSON schema + `__init__.py`
  + two test files with 10 REQs. Non-trivial frozen Pydantic model + projection
  semantics + precedence-band boundary computation. 2-3 days, might push 4.
- OBPI-04 (editor protocol): Size=3. `protocol.py` (Content-Length framing, dispatch,
  versioning, error handling) + JSON schema + specification document + test file + BDD
  scenario. 3-4 days.
- OBPI-05 (justify integration): Size=3. Amend skill + vendor mirrors + extend rendering
  pipeline + fail-open logging + two test files + BDD scenarios. 2-3 days.

---

## Overall Verdict

**[x] GO — Ready for proposal/defense review**

ADR manual weighted total: **4.0/4.0** (threshold 3.0)
OBPI averages: 3.6–3.8, all above 3.0 threshold
No dimension scored 1 at any level

### Strengths

1. **Cluster closure discipline.** The ADR explicitly positions itself as the closing
   member of the four-ADR complexity-doctrine cluster and names its role precisely:
   it consumes ADR-0.0.28's advise band (the only band with no prior consumer) and
   ADR-0.0.29's `AdvisorDiagnosis` schema. The "dead doctrine" framing is concrete.
2. **Projection invariant is non-negotiable.** The full→light, never-reverse projection
   direction is stated in the rationale, the Persona, the Consequences, and each
   consuming OBPI. Drift at implementation time is structurally blocked.
3. **Scope boundary is precise.** Seven non-goals named with responsible-ADR attribution.
   Pool-stub forward references for three known future concerns (reference editor
   implementation, doctrine-amendment-protocol, attestation-quality-measurement).
4. **OBPI briefs are implementation-grade.** STOP-on-BLOCKERS gates, Allowed/Denied
   Paths, field-level REQ specifications, and explicit BDD waivers indicate
   implementation-ready briefs.
5. **Comparator Uplift section.** The Kiro/Spec-Kit note anchors the authoring-guidance
   framing in a current operator-bandwidth concern and names the source-anchor
   requirement to prevent "plausible but unwitnessed planning prose" — the anti-vibe
   variant of the OEE doctrine.

### Minor Observations (no action required)

- **OBPI-04 size:** The editor-protocol implementation (Content-Length framing + dispatch
  + versioning + specification document) is the most scope-dense brief and could push 4
  days. The BDD waiver is NOT registered for OBPI-04 (it has a real BDD scenario at
  `features/authoring_guide_protocol.feature`), which is correct — but the implementation
  window for this OBPI should be planned generously.
- **Advise-band calibration.** Negative consequence #8 acknowledges the first-distillation
  cold-start problem honestly. The tightening trigger (next distillation pass per cluster
  cadence) is named. No action required; the observation is made visible.
- **OBPI-04 adds `--server` flag to OBPI-01's CLI contract.** REQ-0.0.30-04-06 (line 586
  in the brief) notes this flag is "an additive amendment to OBPI-01's contract" and
  argues it is not a Denied Path violation because "OBPI-01's denied-paths list does NOT
  exclude additive flag amendments." This is correct — but the implementer of OBPI-04
  needs to be aware that they will touch `src/gzkit/commands/complexity_guide.py` (which
  IS on OBPI-01's Allowed Paths). The brief handles this via explicit reasoning rather
  than a path-level allowance. Suggest the operator confirm sequencing when OBPI-04
  reaches implementation to ensure OBPI-01 has landed first.

### Action Items

1. **OBPI-04 cross-OBPI edit of OBPI-01's CLI file — confirm sequencing before implementation.**
   REQ-0.0.30-04-06 has OBPI-04 add a `--server` flag to
   `src/gzkit/commands/complexity_guide.py`, which is on OBPI-01's Allowed Paths list.
   This is not a denied-paths violation, but OBPI-04 edits a file authored by OBPI-01 —
   a reverse-direction cross-OBPI edit that the brief handles by argument, not by
   path-level rule. Before OBPI-04 starts implementation: (a) confirm OBPI-01 has
   landed, (b) consider whether OBPI-01's brief should explicitly permit the additive
   `--server` flag amendment to remove the implicit-permission ambiguity.

The remaining observations in the Strengths and Minor Observations sections are
informational and do not block GO.
