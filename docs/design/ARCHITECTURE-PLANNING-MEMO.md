# GZKit Architecture Planning Memo

**Purpose:** Drive Q&A sessions for foundation-level architectural decisions.
**Status:** Active
**Created:** 2026-03-29
**Last Updated:** 2026-03-29

Each section contains analysis, a recommendation, and a **Decision Record** block.
Decision Records start empty. Fill them during Q&A sessions. Once a decision is
recorded, it becomes binding input for ADR authoring.

---

## How to use this document

1. Read a section's analysis and recommendation.
2. Discuss in Q&A. Challenge, refine, or accept.
3. Record the decision with date, rationale, and any deviations from the recommendation.
4. Move to the next section when ready. Sections are ordered by dependency — earlier decisions inform later ones.

---

## Table of Contents

1. [Entity Hierarchy](#1-entity-hierarchy)
2. [State Doctrine and Source-of-Truth](#2-state-doctrine-and-source-of-truth)
3. [Storage Tiers](#3-storage-tiers)
4. [Graph Engine Scope](#4-graph-engine-scope)
5. [OBPI vs REQ vs TASK Responsibilities](#5-obpi-vs-req-vs-task-responsibilities)
6. [Proof Resolution Model](#6-proof-resolution-model)
7. [Blocker Protocol](#7-blocker-protocol)
8. [Pipeline Lifecycle (Pause/Resume/Handoff)](#8-pipeline-lifecycle-pauseresumehandoff)
9. [Agent Operating Model](#9-agent-operating-model)
10. [Pool ADR Restructuring](#10-pool-adr-restructuring)
11. [Sequencing and Promotion Order](#11-sequencing-and-promotion-order)
12. [Architectural Boundaries (What NOT to Do)](#12-architectural-boundaries-what-not-to-do)

---

## 1. Entity Hierarchy

### Analysis

The repo converges on a four-tier governed execution hierarchy. ADR-0.20.0 and
ADR-0.21.0 introduce REQ. ADR-0.22.0 introduces TASK. ADR-0.18.0 dispatches
subagents against TASKs. The hierarchy as grounded in repo evidence:

```
PRD ─────────────── product intent (Major-bound)
 │
 └─ ADR ──────────── architectural decision scope (SemVer-bound)
     │
     └─ OBPI ─────── governed work brief (1:1 with ADR checklist)
         │
         └─ REQ ──── named acceptance criterion (proof obligation)
              │
              └─ TASK ── execution atom (fulfills the REQ)
                   │
                   └─ Evidence ── proof artifact (booked to TASK, not REQ)
```

Key relationships:
- OBPI is the **scope container** and the unit of human review.
- REQ is the **obligation boundary** — what must be proven.
- TASK is the **execution boundary** — how the obligation is fulfilled.
- Evidence is a **first-class proof entity** — **booked to TASK only**, tightly bound hierarchically upward. Evidence never attaches directly to REQ, OBPI, or ADR.

Two-party proof chain:
- Implementer agent executes TASK, produces Evidence (booked to that TASK).
- Reviewer agent examines Evidence at the TASK level, records verdict.
- REQ satisfaction is **derived upward**: all TASKs under REQ have reviewer-confirmed Evidence.
- OBPI completeness is derived upward: all REQs satisfied.
- Human attests at OBPI/ADR level after observing proof summaries.

Readiness flows upward:
- TASK is ready when its blockers are clear.
- REQ is satisfied when all its TASKs have reviewer-confirmed Evidence.
- OBPI is complete when all its REQs are satisfied.
- ADR is closeable when all its OBPIs are complete.

### Recommendation

Lock this hierarchy as the canonical entity model. Every entity gets:
- A stable ID scheme
- A Pydantic model in `core/models.py`
- Ledger event types for lifecycle transitions
- A place in the graph engine

REQ and TASK currently lack Pydantic models and ledger events. ADR-0.22.0
(TASK) is Proposed. REQ is referenced in ADR-0.20.0/0.21.0 but has no
formal entity definition.

### Open Questions (Resolved)

1. **REQ ID authoring:** Ratified as canonical. REQ IDs are authored in OBPI brief
   acceptance criteria sections (`REQ-X.Y.Z-NN-CC` format). Brief-backed validated
   at test import time via `@covers`. Already implemented in `triangle.py`.

2. **TASK creation:** Locked as plan-derived. TASKs are conceived at execution time
   via `create_task_from_plan_step()`. Structural ID encoding
   (`TASK-X.Y.Z-NN-CC-SS`) embeds parent REQ. Five-state lifecycle
   (pending, in_progress, completed, blocked, escalated). Git trailer linkage.
   Already implemented in `tasks.py`.

3. **Evidence status:** Locked as **full first-class entity, booked to TASK only**.
   Evidence gets an ID scheme, Pydantic model, ledger events, and artifact
   presence. Evidence is tightly bound hierarchically upward through TASK — it
   never attaches directly to REQ, OBPI, or ADR. REQ satisfaction is derived
   by walking: REQ → TASKs → Evidence per TASK → reviewer verdict.
   Architectural rationale: an independent reviewer agent must observe,
   reference, and attest to specific evidence artifacts. This creates a
   two-party proof chain (implementer produces evidence at TASK level,
   reviewer validates evidence at TASK level) that is structurally auditable.
   Current `ObpiReceiptEvidence` payload model in `events.py` is a stepping
   stone, not the end state.

### Decision Record

| Field | Value |
|-------|-------|
| Decision | Four-tier entity hierarchy ratified with Evidence as full first-class entity |
| Date | 2026-03-29 |
| Rationale | REQ and TASK implementations already match the hierarchy. Evidence promotion enables two-party proof chain: implementer produces, independent reviewer validates. This is required by ADR-0.23.0 (burden of proof) and ADR-0.18.0 (reviewer subagent). |
| Deviations from recommendation | Evidence promoted from "attribute of receipt event" to full first-class entity booked to TASK only. Original recommendation treated Evidence as a ledger payload attribute. Human decision: independent agent review requires a referenceable entity. Evidence is hierarchically bound upward through TASK — never booked directly to REQ/OBPI/ADR. |
| ADR to author | Foundation ADR to lock the five-entity model (ADR, OBPI, REQ, TASK, Evidence) with ID schemes, Pydantic models, ledger events, and the two-party proof chain contract. |

---

## 2. State Doctrine and Source-of-Truth

### Analysis

The repo has three storage layers but no document that locks which layer is
authoritative for what:

| Layer | What | Examples |
|-------|------|----------|
| Layer 1: Governance canon | Authored markdown with YAML frontmatter | ADR files, OBPI briefs, PRDs |
| Layer 2: Event log | Append-only JSONL ledger | `.gzkit/ledger.jsonl` |
| Layer 3: Derived state | Computed from L1 + L2 | Pipeline markers, `gz status` output, reconciliation caches |

**The problem:** Multiple commands read "current status" from different layers.
`ledger_semantics.py` derives OBPI status from ledger events. `sync_*.py` reads
frontmatter. Reconciliation commands (`gz obpi reconcile`) exist to fix drift
between them. But there is no locked doctrine that says which layer wins when
they disagree.

Pipeline markers (`pipeline_markers.py`) are a third state source for in-progress
execution. They track "which pipeline stage is this OBPI at?" — ephemeral runtime
state that doesn't belong in the ledger (too transient) or in frontmatter (not
governance authority).

### Recommendation

Author a foundation ADR (proposed ADR-0.0.9) that locks:

1. **Ledger events are authoritative for runtime status.** If frontmatter says
   `status: Completed` but no `obpi_receipt_emitted` event exists, the OBPI is
   not complete.
2. **Frontmatter status is a convenience mirror.** Reconciliation keeps it
   aligned with ledger-derived state. Frontmatter is never read as the
   source-of-truth for "is this done?"
3. **Layer 3 is always rebuildable.** Delete all pipeline markers, caches, and
   derived indexes. Run `gz state` and everything reconstructs from L1 + L2.
4. **Reconciliation is a core operation, not a maintenance chore.** It should
   be tested, gated, and optionally run as part of the pipeline.
5. **Layer 3 artifacts cannot block gates.** Only L1 (canon) and L2 (events)
   can be gate evidence. L3 can surface warnings but never fail-close a gate.

This ADR has **zero dependencies** and should have been written before the
runtime track started. It is the single most important missing foundation.

### Open Questions (Resolved)

1. **Frontmatter auto-fix:** Auto-fix at lifecycle moments. `gz closeout`,
   `gz attest`, and `gz obpi reconcile` auto-update frontmatter to match
   ledger-derived state. No manual step required at lifecycle checkpoints.

2. **`gz state --repair`:** Yes. An explicit force-reconcile command exists for
   cases outside lifecycle moments — recovery, onboarding, diagnosing drift.

3. **Pipeline markers:** Acceptable as Layer 3 for now. Stage transition events
   will move to the ledger when the pipeline lifecycle ADR is authored. Markers
   become a pure rebuildable cache at that point. Known architectural debt with
   a clear migration path.

### Decision Record

| Field | Value |
|-------|-------|
| Decision | Three-layer state doctrine locked with five rules. Ledger always wins. Frontmatter is lazy mirror (auto-fixed at lifecycle moments). L3 always rebuildable. Reconciliation is core. L3 cannot block gates (absolute, with pragmatic marker migration timeline). |
| Date | 2026-03-29 |
| Rationale | Ledger is already authoritative for all other state. Pipeline markers are the one inconsistency — resolved by recording migration intent. Lazy mirror (not strict) avoids churn during active work. Auto-fix at lifecycle moments keeps frontmatter useful for git diffs without manual toil. `gz state --repair` provides escape hatch for recovery. |
| Deviations from recommendation | Lock 2 refined from "convenience mirror" to "lazy mirror" — frontmatter allowed to lag during active execution, auto-fixed at lifecycle moments only. Lock 5 accepted as absolute target with pragmatic timing — marker-to-ledger migration deferred to pipeline lifecycle ADR. |
| ADR to author | Foundation ADR-0.0.9: State Doctrine and Source-of-Truth Hierarchy. Locks three-layer model, five rules, auto-fix behavior, repair command, and marker migration intent. |

---

## 3. Storage Tiers

### Analysis

Pool ADR `storage-simplicity-profile` defines three storage tiers:

- **Tier A:** Canonical docs + append-only ledger. The default. No external deps.
- **Tier B:** Deterministic derived indexes/caches rebuilt from canonical sources. Permitted freely but must be rebuildable.
- **Tier C:** External/stateful runtime backends. Only by explicit ADR authorization.

The pool ADR also defines identity surfaces that all tiers must preserve: `ADR-*`,
`OBPI-*`, `REQ-*`. It explicitly rejects mandatory Dolt/SQL runtime dependency.

This pool ADR is well-written and ready for promotion with minimal revision.

### Recommendation

Promote `storage-simplicity-profile` to a foundation ADR (proposed ADR-0.0.10).
Add the following locks beyond what the pool ADR already contains:

1. **Five identity surfaces preserved across all tiers:** ADR-\*, OBPI-\*, REQ-\*,
   TASK-\*, EV-\* (Evidence format TBD). IDs portable — no tier-specific translation.
2. **Tier escalation requires an ADR.** Moving any data from Tier A/B to Tier C
   is a Heavy-lane decision.
3. **No external protocol dependency for core governance.** CLI + hooks + ledger
   is the universal baseline. MCP, LSP, or any future protocol enhances but never
   becomes a prerequisite.
4. **JSONL for 1.0.0.** No SQLite cache for MVP. SQLite is a known future option
   post-1.0, governed by tier escalation. BEADS' JSONL→SQLite progression is
   acknowledged as a likely path.
5. **Replay and recovery:** All Tier A + B state must survive a `git clone` from
   scratch. Ledger committed to git. Tier B rebuilds on demand.

### Open Questions (Resolved)

1. **Ledger query index:** Principle recorded: introduce Tier B index when
   `gz state` latency is user-perceptible. Post-1.0 concern. Current scale
   (~2K events) is well within linear scan performance.

2. **Tier B manifest:** Deferred until 3+ Tier B items exist. Concept recorded.
   Graph engine (when built) will be Tier B item #2, triggering manifest design.

3. **Undocumented Tier B items:** Pipeline markers (`.gzkit/markers/`) are the
   known undocumented Tier B item. Will be listed in the foundation ADR.
   Migration to Tier A (ledger events) deferred per Section 2 decisions.

### Decision Record

| Field | Value |
|-------|-------|
| Decision | Storage tier model locked with five rules. Three tiers (A: canonical, B: derived/rebuildable, C: external/requires ADR). Five identity surfaces. No external protocol dependency for core governance. JSONL for 1.0.0 with SQLite as post-1.0 option. Full state recoverable from git clone. |
| Date | 2026-03-29 |
| Rationale | Pool ADR `storage-simplicity-profile` already well-defined. Locks ratify and extend it with Evidence identity slot (from Section 1), protocol independence (reframed from MCP-specific), and explicit post-1.0 SQLite path (acknowledging BEADS progression). |
| Deviations from recommendation | Lock 3 reframed: "MCP optional" generalized to "no external protocol dependency for core governance." Lock 4 refined: SQLite acknowledged as known future path (BEADS precedent), not just "not yet." |
| ADR to author | Foundation ADR-0.0.10: Storage Tiers and Simplicity Profile. Promotes pool ADR with five locks, Tier B manifest deferred, pipeline markers documented. |

---

## 4. Graph Engine Scope

### Analysis

Pool ADR `execution-memory-graph` describes a typed entity graph with ready/blocked
queue semantics. This is the architectural center of gravity for the runtime track.

The graph must model:
- **Nodes:** ADR, OBPI, REQ, TASK (the four-tier hierarchy)
- **Edges:** typed relationships with explicit semantics
- **Queues:** `ready` (no open blockers) and `blocked` (with reasons)
- **Proof joins:** REQ → Evidence resolution via TASK execution

The graph must be consumable by `gz state` and `gz status` without weakening
existing governance lifecycle semantics. It must not replace ADR/OBPI artifacts
as governance authority.

Currently, `ledger_semantics.py` does OBPI-level state derivation and
`Ledger.get_artifact_graph()` builds parent-child relationships. But there is
no cross-entity graph resolution — no module computes "this REQ is unsatisfied
because TASK-3 is blocked by TASK-1 in a different OBPI."

### Recommendation

Promote `execution-memory-graph` as a pre-release ADR (Heavy lane). This is the
largest and most architecturally significant ADR in the upcoming track.

Lock the following edge types:

| Edge | From | To | Semantics | Source |
|------|------|----|-----------|--------|
| `contains` | ADR | OBPI | scope containment | Structural (ID encoding) |
| `contains` | OBPI | REQ | obligation containment | Authored in OBPI brief |
| `fulfills` | TASK | REQ | execution satisfies obligation | Structural (TASK ID encodes parent REQ) |
| `produces` | TASK | Evidence | work generates proof artifact | Ledger event (evidence booked to TASK) |
| `reviewed-by` | Evidence | ReviewVerdict | reviewer agent's assessment | Ledger event (review_completed) |
| `blocks` | any | any | dependency (cross-entity, cross-ADR) | Authored or discovered (distinguished by source attribute) |
| `discovered-from` | any | any | emergent work lineage | Ledger event |

**REQ satisfaction is derived, not an edge:** REQ is satisfied when all TASKs
under REQ have status=COMPLETED, each TASK has Evidence (via `produces`), and
that Evidence has a ReviewVerdict=sufficient (via `reviewed-by`). This is a
graph traversal computed by the engine.

The graph engine should be a pure-domain module (no I/O) that takes
Layer 1 + Layer 2 inputs and computes the graph. `gz state` becomes a
projection of the graph. `gz status` becomes a filtered view.

### Open Questions (Resolved)

1. **Graph caching:** Compute on every `gz state` call for 1.0.0. No Tier B
   cache. Add caching as optimization when latency becomes perceptible.

2. **Graph scale:** Tractable at any realistic project size for 1.0.0. A project
   with 200 ADRs / 1000 OBPIs / 4000 REQs / 12K TASKs produces ~17K nodes —
   trivially fast for in-memory computation.

3. **Blocks edge sources:** Both authored (from briefs/ADRs, known at planning
   time) and discovered (from runtime events, emergent). Distinguished by
   `source` attribute on the edge.

4. **Cross-ADR dependencies:** Yes. The graph engine resolves the full project
   graph including cross-ADR blocking edges. `gz state --blocked` shows
   project-wide blockers, not just single-ADR blockers.

### Decision Record

| Field | Value |
|-------|-------|
| Decision | Graph engine scoped, edged, and computed as described. Seven edge types. REQ satisfaction derived via graph traversal. Compute-every-time for 1.0.0. Cross-ADR resolution. Blocks from both authored and discovered sources. |
| Date | 2026-03-29 |
| Rationale | Graph engine is the architectural center. Must resolve the full entity hierarchy (ADR → OBPI → REQ → TASK → Evidence) with two-party proof chain (reviewed-by edge). Cross-ADR resolution required for project-wide blocker visibility. Compute-every-time is sufficient at 1.0.0 scale. |
| Deviations from recommendation | Removed `satisfies` edge (Evidence → REQ). Evidence doesn't satisfy REQ directly — it's booked to TASK. REQ satisfaction is derived upward via graph traversal. Added `reviewed-by` edge for two-party proof chain. Added `source` attribute to `blocks` edges. |
| ADR to author | Pre-release ADR (Heavy): Graph Engine. Promotes `execution-memory-graph` pool ADR with locked edge types, derived satisfaction, compute model, and cross-ADR scope. Subsumes `prime-context-hooks` as OBPI (context projection of the graph). |

---

## 5. OBPI vs REQ vs TASK Responsibilities

### Analysis

OBPI is currently overloaded. It serves as scope container, execution container,
proof aggregation point, and status reporting unit. ADR-0.22.0 introduces TASK
as the execution leaf. ADR-0.20.0/0.21.0 introduce REQ as the traceability target.

With the corrected hierarchy (OBPI → REQ → TASK), the responsibility split is:

| Entity | Responsibility | Human reviews at this level? | Carries proof obligations? |
|--------|---------------|------------------------------|---------------------------|
| OBPI | Scope container. Defines allowed/denied paths. Aggregates REQs. | Yes (closeout review) | No — delegates to REQs |
| REQ | Proof obligation. Named acceptance criterion. Join key to tests via `@covers`. | Indirectly (via OBPI) | Yes — the obligation boundary |
| TASK | Execution atom. Plan-derived. Dispatched to subagents. Traces to git commits. | No (machine-managed) | No — produces evidence for REQs |

**Critical boundary:** TASK never carries proof obligations directly. A completed
TASK that doesn't produce evidence satisfying a REQ is a completed TASK with no
governance value. The proof chain is REQ → Evidence, mediated by TASK execution.

### Recommendation

Lock the responsibility split above. Specifically:

1. **OBPI pipeline dispatches at OBPI level.** The five-stage pipeline is per-OBPI.
2. **Within Stage 2 (implementation), subagent dispatch is per-TASK.** (ADR-0.18.0)
3. **Within Stage 3 (verification), validation is per-REQ.** Check that each REQ has satisfying evidence.
4. **TASK lifecycle is advisory for Lite lane, required for Heavy lane.** (ADR-0.22.0's constraint)
5. **REQ does not have lifecycle states.** It is satisfied or unsatisfied — a boolean determined by evidence existence.

### Open Questions

- Can a single TASK fulfill multiple REQs? (Many-to-many or many-to-one?)
- Can a REQ be fulfilled by evidence from TASKs in different OBPIs? (Cross-OBPI proof)
- Should OBPI-level proof obligations (like "all tests pass") be modeled as a synthetic REQ?
- Where does the OBPI brief template change to accommodate REQ authoring?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |
| ADR to author | — |

---

## 6. Proof Resolution Model

### Analysis

The current proof model:
- OBPI briefs list acceptance criteria (implicit REQs).
- Tests use `@covers("REQ-X.Y.Z-NN-CC")` decorators (ADR-0.21.0).
- `gz adr covers-check` resolves REQ → test mappings deterministically.
- `obpi_receipt_emitted` events carry structured evidence payloads.
- Closeout ceremony presents evidence to human attestor (ADR-0.23.0).
- Audit reconciles post-attestation (never primary proof).

With TASK in the picture, proof resolution gains an execution layer:

```
OBPI brief → REQ (authored obligation)
                → TASK (execution that fulfills REQ)
                    → Evidence (artifact produced by TASK)
                        → @covers("REQ-...") in test (links evidence to obligation)
gz adr covers-check → walks the chain: REQ → Evidence → @covers
Pipeline Stage 3   → validates all REQs have satisfying evidence
Closeout           → human observes proof summary
Audit              → reconciles proof claims against ledger
```

### Recommendation

Lock the proof resolution chain:

1. **REQ is the proof anchor.** Everything resolves to "does this REQ have evidence?"
2. **TASK is the execution mediator.** TASKs produce evidence. Evidence satisfies REQs. TASKs don't satisfy REQs directly — evidence does.
3. **`@covers` is the join mechanism.** Tests annotate which REQ they prove. `covers-check` is the deterministic resolver.
4. **Receipt events are the ledger proof.** `obpi_receipt_emitted` with `req_proof_inputs` records what was proven, when, by what evidence.
5. **Proof gaps block Stage 3.** If a REQ has no `@covers` match, verification fails.
6. **Human attestation is terminal.** No proof chain bypasses Gate 5 for Heavy lane.

### Open Questions

- Is `@covers` the only proof mechanism, or can non-test evidence (docs, receipts) satisfy REQs?
- How are documentation REQs proven? (e.g., "runbook entry exists" — is that a test or a different kind of evidence?)
- Should `gz adr covers-check` report at REQ granularity or OBPI granularity?
- What happens when a TASK produces evidence for a REQ that belongs to a different OBPI?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |
| ADR to author | — |

---

## 7. Blocker Protocol

### Analysis

Pool ADR `structured-blocker-envelopes` formalizes the existing `BLOCKERS:` text
convention into machine-readable envelopes. Currently, blocker output is terse
text — good for humans, opaque to agent retry loops.

Proposed envelope schema: `code`, `message`, `artifact`, `stage`, `retryable`,
`next_actions`.

This is independently valuable and does not require the graph engine. Multiple
existing surfaces produce blockers: `gz obpi validate`, `gz obpi reconcile`,
`gz closeout`, `gz gates`.

### Recommendation

Promote early, independently of the graph engine. This is a concrete
quality-of-life improvement with bounded scope.

Lock:
1. **Blocker envelope is a Pydantic model** in `core/models.py`.
2. **All blocker-producing commands emit envelopes** (text by default, JSON with `--json`).
3. **`retryable` is a boolean.** If true, the agent can retry without human intervention.
4. **`next_actions` is a list of actionable strings** — commands or steps the agent can take.
5. **Envelope does not replace `BLOCKERS:` text.** Text rendering is the human-facing default. Envelope is the machine-facing contract.
6. **Migration is incremental.** Start with 3 surfaces, expand over time.

### Open Questions

- Should blocker envelopes be ledger events? (Argument for: audit trail of what blocked and when. Argument against: transient state, noise in ledger.)
- Should `retryable` have more granularity? (e.g., `retryable_by: agent | human | either`)
- Which 3 surfaces should migrate first?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |
| ADR to author | — |

---

## 8. Pipeline Lifecycle (Pause/Resume/Handoff)

### Analysis

Pool ADR `pause-resume-handoff-runtime` addresses a concrete defect: handoff exists
conceptually but not as a reliable runtime command path. The current
`gz-session-handoff` skill has documented drift from actual runtime behavior.

The pool ADR proposes:
- `gz handoff create` / `resume` / `status`
- Repository-local handoff schema (scope, branch, stage, next steps, staleness)
- Deterministic staleness checks (commits since handoff, changed files, branch mismatch)
- Pipeline consumption of handoff state

Pool ADR `channel-agnostic-human-triggers` is architecturally subordinate to this —
it defines how human approvals are delivered to a paused pipeline. It should
become an OBPI under this ADR rather than an independent architecture.

### Recommendation

Promote after the graph engine is locked. The handoff schema needs to reference
graph entities (which OBPI, which REQ, which TASK was in progress). Without the
graph engine, handoff state is untyped.

Subsume `channel-agnostic-human-triggers` as a future OBPI within this ADR.

Lock:
1. **Handoff is a ledger event** (`pipeline_paused`, `pipeline_resumed`).
2. **Handoff schema references graph entities** by typed ID.
3. **Staleness is deterministic** — computed from git state, not heuristic.
4. **Resume is fail-safe** — if staleness exceeds threshold, resume requires explicit human approval.
5. **Channel-agnostic triggers** are a transport concern layered on top of the pause/resume contract.

### Open Questions

- What is the staleness threshold? Commits? Time? File delta?
- Should handoff create a git tag or branch marker?
- Can an OBPI have multiple active handoffs (e.g., paused at different stages)?
- How does handoff interact with OBPI locks (`gz-obpi-lock`)?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |
| ADR to author | — |

---

## 9. Agent Operating Model

### Analysis

Three pool ADRs address agent coordination:

- `agent-role-specialization` — superseded into ADR-0.18.0 (subagent pipeline). Defines Planner, Implementer, Reviewer, Narrator roles.
- `graduated-oversight-model` — three-tier oversight (Full / Standard / Light) replacing binary Normal/Exception.
- `universal-agent-onboarding` — vendor-neutral `gz onboard` for cold-start context injection.

ADR-0.18.0 (subagent-driven-pipeline-execution) is the most architecturally
mature of these. It defines a controller/worker model where the main session
orchestrates governance stages and dispatches fresh subagents for TASK-level
implementation and REQ-level verification.

### Recommendation

**Roles:** Already subsumed into ADR-0.18.0. No separate ADR needed.

**Graduated oversight:** Defer until the graph spine is operational. Risk scoring
needs graph data (file count per TASK, subsystem crossings per REQ, coverage
delta per OBPI). Without graph-backed scoring, oversight tier selection is
guesswork.

**Onboarding:** Merge into `prime-context-hooks` (or its successor). Onboarding
is a special case of context projection — `gz prime --cold-start` or equivalent.
Not a separate architectural decision.

Lock (when the time comes):
1. **Oversight tier is a human decision**, never auto-assigned.
2. **Risk scoring is deterministic** — no LLM-based assessment.
3. **Standard tier still requires all OBPIs to pass self-close evidence requirements.** The spot-check is an additional human layer, not a replacement for automated proof.

### Open Questions

- Is the Normal/Exception binary acceptable for now, or is graduated oversight blocking real work?
- Should `gz prime` exist independently of the graph engine, as a simpler "dump current work state" command?
- Does ADR-0.18.0 need to be implemented before graduated oversight makes sense?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |
| ADR to author | — |

---

## 10. Pool ADR Restructuring

### Analysis

The pool has 27 items. Many are architecturally subordinate to a smaller number of
parent concerns. The current flat list with linear dependency chains obscures the
real structure.

### Recommended Groupings

**Group A: Foundations (promote to 0.0.x)**

| Pool ADR | Action | Rationale |
|----------|--------|-----------|
| `storage-simplicity-profile` | Promote to ADR-0.0.10 | Gates entire runtime track |
| (new) State Doctrine | Author as ADR-0.0.9 | Missing foundation, zero deps |

**Group B: Graph & Runtime (promote as pre-release)**

| Pool ADR | Action | Rationale |
|----------|--------|-----------|
| `execution-memory-graph` | Promote (Heavy) | Architectural center of gravity |
| `prime-context-hooks` | Merge as OBPI under graph ADR | Context projection of the graph |
| `universal-agent-onboarding` | Merge as OBPI under graph ADR | Cold-start projection |
| `structured-blocker-envelopes` | Promote independently (Heavy) | No graph dependency, early value |
| `pause-resume-handoff-runtime` | Promote after graph (Heavy) | Depends on graph entity types |
| `channel-agnostic-human-triggers` | Subordinate as future OBPI under pause/resume | Transport concern, not architecture |

**Group C: Proof Chain (partially promoted)**

| Pool ADR | Action | Rationale |
|----------|--------|-----------|
| `spec-triangle-sync` | Already ADR-0.20.0 | Done |
| `tests-for-spec` | Already ADR-0.21.0 | Done |
| `constraint-library` | Defer | Premature; proof architecture must stabilize first |
| `constraint-cli-surfaces` | Defer | Blocked by constraint-library |

**Group D: Agent Model (partially promoted)**

| Pool ADR | Action | Rationale |
|----------|--------|-----------|
| `agent-role-specialization` | Already superseded into ADR-0.18.0 | Done |
| `graduated-oversight-model` | Defer until graph is operational | Needs graph for risk scoring |

**Group E: Parity & Maintenance**

| Pool ADR | Action | Rationale |
|----------|--------|-----------|
| `airlineops-surface-breadth-parity` | Already ADR-0.9.0 | Done |
| `airlineops-direct-governance-migration` | Defer indefinitely | Not an architecture decision |
| `session-productivity-metrics` | Defer | Not architecturally load-bearing |
| `agentic-security-review` | Defer | Gate plugin, add after proof arch is stable |
| `go-runtime-parity` | Defer | Multi-language is premature |

**Group F: Release Track**

| Pool ADR | Action | Rationale |
|----------|--------|-----------|
| `heavy-lane` | Promote when needed | Gate expansion, not architecture |
| `audit-system` | Promote after graph | Needs proof resolution chain |
| `release-hardening` | Last before 1.0 | Everything else must be done or deferred |
| `ai-runtime-foundations` | Post-1.0 | Keep in pool |
| `evaluation-infrastructure` | Stale — ADR-0.0.5 covers this | Archive or update |
| `controlled-agency-recovery` | Post-1.0 | Keep in pool |

### Open Questions

- Should the pool README be restructured to reflect these groupings?
- Should merged/subordinated pool entries be archived or deleted?
- Are there pool entries I've recommended deferring that are actually blocking current work?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |

---

## 11. Sequencing and Promotion Order

### Recommended Sequence

```
Phase N (immediate):
  [1] ADR-0.0.9  State Doctrine               zero deps
  [2] ADR-0.0.10 Storage Tiers                zero deps
      (can be authored in parallel)

Phase N+1 (after foundations locked):
  [3] Graph Engine (pre-release, Heavy)        deps: [1], [2]
  [4] Blocker Protocol (pre-release, Heavy)    zero deps, parallel with [3]

Phase N+2 (after graph engine):
  [5] Pipeline Lifecycle (pre-release, Heavy)  deps: [3]
  [6] Graduated Oversight (pre-release, Lite)  deps: [3]

Phase N+3 (pre-1.0):
  [7] Audit System (pre-release, Heavy)        deps: [3] (proof resolution)
  [8] Release Hardening                        deps: all above
```

### Rationale

- State Doctrine and Storage Tiers are foundations with zero dependencies. They
  unlock everything else. Author them first.
- Graph Engine is the architectural center. It must be locked before pipeline
  lifecycle, graduated oversight, or audit can be designed properly.
- Blocker Protocol is independently valuable and can run in parallel with the
  graph engine.
- Pipeline Lifecycle needs graph entity types for typed handoff state.
- Graduated Oversight needs graph data for risk scoring.
- Audit needs proof resolution (REQ → Evidence chain) which is a graph operation.
- Release Hardening is the 1.0 boundary. Everything must be done or deferred.

### Open Questions

- Is this sequence too sequential? Can more work run in parallel?
- Are there existing ADRs (0.22.0 TASK, 0.18.0 subagent) that should be completed before or alongside this sequence?
- Should the foundation ADRs be authored as a pair (one Q&A session) or separately?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |

---

## 12. Architectural Boundaries (What NOT to Do)

### Analysis

Based on repo evidence, these are the highest-risk missteps:

**12.1 Do not promote post-1.0 pool ADRs into active work.**

`ai-runtime-foundations`, `controlled-agency-recovery`, and `evaluation-infrastructure`
(the pool version — ADR-0.0.5 already covers the foundation) are post-1.0
concerns. The graph spine, proof architecture, and pipeline lifecycle are not
stable enough to support AI runtime controls on top. Promoting these now creates
dependency chains that delay the foundations.

**12.2 Do not add more pool ADRs to the runtime track.**

The pool has sufficient architectural intent for 2-3 years of work. The problem
is insufficient foundation locking, not insufficient vision. More pool ADRs
create more dependency chains without reducing ambiguity.

**12.3 Do not build the graph engine without locking state doctrine first.**

A graph engine built on implicit state assumptions becomes the single biggest
source of reconciliation bugs. Section 2 must be decided before Section 4 is
authored.

**12.4 Do not let reconciliation remain a maintenance chore.**

If the state doctrine says "derived state is rebuildable," then reconciliation
is a core architectural operation. It should be tested, gated, and optionally
run as part of the pipeline — not invoked ad-hoc when drift is noticed.

**12.5 Do not let AirlineOps parity become perpetual catch-up.**

Current parity (ADRs 0.3.0, 0.9.0, 0.11.0, 0.12.0) is sufficient baseline.
Future parity should flow from gzkit innovations adopted by AirlineOps, not
gzkit chasing AirlineOps patches. Declare parity-tracking paused for the
foundation-locking phase.

**12.6 Do not let derived views silently become source-of-truth.**

`gz status` output, pipeline markers, and reconciliation caches are Layer 3.
If any of these become the only place a fact is recorded, the state doctrine is
violated. Every fact must trace to Layer 1 (canon) or Layer 2 (ledger).

### Open Questions

- Are any of these boundaries already being violated in current practice?
- Is there a pool ADR I've recommended deferring that is actually urgent?
- Should these boundaries be recorded in a foundation ADR or in AGENTS.md?

### Decision Record

| Field | Value |
|-------|-------|
| Decision | — |
| Date | — |
| Rationale | — |
| Deviations from recommendation | — |

---

## Appendix A: Structural Assessment Summary

### Strengths

- **Ledger-first state model.** Append-only JSONL with derived state is the right foundation.
- **OBPI pipeline as operational spine.** Five-stage pipeline is well-defined and AirlineOps-proven.
- **Hexagonal architecture.** ADR-0.0.3 gives clean adapter/domain/port separation.
- **Foundation ADR discipline.** 0.0.x vs 0.y.0 separation is architecturally correct.
- **Human attestation as non-bypassable.** INV-001/INV-002 are the right invariants.
- **Closeout as defense.** ADR-0.23.0 ("agent bears burden of proof") is strong design.

### Under-Designed Areas

- **State doctrine is unwritten.** The most important decision exists only as convention.
- **REQ entity is under-specified.** No Pydantic model, no ID scheme in `core/models.py`, no ledger events.
- **Graph engine is the missing center.** Four-tier hierarchy is documented but no module computes cross-entity resolution.
- **Layer 3 has no doctrine.** Pipeline markers and caches have no rules about what they can/cannot do.

### Single Most Important Move

Write the State Doctrine foundation ADR. One document that prevents divergence
across the entire runtime track.

---

## Appendix B: Cross-Reference to Repo Artifacts

| Section | Key Repo Artifacts |
|---------|-------------------|
| Entity Hierarchy | ADR-0.20.0, ADR-0.21.0, ADR-0.22.0, ADR-0.18.0 |
| State Doctrine | `src/gzkit/ledger_semantics.py`, `src/gzkit/sync.py`, `src/gzkit/pipeline_markers.py` |
| Storage Tiers | `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md` |
| Graph Engine | `docs/design/adr/pool/ADR-pool.execution-memory-graph.md`, `src/gzkit/ledger.py` |
| OBPI/REQ/TASK | `src/gzkit/core/models.py`, `src/gzkit/tasks.py`, `src/gzkit/events.py` |
| Proof Resolution | ADR-0.21.0, `src/gzkit/traceability.py`, `src/gzkit/ledger_proof.py` |
| Blocker Protocol | `docs/design/adr/pool/ADR-pool.structured-blocker-envelopes.md` |
| Pipeline Lifecycle | `docs/design/adr/pool/ADR-pool.pause-resume-handoff-runtime.md`, `src/gzkit/pipeline_runtime.py` |
| Agent Model | ADR-0.18.0, `docs/design/adr/pool/ADR-pool.graduated-oversight-model.md` |
| Pool Restructuring | `docs/design/adr/pool/README.md` |
