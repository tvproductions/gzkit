---
id: ADR-pool.obpi-pipeline-dispatch-attestation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.obpi-pipeline-dispatch-attestation: OBPI Pipeline Subagent Dispatch Attestation

## Status

Pool

## Intent

Close the OBPI pipeline's subagent-dispatch attestation gap. The pipeline
already classifies task complexity, selects a dispatch model, and tracks
re-dispatch counts (`src/gzkit/pipeline_dispatch.py`, ~556 lines covering
`TaskComplexity`, `classify_task_complexity`, `select_dispatch_model`,
`DISPATCH_MODEL_MAP`, `MAX_NEEDS_CONTEXT_RETRIES`, `should_dispatch_review`).
What the pipeline does NOT do is emit ledger events for dispatch decisions or
fail closed when an orchestrator silently abandons a dispatch and edits inline
in the parent context. The result is a runtime where the dispatch contract
exists in code but the operator-visible audit trail does not — the precise
shape `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT names as the failure
class the gate covenant exists to close (operative claim 4: narrative recall
instead of receipts).

GHI #381 surfaced this during OBPI-0.0.23-05 (2026-05-02), where a Haiku-class
orchestrator reported having "bailed to inline editing instead of
re-dispatching, which is exactly what the pipeline's complexity-routing was
supposed to prevent." `grep -E "pipeline_dispatched|pipeline_bailed|pipeline_re_dispatched" .gzkit/ledger.jsonl`
returns empty for the session window — the bypass was invisible to ledger-of-truth.

Note on GHI #381's framing: the body claimed `grep -rn 'model.*floor\|complexity.*rout' src/gzkit/`
returns no implementation and concluded the routing referenced by the
orchestrator's narrative was fabrication. That conclusion was wrong — the
regex was too narrow. The infrastructure exists; what's missing is its
attestation surface and its mechanical gate against the bail-to-inline path.
This ADR scopes the remedy correctly against existing code, not against an
imagined absence.

## Target Scope

Four mechanical defenses, each a candidate `gz`-surface fail-close parallel to
how `gz cli audit` and `gz validate --behave-req-tags` close the
implementation-time class:

### 1. Dispatch receipts as ledger events

Every subagent dispatch (initial and re-dispatch) emits a `pipeline_dispatched`
ledger event naming the OBPI ID, stage, model floor, complexity score, and
turn budget. Bail-to-inline editing is gated on the dispatch receipt being
present and exhausted; without it, the pipeline refuses to continue in the
parent context.

### 2. Mechanical re-dispatch on turn-budget exhaustion

When a dispatched subagent exhausts its turn budget, the pipeline mechanically
re-dispatches a fresh subagent with the partial state attached, rather than
returning control to the parent. Inline editing requires an
`--allow-inline-fallback` flag plus a documented rationale that lands in the
ledger as `pipeline_bailed` with the reason field populated.

### 3. Post-session bail-receipts validator

`gz validate --pipeline-bail-receipts` walks every `pipeline_started` event
and verifies a matching `pipeline_completed` or `pipeline_bailed` event with a
model-floor receipt. Sessions that show implementation activity (`artifact_edited`)
on an OBPI without a corresponding dispatch receipt fail closed.

### 4. Model-floor claims must cite a routing receipt

Any operator-facing summary that names a model floor ("Haiku orchestrating
Opus work") must cite a `pipeline_dispatched` ledger event with the model name
and complexity score. Without the receipt, the claim is fabrication and the
validator flags it. This binds the narrative-recall failure mode to a
mechanical evidence floor.

### 5. Two-stage review dispatch receipts

Superpowers' strongest transfer pattern is not "use more subagents"; it is the
ordered review split: spec-compliance review first, code-quality review second.
gzkit should absorb that through dispatch receipts:

- `pipeline_review_dispatched` event with `review_kind:
  spec_compliance|quality|security|performance`
- spec-compliance review must cite the OBPI brief hash and REQ IDs reviewed
- quality review cannot start until spec-compliance review has passed or emitted
  a blocker envelope
- integration decision cites both review receipts when both are required by lane
  or sensitivity

This prevents review from becoming ritual theater. A fresh reviewer context is
useful only when the output is bound back to the ledger and the integration
decision can prove which review passed.

## Non-Goals

- No new dispatch infrastructure — this ADR scopes attestation and enforcement
  on top of the existing `pipeline_dispatch.py` contract, not a rewrite.
- No model-floor reclassification — `DISPATCH_MODEL_MAP` is the existing
  source of truth and stays. This ADR observes and gates against it; it does
  not redefine it.
- No reviewer prestige hierarchy. Review kinds are evidence roles, not trust in
  a particular model or vendor.
- No bundled close of GHI #380. The authoring-time sibling closes against its
  own destination in a separate ceremony. Each routing-receipt close is
  individual per `ghi-close` doctrine.

## Decision

Pool — design conversation home for the four defenses above. Promotion into a
foundation or feature ADR follows the standard `gz adr promote` ceremony when
the operator sequences this work, with the OBPI decomposition matrix
(`docs/governance/GovZero/obpi-decomposition-matrix.md`) applied per defense.

## Alternatives Considered

### A. Direct fix per defense, no ADR

Rejected. Each defense touches `gz` CLI surface, ledger event schema, and
runtime invariant — three OBPI ceremony triggers per `AGENTS.md` § Defect-fix
routing. A direct-fix path would invert the routing doctrine.

### B. Bundle GHI #380 (authoring-time) and #381 (execution-time) into one ADR

Rejected as a same-session bundling decision. The authoring-time and
execution-time fail-close surfaces share a root cause (anti-vibing operative
claim 4) but have orthogonal mechanical defenses (`gz plan author --check-*`
vs. `gz obpi pipeline --dispatch-receipt`). Either ADR may absorb both
scopes at promotion time; the pool stage does not pre-bind that decision.

### C. Author as foundation-kind ADR-0.0.x directly

Rejected. The defense surface is feature-shaped (new CLI flags, new ledger
event types, new validator scope) rather than invariant-shaped. Foundation
kind is reserved for app/system invariants per ADR-0.0.18; these are
mechanical defenses *of* an invariant (ledger-of-truth), not the invariant
itself.

### D. Withdraw GHI #381 as fabrication

Rejected. The body's grep-claim was wrong, but the underlying observation
(no ledger emission for dispatch, no mechanical gate against bail-to-inline)
is real and reproduces against the current ledger. Premise is intact;
`withdrawn` does not apply.

## Origin

- GHI #381 (execution-time vibes; this ADR's primary surfacing event)
- OBPI-0.0.23-05 implementation session (2026-05-02) — the surfacing run
- Sibling: GHI #380 (authoring-time vibes; closes against its own destination)
- AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 4 (the doctrine root)

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
