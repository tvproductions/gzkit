---
id: ADR-pool.obpi-pipeline-dispatch-attestation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
amendments:
  - date: 2026-05-12
    scope: |
      Added Target Scope #6 — Persona-adoption attestation receipts — to absorb
      GHI #459's persona-adoption gap (Stage 2 declares "Active persona:
      pipeline-orchestrator — read .gzkit/personas/pipeline-orchestrator.md
      and adopt its behavioral identity" with no T2 mechanical fail-close).
      Same failure class as existing Target Scope #5 (two-stage review dispatch
      receipts): T1 doctrine, no ledger evidence of compliance, agent narrative
      recall instead of receipts. Mechanism shape parallels #5 — ledger receipt
      (persona_adopted event citing persona file SHA + session anchor) +
      validator scope (gz validate --persona-adoption-receipts) + pre-skill-
      apply gate. Routes GHI #459 gap 2 to this ADR; gap 1 was already
      absorbed by original Target Scope #5. Gaps 3/4/5 of GHI #459 are sibling-
      routed via GHI #458 to ADR-pool.obpi-pipeline-mandate-enforcement;
      no new scope claimed for those. Existing five Target Scope defenses,
      Non-Goals, Decision, Alternatives Considered, and Origin preserved
      verbatim. No new dispatch infrastructure introduced consistent with
      original Non-Goals.
  - date: 2026-05-26
    scope: |
      Recording GHI #517 cross-analyst diagnosis corroboration
      (`artifacts/reports/ghi-517-cross-analyst-reconciliation.md` §
      Pattern A). Four independent analyst pillars cited this pool ADR's
      pending status as a blocker: `gz-obpi-pipeline/SKILL.md:39,431`,
      `gz-adr-closeout-ceremony/SKILL.md:70`, `gz-adr-audit/SKILL.md:43`,
      `gz-adr-evaluate/SKILL.md:67`. The Lead Architect rated P4 (OBPI
      pipeline) as gold-standard with 7×PASS on the rubric; primary-source
      verification (this reconciliation's Dispute D6) revealed P4 is
      3-4 PASS + 3-4 PARTIAL because dispatch attestation is the missing
      Stage-2-runtime piece — exactly what this pool ADR scopes. No new
      Target Scopes added; this amendment elevates the existing scope's
      priority by recording that this pool ADR is the *single* lever that
      lifts P4 D3 from PARTIAL to PASS and unblocks Pattern A across four
      SKILL surfaces. Pattern routing: prose-vs-mechanics + tautological-
      test-surface (GHI #531) per GHI #517 operator tie-break D8.

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

### 6. Persona-adoption attestation receipts

Added 2026-05-12 under GHI #459 routing (see frontmatter `amendments:`).

Skill prose at `.gzkit/skills/gz-obpi-pipeline/SKILL.md` § Persona declares:
*"Active persona: `pipeline-orchestrator` — read
`.gzkit/personas/pipeline-orchestrator.md` and adopt its behavioral identity."*
There is no SessionStart hook that loads the persona, no validator that
checks adoption, and no ledger event recording the persona-file SHA the
agent read. This is the same failure class as Target Scope #5: T1 doctrine
declaring an agent action with no T2 mechanical evidence the action happened.
The orchestrator that ran OBPI-0.0.32-12 Stage 2 with three implementer
dispatches and zero spec-reviewer / quality-reviewer dispatches (the
GHI #459 surfacing run) is the same orchestrator that may or may not have
read the persona file — the ledger cannot answer either question.

Mechanical defense parallels the dispatch-receipt shape:

- `persona_adopted` ledger event with `persona_id`, `persona_file_sha`,
  `session_anchor` (chat session ID + tool-call timestamp), and
  `adoption_evidence` (e.g. the Read tool call that loaded the persona
  file path)
- `gz validate --persona-adoption-receipts` scope: for each active skill
  invocation that declares an active persona, assert a `persona_adopted`
  event exists in the session window with `persona_file_sha` matching the
  declared persona file's current SHA. Exit 3 on gap or SHA mismatch
- Pre-skill-apply gate (where harness cooperation exists): refuse to load
  the skill body until the active persona file has been read into the
  session. Falls back to validator-only enforcement on harnesses without
  PreToolUse cooperation per ADR-0.0.32 § Named exceptions Exception 1

The defense's lower-priority sibling — described in GHI #459's original
fix sketch as "SessionStart hook reads the active skill's persona file
into the session transcript" — is preserved as an alternative form of the
adoption-evidence trigger when full skill-invocation cooperation is
unavailable. Promotion will pick among the three triggers (SessionStart
preload, PreToolUse cooperation, post-hoc validator) based on the
cross-vendor capability matrix.

This defense does not redefine personas, does not introduce new persona
files, and does not change `.gzkit/personas/`'s authoring contract — it
only attests that the agent loaded the persona the skill declared,
binding the T1 declaration to a T2 receipt.

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

### Routed-here (post-authoring amendments)

- **GHI #459** (2026-05-12) — closed `superseded` against this ADR.
  Gaps 1 (Stage 2 two-stage review dispatch) and 2 (persona adoption)
  routed here; gaps 3/4/5 (mandate-enforcement, marker contract,
  PTY-fallback doctrine drift) sibling-routed to
  `ADR-pool.obpi-pipeline-mandate-enforcement` via GHI #458's prior
  close. Gap 1 absorbed by original Target Scope #5; gap 2 absorbed by
  Target Scope #6 added under this amendment.

## Notes

## Re-routing note (post-ADR-0.0.37)

**Added 2026-06-06 (OBPI-0.0.37-10).**

This pool stub's Alternative-C self-rejection read: *"Foundation kind is reserved for
app/system invariants per ADR-0.0.18; these are mechanical defenses *of* an invariant
(ledger-of-truth), not the invariant itself."*

That reasoning was grounded in AGENTS.md § operative-claim-4 as the claimed foundation
invariant — a prose-asserted claim, not a structurally-witnessed one. ADR-0.0.37 ships
**CIC-2** (brief↔reality coherence) as the actual foundation invariant: the dispatch
attestation gap this stub scopes is a feature-shaped defense *of* that foundation
invariant, not a foundation candidate in its own right.

**Consequence for this stub:** Once ADR-0.0.37 is Validated (CIC-2 landed and attested),
this pool stub promotes to a **feature-kind ADR** — a mechanical defense *of* CIC-2's
execution-time dispatch surface. The Alternative-C reasoning is correct in form but was
pointing at the wrong anchor; CIC-2 is the right one.

**Prerequisite for promotion:** ADR-0.0.37 Validated (OBPI-0.0.37-05/06/07/08 attested-complete).

**Reference:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
