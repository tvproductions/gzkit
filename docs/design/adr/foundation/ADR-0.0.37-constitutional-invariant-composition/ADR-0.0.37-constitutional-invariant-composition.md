---
id: ADR-0.0.37
status: Draft
kind: foundation
semver: 0.0.37
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-06
---

# ADR-0.0.37-constitutional-invariant-composition: Constitutional Invariant Composition

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats AGENTS.md as a Layer-3 derived view to be composed from a constitutional invariant registry, never as Layer-1 canon. Treats brief↔reality coherence as a structural invariant whose witness is mechanical (schema + validator + ledger event + gate), never narrative. Refuses to assert foundational claims in prose without a corresponding registry entry; refuses to advance a brief past Stage 2 or close it past Stage 5 without a fresh reconciliation receipt. The same skepticism the existing § Attestation receipt-ID rule applies at code-execution time, this ADR's persona applies at the canon and brief layers — every claim must be observable, dated, signed, replayable.

This is the largest single foundation ADR in the cluster (ten OBPIs) because it codifies two co-load-bearing invariants (composition + brief↔reality coherence) plus the migration that proves the framework. Decomposition discipline applies — each OBPI is a separable invariant, not a fragmentation move. The ten-OBPI count is locked from the design dialogue's MAX DO IT RIGHT pass.

## Why foundation tier?

Without this ADR, constitutional invariants don't compose mechanically — each invariant has its own validator and recovery doctrine, but invariant composition (e.g., "every artifact satisfies both T1 read-path and T2 write-path") is ad-hoc judgment.

This ADR authors a port: the constitutional-invariant composition contract every multi-invariant validator binds to (composition is structural, not narrated).

## Intent

gzkit's foundation surface is currently inverted. AGENTS.md — the prose contract every agent reads at session start — is treated as Layer 1 canon, with foundation ADRs documenting "defenses of" its claims. This makes every foundational invariant only as trustworthy as the prose it's encoded in: an editable, drift-prone, narrative surface that the project's own MAKE LLM STOCHASTIC VIBES INERT mantra explicitly identifies as the named failure class. Two pool stubs (`ADR-pool.brief-authoring-evidence-checks`, `ADR-pool.obpi-pipeline-dispatch-attestation`) recently rejected foundation-kind framing for their own work on the explicit grounds that "the invariant already exists in AGENTS.md operative-claim-4" — the inversion in plain sight, twice within a week.

The operator's loaded statement (preserved verbatim per OEE doctrine § 3): *"A statement in what is ultimately flimsy and ephemeral - AGENTS.MD - can NOT be considered foundation. Foundation adrs must place structures and processes that guarantee gzkits behavior. I have the LOWEST amount of faith in AGENTS.md."* The doctrinal correction the operator named: *"Foundation = invariant intent of the project's purpose, established with structural witness (schema + validator + ledger event), not asserted in prose. Feature = capability that users invoke (CLI flags, surfaces, mechanical defenses of a foundation invariant). Pool = backlog for feature work. AGENTS.md = composed/generated view of the foundation set, not source-of-truth."*

This ADR fixes the inversion. It establishes a constitutional-invariant registry as Layer 1 canon, renders AGENTS.md from the registry as a derived view, and codifies brief↔reality coherence as the first concrete invariant flowing through the new mechanism. The two halves are co-load-bearing: brief-reconciliation cannot be trusted without the composition framework that gives the invariant its structural witness; the composition framework cannot be tested without an instance.

The recurring failure-mode evidence motivating this ADR: OBPI-0.0.29-02's mid-Stage-4 surface where `data/behave_coverage_waivers.json` had to be edited outside the brief allowlist as coupled-surface coherence work, with the same edit having been applied silently in OBPI-0.0.29-01 (precedent without ceremony). The same shape recurs across the cluster. The pool stubs naming GHI #380 / #406 / #407 / #381 are evidence that the inversion is producing repeated drift at every authoring-time and execution-time boundary the gate covenant assumes is closed.

## Decision

Codify two co-load-bearing foundation invariants in one ADR:

**Invariant CIC-1 (composition).** Every claim that AGENTS.md asserts as foundational MUST originate from an addressable, schema-validated, ledger-witnessed entry in the constitutional invariant registry at `.gzkit/invariants/`. AGENTS.md is *rendered* from the registry; drift between rendered view and committed AGENTS.md is fail-closed at `gz validate --invariant-coherence` (and `gz check`). Hand-authoring foundational claims directly into AGENTS.md is the same class of failure as hand-writing ledger entries (AGENTS.md § Behavior Rules — Never #2 applied at the canon layer).

**Invariant CIC-2 (brief↔reality coherence).** Every OBPI brief is a structural artifact whose Allowed Paths, Discovery Checklist, Verification commands, REQ-IDs, and citation tuples MUST reconcile against current project shape before Stage 2 implementation begins. Drift is fail-closed at `gz obpi pipeline` Stage 1 (refuses Stage 2 entry without a fresh reconciliation receipt) and at `gz obpi complete` Stage 5 (refuses completion without a reconciliation receipt newer than the most recent mutation in the brief's allowlist domain).

**Rationale (numbered, binding):**

1. **Foundation requires structural witness, not prose.** A foundational claim asserted only in AGENTS.md is indistinguishable from doctrine drift at the next agent session — it can be edited, reinterpreted, partially-loaded, or outright forgotten. The mantra (MAKE LLM STOCHASTIC VIBES INERT) names this failure class explicitly; this ADR mechanizes the structural defense the mantra calls for at the canon layer itself.

2. **Two invariants in one ADR because they are co-load-bearing.** CIC-2 (brief↔reality coherence) cannot be trusted without CIC-1's witness mechanism — a brief-reconciliation invariant codified in prose without a structural-witness framework underneath it would re-instance the inversion. CIC-1 (composition) cannot be tested without an instance. Sequencing them across two ADR ceremonies doubles the gate ceremony with no separability gain.

3. **The composition framework's first composition target is AGENTS.md** because AGENTS.md is the most-read, most-edited, highest-blast-radius prose surface in the project. Other composition targets (skill READMEs, persona files, rule mirrors) are forward-references; the registry abstraction supports them but this ADR scopes the AGENTS.md instance only.

4. **The brief-reconciliation invariant covers five drift dimensions** (allowlist, Discovery Checklist, Verification verbs, REQ counts, citation tuples) because each is a separately-observed drift class with a distinct mechanical signature. The cluster's recurring evidence (OBPI-0.0.29-01 / 02 allowlist drift, GHI #380 manpage-anchor + scope-collision, GHI #406 cluster-coherence dimensions, GHI #407 evaluation-time dimensions) names all five.

5. **Reconciliation receipts must be fresher than the most recent mutation in the brief's allowlist domain** because a stale receipt that predates a coupled-surface change carries the same misinformation as no receipt. Freshness is the structural test for receipt validity (parallel to the receipt-freshness rule already governing `.plan-audit-receipt-*.json` per `.claude/rules/governance-core.md`).

6. **Fail-closed at both Stage 1 and Stage 5** because Stage 1 catches authoring drift (brief ≠ project shape at implementation start) and Stage 5 catches in-flight drift (brief shape mutated during implementation, e.g. when a sibling OBPI lands and shifts the allowlist domain). One-gate-only would leave half the failure surface open.

7. **Pool stubs for `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` remain in pool** because they're feature-shaped defenses of CIC-2 once this foundation lands. Promoting them now (as the agent's flawed pre-correction recommendation proposed) would entrench the inversion.

8. **Ten OBPIs is the right size** because each codifies one separable invariant or surface: schema + registry primitive, composition renderer, composition drift validator, brief structural schema, reconciliation engine, CLI verb, Stage 1 gate, Stage 5 gate, AGENTS.md migration, doctrine refresh. Bundling produces one Gate 5 witness for ten separable concerns; over-fragmenting produces ceremony without invariant addition.

**The invariant (canonical statement):** gzkit's foundation surface is composed from a schema-validated, ledger-witnessed constitutional invariant registry, not authored as primary canon in prose. Every OBPI brief reconciles against current project shape before implementation begins and before completion is recorded; drift between brief-declared shape and observed project shape is fail-closed at Stage 1 and Stage 5 of the OBPI pipeline.

**Mechanical surfaces (what changes in code):**

- `src/gzkit/governance/invariants.py` (new): frozen Pydantic `ConstitutionalInvariant` (id, claim, structural_witness, composition_targets fields).
- `src/gzkit/schemas/constitutional_invariant.json` (new): JSON Schema mirror; `additionalProperties: false`; structural-witness array `minItems: 1`.
- `.gzkit/invariants/*.yaml` (new directory): one YAML per invariant; CIC-1, CIC-2, plus the self-referential "every foundation ADR registers ≥1 invariant" check are the seed entries.
- `src/gzkit/governance/compose.py` (new): composition renderer; consumes registry, projects into AGENTS.md template, emits deterministic byte sequence.
- `src/gzkit/commands/governance_render.py` (new): `gz governance render --target agents-md` CLI verb.
- `src/gzkit/governance/trust_audits.py`: extend with `validate_invariant_coherence` (re-renders, byte-compares to committed AGENTS.md) and `validate_brief_reconcile` (drift detection across the five reconciliation dimensions).
- `src/gzkit/schemas/obpi_brief_structure.json` (new): structural schema for OBPI briefs beyond markdown frontmatter.
- `src/gzkit/governance/brief_reconcile.py` (new): reconciliation engine; per-dimension delta computation.
- `src/gzkit/commands/brief_reconcile.py` (new): `gz brief reconcile <OBPI-ID> [--apply]` CLI verb.
- `src/gzkit/cli/parser_artifacts.py`: register the new verbs (`governance render`, `brief reconcile`).
- `src/gzkit/pipeline_runtime.py`: extend Stage 1 to require fresh reconciliation receipt before Stage 2 entry.
- `src/gzkit/commands/obpi_complete.py`: extend to require fresh reconciliation receipt before completion event emission.
- `.gzkit/schemas/ledger_events.json`: extend ledger event family with `invariant_registered`, `invariant_amended`, `composition_rendered`, `composition_drift_detected`, `brief_reconciled`, `brief_reconcile_drift_detected`.
- `tests/governance/test_invariants.py`, `tests/governance/test_compose.py`, `tests/governance/test_brief_reconcile.py`, `tests/commands/test_governance_render.py`, `tests/commands/test_brief_reconcile.py`: REQ-derived assertions across the ten OBPIs.
- `features/constitutional_invariants.feature` + `features/brief_reconcile.feature` (new): BDD scenarios tagged `@REQ-0.0.37-NN-MM`.
- `docs/user/manpages/gz-governance.md` + `docs/user/manpages/gz-brief.md` (new): manpages per gate5-runbook-code-covenant.
- `docs/user/runbook.md`: runbook entries for the new ceremony surfaces.
- `docs/governance/advisory-rules-audit.md`: scorecard entries classifying the new validator scopes.
- AGENTS.md: hand-authored content migrated to `.gzkit/invariants/` registry entries; the file becomes a rendered output.

**Ten OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.37-01 — Constitutional invariant schema + registry primitive:** Frozen Pydantic `ConstitutionalInvariant` (id, claim, structural_witness array, composition_targets array); JSON Schema mirror; first three seed invariants registered: CIC-1, CIC-2, and the self-referential "every foundation ADR registers ≥1 invariant" check.

**OBPI-0.0.37-02 — Composition renderer:** `gz governance render --target agents-md` consumes the registry and projects into AGENTS.md's existing structural shape; deterministic byte output (template-rendered, not LLM-rewritten); supports `--check` mode that exits non-zero on drift without writing.

**OBPI-0.0.37-03 — Composition drift validator:** `gz validate --invariant-coherence` re-renders the registry and byte-compares to committed AGENTS.md; fail-closes on drift; emits `composition_drift_detected` ledger event.

**OBPI-0.0.37-04 — OBPI brief structural schema:** Pydantic `BriefStructure` model; JSON Schema mirror; extends current frontmatter to include machine-readable allowlist domain definitions, REQ-IDs as structured fields, verification commands as structured array, citation tuples; backward-compat permissive mode with deprecation window.

**OBPI-0.0.37-05 — Brief reconciliation engine:** `brief_reconcile.py`: given an OBPI brief, walks the project tree, computes observed vs. declared deltas across all five reconciliation dimensions (allowlist coherence with coupled-surface registries, Discovery Checklist file existence, Verification verb resolution against parser_artifacts, REQ-count parity against acceptance criteria, citation-tuple freshness against current corpus revision).

**OBPI-0.0.37-06 — `gz brief reconcile` CLI verb:** Operator-runnable surface; emits `brief_reconciled` ledger event with delta summary; supports `--apply` to write operator-attested amendments back into the brief frontmatter.

**OBPI-0.0.37-07 — Pipeline Stage 1 fail-close gate:** Extends `gz obpi pipeline` Stage 1 to require a fresh reconciliation receipt before Stage 2 entry; receipt freshness defined as "newer than the most recent mutation timestamp in the brief's allowlist domain."

**OBPI-0.0.37-08 — `gz obpi complete` fail-close gate:** Refuses Stage 5 completion without a fresh reconciliation receipt; receipt staleness blocks the completion event from emitting. The 2am-operator escape hatch (`--accept-stale-reconciliation --reason '<text>'`) records the override to the ledger as a `brief_reconcile_drift_overridden` event.

**OBPI-0.0.37-09 — AGENTS.md migration:** The seed pass — every existing § in AGENTS.md gets analyzed, decomposed into discrete constitutional invariants, registered in `.gzkit/invariants/`. AGENTS.md is then rendered from the registry; drift validator runs in CI to lock the inversion. Operator-attested per § (foundation-kind brief-level Gate 5 across the migration).

**OBPI-0.0.37-10 — Doctrine refresh:** Update ADR-0.0.18 references to clarify the kind axis carries the structural-witness vs. prose distinction (via the `gz adr amend` flow if it exists; otherwise via amendment-pool stub). Update pool stubs `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` with re-routing notes that name CIC-2 as their foundation surface. Update contributing docs.

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-03 (composition framework lands first; ledger events online). Then OBPI-04 → OBPI-05 → OBPI-06 (brief reconciliation engine). Then OBPI-07 → OBPI-08 (gates wired). Then OBPI-09 (migration; depends on OBPI-03 to validate the result). OBPI-10 in parallel with OBPI-09.

**Lane: Heavy.** New Pydantic models + new schema mirrors + new CLI verbs (`gz governance render`, `gz brief reconcile`) + new ledger event family + new validator scopes (`--invariant-coherence`, `--brief-reconcile`) + breaking change to AGENTS.md authoring surface. All trigger heavy-lane rigor per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.18.

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT specify the full constitution-amendment ceremony — the registry primitive (OBPI-01) supports `gz adr amend`-style amendments via emerging amendment pool stubs, but the formal amendment-tracking ceremony is `ADR-pool.adr-amendment-tracking`'s scope.
- Does NOT cover composition targets beyond AGENTS.md — skill READMEs, persona files, rule mirrors are forward-references; the registry abstraction supports them but each composition target is its own (likely future) feature ADR.
- Does NOT cover frontmatter↔body↔ledger metadata coherence — that is `ADR-pool.adr-layer-coherence`'s scope (parallel concern at the metadata layer; this ADR addresses the canon-prose layer).
- Does NOT promote `ADR-pool.brief-authoring-evidence-checks` or `ADR-pool.obpi-pipeline-dispatch-attestation` — those remain in pool until CIC-2 lands; they then become feature-kind ADRs that consume CIC-2.
- Does NOT modify the ledger event schema beyond the new event family added here — broader ledger schema changes are out of scope.
- Does NOT introduce a new attestation type — the existing `human` / `agent-relayed-operator-attestation` / `self-close-exception` taxonomy carries through.

## Comparator Uplift (2026-05-07)

Comparator lessons must not enter gzkit as prose pasted into AGENTS.md. This ADR
is the intake gate: any borrowed doctrine that claims to shape gzkit identity
must become a constitutional invariant with schema, validator, ledger event, and
rendered projection. Workflow conveniences remain feature or pool work until
they have a foundation invariant to defend.

## Consequences

### Positive

1. **AGENTS.md becomes a Layer-3 derived view (per `docs/governance/state-doctrine.md`).** Every foundational claim has a structural witness; drift between rendered and committed AGENTS.md fails CI; hand-authoring becomes mechanically blocked the way ledger-editing already is. Closes the inversion the operator named explicitly.

2. **The foundation/feature kind axis acquires a structural test.** "Is the invariant intent of the project's purpose, established with structural witness?" is now mechanical (does the invariant have a registry entry with a non-empty `structural_witness` array?), not a narrative judgment call. Future foundation ADRs gain a checklist and a fail-closed gate at promotion.

3. **The recurring brief↔reality drift class closes mechanically.** OBPI-0.0.29-02's `behave_coverage_waivers.json` shape, OBPI-0.0.29-01's silent precedent, the GHI #380/#406/#407 superseding chain, the GHI #381 dispatch-attestation gap all route through a single `gz brief reconcile` surface with operator-attested amendments. The pool stubs become feature-kind defenses *of* CIC-2 once this lands.

4. **Operator-bandwidth-protection at brief authoring and at Stage 1 entry.** Operators receive the reconciliation delta upfront with operator-attested amendment shapes, instead of discovering coupled-surface edits mid-Stage-4. The OEE doctrine's "agent drafts substantively, operator reviews" pattern applied at brief reconciliation time.

5. **The composition framework supports future composition targets** (skill READMEs, persona files, rule mirrors) without re-architecture. Each new composition target adds a `composition_targets` entry in the relevant invariant; the renderer pattern is reused.

6. **Ledger-of-truth doctrine extends to canon coherence.** The new event family (`composition_*` + `invariant_*` + `brief_reconcile_*`) makes drift events first-class ledger entries replayable across sessions. Audit trails for governance-surface mutations gain receipts at parity with code-execution receipts.

7. **Pool stubs gain a foundational anchor.** `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` can be authored as feature-kind ADRs that consume CIC-2 — their Alternative-C reasoning gets retroactively justified (foundation invariant exists with structural witness; these stubs are mechanical defenses of that foundation).

8. **The CMS-composition direction the operator named is mechanically begun.** Future foundation ADRs codify invariants in `.gzkit/invariants/` first; AGENTS.md re-renders. The inversion is fixed at the project's foundation layer.

9. **`gz check` becomes the single gate for canon coherence.** Operators have one command that fails closed on every canon-drift class (composition drift, brief↔reality drift) at the same surface as code-quality checks. No special invocation required.

10. **The two co-load-bearing invariants ship together with one Gate 5 ceremony per OBPI.** Foundation-kind brief-level attestation discipline applies; each OBPI gets independent witness; the ten-OBPI count is the right decomposition for ten separable invariants.

### Negative

1. **Largest-foundation ceremony in the cluster (~10 OBPIs).** Composition framework, registry, renderer, drift validator, brief schema, reconcile engine, CLI verb, pipeline gate, completion gate, plus a migration OBPI to seed AGENTS.md content into the registry, plus a doctrine refresh OBPI. Bandwidth cost is real; bounded by foundation-kind decomposition discipline (each OBPI is a separable invariant, not a fragmentation move).

2. **AGENTS.md migration (OBPI-09) is a one-shot risk.** Moving from hand-authored to rendered-from-registry means every existing claim must be analyzed, decomposed, and registered. Risk: claims that look foundational but have no structural witness (today's reality) need either a structural witness authored or downgraded to a non-foundation surface (skill, rule, runbook). Either path is significant work. **Pre-mortem scenario:** 18 months from now, this decision failed because the migration produced a registry of "placeholder structural witnesses" (validator scopes that don't actually validate, ledger events that don't actually emit) — i.e. theater of structure rather than structure. **Mitigation:** each migrated invariant requires at least one assertion-bearing test in `tests/governance/` to count as witnessed.

3. **Brief-structure schema extension is breaking.** Existing OBPI briefs use ad-hoc frontmatter shapes that won't validate against the new `obpi_brief_structure.json`. Either the schema is permissive at first (with a deprecation window) or every existing brief gets a migration pass. Foundation-kind decomposition lets this be one OBPI (OBPI-04 ships permissive mode; a future feature ADR tightens).

4. **Pool stubs need re-routing.** `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation` need their Alternative-C reasoning updated (their pool-stage rejection of foundation-kind was based on the inverted assumption this ADR fixes). Both should remain in pool until CIC-2 lands, then promote as feature-kind ADRs *that consume CIC-2*. Risk: if those stubs are promoted before CIC-2 lands (operator forgets the dependency), the inversion re-instances. **Mitigation:** OBPI-10 (doctrine refresh) explicitly documents the dependency in the pool stubs.

5. **Citation-graph density.** Every future foundation ADR references CIC-1; every brief references CIC-2 implicitly through pipeline gates. This is the same "load-bearing foundation cited everywhere" shape as ADR-0.0.18; bounded by being foundation-kind work it has earned.

6. **Reconciliation receipt-freshness adds Stage 1 + Stage 5 latency.** Every OBPI pipeline run pays the reconciliation cost twice. Real cost in seconds; bounded by the engine's decomposition-by-dimension (only re-walk dimensions whose source surface has mutated since last receipt). Acceptable per the mantra (5:1 governance-to-output ratio is the product).

7. **The composition renderer is itself code with potential for drift between specification and behavior.** **Pre-mortem:** 18 months from now the renderer silently emits invariants in a slightly different order than the registry declares, AGENTS.md drifts byte-by-byte but not semantically, drift validator alarms continuously, operators learn to ignore it. **Mitigation:** byte-deterministic rendering is REQ-01 of OBPI-02; the test suite asserts byte-identical output for every fixture registry input.

8. **OBPI brief structural schema (OBPI-04) introduces fan-out of brief-authoring complexity.** Operators authoring new briefs must now think about the structured forms of allowlist, Discovery Checklist, Verification, REQs, citations. This adds authoring overhead. **Mitigation:** `gz obpi specify` (existing skill) is extended to scaffold the structured form; operators don't hand-author the YAML.

9. **The 2am operator scenario for this ADR's failure path:** an operator on-call at 2am needs to ship an emergency fix and `gz obpi complete` refuses because the reconciliation receipt is stale. **Mitigation:** a `--accept-stale-reconciliation --reason '<text>'` escape hatch (parallel to `--accept-uncovered` for REQ coverage gate per ADR-0.0.25) records the override to the ledger as a `brief_reconcile_drift_overridden` event for later operator review. Never silent.

10. **Reversibility assessment: this is a one-way door.** Once AGENTS.md is rendered-from-registry and CI fails on drift, hand-editing AGENTS.md becomes mechanically blocked. Reversal in 12 months would require disabling the validator and re-authoring AGENTS.md by hand — significant work. Justified by the recurring failure-mode evidence: the door we're closing is one that was producing repeated drift. The asymmetry is intentional; the cost of leaving it open exceeds the cost of closing it.

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
- Baseline Selected: 6
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 10

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.37-01 — Constitutional invariant schema + registry primitive (frozen Pydantic ConstitutionalInvariant + JSON Schema mirror + first three seed invariants: CIC-1, CIC-2, foundation-ADR-registers-invariant)
- [ ] OBPI-0.0.37-02 — Composition renderer (`gz governance render --target agents-md`; deterministic byte output; `--check` mode)
- [ ] OBPI-0.0.37-03 — Composition drift validator (`gz validate --invariant-coherence`; fail-closed on drift; `composition_drift_detected` ledger event)
- [ ] OBPI-0.0.37-04 — OBPI brief structural schema (`BriefStructure` Pydantic + JSON Schema mirror; structured allowlist + REQs + Verification + citations; permissive mode with deprecation window)
- [ ] OBPI-0.0.37-05 — Brief reconciliation engine (project-tree walker; per-dimension delta computation across the five drift classes)
- [ ] OBPI-0.0.37-06 — `gz brief reconcile <OBPI-ID> [--apply]` CLI verb (operator-runnable; `brief_reconciled` ledger event; `--apply` writes operator-attested amendments)
- [ ] OBPI-0.0.37-07 — Pipeline Stage 1 fail-close gate (refuses Stage 2 entry without fresh reconciliation receipt)
- [ ] OBPI-0.0.37-08 — `gz obpi complete` fail-close gate (refuses Stage 5 completion without fresh reconciliation receipt; `--accept-stale-reconciliation --reason` escape hatch records override)
- [ ] OBPI-0.0.37-09 — AGENTS.md migration (register existing AGENTS.md content as constitutional invariants; render AGENTS.md from registry; lock the inversion in CI)
- [ ] OBPI-0.0.37-10 — Doctrine refresh (update ADR-0.0.18 kind-axis distinction; re-route pool stubs `brief-authoring-evidence-checks` and `obpi-pipeline-dispatch-attestation`; update contributing docs)

## Q&A Transcript

*Interview conducted: 2026-05-06 via `uv run gz interview adr --from /tmp/adr-0.0.37-interview.json` after a multi-turn design dialogue with the operator. Full conversation history preserved in session transcript and `.gzkit/insights/agent-insights.jsonl` (2026-05-06T10:45:00 entry — kind-axis doctrinal correction). The dialogue's two operator turns that re-shaped the design:*

*1. **Operator correction to agent's flawed routing recommendation** (verbatim):* *"A statement in what is ultimately flimsy and ephemeral - AGENTS.MD - can NOT be considered foundation. Foundation adrs must place structures and processes that guarantee gzkits behavior. I have the LOWEST amount of faith in AGENTS.md. ... If I go with A, and accepting our distinction of what constitutes a feature ('Foundation kind is reserved for app/system invariants per ADR-0.0.18; these are mechanical defenses of an invariant ... not the invariant itself'), we can't trust AGENTS.MD until a structured set of structured foundational/constitutional invariants are established that AGENTS is composed from. Leading elements of our CMS approach are in place, but not fully to my original intent. Pool is for feature, foundational is for invariant intent of the project's purpose. unfortunately, the emergent nature of this project is revealing and shaping the project as we go."*

*2. **Operator scope decision** (verbatim):* *"Wide == DO IT RIGHT"* — locking the two-invariant scope (CIC-1 composition + CIC-2 brief↔reality coherence in one ADR) over the alternatives of narrow scope or two sequenced ADRs.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/governance/test_invariants.py`, `tests/governance/test_compose.py`, `tests/governance/test_brief_reconcile.py`, `tests/commands/test_governance_render.py`, `tests/commands/test_brief_reconcile.py`, `features/constitutional_invariants.feature`, `features/brief_reconcile.feature`
- [ ] Docs: `docs/user/manpages/gz-governance.md`, `docs/user/manpages/gz-brief.md`, `docs/user/runbook.md` (new entries), `docs/governance/advisory-rules-audit.md` (new scorecard entries), `.gzkit/invariants/*.yaml` (registry seed)

## Alternatives Considered

1. **Promote ADR-pool.brief-authoring-evidence-checks as feature-kind (the agent's flawed pre-correction recommendation).** REJECTED at operator-cited reasoning: the pool stub's Alternative-C self-rejection ("foundation kind is reserved for app/system invariants per ADR-0.0.18; these are mechanical defenses of an invariant, not the invariant itself") was structurally flawed because it rested on AGENTS.md § operative-claim-4 being a trustworthy invariant. Operator's verbatim correction: *"A statement in what is ultimately flimsy and ephemeral - AGENTS.MD - can NOT be considered foundation. Foundation adrs must place structures and processes that guarantee gzkits behavior."* Promoting as feature-kind would entrench the inversion.

2. **Author CIC-1 (composition) and CIC-2 (brief↔reality) as separate sequenced foundation ADRs.** REJECTED — they're co-load-bearing: CIC-2 cannot be trusted without CIC-1's witness mechanism, and CIC-1 cannot be tested without an instance. Sequencing them across two ADR ceremonies doubles the gate ceremony with no separability gain. Foundation-kind decomposition discipline applies within one ADR via OBPI splitting.

3. **Narrow scope to brief-reconciliation only; defer composition framework to later.** REJECTED at operator's *"Wide == DO IT RIGHT"* direction — narrow scope would re-instance the inversion (brief-reconciliation invariant codified in prose without the structural-witness framework underneath it). The composition framework is the structural witness CIC-2 requires.

4. **Continue with pool stubs' "defense of existing invariant" framing.** REJECTED — the existing invariant (AGENTS.md § operative-claim-4) is itself prose without structural witness; defenses of an unwitnessed invariant inherit the unwitness. The cluster's recurring drift evidence shows the framing has produced the very failure class it claimed to defend.

5. **Hand-roll a structural witness for AGENTS.md without a registry abstraction.** REJECTED — AGENTS.md is one composition target; future composition targets (skill READMEs, persona files, rule mirrors) will follow. Registry abstraction is YAGNI-rejected only if we believe AGENTS.md is the only surface; observable evidence says otherwise (multiple vendor mirrors, multiple skill renderings, multiple persona files all asserting partial overlapping foundational content).

6. **Treat composition framework as a chore, not an ADR.** REJECTED — chores are scheduled-maintenance work against existing invariants. Establishing a new invariant (CIC-1) requires foundation-kind ceremony per ADR-0.0.18; chore-tier work cannot establish foundational invariants.

7. **Implement brief reconciliation as a `gz` validator scope only (no CLI verb, no pipeline gate).** REJECTED — a validator without operator-runnable invocation is the same failure shape as an advisor that requires manual invocation (per ADR-0.0.29 § Decision rationale #3). The CLI verb (OBPI-06) is the operator-bandwidth-protection move; the pipeline gates (OBPI-07/08) are the load-bearing mechanical defense.

8. **Allow `--accept-stale-reconciliation` only on lite-lane briefs; heavy lane is fail-closed-without-escape.** REJECTED — the 2am operator scenario applies regardless of lane. Heavy-lane bias is appropriate at attestation rigor (already enforced via foundation/heavy/security axes), not at the operational-recovery escape hatch. The escape hatch records override to ledger; the audit trail is the structural defense, not lane-based access control.

9. **AGENTS.md migration (OBPI-09) deferred to a separate ADR; this ADR ships only the framework + brief reconciliation.** REJECTED — the migration is the test of the framework. Without a real composition target seeded into the registry and rendered to AGENTS.md, CIC-1 ships as theater (registry exists but no composition runs through it). The migration validates that the framework actually works at production scale.

10. **Constitutional invariant registry as a single JSON file rather than per-invariant YAML files.** REJECTED — per-invariant files give git history its natural granularity (one commit per invariant amendment, not one commit that touches every invariant). YAML preferred over JSON for human-authored governance content; existing precedent in `.gzkit/personas/` and `.gzkit/skills/`.

11. **Composition rendering driven by an LLM rather than deterministic templating.** REJECTED — non-determinism at the canon layer is the failure mode this ADR exists to close. Byte-deterministic rendering is the structural witness; LLM rendering would introduce vibing-as-rendering, the canon-layer instance of the cluster's mantra-named failure class.

12. **Reconciliation receipt-freshness defined by wall-clock TTL (e.g. 1 hour) rather than mutation-timestamp comparison.** REJECTED — wall-clock TTL produces false-positive staleness on briefs whose allowlist domain has not mutated, and false-negative freshness on briefs whose allowlist domain mutated 30 seconds after a receipt was emitted. Mutation-timestamp comparison is the semantically-correct freshness test; TTL is the easier-but-wrong proxy.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.37 | Pending | | | |
