---
id: ADR-pool.batched-plan-time-gate-contract
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.batched-plan-time-gate-contract: Batched Plan-Time Gate Contract

## Status

Pool

## Date

2026-05-14

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Close a recurring failure class: gates that are statically evaluable from a
brief and plan fire late (Gate 3–5) and serially, making the artifact path
to Gate-5 closeout expensive. The structural fix is a batched plan-time gate
contract — every gate statically evaluable from the brief+plan alone fires
together at `gz plan audit` time, upstream of any implementation work.

GHI #463 surfaced this as a repeating pattern across the closeout funnel:
late-gate failures are not random noise — they are evaluable-at-plan-time
defects that slipped through because no single point fired all of them at
once. The correct structural response is to move those gates earlier and fire
them atomically, not to add individual gate hardening downstream.

---

## Problem

### Symptoms (GHI #463)

GHI #463 documents a concrete instance: OBPI-0.0.32-15 required ~45–60 minutes
end-to-end, with five cascading single-gate test failures that required a
separate file edit and full test rerun each, across four audit passes:

- `test_help_text_under_80_chars` → fix help text length
- `test_every_event_type_claimed_or_waived` → add waiver in `events.py`
- `test_every_factory_event_has_schema_entry` → add entry in `ledger.json`
- `test_per_flag_doc_waivers_match_real_project_drift` → add flag doc in manpage
- `test_all_schema_events_have_models` → add Pydantic model in `events.py`

Every one of these failures was statically evaluable from the brief and plan
before implementation began. In addition:

- REQ-coverage parity gate fired at Gate 3 (verify), not Gate 2 (tests). The
  `@covers` contract should be authoring-time, not a fifth pass after verify.
- Security canonical-slot gate (GHI #462) fired at Gate 5 (`gz obpi complete`)
  after full implementation and ARB receipts. The deadlock was visible from
  the plan; it should have blocked at `gz plan audit`.
- Behave-waiver gate fired at `gz obpi precomplete`, not at plan-audit, forcing
  a waiver pass after Gate 2 work was already complete.

The pattern in every case: a gate evaluable from brief+plan alone fired late
because no single mechanism batched all static predicates at plan time.

### Root cause

No mechanism exists to run all statically-evaluable gates together at
`gz plan audit` time. The gate covenant defines gates by purpose
(ADR recorded, tests pass, docs updated, BDD, human attestation), not by
*when* they are evaluable. Gates that can be evaluated from static artifacts
are mixed in the same serial pass as gates that require runtime artifacts
(ARB receipts, BDD witnesses). The result is that static failures remain
latent until the gate where they normally fire.

### Failure class (anti-vibing operative claim 3)

Silent doctrine drift: the gate covenant's sequential model was correct when
gates were all runtime-evaluated. As static-evaluable predicates accumulated
(brief scope boundaries, lane/kind assignment, required cross-links, REQ
coverage), the pipeline never extracted them into an early-batch step. The gap
is structural, not individual-gate-shaped.

---

## Target Scope

1. **`plan_time_gates.py` registry module** — explicit registry of every
   `PlanTimeGate` with:
   - `gate_id: str` — stable identifier used in ledger events and error output
   - `evaluator: Callable[[brief, plan_file], GateResult]` — pure function;
     no side effects, no ledger writes; callable idempotently at any stage
   - `description: str` — human-readable gate label shown in `gz plan audit`
     output

2. **`gz plan audit` integration** — iterates the registry and runs every
   evaluator; reports pass/fail/skip per gate; exits non-zero on any failure;
   emits one `plan_audit_batch` ledger event per run with gate-level results
   embedded.

3. **Security gate split** — the current security gate is two wrongly-fused
   predicates with different artifact dependencies:
   - *Structural deadlock detector* (evaluable from brief+plan; no receipts
     required) → moves to `plan_time_gates.py` registry.
   - *Receipt-freshness check* (requires ARB receipts that do not exist at
     plan time) → stays at Gate 5; not a carve-out from the predicate
     mandate but a correct routing of a different gate to its correct artifact
     domain.

4. **Idempotent downstream re-evaluation** — each plan-time gate re-evaluates
   at its original downstream stage as defense-in-depth. Re-evaluation does
   not replace plan-time evaluation; it is additive. A gate that fires at
   plan-time and fails at Gate 4 is a regression, not an expected path.

5. **`gz validate --plan-time-gates` scope** — validates that every
   statically-evaluable gate in the codebase has a registry entry; exits
   non-zero on unregistered static evaluators, preventing silent re-
   accumulation of the failure class this ADR closes. *Derivation:* registry
   completeness enforcement is a mechanical corollary of D3 (explicit registry
   is the source of truth); without a validator, the registry can drift the
   same way the implicit inline-condition model did. Surfaced here as a
   concrete Target Scope item for operator visibility; if the operator prefers
   to defer this to promotion, remove item 5 and note it as a promotion
   obligation in the Decision section.

---

## Non-Goals

- No change to gates that are not statically evaluable from brief+plan alone
  (ARB receipt presence, BDD witness, human attestation — these stay where
  they are).
- No replacement of the downstream gate covenant; downstream gates remain and
  re-evaluate for defense-in-depth.
- No ledger-event-contract consistency work. That is a separate concern
  cross-linked below (ADR-pool.ledger-event-contract-consistency, to be
  authored).
- No OBPI decomposition at pool stage. OBPIs begin after promotion.

---

## Decision

### D1 — Routing

Separate new pool ADR (not merged into `ADR-pool.focused-context-loader` or
`ADR-pool.obpi-pipeline-dispatch-attestation`). Cross-links to both as
adjacent scopes. Rationale: this ADR addresses the plan-audit surface and
the gate-predicate registry, which is orthogonal to context loading and
dispatch attestation. Bundling would conflate gate-evaluation-timing with
context-load strategy and attestation evidence, making each harder to scope
and promote.

### D2 — Predicate mandate (binds absolutely, no carve-outs)

Every gate statically evaluable from brief+plan alone fires at `gz plan audit`
time. The predicate is structural, not gate-by-gate: if an evaluator can
return a deterministic result from brief+plan without runtime artifacts, it
belongs in the plan-time registry. Re-evaluation downstream is required as
defense-in-depth — not optional, not a carve-out.

The security gate split (Target Scope #3) is the operationalization of this
mandate, not an exception to it: two wrongly-fused predicates with different
artifact domains are routed to their correct domains. The structural-deadlock
half satisfies the evaluability predicate and moves to plan-time; the
receipt-freshness half does not satisfy it and stays at Gate 5.

### D3 — Mechanism: explicit registry module (Option C)

A `plan_time_gates.py` module is the canonical registry. Every `PlanTimeGate`
is a first-class data object (not a special-case branch in the audit runner).
Adding a plan-time gate = adding a registry entry + an evaluator function.
The `gz plan audit` runner is a thin iterator over the registry; it does not
contain gate-specific logic.

*Options A and B considered and rejected:*

**A — Inline conditions in `gz plan audit`**: rejected because each new
evaluable gate adds a branch to the audit runner, making the runner the de
facto registry (untestable as a registry, no structured gate-level ledger
output, accumulation of special-case logic is the exact failure class this ADR
closes).

**B — Gating via existing `gz validate` scopes**: rejected because `gz validate`
scopes are post-implementation checks; calling them at plan-time conflates
authoring-time validation with execution-time validation and inverts the
dependency direction (plan-time check would import a runtime surface).

### D4 — Ledger-event-contract consistency

Cross-linked out to a sibling pool ADR (`ADR-pool.ledger-event-contract-consistency`).
Not in scope for this ADR. The `plan_audit_batch` event emitted by Target
Scope #2 must conform to whatever schema that ADR establishes; the
conformance requirement is noted here and enforced at that ADR's promotion
boundary.

---

## Consequences and Risks

### Positive

- Plan-time gate batch catches static failures before any implementation work
  begins; eliminates the multi-cycle correction overhead GHI #463 documents.
- Registry module is the single source of plan-time gate truth; `gz validate
  --plan-time-gates` prevents silent re-accumulation.
- Idempotent downstream re-evaluation means promotion to heavy-lane or
  foundation-kind does not require new gate infrastructure — it inherits the
  same evaluators, now running at two points.
- Security gate split resolves a latent confusion between structural and
  receipt-freshness predicates that has caused mis-routing in prior
  implementation sessions.

### Risks

- **Registry staleness**: evaluators can drift from the gates they claim to
  check. Mitigation: `gz validate --plan-time-gates` enforces registry
  completeness; test coverage on each evaluator is a REQ-coverage obligation
  at OBPI time.
- **Evaluator purity**: an evaluator that writes ledger events or has side
  effects breaks idempotent re-evaluation. Mitigation: evaluator signature
  `Callable[[brief, plan_file], GateResult]` is typed; any I/O attempt in an
  evaluator is a type error.
- **Ledger-event-schema coupling**: `plan_audit_batch` event shape must align
  with the forthcoming `ADR-pool.ledger-event-contract-consistency` schema.
  If that ADR's schema is incompatible with this ADR's emitted shape,
  promotion of either ADR requires a coordinated schema update. Risk surface:
  medium; mitigation is the cross-link and explicit promotion boundary noted
  in D4.
- **Lane assignment**: this ADR is currently `lite` (no CLI surface change at
  pool stage). At promotion, if `gz plan audit` gains new flags or new ledger
  event types become externally contracted, lane must be upgraded to `heavy`
  per the gate covenant. The lane decision is re-evaluated at promotion, not
  fixed here.

---

## Alternatives Considered

### A. Harden individual gates downstream serially

Rejected as treating the symptom, not the failure class. Adding per-gate
hardening at Gate 3–5 does not change the serial, late-firing structure
that GHI #463 identifies. Each new gate requires its own ceremonial pass;
the cost-per-gate-failure remains constant rather than collapsing to zero via
early-batch detection.

### B. Merge into `ADR-pool.obpi-pipeline-dispatch-attestation`

Rejected (D1). Dispatch attestation is about ledger evidence for dispatch
decisions at execution time; plan-time gate batching is about evaluating
static predicates before implementation begins. They share a root concern
(making vibing structurally inert) but have orthogonal mechanical defenses
and different artifact domains.

### C. Merge into `ADR-pool.focused-context-loader`

Rejected (D1). Context loading optimizes agent token economy at session start;
plan-time gate batching optimizes gate-failure cost at plan close. The only
shared surface is `gz plan audit`; sharing that command entry point is
insufficient coupling to warrant bundling two orthogonal architectural
decisions.

### D. Implicit gate discovery via decorator scan

An alternative to the explicit registry: scan for `@plan_time_gate` decorators
at import time and build the registry dynamically. Rejected because dynamic
discovery at import time is fragile to import order, makes the gate list
non-enumerable without running the scanner, and produces an implicit registry
(the exact failure mode D3 closes). Explicit beats implicit here.

---

## Origin

- GHI #463 (batched plan-time gate contract; this ADR's primary surfacing event)
- Design dialogue 2026-05-14 (decisions D1–D4 booked in session)
- AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 3 (doctrine-drift
  root cause)

---

## Adjacent Pool ADRs (cross-links)

- [`ADR-pool.focused-context-loader`](ADR-pool.focused-context-loader.md) —
  sibling: focused context delivery at session start; orthogonal to gate
  timing but both address plan-audit efficiency
- [`ADR-pool.obpi-pipeline-dispatch-attestation`](ADR-pool.obpi-pipeline-dispatch-attestation.md) —
  sibling: execution-time dispatch attestation; shares anti-vibing root
  concern, different artifact domain
- `ADR-pool.ledger-event-contract-consistency` (to be authored) — sibling:
  ledger event schema contract; `plan_audit_batch` event shape depends on
  that schema; D4 cross-link

---

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

At promotion, re-evaluate lane assignment: if `gz plan audit` CLI surface is
externally contracted (new flags, new output schema), upgrade to `heavy`.
