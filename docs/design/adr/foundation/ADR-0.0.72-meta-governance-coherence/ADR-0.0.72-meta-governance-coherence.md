---
id: ADR-0.0.72-meta-governance-coherence
status: Draft
kind: foundation
semver: 0.0.72
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-06-13
---

# ADR-0.0.72-meta-governance-coherence: Meta-Governance Validator Round-Trip Coherence

> **⚠️ COLLAPSED 2026-06-13 → PARTIALLY REVERSED 2026-07-13 (operator-ratified, g0).**
>
> **2026-06-13 collapse (preserved as history):** this foundation ADR was
> collapsed as over-construction. Its PORT (OBPI-01,
> `gz validate --writer-model-roundtrip`, an always-on meta-validator) was proven
> by a 2026-06-13 pipeline run to be the disease, not the cure: landing it tripped
> four *more* incoherences it does not address (brief-reconcile, InsightRecord,
> plan-audit, lock-release coupling) — you cannot audit your way out of
> over-auditing. C1–C4 were re-routed to GHIs (**#612** closed via OBPI-02;
> **#575** open — InsightRecord ↔ Behavior Rule 11 drift; **#581** open —
> brief-reconcile crudeness) and the architectural remedy sent to the Config-first
> SSOT workstream (coherence by *construction*, never another validator).
>
> **2026-07-13 partial reversal (Foundation Sunset prerequisite, operator-ratified):**
> the Foundation Sunset (ADR-0.34.0) requires this ADR terminal. This is a
> **re-scope, NOT a wholesale un-collapse**: OBPI-01's **global** meta-validator
> stays **withdrawn** (`gz obpi withdraw` — the 2026-06-13 hydra finding stands);
> its coherence intent is re-homed to **localized per-writer round-trip tests**
> inside the adapters (construction-coherence at the point-fix, no fifth global
> gate). The two adapters that close live defects are **built**: **OBPI-03**
> (InsightRecord append helper + Rule-11 prose reconcile, closes C4 / GHI #575) and
> **OBPI-04** (`security_floor_overridden` event, closes the override-audit hole).
> **OBPI-02** (HandoffFrontmatter) was already complete. Terminal set: 02+03+04
> (01 excluded via withdraw). The original ADR text below is preserved as authored;
> Decision item #1 and Checklist item #1 carry inline WITHDRAWN annotations.

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
The operative stance for this ADR: **the machinery that audits everything must
itself be audited against the same standard it imposes**. gzkit asks every
governance artifact to validate against its own contract; an authoring model
that rejects what its own writers produce or its own consumers require is the
harness failing its own test. The work here is not adding a feature — it is
restoring the machinery's right to be trusted by making its validators
coherent with each other, fail-closed, and exhaustively covered.

## Why foundation tier?

Without this ADR, gzkit still has gates that catch agent vibing — but the gates
that validate governance *artifacts* contradict each other (an authoring model
rejecting the exact shape its consumer requires), and the contradictions are
invisible because the strict side is un-gated. A harness whose reason to exist
is making stochastic drift structurally inert, yet whose own validators are
silently drifted from one another, is not the harness it claims to be. Closing
that inverse — the machinery must be self-coherent — is identity-shaping, so the
invariance test resolves **yes**.

Port-vs-adapter: this ADR is a **port**. "Every governance-artifact writer's
output MUST validate against that artifact's own authoring model, and that model
MUST accept everything its consumers require" is the abstract contract; the
`gz validate --writer-model-roundtrip` validator and the
HandoffFrontmatter/InsightRecord/security-floor adapters are its first
implementations. Future meta-governance surfaces inherit the same port.

## Intent

gzkit's governance machinery validates governance artifacts (handoffs, insights, ledger receipts, briefs) through TWO surfaces authored at different times: an authoring-time Pydantic model (what the artifact MAY contain) and a consuming-time lookup or validator (what a downstream gate REQUIRES). A census run during the OBPI-0.0.71-01 pipeline found these surfaces were authored in separate OBPIs/GHIs without the DO IT RIGHT §1a coupled-surface-coherence check, producing a CLASS of mutual contradictions in which an authoring model rejects the exact shape its own consumer requires. Four are confirmed with file:line citations on both sides: (C1) `HandoffFrontmatter` (extra=forbid, src/gzkit/handoff_validation.py:90) rejects the `last_lock_event_timestamp`/`last_commit_sha` fields that `validate_lock_handoff_coupling` REQUIRES (src/gzkit/governance/trust_audits/lock_handoff_coupling.py:170-171); (C2) the same model rejects the frontmatter its OWN module's `write_degenerate_handoff`/`_write_reaping_handoff` writers emit (handoff_validation.py:434-446, lock_manager.py:231-245); (C3) the model's `obpi_id` regex `^OBPI-\d+\.\d+\.\d+-\d{2}$` (short-form only, :61) contradicts both the canonical `obpi.json` id pattern (slug-bearing, schemas/obpi.json:16) and `find_handoff_for_release`'s exact-match lookup against the slug-bearing id the release command threads in (:513); (C4) `InsightRecord` requires `ts`/`type` and `evidence: list[str]` (insights/model.py:32-49) while AGENTS.md Behavior Rule 11 instructs agents to write `scope`/`summary`/`evidence`/`next_action` with scalar-or-list evidence (AGENTS.md:138). An ENFORCEMENT ASYMMETRY hid every break: the consuming validators are fail-closed and gated in `gz check`, while the authoring models are un-gated (`validate_handoff_document` is wired to no gate; the insights contract is prose). So the contradictions sit dormant until a full heavy-lane pipeline run actually exercises the rarely-run meta-governance surfaces — which is exactly what tripped C1 and C3 (handoff release, twice) and C4 (insight append) in a single session. The census also found that `gz obpi complete --accept-security-floor` overrides emit NO first-class ledger event (`security_floor_overridden`: 0 lifetime), so an operator override of a completion-state-editing gate is invisible to ledger audit. The same census established the surrounding picture so this ADR is correctly scoped: the 509-waiver pile is ~99% legitimate (one historical grandfather + structural exemptions), so waivers are NOT the defect; the real signals are this validator-coherence class, a continuous 67% brief-reconcile drift rate, and the security-override audit hole. Foundation tier — the invariance test resolves yes: gzkit IS the harness whose reason to exist is making stochastic vibing structurally inert via governance gates. When the gates that validate governance artifacts contradict each other, the harness cannot trust its own machinery — the validators meant to catch drift are themselves drifted, and the drift is invisible precisely because the strict side is toothless. Restoring self-coherence to the machinery is identity-shaping, not feature work. Port-vs-adapter: 'every governance-artifact writer's output MUST validate against that artifact's own authoring model' is the PORT (abstract invariant); the HandoffFrontmatter/InsightRecord reconciliations and the security-floor ledger event are its first ADAPTERS.

## Decision

> **Re-scoped 2026-07-13 (operator-ratified — see reversal note at top).** The
> original four-item decision is preserved below with inline annotations: item #1
> (the global PORT validator) is **WITHDRAWN**, and items #3/#4 realize their
> coherence check as **localized per-writer round-trip tests** rather than through
> that global validator. The invariant itself stands — only its enforcement moves
> from one global gate to point-fix tests.

Establish meta-governance self-coherence as a foundation-attested invariant with a structural validator (the PORT) and reconcile the confirmed instances (the ADAPTERS), decomposed into four OBPIs 1:1 with the Feature Checklist.

**The invariant (canonical statement):** Every registered governance-artifact writer's emitted output MUST validate cleanly against that artifact's own authoring model, and that authoring model MUST accept everything its downstream consumers require. An authoring model that rejects what its writers produce or its consumers require is a fail-closed defect.

**Decision items (1:1 with Feature Checklist):**

1. **PORT — `gz validate --writer-model-roundtrip` coherence validator.** **[WITHDRAWN 2026-07-13 — the global always-on meta-validator stays withdrawn per the 2026-06-13 hydra evidence; its coherence intent is re-homed to localized per-writer round-trip tests in OBPI-03/04.]** A new validate scope with an explicit registry of meta-governance artifact writers (handoff writers, the insight append path, ledger-event factories, brief authoring). For each, it round-trips the writer's ACTUAL emitted output (captured from a real emission or a golden fixture derived from the writer, never a hand-built happy-path stub) back through that artifact's own authoring model, and fails closed (exit 3) on any divergence. An exhaustiveness test asserts every `*_handoff`/`*_event`/`*_record` writer in the meta-governance layer is registered, so a new writer cannot silently escape the round-trip. Wired into the `gz check` default bundle. This is the structural catcher for the entire C1–C4 class and any future sibling.

2. **ADAPTER — reconcile `HandoffFrontmatter` to its writers and consumers (closes C1/C2/C3).** Widen `obpi_id` to the canonical `obpi.json` pattern (slug-optional). Replace the bare `extra=forbid` with an EXPLICIT SUPERSET model that declares every field the module actually writes — the min-info fields (`last_lock_event_timestamp`, `last_commit_sha`, `branch`) and the degenerate/reaping fields (`abandoned`, `category`, `abandoned_by`, `abandoned_at`, `previous_agent`, `reason`) — so typo-defense is preserved (unknown keys still fail) while legitimate fields pass. Wire `validate_handoff_document` into a gate so the model can no longer drift un-noticed. Acceptance: the reconciled model round-trips clean against `write_degenerate_handoff`, `_write_reaping_handoff`, and a normal-release handoff, and a slug-bearing `obpi_id` both validates and exact-matches `find_handoff_for_release`.

3. **ADAPTER — reconcile `InsightRecord` ↔ authoring contract (closes C4; closes GHI #575).** Provide an `InsightRecord`-backed append helper (a mechanical writer) so the authoring path cannot drift from the model, and expose it as the governed `gz insights remember` CLI verb (mirroring `gz content remember`) — the `gz <verb>` surface agents invoke, closing GHI #575's hand-append-only gap. AND align the AGENTS.md Behavior Rule 11 (now directing agents to `gz insights remember`) + agent-contract-rationale 'required fields' prose with the model envelope (add `ts`/`type`; specify `evidence` as a list). Acceptance: an append produced via `gz insights remember` round-trips clean via a localized round-trip test (the helper's real emitted output re-validated against `InsightRecord` directly, never a happy-path stub), and the AGENTS.md prose names exactly the model's required fields and points at the verb.

4. **ADAPTER — `security_floor_overridden` ledger event.** New Pydantic event model + factory + `ledger.json` schema entry, emitted whenever `gz obpi complete --accept-security-floor` fires, recording `obpi_id`, overridden surface(s), `reason`, `attestor`, and `ts`. Makes overrides of a completion-state-editing gate auditable via ledger census, closing the hole the OBPI-0.0.71-01 override exposed. Acceptance: emitting the event then running the census surfaces the override; the event round-trips clean through the existing `_EVENT_MODELS` model↔schema alignment (localized writer-model coherence).

**Sequencing (revised 2026-07-13):** OBPI-01 (the global port/validator) is WITHDRAWN — see reversal note. OBPI-02 is complete. OBPI-03 and -04 (the adapters) land independently, each carrying its OWN localized round-trip test (the writer's real emitted output re-validated against its authoring model); there is no global gate to wire into `gz check`. Terminal set is 02+03+04.

**Lane: Heavy.** New `gz validate` scope (CLI/contract), schema + ledger-event change, and a gated authoring model all trigger heavy-lane rigor. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.36.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT remediate the 67% brief↔code reconcile drift rate — a diagnostic finding that needs its own investigation ADR; this ADR is the validator-coherence class, not the drift class.
- Does NOT fix the single `adr-0.0.33-05` behave capitulation — a separable direct-fix (the only genuine capitulation in 509 waivers), routed independently.
- Does NOT rewrite the lock/handoff state machine — it reconciles the frontmatter model to the existing writers/consumers, additively.
- Does NOT drop `extra=forbid` wholesale — it replaces it with an explicit superset to preserve typo-defense.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Re-scoped (2026-07-13): the coherence thesis is realized as localized writer-model checks, not a global validator. The insights writer surface (OBPI-03's `InsightRecord` adapter target, closing C4/GHI #575) is shape-coherent against its own authoring model. | uv run gz validate --insights-shape | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.72-meta-governance-coherence --check | 0 |

## Consequences

### Positive

1. **The C1–C4 contradiction class gains a structural catcher.** The round-trip validator fails closed on any writer-model divergence, so the next HandoffFrontmatter-class defect is caught at `gz check` time, not at pipeline-trip time. This is the fix-the-class remedy (DO IT RIGHT §1), not instance-patching.

2. **The enforcement asymmetry that hid every break is closed.** Authoring models become gated (the round-trip validator runs them against real writer output), so a model can no longer be 'authored wrong but toothless' and sit dormant until a full pipeline run trips it.

3. **Lock release stops being a latent coin-flip.** With `HandoffFrontmatter` accepting the canonical slug `obpi_id` plus the min-info/degenerate fields, a valid handoff actually unblocks release and the coupling validator simultaneously — C1/C2/C3 closed in one reconciliation.

4. **Insight appends stop failing closed.** The mechanical append helper means agents can't hand-author drift; the AGENTS.md prose finally names the model's real fields — C4 closed at the authoring source.

5. **Security-floor overrides become auditable.** A first-class ledger event means `gz` census surfaces can count and trace overrides of completion-state edits — closing the invisible-override hole the OBPI-0.0.71-01 override exposed.

6. **The remedy generalizes.** The validator's writer-registry + exhaustiveness test means future meta-governance surfaces (new event types, new artifact writers) are forced into round-trip coverage, so the class cannot silently regrow.

### Negative

1. **The round-trip validator could become performative.** Pre-mortem: 18 months out, the validator passes green while a new writer drifts because its registered 'representative output' was a happy-path stub that never exercised the divergent field. Mitigation: the validator MUST round-trip the writer's ACTUAL emitted output (captured from a real emission or a golden fixture derived from the writer), never a hand-built sample; and the exhaustiveness test asserts every meta-governance writer is registered, so coverage can't quietly shrink.

2. **Replacing `extra=forbid` risks losing typo-defense.** Pre-mortem: a reconciliation that simply drops `extra=forbid` lets a misspelled field pass silently, trading one drift class for another. Mitigation: the decision is explicit — replace with a SUPERSET model that declares every real field, so unknown keys still fail while legitimate fields pass. Dropping the guard is named as the rejected path.

3. **`security_floor_overridden` is a schema/event change (heavy).** Mitigation: additive event type following the exact pattern of `obpi_completion_repudiated`, which just landed under ADR-0.0.71 — a proven, low-risk shape.

4. **One-way door at the validator level.** Once `gz check` gates on round-trip coherence, every meta-governance writer must forever round-trip clean. Reversal in 12 months would require an ADR amendment. Justified: that is precisely the invariant we want; the asymmetry is intentional, because the cost of leaving the door open is the dormant-contradiction class this ADR closes.

5. **Risk of mis-targeting if the real problem were authoring discipline, not model coherence.** Mitigation: the census cited 4 confirmed contradictions with file:line on BOTH sides — the defect is structural (the model and its consumer cannot both be satisfied), not a narration problem. An authoring-discipline fix alone would leave the model still rejecting its own writers.

6. **The 67% brief-drift signal is deferred and could read as ignoring the bigger number.** Mitigation: explicitly scoped out as needing its own investigation ADR. Brief↔code drift is a different coupling (artifact-vs-code) from validator self-coherence (model-vs-its-own-consumer); folding them would produce an incoherent ADR. The deferral is named, not silent.

7. **The 2am operator scenario.** An operator override (`--accept-security-floor`) now also emits a ledger event; if the emission path failed, could it block completion? Mitigation: the event emission is additive and best-effort-after-completion in the same transaction as the existing receipt; a failed emission is a defect to fix, never a new gate on the override itself — the override remains operator-sovereign.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 0
- Dimension Total: 5
- Baseline Range: 3
- Baseline Selected: 3
<!-- Re-scored 2026-07-13: OBPI-01 (the PORT) withdrawn per the reversal note; the port↔adapter surface-boundary split collapses (the 3 survivors 02/03/04 are all adapters), so Split Surface Boundary 1→0, Split Total 1→0, Final 4→3. Active target now equals the 3 non-withdrawn OBPIs. -->
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] PORT: `gz validate --writer-model-roundtrip` coherence validator [withdrawn; the global always-on meta-validator per the 2026-06-13 hydra evidence (landing it tripped four more incoherences it does not address); coherence intent re-homed to localized per-writer round-trip tests in OBPI-03/04; excluded from the terminal partition; `obpi_withdrawn` 2026-07-13, operator-ratified]
- [ ] ADAPTER (C1/C2/C3): reconcile `HandoffFrontmatter` — widen `obpi_id` to the canonical `obpi.json` slug-optional pattern; replace bare `extra=forbid` with an explicit SUPERSET model declaring the min-info fields (last_lock_event_timestamp, last_commit_sha, branch) and degenerate/reaping fields (abandoned, category, abandoned_by, abandoned_at, previous_agent, reason); wire `validate_handoff_document` into a gate; verify the model round-trips clean against write_degenerate_handoff, _write_reaping_handoff, a normal-release handoff, and that a slug-bearing obpi_id both validates and exact-matches find_handoff_for_release.
- [ ] ADAPTER (C4): reconcile `InsightRecord` ↔ authoring contract — provide an InsightRecord-backed append helper (mechanical writer) and expose it as the governed `gz insights remember` CLI verb (mirrors `gz content remember`, closes GHI #575); align AGENTS.md Behavior Rule 11 (now pointing at `gz insights remember`) + agent-contract-rationale 'required fields' prose with the model envelope (add ts/type; evidence as list[str]); verify a helper-produced append round-trips clean via a localized round-trip test (real emitted output re-validated against InsightRecord).
- [ ] ADAPTER: `security_floor_overridden` ledger event — Pydantic event model + factory + ledger.json schema entry; emitted from `gz obpi complete --accept-security-floor` recording obpi_id, overridden surface(s), reason, attestor, ts; unit tests; round-trips clean through the existing `_EVENT_MODELS` model↔schema alignment; census query surfaces the override.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-06-13T02:53:10.737141*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.72-meta-governance-coherence

### Q: What is the title of this ADR?

**A:** Meta-Governance Validator Round-Trip Coherence

### Q: What is the semantic version?

**A:** 0.0.72

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's governance machinery validates governance artifacts (handoffs, insights, ledger receipts, briefs) through TWO surfaces authored at different times: an authoring-time Pydantic model (what the artifact MAY contain) and a consuming-time lookup or validator (what a downstream gate REQUIRES). A census run during the OBPI-0.0.71-01 pipeline found these surfaces were authored in separate OBPIs/GHIs without the DO IT RIGHT §1a coupled-surface-coherence check, producing a CLASS of mutual contradictions in which an authoring model rejects the exact shape its own consumer requires. Four are confirmed with file:line citations on both sides: (C1) `HandoffFrontmatter` (extra=forbid, src/gzkit/handoff_validation.py:90) rejects the `last_lock_event_timestamp`/`last_commit_sha` fields that `validate_lock_handoff_coupling` REQUIRES (src/gzkit/governance/trust_audits/lock_handoff_coupling.py:170-171); (C2) the same model rejects the frontmatter its OWN module's `write_degenerate_handoff`/`_write_reaping_handoff` writers emit (handoff_validation.py:434-446, lock_manager.py:231-245); (C3) the model's `obpi_id` regex `^OBPI-\d+\.\d+\.\d+-\d{2}$` (short-form only, :61) contradicts both the canonical `obpi.json` id pattern (slug-bearing, schemas/obpi.json:16) and `find_handoff_for_release`'s exact-match lookup against the slug-bearing id the release command threads in (:513); (C4) `InsightRecord` requires `ts`/`type` and `evidence: list[str]` (insights/model.py:32-49) while AGENTS.md Behavior Rule 11 instructs agents to write `scope`/`summary`/`evidence`/`next_action` with scalar-or-list evidence (AGENTS.md:138). An ENFORCEMENT ASYMMETRY hid every break: the consuming validators are fail-closed and gated in `gz check`, while the authoring models are un-gated (`validate_handoff_document` is wired to no gate; the insights contract is prose). So the contradictions sit dormant until a full heavy-lane pipeline run actually exercises the rarely-run meta-governance surfaces — which is exactly what tripped C1 and C3 (handoff release, twice) and C4 (insight append) in a single session. The census also found that `gz obpi complete --accept-security-floor` overrides emit NO first-class ledger event (`security_floor_overridden`: 0 lifetime), so an operator override of a completion-state-editing gate is invisible to ledger audit. The same census established the surrounding picture so this ADR is correctly scoped: the 509-waiver pile is ~99% legitimate (one historical grandfather + structural exemptions), so waivers are NOT the defect; the real signals are this validator-coherence class, a continuous 67% brief-reconcile drift rate, and the security-override audit hole. Foundation tier — the invariance test resolves yes: gzkit IS the harness whose reason to exist is making stochastic vibing structurally inert via governance gates. When the gates that validate governance artifacts contradict each other, the harness cannot trust its own machinery — the validators meant to catch drift are themselves drifted, and the drift is invisible precisely because the strict side is toothless. Restoring self-coherence to the machinery is identity-shaping, not feature work. Port-vs-adapter: 'every governance-artifact writer's output MUST validate against that artifact's own authoring model' is the PORT (abstract invariant); the HandoffFrontmatter/InsightRecord reconciliations and the security-floor ledger event are its first ADAPTERS.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Establish meta-governance self-coherence as a foundation-attested invariant with a structural validator (the PORT) and reconcile the confirmed instances (the ADAPTERS), decomposed into four OBPIs 1:1 with the Feature Checklist.

**The invariant (canonical statement):** Every registered governance-artifact writer's emitted output MUST validate cleanly against that artifact's own authoring model, and that authoring model MUST accept everything its downstream consumers require. An authoring model that rejects what its writers produce or its consumers require is a fail-closed defect.

**Decision items (1:1 with Feature Checklist):**

1. **PORT — `gz validate --writer-model-roundtrip` coherence validator.** A new validate scope with an explicit registry of meta-governance artifact writers (handoff writers, the insight append path, ledger-event factories, brief authoring). For each, it round-trips the writer's ACTUAL emitted output (captured from a real emission or a golden fixture derived from the writer, never a hand-built happy-path stub) back through that artifact's own authoring model, and fails closed (exit 3) on any divergence. An exhaustiveness test asserts every `*_handoff`/`*_event`/`*_record` writer in the meta-governance layer is registered, so a new writer cannot silently escape the round-trip. Wired into the `gz check` default bundle. This is the structural catcher for the entire C1–C4 class and any future sibling.

2. **ADAPTER — reconcile `HandoffFrontmatter` to its writers and consumers (closes C1/C2/C3).** Widen `obpi_id` to the canonical `obpi.json` pattern (slug-optional). Replace the bare `extra=forbid` with an EXPLICIT SUPERSET model that declares every field the module actually writes — the min-info fields (`last_lock_event_timestamp`, `last_commit_sha`, `branch`) and the degenerate/reaping fields (`abandoned`, `category`, `abandoned_by`, `abandoned_at`, `previous_agent`, `reason`) — so typo-defense is preserved (unknown keys still fail) while legitimate fields pass. Wire `validate_handoff_document` into a gate so the model can no longer drift un-noticed. Acceptance: the reconciled model round-trips clean against `write_degenerate_handoff`, `_write_reaping_handoff`, and a normal-release handoff, and a slug-bearing `obpi_id` both validates and exact-matches `find_handoff_for_release`.

3. **ADAPTER — reconcile `InsightRecord` ↔ authoring contract (closes C4).** Provide an `InsightRecord`-backed append helper (a mechanical writer) so the authoring path cannot drift from the model, AND align the AGENTS.md Behavior Rule 11 + agent-contract-rationale 'required fields' prose with the model envelope (add `ts`/`type`; specify `evidence` as a list). Acceptance: an append produced by the helper round-trips clean through the new validator, and the AGENTS.md prose names exactly the model's required fields.

4. **ADAPTER — `security_floor_overridden` ledger event.** New Pydantic event model + factory + `ledger.json` schema entry, emitted whenever `gz obpi complete --accept-security-floor` fires, recording `obpi_id`, overridden surface(s), `reason`, `attestor`, and `ts`. Makes overrides of a completion-state-editing gate auditable via ledger census, closing the hole the OBPI-0.0.71-01 override exposed. Acceptance: emitting the event then running the census surfaces the override; the event round-trips clean through OBPI-01's validator.

**Sequencing:** OBPI-02, -03, -04 (the adapters) can land in parallel — independent surfaces. OBPI-01 (the port/validator) depends on the adapters existing as its first registered round-trip targets, OR lands first as a failing-then-green gate that the adapters satisfy; either ordering is acceptable provided the adapters round-trip clean before OBPI-01 is wired into `gz check`.

**Lane: Heavy.** New `gz validate` scope (CLI/contract), schema + ledger-event change, and a gated authoring model all trigger heavy-lane rigor. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.36.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT remediate the 67% brief↔code reconcile drift rate — a diagnostic finding that needs its own investigation ADR; this ADR is the validator-coherence class, not the drift class.
- Does NOT fix the single `adr-0.0.33-05` behave capitulation — a separable direct-fix (the only genuine capitulation in 509 waivers), routed independently.
- Does NOT rewrite the lock/handoff state machine — it reconciles the frontmatter model to the existing writers/consumers, additively.
- Does NOT drop `extra=forbid` wholesale — it replaces it with an explicit superset to preserve typo-defense.

### Q: What good things result from this decision? List benefits.

**A:** 1. **The C1–C4 contradiction class gains a structural catcher.** The round-trip validator fails closed on any writer-model divergence, so the next HandoffFrontmatter-class defect is caught at `gz check` time, not at pipeline-trip time. This is the fix-the-class remedy (DO IT RIGHT §1), not instance-patching.

2. **The enforcement asymmetry that hid every break is closed.** Authoring models become gated (the round-trip validator runs them against real writer output), so a model can no longer be 'authored wrong but toothless' and sit dormant until a full pipeline run trips it.

3. **Lock release stops being a latent coin-flip.** With `HandoffFrontmatter` accepting the canonical slug `obpi_id` plus the min-info/degenerate fields, a valid handoff actually unblocks release and the coupling validator simultaneously — C1/C2/C3 closed in one reconciliation.

4. **Insight appends stop failing closed.** The mechanical append helper means agents can't hand-author drift; the AGENTS.md prose finally names the model's real fields — C4 closed at the authoring source.

5. **Security-floor overrides become auditable.** A first-class ledger event means `gz` census surfaces can count and trace overrides of completion-state edits — closing the invisible-override hole the OBPI-0.0.71-01 override exposed.

6. **The remedy generalizes.** The validator's writer-registry + exhaustiveness test means future meta-governance surfaces (new event types, new artifact writers) are forced into round-trip coverage, so the class cannot silently regrow.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **The round-trip validator could become performative.** Pre-mortem: 18 months out, the validator passes green while a new writer drifts because its registered 'representative output' was a happy-path stub that never exercised the divergent field. Mitigation: the validator MUST round-trip the writer's ACTUAL emitted output (captured from a real emission or a golden fixture derived from the writer), never a hand-built sample; and the exhaustiveness test asserts every meta-governance writer is registered, so coverage can't quietly shrink.

2. **Replacing `extra=forbid` risks losing typo-defense.** Pre-mortem: a reconciliation that simply drops `extra=forbid` lets a misspelled field pass silently, trading one drift class for another. Mitigation: the decision is explicit — replace with a SUPERSET model that declares every real field, so unknown keys still fail while legitimate fields pass. Dropping the guard is named as the rejected path.

3. **`security_floor_overridden` is a schema/event change (heavy).** Mitigation: additive event type following the exact pattern of `obpi_completion_repudiated`, which just landed under ADR-0.0.71 — a proven, low-risk shape.

4. **One-way door at the validator level.** Once `gz check` gates on round-trip coherence, every meta-governance writer must forever round-trip clean. Reversal in 12 months would require an ADR amendment. Justified: that is precisely the invariant we want; the asymmetry is intentional, because the cost of leaving the door open is the dormant-contradiction class this ADR closes.

5. **Risk of mis-targeting if the real problem were authoring discipline, not model coherence.** Mitigation: the census cited 4 confirmed contradictions with file:line on BOTH sides — the defect is structural (the model and its consumer cannot both be satisfied), not a narration problem. An authoring-discipline fix alone would leave the model still rejecting its own writers.

6. **The 67% brief-drift signal is deferred and could read as ignoring the bigger number.** Mitigation: explicitly scoped out as needing its own investigation ADR. Brief↔code drift is a different coupling (artifact-vs-code) from validator self-coherence (model-vs-its-own-consumer); folding them would produce an incoherent ADR. The deferral is named, not silent.

7. **The 2am operator scenario.** An operator override (`--accept-security-floor`) now also emits a ledger event; if the emission path failed, could it block completion? Mitigation: the event emission is additive and best-effort-after-completion in the same transaction as the existing receipt; a failed emission is a defect to fix, never a new gate on the override itself — the override remains operator-sovereign.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. PORT: `gz validate --writer-model-roundtrip` coherence validator — explicit registry of meta-governance artifact writers (handoff writers, insight append path, ledger-event factories, brief authoring); round-trips each writer's ACTUAL emitted output (real emission or writer-derived golden fixture, not a happy-path stub) through that artifact's own authoring model; fails closed (exit 3) on divergence; wired into `gz check`; exhaustiveness test asserts every meta-governance `*_handoff`/`*_event`/`*_record` writer is registered.
2. ADAPTER (C1/C2/C3): reconcile `HandoffFrontmatter` — widen `obpi_id` to the canonical `obpi.json` slug-optional pattern; replace bare `extra=forbid` with an explicit SUPERSET model declaring the min-info fields (last_lock_event_timestamp, last_commit_sha, branch) and degenerate/reaping fields (abandoned, category, abandoned_by, abandoned_at, previous_agent, reason); wire `validate_handoff_document` into a gate; verify the model round-trips clean against write_degenerate_handoff, _write_reaping_handoff, a normal-release handoff, and that a slug-bearing obpi_id both validates and exact-matches find_handoff_for_release.
3. ADAPTER (C4): reconcile `InsightRecord` ↔ authoring contract — provide an InsightRecord-backed append helper (mechanical writer); align AGENTS.md Behavior Rule 11 + agent-contract-rationale 'required fields' prose with the model envelope (add ts/type; evidence as list[str]); verify a helper-produced append round-trips clean through the OBPI-01 validator.
4. ADAPTER: `security_floor_overridden` ledger event — Pydantic event model + factory + ledger.json schema entry; emitted from `gz obpi complete --accept-security-floor` recording obpi_id, overridden surface(s), reason, attestor, ts; unit tests; round-trips clean through the OBPI-01 validator; census query surfaces the override.

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Narrow — validator scope only, fix the 4 contradictions later.** REJECTED by operator at the scope decision: leaves the 4 confirmed contradictions live until follow-on work, which means lock release and insight append keep failing in the interim. The adapters are cheap and the port needs real round-trip targets to validate against.

2. **Scatter the findings as 5 GHIs.** REJECTED: these are one coherent defect class with one structural root cause (coupled surfaces authored without §1a coherence verification, hidden by enforcement asymmetry). GHI-scattering loses the class framing, and there is an operator moratorium on reflexive GHI-filing. A foundation ADR is the correct trackable home; the 4 contradictions are its forcing instances.

3. **Just drop `extra=forbid` on the offending models.** REJECTED: trades typo-defense for permissiveness — a misspelled field would then pass silently, swapping one drift class for another. The explicit-superset model preserves typo-defense while accepting the real fields.

4. **Fix each contradiction as an independent direct-fix without the validator.** REJECTED: fixes instances, not the class. The root cause is that coupled surfaces get authored in separate OBPIs without coherence verification; without the round-trip validator, the next surface authored in a separate OBPI drifts again and trips the next pipeline run. DO IT RIGHT §1 mandates fixing the class.

5. **Broad — also remediate the 67% brief-drift and the adr-0.0.33-05 behave capitulation.** REJECTED by operator at the scope decision: scope creep. Brief↔code drift is a different coupling needing its own investigation; the single behave capitulation is a separable direct-fix. Folding them would produce an incoherent multi-class ADR.

6. **Feature kind instead of foundation.** REJECTED at the kind decision: this is not a user-facing capability but the self-coherence of the governance machinery — identity-shaping. The invariance test resolves yes (a harness whose own validators contradict each other is failing its reason to exist).

7. **Treat it as an authoring-discipline problem (better agent instructions) rather than model coherence.** REJECTED: the census cited both sides with file:line — the model and its consumer are mutually unsatisfiable regardless of how disciplined the author is. Better instructions cannot make a model accept a field it declares forbidden.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Narrow — validator scope only, fix the 4 contradictions later.** REJECTED by operator at the scope decision: leaves the 4 confirmed contradictions live until follow-on work, which means lock release and insight append keep failing in the interim. The adapters are cheap and the port needs real round-trip targets to validate against.

2. **Scatter the findings as 5 GHIs.** REJECTED: these are one coherent defect class with one structural root cause (coupled surfaces authored without §1a coherence verification, hidden by enforcement asymmetry). GHI-scattering loses the class framing, and there is an operator moratorium on reflexive GHI-filing. A foundation ADR is the correct trackable home; the 4 contradictions are its forcing instances.

3. **Just drop `extra=forbid` on the offending models.** REJECTED: trades typo-defense for permissiveness — a misspelled field would then pass silently, swapping one drift class for another. The explicit-superset model preserves typo-defense while accepting the real fields.

4. **Fix each contradiction as an independent direct-fix without the validator.** REJECTED: fixes instances, not the class. The root cause is that coupled surfaces get authored in separate OBPIs without coherence verification; without the round-trip validator, the next surface authored in a separate OBPI drifts again and trips the next pipeline run. DO IT RIGHT §1 mandates fixing the class.

5. **Broad — also remediate the 67% brief-drift and the adr-0.0.33-05 behave capitulation.** REJECTED by operator at the scope decision: scope creep. Brief↔code drift is a different coupling needing its own investigation; the single behave capitulation is a separable direct-fix. Folding them would produce an incoherent multi-class ADR.

6. **Feature kind instead of foundation.** REJECTED at the kind decision: this is not a user-facing capability but the self-coherence of the governance machinery — identity-shaping. The invariance test resolves yes (a harness whose own validators contradict each other is failing its reason to exist).

7. **Treat it as an authoring-discipline problem (better agent instructions) rather than model coherence.** REJECTED: the census cited both sides with file:line — the model and its consumer are mutually unsatisfiable regardless of how disciplined the author is. Better instructions cannot make a model accept a field it declares forbidden.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.72 | Pending | | | |
