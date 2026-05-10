---
id: ADR-0.0.30-complexity-authoring-guidance
status: Validated
kind: foundation
semver: 0.0.30
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-25
---

# ADR-0.0.30: Complexity Authoring Guidance

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats the authoring-guidance surface as the upstream-prevention complement to ADR-0.0.29's trigger-time advisor: hints surface at design time, not at gate time. Refuses to reimplement schema; `AuthoringHint` is a fixed-direction projection of `AdvisorDiagnosis` (full → light), never the reverse. Reads the editor/IDE integration as a contract specification, not as editor implementations — the protocol is what editor authors consume; gzkit's scope is the contract, not the editor ecosystem. Honors the additive-only constraint at the `gz justify` integration: the existing reasoning-walkthrough structure is preserved; authoring hints are an additional evidence section that closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference. Accepts that the advise band's qualitative threshold may not be calibrated against developer attention bandwidth on first distillation; calibration tightens at the next distillation pass per the cluster cadence.

This ADR is the fourth and closing foundation in the four-ADR complexity-doctrine cluster (0.0.27 corpus / 0.0.28 thresholds / 0.0.29 advisor / 0.0.30 authoring-guidance). It is the lightest-touch trigger-semantic surface (consuming the advise band of ADR-0.0.28) and the cluster's loop-closer with ADR-0.0.19's pre-execution reasoning-walkthrough doctrine. The cluster's mantra (5:1 governance-to-output ratio is the product) holds even at this lightest-touch layer — operator-bandwidth-protection does NOT mean operator-decision-bypass.

## Intent

ADR-0.0.29's advisor is the trigger-time response surface — it fires when a metric crosses warn or block at commit time. ADR-0.0.30 is the upstream-prevention complement: it surfaces complexity hints to the developer while they are authoring code, before the metric crosses any band, so refactor decisions land at design time rather than at gate time. The two surfaces share `AdvisorDiagnosis` schema (consumed) and the cluster's distilled-characteristics + threshold table; they differ in trigger time (authoring vs. commit), presentation (in-line hint vs. structured diagnosis), and consumer surface (editor/IDE + `gz justify` vs. CLI + pre-commit hook).

Without ADR-0.0.30, the `advise` band of ADR-0.0.28's threshold table has no consumer surface — the band exists but does nothing, which is the foundation-doctrine version of dead code (the ADR-0.0.28 § Alternatives Considered #5 rejection applied to the missing-consumer surface). The advise band is the cluster's lightest-touch trigger semantic: it does not block the build (block band is xenon), does not surface a structured advisor diagnosis (warn band is ADR-0.0.29), and is reserved precisely for authoring-time hints. ADR-0.0.30 is the surface that consumes it.

The authoring-guidance surface ships three pathways: (a) `gz complexity-guide <path>` for ad-hoc authoring-time review (operator-invocable while editing); (b) an editor/IDE integration contract specified as an LSP-style JSON-over-stdio protocol that editor authors can consume — no editor implementations land in this ADR (specification only, per the handoff's locked scope at OBPI-04); (c) integration with the OBPI-pipeline `gz justify` skill (ADR-0.0.19) so authoring-time hints for an OBPI's allowed-paths surface inside the pre-execution reasoning walkthrough — closing the loop with the cluster's reasoning-walkthrough doctrine. The cluster's deliberate mirror-shape: ADR-0.0.27 corpus / 0.0.28 thresholds / 0.0.29 advisor (trigger-time) / 0.0.30 authoring-guidance (upstream-prevention) — four foundation invariants binding the operator's complexity-decision moment from corpus measurement through pre-commit gate.

## Decision

Codify the complexity-authoring-guidance surface as one CLI verb (`gz complexity-guide`), one operator-runnable skill (`complexity-guide`), one authoring-time hint engine consuming `AdvisorDiagnosis` (ADR-0.0.29) and emitting a lighter `AuthoringHint` shape, one editor/IDE integration contract (LSP-style JSON-over-stdio protocol specification), and one integration with the existing `gz justify` skill (ADR-0.0.19) so authoring-time hints surface during pre-implementation reasoning walkthroughs.

**Rationale (numbered, binding):**

1. The authoring surface consumes `AdvisorDiagnosis` directly from ADR-0.0.29-01, **because** schema duplication across the trigger-time and authoring-time surfaces is the same parser-divergence drift class ADR-0.0.28 closed at the `ThresholdTable` layer. The authoring-time `AuthoringHint` is a lighter projection of the trigger-time diagnosis; the projection is one direction (full → light), never the reverse.
2. The advise band is the cluster's lightest-touch trigger semantic and ADR-0.0.30's primary consumer, **because** the foundation-doctrine version of dead code is a band with no consumer surface (the ADR-0.0.28 § Alternatives Considered #5 rejection inherited verbatim). Without ADR-0.0.30, the advise band exists but does nothing.
3. The editor/IDE integration is specified as a contract, NOT implemented as editor plugins in this ADR, **because** editor implementations are forward-looking specifications that editor authors consume; gzkit's scope is the protocol surface, not the editor ecosystem. The handoff's locked scope at OBPI-04 ratifies this.
4. The protocol is JSON-over-stdio (LSP-style) NOT a TCP/HTTP server, **because** stdio matches the existing CLI invocation pattern and avoids introducing a network surface (which would expand the security-surface scope this cluster does not address). LSP-style is the well-known precedent editors already implement; reusing the precedent reduces editor-author friction.
5. The `gz justify` integration is mandatory, **because** ADR-0.0.19's pre-execution reasoning walkthrough is the canonical home for authoring-time complexity reasoning — surfacing hints inside the walkthrough closes the loop between authoring intent and gate-time verdict. Without the integration, `gz justify` and the authoring-guidance surface are two unconnected reasoning surfaces.
6. Five OBPIs is the right size, **because** each codifies one distinct invariant (CLI, skill, hint engine, protocol contract, justify integration); bundling produces one Gate 5 witness for five separable concerns; over-fragmenting (e.g. one OBPI per archetype-hint kind) produces ceremony without invariant addition.

**The invariant (canonical statement):** gzkit publishes one canonical authoring-guidance surface that consumes the advise band of ADR-0.0.28's `ThresholdTable` and the `AdvisorDiagnosis` schema of ADR-0.0.29, projects authoring-time hints via a stable `AuthoringHint` shape, exposes three pathways (ad-hoc CLI, editor/IDE protocol, `gz justify` integration), and closes the cluster's loop with the pre-execution reasoning-walkthrough doctrine (ADR-0.0.19).

**Mechanical surfaces (what changes in code):**

- `src/gzkit/complexity/authoring/__init__.py` (new package)
- `src/gzkit/complexity/authoring/hint.py` (new): frozen Pydantic `AuthoringHint`, projection from `AdvisorDiagnosis` to `AuthoringHint`.
- `src/gzkit/complexity/authoring/engine.py` (new): authoring-time hint engine; consumes `AdvisorDiagnosis` from ADR-0.0.29-02 engine; projects to `AuthoringHint`; honors the advise band per ADR-0.0.28.
- `src/gzkit/complexity/authoring/protocol.py` (new): JSON-over-stdio LSP-style protocol implementation (server side); editor plugins are consumers, not implemented here.
- `src/gzkit/commands/complexity_guide.py` (new): `gz complexity-guide` CLI verb (Heavy-lane new subcommand).
- `src/gzkit/cli/parser_artifacts.py`: register the new verb.
- `src/gzkit/schemas/authoring_hint.json` (new): JSON Schema mirror.
- `src/gzkit/schemas/authoring_guide_protocol.json` (new): JSON Schema for protocol message envelopes.
- `.gzkit/skills/complexity-guide/SKILL.md` (new): operator-runnable skill; vendor-mirrored.
- `.gzkit/skills/gz-justify/SKILL.md`: extend to invoke authoring-guidance hints for the OBPI's allowed-paths during justification (additive amendment to the existing skill).
- `tests/complexity/authoring/**`: REQ-derived assertions across all five OBPIs.
- `features/complexity_guide.feature` (new): BDD scenarios tagged `@REQ-0.0.30-NN-MM`.
- `docs/user/manpages/gz-complexity-guide.md` (new): manpage per the gate5-runbook-code-covenant.
- `docs/user/runbook.md`: runbook entry under "Complexity doctrine surfaces".
- `docs/governance/complexity/authoring-guide-protocol.md` (new): protocol specification document for editor authors.
- `docs/governance/advisory-rules-audit.md`: scorecard entries.

**Five OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.30-01 — `gz complexity-guide` CLI verb:** Heavy-lane new subcommand per `.claude/rules/cli.md`: ADR (this), manpage at `docs/user/manpages/gz-complexity-guide.md`, behave smoke, release-notes. Default human output is in-line hint prose (one block per hint with archetype, doctrinal frame excerpt headline, recommended-move headline); `--json` emits canonical `AuthoringHint` serialization.

**OBPI-0.0.30-02 — `complexity-guide` skill:** `.gzkit/skills/complexity-guide/SKILL.md` carrying operator invocation patterns + Output Contract declaration; vendor-mirrored. Tool / Skill / Runbook alignment per `.gzkit/rules/tool-skill-runbook-alignment.md`.

**OBPI-0.0.30-03 — Authoring-time hint engine:** `src/gzkit/complexity/authoring/engine.py`; consumes ADR-0.0.29-02's diagnosis engine output; projects to `AuthoringHint` via `src/gzkit/complexity/authoring/hint.py`. The projection is lighter than `AdvisorDiagnosis`: omits `proof: tuple[ProofRange, ...]` (the developer has the file open — proof is implicit), omits `intrinsic_attestation` (authoring-time hints precede attestation), retains `archetype`, `doctrinal_frame.excerpt` (truncated to 1-line headline), `recommended_move`, plus a new `precedence_band: Literal["approaching", "approaching_warn"]` indicating which side of the advise band the function is on.

**OBPI-0.0.30-04 — Editor/IDE integration contract (specification):** `src/gzkit/complexity/authoring/protocol.py` implements the server side of an LSP-style JSON-over-stdio protocol. Specification document at `docs/governance/complexity/authoring-guide-protocol.md` defines the message envelope: `initialize`, `analyze` (input: file path + cursor position; output: list of `AuthoringHint` with line ranges), `shutdown`. The JSON Schema at `src/gzkit/schemas/authoring_guide_protocol.json` validates message envelopes. NO editor implementations land here; the contract is what editor authors consume.

**OBPI-0.0.30-05 — `gz justify` integration:** Amend `.gzkit/skills/gz-justify/SKILL.md` (additive only — the skill remains as-is for non-complexity reasoning) so that when an operator runs `gz justify` for an OBPI whose `Allowed Paths` include `.py` files, the authoring-guidance hints for those files surface in the justification scaffold's evidence section. The integration uses the existing `complexity-guide` engine; no new engine is built. Closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference at brief level.

**Sequencing:** OBPI-03 → OBPI-01 → OBPI-02 → OBPI-04 → OBPI-05. The hint engine + projection (OBPI-03) is the data surface; the CLI (OBPI-01) wires it to the operator's ad-hoc invocation; the skill (OBPI-02) routes the operator at the surface layer; the protocol contract (OBPI-04) extends the engine to a stdio interface for editors; the `gz justify` integration (OBPI-05) lands last because it amends an existing skill.

**Lane: Heavy.** New CLI subcommand + new skill + new protocol contract + new editor-facing specification + new `gz justify` skill amendment. All four trigger heavy-lane rigor per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.18.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the corpus selection methodology — that is ADR-0.0.27's scope.
- Does NOT specify the threshold values or trigger semantics — that is ADR-0.0.28's scope.
- Does NOT author the complexity advisor (trigger-time response surface) — that is ADR-0.0.29's scope.
- Does NOT implement editor/IDE plugins — the protocol contract is specification-only at OBPI-04; editor authors consume the contract on their own ADR scope.
- Does NOT modify the `gz justify` skill's reasoning structure — the integration at OBPI-05 is additive (an extra evidence section), not a redesign.
- Does NOT introduce new ledger event families — authoring hints are diagnostic-only and do not land in `.gzkit/ledger.jsonl`.
- Does NOT vendor or reimplement LSP — gzkit's protocol is LSP-style for shape similarity but is its own contract; an editor implementing the gzkit protocol does NOT need a full LSP runtime.

## Comparator Uplift (2026-05-07)

Kiro/Spec Kit-style front doors reduce operator blank-page cost. This ADR should
absorb that as authoring guidance that drafts complexity-aware decomposition,
tradeoffs, and verification hooks for operator review. Each generated hint must
carry a source anchor or explicit inference label so "helpful guidance" cannot
become plausible but unwitnessed planning prose.

## Consequences

### Positive

1. **Closes the cluster's loop.** ADR-0.0.27 (corpus) → 0.0.28 (thresholds) → 0.0.29 (trigger-time response) → 0.0.30 (upstream prevention). All four foundations land; the developer's complexity-decision moment is bound from corpus measurement through pre-commit gate through authoring-time hint.

2. **The advise band finally has a consumer.** Without ADR-0.0.30, the advise band of ADR-0.0.28 is dead doctrine. The CLI + protocol + `gz justify` integration give the band three concrete surfaces.

3. **Schema reuse via projection.** `AuthoringHint` is a lighter projection of `AdvisorDiagnosis` (ADR-0.0.29-01); no schema duplication. The projection direction is fixed (full → light, never the reverse), preserving the trigger-time surface's authoritative role.

4. **Editor integration as contract, not implementation.** The protocol specification at `docs/governance/complexity/authoring-guide-protocol.md` is what editor authors consume; gzkit's scope is the contract, not the editor ecosystem. Closes the "vendor lock to one editor" failure class.

5. **JSON-over-stdio matches existing CLI patterns.** No network surface introduced; no security-scope expansion. LSP-style precedent reduces editor-author friction.

6. **`gz justify` integration closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference.** Pre-execution reasoning walkthroughs surface authoring-time complexity hints for the OBPI's allowed-paths inline; the operator does not have to run two surfaces (`gz justify` AND `gz complexity-guide`) and stitch the outputs together.

7. **Five OBPIs is the right size.** Each codifies one distinct invariant (CLI, skill, engine + projection, protocol contract, justify integration); foundation-kind brief-level Gate 5 across five increments per ADR-0.0.18.

8. **The protocol contract is forward-compatible with the editor ecosystem's evolution.** LSP-style envelopes are extensible; future hints (e.g. hover-time citation lookup) can be added without breaking existing editor consumers. Schema extensibility per the additive-only amendment discipline.

9. **Operator-bandwidth-protection at authoring time.** The OEE doctrine's "agent drafts substantively, operator reviews" pattern lands at the developer's editing moment: the hint engine drafts the archetype + recommended-move; the developer decides whether to refactor.

10. **Cluster mantra is preserved at the lightest-touch trigger semantic.** The mantra (ceremony is the deliverable; the 5:1 governance-to-output ratio is the product) holds even at the advise band — operator-bandwidth-protection does NOT mean operator-decision-bypass.

### Negative

1. **Five OBPIs of foundation-kind ceremony for a surface that does not block the build.** Real bandwidth cost; mitigated by the foundation-kind discipline (each OBPI is a separable invariant, not a fragmentation move) and by the cluster mantra (ceremony is the deliverable).

2. **The protocol contract has no canonical implementation in this ADR.** Editor authors who want to consume the contract have to read the specification document; there is no reference implementation. Pool stub `ADR-pool.complexity-authoring-editor-reference` (forward-reference at OBPI-04) names the future ADR scope if a reference editor implementation becomes warranted.

3. **The `gz justify` skill amendment couples ADR-0.0.30 to ADR-0.0.19.** Amendments to either ADR's contract require coordinated work. Mitigated by the additive-only constraint at OBPI-05 (the existing reasoning-walkthrough structure is preserved; authoring hints are an additional evidence section).

4. **`AuthoringHint` projection from `AdvisorDiagnosis` introduces a versioning surface.** Future amendments to `AdvisorDiagnosis` (ADR-0.0.29) require the projection to be re-derived. The doctrine-amendment-protocol pool stub is the canonical home for that work.

5. **JSON-over-stdio is well-suited to local-only editor invocation.** A future remote-editor scenario (e.g. cloud-IDE with the gzkit guide running on a separate machine) would require a different protocol substrate. Out of scope; pool-stub forward-reference if it materializes.

6. **Three pathways (ad-hoc CLI, editor protocol, `gz justify` integration) means three test surfaces.** Real test-authoring cost; bounded by the cluster's existing test discipline (mock at subprocess boundaries, `tempfile`-backed fixtures, REQ-derived assertions).

7. **The skill's Output Contract has to align with the CLI verb's default form.** Invariant 3 of the tool-skill-runbook-alignment rule binds; if the CLI's hint-formatting changes, the skill's contract has to be updated in the same patch.

8. **The advise band's qualitative thresholds may not be calibrated against developer attention bandwidth.** First-distillation cold-start (per ADR-0.0.27 § Negative #9) means the initial advise-band cutoff is set conservatively; if it produces too many hints (operator-fatigue) or too few (under-surface), it gets re-tightened at the next distillation pass per the cluster cadence.

9. **Foundation-kind attestation across five OBPIs.** Attestation fatigue across the cluster's twenty-four OBPIs (7+3+9+5) is a real operator cost; pool stub `ADR-pool.attestation-quality-measurement` is the cluster-wide forward-reference if it materializes.

10. **The protocol is gzkit-specific, not LSP-compliant.** An editor that already implements LSP cannot drop in the gzkit protocol without writing a separate handler; the protocol borrows LSP's envelope style but is not interoperable with LSP servers. The tradeoff is deliberate (gzkit's surface is its own contract; LSP-compliance would force schema concessions the cluster's mantra refuses).

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
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.30-01 — `gz complexity-guide` CLI verb (Heavy-lane new subcommand: ADR + manpage + smoke + release notes; default in-line hint prose; --json mode)
- [ ] OBPI-0.0.30-02 — `complexity-guide` skill (vendor-mirrored; Output Contract declared; tool-skill-runbook-alignment Invariants 1-3)
- [ ] OBPI-0.0.30-03 — Authoring-time hint engine + AuthoringHint projection from AdvisorDiagnosis (consumes ADR-0.0.29-02 engine; src/gzkit/complexity/authoring/{hint.py, engine.py})
- [ ] OBPI-0.0.30-04 — Editor/IDE integration contract specification (LSP-style JSON-over-stdio protocol at src/gzkit/complexity/authoring/protocol.py + spec document at docs/governance/complexity/authoring-guide-protocol.md; no editor implementations in this ADR)
- [ ] OBPI-0.0.30-05 — `gz justify` integration (amend `.gzkit/skills/gz-justify/SKILL.md` so authoring-guidance hints for an OBPI's .py allowed-paths surface in the justification scaffold's evidence section)

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-04-25T15:44:40.370824*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.30

### Q: What is the title of this ADR?

**A:** Complexity Authoring Guidance

### Q: What is the semantic version?

**A:** 0.0.30

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** ADR-0.0.29's advisor is the trigger-time response surface — it fires when a metric crosses warn or block at commit time. ADR-0.0.30 is the upstream-prevention complement: it surfaces complexity hints to the developer while they are authoring code, before the metric crosses any band, so refactor decisions land at design time rather than at gate time. The two surfaces share `AdvisorDiagnosis` schema (consumed) and the cluster's distilled-characteristics + threshold table; they differ in trigger time (authoring vs. commit), presentation (in-line hint vs. structured diagnosis), and consumer surface (editor/IDE + `gz justify` vs. CLI + pre-commit hook).

Without ADR-0.0.30, the `advise` band of ADR-0.0.28's threshold table has no consumer surface — the band exists but does nothing, which is the foundation-doctrine version of dead code (the ADR-0.0.28 § Alternatives Considered #5 rejection applied to the missing-consumer surface). The advise band is the cluster's lightest-touch trigger semantic: it does not block the build (block band is xenon), does not surface a structured advisor diagnosis (warn band is ADR-0.0.29), and is reserved precisely for authoring-time hints. ADR-0.0.30 is the surface that consumes it.

The authoring-guidance surface ships three pathways: (a) `gz complexity-guide <path>` for ad-hoc authoring-time review (operator-invocable while editing); (b) an editor/IDE integration contract specified as an LSP-style JSON-over-stdio protocol that editor authors can consume — no editor implementations land in this ADR (specification only, per the handoff's locked scope at OBPI-04); (c) integration with the OBPI-pipeline `gz justify` skill (ADR-0.0.19) so authoring-time hints for an OBPI's allowed-paths surface inside the pre-execution reasoning walkthrough — closing the loop with the cluster's reasoning-walkthrough doctrine. The cluster's deliberate mirror-shape: ADR-0.0.27 corpus / 0.0.28 thresholds / 0.0.29 advisor (trigger-time) / 0.0.30 authoring-guidance (upstream-prevention) — four foundation invariants binding the operator's complexity-decision moment from corpus measurement through pre-commit gate.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Codify the complexity-authoring-guidance surface as one CLI verb (`gz complexity-guide`), one operator-runnable skill (`complexity-guide`), one authoring-time hint engine consuming `AdvisorDiagnosis` (ADR-0.0.29) and emitting a lighter `AuthoringHint` shape, one editor/IDE integration contract (LSP-style JSON-over-stdio protocol specification), and one integration with the existing `gz justify` skill (ADR-0.0.19) so authoring-time hints surface during pre-implementation reasoning walkthroughs.

**Rationale (numbered, binding):**

1. The authoring surface consumes `AdvisorDiagnosis` directly from ADR-0.0.29-01, **because** schema duplication across the trigger-time and authoring-time surfaces is the same parser-divergence drift class ADR-0.0.28 closed at the `ThresholdTable` layer. The authoring-time `AuthoringHint` is a lighter projection of the trigger-time diagnosis; the projection is one direction (full → light), never the reverse.
2. The advise band is the cluster's lightest-touch trigger semantic and ADR-0.0.30's primary consumer, **because** the foundation-doctrine version of dead code is a band with no consumer surface (the ADR-0.0.28 § Alternatives Considered #5 rejection inherited verbatim). Without ADR-0.0.30, the advise band exists but does nothing.
3. The editor/IDE integration is specified as a contract, NOT implemented as editor plugins in this ADR, **because** editor implementations are forward-looking specifications that editor authors consume; gzkit's scope is the protocol surface, not the editor ecosystem. The handoff's locked scope at OBPI-04 ratifies this.
4. The protocol is JSON-over-stdio (LSP-style) NOT a TCP/HTTP server, **because** stdio matches the existing CLI invocation pattern and avoids introducing a network surface (which would expand the security-surface scope this cluster does not address). LSP-style is the well-known precedent editors already implement; reusing the precedent reduces editor-author friction.
5. The `gz justify` integration is mandatory, **because** ADR-0.0.19's pre-execution reasoning walkthrough is the canonical home for authoring-time complexity reasoning — surfacing hints inside the walkthrough closes the loop between authoring intent and gate-time verdict. Without the integration, `gz justify` and the authoring-guidance surface are two unconnected reasoning surfaces.
6. Five OBPIs is the right size, **because** each codifies one distinct invariant (CLI, skill, hint engine, protocol contract, justify integration); bundling produces one Gate 5 witness for five separable concerns; over-fragmenting (e.g. one OBPI per archetype-hint kind) produces ceremony without invariant addition.

**The invariant (canonical statement):** gzkit publishes one canonical authoring-guidance surface that consumes the advise band of ADR-0.0.28's `ThresholdTable` and the `AdvisorDiagnosis` schema of ADR-0.0.29, projects authoring-time hints via a stable `AuthoringHint` shape, exposes three pathways (ad-hoc CLI, editor/IDE protocol, `gz justify` integration), and closes the cluster's loop with the pre-execution reasoning-walkthrough doctrine (ADR-0.0.19).

**Mechanical surfaces (what changes in code):**

- `src/gzkit/complexity/authoring/__init__.py` (new package)
- `src/gzkit/complexity/authoring/hint.py` (new): frozen Pydantic `AuthoringHint`, projection from `AdvisorDiagnosis` to `AuthoringHint`.
- `src/gzkit/complexity/authoring/engine.py` (new): authoring-time hint engine; consumes `AdvisorDiagnosis` from ADR-0.0.29-02 engine; projects to `AuthoringHint`; honors the advise band per ADR-0.0.28.
- `src/gzkit/complexity/authoring/protocol.py` (new): JSON-over-stdio LSP-style protocol implementation (server side); editor plugins are consumers, not implemented here.
- `src/gzkit/commands/complexity_guide.py` (new): `gz complexity-guide` CLI verb (Heavy-lane new subcommand).
- `src/gzkit/cli/parser_artifacts.py`: register the new verb.
- `src/gzkit/schemas/authoring_hint.json` (new): JSON Schema mirror.
- `src/gzkit/schemas/authoring_guide_protocol.json` (new): JSON Schema for protocol message envelopes.
- `.gzkit/skills/complexity-guide/SKILL.md` (new): operator-runnable skill; vendor-mirrored.
- `.gzkit/skills/gz-justify/SKILL.md`: extend to invoke authoring-guidance hints for the OBPI's allowed-paths during justification (additive amendment to the existing skill).
- `tests/complexity/authoring/**`: REQ-derived assertions across all five OBPIs.
- `features/complexity_guide.feature` (new): BDD scenarios tagged `@REQ-0.0.30-NN-MM`.
- `docs/user/manpages/gz-complexity-guide.md` (new): manpage per the gate5-runbook-code-covenant.
- `docs/user/runbook.md`: runbook entry under "Complexity doctrine surfaces".
- `docs/governance/complexity/authoring-guide-protocol.md` (new): protocol specification document for editor authors.
- `docs/governance/advisory-rules-audit.md`: scorecard entries.

**Five OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.30-01 — `gz complexity-guide` CLI verb:** Heavy-lane new subcommand per `.claude/rules/cli.md`: ADR (this), manpage at `docs/user/manpages/gz-complexity-guide.md`, behave smoke, release-notes. Default human output is in-line hint prose (one block per hint with archetype, doctrinal frame excerpt headline, recommended-move headline); `--json` emits canonical `AuthoringHint` serialization.

**OBPI-0.0.30-02 — `complexity-guide` skill:** `.gzkit/skills/complexity-guide/SKILL.md` carrying operator invocation patterns + Output Contract declaration; vendor-mirrored. Tool / Skill / Runbook alignment per `.gzkit/rules/tool-skill-runbook-alignment.md`.

**OBPI-0.0.30-03 — Authoring-time hint engine:** `src/gzkit/complexity/authoring/engine.py`; consumes ADR-0.0.29-02's diagnosis engine output; projects to `AuthoringHint` via `src/gzkit/complexity/authoring/hint.py`. The projection is lighter than `AdvisorDiagnosis`: omits `proof: tuple[ProofRange, ...]` (the developer has the file open — proof is implicit), omits `intrinsic_attestation` (authoring-time hints precede attestation), retains `archetype`, `doctrinal_frame.excerpt` (truncated to 1-line headline), `recommended_move`, plus a new `precedence_band: Literal["approaching", "approaching_warn"]` indicating which side of the advise band the function is on.

**OBPI-0.0.30-04 — Editor/IDE integration contract (specification):** `src/gzkit/complexity/authoring/protocol.py` implements the server side of an LSP-style JSON-over-stdio protocol. Specification document at `docs/governance/complexity/authoring-guide-protocol.md` defines the message envelope: `initialize`, `analyze` (input: file path + cursor position; output: list of `AuthoringHint` with line ranges), `shutdown`. The JSON Schema at `src/gzkit/schemas/authoring_guide_protocol.json` validates message envelopes. NO editor implementations land here; the contract is what editor authors consume.

**OBPI-0.0.30-05 — `gz justify` integration:** Amend `.gzkit/skills/gz-justify/SKILL.md` (additive only — the skill remains as-is for non-complexity reasoning) so that when an operator runs `gz justify` for an OBPI whose `Allowed Paths` include `.py` files, the authoring-guidance hints for those files surface in the justification scaffold's evidence section. The integration uses the existing `complexity-guide` engine; no new engine is built. Closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference at brief level.

**Sequencing:** OBPI-03 → OBPI-01 → OBPI-02 → OBPI-04 → OBPI-05. The hint engine + projection (OBPI-03) is the data surface; the CLI (OBPI-01) wires it to the operator's ad-hoc invocation; the skill (OBPI-02) routes the operator at the surface layer; the protocol contract (OBPI-04) extends the engine to a stdio interface for editors; the `gz justify` integration (OBPI-05) lands last because it amends an existing skill.

**Lane: Heavy.** New CLI subcommand + new skill + new protocol contract + new editor-facing specification + new `gz justify` skill amendment. All four trigger heavy-lane rigor per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks per ADR-0.0.18.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the corpus selection methodology — that is ADR-0.0.27's scope.
- Does NOT specify the threshold values or trigger semantics — that is ADR-0.0.28's scope.
- Does NOT author the complexity advisor (trigger-time response surface) — that is ADR-0.0.29's scope.
- Does NOT implement editor/IDE plugins — the protocol contract is specification-only at OBPI-04; editor authors consume the contract on their own ADR scope.
- Does NOT modify the `gz justify` skill's reasoning structure — the integration at OBPI-05 is additive (an extra evidence section), not a redesign.
- Does NOT introduce new ledger event families — authoring hints are diagnostic-only and do not land in `.gzkit/ledger.jsonl`.
- Does NOT vendor or reimplement LSP — gzkit's protocol is LSP-style for shape similarity but is its own contract; an editor implementing the gzkit protocol does NOT need a full LSP runtime.

### Q: What good things result from this decision? List benefits.

**A:** 1. **Closes the cluster's loop.** ADR-0.0.27 (corpus) → 0.0.28 (thresholds) → 0.0.29 (trigger-time response) → 0.0.30 (upstream prevention). All four foundations land; the developer's complexity-decision moment is bound from corpus measurement through pre-commit gate through authoring-time hint.

2. **The advise band finally has a consumer.** Without ADR-0.0.30, the advise band of ADR-0.0.28 is dead doctrine. The CLI + protocol + `gz justify` integration give the band three concrete surfaces.

3. **Schema reuse via projection.** `AuthoringHint` is a lighter projection of `AdvisorDiagnosis` (ADR-0.0.29-01); no schema duplication. The projection direction is fixed (full → light, never the reverse), preserving the trigger-time surface's authoritative role.

4. **Editor integration as contract, not implementation.** The protocol specification at `docs/governance/complexity/authoring-guide-protocol.md` is what editor authors consume; gzkit's scope is the contract, not the editor ecosystem. Closes the "vendor lock to one editor" failure class.

5. **JSON-over-stdio matches existing CLI patterns.** No network surface introduced; no security-scope expansion. LSP-style precedent reduces editor-author friction.

6. **`gz justify` integration closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference.** Pre-execution reasoning walkthroughs surface authoring-time complexity hints for the OBPI's allowed-paths inline; the operator does not have to run two surfaces (`gz justify` AND `gz complexity-guide`) and stitch the outputs together.

7. **Five OBPIs is the right size.** Each codifies one distinct invariant (CLI, skill, engine + projection, protocol contract, justify integration); foundation-kind brief-level Gate 5 across five increments per ADR-0.0.18.

8. **The protocol contract is forward-compatible with the editor ecosystem's evolution.** LSP-style envelopes are extensible; future hints (e.g. hover-time citation lookup) can be added without breaking existing editor consumers. Schema extensibility per the additive-only amendment discipline.

9. **Operator-bandwidth-protection at authoring time.** The OEE doctrine's "agent drafts substantively, operator reviews" pattern lands at the developer's editing moment: the hint engine drafts the archetype + recommended-move; the developer decides whether to refactor.

10. **Cluster mantra is preserved at the lightest-touch trigger semantic.** The mantra (ceremony is the deliverable; the 5:1 governance-to-output ratio is the product) holds even at the advise band — operator-bandwidth-protection does NOT mean operator-decision-bypass.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **Five OBPIs of foundation-kind ceremony for a surface that does not block the build.** Real bandwidth cost; mitigated by the foundation-kind discipline (each OBPI is a separable invariant, not a fragmentation move) and by the cluster mantra (ceremony is the deliverable).

2. **The protocol contract has no canonical implementation in this ADR.** Editor authors who want to consume the contract have to read the specification document; there is no reference implementation. Pool stub `ADR-pool.complexity-authoring-editor-reference` (forward-reference at OBPI-04) names the future ADR scope if a reference editor implementation becomes warranted.

3. **The `gz justify` skill amendment couples ADR-0.0.30 to ADR-0.0.19.** Amendments to either ADR's contract require coordinated work. Mitigated by the additive-only constraint at OBPI-05 (the existing reasoning-walkthrough structure is preserved; authoring hints are an additional evidence section).

4. **`AuthoringHint` projection from `AdvisorDiagnosis` introduces a versioning surface.** Future amendments to `AdvisorDiagnosis` (ADR-0.0.29) require the projection to be re-derived. The doctrine-amendment-protocol pool stub is the canonical home for that work.

5. **JSON-over-stdio is well-suited to local-only editor invocation.** A future remote-editor scenario (e.g. cloud-IDE with the gzkit guide running on a separate machine) would require a different protocol substrate. Out of scope; pool-stub forward-reference if it materializes.

6. **Three pathways (ad-hoc CLI, editor protocol, `gz justify` integration) means three test surfaces.** Real test-authoring cost; bounded by the cluster's existing test discipline (mock at subprocess boundaries, `tempfile`-backed fixtures, REQ-derived assertions).

7. **The skill's Output Contract has to align with the CLI verb's default form.** Invariant 3 of the tool-skill-runbook-alignment rule binds; if the CLI's hint-formatting changes, the skill's contract has to be updated in the same patch.

8. **The advise band's qualitative thresholds may not be calibrated against developer attention bandwidth.** First-distillation cold-start (per ADR-0.0.27 § Negative #9) means the initial advise-band cutoff is set conservatively; if it produces too many hints (operator-fatigue) or too few (under-surface), it gets re-tightened at the next distillation pass per the cluster cadence.

9. **Foundation-kind attestation across five OBPIs.** Attestation fatigue across the cluster's twenty-four OBPIs (7+3+9+5) is a real operator cost; pool stub `ADR-pool.attestation-quality-measurement` is the cluster-wide forward-reference if it materializes.

10. **The protocol is gzkit-specific, not LSP-compliant.** An editor that already implements LSP cannot drop in the gzkit protocol without writing a separate handler; the protocol borrows LSP's envelope style but is not interoperable with LSP servers. The tradeoff is deliberate (gzkit's surface is its own contract; LSP-compliance would force schema concessions the cluster's mantra refuses).

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. `gz complexity-guide` CLI verb (Heavy-lane new subcommand: ADR + manpage + smoke + release notes; default in-line hint prose; --json mode)
2. `complexity-guide` skill (vendor-mirrored; Output Contract declared; tool-skill-runbook-alignment Invariants 1-3)
3. Authoring-time hint engine + AuthoringHint projection from AdvisorDiagnosis (consumes ADR-0.0.29-02 engine; src/gzkit/complexity/authoring/{hint.py, engine.py})
4. Editor/IDE integration contract specification (LSP-style JSON-over-stdio protocol at src/gzkit/complexity/authoring/protocol.py + spec document at docs/governance/complexity/authoring-guide-protocol.md; no editor implementations in this ADR)
5. `gz justify` integration (amend `.gzkit/skills/gz-justify/SKILL.md` so authoring-guidance hints for an OBPI's .py allowed-paths surface in the justification scaffold's evidence section)

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Single-OBPI ADR (CLI + skill + engine + protocol + justify integration bundled).** REJECTED: bundles five separable invariants under one Gate 5 witness; obscures the dependency graph; produces one foundation-kind ceremony for what is structurally five distinct invariants.

2. **Authoring guidance as a sub-command of `gz complexity-advise` instead of its own verb.** REJECTED: dilutes operator-facing diagnostic naming (advise is the trigger-time response; guidance is upstream-prevention — different operator moments). Heavy-lane subcommand-naming discipline per `.claude/rules/cli.md`.

3. **Implement editor/IDE plugins in this ADR (specifically VS Code + Neovim + JetBrains).** REJECTED at design dialogue: editor implementations are an editor-author concern; gzkit's scope is the protocol contract. Implementing plugins would lock the cluster to specific editor ecosystems and dramatically expand the scope.

4. **Use full LSP instead of a gzkit-specific LSP-style protocol.** REJECTED: full LSP imposes schema concessions (LSP's diagnostic shape would force `AuthoringHint` to lose fields the cluster's mantra requires); gzkit's surface is its own contract. The LSP-style envelope is borrowed for shape similarity (reduces editor-author friction); full LSP-compliance is not the goal.

5. **TCP/HTTP server protocol instead of stdio.** REJECTED: introduces a network surface (security-scope expansion the cluster does not address); breaks the existing CLI invocation pattern; demands additional infrastructure (port allocation, lifecycle management) editor authors should not have to manage.

6. **Author guidance as part of ADR-0.0.29 (combine trigger-time response + upstream prevention into one ADR).** REJECTED at design dialogue: trigger-time and authoring-time are different operator moments with different presentation defaults, different consumer surfaces, and different gate semantics. Combining them obscures the cluster's invariant decomposition.

7. **Skip `gz justify` integration (OBPI-05) and let operators run two surfaces independently.** REJECTED: the integration closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference; without it, pre-execution reasoning walkthroughs and authoring-time hints are two unconnected surfaces the operator has to stitch together by hand.

8. **Make `AuthoringHint` independent of `AdvisorDiagnosis` (no projection; separate schemas).** REJECTED: the same parser-divergence drift class ADR-0.0.28 closed at the `ThresholdTable` layer reappears here. Projection direction is fixed (full → light); reverse projection is not allowed.

9. **Editor protocol uses YAML or TOML envelopes instead of JSON.** REJECTED: JSON is the dominant protocol envelope format (LSP, JSON-RPC, MCP, etc.); editor authors expect JSON; YAML/TOML would introduce friction for no gain.

10. **Make the editor protocol an ADR scope expansion (one ADR per editor implementation).** REJECTED: editor implementations are forward-looking; the protocol contract is what gzkit ships. Pool stub `ADR-pool.complexity-authoring-editor-reference` is the future home if a reference editor implementation becomes warranted.

11. **Cut OBPI-04 (editor/IDE protocol contract) — handle editor integration via ad-hoc CLI invocation only.** REJECTED at design dialogue (per the handoff's locked decision): the protocol contract is forward-looking specification that closes the ecosystem-readiness failure class. Editor authors who want to consume gzkit complexity hints need a stable contract to bind against; without OBPI-04 they are stuck shelling out to the CLI per file edit, which is the operator-experience equivalent of a dropped frame rate.

12. **Author the editor protocol as a separate ADR (post-cluster).** REJECTED: the protocol is the surface that consumes `AuthoringHint`; separating it from the surface that produces `AuthoringHint` introduces an artificial ADR boundary. The cluster's decomposition discipline binds toward including the protocol here.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Single-OBPI ADR (CLI + skill + engine + protocol + justify integration bundled).** REJECTED: bundles five separable invariants under one Gate 5 witness; obscures the dependency graph; produces one foundation-kind ceremony for what is structurally five distinct invariants.

2. **Authoring guidance as a sub-command of `gz complexity-advise` instead of its own verb.** REJECTED: dilutes operator-facing diagnostic naming (advise is the trigger-time response; guidance is upstream-prevention — different operator moments). Heavy-lane subcommand-naming discipline per `.claude/rules/cli.md`.

3. **Implement editor/IDE plugins in this ADR (specifically VS Code + Neovim + JetBrains).** REJECTED at design dialogue: editor implementations are an editor-author concern; gzkit's scope is the protocol contract. Implementing plugins would lock the cluster to specific editor ecosystems and dramatically expand the scope.

4. **Use full LSP instead of a gzkit-specific LSP-style protocol.** REJECTED: full LSP imposes schema concessions (LSP's diagnostic shape would force `AuthoringHint` to lose fields the cluster's mantra requires); gzkit's surface is its own contract. The LSP-style envelope is borrowed for shape similarity (reduces editor-author friction); full LSP-compliance is not the goal.

5. **TCP/HTTP server protocol instead of stdio.** REJECTED: introduces a network surface (security-scope expansion the cluster does not address); breaks the existing CLI invocation pattern; demands additional infrastructure (port allocation, lifecycle management) editor authors should not have to manage.

6. **Author guidance as part of ADR-0.0.29 (combine trigger-time response + upstream prevention into one ADR).** REJECTED at design dialogue: trigger-time and authoring-time are different operator moments with different presentation defaults, different consumer surfaces, and different gate semantics. Combining them obscures the cluster's invariant decomposition.

7. **Skip `gz justify` integration (OBPI-05) and let operators run two surfaces independently.** REJECTED: the integration closes the ADR-0.0.19 ↔ ADR-0.0.30 forward reference; without it, pre-execution reasoning walkthroughs and authoring-time hints are two unconnected surfaces the operator has to stitch together by hand.

8. **Make `AuthoringHint` independent of `AdvisorDiagnosis` (no projection; separate schemas).** REJECTED: the same parser-divergence drift class ADR-0.0.28 closed at the `ThresholdTable` layer reappears here. Projection direction is fixed (full → light); reverse projection is not allowed.

9. **Editor protocol uses YAML or TOML envelopes instead of JSON.** REJECTED: JSON is the dominant protocol envelope format (LSP, JSON-RPC, MCP, etc.); editor authors expect JSON; YAML/TOML would introduce friction for no gain.

10. **Make the editor protocol an ADR scope expansion (one ADR per editor implementation).** REJECTED: editor implementations are forward-looking; the protocol contract is what gzkit ships. Pool stub `ADR-pool.complexity-authoring-editor-reference` is the future home if a reference editor implementation becomes warranted.

11. **Cut OBPI-04 (editor/IDE protocol contract) — handle editor integration via ad-hoc CLI invocation only.** REJECTED at design dialogue (per the handoff's locked decision): the protocol contract is forward-looking specification that closes the ecosystem-readiness failure class. Editor authors who want to consume gzkit complexity hints need a stable contract to bind against; without OBPI-04 they are stuck shelling out to the CLI per file edit, which is the operator-experience equivalent of a dropped frame rate.

12. **Author the editor protocol as a separate ADR (post-cluster).** REJECTED: the protocol is the surface that consumes `AuthoringHint`; separating it from the surface that produces `AuthoringHint` introduces an artificial ADR boundary. The cluster's decomposition discipline binds toward including the protocol here.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.30 | Completed | Jeffry | 2026-05-10 | attest completed — ADR-0.0.30 closeout: gz complexity guide CLI verb (OBPI-01) + skill mirrors (OBPI-02) + AuthoringHint engine (OBPI-03) + LSP-style editor protocol (OBPI-04) + gz justify integration (OBPI-05) all live and exercised. Product demos seated in briefs (commit 6493c3bc): gz complexity guide src/gzkit/commands/validate_cmd.py emits ~8 AuthoringHint blocks; --json yields canonical schema; gz justify OBPI-0.0.30-05 surfaces live ### Authoring-time complexity hints from justify/cli.py + walkthrough.py. Heavy-lane receipts at clean tree dirty=false: arb-ruff-07918fc16ee540aa9c9780d8e226c125, arb-step-unittest-d98f3e4f724e4ba6b3846a3c7e3acfb0 (4648 tests), arb-step-typecheck-970c7de257434aa0bc3b9d2cef600f8d, arb-step-mkdocs-310bc12fe56441ea82793b8f1113864b. In-flight walkthrough-discovery weakness fixed (5 brief Demo sections appended) + GHI #431 tracks systemic gz validate --brief-demo-section enhancement. Attestor: g0. |
