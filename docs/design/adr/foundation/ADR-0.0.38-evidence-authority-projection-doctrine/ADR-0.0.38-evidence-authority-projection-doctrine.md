---
id: ADR-0.0.38-evidence-authority-projection-doctrine
status: Draft
kind: foundation
semver: 0.0.38
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-05-06
promoted_from: ADR-pool.evidence-vs-authority-doctrine
---

# ADR-0.0.38-evidence-authority-projection-doctrine: Evidence-Authority-Projection Doctrine

## Persona

Active persona: `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.

This ADR codifies a foundational distinction (which surfaces bind gate decisions vs. which inform operator judgment vs. which merely project Layer-1/Layer-2 truth). The author of every section reads existing surfaces whole before classifying — frontmatter, body invocations, call-site shapes, exit-code semantics — because the binding character of a surface is determined by how callers consume it, not by how its own code is shaped. Refusing to classify a surface whose binding character cannot be observed from evidence is craft, not avoidance; the canonical home for unresolved cases is a `surface_axis_undecidable` ledger event with the named ambiguity, never a guess.

## Intent

**Current state.** Multiple gzkit surfaces — `gz-plan-audit` findings,
`gz-adr-evaluate` scores, `gz-tech-debt-review` reports, the runtime
`advisor()` tool, the proposed advisory-judge surface, the proposed
solved-problem pattern corpus, the proposed lightweight
pre-implementation challenger — all produce output an operator or
agent **acts on**, but none of them bind gate decisions. **Today,**
every one of them re-derives the boundary between *advisory* and
*gating* from scratch in its own SKILL or pool sketch. The state
**before this ADR**: no foundation rule names the function-axis
constraint they inherit, so at least one will drift toward gate-shape
silently — same drift class that produced GHI #195 (default-to-ceremony
intuition without precedent), GHI #290 (agent-synthesized payload
fabrication), and the recurring Boundary 6 flagged in
`docs/governance/state-doctrine.md`.

Symmetrically, Layer-3 derived views — `gz status` output,
`docs/governance/GovZero/adr-status.md`, reconciliation caches — are
projections of Layer-1 canon and Layer-2 ledger truth, but Architectural
Boundary 6 (AGENTS.md) names the failure where an operator or agent
silently treats a derived view as source-of-truth. The state-doctrine
storage axis bans Layer-3 from being source-of-truth; what no rule yet
bans is Layer-3 being treated as an authoritative *binding* surface,
which is a different drift on a different axis.

The state-doctrine layer model (`docs/governance/state-doctrine.md`)
names the **storage** hierarchy. This ADR names the orthogonal
**function** hierarchy: how a surface's output is consumed by callers.
The two layer models are orthogonal — a Layer-2 receipt can be
produced by an Authoritative or an Evidentiary surface; a Layer-3
projection of authoritative ledger state is itself neither
authoritative nor evidentiary in the function axis. Conflating storage
and function is the named risk this ADR closes.

The doctrine codified here is the **prerequisite** for ADR-0.0.39
(LLM-as-judge doctrine) and ADR-0.0.40 (judge enforcement validators).
Both descend from the survey-aligned framework in
[arxiv 2411.15594 — *From Generation to Judgment*](https://arxiv.org/abs/2411.15594)
and [llm-as-a-judge.github.io](https://llm-as-a-judge.github.io/), but
neither lands cleanly without the function-axis taxonomy this ADR names
first.

## Decision

Codify a **three-category function-axis taxonomy** for every gzkit
surface that emits output a caller acts on. The categories are
exhaustive (every surface fits exactly one) and mutually exclusive
(a surface that genuinely produces both binding and advisory output
is two surfaces, classified separately).

### The three categories

| Category | Definition | Caller contract | Canonical examples |
|---|---|---|---|
| **Authoritative** | Output binds gate decisions. A non-zero exit code, a `False` return, or a `passed=False` receipt MUST stop the calling pipeline. Callers may not "consider and proceed." | Fail-closed. | `gz validate --*` (every scope), schema validators in `src/gzkit/schemas/`, ARB canonical-step floor (`src/gzkit/arb/validator.py`), ledger reconciliation, `_enforce_human_attestation_authenticity` and `_requires_human_obpi_attestation` (`src/gzkit/commands/adr_audit.py`), `_enforce_req_coverage_gate` (`src/gzkit/commands/obpi_complete.py`), pre-commit hooks in `.gzkit/hooks/` |
| **Evidentiary** | Output informs operator judgment but never binds. Findings produce a receipt or report; operator decides accept / revise / reject. Callers MUST NOT branch on Evidentiary output as a fail-closed gate. | Advisory; receipt cited in attestation. | `gz-plan-audit` findings, `gz-adr-evaluate` scores (the 8-dim ADR / 5-dim OBPI rubric), `gz-tech-debt-review` reports, `gz-obpi-simplify` recommendations, runtime `advisor()` tool, the to-be-promoted LLM-as-judge surfaces (advisory-judge-surface, attestation-advisory-agent, lightweight-pre-implementation-challenger) |
| **Projection** | Layer-3 derived view that **presents** Layer-1 canon or Layer-2 ledger truth. Neither binds nor advises directly — the underlying truth advises or binds; the projection only renders. Callers reading a Projection MUST trace through to Layer-1 / Layer-2 to ground any decision. | Read-only render of authoritative ledger state. | `gz status` table output, `docs/governance/GovZero/adr-status.md`, `gz state` graph projections, reconciliation caches under `artifacts/reconcile/`, the `gz-adr-status` and `gz-state` skill outputs, every command surface that takes Layer-2 ledger events and renders them as a table or tree |

### Non-categories (deliberate exclusions)

- A surface that produces **only logs** (no receipt, no exit-code semantics consumed by a caller) is not in scope. Logging is observability, not a function-axis surface.
- A surface that produces **only Layer-1 canon** (a `.gzkit/rules/` rule file, an ADR document, a schema definition) is itself the truth, not a function-axis surface that emits output. The validator that **reads** the rule file is the function-axis surface; the rule file is its authoritative input.

### The four binding rules (every surface MUST honor)

1. **Declare-axis-at-authoring.** Every new surface declares its axis at authoring time. Declaration sites by surface kind:
   - **Skills** (`.gzkit/skills/<name>/SKILL.md`): YAML frontmatter field `surface_axis: {authoritative,evidentiary,projection}`.
   - **Rules** (`.gzkit/rules/<name>.md`): body-level marker `<!-- surface-axis: <axis> -->` immediately after the version marker (per the body-marker convention from skill-surface-sync rule v0.2.0).
   - **Validator scopes** (`gz validate --<scope>`): registered in the validator-scope registry at `src/gzkit/governance/trust_audits.py` (or successor module) with an `axis` field on each registered scope. Default axis for `gz validate --*` is **authoritative** unless explicitly overridden.
   - **Code-level functions** that emit receipts or fail-closed exit codes: module-level constant `SURFACE_AXIS: Final[str] = "<axis>"` declared once per module that emits, validated by introspection.
   - **CLI verbs** (`gz <verb>`) whose default human-readable output an operator acts on: declared in the CLI parser registration with an `axis` field.

2. **Promotion-requires-foundation-ADR.** Promotion from Evidentiary to Authoritative — i.e., a previously advisory surface becoming a fail-closed gate — requires a new foundation-kind ADR justifying the promotion. Silent uptake by a calling skill (an evaluator's score becoming a pass/fail check inside `gz-adr-audit`) is the named drift class this rule closes. The reverse demotion (Authoritative → Evidentiary) also requires foundation-kind ADR; an authoritative surface cannot be silently weakened to advisory.

3. **Projection-MUST-NOT-bind.** A caller reading a Projection-tagged surface MUST trace to the underlying Layer-1 / Layer-2 source for any decision-binding inference. Treating a Projection surface as Authoritative — branching on its rendered text, exit-code-checking a status renderer, gating a release on `adr-status.md` markdown — is a doctrine violation detectable by axis mismatch in the call graph. Architectural Boundary 6 names the failure shape; this rule names the prevention.

4. **Receipt-shape-shared, binding-distinct.** Authoritative and Evidentiary surfaces both emit ARB-shaped receipts (model, prompt-hash, input-hash, output, exit status, timestamp). The receipt-ID contract is shared. The **binding semantics** are not: an Authoritative receipt with `passed=False` halts a pipeline; an Evidentiary receipt with `verdict=concerns-raised` produces a finding the operator weighs. Citing a receipt in attestation does not promote it from Evidentiary to Authoritative — citation is provenance, not binding.

### Foundation rule deliverable

A new canonical rule file at `.gzkit/rules/evidence-vs-authority.md`,
authored under OBPI-0.0.38-01 and registered in the advisory-rules-audit
scorecard at `docs/governance/advisory-rules-audit.md`. The rule file is
the single addressable home for the four rules above; the table in this
ADR is a readable projection.

### Validator deliverable

A new mechanical validator scope `gz validate --surface-axis` (Heavy lane —
new CLI surface), authored under OBPI-0.0.38-02. The scope fail-closes on:

- Any surface (skill, rule, validator scope, declared CLI verb, receipt-emitting module) lacking an axis declaration.
- Any caller treating a Projection-tagged surface as fail-closed gate input (detected by call-graph analysis of `subprocess.run(["gz", "status", ...]).returncode`-style patterns and equivalent shapes).
- Any commit that promotes a previously-Evidentiary surface to Authoritative without a referenced foundation-kind ADR in the commit body or in the surface's declaration site.

### Retroactive classification deliverable

A one-time audit pass under OBPI-0.0.38-03 classifying every existing
surface, emitting a `surface_axis_classified` ledger event per surface,
and producing the baseline audit at
`artifacts/audits/surface-axis-2026-05-06.md`. The audit is the snapshot;
the rule file and the validator are the going-forward enforcement.

### Sequencing into ADR-0.0.39 and ADR-0.0.40

ADR-0.0.39 (LLM-as-judge doctrine) and ADR-0.0.40 (judge enforcement
validators) are committed-to as the next two foundation ADRs in the
trajectory. ADR-0.0.39 imports the Evidentiary category from this ADR
and adds LLM-as-judge-specific invariants (three-axis what/how/where
declaration, named bias roster, methodology menu, explanation-then-verdict,
meta-evaluation cadence). ADR-0.0.40 adds the judge-specific validators
(`gz validate --judge-leakage`, `gz validate --judge-output-discipline`,
`gz judge meta-eval`). Neither lands until 0.0.38 is closed out.

## Rationale

Three claims drive the function-axis taxonomy and the four binding
rules.

**Claim 1 — Doctrine fragmentation is invariant fragmentation.** Six
existing or proposed surfaces (`gz-plan-audit`, `gz-adr-evaluate`,
`gz-tech-debt-review`, advisory-judge-surface, attestation-advisory-agent,
lightweight-pre-implementation-challenger) each name their own
"advisory, never gating" boundary in their own SKILL or pool sketch.
Without a single named foundation rule, every new surface re-derives
the boundary, and the marginal cost of one surface drifting to
gate-shape is small but the cumulative risk over a two-year planning
window is non-trivial. The anti-vibing mantra (AGENTS.md) names doctrine
drift as invariant drift; this ADR is the mechanical defense at the
function-axis layer.

**Claim 2 — Projection is the missing third category.** State-doctrine
already names Layer-3 derived views as "never source-of-truth" — the
storage axis. But a Layer-3 view can still be **read** as authoritative
by a caller (Architectural Boundary 6: *"do not let derived views
silently become source-of-truth"*). The storage rule prevents Layer-3
from holding truth; the function rule must additionally prevent
callers from treating Layer-3 output as gate-binding. Folding
Projection into Evidentiary would lose that distinction — Evidentiary
surfaces produce *new* judgment-informing output; Projection surfaces
produce *renderings* of existing canonical truth. They have different
provenance contracts and different repair paths when wrong (Evidentiary:
re-judge; Projection: regenerate from source).

**Claim 3 — Receipt-shape sharing is intentional, binding-semantics
sharing would be the failure mode.** ARB-shaped receipts are emitted
identically by Authoritative and Evidentiary surfaces because the
provenance contract (model, prompt-hash, input-hash, output, exit
status) is shared. What is not shared is the **caller's contract**:
Authoritative receipts halt pipelines; Evidentiary receipts inform.
The named risk is a calling skill that reads an Evidentiary receipt's
non-pass status as if it were Authoritative — i.e., promoting a
finding to a gate by inheritance through the receipt shape. Rule 4
("receipt shape shared, binding distinct") is the explicit floor
against this drift.

**Why this is foundation-kind.** The taxonomy applies to every gzkit
surface that emits output. It is invariant-shaped — naming a binding
character that every caller and every author must honor. Per
ADR-0.0.18, foundation-kind is reserved for app/system invariants;
this qualifies. Foundation-kind triggers brief-level human attestation
(per the lane × kind matrix) — appropriate, because mis-classification
of a high-stakes surface (e.g., classifying `gz validate --documents`
as Evidentiary) would silently weaken the gate fabric.

**Why heavy lane.** OBPI-0.0.38-02 introduces a new validator scope
(`gz validate --surface-axis`), which is a CLI/contract surface change.
Heavy lane is the canonical trigger per AGENTS.md § Gate Covenant. Lite
lane would skip the BDD verification (Gate 4) and the docs-tracks-code
covenant (Gate 3); both are needed when a new validator scope ships.

**Exemplars and precedents.** The shape of this ADR follows several
established gzkit patterns:

- **ADR-0.0.9 (state-doctrine-source-of-truth)** is the directly
  parallel exemplar — it codifies the storage axis (Layer 1 / 2 / 3)
  with a body rule (`docs/governance/state-doctrine.md`) and validator
  enforcement. This ADR is the function-axis sibling, deliberately
  patterned on 0.0.9's storage-axis architecture: orthogonal axes,
  shared receipt-shape, distinct enforcement validators.
- **ADR-0.0.22 (security-sensitivity-doctrine)** is the architectural
  precedent for adding a third orthogonal axis to gzkit's classification
  fabric. It codified `sensitivity` as the third axis alongside `kind`
  and `lane`, with a registry (`data/security_surfaces.json`), a body
  rule (`.gzkit/rules/security-sensitivity.md`), and a validator scope
  (`gz validate --sensitivity`). The structural shape — registry +
  rule + validator + retroactive classification audit + Gate 5
  walkthrough extension — is the model this ADR follows. The
  `data/surface_axis_inventory.json` artifact this ADR proposes is the
  same shape as `data/security_surfaces.json`; the
  `gz validate --surface-axis` scope is the same shape as
  `gz validate --sensitivity`.
- **ADR-0.0.27 (exemplar-corpus-doctrine)** is the precedent for
  brief-level human attestation on foundation-kind ADRs. It established
  the matrix where foundation-kind always requires Gate 5 walkthrough
  at OBPI close, regardless of lane. This ADR inherits that matrix
  unchanged; OBPI-0.0.38-03's Gate 5 walkthrough specifically extends
  the security-sensitivity walkthrough pattern (sample-classification
  prompt, receipt-confirmation, classification-confirmation) to the
  function-axis surface.
- **ADR-0.0.18 (adr-taxonomy-doctrine)** is the precedent for
  orthogonal classification axes (kind × lane). This ADR's three
  function-axis categories are orthogonal to ADR-0.0.18's kind-axis,
  ADR-0.0.22's sensitivity-axis, and ADR-0.0.9's storage-axis — gzkit's
  classification fabric is now four-axis (kind, lane, sensitivity,
  function), each closing a distinct failure class.

The pattern across all four exemplars: **named axis → registry → rule →
validator → retroactive baseline → Gate 5 walkthrough.** This ADR
follows that pattern fully; OBPI-0.0.38-01/02/03 land each layer in
sequence.

## Comparator Uplift (2026-05-07)

Specmatic-style executable contracts and GSD-style workflow receipts both make
the same demand: authority must project from evidence, not from tool branding.
This ADR should classify comparator references as low authority until they are
backed by gzkit-local receipts, tests, validators, or ledger events. A borrowed
pattern becomes authoritative only through local evidence projection.

## Consequences

### Positive

- **Closes doctrine fragmentation across at least six existing and proposed surfaces.** Every surface inherits its function axis from one rule file, not from re-derived boundary sketches.
- **Closes Architectural Boundary 6 mechanically.** The Projection category gives the call-graph analyzer a tag to detect "Projection consumed as gate input" without conflating with state-doctrine's storage axis.
- **Unblocks the LLM-as-judge ADR-0.0.39 and validator ADR-0.0.40.** Both depend on the Evidentiary category being foundation-codified rather than per-surface-asserted.
- **Strengthens advisory-rules-audit scorecard mechanically.** The new rule registers a Mechanical (validator-enforced) entry, not a Promotable-but-unpromoted entry — the scorecard's named anti-pattern.
- **Provides a one-time baseline of every classified surface,** which becomes the canonical inventory the validator scopes against and which downstream ADRs can cite.

### Negative

- **Retroactive classification labor at promotion.** OBPI-0.0.38-03 must classify every existing surface — likely 80–150 entries by the time receipt-emitting code-level functions and Layer-3 projections are counted. The labor is bounded (one-shot) but non-trivial.
- **New validator scope to maintain.** `gz validate --surface-axis` is one more scope in the Heavy-lane bundle; every future surface must declare its axis, raising the floor of authoring discipline.
- **Risk of false-flag during retroactive classification.** A handful of existing surfaces have hybrid behavior (e.g., `gz-plan-audit` mostly produces advisory findings but exits non-zero on a small set of structural failures). The taxonomy says "two surfaces" — but in practice this requires either splitting the implementation or carrying both axes in the declaration with documented branch points. OBPI-0.0.38-03 will surface these and propose resolution.

### Risks

- **Misclassification of a high-stakes surface.** Classifying `gz validate --documents` as Evidentiary would silently weaken the gate fabric. Mitigation: Gate 5 brief-level human attestation on OBPI-0.0.38-03 per the foundation-kind matrix; the operator reviews the classification table before the audit ledger event lands.
- **Validator false-positive on legitimate Projection-as-input cases.** The call-graph analyzer in OBPI-0.0.38-02 must distinguish "Projection consumed as gate" (failure) from "Projection consumed as data source then re-derived from Layer-2" (legitimate). Mitigation: explicit waiver list on the validator scope, with each waiver requiring a named-and-cited reason — same pattern as `_UTF8_PIPE_WAIVERS` per the cross-platform rule.
- **Trajectory commitment.** This ADR commits to ADR-0.0.39 and ADR-0.0.40 as the next two ADRs in the foundation line. If subsequent operator priority shifts, the doctrine still stands but the validator infrastructure is incomplete; the rule remains advisory-on-paper-but-mechanical-by-axis-declaration until 0.0.40 closes.

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

- [ ] OBPI-0.0.38-01: **rule-and-schema** — Author the canonical rule file at `.gzkit/rules/evidence-vs-authority.md` codifying the three-axis taxonomy (Authoritative / Evidentiary / Projection); register the rule in the advisory-rules-audit scorecard; define the axis-declaration schema fields surfaces must carry (frontmatter for skills/rules; module-level constant for code-level surfaces; CLI registration metadata for validator scopes).
- [ ] OBPI-0.0.38-02: **surface-axis-validator** — Implement `gz validate --surface-axis` enumerating every surface against the canonical inventory, fail-closing on (a) any surface missing an axis declaration, (b) any caller treating a Projection-tagged surface as a gate input, (c) any Evidentiary-to-Authoritative promotion lacking a foundation-kind ADR justification.
- [ ] OBPI-0.0.38-03: **retroactive-classification** — One-time audit pass classifying every existing skill, rule, validator scope, code-level fail-closed function (e.g. `_enforce_human_attestation_authenticity`), and Layer-3 derived view (e.g. `gz status` output, `docs/governance/GovZero/adr-status.md`); emit a `surface_axis_classified` ledger event per surface naming axis + rationale; produce `artifacts/audits/surface-axis-2026-05-06.md`.

## Target Scope

- **rule-and-schema** — Author the canonical rule file at `.gzkit/rules/evidence-vs-authority.md` codifying the three-axis taxonomy (Authoritative / Evidentiary / Projection); register the rule in the advisory-rules-audit scorecard; define the axis-declaration schema fields surfaces must carry (frontmatter for skills/rules; module-level constant for code-level surfaces; CLI registration metadata for validator scopes).
- **surface-axis-validator** — Implement `gz validate --surface-axis` enumerating every surface against the canonical inventory, fail-closing on (a) any surface missing an axis declaration, (b) any caller treating a Projection-tagged surface as a gate input, (c) any Evidentiary-to-Authoritative promotion lacking a foundation-kind ADR justification.
- **retroactive-classification** — One-time audit pass classifying every existing skill, rule, validator scope, code-level fail-closed function (e.g. `_enforce_human_attestation_authenticity`), and Layer-3 derived view (e.g. `gz status` output, `docs/governance/GovZero/adr-status.md`); emit a `surface_axis_classified` ledger event per surface naming axis + rationale; produce `artifacts/audits/surface-axis-2026-05-06.md`.

## Notes

Promotion ordering: this ADR should promote **before** the two pool
ADRs that depend on it (`solved-problem-pattern-corpus`,
`advisory-judge-surface`). Both reference the four-invariant frame
this doctrine names; without it, their invariants are local rather
than inherited.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.evidence-vs-authority-doctrine` on 2026-05-06; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Rule file: `.gzkit/rules/evidence-vs-authority.md` (authored under OBPI-0.0.38-01)
- [ ] Advisory-rules-audit registration: `docs/governance/advisory-rules-audit.md` (registered under OBPI-0.0.38-01)
- [ ] Validator scope: `gz validate --surface-axis` (implemented under OBPI-0.0.38-02)
- [ ] Validator tests: `tests/governance/test_surface_axis_validator.py` (authored under OBPI-0.0.38-02)
- [ ] BDD scenarios: `features/governance/surface_axis.feature` (authored under OBPI-0.0.38-02; Heavy lane Gate 4)
- [ ] Retroactive classification audit: `artifacts/audits/surface-axis-2026-05-06.md` (produced under OBPI-0.0.38-03)
- [ ] Ledger events: `surface_axis_classified` (one per surface, emitted under OBPI-0.0.38-03)
- [ ] Operator runbook update: `docs/user/runbook.md` — `gz validate --surface-axis` workflow added
- [ ] Governance runbook update: `docs/governance/governance_runbook.md` — surface classification protocol added
- [ ] Manpage: `docs/user/manpages/gz-validate.md` — `--surface-axis` scope documented
- [ ] Three-axis taxonomy table: see § Decision in this ADR
- [ ] OBPI briefs: OBPI-0.0.38-01-rule-and-schema, OBPI-0.0.38-02-surface-axis-validator, OBPI-0.0.38-03-retroactive-classification

## Alternatives Considered

1. **Two-category taxonomy (Authoritative / Evidentiary only).** The pool sketch's original shape. Rejected: leaves Architectural Boundary 6 (Layer-3 silent promotion to source-of-truth) with no function-axis defense. State-doctrine bans Layer-3 from being source-of-truth (storage axis); without the Projection category, nothing bans Layer-3 from being read as Authoritative-binding (function axis). The two failures are on different axes — closing one does not close the other. The maxim disqualifies "smaller taxonomy" as a concrete downside; the failure-class scoreboard showed three closed by two-category, four closed by three-category, no concrete cost to the third.

2. **Single-binary axis (binds gates / does not bind gates).** Rolls Projection back into "does not bind gates" alongside Evidentiary. Rejected for the same reason as (1) — the binary obscures the provenance distinction (Evidentiary produces new judgment-informing output; Projection renders existing canonical truth) and the repair path distinction (Evidentiary: re-judge; Projection: regenerate from source). A caller reading "does not bind" cannot distinguish whether they should escalate to operator judgment (Evidentiary) or re-derive from Layer-2 ledger (Projection).

3. **Encode the distinction inside each surface's `SKILL.md` without a foundation rule.** The pool sketch's named alternative #2. Rejected: local declaration without a global rule leaves the cross-cutting invariant unenforced; advisory-rules-audit scorecard cannot grade against a missing rule. This was named in the pool ADR; ratified here.

4. **Fold into the storage-tier state-doctrine.** The pool sketch's named alternative #3. Rejected: conflates orthogonal axes. A Layer-2 receipt can be produced by an Authoritative or an Evidentiary surface; a Layer-3 projection of authoritative ledger state is in neither function category cleanly. Storage tier and binding authority are different questions; this ADR's job is the function axis, not the storage axis.

5. **Defer to ADR-0.0.39 (LLM-as-judge doctrine) and codify the distinction inside the LLM-judge-specific frame.** Rejected: at least three Evidentiary surfaces (`gz-plan-audit`, `gz-tech-debt-review`, `gz-obpi-simplify`) are not LLM-as-judge surfaces but still need the same function-axis discipline. Folding the doctrine into the LLM-judge ADR would either fragment again (other Evidentiary surfaces re-derive their boundary) or expand ADR-0.0.39 beyond its named scope.

6. **Skip the validator (`gz validate --surface-axis`); ship the rule only.** Rejected as the canonical Promotable-but-unpromoted anti-pattern named in `docs/governance/advisory-rules-audit.md`. Shipping a foundation rule whose key invariants ("declare axis," "no Projection-as-gate-input," "promotion requires foundation ADR") have no validator firing manufactures a fresh advisory-only rule on a surface where Mechanical enforcement is feasible. The maxim ("the most thorough fix is always preferred") disqualifies this.

7. **Skip the retroactive classification; classify lazily as surfaces are next-touched.** Rejected: leaves the existing ~80–150 surfaces with no axis declarations until each is independently edited, which may take months or years. The validator from OBPI-0.0.38-02 cannot fail-close on missing declarations until the baseline exists; lazy classification means the validator is advisory-only at landing, which reproduces the Promotable-unpromoted anti-pattern at the classification layer.

8. **Wait for the validator infrastructure (ADR-0.0.40 territory) before promoting this ADR.** Rejected: doctrine before tooling is the gzkit ordering. ADR-0.0.39 explicitly depends on this ADR's Evidentiary category being foundation-codified; deferring this ADR pushes 0.0.39 out by the same amount and leaves the in-flight pool ADRs (advisory-judge-surface, etc.) blocked on doctrine they cannot inherit yet.

9. **Keep this work in the pool backlog until reprioritized.** Rejected per the explicit promotion-ordering note in the pool ADR's Notes section: the rule must promote before the dependent pool ADRs (`solved-problem-pattern-corpus`, `advisory-judge-surface`) can land cleanly. Operator authorized "DO IT RIGHT, MAX OUT" — keeping in pool was the deferred state this directive overrode.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.38 | Pending | | | |
