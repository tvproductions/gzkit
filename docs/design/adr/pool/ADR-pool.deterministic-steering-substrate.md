---
id: ADR-pool.deterministic-steering-substrate
status: Pool
lane: heavy
parent: PRD-GZKIT-1.0.0
---

# ADR-pool.deterministic-steering-substrate: Deterministic Steering Substrate

## Persona

Active persona: `main-session` (`.gzkit/personas/main-session.md`). Craftsperson, governance-aware, whole-file-reasoning, direct. Treats the steering substrate not as a convenience layer but as the orientation surface that makes deterministic query of governance state beat stochastic recall of it. Implementations of this ADR's OBPIs MUST keep every surface here Evidentiary/Projection (ADR-0.0.38) — never gate-binding; MUST keep routing/ranking a deterministic decision table (ADR-0.0.39/0.0.40) with NO LLM inference in the path; MUST land the `tdd-receipt-stream` event-kind schema (OBPI-01) before any consumer because it is the one-way-ish element; and MUST layer the queryability surfaces (gz search, gz insights query) so they survive failure of the `gz next` engine. This ADR DECLARES the supersession relationships listed in the Decision; it does NOT itself demote ADR-0.0.46/0.0.47/0.0.48 or the six coalesced pool ADRs — those verified demotions are a follow-up the main session discharges.

## Why foundation tier?

**Invariance test:** Without this ADR, the project would not be the project because gzkit's read side — how an agent reads governance state and decides the next best move — would remain scattered across roughly nine dormant pool/booked-foundation ADRs with no coherent substrate. The graph spine would keep accreting state (ledger, receipts, insights, ADR/OBPI lifecycle) with no deterministic orientation surface over it, and agents would fall back on stochastic recall of *where things are* instead of deterministic query of *where things are*. That is identity-shaping for gzkit's anti-vibing mantra (operative claim 4: stochastic LLM vibing is the named failure class): the substrate is the orientation half of making vibing structurally inert, the sibling of the Harness Hardening enforcement half. A read-substrate is the kind of identity-shaping fact ADR-0.0.18 § decision item 1 names as foundation, not a release-carrying capability.

**Port-vs-adapter framing:** This ADR is a **port** — it specifies *what* the deterministic steering read-surface MUST be: a single append-only governance-event stream (the hub) read by both an orientation consumer (this ADR) and an enforcement consumer (the Harness Hardening spine); a deterministic, non-LLM next-best-action decision table; queryability surfaces that survive engine failure; all Evidentiary/Projection, all Layer-3-never-source-of-truth with freshness drift validators. The concrete CLI verbs (`gz next`, `gz metrics`, `gz search`, `gz insights query`), the FTS5 index, the decision-table implementation, and the solved-problem corpus are all **adapters** behind this port. The hexagonal lens also draws the boundary with the parked `execution-memory-graph`: `gz next` READS state (adapter behind this port), the work-node graph COMPUTES readiness (a separate port) — read vs compute is the seam, and it is why the graph stays a separate ADR.

## Intent

gzkit's capability to answer 'how does an agent read governance state and decide the next best move' is scattered across roughly nine dormant pool/booked-foundation ADRs. As the repository grows, agents under-consult history, prior-art, and current-state because there is no single coherent read-substrate to consult. This ADR establishes the Deterministic Steering Substrate: the deterministic ledger/receipt/insights queryability plus next-best-action read layer. It is the ORIENTATION-layer sibling of the return-to-health plan's Harness Hardening anti-vibe-mechanization spine (docs/governance/return-to-health-plan-2026-05-30.md), sharing the tdd-receipt-stream hub: the spine reads the stream for ENFORCEMENT, this substrate reads it for ORIENTATION. Same hub, two consumers. Promotion of a new heavy foundation ADR during the return-to-health recovery freeze is an explicit operator decision against Architectural Boundary 1 / Operating Rule 6, made on the routing facts and reserved for the operator by the plan itself ('an explicit operator decision against the Architectural Boundary 1 freeze (Operating Rule 6) - not a default'); it is not a default. Foundation tier per the invariance test: without a coherent deterministic read-substrate, the governance graph keeps accreting state with no orientation surface, and agents fall back on stochastic recall of where things are rather than deterministic query of where things are. That is identity-shaping for gzkit's anti-vibing mantra (operative claim 4: stochastic LLM vibing is the named failure class).

## Decision

Establish ONE foundation ADR: the Deterministic Steering Substrate. It coalesces six live pool ADRs and subsumes three booked-but-unbuilt foundation ADRs into a single substrate plus a clear leaf-first OBPI sequence that mirrors the return-to-health Harness Hardening promotion order (leaf first, 1:1 checklist to OBPI). COALESCES (declares supersession of these six live pool ADRs): tdd-receipt-stream (THE HUB - generalized append-only governance-event receipt stream; folds in the rival ADR-pool.tdd-emission-and-graph-rot-remediation); agent-execution-intelligence ONLY CAP-22 (gz next deterministic decision-table next-best-action over the ledger) plus the CAP-08 MODE surface (CAP-08 tiers / CAP-09 / CAP-10 / CAP-21 stay PARKED post-1.0); session-productivity-metrics (gz metrics read-view over the stream); cross-session-search (gz search, stdlib SQLite FTS5); insights-browsable-by-topic (gz insights query); solved-problem-pattern-corpus (prior-art memory read-surface). SUBSUMES (declares supersession of these three booked-but-UNBUILT foundation ADRs - zero OBPIs implemented): ADR-0.0.46 pool-management (gz pool triage/rank/override/show); ADR-0.0.47 pool-dag-promotion-routing (gz pool graph; gz next --pool); ADR-0.0.48 gz-adr-pool-triage (/pool-triage skill). UNIFY: gz next = whole-project next-best-action; gz next --pool = pool-scoped subset; /pool-triage becomes a pool-scoped mode of the renamed steering skill. HEADLINE CAPABILITY: gz next (whole-project best-next-closable-task) is wielded by a SEPARATE GHI-routed skill gz-next (renamed from the proposed gz-triage because it is whole-project, not GHI-flavored; ghi-triage stays the GHI-queue ranker). This ADR authors substrate/software ONLY; the gz-next skill is a downstream GHI, not authored here. BINDING DOCTRINES (cite, obey, do not duplicate): ADR-0.0.38 evidence-authority-projection - every surface here is Evidentiary/Projection and NEVER binds a gate; ADR-0.0.39/0.0.40 llm-as-judge - NO LLM inference in the deterministic routing/ranking (gz next is a deterministic decision table). All read-views are pointer-only, Layer-3-never-source-of-truth, with *-fresh drift validators. Decision items (1:1 with the six-item OBPI decomposition, leaf-first): (1) tdd-receipt-stream hub (event-kind registry plus append-only emission; the one-way-ish receipt event-kind schema lands FIRST and is got right before any consumer); (2) gz next (CAP-22) plus CAP-08 MODE (deterministic decision table over ledger/OBPI/ADR state; surfaces, never auto-executes, human gates); (3) gz metrics read-view over the stream; (4) queryability verbs gz search (FTS5) and gz insights query; (5) solved-problem-pattern-corpus read-surface (governed; append-only; citation-bound); (6) subsume ADR-0.0.46/47/48 into gz next / gz next --pool and re-home /pool-triage as a pool-scoped mode of gz-next. Lane: heavy (adds new CLI verbs gz next, gz metrics, gz search, gz insights query, and new ledger event types via the receipt stream). Foundation-kind brief-level Gate 5 attestation per ADR-0.0.36 (universal). Reversibility is mostly two-way (read-layer over append-only data; verbs removable with data intact; the 46/47/48 subsumption reversible while unbuilt); the one-way-ish element is the receipt event-kind schema (OBPI 1).

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: gz next and gz search are unbuilt (Draft); the Layer-3 read-view freshness drift validation the substrate's read-views mandate runs green. | uv run gz validate --reconcile-freshness | 0 |

## Consequences

### Positive

1. Consolidates roughly nine scattered dormant artifacts (six pool ADRs plus three booked-but-unbuilt foundation ADRs) into ONE substrate with a clear leaf-first OBPI sequence — the dormant sprawl the operator directed me to coalesce becomes a single coherent read-layer.
2. Gives agents a deterministic 'next best move' (`gz next`) over current governance state — a decision table, not LLM inference — directly attacking the under-consultation-of-state failure that grows with the repo.
3. Builds the long-overdue ledger/insights/ARB queryability (`gz search` over FTS5, `gz insights query`) so prior decisions and corrections are deterministically recallable rather than re-derived from stochastic memory.
4. Shares the `tdd-receipt-stream` receipt hub with the Harness Hardening enforcement spine: one event source, two consumers (enforcement reads it, orientation reads it), so the stream is not doubled.
5. The queryability layer is architected to survive engine failure: `gz search`, `gz insights query`, and raw ledger reads do NOT depend on the `gz next` engine — when the next-best-action engine is down, raw recall still works.
6. Unifies pool-scoped triage under the same engine: `gz next` is whole-project, `gz next --pool` is the pool-scoped subset, `/pool-triage` becomes a pool-scoped mode of `gz-next` — one engine, not three parallel CLI surfaces.
7. Obeys the evidence/authority and llm-as-judge doctrines by construction: every surface is Evidentiary/Projection (ADR-0.0.38) and routing is a deterministic decision table (ADR-0.0.39/0.0.40) — no LLM in the gate or ranking path.
8. Forces clean downstream follow-ups rather than swallowing them: a separate `execution-memory-graph` ADR (read vs compute), `agent-reliability-framework` stays separate, the `gz-next` skill ships as its own GHI, and the return-to-health plan gains a reference to this ADR in the Harness Hardening workstream.

### Negative

1. A new heavy foundation ADR is promoted DURING the return-to-health recovery freeze — the Architectural Boundary 1 / Operating Rule 6 cost, consciously waived by the operator on the routing facts, but real and named.
2. Implementation bandwidth competes with the emergency GHI #519 remediation; the pre-mortem's most plausible failure is exactly this — promoted during recovery then starved of bandwidth while #519 consumes everything, leaving it another dormant unbuilt foundation ADR.
3. The `gz next` decision table may not match real 'best next' judgment; if weak, agents ignore it. Mitigation per ADR-0.0.39: do NOT add LLM to the gate path — degrade to advisory, never to vibe.
4. `gz next` vs `gz next --pool` semantics could collide if not designed cleanly; named in the pre-mortem; the UNIFY framing (whole-project vs pool-scoped subset of the same engine) is the mitigation, but the risk is real until OBPIs 02 and 06 land.
5. The `tdd-receipt-stream` hub could become a parallel stream alongside the ledger instead of THE source, doubling state; the hub-first ordering (OBPI-01) and the Layer-3-never-source-of-truth constraint are the mitigations; the receipt event-kind schema is the one-way-ish element that must be got right first.
6. The solved-problem-pattern-corpus read-surface carries the standing governed-corpus risk (free-form learnings reproduce training-corpus bias if ungoverned); the four governance invariants (append-only, Layer-2, citation-bound, skill-written) are inherited from the pool ADR and must hold or the surface should be rejected.
7. Subsuming three booked foundation ADRs (0.0.46/0.0.47/0.0.48) into this one creates a verified-demotion obligation the main session must discharge; until then the supersession is declared-but-not-executed, which is itself a tracked follow-up, not a silent state.

## Boundary Invariants

Cross-OBPI structural invariants spanning the six-OBPI decomposition. Each
invariant is audited at ADR closeout, not per-OBPI; STRUCTURAL-FENCE REQs
in the child briefs cite this section as their proof channel
(ADR-0.0.59 § REQ-kind discipline).

1. **Every surface in this ADR is Evidentiary/Projection and NEVER binds a gate.**
   `gz next`, `gz metrics`, `gz search`, `gz insights query`, and the
   solved-problem corpus are read/projection surfaces per ADR-0.0.38. No OBPI
   in this ADR may wire any of these surfaces into a gate decision, a closeout
   fail-close, or an attestation requirement. The substrate orients; it does
   not enforce. Enforcement over the same hub is the Harness Hardening spine's
   job, not this ADR's.
   (OBPI-02, OBPI-03, OBPI-05)

2. **No LLM inference in the deterministic routing/ranking path.** `gz next`'s
   next-best-action selection and any ranking it performs MUST be a
   deterministic decision table over observable state (ledger events, OBPI/ADR
   lifecycle, working-tree status) per ADR-0.0.39/0.0.40. No OBPI may introduce
   an LLM call into the routing or ranking path. If the deterministic table
   proves insufficient, the only sanctioned degrade is to advisory output —
   never to LLM-inferred routing.
   (OBPI-02)

3. **The ledger remains system-of-record; every read-view is Layer-3 derived
   and never source-of-truth.** The `tdd-receipt-stream` hub is append-only and
   the ledger stays the system-of-record (state-doctrine; Architectural
   Boundary 6). `gz metrics`, `gz search`, and `gz insights query` are Layer-3
   derived views, each fully rebuildable from Layer-1/Layer-2 sources and each
   guarded by a freshness drift validator. No OBPI may let a derived view
   become a write target or a source-of-truth.
   (OBPI-01, OBPI-03, OBPI-04, OBPI-05)

4. **The queryability surfaces do not depend on the `gz next` engine.**
   `gz search`, `gz insights query`, and raw ledger reads MUST function when
   the next-best-action engine is unavailable (the 2am-operator invariant). No
   OBPI may introduce a code path that makes the queryability layer call into,
   import-cycle with, or hard-depend on the `gz next` decision engine.
   (OBPI-04)

5. **This ADR DECLARES supersession; it does not demote.** The supersession of
   ADR-0.0.46/0.0.47/0.0.48 and the six coalesced pool ADRs
   (`tdd-receipt-stream`, `tdd-emission-and-graph-rot-remediation`,
   `agent-execution-intelligence` CAP-22 + CAP-08 MODE,
   `session-productivity-metrics`, `cross-session-search`,
   `insights-browsable-by-topic`, `solved-problem-pattern-corpus`) is declared
   in this ADR's body. No OBPI in this ADR may edit those superseded ADRs'
   frontmatter or status; the verified demotions are a separate follow-up the
   main session discharges under its own routing.
   (OBPI-06)

## Architectural Alignment

**Source-file integration points (where the substrate seats).** The substrate
is read-layer software over the existing governance spine; it integrates at
these surfaces rather than inventing new state:

- `src/gzkit/events.py` and `src/gzkit/schemas/` — the receipt event-kind models
  and per-kind `*_receipt.schema.json` for the OBPI-01 hub (the same modules
  ADR-0.0.64 extended for the TASK `task_id` field; this ADR adds receipt-stream
  kinds, not worklog fields).
- `.gzkit/ledger.jsonl` — the Layer-2 system-of-record the stream appends to and
  the read-views (`gz next`, `gz metrics`, `gz search`) read from; never a write
  target for derived views (state-doctrine; Architectural Boundary 6).
- `src/gzkit/cli/` and `src/gzkit/commands/` — the new verbs (`gz next`,
  `gz metrics`, `gz search`, `gz insights query`, the pattern-corpus read verb,
  `gz pool graph`) register here, following the existing `gz <verb>` parser-tree
  convention audited by `gz cli audit`.
- `.gzkit/insights/agent-insights.jsonl` — the T2 insights store `gz insights
  query` reads (read-only) and `gz search` indexes; unchanged as source-of-truth.
- `src/gzkit/trust_audits.py` (validator-scope home) — the `*-fresh` drift
  validators for each Layer-3 read-view, following the `--adr-status-fresh` /
  `--commit-trailers` / `--cli-alignment` precedent already wired into
  `gz check`.

**Exemplar / precedent the substrate reuses (not novel machinery).**

- **Receipt stream:** the ARB receipt corpus (`src/gzkit/arb/`) is the
  reference pattern for the wrapper/emit shape; the hub generalizes it to
  governance-event kinds whose semantics are not exit-coded (the
  `tdd-receipt-stream` pool ADR's own framing). Verified-emission semantics
  (RED must fail, GREEN must pass) fold in from `tdd-emission-and-graph-rot-remediation`.
- **Decision table over ledger state:** `gz next`'s deterministic routing mirrors
  the existing reconciliation/state-read pattern (`gz state`, `gz status`) — it
  reads the same ledger projections those verbs read, then maps state to a
  recommended verb via a static table (GSD `/gsd-next` is the external
  inspiration; gzkit's adaptation is deterministic, not LLM-inferred, per
  ADR-0.0.39/0.0.40).
- **FTS5 index:** stdlib `sqlite3` FTS5 is the named substrate in the
  `cross-session-search` pool ADR — no third-party search dependency, per the
  Stdlib-First doctrine.
- **Read-vs-compute boundary:** the substrate deliberately stops at READ; the
  parked `execution-memory-graph` ADR owns COMPUTE (work-node readiness). This
  is the same port boundary the hexagonal lens draws in § Why foundation tier?.

This ADR introduces no abstraction that does not already have a precedent in
the codebase or a parked-but-articulated pool ADR; the work is read-layer
composition over the existing spine, which is why reversibility is mostly
two-way (§ Reversibility).

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 6

<!-- Surface-boundary split applied (+1): the substrate spans distinct surfaces
     that warrant separate briefs — the append-only receipt-stream hub (a write
     surface), the deterministic decision engine (gz next), read-views (gz
     metrics), queryability (gz search / gz insights query), the governed
     solved-problem corpus, and the pool-unification re-home. Six briefs, 1:1
     with the checklist. -->


## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] tdd-receipt-stream-hub: Establish the tdd-receipt-stream as THE shared append-only governance-event receipt stream - event-kind registry plus append-only emission path. Fold in the rival ADR-pool.tdd-emission-and-graph-rot-remediation (verified RED/GREEN emission semantics). This is the hub the Harness Hardening enforcement spine ALSO consumes; the receipt event-kind schema is the one-way-ish element, so it lands FIRST and is got right before any consumer. Layer-3-never-source-of-truth; the ledger remains system-of-record. (heavy lane: new ledger event types).
- [ ] gz-next-cap22-and-cap08-mode: Implement gz next (CAP-22) - whole-project deterministic decision-table next-best-action over ledger/OBPI/ADR state - plus the CAP-08 MODE per-invocation intent surface (READ-ONLY / PLAN-FIRST / IMPLEMENT). Decision table is deterministic per ADR-0.0.39/0.0.40 (NO LLM inference). Output modes gz next / --dry-run / --explain; never auto-executes Gate 5 or destructive ops - surfaces human gates and waits. CAP-08 tiers, CAP-09, CAP-10, CAP-21 stay PARKED. (heavy lane: new CLI verb).
- [ ] gz-metrics-read-view: Implement gz metrics - a read-view over the receipt stream computing throughput, duration, defect rate, rework cycles, WIP, and trend. Read-view only (collapses the proposed parallel session-metrics.jsonl into a read over the unified stream); Layer-3 derived; freshness drift validator. (heavy lane: new CLI verb).
- [ ] queryability-search-and-insights-query: Implement gz search (stdlib SQLite FTS5 index over ledger events, handoffs, and insights; gz search rebuild for full rebuild) and gz insights query (browsable-by-topic read over agent-insights.jsonl). Both MUST be independent of the gz next engine so reads survive engine failure (the 2am-operator invariant). Layer-3 derived; freshness validators. (heavy lane: new CLI verbs).
- [ ] solved-problem-pattern-corpus-read-surface: Implement the solved-problem pattern corpus as a governed prior-art memory read-surface, bound by the four invariants (append-only, Layer-2, each entry cites primary evidence, skill-written never hand-edited). Provides the aggregated recurring-failure-pattern artifact that per-occurrence search does not. (heavy lane: new read surface over governed corpus).
- [ ] subsume-pool-management-into-gz-next: Subsume ADR-0.0.46 pool-management, ADR-0.0.47 pool-dag-promotion-routing, and ADR-0.0.48 gz-adr-pool-triage into the unified engine: gz next --pool is the pool-scoped subset of gz next, gz pool graph is the pool DAG read, and /pool-triage becomes a pool-scoped MODE of the renamed gz-next steering skill. This ADR DECLARES the supersession; the verified demotions of 0.0.46/47/48 are a follow-up the main session discharges. (heavy lane: CLI surface unification; declared supersession).

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-05-31T08:54:40.030878*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.66-deterministic-steering-substrate

### Q: What is the title of this ADR?

**A:** Deterministic Steering Substrate

### Q: What is the semantic version?

**A:** 0.0.66

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's capability to answer 'how does an agent read governance state and decide the next best move' is scattered across roughly nine dormant pool/booked-foundation ADRs. As the repository grows, agents under-consult history, prior-art, and current-state because there is no single coherent read-substrate to consult. This ADR establishes the Deterministic Steering Substrate: the deterministic ledger/receipt/insights queryability plus next-best-action read layer. It is the ORIENTATION-layer sibling of the return-to-health plan's Harness Hardening anti-vibe-mechanization spine (docs/governance/return-to-health-plan-2026-05-30.md), sharing the tdd-receipt-stream hub: the spine reads the stream for ENFORCEMENT, this substrate reads it for ORIENTATION. Same hub, two consumers. Promotion of a new heavy foundation ADR during the return-to-health recovery freeze is an explicit operator decision against Architectural Boundary 1 / Operating Rule 6, made on the routing facts and reserved for the operator by the plan itself ('an explicit operator decision against the Architectural Boundary 1 freeze (Operating Rule 6) - not a default'); it is not a default. Foundation tier per the invariance test: without a coherent deterministic read-substrate, the governance graph keeps accreting state with no orientation surface, and agents fall back on stochastic recall of where things are rather than deterministic query of where things are. That is identity-shaping for gzkit's anti-vibing mantra (operative claim 4: stochastic LLM vibing is the named failure class).

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Establish ONE foundation ADR: the Deterministic Steering Substrate. It coalesces six live pool ADRs and subsumes three booked-but-unbuilt foundation ADRs into a single substrate plus a clear leaf-first OBPI sequence that mirrors the return-to-health Harness Hardening promotion order (leaf first, 1:1 checklist to OBPI). COALESCES (declares supersession of these six live pool ADRs): tdd-receipt-stream (THE HUB - generalized append-only governance-event receipt stream; folds in the rival ADR-pool.tdd-emission-and-graph-rot-remediation); agent-execution-intelligence ONLY CAP-22 (gz next deterministic decision-table next-best-action over the ledger) plus the CAP-08 MODE surface (CAP-08 tiers / CAP-09 / CAP-10 / CAP-21 stay PARKED post-1.0); session-productivity-metrics (gz metrics read-view over the stream); cross-session-search (gz search, stdlib SQLite FTS5); insights-browsable-by-topic (gz insights query); solved-problem-pattern-corpus (prior-art memory read-surface). SUBSUMES (declares supersession of these three booked-but-UNBUILT foundation ADRs - zero OBPIs implemented): ADR-0.0.46 pool-management (gz pool triage/rank/override/show); ADR-0.0.47 pool-dag-promotion-routing (gz pool graph; gz next --pool); ADR-0.0.48 gz-adr-pool-triage (/pool-triage skill). UNIFY: gz next = whole-project next-best-action; gz next --pool = pool-scoped subset; /pool-triage becomes a pool-scoped mode of the renamed steering skill. HEADLINE CAPABILITY: gz next (whole-project best-next-closable-task) is wielded by a SEPARATE GHI-routed skill gz-next (renamed from the proposed gz-triage because it is whole-project, not GHI-flavored; ghi-triage stays the GHI-queue ranker). This ADR authors substrate/software ONLY; the gz-next skill is a downstream GHI, not authored here. BINDING DOCTRINES (cite, obey, do not duplicate): ADR-0.0.38 evidence-authority-projection - every surface here is Evidentiary/Projection and NEVER binds a gate; ADR-0.0.39/0.0.40 llm-as-judge - NO LLM inference in the deterministic routing/ranking (gz next is a deterministic decision table). All read-views are pointer-only, Layer-3-never-source-of-truth, with *-fresh drift validators. Decision items (1:1 with the six-item OBPI decomposition, leaf-first): (1) tdd-receipt-stream hub (event-kind registry plus append-only emission; the one-way-ish receipt event-kind schema lands FIRST and is got right before any consumer); (2) gz next (CAP-22) plus CAP-08 MODE (deterministic decision table over ledger/OBPI/ADR state; surfaces, never auto-executes, human gates); (3) gz metrics read-view over the stream; (4) queryability verbs gz search (FTS5) and gz insights query; (5) solved-problem-pattern-corpus read-surface (governed; append-only; citation-bound); (6) subsume ADR-0.0.46/47/48 into gz next / gz next --pool and re-home /pool-triage as a pool-scoped mode of gz-next. Lane: heavy (adds new CLI verbs gz next, gz metrics, gz search, gz insights query, and new ledger event types via the receipt stream). Foundation-kind brief-level Gate 5 attestation per ADR-0.0.36 (universal). Reversibility is mostly two-way (read-layer over append-only data; verbs removable with data intact; the 46/47/48 subsumption reversible while unbuilt); the one-way-ish element is the receipt event-kind schema (OBPI 1).

### Q: What good things result from this decision? List benefits.

**A:** 1. Consolidates roughly nine scattered dormant artifacts (six pool ADRs plus three booked-but-unbuilt foundation ADRs) into ONE substrate with a clear leaf-first OBPI sequence. 2. Gives agents a deterministic 'next best move' (gz next) over current governance state - a decision table, not LLM inference - directly attacking the under-consultation-of-state failure that grows with the repo. 3. Builds the long-overdue ledger/insights/ARB queryability (gz search over FTS5, gz insights query) so prior decisions and corrections are deterministically recallable rather than re-derived from stochastic memory. 4. Shares the tdd-receipt-stream receipt hub with the Harness Hardening enforcement spine: one event source, two consumers (enforcement reads it, orientation reads it), so the stream is not doubled. 5. The queryability layer is architected to survive engine failure: gz search, gz insights query, and raw ledger reads do NOT depend on the gz next engine - when the next-best-action engine is down, raw recall still works. 6. Unifies pool-scoped triage under the same engine: gz next is whole-project, gz next --pool is the pool-scoped subset, /pool-triage becomes a pool-scoped mode of gz-next - one engine, not three parallel CLI surfaces. 7. Obeys the evidence/authority and llm-as-judge doctrines by construction: every surface is Evidentiary/Projection (ADR-0.0.38) and routing is a deterministic decision table (ADR-0.0.39/0.0.40) - no LLM in the gate or ranking path. 8. Forces clean downstream follow-ups rather than swallowing them: a separate execution-memory-graph ADR (read vs compute), agent-reliability-framework stays separate, the gz-next skill ships as its own GHI, and the return-to-health plan gains a reference to this ADR in the Harness Hardening workstream.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. A new heavy foundation ADR is promoted DURING the return-to-health recovery freeze - the Architectural Boundary 1 / Operating Rule 6 cost, consciously waived by the operator on the routing facts, but real and named. 2. Implementation bandwidth competes with the emergency GHI #519 remediation; the pre-mortem's most plausible failure is exactly this - promoted during recovery then starved of bandwidth while #519 consumes everything, leaving it another dormant unbuilt foundation ADR. 3. The gz next decision table may not match real 'best next' judgment; if weak, agents ignore it. Mitigation per ADR-0.0.39: do NOT add LLM to the gate path - degrade to advisory, never to vibe. 4. gz next vs gz next --pool semantics could collide if not designed cleanly; named in the pre-mortem; the UNIFY framing (whole-project vs pool-scoped subset of the same engine) is the mitigation, but the risk is real until OBPI 2/6 land. 5. The tdd-receipt-stream hub could become a parallel stream alongside the ledger instead of THE source, doubling state; the hub-first ordering (OBPI 1) and the Layer-3-never-source-of-truth constraint are the mitigations; the receipt event-kind schema is the one-way-ish element that must be got right first. 6. The solved-problem-pattern-corpus read-surface carries the standing governed-corpus risk (free-form learnings reproduce training-corpus bias if ungoverned); the four governance invariants (append-only, Layer-2, citation-bound, skill-written) are inherited from the pool ADR and must hold or the surface should be rejected. 7. Subsuming three booked foundation ADRs (0.0.46/47/48) into this one creates a verified-demotion obligation the main session must discharge; until then the supersession is declared-but-not-executed, which is itself a tracked follow-up, not a silent state.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. tdd-receipt-stream-hub: Establish the tdd-receipt-stream as THE shared append-only governance-event receipt stream - event-kind registry plus append-only emission path. Fold in the rival ADR-pool.tdd-emission-and-graph-rot-remediation (verified RED/GREEN emission semantics). This is the hub the Harness Hardening enforcement spine ALSO consumes; the receipt event-kind schema is the one-way-ish element, so it lands FIRST and is got right before any consumer. Layer-3-never-source-of-truth; the ledger remains system-of-record. (heavy lane: new ledger event types).
2. gz-next-cap22-and-cap08-mode: Implement gz next (CAP-22) - whole-project deterministic decision-table next-best-action over ledger/OBPI/ADR state - plus the CAP-08 MODE per-invocation intent surface (READ-ONLY / PLAN-FIRST / IMPLEMENT). Decision table is deterministic per ADR-0.0.39/0.0.40 (NO LLM inference). Output modes gz next / --dry-run / --explain; never auto-executes Gate 5 or destructive ops - surfaces human gates and waits. CAP-08 tiers, CAP-09, CAP-10, CAP-21 stay PARKED. (heavy lane: new CLI verb).
3. gz-metrics-read-view: Implement gz metrics - a read-view over the receipt stream computing throughput, duration, defect rate, rework cycles, WIP, and trend. Read-view only (collapses the proposed parallel session-metrics.jsonl into a read over the unified stream); Layer-3 derived; freshness drift validator. (heavy lane: new CLI verb).
4. queryability-search-and-insights-query: Implement gz search (stdlib SQLite FTS5 index over ledger events, handoffs, and insights; gz search rebuild for full rebuild) and gz insights query (browsable-by-topic read over agent-insights.jsonl). Both MUST be independent of the gz next engine so reads survive engine failure (the 2am-operator invariant). Layer-3 derived; freshness validators. (heavy lane: new CLI verbs).
5. solved-problem-pattern-corpus-read-surface: Implement the solved-problem pattern corpus as a governed prior-art memory read-surface, bound by the four invariants (append-only, Layer-2, each entry cites primary evidence, skill-written never hand-edited). Provides the aggregated recurring-failure-pattern artifact that per-occurrence search does not. (heavy lane: new read surface over governed corpus).
6. subsume-pool-management-into-gz-next: Subsume ADR-0.0.46 pool-management, ADR-0.0.47 pool-dag-promotion-routing, and ADR-0.0.48 gz-adr-pool-triage into the unified engine: gz next --pool is the pool-scoped subset of gz next, gz pool graph is the pool DAG read, and /pool-triage becomes a pool-scoped MODE of the renamed gz-next steering skill. This ADR DECLARES the supersession; the verified demotions of 0.0.46/47/48 are a follow-up the main session discharges. (heavy lane: CLI surface unification; declared supersession).

### Q: What alternatives were considered and why were they rejected?

**A:** 1. Leave the six pool ADRs plus the three booked foundation ADRs (0.0.46/47/48) scattered as-is. REJECTED - that scattered dormant sprawl is precisely the condition the operator directed me to coalesce; doing nothing perpetuates the under-consultation failure. 2. Fold execution-memory-graph and agent-reliability-framework into this ADR as well. REJECTED - that swallows the repository and conflates three distinct concerns: a read-substrate (this ADR), a runtime work-node graph that COMPUTES readiness (execution-memory-graph; gz next READS state, the graph COMPUTES it), and a standards-grade reliability framework (agent-reliability-framework, AR0-AR4 / GBOM). Each stays a separate ADR. 3. Author this as the Harness Hardening ENFORCEMENT spine (the tool-permission-classifier / skill-behavioral-hardening / harness-aware-execution-modes promotion chain). REJECTED - that is the enforcement lens on the shared tdd-receipt-stream hub; THIS ADR is the ORIENTATION lens on the same hub. Same hub, two consumers, two ADRs - not one. 4. Pipeline/LLM-inferred next-best-action instead of a deterministic decision table. REJECTED - ADR-0.0.39/0.0.40 forbid LLM inference in the routing/ranking gate path; if the deterministic table proves weak, the correct degrade is advisory, never vibe. 5. Make the next-best-action engine the dependency for all queryability (gz search / gz insights query route through gz next). REJECTED - the 2am-operator forcing function requires raw recall to survive engine failure; the queryability layer must NOT depend on the next-best-action engine. 6. A parallel session-metrics.jsonl store for gz metrics. REJECTED - the tdd-receipt-stream generalization already collapses metrics into a read-view over the unified ledger event stream; a parallel store doubles state.


## Stress-test forcing-function answers (Tier 2)

Drafted from the design session; the operator amends at review.

**Pre-mortem (18 months out, failed spectacularly):** (a) it became another dormant unbuilt foundation ADR — promoted during recovery then starved of bandwidth while GHI #519 consumed everything; (b) the `gz next` decision table didn't match real "best next" judgment, so agents ignored it; (c) `gz next` vs `gz next --pool` semantics collided; (d) `tdd-receipt-stream` became a parallel stream alongside the ledger instead of THE source, doubling state. Mitigations: leaf-first sequencing with the hub schema (OBPI-01) got right first; deterministic-table degrade-to-advisory (never LLM) per Boundary Invariant 2; the UNIFY framing (whole-project vs pool-scoped subset of one engine); Layer-3-never-source-of-truth per Boundary Invariant 3.

**What would have to be true (this is right):** (i) `tdd-receipt-stream` genuinely unifies as the single event source; (ii) the decision table earns agent trust; (iii) recovery (GHI #519) closes so build bandwidth exists. Shakiest condition is (iii) — bandwidth contention during recovery; the operator's explicit Boundary-1 waiver on the routing facts is the conscious acceptance of that risk, and the closing-question follow-up (a return-to-health plan edit referencing this ADR in the Harness Hardening workstream) is the structural mitigation.

**What would have to be true (Alternative B — fold pool-management's CLI into a separate ADR rather than subsuming it here — to be better):** only if `pool-management`'s CLI were large or independent enough to bloat the unified ADR. But ADR-0.0.46/0.0.47/0.0.48 are booked-but-unbuilt (zero OBPIs implemented), so subsumption is cheap — re-homing an unbuilt surface costs far less than maintaining a parallel pool-triage ADR track. Not credible that a separate track is better.

**Constraint archaeology:** the "no new foundation ADR during recovery" freeze (Architectural Boundary 1 / Operating Rule 6) is real and load-bearing — it exists to keep the return-to-health recovery focused while `gz check` stabilizes. But the return-to-health plan itself reserves an operator waiver ("an explicit operator decision against the Architectural Boundary 1 freeze (Operating Rule 6) — not a default"). The constraint is a recovery-posture constraint consciously overridden by the authority who owns it, on the routing facts — not an inherited convention nobody re-examined.

**Assumptions surfaced:** (a) `tdd-receipt-stream` (not `execution-memory-graph`) is the right orientation hub — defensible on the read-vs-compute seam: `gz next` READS state, the graph COMPUTES readiness; (b) deterministic-table routing suffices — if it proves weak, ADR-0.0.39 forbids adding LLM to the gate path, so the degrade is to advisory, not to vibe; (c) recovery (GHI #519) closes so bandwidth exists. The counter-truth for each is named: read-vs-compute boundary (a), degrade-to-advisory (b), and the bandwidth-contention pre-mortem (c).

**2am operator question:** "`gz next` is down — how do I find out where the work stands?" Raw queryability (`gz search`, `gz insights query`, and direct ledger reads) MUST still work; the queryability layer MUST NOT depend on the next-best-action engine. This is Boundary Invariant 4 — reads are layered so they survive engine failure.

**Reversibility:** Mostly two-way. The substrate is a read-layer over append-only data: verbs can be removed with the underlying data intact; the ADR-0.0.46/0.0.47/0.0.48 subsumption is reversible while those ADRs are unbuilt. The one-way-ish element is the receipt event-kind schema — once events are written under a schema, changing it is migration-shaped. Mitigation: get the hub registry (OBPI-01) right first, before any consumer depends on it. Reversal cost in 12 months: low for the verbs/read-views, migration-shaped for the event-kind schema.

**Scope minimization:** smallest valuable unit = the `tdd-receipt-stream` hub (OBPI-01) + `gz next` (OBPI-02). The read-views and queryability (OBPIs 03–05) are additive; the subsumption (OBPI-06) lands last. If bandwidth halved, ship the hub + `gz next` only and defer 03–06 — the orientation value proposition is intact with just those two.

**Downstream ADRs/work forced (closing question):** (i) a separate `execution-memory-graph` ADR (the runtime work-node graph that COMPUTES readiness — read vs compute seam); (ii) `agent-reliability-framework` stays a separate standards-grade ADR; (iii) the `gz-next` SKILL as its own GHI (this ADR is substrate/software only); (iv) the verified demotions of ADR-0.0.46/0.0.47/0.0.48 + the six coalesced pool ADRs (the main session's follow-up); (v) a return-to-health plan edit referencing this ADR in the Harness Hardening workstream as the orientation sibling of the enforcement spine.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. Leave the six pool ADRs plus the three booked foundation ADRs (0.0.46/47/48) scattered as-is. REJECTED - that scattered dormant sprawl is precisely the condition the operator directed me to coalesce; doing nothing perpetuates the under-consultation failure. 2. Fold execution-memory-graph and agent-reliability-framework into this ADR as well. REJECTED - that swallows the repository and conflates three distinct concerns: a read-substrate (this ADR), a runtime work-node graph that COMPUTES readiness (execution-memory-graph; gz next READS state, the graph COMPUTES it), and a standards-grade reliability framework (agent-reliability-framework, AR0-AR4 / GBOM). Each stays a separate ADR. 3. Author this as the Harness Hardening ENFORCEMENT spine (the tool-permission-classifier / skill-behavioral-hardening / harness-aware-execution-modes promotion chain). REJECTED - that is the enforcement lens on the shared tdd-receipt-stream hub; THIS ADR is the ORIENTATION lens on the same hub. Same hub, two consumers, two ADRs - not one. 4. Pipeline/LLM-inferred next-best-action instead of a deterministic decision table. REJECTED - ADR-0.0.39/0.0.40 forbid LLM inference in the routing/ranking gate path; if the deterministic table proves weak, the correct degrade is advisory, never vibe. 5. Make the next-best-action engine the dependency for all queryability (gz search / gz insights query route through gz next). REJECTED - the 2am-operator forcing function requires raw recall to survive engine failure; the queryability layer must NOT depend on the next-best-action engine. 6. A parallel session-metrics.jsonl store for gz metrics. REJECTED - the tdd-receipt-stream generalization already collapses metrics into a read-view over the unified ledger event stream; a parallel store doubles state.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.66 | Pending | | | |
