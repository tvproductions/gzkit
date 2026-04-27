---
id: ADR-pool.obpi-state-machine
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.obpi-state-machine: OBPI State Machine and Runtime Invariant Monitor

## Status

Pool

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
- **TTY / `--attestor-present` taxonomy** introduced under GHI #290 and
  GHI #292: agent-relayed-operator-attestation was bolted onto exactly
  one CLI command (`gz obpi complete`) rather than declared as a
  transition guard at every surface where the
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
   ancillary events), and declared witness requirements (TTY-typed
   human, agent-relayed via `--attestor-present`, or self-close per
   Exception-mode rules). The TTY / `--attestor-present` distinction
   becomes a property of the transition, not of one CLI command.

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
