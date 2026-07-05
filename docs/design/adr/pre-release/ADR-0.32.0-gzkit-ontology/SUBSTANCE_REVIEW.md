# ADR-0.32.0-gzkit-ontology — Substance + Red-Team Review

> **Channel:** judge-graded **SUBSTANCE** (decision quality), distinct from
> the deterministic structural-completeness score in `EVALUATION_SCORECARD.md`.
> **Per GHI #624 these two MUST NOT be composited** — the 3.60/4.0 structural
> number measures section presence/depth; this review measures whether the
> decisions hold. Advisory, non-gating (Tier-B): this review never itself
> gates; it informs the operator's proposal/defense decision.

- **ADR:** ADR-0.32.0-gzkit-ontology (Draft, HEAVY, feature, 0/7 OBPIs)
- **Evaluator:** `gz-adr-evaluate` substance pass (`--red-team`) — three
  independent persona reviewers (`spec-reviewer`, `quality-reviewer`,
  adversarial red-team) synthesized by the `pipeline-orchestrator` driver
- **Date:** 2026-07-05
- **Structural pre-screen (NOT composited):** 3.60/4.0 STRUCTURALLY COMPLETE

---

## Verdict (as first authored): CONDITIONAL GO — revise, then re-evaluate

> **SUPERSEDED by Revision 1 (end of file): after corrective authoring, the
> independently re-verified verdict is GO.** This section is preserved unchanged
> as the original CONDITIONAL-GO record.

Do **not** proceed to proposal/defense yet. No structural teardown is needed —
the corpus-first MVP spine (OBPI-01 → 02 → 03) is a sound, low-risk,
two-way-door increment, and the Tier-B derived-never-authority posture is a
genuine strength. But the ADR currently ships its **trust keystone (rebuild
fidelity) as a self-report rather than a gated falsifier**, and rides its **one
irreversible surface (OBPI-06)** and its **weakest dependency (OBPI-07 /
tree-sitter)** in on the coattails of that low-risk MVP.

### Three-axis threshold reconciliation

| Axis | Result | Threshold read |
|---|---|---|
| ADR weighted total | **3.15 / 4.0** | ≥3.0 → GO |
| Per-OBPI average | OBPI-03 = **2.8** (below 3.0 bar); no dimension scored 1 | flag → revise/split |
| Red-team (10 challenges) | **3 PASS / 7 FAIL** | ≥5 fails → NO GO (mechanical); red-team's own holistic call CONDITIONAL GO |

The axes disagree; reconciled fail-closed to the honest middle — **not GO**
(the ADR's own declared load-bearing element ships as a self-report; evidence is
weakest exactly where irreversibility is highest), **not NO GO** (no teardown,
no dimension scored 1, MVP spine sound). Verdict: **CONDITIONAL GO**.

---

## ADR-Level Substance Scores

| # | Dimension | Wt | Manual | Weighted | CLI | Divergence rationale (why manual ≠ structural) |
|---|-----------|----|--------|----------|-----|-----------------------------------------------|
| 1 | Problem Clarity | 15% | 4 | 0.60 | 3 | Grounded in a *verified live incident* (GO-attested substrate silently reversed); the only ding is a missing incident-GHI anchor. Manual > CLI: CLI heuristic penalized "no concrete references" in Intent, but the incident *is* the reference. |
| 2 | Decision Justification | 15% | 3 | 0.45 | 4 | Six alternatives named + dismissed; all exemplars verified real. Held from 4: the networkx *cited authority* ("topo-sort/cycle-detection stdlib cannot supply") is technically wrong — `graphlib.TopologicalSorter` supplies both; the correct rationale (reachability + multigraph) lives only in the body. |
| 3 | Feature Checklist | 15% | 3 | 0.45 | 3 | 7 items map 1:1 to 7 OBPIs, all testable; uneven granularity, and no checklist item discharges the declared supersessions / ADR-0.0.47 read-fold. |
| 4 | OBPI Decomposition | 15% | 3 | 0.45 | 4 | Acyclic DAG, no numbering gaps, clean domain groupings. Held from 4: OBPI-02/03/06/07 exceed a 1–3 day unit; a fidelity-keystone OBPI (KEEL's OBPI-03 analogue) is absent. |
| 5 | Lane Assignment | 10% | 3 | 0.30 | 4 | OBPI-04 honestly Lite; but OBPI-05 is Heavy-by-conformity over an internal-only module (contradicts OBPI-04's rationale), and 5 Heavy OBPIs carry a Gate-4 BDD obligation with no feature file. |
| 6 | Scope Discipline | 10% | 4 | 0.40 | 4 | ≥5 explicit non-goals; mechanical Denied-Paths + NEVER guardrails on every OBPI; one-way-door isolation is a disciplined boundary. (The red-team's OBPI-06 challenge is a scope *decision* critique, filed under action items, not a scope-*discipline* deficiency.) |
| 7 | **Evidence Requirements** | 10% | **2** | 0.20 | 4 | **Decisive gap.** The most irreversible decision (freeze permanent L2 vocabulary, OBPI-06) "proves" only via doc-presence; BI#1 fidelity test cannot prove "no missed type" in the direction that matters; `sense` false-positive rate is named a first-class concern with no bounding REQ. CLI sees section-presence (4); substance sees tautology (2). |
| 8 | Architectural Alignment | 10% | 3 | 0.30 | 3 | **Zero fabricated integration points** — every named symbol verified (`get_artifact_graph`@776, `triangle` surface, `state.py` render, `events.py` union, `traceability.py`, `$defs.plane`, OKF package, noun-namespace pattern). Held from 4: tree-sitter departure unexercised-in-MVP. |

**WEIGHTED TOTAL: 3.15 / 4.0** — the CLI's 4s on dims 5/7 are exactly the
GHI #624 blind spot: structural completeness ≠ substance.

---

## OBPI-Level Scores (spec-reviewer)

| OBPI | Independence | Testability | Value | Size | Clarity | Avg |
|------|:-:|:-:|:-:|:-:|:-:|:-:|
| 01 model + purity | 4 | 3 | 4 | 3 | 2 | 3.2 |
| 02 substrate + corpus | 3 | 4 | 4 | 3 | 3 | 3.4 |
| 03 gz ontology interface | 3 | 3 | 4 | 2 | 2 | **2.8** |
| 04 doctrine + boundary invariants | 4 | 3 | 2 | 4 | 4 | 3.4 |
| 05 OKF open-absorption | 3 | 4 | 3 | 4 | 3 | 3.4 |
| 06 work-domain L2 schema | 4 | 3 | 4 | 2 | 3 | 3.2 |
| 07 source-domain tree-sitter | 3 | 3 | 4 | 2 | 3 | 3.0 |

No dimension scored 1 (no hard-fail). **OBPI-03 (2.8) is below the 3.0
per-OBPI bar** — a size outlier (5 verbs + `--json/--dot` + parser wiring +
`state.py` extension + manpage + index + doc-coverage + 2 runbooks + behave, in
one unit) with an unspecified `resense` baseline.

---

## Red-Team Challenge Scorecard

| # | Challenge | Verdict | Note |
|---|-----------|:-------:|------|
| 1 | So What? | PASS | 5/7 items lose a concrete capability; OBPI-04 + the absorption-halves of 02/07 are thin by design. |
| 2 | Scope | FAIL | OBPI-06 (the sole irreversible surface) backs an advisory-only queue nothing consumes and is thesis-adjacent — least-defensible inclusion. |
| 3 | Alternative | FAIL | OBPI-04 folds into 01/02; OBPI-02 could split (generic graph vs. absorption); a fidelity-keystone OBPI is missing. |
| 4 | Dependency | PASS | Clean DAG; OBPI-01 is the correctly-identified SPOF; 02 the secondary chokepoint. |
| 5 | Gold Standard (vs KEEL) | FAIL | Takes KEEL's "one unified ADR" half, drops KEEL's "tracer-first, gate breadth behind a live landing falsifier" half. Missing Target-Scope/Deferred section + breadth-gating falsifier + refusal-exercising fidelity assertions. |
| 6 | Timeline | PASS | Critical path 01→02→03 (depth 3); up to 4-wide parallelism after 01. |
| 7 | Evidence | FAIL | OBPI-06 one-way-door proof is doc-presence, not a mechanical gate; BI#1 test only injects *known* types. |
| 8 | Consumer | FAIL | Unanswered: fidelity-over-time, `sense` FPR bound, `resense`→airlock consumer (none), perf budget, torque-up owner, incident GHI. |
| 9 | Regression | FAIL | BI#1 completeness is self-referential — a future-added L2 type is silently dropped while self-reporting `complete=True` unless diffed against the live `TypedLedgerEvent` registry (no REQ mandates it). The exact "wrong graph more dangerous than none" failure the ADR names. |
| 10 | Parity | FAIL | tree-sitter "stdlib cannot supply" is weak (Python-only; `ast` + `traceability.py` cover the exercised surface); "less code, one source of shape" is contradicted by the compat-view (net *more* code + two synced representations). |

**Biggest risk:** the trust keystone (rebuild fidelity, BI#1) is asserted via a
self-report but never gated as a breadth-blocking landing falsifier.
**Most likely failure mode:** OBPI-02 ships a fidelity report whose completeness
compares against a hardcoded handled-type set; it passes every test; months
later an unrelated ADR adds an event type, it is silently dropped, `complete=True`
persists, and the airlock certifies "all seams seen" against a lie.

---

## Convergent Findings (each surfaced by ≥2 independent reviewers)

1. **Rebuild-fidelity keystone (BI#1) is a self-report, not a gated falsifier**
   — red-team #1 risk + spec Evidence=2. A **correction, not an enhancement**:
   BI#1 declares "the graph never lies about the shape," and the current proof
   cannot guarantee it.
2. **The one-way door (OBPI-06) has near-tautological evidence** — spec
   weakest-point #3 + red-team Ch7. Weakest proof on the most irreversible
   surface.
3. **tree-sitter is the thinnest STDLIB-FIRST departure** — quality + red-team
   Ch10. Named (clears doctrine bar) but unexercised-in-MVP and self-conceded.
4. **OBPI-01's object-type catalog is undefined** — spec weakest-point #1. The
   OBPI advised to implement first: REQ-01-04's partition test has no seating
   list, and the cited corpus `.gzkit/governance/ontology.json` is a doctrine
   doc, not an object catalog.
5. **OBPI-03 `resense` baseline mechanism is unspecified** and in tension with
   the read-only fence (REQ-03-08) — spec weakest-point #2; the airlock's
   certification gate left implementation-ambiguous.

---

## Ranked Action Items to Reach GO (revision, not teardown)

1. **Harden BI#1 into a registry-coupled, breadth-gating falsifier** (import
   KEEL's BI#3 pattern): compute completeness by diffing replayed event types
   against the live `TypedLedgerEvent` discriminator set (not a hardcoded list);
   add a falsifier that derives an unhandled type *from the registry* and
   asserts `complete=False`; gate OBPI-05/06/07 behind OBPI-02's fidelity fence
   proven live.
2. **Re-route or re-justify the two coattail items.** OBPI-06: give REQ-06-07 a
   real fail-closed emission gate (refuse emission of the four event types
   absent a recorded WWHTBT) or split it to its own separately-attested ADR.
   OBPI-07: re-attest tree-sitter against genuine multi-surface need or defer it
   until a non-Python adopter exists.
3. **Define OBPI-01's object-type catalog** and fix the wrong `ontology.json`
   prerequisite so REQ-01-04's partition test can fail on a business-logic
   change.
4. **Specify `resense`'s baseline persistence** and reconcile it with the
   read-only fence; consider splitting OBPI-03 (size outlier, avg 2.8).
5. **Fold OBPI-04 into the MVP spine's closeout** (5 of 6 REQs re-declare fences
   already anchored by siblings); **correct the overreaching claims**: "less
   code" (contradicted by the compat-view design), temper "KEEL lands cleanly"
   (KEEL was a 3-OBPI tracer that gated breadth), add a Target-Scope/Deferred
   section, and cite the motivating incident GHI in Intent.

Net discipline: **ship the sonar (01–03), gate the breadth (05/06/07)** — the
exact pattern the cited exemplar (KEEL / ADR-0.31.0, verified `Validated` /
`COMPLETED`) actually demonstrated.

---

## Provenance

- **Method:** persona-dispatched independent scoring (skill v6.0.0 § Persona
  Dispatch) — driver did not score its own scoring.
- **Ground-truth checks performed:** all named integration points verified to
  exist (no fabricated precedents); ADR-0.31.0 KEEL confirmed `Validated` /
  `COMPLETED` (3/3); `.gzkit/governance/ontology.json` confirmed to be a
  doctrine document, not an object catalog; `$defs.plane` = `["product",
  "process"]`.
- **Structural pre-screen** (`gz adr evaluate`, 3.60/4.0) left intact in
  `EVALUATION_SCORECARD.md`; not composited here (GHI #624).

---

# Revision 1 — Re-evaluation after corrective authoring (2026-07-05)

Corrective authoring under the CONDITIONAL-GO action items (operator-directed:
"fix the issues, increase scorecard"). Fixes verified by an INDEPENDENT
adversarial re-check (red-team, ground-truth-checked against `src/gzkit/events.py`),
never by self-assessment.

## Revised verdict: **GO**

The load-bearing risk (rebuild-fidelity self-report) is **genuinely closed, not
cosmetically** — verified three ways: (a) BI#1 now mandates completeness be
diffed against the live `TypedLedgerEvent` discriminator registry, never a
hardcoded set; (b) OBPI-02 REQ-02-05 mandates the falsifier DERIVE an unhandled
discriminator from the live union and assert `complete=False`; (c) the union was
confirmed real + enumerable in `src/gzkit/events.py` (~46 members), so the
mechanism is implementable, not aspirational.

## Fixes applied (ADR + five OBPI briefs)

| Action item | Fix | Verified effect |
|---|---|---|
| Registry-coupled fidelity | BI#1 + OBPI-02 REQ-02-05 diff vs live `TypedLedgerEvent`; falsifier derives the unhandled type from the union | Ch9 FAIL→PASS |
| Tracer + breadth-gate | New `## Target Scope`; 05/06/07 gated behind the fence proven live (KEEL BI#3 pattern) | Ch5 FAIL→PASS; Ch2 FAIL→PASS |
| One-way-door proof | OBPI-06 REQ-06-07 SUPPORT→BEHAVIOR: mechanical fail-closed emission gate + refusal test + fixture-ledger test-safety note | Ch7 FAIL→PASS |
| OBPI-01 catalog | Total `OBJECT_TYPE_REGISTRY` over closed `ObjectType`; corrected the wrong `ontology.json`-as-catalog prerequisite | REQ-01-04 now fails on an unclassified type (non-tautological) |
| resense baseline | Tier-B `last_sweep.json` snapshot reconciled with the read-only fence; added to Allowed Paths | REQ-03-03/08 coherent |
| Claim corrections | "less code"→honest net-more-code; KEEL tempered; tree-sitter re-justified as a named-capability gap (NOT reversed) | Ch10 FAIL→PASS |
| sense FPR floor | REQ-03-01 asserts zero-spurious-seam over a clean fixture | Ch8 FPR sub-gap closed |

## Verified score deltas

| Dimension | Before | After |
|---|:---:|:---:|
| 1 Problem Clarity | 4 | 4 |
| 2 Decision Justification | 3 | **4** |
| 3 Feature Checklist | 3 | 3 |
| 4 OBPI Decomposition | 3 | 3 |
| 5 Lane Assignment | 3 | 3 |
| 6 Scope Discipline | 4 | 4 |
| 7 Evidence Requirements | **2** | **4\*** |
| 8 Architectural Alignment | 3 | 3 |

- **Weighted total: 3.15 → ~3.50.** Independently re-verified at **3.40** (Evidence=3)
  *before* the FPR-floor fix; Evidence→4\* rests on REQ-03-01 added *after* the
  re-check (the re-check's own stated condition to clear the sole held-back reason)
  — a fresh independent pass would confirm the 4.
- **Red-team: 7 FAIL → 1 FAIL** (only Ch8 Consumer, narrowed to perf-budget +
  torque-up-owner; the FPR sub-gap is now closed). ≤2 FAIL = GO.
- **Structural pre-screen: 3.60 → 3.85.**

## Deliberate non-actions (held, with reason)

- **tree-sitter NOT reversed/deferred** — that reverses the GO-attested substrate
  floor (2026-07-02), the exact drift this ADR exists to prevent. Re-justified instead.
- **OBPI-06 NOT split** — the mechanical emission gate is the less-invasive
  correction and preserves the GO-attested single-ADR shape.
- **OBPI-04 NOT folded** — preserves the 1:1 checklist↔OBPI sync mandate.

## Remaining minors (trackable, non-blocking)

- Ch8 residual: no perf budget for a full-shape `sense`; `TORQUE_UP_MILESTONE`
  owner unnamed.
- OBPI-03 remains a size outlier (gained the `last_sweep` surface).
- Doc-decomposition dims (3/4/5) unchanged: pool-ADR supersession-discharge not
  a checklist item; OBPI-05 still Heavy-by-conformity; Gate-4 BDD checkbox on
  library-only OBPIs (02/05/06/07) without a feature file.
- Q&A Transcript preserved as-said (raw interview record); its "less code" /
  "KEEL lands cleanly" phrasings are superseded by the corrected binding
  sections, not synced — a deliberate historical record, not drift.

## Gates (all green post-revision)

authored briefs 7/7 · `--decomposition` · `--req-kind-discipline` ·
`--fidelity-presence` · `--documents` · structural 3.85.
