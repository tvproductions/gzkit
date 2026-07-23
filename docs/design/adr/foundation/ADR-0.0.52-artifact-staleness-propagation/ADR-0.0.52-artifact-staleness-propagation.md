---
id: ADR-0.0.52-artifact-staleness-propagation
status: Draft
kind: foundation
semver: 0.0.52
lane: heavy
parent:
date: 2026-05-18
---

# ADR-0.0.52-artifact-staleness-propagation: Artifact Staleness Propagation

## Persona

`main-session` + `implementer`. Heavy-lane runtime contract change introducing a new validator family (`gz validate --adr-eval-fresh`, `gz validate --staleness-coherence`), four new ledger event kinds, a frontmatter schema delta, an OBPI brief schema delta, and a new CLI verb family (`gz adr clear-stale`, `gz adr explain-stale`, `gz adr propagation retry-tier2`). The mechanism is fail-closed by design at Tier 1 and attestation-gated at Tier 2; the `implementer` persona owns the atomic-transaction semantics (`tx_id` pairing of ledger emit + frontmatter write) and the Tier 2 anti-theatre defenses (refuse identical reason strings, require per-candidate identifier references) without relaxing them under pressure. The `main-session` persona owns the doctrine alignment — every relaxation request must trace back to anti-vibing operative claims before it lands.

## Why foundation tier?

Without this ADR, cross-artifact design-assumption coupling at the ADR/OBPI graph tier has no mechanical witness. Invariant 1a (coupled-surface coherence) holds at the file level; the `last_reviewed` ↔ skill-version coupling holds at the rule level; the artifact-graph tier — the upstream-canon → downstream-canon coherence boundary — is the missing third tier. Without it, downstream artifacts carry silently-invalidated design assumptions through the lifecycle window with no surface to detect or attest. This is identity-shaping: gzkit's commitment to T1/T2/T3 trust invariants requires that every cross-artifact coupling surface have a mechanical witness, not just the file and rule tiers.

**Port-vs-adapter framing:** Port. This ADR authors an abstract contract (the propagation pipeline interface that every artifact-lifecycle advance must honor). The specific detection algorithms (declared-edge walking, path-overlap, fan-in downweight, TF-IDF prefilter, LLM-as-judge ranker) are adapter implementations of the port. Future ADRs that swap algorithms (embedding similarity instead of TF-IDF, alternative judge frameworks per ADR-0.0.39 evolution) reuse the port unchanged.

## Intent

**Before / current state:** The closeout ceremony stops at "this ADR is attested" without computing the blast radius across the artifact graph. Today, when ADR A closes — its Decision body amended in the run-up, its OBPIs landing one by one — downstream ADRs/OBPIs that cite A or share A's surfaces carry silently-invalidated design assumptions. There is no mechanical witness; the discovery surface is "agent notices during next OBPI authoring," which is honor-system, late, and undetectable when missed. Invariant 1a (coupled-surface coherence) handles the file level; the `last_reviewed` ↔ skill-version coupling handles the rule level. The ADR/OBPI graph tier — the third tier — has no enforcement.

**After / target state:** Every ADR closeout and every OBPI completion fires a mechanical propagation pipeline. Downstream artifacts whose declared edges or surface overlap intersect the trigger receive `evaluation_stale` frontmatter flags paired with `artifact_staleness_flagged` ledger events. A second tier surfaces ranked semantic-impact candidates at ADR closeout boundaries for operator-attested promotion. Flagged artifacts are mechanically refused lifecycle advance (`gz validate --adr-eval-fresh`, fail-closed) until cleared via the confirm-or-amend resolution ceremony. Layer-1 frontmatter ↔ Layer-2 ledger coherence is fail-closed by a coherence validator. The trust-doctrine T2 evidence layer extends across the artifact graph the same way ADR-0.0.26 extended it across reasoning evidence.

ADR-0.0.26 closed the orthogonal **agent-reasoning → rule-corpus** loop (scores and reasoning artifacts feeding rule edits via human-attested GHI proposals). This ADR closes the **upstream-canon → downstream-canon** loop: when upstream artifact A's intent shifts at closeout or per-OBPI completion, downstream artifacts B/C/D whose design assumptions referenced A or shared A's surface must be flagged as evaluation-stale and refused stable advancement until re-evaluated.

The failure class this addresses, named: **silent invalidation of cross-artifact design assumptions through the lifecycle window** between when an upstream artifact's intent crystallizes and when downstream artifacts independently come up for closure. Without mechanical detection, the discovery surface is "agent notices during next OBPI authoring" — honor-system, late, undetectable when missed. The propagation pipeline mechanically witnesses every closeout and OBPI completion against the affected-set; the missing tier becomes load-bearing surface.

## Decision

Cross-artifact staleness propagation mechanism with two tiers, fired at every ADR closeout and every OBPI completion.

### Trigger surface (binding)

- `gz closeout <ADR-X.Y.Z>` fires the **full** pipeline (Tier 1 + Tier 2).
- `gz obpi complete <OBPI-X.Y.Z-NN>` fires **Tier 1 only** (Tier 2 is reserved for ADR boundaries to bound cost and noise).
- Both invoke a shared `gzkit.governance.propagation.propagate(trigger_event)` entry point. The hook is unconditional on the verb — no operator opt-in / opt-out flag, by design (no out-of-band trigger surface).

### Tier 1 — Mechanical detection (fail-closed)

Affected-set = (artifacts citing the upstream via frontmatter `parent:`, `cites:`, `relates_to:`) ∪ (artifacts whose OBPI `actual_paths_touched` intersect the upstream's). Apply **fan-in downweight** (calibrated threshold in `data/staleness_propagation_thresholds.json`): paths touched by ≥ N ADRs are excluded from overlap to prevent shared-infrastructure modules (`src/gzkit/validate.py`, `cli.py`) from dragging the whole graph into every affected-set.

Each member of the affected-set receives:

- Frontmatter entry: `evaluation_stale: [{upstream_id, flagged_at, source: mechanical, upstream_event_id}]`
- Ledger event: `artifact_staleness_flagged` (source: `mechanical`, with `detection_signal` like `declared_edge:cites` or `path_overlap:src/X/Y.py`)

### Tier 2 — Advisory candidate scan (ADR closeout only; NOT per-OBPI)

TF-IDF prefilter over corpus = all active artifacts' Decision / Intent sections → top-K candidates by cosine similarity. LLM-as-judge ranker (consuming ADR-0.0.39's judge contract surface) scores each candidate by plausibility of design-assumption impact, producing `(plausibility_score, reasoning, impact_summary)` per candidate. Operator reviews ranked list at closeout in a batch table; promote/reject per candidate with operator attestation; promoted candidates enter affected-set with `source: semantic_scan` and `attested_by` set. **The promotion gate is operator attestation, never automatic.** Ledger event `propagation_candidates_reviewed` records all promote/reject decisions even when nothing was promoted (provenance discipline — the review happened, the ledger records what was considered).

### Fast path (categorical no-change, 6 mechanical conditions)

Fast path fires when **all** are true:

1. No new REQ added since `adr_created` / `obpi_created`
2. No REQ-body semantic amendment (text-diff allowed only on prose around a REQ, not the REQ statement itself — enforced by REQ-extraction parser)
3. No new OBPI added to checklist (ADR closeout only)
4. `actual_paths_touched` ⊆ paths declared at authoring
5. No `kind:` / `lane:` / `sensitivity:` frontmatter shift
6. For ADR closeout: every child OBPI itself fast-pathed at its own completion (transitive no-surprise)

On fast-path fire: emit `propagation_evaluated` with `affected_set: []` and `fast_path_reason: {<conditions>}`. **Always emit the event — empty affected-set is governance evidence, not silence.**

### Bounded depth = 1

Each cascade step produces a discrete event with its own attestation. When a flagged artifact resolves (re-evaluate + amend/confirm + attest), its resolution closeout fires a *new independent* propagation wave on its own. Convergence through multiple bounded waves preserves per-cascade-step attestation provenance — depth=∞ was rejected as evidence-density-dilutive (one ceremony covering N flags collapses the T2 attestation density the trust doctrine values, and structurally misses the amendment-introduces-new-shifts subclass by spending the cascade at trigger-time).

### Resolution ceremony (confirm-or-amend)

```bash
gz adr clear-stale <flagged-id> --upstream <upstream-id> \
  --kind {confirmed_unchanged | amended} \
  --reason "..." --attest "..."
```

Invokes `gz-adr-evaluate <flagged-id>` (emits canonical `adr-evaluation` event per ADR-0.0.26 Decision 1 — this is the orthogonal composition surface). Emits `artifact_staleness_cleared` with `{artifact_id, upstream_id, flagged_event_id, clearance_kind, reason, attestation, fresh_evaluation_event_id}` and (for `amended`) `amendment_ref` (transitional handle = commit SHA until ADR-pool.adr-amendment-tracking promotes). Frontmatter entry removed atomically (paired with ledger emit via `tx_id`).

### Validators

- **`gz validate --adr-eval-fresh`** (fail-closed, exit 3): when an artifact carries unresolved `evaluation_stale` entries and is attempting lifecycle advance (closeout, attest, OBPI complete, audit-check). Joins default `gz check` pipeline.
- **`gz validate --staleness-coherence`**: cross-checks every frontmatter `evaluation_stale` entry has a matching ledger `artifact_staleness_flagged` event without a matching `artifact_staleness_cleared`, and vice versa. Catches Layer-1 vs Layer-2 drift (trust-chain-poisoning defense per `docs/governance/trust-doctrine.md`). Joins default `gz check`.

### Composition with ADR-0.0.26 (orthogonal)

`--adr-eval-fresh` and `--evaluation-justify-binding` are orthogonal validators — they check different invariants and both can fail independently:

| Artifact state | `--adr-eval-fresh` | `--evaluation-justify-binding` |
|---|---|---|
| stale flag, score ≥ 3.0 | fires | quiet |
| stale flag, score < 3.0 | fires | fires |
| no flag, score < 3.0 | quiet | fires |
| no flag, score ≥ 3.0 | quiet | quiet |

The clearance ceremony's `gz-adr-evaluate` re-run produces a fresh `adr-evaluation` event that ADR-0.0.26's validator consumes naturally if the fresh score < 3.0. No special interlock logic — composition through the shared `adr-evaluation` ledger event family. **Anti-pattern explicitly named: "one validator silently subsumes the other under condition X" — must never be added.**

### 2am operational discipline (load-bearing in design)

- **Atomic transaction semantics:** every ledger event emit + frontmatter write paired by `tx_id`. On crash mid-transaction, the next `--staleness-coherence` invocation reconciles.
- **LLM-as-judge graceful degradation:** timeout or schema-invalid response → emit `propagation_candidates_reviewed` with `reviews: []`, `judge_unreachable_reason: <reason>`, `operator_attestation: ""` (NOT operator-attested in this case; mechanical fallback). Closeout proceeds with Tier 1 only. Operator may retry via `gz adr propagation retry-tier2 <ADR-id>`.
- **`gz adr explain-stale <artifact-id> [--upstream <upstream-id>]`**: read-only query showing `detection_signal`, upstream, `flagged_at`, source per unresolved entry. 2am ergonomic surface.

### Tier 2 anti-theatre defenses (mechanical, in implementation)

- Refuse `[commit]` if all promoted/rejected candidates carry identical reason strings (copy-paste defense)
- Require operator rejection reasons to reference specific upstream or candidate identifiers (not generic "no impact" / "irrelevant")
- Operational tripwire (`gz arb`-style analytical receipt) periodically samples `propagation_candidates_reviewed` events and flags suspiciously uniform attestation patterns; measures `confirmed_unchanged` / `amended` clearance ratio (low `amended` ratio signals assumption-3 `paths_touched`-as-coupling-proxy failure); counts distinct ever-flagged artifacts (cumulative implicit-dependency surface size = one-way-door cost). Does not gate work; surfaces drift.

### Phasing (structurally significant, not just sequencing convenience)

- **Phase 1** (OBPIs 01–06, 08–10): closeout hook + Tier 1 detection + fast path + frontmatter + validators + resolution + ergonomics + tripwire + docs + tests. **Operationally complete on its own** — the validator works, the resolution ceremony works, the trust surface closes at Phase 1 attestation. Independent of ADR-0.0.39.
- **Phase 2** (OBPI-07): Tier 2 pipeline + interactive promotion surface. Hard-blocked on ADR-0.0.39 reaching `Proposed` with a named "judge contract surface" subsection locked. ADR-0.0.52 as a whole cannot `Validated` until OBPI-07 validates, but Phase 1 surface is **live and exercised throughout the prereq window** — this is the structural defense against the prereq-ossification failure mode.

### Cross-ADR ports established

| Direction | Partner | Nature |
|---|---|---|
| → | ADR-0.0.39 (LLM-as-judge doctrine) | Consumes judge framework (Phase 2) |
| ↔ | ADR-0.0.26 (eval feedback loop) | Orthogonal validator composition via shared `adr-evaluation` event family |
| → | ADR-pool.adr-amendment-tracking | Resolution ceremony's `clearance_kind: amended` (strong promotion signal) |
| → | ADR-pool.adr-layer-coherence | Fast-path's `no_metadata_shift` detection depends on layer-coherence enforcement |
| ⊥ | ADR-0.0.8 (feature-toggle system) | Explicitly NOT consumed — no pre-emptive escape hatch |

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The artifact relationship graph reconstructs from L1+L2 canon via gz state — the cross-artifact surface staleness flags propagate across. | uv run gz state --json | 0 |

## Consequences

### Positive

1. Closes the **upstream-canon → downstream-canon trust-doctrine loop**. ADR-0.0.26 closed the orthogonal agent-reasoning → rule-corpus loop; together they cover the two principal trust-doctrine evidence flows that previously terminated at "agent reasoned and proceeded."
2. The fail-closed mechanical surface (Tier 1) catches the **declared-edge and path-overlap subclasses** of design-assumption coupling without honor-system reliance. Every flag is a Layer-2 ledger event paired with a Layer-1 frontmatter entry; every clearance is operator-attested.
3. The advisory surface (Tier 2) covers the **silent-cross-conceptual-impact subclass** that mechanical detection structurally cannot reach. Anti-vibing operative claim 1 (5:1 governance ratio is product not overhead) justifies shipping both tiers in one ADR rather than deferring Tier 2 to a sibling.
4. Composes **orthogonally** with ADR-0.0.26 through the shared `adr-evaluation` ledger event family. Resolution ceremony's `gz-adr-evaluate` re-run is the natural composition surface — no new interlock logic required.
5. **Self-application is the correctness proof.** The ADR is subject to its own propagation pipeline. When ADR-0.0.39 amends its judge contract mid-flight (the meta-irony case), this ADR's OBPI-07 will be flagged `evaluation_stale: ADR-0.0.39` by its own mechanism and resolve via its own ceremony. If the mechanism could not handle this case, it would be wrong by construction.
6. **Phase 1 / Phase 2 phasing is structurally protective** against the long-prereq-window ignore-pattern failure mode (operator may exercise the full Phase 1 surface during the entire Phase 2 prereq wait). Phase 1 mechanical adoption builds the muscle memory Phase 2 needs to land into.
7. Anchors the promotion of **two pool ADRs** (`ADR-pool.adr-amendment-tracking`, `ADR-pool.adr-layer-coherence`) by creating operational demand for both surfaces — naturally moves both up the priority queue.
8. The **depth=1 attestation-density principle** preserves per-cascade-step provenance under the trust-doctrine T2 evidence-density invariant. Each cascade step earns its own attestation; depth=∞ was rejected as evidence-dilutive (one event covering N flags collapses the T2 attestation density the trust doctrine values).
9. The **fast path** (6 categorical conditions) makes the per-OBPI-completion cadence tolerable — the common case (implemented-exactly-as-designed) short-circuits to a single `propagation_evaluated` event with empty affected-set. Operator-economy preserved without abandoning the trigger frequency the depth=1 principle requires.

### Negative

1. **Hard prereq on ADR-0.0.39 creates critical-path coupling.** ADR-0.0.52 cannot `Validated` until ADR-0.0.39 reaches `Proposed` with a named "judge contract surface" subsection locked. If 0.0.39 takes longer than expected, OBPI-07 cannot start; the ignore-pattern risk (Pre-Mortem failure mode #3) is non-zero even under the loosened-prereq-to-Proposed tightening from Constraint Archaeology #1.

2. **Per-OBPI-completion trigger cadence is high — fast path is load-bearing.** If the fast path's 6 categorical conditions are too strict and rarely fire, churn pushes back to the per-trigger pipeline cost. Calibration is empirical via `data/staleness_propagation_thresholds.json`; misjudgment costs operator-economy.

3. **Tier 2 surface introduces stochastic input to a fail-closed governance pipeline.** The promotion gate (operator attestation per-candidate) is the only structural defense against the stochastic surface becoming a vibing channel. Anti-theatre mechanical defenses (refuse identical reason strings, require per-candidate identifier references in rejection reasons, tripwire receipt) supplement but do not replace operator discipline.

4. **Tier 2 theatre is the named most-likely failure mode** (Pre-Mortem #1, operator-ratified). Operators glazing through candidate review at every closeout, batch-rejecting or copy-pasting reasons to clear it, would degrade attestation to ritual. The mechanical defenses + tripwire surface this drift, but cannot prevent it. The shakiest WWHTBT condition (operator-engagement-with-Tier-2) is operationalized exactly by this failure mode; Tier 2's interactive surface design carries unusual load — it is the surface that must *resist becoming theatre* against the predicted failure mode.

5. **Goodhart risk inherited from ADR-0.0.26** at the closeout-text-shapes-downstream-flag layer. Agents who know closeout text shapes downstream affected-sets may craft closeout text accordingly. Mitigation: propagation is observational (closeout text is the operator's job, not the agent's), and rule-corpus promotion remains operator-attested per 0.0.26. Cite ADR-0.0.26 § Consequences/Negative directly; same risk shape, same mitigation.

6. **Cumulative one-way-door reversibility cost.** Mechanism-level reversal is one-way through ADR amendment ceremony; the implicit-dependency surface (artifacts authored under the mechanism's silent guarantees) grows over time. **Twelve-month reversal cost is materially higher than landing-day reversal cost.** Tripwire receipt's distinct-ever-flagged-artifacts count is the metric. No pre-emptive feature-toggle escape hatch ships with this ADR; if reversal pressure materializes, a separate ADR adds the toggle with full ceremony around when-it-is-acceptable-to-flip.

7. **Both-tiers-in-one-ADR pattern carried hidden reversibility cost** (visible at Q3 design time; doctrine still preferred B). Tier 2 removal is one-way through ADR amendment. Named here as cost rather than discovery.

8. **Implicit assumption surface — load-bearing operational assumptions made explicit:**
   - **Artifact graph is dense enough for propagation to produce meaningful affected-sets.** Sparse graph → mechanism mostly fast-paths or returns empty → "this never fires" pattern → silent abandonment. *Detectability: operational, depends on corpus shape.*
   - **Canon-text corpus is stable enough between triggers for TF-IDF to produce stable rankings.** Rapidly-edited canon → rankings churn → operators see inconsistent candidate orderings. *Detectability: side-by-side ledger replay.*
   - **`actual_paths_touched` is a meaningful proxy for design-assumption coupling.** If false, Tier 1 path-overlap detection is theatre and forces operators to clear flags that don't correspond to actual impact, degrading `confirmed_unchanged` reasons to copy-paste boilerplate (same theatre pattern, mechanical instead of stochastic). *Detectability: measurable from `confirmed_unchanged` vs `amended` clearance ratio in the tripwire receipt.*
   - **OBPIs are the right unit of trigger granularity.** Bundled OBPI commits → per-OBPI trigger fires after-the-fact for changes that were one design unit → fast-path conditions evaluated on staged increments rather than the design unit. *Detectability: ledger trigger-event correlation analysis.*
   - **Closeout = intent-stable for the upstream artifact.** Pre-closeout amendments to upstream Decision drafts → downstream artifacts authored against the draft are stale before the trigger fires. OBPI-completion triggers partially cover; doesn't fully eliminate.
   - **Operator typing budget is bounded but renewable per closeout.** ADR closeouts multiple-times-per-day → Tier 2 review fatigue compounds with failure mode #1, renewable-budget assumption breaks. *Detectability: operational telemetry — count promote/reject decisions per operator per rolling window.*
   - **LLM-as-judge outputs are honest under gzkit doctrine** (inherited from ADR-0.0.39). If 0.0.39's judge framework allows known-failure modes 0.0.52 does not model, those modes propagate. Hard prereq + back-pointer to 0.0.39's judge-contract subsection is the surface.

9. **Ledger schema grows by four event kinds** (`artifact_staleness_flagged`, `artifact_staleness_cleared`, `propagation_evaluated`, `propagation_candidates_reviewed`). `gz validate --documents` must recognize them; ledger consumers must update. Backward-compatible (additive) but a surface to maintain.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 10

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.52-01: OBPI brief schema addition — `actual_paths_touched` array field populated by `gz obpi complete` from staged-file analysis (precondition for Tier 1 path-overlap detection)
- [ ] OBPI-0.0.52-02: Pydantic models + ledger event JSON Schema registration + frontmatter schema delta (`evaluation_stale`) + threshold config model (`data/staleness_propagation_thresholds.json`)
- [ ] OBPI-0.0.52-03: Tier 1 mechanical detection algorithm — declared edges + path overlap + fan-in downweight; fast-path 6-condition check; `propagation_evaluated` and `artifact_staleness_flagged` event emission with `tx_id` pairing
- [ ] OBPI-0.0.52-04: Trigger wiring — `gz closeout` and `gz obpi complete` hooks into `gzkit.governance.propagation.propagate`; atomic-transaction semantics (frontmatter write + ledger emit paired by `tx_id`)
- [ ] OBPI-0.0.52-05: `gz validate --adr-eval-fresh` validator + `gz validate --staleness-coherence` validator; default `gz check` bundle integration; `gz adr audit-check` augmentation to refuse `Completed` claim if any child OBPI carries unresolved flag
- [ ] OBPI-0.0.52-06: `gz adr clear-stale` resolution verb + `gz-adr-evaluate` invocation + `artifact_staleness_cleared` event emission with operator attestation + composition with ADR-0.0.26's `--evaluation-justify-binding` validated end-to-end
- [ ] OBPI-0.0.52-07: **HARD BLOCKED on ADR-0.0.39 reaching `Proposed` with named judge-contract surface locked.** Tier 2 pipeline — TF-IDF prefilter + LLM-as-judge ranker consuming 0.0.39 framework; batch-table interactive promotion surface with mechanical anti-theatre defenses (refuse identical reasons, require per-candidate identifier references); `propagation_candidates_reviewed` event; graceful degradation on judge unreachability via `judge_unreachable_reason`; `gz adr propagation retry-tier2` recovery verb
- [ ] OBPI-0.0.52-08: Status surfacing — `gz status --table` Stale column; `gz state --json` `staleness_flags` payload; `gz adr explain-stale` read-only query verb; tripwire `arb` analytical receipt (samples `propagation_candidates_reviewed` events, measures `confirmed_unchanged`/`amended` clearance ratio, counts distinct ever-flagged artifacts)
- [ ] OBPI-0.0.52-09: BDD coverage — heavy-lane `@REQ`-tagged scenarios for fast-path fire, Tier 1 mechanical detection, Tier 2 advisory candidate promotion, clearance ceremony, validator fail-close, anti-theatre defenses, `tx_id` recovery
- [ ] OBPI-0.0.52-10: Docs + runbook updates — operator runbook, governance runbook, new-verb manpages (`gz adr clear-stale`, `gz adr explain-stale`, `gz adr propagation retry-tier2`, `gz validate --adr-eval-fresh`, `gz validate --staleness-coherence`), AGENTS.md § Behavior Rules entry naming the staleness-flag-resolution discipline

## Q&A Transcript

Authored 2026-05-18 via `gz-design` skill (collaborative design dialogue). Operator (g0) opened with the gap observation: "the evaluate steps in our pipeline, including those recently designed as orchestrated routing skills for evaluation, do [not] propagate the changes that result from an ADR's implementation to related/affected ADRs/OPBIs so that their own design assumptions are adjusted if/when necessary, this is an oversight."

Routed to ADR territory (foundation kind, by operator's identification). Overlap survey against existing pool ADRs found `adr-amendment-tracking` (adjacent — self-amendment, not cross-artifact propagation), `adr-layer-coherence` (adjacent — within-ADR layer coherence, different boundary), `ADR-0.0.26 evaluation-feedback-loop-doctrine` (sibling — closes the orthogonal agent-reasoning → rule-corpus loop), and `artifact-graph-navigation` (enabling, deferred). No supersession.

Six structuring questions resolved through design dialogue:

| Q | Locked decision | Operator framing |
|---|---|---|
| Q1 trigger scope | Closeout + OBPI completion | "more churn than I had in mind, but the logic is sound" |
| Q2 detection rule | Declared edges + path overlap + fan-in downweight, plus Tier 2 semantic scan at ADR boundaries | "you might have a provision that, at adr boundaries, we do a broader semantic search... a meaning/likelihood scan" |
| Q3 single vs phased ADR | Both tiers in 0.0.52 with hard prereq on ADR-0.0.39 | "B is more suited to gzkit philosophy" |
| Q4 cascade depth | Depth = 1 (per-cascade-step attestation; self-correcting via downstream re-closeout waves) | Operator initially "govmaxxing" (read as depth=∞); reframed via attestation-provenance-density argument that depth=1 is the actually-higher-governance answer; ratified "A it is" |
| Q5 fast-path definition | Categorical no-change (6 mechanical conditions); always emit event | "B" |
| Q6 resolution ceremony | Confirm-or-amend re-evaluation with orthogonal validator composition | "recommend?" → A ratified |

Seven design forcing functions applied (Pre-Mortem, WWHTBT, Constraint Archaeology, Assumption Surfacing, 2am Operator, Reversibility, Scope Minimization) and closing question. Each forcing function produced concrete decisions that landed in Decision / Consequences sections rather than transcript footnotes. See `adr-interview.json` for the full structured interview record and provenance.

Two structural amendments emerged from forcing-function review:

- **Hard prereq strictness loosened** from "ADR-0.0.39 must `Validated`" to "ADR-0.0.39 must `Proposed` with named 'judge contract surface' subsection locked" (Constraint Archaeology #1, recommended B). Halves prereq window; reduces failure-mode #3 risk; creates contract-stability authoring obligation on 0.0.39 that must be communicated to its author.
- **Phasing recognized as structurally significant** (Scope Minimization recommendation n-o). Phase 1 / Phase 2 distinction promoted from sequencing convenience into Decision body — Phase 1 must be operationally complete on its own, Phase 2 is additive capability.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Pydantic models: `src/gzkit/governance/propagation/models.py`
- [ ] Detection algorithm: `src/gzkit/governance/propagation/detect.py`
- [ ] Trigger wiring: `src/gzkit/governance/propagation/trigger.py` + hooks in `src/gzkit/commands/closeout_cmd.py` and `src/gzkit/commands/obpi_complete_cmd.py`
- [ ] Validators: `src/gzkit/governance/trust_audits.py` (new scopes `--adr-eval-fresh`, `--staleness-coherence`)
- [ ] Resolution verb: `src/gzkit/commands/adr_clear_stale_cmd.py`
- [ ] Explain verb: `src/gzkit/commands/adr_explain_stale_cmd.py`
- [ ] Retry verb: `src/gzkit/commands/adr_propagation_cmd.py` (subverb `retry-tier2`)
- [ ] Threshold config: `data/staleness_propagation_thresholds.json`
- [ ] OBPI brief schema delta: `src/gzkit/schemas/obpi.json` (`actual_paths_touched`)
- [ ] Frontmatter schema delta: ADR/OBPI frontmatter schemas (`evaluation_stale`)
- [ ] Ledger event corpus schema: registrations for `artifact_staleness_flagged`, `artifact_staleness_cleared`, `propagation_evaluated`, `propagation_candidates_reviewed`
- [ ] Tests: `tests/governance/test_staleness_propagation.py`, `tests/governance/test_adr_eval_fresh.py`, `tests/governance/test_staleness_coherence.py`
- [ ] BDD: `features/staleness_propagation.feature`
- [ ] Docs: `docs/user/runbook.md` § Staleness propagation; `docs/governance/governance_runbook.md` § Cross-artifact coherence; `docs/user/manpages/` for each new verb
- [ ] AGENTS.md: § Behavior Rules entry naming the staleness-flag resolution discipline
- [ ] Interview record: `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/adr-interview.json`

## Alternatives Considered

1. **Tier 1 only with Tier 2 deferred to a sibling foundation ADR (Q3 option A).** Rejected on anti-vibing operative claim 1: leaving the silent-cross-conceptual-impact subclass open between landings would be a vibing surface; deferring Tier 2 framed as cost ("lighter ceremony") is exactly the framing the doctrine forbids. The meta-irony of coupling 0.0.52 to a still-Pending 0.0.39 was reframed as self-validation — the mechanism's correctness is demonstrated by its survival under self-application.

2. **Depth = ∞ (transitive closure cascade in single trigger) — Q4 option B.** Rejected on attestation-provenance grounds. Depth=∞ looks govmaxxing (more flags per event) but is actually evidence-density-dilutive (one ceremony, one attestation receipt covers N flags). Depth=1 produces N attestations for an N-step cascade and self-corrects through downstream re-closeout waves — including the amendment-introduces-new-shifts subclass that depth=∞ misses by spending the cascade at trigger-time. Depth=1 is the *higher*-governance answer when measured by per-artifact attestation density (T2 ledger truth).

3. **Pure byte-equality fast path (Q5 option A).** Rejected: cosmetic edits (comma rephrasing, typo fix in Decision body) would falsely flip the fast path off, pushing churn back up and rendering the fast path effectively unused.

4. **Operator-attested fast path (Q5 option C).** Rejected: reintroduces operator judgment into a mechanical gate, undermining the depth=1 attestation-density principle and reintroducing the vibing surface in exactly the place the design tried to remove it from.

5. **Full re-evaluation resolution ceremony (Q6 option B).** Rejected: heavy ceremony is for authoring, not for downstream-impact check. Re-using the full 8-dim + red-team cycle as the clearance ceremony would discourage flagging, creating pressure toward fewer triggers and undermining the depth=1 high-attestation-density principle.

6. **Source-dependent resolution rigor (Q6 option C).** Rejected: double-counts. The rigor for semantic-scan candidates belongs in the promotion gate (operator attestation per-candidate before entering the affected-set), not in the resolution ceremony. Once an artifact is in the affected-set, all flags resolve the same way.

7. **Hard prereq = ADR-0.0.39 `Validated` (Constraint Archaeology #1, option A).** Rejected after re-examination: the strict prereq materially amplifies failure mode #3 (ignore-pattern ossification during prereq wait). Loosening to `Proposed with named judge-contract surface locked` halves the prereq window without sacrificing doctrine alignment, because any contract amendment between Proposed and Validated would be flagged by this ADR's own propagation mechanism (self-validation).

8. **Soft prereq with LLM-judge mock surface (Constraint Archaeology #1, option C).** Rejected: shipping a stub judge produces meaningless scores that look like Tier 2 governance evidence in the ledger. Worse, it actively hardens failure mode #1 (Tier 2 theatre) from day one because operators learn "Tier 2 candidates are noise" before there is ever real signal to engage with. Anti-doctrine.

9. **Pre-emptive feature-toggle escape hatch via ADR-0.0.8.** Rejected as Reversibility (k) negative scope: a toggle is a vibing surface — "just turn it off if it's annoying" becomes the temptation, and anti-vibing operative claim 2 forbids framing this as velocity-coded tradeoff. If operational evidence eventually shows reversal pressure that warrants the escape hatch, a separate ADR adds the toggle with full ceremony around when-it-is-acceptable-to-flip.

10. **`gz adr clear-stale` folded into `gz adr evaluate --clear-stale` (Constraint Archaeology #4).** Rejected: surface clarity outweighs verb-count economy. Clearance is a distinct ceremony with its own attestation and event family. Folding would reintroduce the "I ran propagation manually" out-of-band concern the design explicitly rejected.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.52 | Pending | | | |
