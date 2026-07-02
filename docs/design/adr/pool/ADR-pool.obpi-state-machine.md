---
id: ADR-pool.obpi-state-machine
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: openai/symphony
amendments:
  - 2026-05-02 — added § Amendment 2026-05-02 (per-lane concurrency caps as state-machine invariant)
  - 2026-05-19 — added § Amendment 2026-05-19 (canonical failure-class taxonomy + named runtime event vocabulary, inspired by Symphony SPEC.md §14 + §10.4)
promoted_to: ADR-0.31.0-obpi-state-machine
---

# ADR-pool.obpi-state-machine: OBPI State Machine and Runtime Invariant Monitor
> Promoted to `ADR-0.31.0-obpi-state-machine` on 2026-07-02. This pool file is retained as historical intake context.


## Status

Superseded

## Intent

Replace the current choreography of ~30 independent audits and reconcilers
with a **canonical OBPI state machine** that names every legal state, every
legal transition, every transition's preconditions and witness requirements,
and a **runtime invariant monitor** that fires on every state-affecting
operation rather than only at ceremony boundaries.

This ADR exists because gzkit's governance surface today is **choreographed,
not state-machined**: each individual audit and reconciler is correct in
isolation, but the system as a whole works only when ceremonies fire on
schedule and operators do not hand-edit. The first time either assumption
fails — the ledger gets out of step, an operator pulls a brief without a
CLI verb, an attestation is bundled into a sync, a frontmatter term is
edited directly — the choreography decoheres and the only recovery is "run
reconcile and hope it picks the right answer."

**Canonical observed symptom (2026-04-27, OBPI-0.0.21-08 Stage 5).**
`OBPI-0.31.0-02-complexity-check.md` was operator-marked `status: Withdrawn`
by hand-edit. There was no `gz` command for "withdraw an OBPI", so no
ledger event was emitted. When `gz frontmatter reconcile` ran during a
*different* OBPI's precomplete, it observed L3-frontmatter (`Withdrawn`,
mapping to `abandoned`) disagreeing with L2-ledger (no completion or
abandonment event → `pending`), applied L2-wins per ADR-0.0.9 Rule 1, and
silently rewrote the brief to `status: pending`. Operator intent was
erased. See GHI #348 for the symptom; see GHI #347 for the adjacent vocab
gap that surfaced it.

This is not a bug in the reconciler. The reconciler is doing exactly what
ADR-0.0.9 mandates. The bug is that **gzkit has no event vocabulary for
withdrawal** and **no runtime monitor catching the silent rewrite**, so
the ledger-wins rule fires correctly but on incomplete information.

The same shape recurs across the surface:

- **Status-vocabulary proliferation** in
  `gzkit.governance.status_vocab.STATUS_VOCAB_MAPPING`: `Draft` /
  `Proposed` / `Pending` / `Pool` / `Promoted` all map to `pending`;
  `Pending-Attestation` / `Completed` / `Attested` / `attested_completed`
  all collapse into the same canonical territory. The synonyms accreted
  because there was no canonical state machine to author against —
  operators (and agents) reached for natural-language status terms,
  the reconciler tolerated them, and the vocab table grew. **The
  vocab table is the choreography; it would be the state-enum if the
  state machine existed.**
- **Witness handling bolted onto one command** under GHI #290 and
  GHI #292: agent-relayed operator attestation (`--attestor-present`) was
  bolted onto exactly one CLI command (`gz obpi complete`) rather than
  declared as a transition guard at every surface where the
  `attested_completed` transition can fire. The bolted-on guard is a
  workaround for the absence of a single transition-witness contract.
- **Reconcile-then-precomplete loops**: the typical Stage 5 pattern is
  three rounds of "fix one thing, re-run, find next thing" because
  there is no single surface that says "here is the state of OBPI-X
  and here is what is preventing its next transition." Each
  precondition is checked by a separate validator firing on demand.
- **Frontmatter rewrite cascades during precomplete**: drift accumulates
  silently across briefs and only surfaces when one specific OBPI's
  precomplete forces a global reconcile. The OBPI-0.0.21-08 Stage 5
  rewrote 3 unrelated files (`ADR-0.0.23` lane drift, `ADR-0.0.35` lane
  drift, `OBPI-0.31.0-02` Withdrawn demotion). All three were silent
  drift the system tolerated until one ceremony forced the audit.

The architectural absence is not in any one of these places. It is the
**missing source-of-truth artifact** that all of them should derive from.

## Decision

Define, schema-bind, and runtime-enforce an OBPI state machine with the
following five properties:

1. **Named states (closed enum, schema-bound).** Every OBPI is in
   exactly one of: `drafted`, `planned`, `implementing`, `verified`,
   `attested`, `synced`, `withdrawn`, `superseded`. The current
   `STATUS_VOCAB_MAPPING` becomes a *legacy-import* table only — new
   briefs author against the closed enum directly, and the vocab table
   shrinks rather than grows.

2. **Named transitions (closed enum, schema-bound).** Every state
   change is an event with a name (e.g. `obpi.transitioned.attested`),
   declared preconditions (predecessor state, required adjacent
   evidence), declared postconditions (successor state, emitted
   ancillary events), and a declared witness requirement: `human_attested`
   (a human attests — transport-agnostic, relayed verbatim via
   `--attestor-present` / `--attestation-text`) or `self_close` per
   Exception-mode rules. Human attestation is sacrosanct and
   transport-agnostic; no TTY/PTY/interactive-terminal mechanism gates the
   witness — the mechanism serves the attestation, never gates it
   (canon-owner directive). The witness requirement is a property of the
   transition, not of one CLI command.

3. **Receipts ARE the events.** Today receipts are adjuncts that need a
   separate reconciler to align with state — the receipt sits in
   `artifacts/receipts/`, the ledger has its own event, the brief
   frontmatter has its own marker, and they are aligned by ceremony.
   Under this ADR, **emitting a receipt IS the state transition**:
   the receipt's existence is the canonical proof that the transition
   fired, and there is no separate ledger-mirror to drift against.
   This subsumes ADR-0.0.24's attestation-receipt-binding into the
   broader transition-witness contract.

4. **A single invariant monitor.** Every read or write to the artifact
   graph passes through one monitor that asserts: (a) the operation
   names a transition declared in (2); (b) preconditions are
   satisfied; (c) the witness requirement is met. A frontmatter
   hand-edit that is not backed by a declared transition is either
   **rejected** (no matching transition allowed) or **auto-emits the
   transition** (so receipts and state never disagree). Today the
   reconciler silently picks a winner; the monitor would refuse to let
   them disagree in the first place.

5. **Withdraw / supersede are first-class transitions.** `gz obpi
   withdraw OBPI-X.Y.Z-NN --rationale ...` and `gz obpi supersede
   OBPI-X.Y.Z-NN --by OBPI-Y.Y.Y-MM` emit canonical transitions with
   their own receipts, witness requirements, and lifecycle
   semantics. The Withdrawn-demotion failure (GHI #348) is closed
   because (a) a hand-edit `Withdrawn` is rejected by the monitor
   pointing at the canonical transition CLI; (b) once the transition
   fires, the ledger has the event and the reconciler has nothing to
   "fix."

## Target Scope

This promotion realizes the **airlock-critical tracer** of the state machine —
the first end-to-end slice (schema → model → monitor → CLI → ledger), **not** the
full eight-property machine. The tracer pierces the whole vertical once so the
keystone (the runtime monitor) can be proven against its landing falsifier before
breadth expansion (tracer-bullet discipline; `docs/governance/airlock-in-constellation-2026-06-30.md`
§ Volume declaration / § Pre-registered falsifiers).

- **state-transition-models** — Closed `StrEnum` OBPI state name-set (`drafted`,
  `planned`, `implementing`, `verified`, `attested`, `synced`, `withdrawn`,
  `superseded`) plus Pydantic `State` and `Transition` models declaring each
  transition's predecessor state, required adjacent evidence, and witness
  requirement; schema-bound. The state anchor the monitor and CLI verbs consume
  (§ Decision rules 1–2).
- **withdraw-supersede-transitions** — Elevate the existing `gz obpi withdraw`
  event-recorder into a first-class monitor-backed transition and build the
  missing `gz obpi supersede OBPI-X --by OBPI-Y` verb; both emit canonical
  transition events (`obpi.transitioned.withdrawn` / `.superseded`). Closes the
  GHI #348 root cause: withdrawal becomes a witnessed transition, not a hand-edit
  the reconciler silently demotes (§ Decision rule 5).
- **runtime-invariant-monitor** — The load-bearing monitor on the artifact-graph
  read/write boundary: it classifies each state-affecting operation against a
  declared transition, rejects undeclared ones, and **refuses a silent `status:`
  frontmatter drift (the GHI #348 class) in production config**. This refusal is
  the constellation's pre-registered landing falsifier (airlock-in
  § Pre-registered falsifiers #1) and gates Phase 2 / HULL (§ Decision rule 4).

### Deferred-in-keel (later OBPIs of this ADR; NOT in this checklist)

Declared by this ADR but out of the tracer slice; each lands as a subsequent OBPI
after the tracer's landing falsifier is proven live: full choreography retirement
(§ Decision rule 4 migration of the ~30 reconcilers), receipts-ARE-events
subsumption (rule 3), per-lane/kind/sensitivity concurrency caps (Amendment
2026-05-02 / property 6), the canonical failure-class taxonomy (Amendment
2026-05-19 / property 7), the named runtime event-vocabulary table (property 8),
and the `STATUS_VOCAB_MAPPING` shrink-to-import-only. The `foundation` enum
abolition remains Movement IV, not this ADR.

## Proposed OBPI Decomposition

| # | Slug | Description | Lane |
|---|------|-------------|------|
| 01 | state-transition-models | Closed StrEnum state name-set + Pydantic State/Transition models (preconditions, adjacent-evidence, witness) with schema binding | Heavy |
| 02 | withdraw-supersede-transitions | Elevate withdraw to a monitor-backed first-class transition and build `gz obpi supersede`; both emit canonical transition events; closes GHI #348 root | Heavy |
| 03 | runtime-invariant-monitor | Runtime invariant monitor on the artifact-graph read/write boundary that refuses silent `status:` frontmatter drift (GHI #348 class) in production — the pre-registered landing falsifier | Heavy |

## Alternatives Considered

### A. Continue extending the choreography (status quo, rejected)

Add more audits, more reconcilers, more vocab terms, more bolted-on
guards as failures surface. This is the path that produced the
current state. The anti-vibing mantra (`AGENTS.md` § MAKE LLM
STOCHASTIC VIBES INERT) names this shape: each addition is locally
correct and globally incoherent. **Concrete cost named:** the
OBPI-0.0.21-08 Stage 5 sequence ran six tooling rounds (precomplete →
reconcile → precomplete → complete → lock-release → git-sync) and
required a 1-line direct fix mid-flight (GHI #347) and surfaced one
silent-rewrite defect (GHI #348). Both #347 and #348 are tabular
symptoms of the absent state machine. Continuing to file them
individually is not a solution; it is the failure mode rendered as
issue tracker.

### B. State machine without runtime monitor (rejected)

Define the closed-enum states and transitions, but continue to
enforce them via batch reconcilers that fire at ceremony moments. This
is "ADR-0.0.16 plus stricter vocabulary" — it closes the synonym
sprawl but does not close the silent-edit class. An operator who hand-
edits `status: Withdrawn` between reconcile cycles still creates a
window in which L1 (canon) and L2 (ledger) disagree, and the
reconciler still has to pick a winner. **The runtime monitor is the
load-bearing piece**, not the schema enum.

### C. Runtime monitor without state machine (rejected)

Build a monitor that observes every read/write and emits warnings,
without first defining the state space it monitors. This is the
worst-of-both — a monitor that fires on every change but cannot say
*what state the system is in or which transition it is asserting* is
just a more verbose audit log. The canonical states must precede the
monitor, not follow it.

### D. Replace ledger with a state-machine engine (rejected as scope)

Migrate `.gzkit/ledger.jsonl` to a stateful engine (sqlite, kv store,
or a third-party state-machine library). Rejected: gzkit's
stdlib-first doctrine (`AGENTS.md` § STDLIB-FIRST DOCTRINE) and
ADR-0.0.10 (storage tiers — simplicity profile) both rule against
this. The append-only JSONL ledger is the right tier; the state
machine should be derived from it, not replace it. Pydantic models
and a stdlib-only event-sourcing pattern are sufficient.

## Relationship to existing ADRs

| ADR | Role under this state machine |
|---|---|
| ADR-0.0.9 (state-doctrine) | Foundation. The L1/L2/L3 hierarchy is preserved; this ADR defines *what L2 events exist* and how they bind L1 and L3. |
| ADR-0.0.16 (frontmatter-ledger coherence) | Subsumed. The coherence guard becomes a property of the runtime monitor (rule 4) rather than a batch reconciler. |
| ADR-0.0.24 (attestation-receipt binding) | Subsumed. The receipt-attestation binding becomes a property of the `attested` transition's witness contract (rule 2 / rule 3). |
| ADR-0.0.31 (distribution-invariant doctrine, T0) | Independent. T0 governs wheel→consumer delivery; this ADR governs runtime state. They share trust-doctrine vocabulary but not surface area. |
| ADR-0.0.32 (canonical-surface packaging) | Independent. Layout + scaffolding; not state. |
| ADR-pool.execution-memory-graph | Adjacent. The execution-memory graph is one *consumer* of the state machine; the state machine is upstream. |

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

This ADR is **foundation-kind** material when promoted (it codifies an
app-system invariant — every OBPI's lifecycle — and binds every governance
surface). Promotion would be `gz adr promote ADR-pool.obpi-state-machine
--kind foundation --semver 0.0.<next>`.

**Suggested next ADRs / OBPIs once promoted:**

1. State enum + transition enum + Pydantic schemas (foundation, lite —
   schema and model only, no runtime change yet).
2. Withdraw/supersede CLI verbs (heavy — adds CLI surface, closes
   GHI #348 root cause).
3. Runtime invariant monitor on the artifact graph read/write boundary
   (heavy — the load-bearing piece).
4. Migrate `gz obpi complete` / `gz obpi reconcile` /
   `gz frontmatter reconcile` from batch-reconciler shape to
   transition-emitter shape (heavy — the choreography retirement).
5. `STATUS_VOCAB_MAPPING` shrink-to-import-only (lite — vocab freeze).

**Surfaced by:** Operator review during OBPI-0.0.21-08 closeout
(2026-04-27). Operator quote: *"we lack a proper statemachine that governs
receipts vs. adr/opbi state. we have tooling to reconcile, but not a
runtime state machine that monitors — its all vibey."*

**Related GHIs:**
- GHI #347 — STATUS_VOCAB_MAPPING missing 'Withdrawn' (vocab gap, fixed)
- GHI #348 — frontmatter reconcile silently demoted Withdrawn → pending (symptom)
- GHI #349 — gzkit governance surface is choreographed not state-machined (architectural absence; this ADR is the durable home)

---

## Amendment 2026-05-02: Per-lane concurrency caps as a state-machine invariant

The `openai/symphony` SPEC.md (released 2026-04-23,
[github.com/openai/symphony](https://github.com/openai/symphony)) names a
mechanism gzkit currently lacks: `agent.max_concurrent_agents_by_state` —
per-state dispatch caps that bound how many workers may occupy a given
state simultaneously (e.g., limit `"In Progress"` to 3 concurrent agents
while allowing 10 globally). The gzkit equivalent is **per-lane / per-kind
concurrency caps** as a state-machine invariant rather than a runtime
config knob.

### Sixth state-machine property (added to § Decision)

6. **Per-lane / per-kind / per-sensitivity concurrency invariants.** The
   runtime monitor (rule 4) asserts dispatch caps as a precondition of the
   `implementing` and `attested` transitions:

   - **Heavy-lane single-flight.** At most one OBPI may occupy
     `implementing` or `attested-pending` simultaneously when its parent
     ADR is `lane: heavy`. The Gate-5 attestation surface is operator-
     attention-bound; concurrent heavy attestations are an attention-race
     defect, not a throughput optimization. Codifies what
     [`heavy-lane`](ADR-pool.heavy-lane.md) implies but never names.
   - **Foundation-kind single-flight.** Same invariant for `kind:
     foundation` parent ADRs regardless of lane. Foundation-kind walkthrough
     discipline (`AGENTS.md` § OBPI Acceptance Protocol) fires per-brief; two
     foundation OBPIs in flight create the same attention race as two heavy
     OBPIs.
   - **Security-sensitivity single-flight.** Same invariant for OBPIs
     carrying `sensitivity: security` per [ADR-0.0.22](../foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md).
     The three-axis OR from `_requires_human_obpi_attestation` collapses to
     one cap: any axis flagging brief-level attestation rigor binds the
     same single-flight invariant.
   - **Lite-feature parallelism is uncapped at the state-machine layer.**
     [`wave-dependency-execution`](ADR-pool.wave-dependency-execution.md)
     owns the wave-bounded parallelism story for lite work. The state
     machine asserts only the attestation-attention invariant; throughput
     is wave-orchestrator's surface.

### Mechanical predicate (binding when promoted)

The runtime monitor's transition guard for `obpi.transitioned.implementing`
and `obpi.transitioned.attested` becomes a three-way OR rejecting dispatch
when any axis is occupied:

```
deny if (
    parent_lane == "heavy" and any_obpi_in_state(implementing|attested-pending, parent_lane="heavy")
) or (
    parent_kind == "foundation" and any_obpi_in_state(implementing|attested-pending, parent_kind="foundation")
) or (
    sensitivity == "security" and any_obpi_in_state(implementing|attested-pending, sensitivity="security")
)
```

This is the same three-way OR as the Lane & Kind & Sensitivity Attestation
Matrix in `AGENTS.md` § OBPI Acceptance Protocol, applied to dispatch
admission rather than completion authorization. The matrix and the
concurrency cap share one predicate; if matrix and cap disagree, code is
source of truth (matrix and cap are projections).

### Coupled-surface coherence

- **[`wave-dependency-execution`](ADR-pool.wave-dependency-execution.md)** —
  consumes this invariant. Wave 1 may contain N lite-feature OBPIs but at
  most one heavy-or-foundation-or-security OBPI; wave planner respects the
  cap rather than re-deriving it.
- **[`change-isolation-workspace`](ADR-pool.change-isolation-workspace.md)
  § Amendment 2026-05-02** — worktree spawn happens *after* the dispatch
  guard fires green. A heavy OBPI lock-claim that violates the cap is
  rejected before the worktree is created.
- **[`obpi-pipeline-dispatch-attestation`](ADR-pool.obpi-pipeline-dispatch-attestation.md)** —
  dispatch receipts include the cap-check evidence (which OBPIs are
  currently occupying which axes), making the guard's decision auditable.
- **[ADR-0.0.18](../foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md)
  / ADR-0.0.22 / ADR-0.0.36** — the lane/kind/sensitivity axes of the
  attestation matrix become the same axes of the concurrency matrix. One
  doctrine surface, two enforcement points.

### Distinct from Symphony

- **Lane/kind/sensitivity, not workflow-state.** Symphony caps by
  workflow-state (`"In Progress"`); gzkit caps by attestation-attention
  axes. The choice is invariant-shaped, not throughput-shaped.
- **State-machine property, not runtime config knob.** Symphony exposes
  the cap via `WORKFLOW.md` for live reload; gzkit binds it as a transition
  guard derived from foundation ADRs (0.0.18 / 0.0.22 / 0.0.36). Operators
  cannot raise heavy-lane parallelism by editing config — they would have
  to amend foundation doctrine.
- **Fail-closed dispatch, not queueing.** Symphony queues blocked
  dispatches for retry; gzkit rejects with a structured blocker envelope
  ([`structured-blocker-envelopes`](ADR-pool.structured-blocker-envelopes.md))
  naming which axis is occupied, by which OBPI, since when. Operator
  course-correction surface, not invisible throughput shaping.

### Inspired By (extended)

[openai/symphony SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md)
§ Per-State Concurrency Control (`agent.max_concurrent_agents_by_state`).
The mechanism is generalizable; the axes (workflow-state vs. attestation-
attention) are domain-specific.

---

## Amendment 2026-05-19: Canonical failure-class taxonomy + named runtime event vocabulary

The `openai/symphony` SPEC.md (re-read 2026-05-19 in full) names two
mechanisms gzkit's pool ADR has implied but not enumerated: **§14 Failure
Model and Recovery Strategy** (closed-enum failure classes, each with named
recovery behavior) and **§10.4 Emitted Runtime Events** (closed-enum named
event vocabulary emitted upstream from workers to the orchestrator). The
gzkit equivalents are the **pipeline-state failure taxonomy** and the
**transition-event vocabulary** — both schema-bound, both runtime-monitored
under rule 4, both first-class.

### Seventh state-machine property (added to § Decision)

7. **Canonical failure-class taxonomy with named recovery behaviors.**
   Pipeline-state failures form a closed enum, schema-bound in
   `data/obpi_failure_classes.json`, each with a declared recovery
   behavior the runtime monitor (rule 4) consults when the transition is
   rejected. Initial classes (extensible by amendment, closed at
   any given release):

   | Failure class | Trigger | Recovery behavior |
   |---|---|---|
   | `precondition_unsatisfied` | Transition attempted from a state whose declared preconditions do not hold (e.g., `attested` attempted while predecessor state is not `verified`) | Emit `RemediationPayload` (ADR-0.0.53) naming the predecessor-transition CLI; no state change; no receipt |
   | `witness_missing` | Transition attempted without the witness declared in rule 2 (e.g., `attested` without a `human_attested` witness) | Block transition; emit `obpi.witness_required` event; operator-required-action surface |
   | `receipt_fabrication_detected` | Transition's witness receipt fails ARB receipt-binding (ADR-0.0.24) — receipt ID does not resolve, hash does not match, name does not satisfy CANONICAL_STEP_COMMANDS regex | Reject transition; emit `obpi.receipt_fabrication_blocked`; ARB receipt-binding error in operator stream |
   | `vocab_out_of_enum` | Hand-edited frontmatter status term not in the closed enum (rule 1) and not in the legacy-import vocab table | Reject edit at monitor (rule 4); emit `obpi.frontmatter_rejected`; recovery payload names canonical CLI verb |
   | `frontmatter_ledger_disagreement` | L1 (canon) and L2 (ledger) disagree after a write (the failure mode GHI #348 named) | Auto-emit the declared transition that reconciles them OR reject the write (depending on which side mutated last); never silent rewrite |
   | `monitor_rejected_edit` | Read/write to the artifact graph names a transition not declared in rule 2 | Reject at the monitor boundary; emit `obpi.unknown_transition_blocked`; operator must either route through a declared CLI verb or add the transition to the enum under an amendment ADR |
   | `concurrency_cap_violated` | Heavy-lane / foundation-kind / security-sensitivity single-flight cap from Amendment 2026-05-02 is occupied | Reject dispatch with a `structured-blocker-envelope` naming the occupying OBPI; no queueing |

   The taxonomy is **fail-closed by default** — unrecognized failure
   shapes route to `monitor_rejected_edit` rather than silently producing
   an unclassified rejection. Each class's recovery binds to the
   `RemediationPayload` contract from ADR-0.0.53 so the agent reading the
   rejection has a structured next step.

### Eighth state-machine property (added to § Decision)

8. **Named runtime event vocabulary table.** Every state-affecting
   operation emits a named event from a closed enum declared in
   `data/obpi_event_vocabulary.json`. The vocabulary is the same shape
   as the state enum (rule 1) and transition enum (rule 2) — closed,
   schema-bound, monotonically growing only via amendment ADRs. Initial
   vocabulary (extensible):

   **Transition events** (one per declared transition; mirror rule 2):

   - `obpi.transitioned.drafted` — emitted on initial brief creation
   - `obpi.transitioned.planned` — emitted on plan-audit attestation
   - `obpi.transitioned.implementing` — emitted on Stage 1 → Stage 2
   - `obpi.transitioned.verified` — emitted on Gate 2 pass with receipt
   - `obpi.transitioned.attested` — emitted on Gate 5 human/agent-relayed witness
   - `obpi.transitioned.synced` — emitted on `gz git-sync` ceremony completion
   - `obpi.transitioned.withdrawn` — emitted on `gz obpi withdraw`
   - `obpi.transitioned.superseded` — emitted on `gz obpi supersede`

   **Precondition / witness events** (one per failure-class category from rule 7):

   - `obpi.precondition_check_failed` — predecessor state not satisfied
   - `obpi.witness_required` — transition blocked pending witness
   - `obpi.receipt_emitted` — ARB receipt produced for a transition
   - `obpi.receipt_fabrication_blocked` — receipt rejected by binding rule
   - `obpi.frontmatter_rejected` — hand-edit refused by monitor
   - `obpi.unknown_transition_blocked` — undeclared transition rejected
   - `obpi.cap_blocked` — concurrency-cap rejection (rule 6)

   **Lifecycle / observability events** (decoupled from individual transitions):

   - `obpi.monitor_started` / `obpi.monitor_stopped` — runtime-monitor lifecycle
   - `obpi.reconcile_started` / `obpi.reconcile_completed` — batch reconciliation boundaries
   - `obpi.attestation_walkthrough_started` / `obpi.attestation_walkthrough_completed` — Gate 5 walkthrough boundaries

   Every event has a Pydantic model in `src/gzkit/models/` declaring the
   payload shape; every event consumer (validators, hooks, reporters,
   trace bundles per `ADR-pool.harness-trace-bundles`) imports from
   the canonical vocabulary rather than parsing event-type strings ad hoc.

### Mechanical predicate (binding when promoted)

The runtime monitor (rule 4) routes every state-affecting operation through
a uniform decision:

```
def monitor(operation: GraphOperation) -> Outcome:
    transition = classify(operation)  # → declared transition or None
    if transition is None:
        return reject(FailureClass.monitor_rejected_edit, operation)
    if not transition.preconditions_satisfied(state):
        return reject(FailureClass.precondition_unsatisfied, transition)
    if not transition.witness_satisfied(witness_context):
        return reject(FailureClass.witness_missing, transition)
    if transition.requires_receipt and not arb.receipt_validates(transition.receipt):
        return reject(FailureClass.receipt_fabrication_detected, transition)
    if not concurrency_cap_admits(transition):
        return reject(FailureClass.concurrency_cap_violated, transition)
    emit(transition.event_name, payload=transition.payload)  # from rule 8 vocabulary
    return accept(transition)
```

Every `reject(FailureClass.X, ...)` carries a `RemediationPayload` (ADR-0.0.53)
whose `recovery` field names the canonical resolution path declared in rule 7's
table. The agent reading the failure stream gets the structured next step
without parsing.

### Coupled-surface coherence

- **[ADR-0.0.53](../foundation/ADR-0.0.53-validator-remediation-payload-invariant/)
  (Validator Remediation Payload Invariant, Draft 2026-05-19)** — every
  rule-7 rejection emits a `RemediationPayload`; the failure-class table is
  the rule-citation source for the payload's `rule_citation` field. The
  two doctrines compose: ADR-0.0.53 provides the *shape*, this property
  provides the *enumeration*.
- **[ADR-0.0.24](../foundation/ADR-0.0.24-attestation-receipt-binding/)
  (Attestation Receipt Binding)** — `receipt_fabrication_detected` is the
  failure-class form of ADR-0.0.24's binding rule. The state machine
  surfaces ADR-0.0.24's binding decision into the unified monitor stream.
- **[ADR-pool.harness-trace-bundles](ADR-pool.harness-trace-bundles.md)** —
  trace bundles consume the rule-8 event vocabulary as canonical span
  names. Trace-bundle span types and rule-8 event names share one
  enumeration; drift between them is a coupled-surface coherence defect.
- **[ADR-pool.workflow-specification](ADR-pool.workflow-specification.md)
  § Amendment 2026-05-19** — the JSON workflow spec's `ledger events`
  field consumes rule-8's vocabulary directly. The workflow validator
  fail-closes on any workflow-stage declaring an event not in the
  vocabulary.
- **[ADR-pool.harness-fitness-report](ADR-pool.harness-fitness-report.md)** —
  the fitness report measures rule-7 failure-class hit rates over time
  (which classes fire most; which are zero-hit retirement candidates) and
  rule-8 event emission distribution per transition.
- **[`.gzkit/rules/agent-failure-modes.md`](../../../../.gzkit/rules/agent-failure-modes.md)** —
  agent-behavior failure modes (6-pattern taxonomy). Distinct axis: agent
  behavior vs pipeline state. Rule 7's taxonomy does NOT subsume
  agent-failure-modes; they are orthogonal — an agent in `Skipped cheap
  verification` mode can produce a `receipt_fabrication_detected`
  pipeline-state failure, but the two surfaces fire independently.

### Distinct from Symphony

- **Closed enum, not free-form strings.** Symphony §14 names failure
  classes as documentation; gzkit binds them in `data/obpi_failure_classes.json`
  as a schema-validated closed enum. Adding a class requires an amendment
  ADR; agents cannot rename or invent classes mid-run.
- **Receipt-bound recovery, not retry-loop recovery.** Symphony §14.2
  recovery emphasizes retry/backoff/handoff. gzkit's recovery emphasizes
  *receipt emission* — the recovery action is itself a witnessed state
  transition, not an opaque retry attempt. The doctrines differ because
  the threat models differ (Symphony: keep the daemon running; gzkit:
  preserve audit truth).
- **Event vocabulary as L2 truth, not telemetry.** Symphony §10.4 events
  are observability/telemetry signals flowing upstream from worker to
  orchestrator. gzkit's rule-8 events ARE the ledger — they are the
  canonical L2 facts the system is built around. Symphony's events can
  be dropped without state corruption; gzkit's events being dropped IS
  state corruption.
- **Failure-class is a state-machine concept, not a recovery-strategy concept.**
  Symphony §14.1 enumerates failures and §14.2 enumerates recoveries as
  separate sections. gzkit binds them in one table because the recovery is
  declared *at the failure-class boundary*, not as a separate strategy
  layer — the recovery IS what the runtime monitor does next.

### Inspired By (extended)

[openai/symphony SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md)
**§14 Failure Model and Recovery Strategy** (closed-enum failure classes
with named recovery behaviors) and **§10.4 Emitted Runtime Events**
(closed-enum named event vocabulary emitted upstream). Both mechanisms
generalize cleanly to a state-machined governance harness; the gzkit
adaptations (receipt-bound recovery, L2-truth event semantics) are domain-
specific. The full re-read of Symphony SPEC.md on 2026-05-19 surfaced these
as the two mechanisms gzkit had *implied* in earlier amendments but never
*enumerated*; this amendment closes the enumeration gap so the runtime
monitor (rule 4) has structured truth to consult rather than ad-hoc tables.
