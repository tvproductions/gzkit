---
id: ADR-0.31.0-obpi-state-machine
status: Completed
kind: feature
semver: 0.31.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-07-02
promoted_from: ADR-pool.obpi-state-machine
---

# ADR-0.31.0-obpi-state-machine: OBPI State Machine and Runtime Invariant Monitor

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

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

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Withdrawal is a witnessed transition validated against CANONICAL_TRANSITIONS: a legal predecessor state passes (non-mutating dry-run). | uv run gz obpi withdraw OBPI-0.31.0-01-state-transition-models --reason fidelity-assertion --attestor g0 --dry-run | 0 |
| The witness requirement is transport-agnostic and fail-closed: an empty attestor is rejected with no ledger write (no TTY/PTY, only a human witnesses). | uv run gz obpi withdraw OBPI-0.31.0-01-state-transition-models --reason fidelity-assertion --attestor "" --dry-run | 1 |

<!-- These two assertions exercise the state-machine thesis at the CLI boundary
     (OBPI-02's witnessed withdraw/supersede transitions). OBPI-03's runtime
     monitor refuses undeclared status: drift at the reconcile chokepoint; that
     thesis has no single gz command that exercises a refusal on a healthy tree
     (a refusal requires live drift, and staging drift IS the forbidden
     hand-edit), so its proof is the landing-falsifier regression test
     (REQ-0.31.0-03-03), not a fidelity command. -->


## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 1
- Lineage: 0
- Dimension Total: 4
- Baseline Range: 3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.31.0-01: **state-transition-models** — Closed StrEnum state name-set + Pydantic State/Transition models (preconditions, adjacent-evidence, witness) with schema binding
- [ ] OBPI-0.31.0-02: **withdraw-supersede-transitions** — Elevate withdraw to a monitor-backed first-class transition and build `gz obpi supersede`; both emit canonical transition events; closes GHI #348 root
- [ ] OBPI-0.31.0-03: **runtime-invariant-monitor** — Runtime invariant monitor on the artifact-graph read/write boundary that refuses silent `status:` frontmatter drift (GHI #348 class) in production — the pre-registered landing falsifier

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

## Boundary Invariants

Cross-OBPI fences for the airlock-critical tracer. Each is audited at ADR
closeout, not per-OBPI, and anchors the STRUCTURAL-FENCE REQs in the tracer's
briefs.

1. **Model / monitor / CLI separation (OBPI-01 fence).** The state-machine
   *model layer* — the closed `OBPIState` enum, the `State`/`Transition`
   Pydantic models, and their committed JSON schema — is delivered by OBPI-01
   as pure, additive domain code that imports no runtime-monitor and no
   command surface. The runtime invariant monitor (OBPI-03) and the
   withdraw/supersede CLI verbs (OBPI-02) *consume* this model; the model
   never depends on them. Retiring the legacy `core/lifecycle.py` choreography
   is deferred-in-keel and out of every tracer OBPI's scope.
2. **Transport-agnostic witness (canon fence).** No transition witness value
   in this ADR's realization is a TTY / PTY / interactive-terminal mechanism.
   Human attestation is sacrosanct and transport-agnostic: the witness
   requirement is `human_attested` (a human attests, relayed verbatim via
   `--attestor-present` / `--attestation-text`) vs `self_close`, and the
   mechanism serves the attestation, never gates it (canon-owner directive).
3. **Landing falsifier gates breadth (OBPI-03 fence).** No deferred-in-keel
   OBPI of this ADR (choreography retirement, receipts-ARE-events, concurrency
   caps, failure-class taxonomy, vocab shrink) begins until OBPI-03's monitor
   refuses a silent `status:` frontmatter drift live in production config.

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

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.obpi-state-machine` on 2026-07-02; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.31.0 | Completed | g0 | 2026-07-04 | Completed — "attest completed" (g0). ADR-0.31.0 OBPI state machine keel: 3/3 OBPIs attested (g0); spec-reviewer 18/18 REQs PASS + quality-reviewer COHERENT (one CANONICAL_TRANSITIONS consumed by verbs and monitor); real fidelity gate 2 pass after commit 5c2a07ab replaced the placeholder; 2 closeout corrections landed (fidelity assertions + except narrowing, pinning test); GHI #516 closed (commit 8ba9077f); full suite 6768 pass (arb-step-unittest-9cac4345975143b092404d6415f3eb21), ruff/typecheck/mkdocs strict clean. |
