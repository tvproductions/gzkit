---
id: ADR-0.0.28-complexity-threshold-doctrine
status: Validated
kind: foundation
semver: 0.0.28
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-25
---

# ADR-0.0.28: Complexity Threshold Doctrine

## Post-closeout amendment (GHI #426)

**The threshold data was lifted from regex-parsed markdown to a structured JSON sibling on 2026-05-09.** The canonical surface is now a pair under `.gzkit/rules/`:

- `complexity-thresholds.json` — runtime data source-of-truth (per-metric bands + citation tuple); loaded by `gzkit.complexity.thresholds.load_threshold_table` via `json.load()` + Pydantic validation.
- `complexity-thresholds.md` — doctrine narrative (Invariant, Trigger-Semantic Vocabulary, Bootstrap carve-out, Operator-amendable mapping protocol); links to the JSON.

The narrative below referring to *"`.gzkit/rules/complexity-thresholds.md`"* as the threshold table refers to the pair; the runtime contract (validator, advisor, hooks) consumes the JSON. The split closes the structural defect in GHI #426 ("deterministic config should be JSON, not regex-parsed markdown") without amending any doctrinal commitment in this ADR.

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats the threshold table as foundation doctrine cited from corpus measurement, not as configuration to be tuned by intuition. Distinguishes the trigger-semantic vocabulary (block / warn / advise — fixed enum doctrine) from the per-metric mapping (operator-amendable doctrine through the doctrine-amendment-protocol pool stub). Reads the OBPI-0.0.27-05 citation contract as binding for every cited boundary — percentile-of-corpus AND absolute-number-at-that-percentile, never one without the other. Refuses graceful degradation: a stripped install must not silently produce a different verdict than a full install (the Q4 rejection from ADR-0.0.27 § Decision is inherited here without amendment).

This ADR is the second foundation in the four-ADR complexity-doctrine cluster (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30). It consumes ADR-0.0.27's distilled-characteristics document via the citation tuple from OBPI-0.0.27-05, produces the `ThresholdTable` data contract that ADR-0.0.29 (advisor) and ADR-0.0.30 (authoring-guidance) bind against, and gates the cluster's downstream surfaces via `gz validate --complexity-thresholds` integrated into `gz check`. The mantra binds the choice toward one canonical home for thresholds; the Q4 rejection from ADR-0.0.27 binds the choice toward fail-closed validation; the OBPI-0.0.27-05 citation contract binds the choice toward percentile + absolute pairing for refresh portability.

## Why foundation tier?

Without this ADR, complexity thresholds drift silently — the advisor's band cutoffs live in code as magic numbers, the exemplar-corpus link is informal, and a threshold change can land without a witness to the calibration that justifies it.

This ADR authors a port: the complexity-threshold rule file contract (versioned, validator-checked, exemplar-grounded) that every advisor invocation reads against.

## Intent

gzkit's complexity-doctrine cluster needs a single canonical threshold table that maps per-metric numeric boundaries to trigger semantics (block / warn / advise). Without ADR-0.0.28, the threshold values would proliferate across xenon configuration flags, advisor rule tables (ADR-0.0.29), authoring-guidance prose (ADR-0.0.30), and the existing complexity-reduction-xenon chore — drifting independently each time any one of them is amended. The MAKE LLM STOCHASTIC VIBES INERT mantra forbids that drift class structurally; situational thresholds are doctrine drift by another name (the Q4 graceful-degradation rejection from ADR-0.0.27 § Decision applies here too). This ADR consumes ADR-0.0.27's distilled-characteristics document via the OBPI-0.0.27-05 citation contract and produces the binding threshold table that all downstream complexity surfaces honor.

The distinction from ADR-0.0.27: ADR-0.0.27 codifies how thresholds are derived (corpus measurement → distillation → percentile-based boundaries with doctrinal-frame attribution); ADR-0.0.28 codifies the threshold table itself + the trigger-semantic mapping (which percentile bands fire which actions). The two ADRs are deliberately separable — corpus refresh shifts the threshold table; trigger semantics remain stable across refresh because they are operator-amendable doctrine, not corpus output.

The trigger-semantic vocabulary (block / warn / advise) is itself doctrine, not configuration. Three actions, one mapping per metric per band: a percentile crossing the `block` band fails xenon-as-gate (closing the build); a percentile crossing the `warn` band surfaces an advisor recommendation (ADR-0.0.29); a percentile crossing the `advise` band feeds the authoring-guidance surface (ADR-0.0.30) without blocking. Operator-amendable mappings are recorded against the doctrine-amendment-protocol pool stub (forward-referenced from ADR-0.0.27 OBPI-02).

## Decision

Codify the canonical threshold table at `.gzkit/rules/complexity-thresholds.md` derived from the distilled-characteristics document via OBPI-0.0.27-05's citation tuple form, plus a frozen `ThresholdTable` Pydantic loader at `src/gzkit/complexity/thresholds.py`, plus a `gz validate --complexity-thresholds` validator that fail-closes on unmapped bands or missing percentile + absolute pairings.

**Rationale (numbered, binding):**

1. The threshold table lives in `.gzkit/rules/`, not `data/`, **because** doctrine belongs in rules (vendor-mirrored to `.claude/`, `.agents/`, `.github/`) and data files do not get mirrored — the rule-mirror surface is the structural defense against agent-pattern-matching against the wrong threshold values from training memory.
2. The trigger-semantic vocabulary is fixed at exactly three values (`block`, `warn`, `advise`), **because** the three values map cleanly to the three downstream consumer surfaces (xenon-as-gate, advisor, authoring-guidance) and a fourth state with no consumer is the foundation-doctrine version of dead code (the ADR-0.0.27 § Alternatives Considered Q4 graceful-degradation rejection is the inherited justification).
3. Every metric MUST carry a `block` band, **because** a threshold without a blocking band is prose, not a threshold — the schema-level requirement closes the "threshold that cannot fail" failure class named in ADR-0.0.27 § Negative #4.
4. Every band carries the percentile + absolute pairing, **because** OBPI-0.0.27-05's citation contract names this as the load-bearing portability invariant: corpus refresh shifts absolute numbers but preserves percentile semantics, so the table remains readable across refresh cycles. The reasoning is inherited verbatim, not relitigated.
5. The validator integrates into `gz validate --all` and `gz check`, **because** a validator that exists but never fires at gate time is the canonical "validator drift" failure class — the rationale is the same shape as ADR-0.0.27 OBPI-07's link-integrity validator, applied at the threshold-table layer.
6. Three OBPIs is the right size, **because** each codifies one distinct invariant (rule = doctrine surface, loader = runtime contract, validator = gate); bundling under one OBPI obscures the dependency boundary and over-fragmenting (one OBPI per metric) produces ceremony without invariant addition. The justification mirrors ADR-0.0.27's seven-OBPI decomposition reasoning at smaller scale.

The cluster's deliberate mirror-shape: this ADR follows the same exemplar structure as ADR-0.0.27 (rule + loader + validator) so that the precedent established at the corpus-doctrine layer carries forward to the threshold-doctrine layer; the precedent at this layer is the exemplar ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance bind against in turn.

**The invariant (canonical statement):** gzkit publishes one canonical threshold table whose every entry is a (metric, percentile-band, absolute-number, trigger-semantic) tuple cited from the current distilled-characteristics document. The trigger-semantic vocabulary is fixed (block / warn / advise); the mapping per metric per band is operator-amendable doctrine. Downstream surfaces (xenon-as-gate, advisor, authoring-guidance) consume the table; none of them owns its own thresholds.

**Threshold table shape (binding):** Each metric in `.gzkit/rules/complexity-thresholds.md` lists three rows minimum: an `advise` band, a `warn` band, and a `block` band, each expressed as `(corpus_percentile, absolute_number_at_that_percentile, trigger_semantic)`. Example: cyclomatic complexity at OBPI-0.0.27-04's first distillation might map `(p75, CC=8, advise)`, `(p90, CC=12, warn)`, `(p95, CC=18, block)`. The percentile + absolute pairing is mandatory per the citation contract — corpus refresh updates absolute numbers but preserves percentile semantics, so the table remains readable across refresh cycles.

**Trigger-semantic vocabulary (binding):** Exactly three values are accepted by the schema:
- `block` — the metric crossing this band fails the gate (xenon-as-gate exit 3); the build does not pass
- `warn` — the metric crossing this band surfaces an advisor recommendation; build proceeds, advisor diagnosis lands in the developer's session
- `advise` — the metric crossing this band feeds the authoring-guidance surface only; no advisor invocation, no build effect

A metric MUST have a `block` band (a metric that cannot fail the gate is not a real threshold). `warn` and `advise` bands are optional but recommended for full coverage.

**Mechanical surfaces:**
- `.gzkit/rules/complexity-thresholds.md` (new): canonical threshold table; cites the distilled-characteristics document via OBPI-0.0.27-05's tuple. Body-level rule-version marker per skill-surface-sync rules. Mirrored to vendor surfaces.
- `src/gzkit/complexity/thresholds.py` (new): `ThresholdTable` and `ThresholdBand` Pydantic models with `ConfigDict(frozen=True, extra='forbid')`. Loader parses the rule body into the model. Lookup methods: `band_for(metric, value) -> Trigger` (returns the highest-severity band a value crosses), `bands_for_metric(metric) -> list[ThresholdBand]`.
- `src/gzkit/schemas/complexity_thresholds.json` (new): JSON Schema mirror enforcing the trigger-semantic enum and the percentile + absolute pairing.
- `src/gzkit/governance/trust_audits.py`: extend `validate_complexity_thresholds` for the `gz validate --complexity-thresholds` scope. Fail-closes on: missing `block` band per metric, missing percentile + absolute pairing, trigger-semantic outside the enum, citation tuple that does not parse.
- `src/gzkit/cli/parser_artifacts.py` + `gz validate` dispatcher: register the `--complexity-thresholds` flag.
- `docs/user/manpages/gz-validate.md`: manpage section for the new flag.
- `docs/user/runbook.md`: runbook entry under "Complexity doctrine surfaces".
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.

**Three OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.28-01 — Threshold table rule file (`.gzkit/rules/complexity-thresholds.md`):** Author the canonical rule body codifying per-metric (advise / warn / block) band rows, the trigger-semantic vocabulary, the percentile + absolute pairing requirement, and the citation form pointing at the OBPI-0.0.27-04 distilled-characteristics document. Vendor mirrors via `gz agent sync control-surfaces`. Advisory-rules-audit.md scorecard entry. Foundation-kind brief-level Gate 5 attestation per ADR-0.0.18.

**OBPI-0.0.28-02 — `ThresholdTable` Pydantic loader (`src/gzkit/complexity/thresholds.py`):** Implement frozen `ThresholdBand` and `ThresholdTable` models with `ConfigDict(frozen=True, extra='forbid')`. Loader parses the rule body and yields the model. Lookup methods return the highest-severity band a value crosses. JSON Schema mirror enforces the trigger-semantic enum and percentile + absolute pairing. TDD coverage of band lookup, percentile portability across corpus refresh, and rejection of malformed entries.

**OBPI-0.0.28-03 — `gz validate --complexity-thresholds` validator:** `validate_complexity_thresholds` in `src/gzkit/governance/trust_audits.py`; CLI flag registration; fail-closes (exit 3) on unmapped bands, missing `block` band per metric, missing percentile + absolute pairing, trigger-semantic outside the enum, or unparseable citation tuple. Integrates into `gz validate --all` and `gz check`. Manpage and runbook updates land in the same patch per the gate5-runbook-code-covenant.

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-03. OBPI-01's rule file is the contract OBPI-02's loader parses; OBPI-03's validator consumes both.

**Lane: Heavy.** New canonical rule file is a doctrine surface; new Pydantic data contract is a runtime contract consumed by ADR-0.0.29 and ADR-0.0.30; new CLI flag is a contract change per `.gzkit/rules/cli.md`. Foundation-kind rigor stacks on top per ADR-0.0.18 — brief-level Gate 5 attestation regardless of lane.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the corpus selection methodology — that is ADR-0.0.27's scope.
- Does NOT author the complexity advisor or its CLI surface — that is ADR-0.0.29's scope.
- Does NOT author the authoring-time guidance surface — that is ADR-0.0.30's scope.
- Does NOT modify the existing `complexity-reduction-xenon` chore — that chore consumes the threshold table after this ADR lands but the chore-strengthening work is tracked separately.
- Does NOT specify the trigger-semantic actions' implementation (xenon invocation, advisor invocation, authoring-guidance integration) — those are downstream ADR concerns.
- Does NOT vendor or reimplement xenon — xenon-as-gate is the chosen substrate; the table is the data contract xenon consumes.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The canonical threshold table validates: every metric carries a block band with percentile + absolute pairing and an in-enum trigger semantic. | uv run gz validate --complexity-thresholds | 0 |

## Consequences

### Positive

1. **Single canonical threshold home prevents drift across xenon, advisor, authoring-guidance, and the chore.** Without this ADR, four surfaces would each carry their own threshold values and drift independently. The mantra ("every option is framed by which choice leaves the smallest surface for vibing to leak through") binds the choice toward one canonical table.

2. **Percentile + absolute pairing makes the table portable across corpus refresh.** OBPI-0.0.27-05's citation contract is the load-bearing portability invariant; ADR-0.0.28 inherits it. Corpus refresh shifts absolute numbers but preserves percentile semantics; the table remains readable.

3. **Trigger-semantic vocabulary (block / warn / advise) is fixed enum doctrine, not configuration.** Three values, foundation-kind. Operators amend the per-metric mapping (which percentile band gets which trigger), not the vocabulary.

4. **Mandatory `block` band per metric closes the "threshold that cannot fail" failure class.** A threshold without a block band is not a threshold; it's prose. The schema enforces a `block` band on every metric.

5. **`gz validate --complexity-thresholds` integrates into `gz check` and `gz validate --all`.** Pre-commit and pre-merge gates fire automatically; threshold drift surfaces at gate time, not at midnight when the operator is debugging an advisor diagnosis.

6. **Foundation-kind brief-level Gate 5 across three OBPIs.** Each OBPI codifies one invariant (rule file, loader, validator); each invariant gets independent witness per ADR-0.0.18.

7. **The `ThresholdTable` model is the binding consumed by ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance.** Both downstream ADRs receive a frozen Pydantic surface, not a JSON file they each parse separately. The single loader is the structural defense against parser-divergence drift.

8. **The validator surfaces unmapped bands at gate time.** When OBPI-0.0.27-04 distillation produces new percentile boundaries, the threshold table must be updated to map them; if any new band is unmapped, `gz check` fails closed. The rebinding work cannot silently lag behind corpus refresh.

9. **Operator-amendable mapping records flow through the doctrine-amendment-protocol pool stub.** When the operator amends a `(metric, band, trigger)` mapping, the change is witnessed via the protocol — not silent edits to a config file.

10. **Three OBPIs is the right size — not bundled, not over-fragmented.** Each OBPI is a distinct invariant: the rule file is the doctrine surface, the loader is the runtime contract, the validator is the gate. Bundling them under one OBPI obscures the dependency boundary; over-fragmenting (e.g. one OBPI per metric) produces ceremony without invariant addition.

### Negative

1. **The threshold table needs to be re-amended whenever OBPI-0.0.27-04 distillation produces new percentile boundaries.** This is the citation-graph density consequence ADR-0.0.27 § Negative #7 named, surfaced as concrete editorial cost in 0.0.28. Mitigated by the validator: `gz check` fails closed on unmapped bands, so the rebinding work is forced rather than allowed to drift.

2. **Three OBPIs of foundation-kind ceremony for what could be a single config-file PR.** The mantra position is that ceremony is the deliverable; this consequence is the cost paid for that position. The alternative (treating thresholds as configuration) is the structural drift class this ADR exists to close.

3. **Operator-amendable mapping creates a per-amendment Gate 5 walkthrough.** Every (metric, band, trigger) change is doctrine, not configuration; each amendment fires brief-level Gate 5 per ADR-0.0.18. Attestation-fatigue risk per ADR-0.0.27 § Negative #5 applies — pool stub `ADR-pool.attestation-quality-measurement` is the forward-reference if it materializes.

4. **Mandatory `block` band per metric may force operators to set blocking thresholds before they have empirical confidence in the band.** First-distillation cold-start (per ADR-0.0.27 § Negative #9) means OBPI-0.0.28-01's first rule body must pick block-band absolute numbers from a single distillation pass with no diff history. Mitigation: the band can be set conservatively (e.g. `block` at p99 rather than p95) and tightened in subsequent distillations.

5. **The trigger-semantic vocabulary is fixed at three values.** Operators wanting a fourth state (e.g. `info` — surface but do not record) must amend ADR-0.0.28 itself, not the rule body. This is deliberate (the vocabulary is foundation, not configuration) but creates a heavier amendment path than a config file.

6. **Citation graph: ADR-0.0.28 cites ADR-0.0.27 OBPI-04 and OBPI-05; ADR-0.0.29 and ADR-0.0.30 will cite ADR-0.0.28; the link-integrity validator (OBPI-0.0.27-07) is the structural defense.** Citation density is real and acknowledged in the negative-consequences chain spanning the cluster.

7. **The validator integrates into `gz check`, increasing pre-commit / pre-merge time.** Real cost in seconds; bounded by the table's small size (one parse + one schema check + one citation parse per metric). Acceptable per the mantra (5:1 governance-to-output ratio is the product).

8. **A frozen Pydantic surface as the runtime contract creates a versioning surface.** When ADR-0.0.29 / ADR-0.0.30 land, they will each have a coupling to `ThresholdTable`. A future amendment to the model shape (e.g. adding a fourth field) requires coordinated work across the three downstream ADRs. Mitigation: the doctrine-amendment-protocol pool stub is the canonical home for that work.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 0
- Lineage: 0
- Dimension Total: 6
- Baseline Range: 3-3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.28-01 — Threshold table rule file (`.gzkit/rules/complexity-thresholds.md`) — codifies per-metric (advise / warn / block) bands, trigger-semantic vocabulary, percentile + absolute pairing, citation form pointing at OBPI-0.0.27-04 distilled-characteristics; vendor mirrors; advisory-rules-audit.md scorecard entry
- [ ] OBPI-0.0.28-02 — `ThresholdTable` Pydantic loader (`src/gzkit/complexity/thresholds.py`) — frozen `ThresholdBand` / `ThresholdTable` models; rule-body parser; band-lookup methods; JSON Schema mirror at `src/gzkit/schemas/complexity_thresholds.json`
- [ ] OBPI-0.0.28-03 — `gz validate --complexity-thresholds` validator (`src/gzkit/governance/trust_audits.py`) — fail-closes on unmapped bands, missing block band, missing percentile + absolute pairing, trigger-semantic outside enum, unparseable citation; integrates into `gz validate --all` and `gz check`; manpage + runbook updates

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-04-25T15:10:59.204746*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.28

### Q: What is the title of this ADR?

**A:** Complexity Threshold Doctrine

### Q: What is the semantic version?

**A:** 0.0.28

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's complexity-doctrine cluster needs a single canonical threshold table that maps per-metric numeric boundaries to trigger semantics (block / warn / advise). Without ADR-0.0.28, the threshold values would proliferate across xenon configuration flags, advisor rule tables (ADR-0.0.29), authoring-guidance prose (ADR-0.0.30), and the existing complexity-reduction-xenon chore — drifting independently each time any one of them is amended. The MAKE LLM STOCHASTIC VIBES INERT mantra forbids that drift class structurally; situational thresholds are doctrine drift by another name (the Q4 graceful-degradation rejection from ADR-0.0.27 § Decision applies here too). This ADR consumes ADR-0.0.27's distilled-characteristics document via the OBPI-0.0.27-05 citation contract and produces the binding threshold table that all downstream complexity surfaces honor.

The distinction from ADR-0.0.27: ADR-0.0.27 codifies how thresholds are derived (corpus measurement → distillation → percentile-based boundaries with doctrinal-frame attribution); ADR-0.0.28 codifies the threshold table itself + the trigger-semantic mapping (which percentile bands fire which actions). The two ADRs are deliberately separable — corpus refresh shifts the threshold table; trigger semantics remain stable across refresh because they are operator-amendable doctrine, not corpus output.

The trigger-semantic vocabulary (block / warn / advise) is itself doctrine, not configuration. Three actions, one mapping per metric per band: a percentile crossing the `block` band fails xenon-as-gate (closing the build); a percentile crossing the `warn` band surfaces an advisor recommendation (ADR-0.0.29); a percentile crossing the `advise` band feeds the authoring-guidance surface (ADR-0.0.30) without blocking. Operator-amendable mappings are recorded against the doctrine-amendment-protocol pool stub (forward-referenced from ADR-0.0.27 OBPI-02).

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Codify the canonical threshold table at `.gzkit/rules/complexity-thresholds.md` derived from the distilled-characteristics document via OBPI-0.0.27-05's citation tuple form, plus a frozen `ThresholdTable` Pydantic loader at `src/gzkit/complexity/thresholds.py`, plus a `gz validate --complexity-thresholds` validator that fail-closes on unmapped bands or missing percentile + absolute pairings.

**The invariant (canonical statement):** gzkit publishes one canonical threshold table whose every entry is a (metric, percentile-band, absolute-number, trigger-semantic) tuple cited from the current distilled-characteristics document. The trigger-semantic vocabulary is fixed (block / warn / advise); the mapping per metric per band is operator-amendable doctrine. Downstream surfaces (xenon-as-gate, advisor, authoring-guidance) consume the table; none of them owns its own thresholds.

**Threshold table shape (binding):** Each metric in `.gzkit/rules/complexity-thresholds.md` lists three rows minimum: an `advise` band, a `warn` band, and a `block` band, each expressed as `(corpus_percentile, absolute_number_at_that_percentile, trigger_semantic)`. Example: cyclomatic complexity at OBPI-0.0.27-04's first distillation might map `(p75, CC=8, advise)`, `(p90, CC=12, warn)`, `(p95, CC=18, block)`. The percentile + absolute pairing is mandatory per the citation contract — corpus refresh updates absolute numbers but preserves percentile semantics, so the table remains readable across refresh cycles.

**Trigger-semantic vocabulary (binding):** Exactly three values are accepted by the schema:
- `block` — the metric crossing this band fails the gate (xenon-as-gate exit 3); the build does not pass
- `warn` — the metric crossing this band surfaces an advisor recommendation; build proceeds, advisor diagnosis lands in the developer's session
- `advise` — the metric crossing this band feeds the authoring-guidance surface only; no advisor invocation, no build effect

A metric MUST have a `block` band (a metric that cannot fail the gate is not a real threshold). `warn` and `advise` bands are optional but recommended for full coverage.

**Mechanical surfaces:**
- `.gzkit/rules/complexity-thresholds.md` (new): canonical threshold table; cites the distilled-characteristics document via OBPI-0.0.27-05's tuple. Body-level rule-version marker per skill-surface-sync rules. Mirrored to vendor surfaces.
- `src/gzkit/complexity/thresholds.py` (new): `ThresholdTable` and `ThresholdBand` Pydantic models with `ConfigDict(frozen=True, extra='forbid')`. Loader parses the rule body into the model. Lookup methods: `band_for(metric, value) -> Trigger` (returns the highest-severity band a value crosses), `bands_for_metric(metric) -> list[ThresholdBand]`.
- `src/gzkit/schemas/complexity_thresholds.json` (new): JSON Schema mirror enforcing the trigger-semantic enum and the percentile + absolute pairing.
- `src/gzkit/governance/trust_audits.py`: extend `validate_complexity_thresholds` for the `gz validate --complexity-thresholds` scope. Fail-closes on: missing `block` band per metric, missing percentile + absolute pairing, trigger-semantic outside the enum, citation tuple that does not parse.
- `src/gzkit/cli/parser_artifacts.py` + `gz validate` dispatcher: register the `--complexity-thresholds` flag.
- `docs/user/manpages/gz-validate.md`: manpage section for the new flag.
- `docs/user/runbook.md`: runbook entry under "Complexity doctrine surfaces".
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.

**Three OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.28-01 — Threshold table rule file (`.gzkit/rules/complexity-thresholds.md`):** Author the canonical rule body codifying per-metric (advise / warn / block) band rows, the trigger-semantic vocabulary, the percentile + absolute pairing requirement, and the citation form pointing at the OBPI-0.0.27-04 distilled-characteristics document. Vendor mirrors via `gz agent sync control-surfaces`. Advisory-rules-audit.md scorecard entry. Foundation-kind brief-level Gate 5 attestation per ADR-0.0.18.

**OBPI-0.0.28-02 — `ThresholdTable` Pydantic loader (`src/gzkit/complexity/thresholds.py`):** Implement frozen `ThresholdBand` and `ThresholdTable` models with `ConfigDict(frozen=True, extra='forbid')`. Loader parses the rule body and yields the model. Lookup methods return the highest-severity band a value crosses. JSON Schema mirror enforces the trigger-semantic enum and percentile + absolute pairing. TDD coverage of band lookup, percentile portability across corpus refresh, and rejection of malformed entries.

**OBPI-0.0.28-03 — `gz validate --complexity-thresholds` validator:** `validate_complexity_thresholds` in `src/gzkit/governance/trust_audits.py`; CLI flag registration; fail-closes (exit 3) on unmapped bands, missing `block` band per metric, missing percentile + absolute pairing, trigger-semantic outside the enum, or unparseable citation tuple. Integrates into `gz validate --all` and `gz check`. Manpage and runbook updates land in the same patch per the gate5-runbook-code-covenant.

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-03. OBPI-01's rule file is the contract OBPI-02's loader parses; OBPI-03's validator consumes both.

**Lane: Heavy.** New canonical rule file is a doctrine surface; new Pydantic data contract is a runtime contract consumed by ADR-0.0.29 and ADR-0.0.30; new CLI flag is a contract change per `.gzkit/rules/cli.md`. Foundation-kind rigor stacks on top per ADR-0.0.18 — brief-level Gate 5 attestation regardless of lane.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the corpus selection methodology — that is ADR-0.0.27's scope.
- Does NOT author the complexity advisor or its CLI surface — that is ADR-0.0.29's scope.
- Does NOT author the authoring-time guidance surface — that is ADR-0.0.30's scope.
- Does NOT modify the existing `complexity-reduction-xenon` chore — that chore consumes the threshold table after this ADR lands but the chore-strengthening work is tracked separately.
- Does NOT specify the trigger-semantic actions' implementation (xenon invocation, advisor invocation, authoring-guidance integration) — those are downstream ADR concerns.
- Does NOT vendor or reimplement xenon — xenon-as-gate is the chosen substrate; the table is the data contract xenon consumes.

### Q: What good things result from this decision? List benefits.

**A:** 1. **Single canonical threshold home prevents drift across xenon, advisor, authoring-guidance, and the chore.** Without this ADR, four surfaces would each carry their own threshold values and drift independently. The mantra ("every option is framed by which choice leaves the smallest surface for vibing to leak through") binds the choice toward one canonical table.

2. **Percentile + absolute pairing makes the table portable across corpus refresh.** OBPI-0.0.27-05's citation contract is the load-bearing portability invariant; ADR-0.0.28 inherits it. Corpus refresh shifts absolute numbers but preserves percentile semantics; the table remains readable.

3. **Trigger-semantic vocabulary (block / warn / advise) is fixed enum doctrine, not configuration.** Three values, foundation-kind. Operators amend the per-metric mapping (which percentile band gets which trigger), not the vocabulary.

4. **Mandatory `block` band per metric closes the "threshold that cannot fail" failure class.** A threshold without a block band is not a threshold; it's prose. The schema enforces a `block` band on every metric.

5. **`gz validate --complexity-thresholds` integrates into `gz check` and `gz validate --all`.** Pre-commit and pre-merge gates fire automatically; threshold drift surfaces at gate time, not at midnight when the operator is debugging an advisor diagnosis.

6. **Foundation-kind brief-level Gate 5 across three OBPIs.** Each OBPI codifies one invariant (rule file, loader, validator); each invariant gets independent witness per ADR-0.0.18.

7. **The `ThresholdTable` model is the binding consumed by ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance.** Both downstream ADRs receive a frozen Pydantic surface, not a JSON file they each parse separately. The single loader is the structural defense against parser-divergence drift.

8. **The validator surfaces unmapped bands at gate time.** When OBPI-0.0.27-04 distillation produces new percentile boundaries, the threshold table must be updated to map them; if any new band is unmapped, `gz check` fails closed. The rebinding work cannot silently lag behind corpus refresh.

9. **Operator-amendable mapping records flow through the doctrine-amendment-protocol pool stub.** When the operator amends a `(metric, band, trigger)` mapping, the change is witnessed via the protocol — not silent edits to a config file.

10. **Three OBPIs is the right size — not bundled, not over-fragmented.** Each OBPI is a distinct invariant: the rule file is the doctrine surface, the loader is the runtime contract, the validator is the gate. Bundling them under one OBPI obscures the dependency boundary; over-fragmenting (e.g. one OBPI per metric) produces ceremony without invariant addition.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **The threshold table needs to be re-amended whenever OBPI-0.0.27-04 distillation produces new percentile boundaries.** This is the citation-graph density consequence ADR-0.0.27 § Negative #7 named, surfaced as concrete editorial cost in 0.0.28. Mitigated by the validator: `gz check` fails closed on unmapped bands, so the rebinding work is forced rather than allowed to drift.

2. **Three OBPIs of foundation-kind ceremony for what could be a single config-file PR.** The mantra position is that ceremony is the deliverable; this consequence is the cost paid for that position. The alternative (treating thresholds as configuration) is the structural drift class this ADR exists to close.

3. **Operator-amendable mapping creates a per-amendment Gate 5 walkthrough.** Every (metric, band, trigger) change is doctrine, not configuration; each amendment fires brief-level Gate 5 per ADR-0.0.18. Attestation-fatigue risk per ADR-0.0.27 § Negative #5 applies — pool stub `ADR-pool.attestation-quality-measurement` is the forward-reference if it materializes.

4. **Mandatory `block` band per metric may force operators to set blocking thresholds before they have empirical confidence in the band.** First-distillation cold-start (per ADR-0.0.27 § Negative #9) means OBPI-0.0.28-01's first rule body must pick block-band absolute numbers from a single distillation pass with no diff history. Mitigation: the band can be set conservatively (e.g. `block` at p99 rather than p95) and tightened in subsequent distillations.

5. **The trigger-semantic vocabulary is fixed at three values.** Operators wanting a fourth state (e.g. `info` — surface but do not record) must amend ADR-0.0.28 itself, not the rule body. This is deliberate (the vocabulary is foundation, not configuration) but creates a heavier amendment path than a config file.

6. **Citation graph: ADR-0.0.28 cites ADR-0.0.27 OBPI-04 and OBPI-05; ADR-0.0.29 and ADR-0.0.30 will cite ADR-0.0.28; the link-integrity validator (OBPI-0.0.27-07) is the structural defense.** Citation density is real and acknowledged in the negative-consequences chain spanning the cluster.

7. **The validator integrates into `gz check`, increasing pre-commit / pre-merge time.** Real cost in seconds; bounded by the table's small size (one parse + one schema check + one citation parse per metric). Acceptable per the mantra (5:1 governance-to-output ratio is the product).

8. **A frozen Pydantic surface as the runtime contract creates a versioning surface.** When ADR-0.0.29 / ADR-0.0.30 land, they will each have a coupling to `ThresholdTable`. A future amendment to the model shape (e.g. adding a fourth field) requires coordinated work across the three downstream ADRs. Mitigation: the doctrine-amendment-protocol pool stub is the canonical home for that work.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Threshold table rule file (`.gzkit/rules/complexity-thresholds.md`) — codifies per-metric (advise / warn / block) bands, trigger-semantic vocabulary, percentile + absolute pairing, citation form pointing at OBPI-0.0.27-04 distilled-characteristics; vendor mirrors; advisory-rules-audit.md scorecard entry
2. `ThresholdTable` Pydantic loader (`src/gzkit/complexity/thresholds.py`) — frozen `ThresholdBand` / `ThresholdTable` models; rule-body parser; band-lookup methods; JSON Schema mirror at `src/gzkit/schemas/complexity_thresholds.json`
3. `gz validate --complexity-thresholds` validator (`src/gzkit/governance/trust_audits.py`) — fail-closes on unmapped bands, missing block band, missing percentile + absolute pairing, trigger-semantic outside enum, unparseable citation; integrates into `gz validate --all` and `gz check`; manpage + runbook updates

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Embed thresholds in xenon configuration only (no canonical rule file).** REJECTED: violates the single-canonical-home invariant; xenon configuration is consumed only by xenon-as-gate, leaving advisor (ADR-0.0.29) and authoring-guidance (ADR-0.0.30) to maintain their own threshold copies and drift independently. The cluster's whole point is to prevent that drift class.

2. **Embed thresholds inline in `.gzkit/rules/complexity-doctrine.md` (ADR-0.0.27's rule).** REJECTED: bundles two distinct invariants (corpus methodology vs. trigger-semantic mapping) under one foundation-kind brief; obscures the citation graph; produces a rule body whose amendment ceremony is harder to scope (corpus methodology changes annually; trigger mapping changes per-distillation). Two rule files, two attestation surfaces, is the correct decomposition.

3. **Make the threshold table data (`data/complexity_thresholds.json`) rather than rule body (`.gzkit/rules/...`).** REJECTED: data files do not get vendor-mirrored to `.claude/`, `.agents/`, `.github/`; the rule-mirror surface is the structural defense against agent-pattern-matching against the wrong threshold values from training memory. Doctrine belongs in rules; data belongs in `data/`.

4. **Two trigger-semantic values (block / warn) instead of three.** REJECTED: collapses the authoring-guidance surface (ADR-0.0.30) into the advisor surface (ADR-0.0.29) by losing the `advise` distinction; the operator-bandwidth-protection benefit of `advise` (no advisor session, just authoring-time hint) is lost. The three-value vocabulary maps cleanly to the three downstream consumer surfaces.

5. **Four trigger-semantic values (block / warn / advise / info).** REJECTED: introduces a state with no consumer surface; `info` is what `advise` already does at the lightest end of the spectrum. Adding values without a consumer surface is the foundation-doctrine version of dead code.

6. **Operator-defined trigger-semantic vocabulary (no fixed enum).** REJECTED: situational vocabulary is doctrine drift by another name (the Q4 graceful-degradation rejection from ADR-0.0.27 applies). The vocabulary must be foundation-kind for downstream ADRs to bind against it.

7. **Optional `block` band per metric.** REJECTED: a metric without a `block` band is prose, not a threshold. The schema-level requirement closes the "threshold that cannot fail" failure class.

8. **Single-OBPI ADR (rule + loader + validator under one brief).** REJECTED: bundles three distinct invariants under one Gate 5 witness; the rule is the doctrine surface, the loader is the runtime contract, the validator is the gate — three separable invariants per the cluster's decomposition discipline.

9. **Five-OBPI ADR (per-metric OBPIs).** REJECTED: produces ceremony without invariant addition; the per-metric mappings are doctrine content the rule body carries, not separable invariants.

10. **No validator (rely on operator discipline to keep the table consistent).** REJECTED: the validator is the structural defense against silent threshold drift across corpus refresh; without it, an unmapped band introduced by a new distillation surfaces only at the next operator session, possibly months later. Fail-closed at gate time is the load-bearing closing invariant.

11. **Use a generic `gz validate --documents` extension instead of a dedicated `--complexity-thresholds` flag.** REJECTED: aggregating cluster-specific validation into the generic documents flag dilutes the operator-facing diagnostic message ("validation failed" vs. "complexity threshold table has unmapped band at metric X"). The dedicated flag is the load-bearing diagnostic surface.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Embed thresholds in xenon configuration only (no canonical rule file).** REJECTED: violates the single-canonical-home invariant; xenon configuration is consumed only by xenon-as-gate, leaving advisor (ADR-0.0.29) and authoring-guidance (ADR-0.0.30) to maintain their own threshold copies and drift independently. The cluster's whole point is to prevent that drift class.

2. **Embed thresholds inline in `.gzkit/rules/complexity-doctrine.md` (ADR-0.0.27's rule).** REJECTED: bundles two distinct invariants (corpus methodology vs. trigger-semantic mapping) under one foundation-kind brief; obscures the citation graph; produces a rule body whose amendment ceremony is harder to scope (corpus methodology changes annually; trigger mapping changes per-distillation). Two rule files, two attestation surfaces, is the correct decomposition.

3. **Make the threshold table data (`data/complexity_thresholds.json`) rather than rule body (`.gzkit/rules/...`).** REJECTED: data files do not get vendor-mirrored to `.claude/`, `.agents/`, `.github/`; the rule-mirror surface is the structural defense against agent-pattern-matching against the wrong threshold values from training memory. Doctrine belongs in rules; data belongs in `data/`.

4. **Two trigger-semantic values (block / warn) instead of three.** REJECTED: collapses the authoring-guidance surface (ADR-0.0.30) into the advisor surface (ADR-0.0.29) by losing the `advise` distinction; the operator-bandwidth-protection benefit of `advise` (no advisor session, just authoring-time hint) is lost. The three-value vocabulary maps cleanly to the three downstream consumer surfaces.

5. **Four trigger-semantic values (block / warn / advise / info).** REJECTED: introduces a state with no consumer surface; `info` is what `advise` already does at the lightest end of the spectrum. Adding values without a consumer surface is the foundation-doctrine version of dead code.

6. **Operator-defined trigger-semantic vocabulary (no fixed enum).** REJECTED: situational vocabulary is doctrine drift by another name (the Q4 graceful-degradation rejection from ADR-0.0.27 applies). The vocabulary must be foundation-kind for downstream ADRs to bind against it.

7. **Optional `block` band per metric.** REJECTED: a metric without a `block` band is prose, not a threshold. The schema-level requirement closes the "threshold that cannot fail" failure class.

8. **Single-OBPI ADR (rule + loader + validator under one brief).** REJECTED: bundles three distinct invariants under one Gate 5 witness; the rule is the doctrine surface, the loader is the runtime contract, the validator is the gate — three separable invariants per the cluster's decomposition discipline.

9. **Five-OBPI ADR (per-metric OBPIs).** REJECTED: produces ceremony without invariant addition; the per-metric mappings are doctrine content the rule body carries, not separable invariants.

10. **No validator (rely on operator discipline to keep the table consistent).** REJECTED: the validator is the structural defense against silent threshold drift across corpus refresh; without it, an unmapped band introduced by a new distillation surfaces only at the next operator session, possibly months later. Fail-closed at gate time is the load-bearing closing invariant.

11. **Use a generic `gz validate --documents` extension instead of a dedicated `--complexity-thresholds` flag.** REJECTED: aggregating cluster-specific validation into the generic documents flag dilutes the operator-facing diagnostic message ("validation failed" vs. "complexity threshold table has unmapped band at metric X"). The dedicated flag is the load-bearing diagnostic surface.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.28 | Completed | Jeffry | 2026-05-05 | completed |
