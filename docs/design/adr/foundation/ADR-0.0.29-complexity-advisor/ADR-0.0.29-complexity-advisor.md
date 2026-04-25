---
id: ADR-0.0.29
status: Draft
kind: foundation
semver: 0.0.29
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-25
---

# ADR-0.0.29: Complexity Advisor

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats the advisor as the trigger-time doctrinal-frame surface, not as a numeric reporter — every diagnosis carries an authority citation, a refactor archetype, and a proof range linking to AST nodes / line ranges. Refuses plausible-looking advice without traceable evidence (the verdict ↔ proof binding is the same shape as AGENTS.md § Attestation's receipt-ID requirement applied at the diagnosis-time layer). Distinguishes the auto-chain pathway (load-bearing trigger from xenon-as-gate failure) from the ad-hoc pathway (preview-before-fail per OEE doctrine); the two paths have distinct presentation defaults and are tested independently. Honors the two-path intrinsic-complexity attestation as the 2am Scenario-3 amelioration: a function whose complexity is irreducibly algorithmic gets either a `@intrinsic_complexity` decorator OR a commit-time `--attest-intrinsic` flag with Gate 5 follow-up — neither path produces a silent escape hatch. Reads pre-commit timeout / fail-open as the 2am Scenario-1 amelioration: the advisor never blocks a developer's commit indefinitely; failure logs at `.gzkit/insights/advisor-failures.jsonl`.

This ADR is the third foundation in the four-ADR complexity-doctrine cluster (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30) and the largest single-ADR ceremony in the cluster (nine OBPIs). The advisor consumes ADR-0.0.27 OBPI-04's distilled-characteristics document and ADR-0.0.28-02's `ThresholdTable` model directly — neither is reimplemented; both are imported. The advisor is the trigger-time response surface ADR-0.0.30 (authoring-guidance, the cluster's fourth foundation) builds on as the upstream-prevention complement.

## Intent

When a metric crosses the `warn` band per ADR-0.0.28's threshold table, the developer needs a structured diagnosis: which authority (Fowler *Refactoring* 2e, Martin SOLID, Page-Jones connascence taxonomy, Constantine coupling/cohesion modes — the diagnostic vocabulary canonized in ADR-0.0.27) speaks to this kind of complexity, what refactor archetype applies (Long Parameter List → Parameter Object, Arrowhead → Guard Clauses, Switch-on-Type → Polymorphism, Feature Envy → Move Method, etc.), what specific lines or AST nodes are responsible, and what the recommended next move is. Without ADR-0.0.29, the developer gets a number (`CC=14`) and no doctrinal frame for action — the canonical training-corpus failure mode the MAKE LLM STOCHASTIC VIBES INERT mantra forbids at the trigger-time response layer. The advisor is the trigger-time response surface that closes that gap.

The advisor is the third foundation in the four-ADR complexity-doctrine cluster (ADR-0.0.27 corpus / 0.0.28 thresholds / 0.0.29 advisor / 0.0.30 authoring-guidance). It auto-chains from xenon-as-gate failure (per the operator's locked decision: triggered design responses fire when the xenon threshold trips) and is also operator-invocable ad-hoc. Auto-chain is the structural defense against the "advisor exists but never fires" failure class; ad-hoc invocation is the operator-bandwidth-protection for preview-before-fail.

The advisor consumes ADR-0.0.28's `ThresholdTable` for band classification and ADR-0.0.27 OBPI-04's distilled-characteristics document for doctrinal-frame attribution. It does NOT reimplement either; it imports the model and parses the cited document. The verdict ↔ proof binding (OBPI-08) is the structural defense against the "advisor recommends but cannot show why" failure class — every diagnosis carries a `proof` field linking to the AST nodes / line ranges responsible, so the operator can audit the advisor's reasoning at trigger time.

The two-path intrinsic-complexity attestation (OBPI-07) is the 2am Scenario-3 amelioration locked in the design dialogue: a function whose complexity is irreducibly algorithmic (e.g. CC=24 in a query optimizer's join-cost calculator) gets a `@intrinsic_complexity(reason=..., attestor=...)` decorator that the advisor honors at diagnosis time, OR an in-flight commit-time `--attest-intrinsic` flag that records the attestation with Gate 5 follow-up persistence. Both paths land at brief-level Gate 5; neither path produces a silent escape hatch. The pre-commit timeout / fallback / failure-logging (OBPI-09) is the 2am Scenario-1 amelioration: the advisor itself must time out gracefully and never block the operator's commit indefinitely, with failure logged for later operator review.

## Decision

Codify the advisor as one CLI verb (`gz complexity-advise`), one operator-runnable skill (`complexity-advisor`), one diagnosis engine bound to ADR-0.0.28's `ThresholdTable` + ADR-0.0.27 OBPI-04's distilled-characteristics document, with auto-chain from xenon-as-gate failure preserving SKIP-bypass guard wiring, two-path intrinsic-complexity attestation, verdict ↔ proof binding, and pre-commit timeout / fallback / failure-logging.

**Rationale (numbered, binding):**

1. The advisor consumes the `ThresholdTable` model directly, not a JSON re-parse, **because** the parser-divergence drift class is closed at the ADR-0.0.28-02 layer; reimplementing the parse here introduces a vibing surface (training-corpus pattern-matching against possibly-different field names) the cluster's mantra forbids.
2. The diagnostic vocabulary is restricted to the four canonical authorities (Fowler / Martin / Page-Jones / Constantine), **because** the corpus methodology in ADR-0.0.27 binds these as the cluster's authority canon; admitting a fifth authority requires foundation-kind ceremony (corpus refresh, distillation, citation update) — the rationale is inherited verbatim.
3. Auto-chain from xenon-as-gate failure is the load-bearing trigger, **because** an advisor that requires manual invocation has the same failure shape as a validator that exists but never fires (the OBPI-0.0.27-07 link-integrity-validator rationale applied to the trigger-time surface). The operator's locked decision in the handoff ratifies this.
4. Operator-invocable ad-hoc path is preserved alongside auto-chain, **because** preview-before-fail is the operator-bandwidth-protection move (the OEE doctrine's "agent drafts substantively, operator reviews" shape applied to the developer's pre-commit moment).
5. Verdict ↔ proof binding is mandatory on every diagnosis, **because** an advisor that recommends without showing why is the same training-corpus failure mode the mantra forbids — the proof field linking to AST nodes / line ranges is the structural defense against "plausible-looking advice with no traceable evidence". The justification mirrors AGENTS.md § Attestation's receipt-ID requirement at the diagnosis-time layer.
6. Two-path intrinsic-complexity attestation closes the 2am Scenario-3 reality (CC=24 ship-now), **because** a one-path attestation (decorator-only) excludes commit-time attestation and forces the developer to amend code before commit even when the complexity is genuinely irreducible; a one-path attestation (commit-time-only) excludes pre-attested invariants and forces re-attestation per commit. Both paths land at Gate 5; neither produces a silent escape hatch.
7. Pre-commit timeout / fallback / failure-logging closes the 2am Scenario-1 reality (advisor itself hangs), **because** an advisor whose own failure blocks the operator's commit indefinitely is the worst possible operator-experience failure class — the timeout + fail-open-with-log pattern is the structural defense.
8. Nine OBPIs is the right size, **because** each codifies one distinct invariant (schema, engine, CLI, skill, auto-chain, ad-hoc, attestation, proof, timeout); bundling produces one Gate 5 witness for nine separable concerns; over-fragmenting produces ceremony without invariant addition. The nine-OBPI count is locked from the design dialogue's MAX DO IT RIGHT-maxxing decomposition pass.

**The invariant (canonical statement):** gzkit publishes one canonical complexity advisor whose every diagnosis cites the active distilled-characteristics document and the canonical `ThresholdTable`, carries a `proof` field linking to the responsible AST nodes / line ranges, and respects the two-path intrinsic-complexity attestation. The advisor auto-chains from xenon-as-gate failure (preserving SKIP-bypass guard wiring) and is operator-invocable ad-hoc. Pre-commit timeouts fail open with logging; the advisor never blocks an operator's commit indefinitely.

**Mechanical surfaces (what changes in code):**

- `src/gzkit/complexity/advisor/__init__.py` (new package)
- `src/gzkit/complexity/advisor/diagnosis.py` (new): frozen Pydantic `AdvisorDiagnosis`, `RefactorArchetype` enum, `DoctrinalFrame` model, `ProofRange` model.
- `src/gzkit/complexity/advisor/engine.py` (new): given an AST context + a metric crossing, returns `AdvisorDiagnosis`. Imports `ThresholdTable` (ADR-0.0.28-02) and reads OBPI-0.0.27-04's distilled-characteristics for doctrinal-frame attribution.
- `src/gzkit/complexity/advisor/intrinsic.py` (new): `@intrinsic_complexity` decorator and the runtime registry; commit-time `--attest-intrinsic` flag handling.
- `src/gzkit/complexity/advisor/timeout.py` (new): pre-commit timeout / fallback / failure-logging primitives.
- `src/gzkit/commands/complexity_advise.py` (new): `gz complexity-advise` CLI verb (Heavy-lane new subcommand per `.claude/rules/cli.md`).
- `src/gzkit/cli/parser_artifacts.py`: register the new verb.
- `src/gzkit/schemas/advisor_diagnosis.json` (new): JSON Schema mirror.
- `.gzkit/skills/complexity-advisor/SKILL.md` (new): operator-runnable skill carrying invocation patterns + intrinsic-attestation guidance + auto-chain explanation. Vendor-mirrored.
- `.gzkit/hooks/pre-commit-complexity-advisor` (new): auto-chain hook fired on xenon-as-gate non-zero exit; preserves SKIP-bypass guard wiring.
- `tests/complexity/advisor/**`: REQ-derived assertions across all nine OBPIs.
- `features/complexity_advisor.feature` (new): BDD scenarios tagged `@REQ-0.0.29-NN-MM`.
- `docs/user/manpages/gz-complexity-advise.md` (new): manpage per the gate5-runbook-code-covenant.
- `docs/user/runbook.md`: runbook entry under "Complexity doctrine surfaces".
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the advisor surface.

**Nine OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.29-01 — Advisor diagnosis schema:** Frozen Pydantic `AdvisorDiagnosis`, `RefactorArchetype` enum (initial values: long-parameter-list, arrowhead, switch-on-type, feature-envy, large-class, divergent-change, shotgun-surgery, primitive-obsession, data-clumps, message-chain), `DoctrinalFrame` model (authority + citation + chapter/page anchor), `ProofRange` model (file path + line range + AST node descriptor). JSON Schema mirror at `src/gzkit/schemas/advisor_diagnosis.json`.

**OBPI-0.0.29-02 — Diagnosis engine:** Given an AST context + a metric crossing, returns `AdvisorDiagnosis`. Imports `ThresholdTable` (ADR-0.0.28-02) for band classification; reads OBPI-0.0.27-04's distilled-characteristics for doctrinal-frame attribution. Refactor-archetype detection rules are themselves data-driven (rule table at `data/advisor_archetype_rules.json`) — the rules are doctrine, not code, so amendments flow through the doctrine-amendment-protocol pool stub.

**OBPI-0.0.29-03 — `gz complexity-advise` CLI verb:** Heavy-lane new subcommand per `.claude/rules/cli.md` § "New Subcommand (Heavy Lane)": ADR (this), manpage at `docs/user/manpages/gz-complexity-advise.md`, behave smoke scenario, release-notes entry. Default human output is structured prose; `--json` mode emits the canonical Pydantic model serialization.

**OBPI-0.0.29-04 — `complexity-advisor` skill:** `.gzkit/skills/complexity-advisor/SKILL.md` carrying invocation patterns, intrinsic-attestation guidance, auto-chain explanation, and the OBPI-09 timeout-handling description. Vendor-mirrored. Output Contract declares the destination verb's default form per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3.

**OBPI-0.0.29-05 — Auto-chain from xenon-as-gate failure:** Pre-commit hook at `.gzkit/hooks/pre-commit-complexity-advisor`; fires when xenon-as-gate exits non-zero; preserves SKIP-bypass guard wiring (the existing SKIP semantics from the complexity-reduction-xenon chore are honored unchanged). The hook calls `gz complexity-advise --auto-chain` which signals to the advisor that the invocation is auto-fired (different presentation defaults than ad-hoc).

**OBPI-0.0.29-06 — Operator-invocable ad-hoc path:** `gz complexity-advise <path>` for preview-before-fail. Distinct presentation defaults from auto-chain (verbose preview vs. trigger-time fail-fast). Tested independently from the auto-chain pathway.

**OBPI-0.0.29-07 — Two-path intrinsic-complexity attestation:** `@intrinsic_complexity(reason=..., attestor=...)` decorator (the pre-attested path) and `gz complexity-advise --attest-intrinsic` commit-time flag (the in-flight path). Both paths persist the attestation (decorator: in code; commit-time: in `.gzkit/ledger.jsonl` via canonical event emission). Gate 5 follow-up at brief-level for foundation-kind rigor.

**OBPI-0.0.29-08 — Verdict ↔ proof binding:** Every `AdvisorDiagnosis` carries a non-empty `proof: tuple[ProofRange, ...]` field. The engine fails closed if it cannot produce proof for a diagnosis (no "plausible-looking advice without traceable evidence"). Tested with synthetic AST fixtures.

**OBPI-0.0.29-09 — Pre-commit timeout / fallback / failure-logging:** The pre-commit hook (OBPI-05) wraps the advisor invocation in a configurable timeout (default 30s); on timeout the hook fails open with a logged warning (commit proceeds; defect surface is the log) per the 2am Scenario-1 amelioration. Logs land at `.gzkit/insights/advisor-failures.jsonl`. The fail-open is deliberate: blocking commits on advisor failure is worse than letting them through with a logged warning.

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-08 (proof binding lands with engine) → OBPI-03 → OBPI-04 → OBPI-05 → OBPI-09 (timeout binds with auto-chain) → OBPI-06 → OBPI-07. The diagram is sequential at the schema/engine layer, parallel-able at the surface layer (CLI/skill/hooks).

**Lane: Heavy.** New CLI subcommand + new skill + new pre-commit hook + new ledger event family (intrinsic-attestation events) + new schema. All four trigger heavy-lane rigor per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.18.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the corpus selection methodology — that is ADR-0.0.27's scope.
- Does NOT specify the threshold values or trigger semantics — that is ADR-0.0.28's scope.
- Does NOT author the authoring-time guidance surface — that is ADR-0.0.30's scope.
- Does NOT modify the existing `complexity-reduction-xenon` chore's xenon-as-gate behavior — the chore continues to fire xenon at gate time; this ADR adds the advisor on the failure path, not in place of xenon.
- Does NOT specify the refactor-archetype detection rules' empirical validation — the rules are doctrine; their empirical fit is measured at the next distillation pass per ADR-0.0.27 OBPI-04.
- Does NOT vendor or reimplement xenon — xenon-as-gate remains the chosen substrate per ADR-0.0.28's scope boundary.

## Consequences

### Positive

1. **Trigger-time doctrinal frame replaces opaque numeric verdicts.** When a metric crosses the warn band, the developer gets `(authority, refactor archetype, proof range, recommended move)`, not just `CC=14`. Closes the canonical training-corpus failure mode at the trigger-time response layer.

2. **Auto-chain from xenon-as-gate failure preserves SKIP-bypass wiring.** The existing chore's escape-hatch for known-irreducible code continues to work; the advisor adds diagnosis on the genuine-failure path, not on the SKIP path.

3. **Two-path intrinsic-complexity attestation honors both pre-attested and in-flight cases.** A decorator path for known-irreducible functions; a commit-time path for newly-discovered ones. Both attest at Gate 5; neither produces a silent escape hatch.

4. **Verdict ↔ proof binding closes the "plausible advice without evidence" failure class.** Every diagnosis carries AST nodes / line ranges; the operator can audit the advisor's reasoning at trigger time. Mirrors AGENTS.md § Attestation receipt-ID discipline at the diagnosis-time layer.

5. **Pre-commit timeout / fallback / failure-logging closes the 2am Scenario-1 reality.** The advisor never blocks an operator's commit indefinitely; failure surfaces as a logged warning, not a wedged terminal.

6. **The advisor consumes ThresholdTable directly.** Parser-divergence drift across the cluster is closed at the ADR-0.0.28-02 layer; the advisor binds against the frozen Pydantic model, not a JSON re-parse.

7. **Refactor-archetype detection rules are data-driven doctrine.** The rule table at `data/advisor_archetype_rules.json` is amendable through the doctrine-amendment-protocol pool stub, not silent code edits.

8. **Operator-invocable ad-hoc path enables preview-before-fail.** OEE-doctrine-aligned: the developer can preview advisor diagnosis before xenon would fail it, bandwidth-protecting the commit moment.

9. **Foundation-kind brief-level Gate 5 across nine OBPIs.** Each invariant gets independent witness per ADR-0.0.18; the cluster's mantra (ceremony is the deliverable) holds at the largest single ADR in the cluster.

10. **The cluster's third-of-four foundation lands as the trigger-time response surface.** Every layer below it (corpus, threshold) is consumed, not relitigated; every layer above (authoring-guidance) consumes its diagnostic schema.

### Negative

1. **Nine OBPIs is the largest single-ADR ceremony in the cluster.** Operator bandwidth cost is real; bounded by the foundation-kind decomposition discipline (each OBPI is a separable invariant, not a fragmentation move).

2. **Refactor-archetype detection rules are heuristic.** First-distillation cold-start (per ADR-0.0.27 § Negative #9) means the initial rule table is calibrated against literature canon, not against measured archetype-frequency in the corpus. Future distillation passes can refine the rules' empirical fit.

3. **The advisor binds to ADR-0.0.27 OBPI-04 + ADR-0.0.28-02.** Citation-graph density is acknowledged; the link-integrity validator (OBPI-0.0.27-07) is the structural defense.

4. **Auto-chain hook adds pre-commit time.** Real cost in seconds; bounded by OBPI-09's timeout (default 30s with fail-open). Acceptable per the mantra (5:1 governance-to-output ratio is the product).

5. **Commit-time intrinsic-attestation requires ledger event emission.** Every `--attest-intrinsic` invocation emits an `intrinsic-complexity-attestation` ledger event; the event family extends the ledger schema (managed within OBPI-07). Forward-cost: every future ADR consuming intrinsic-attestation events binds against the schema.

6. **Pre-commit hook interaction with developer git workflows is fragile.** Hooks that fail silently or hang frustrate developers; OBPI-09's timeout/fallback/log is the structural defense, but pre-commit-hook interaction is genuinely difficult to make perfectly invisible. Mitigation: the auto-chain hook is opt-in (operator installs it explicitly), not auto-applied at `gz init`.

7. **Default 30s timeout may be too long or too short for some codebases.** Configurable via `.gzkit/config` per the cluster's existing config conventions; calibration against operator workflows is a forward-iteration concern.

8. **The intrinsic-attestation decorator persists in code.** A function decorated with `@intrinsic_complexity` remains attested across rebases/refactors — but if the function changes shape (e.g. CC drops from 24 to 12 after refactoring), the attestation is stale doctrine. Pool stub forward-reference: a future `gz validate --intrinsic-attestation-current` scope would close the stale-attestation failure class.

9. **Verdict ↔ proof binding requires AST traversal at diagnosis time.** Performance cost on large modules; bounded by the metric-crossing precondition (the advisor only fires on warn-or-block crossings, not on every commit). Future optimization (caching parsed ASTs) is a downstream-OBPI concern.

10. **Foundation-kind attestation across nine OBPIs.** Attestation fatigue across nine Gate 5 walkthroughs is a real operator cost; pool stub `ADR-pool.attestation-quality-measurement` is the forward-reference if it materializes (the same forward-reference ADR-0.0.27 § Negative #5 named).

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
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 9

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.29-01 — Advisor diagnosis schema (frozen Pydantic AdvisorDiagnosis, RefactorArchetype enum, DoctrinalFrame, ProofRange; JSON Schema mirror)
- [ ] OBPI-0.0.29-02 — Diagnosis engine (binds ThresholdTable + distilled-characteristics; refactor-archetype rules data-driven at data/advisor_archetype_rules.json)
- [ ] OBPI-0.0.29-03 — `gz complexity-advise` CLI verb (Heavy-lane new subcommand: ADR + manpage + smoke + release notes)
- [ ] OBPI-0.0.29-04 — `complexity-advisor` skill (vendor-mirrored; Output Contract declared; auto-chain + ad-hoc + intrinsic-attestation guidance)
- [ ] OBPI-0.0.29-05 — Auto-chain from xenon-as-gate failure (pre-commit hook; preserves SKIP-bypass guard wiring)
- [ ] OBPI-0.0.29-06 — Operator-invocable ad-hoc path (preview-before-fail; distinct presentation defaults from auto-chain)
- [ ] OBPI-0.0.29-07 — Two-path intrinsic-complexity attestation (`@intrinsic_complexity` decorator + `--attest-intrinsic` commit-time flag; both Gate 5 follow-up)
- [ ] OBPI-0.0.29-08 — Verdict ↔ proof binding (every diagnosis carries non-empty proof: tuple[ProofRange, ...]; engine fails closed if proof unavailable)
- [ ] OBPI-0.0.29-09 — Pre-commit timeout / fallback / failure-logging (default 30s; fail-open with log to `.gzkit/insights/advisor-failures.jsonl`)

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-04-25T15:25:49.433403*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.29

### Q: What is the title of this ADR?

**A:** Complexity Advisor

### Q: What is the semantic version?

**A:** 0.0.29

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** When a metric crosses the `warn` band per ADR-0.0.28's threshold table, the developer needs a structured diagnosis: which authority (Fowler *Refactoring* 2e, Martin SOLID, Page-Jones connascence taxonomy, Constantine coupling/cohesion modes — the diagnostic vocabulary canonized in ADR-0.0.27) speaks to this kind of complexity, what refactor archetype applies (Long Parameter List → Parameter Object, Arrowhead → Guard Clauses, Switch-on-Type → Polymorphism, Feature Envy → Move Method, etc.), what specific lines or AST nodes are responsible, and what the recommended next move is. Without ADR-0.0.29, the developer gets a number (`CC=14`) and no doctrinal frame for action — the canonical training-corpus failure mode the MAKE LLM STOCHASTIC VIBES INERT mantra forbids at the trigger-time response layer. The advisor is the trigger-time response surface that closes that gap.

The advisor is the third foundation in the four-ADR complexity-doctrine cluster (ADR-0.0.27 corpus / 0.0.28 thresholds / 0.0.29 advisor / 0.0.30 authoring-guidance). It auto-chains from xenon-as-gate failure (per the operator's locked decision: triggered design responses fire when the xenon threshold trips) and is also operator-invocable ad-hoc. Auto-chain is the structural defense against the "advisor exists but never fires" failure class; ad-hoc invocation is the operator-bandwidth-protection for preview-before-fail.

The advisor consumes ADR-0.0.28's `ThresholdTable` for band classification and ADR-0.0.27 OBPI-04's distilled-characteristics document for doctrinal-frame attribution. It does NOT reimplement either; it imports the model and parses the cited document. The verdict ↔ proof binding (OBPI-08) is the structural defense against the "advisor recommends but cannot show why" failure class — every diagnosis carries a `proof` field linking to the AST nodes / line ranges responsible, so the operator can audit the advisor's reasoning at trigger time.

The two-path intrinsic-complexity attestation (OBPI-07) is the 2am Scenario-3 amelioration locked in the design dialogue: a function whose complexity is irreducibly algorithmic (e.g. CC=24 in a query optimizer's join-cost calculator) gets a `@intrinsic_complexity(reason=..., attestor=...)` decorator that the advisor honors at diagnosis time, OR an in-flight commit-time `--attest-intrinsic` flag that records the attestation with Gate 5 follow-up persistence. Both paths land at brief-level Gate 5; neither path produces a silent escape hatch. The pre-commit timeout / fallback / failure-logging (OBPI-09) is the 2am Scenario-1 amelioration: the advisor itself must time out gracefully and never block the operator's commit indefinitely, with failure logged for later operator review.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Codify the advisor as one CLI verb (`gz complexity-advise`), one operator-runnable skill (`complexity-advisor`), one diagnosis engine bound to ADR-0.0.28's `ThresholdTable` + ADR-0.0.27 OBPI-04's distilled-characteristics document, with auto-chain from xenon-as-gate failure preserving SKIP-bypass guard wiring, two-path intrinsic-complexity attestation, verdict ↔ proof binding, and pre-commit timeout / fallback / failure-logging.

**Rationale (numbered, binding):**

1. The advisor consumes the `ThresholdTable` model directly, not a JSON re-parse, **because** the parser-divergence drift class is closed at the ADR-0.0.28-02 layer; reimplementing the parse here introduces a vibing surface (training-corpus pattern-matching against possibly-different field names) the cluster's mantra forbids.
2. The diagnostic vocabulary is restricted to the four canonical authorities (Fowler / Martin / Page-Jones / Constantine), **because** the corpus methodology in ADR-0.0.27 binds these as the cluster's authority canon; admitting a fifth authority requires foundation-kind ceremony (corpus refresh, distillation, citation update) — the rationale is inherited verbatim.
3. Auto-chain from xenon-as-gate failure is the load-bearing trigger, **because** an advisor that requires manual invocation has the same failure shape as a validator that exists but never fires (the OBPI-0.0.27-07 link-integrity-validator rationale applied to the trigger-time surface). The operator's locked decision in the handoff ratifies this.
4. Operator-invocable ad-hoc path is preserved alongside auto-chain, **because** preview-before-fail is the operator-bandwidth-protection move (the OEE doctrine's "agent drafts substantively, operator reviews" shape applied to the developer's pre-commit moment).
5. Verdict ↔ proof binding is mandatory on every diagnosis, **because** an advisor that recommends without showing why is the same training-corpus failure mode the mantra forbids — the proof field linking to AST nodes / line ranges is the structural defense against "plausible-looking advice with no traceable evidence". The justification mirrors AGENTS.md § Attestation's receipt-ID requirement at the diagnosis-time layer.
6. Two-path intrinsic-complexity attestation closes the 2am Scenario-3 reality (CC=24 ship-now), **because** a one-path attestation (decorator-only) excludes commit-time attestation and forces the developer to amend code before commit even when the complexity is genuinely irreducible; a one-path attestation (commit-time-only) excludes pre-attested invariants and forces re-attestation per commit. Both paths land at Gate 5; neither produces a silent escape hatch.
7. Pre-commit timeout / fallback / failure-logging closes the 2am Scenario-1 reality (advisor itself hangs), **because** an advisor whose own failure blocks the operator's commit indefinitely is the worst possible operator-experience failure class — the timeout + fail-open-with-log pattern is the structural defense.
8. Nine OBPIs is the right size, **because** each codifies one distinct invariant (schema, engine, CLI, skill, auto-chain, ad-hoc, attestation, proof, timeout); bundling produces one Gate 5 witness for nine separable concerns; over-fragmenting produces ceremony without invariant addition. The nine-OBPI count is locked from the design dialogue's MAX DO IT RIGHT-maxxing decomposition pass.

**The invariant (canonical statement):** gzkit publishes one canonical complexity advisor whose every diagnosis cites the active distilled-characteristics document and the canonical `ThresholdTable`, carries a `proof` field linking to the responsible AST nodes / line ranges, and respects the two-path intrinsic-complexity attestation. The advisor auto-chains from xenon-as-gate failure (preserving SKIP-bypass guard wiring) and is operator-invocable ad-hoc. Pre-commit timeouts fail open with logging; the advisor never blocks an operator's commit indefinitely.

**Mechanical surfaces (what changes in code):**

- `src/gzkit/complexity/advisor/__init__.py` (new package)
- `src/gzkit/complexity/advisor/diagnosis.py` (new): frozen Pydantic `AdvisorDiagnosis`, `RefactorArchetype` enum, `DoctrinalFrame` model, `ProofRange` model.
- `src/gzkit/complexity/advisor/engine.py` (new): given an AST context + a metric crossing, returns `AdvisorDiagnosis`. Imports `ThresholdTable` (ADR-0.0.28-02) and reads OBPI-0.0.27-04's distilled-characteristics for doctrinal-frame attribution.
- `src/gzkit/complexity/advisor/intrinsic.py` (new): `@intrinsic_complexity` decorator and the runtime registry; commit-time `--attest-intrinsic` flag handling.
- `src/gzkit/complexity/advisor/timeout.py` (new): pre-commit timeout / fallback / failure-logging primitives.
- `src/gzkit/commands/complexity_advise.py` (new): `gz complexity-advise` CLI verb (Heavy-lane new subcommand per `.claude/rules/cli.md`).
- `src/gzkit/cli/parser_artifacts.py`: register the new verb.
- `src/gzkit/schemas/advisor_diagnosis.json` (new): JSON Schema mirror.
- `.gzkit/skills/complexity-advisor/SKILL.md` (new): operator-runnable skill carrying invocation patterns + intrinsic-attestation guidance + auto-chain explanation. Vendor-mirrored.
- `.gzkit/hooks/pre-commit-complexity-advisor` (new): auto-chain hook fired on xenon-as-gate non-zero exit; preserves SKIP-bypass guard wiring.
- `tests/complexity/advisor/**`: REQ-derived assertions across all nine OBPIs.
- `features/complexity_advisor.feature` (new): BDD scenarios tagged `@REQ-0.0.29-NN-MM`.
- `docs/user/manpages/gz-complexity-advise.md` (new): manpage per the gate5-runbook-code-covenant.
- `docs/user/runbook.md`: runbook entry under "Complexity doctrine surfaces".
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the advisor surface.

**Nine OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.29-01 — Advisor diagnosis schema:** Frozen Pydantic `AdvisorDiagnosis`, `RefactorArchetype` enum (initial values: long-parameter-list, arrowhead, switch-on-type, feature-envy, large-class, divergent-change, shotgun-surgery, primitive-obsession, data-clumps, message-chain), `DoctrinalFrame` model (authority + citation + chapter/page anchor), `ProofRange` model (file path + line range + AST node descriptor). JSON Schema mirror at `src/gzkit/schemas/advisor_diagnosis.json`.

**OBPI-0.0.29-02 — Diagnosis engine:** Given an AST context + a metric crossing, returns `AdvisorDiagnosis`. Imports `ThresholdTable` (ADR-0.0.28-02) for band classification; reads OBPI-0.0.27-04's distilled-characteristics for doctrinal-frame attribution. Refactor-archetype detection rules are themselves data-driven (rule table at `data/advisor_archetype_rules.json`) — the rules are doctrine, not code, so amendments flow through the doctrine-amendment-protocol pool stub.

**OBPI-0.0.29-03 — `gz complexity-advise` CLI verb:** Heavy-lane new subcommand per `.claude/rules/cli.md` § "New Subcommand (Heavy Lane)": ADR (this), manpage at `docs/user/manpages/gz-complexity-advise.md`, behave smoke scenario, release-notes entry. Default human output is structured prose; `--json` mode emits the canonical Pydantic model serialization.

**OBPI-0.0.29-04 — `complexity-advisor` skill:** `.gzkit/skills/complexity-advisor/SKILL.md` carrying invocation patterns, intrinsic-attestation guidance, auto-chain explanation, and the OBPI-09 timeout-handling description. Vendor-mirrored. Output Contract declares the destination verb's default form per `.gzkit/rules/tool-skill-runbook-alignment.md` § Invariant 3.

**OBPI-0.0.29-05 — Auto-chain from xenon-as-gate failure:** Pre-commit hook at `.gzkit/hooks/pre-commit-complexity-advisor`; fires when xenon-as-gate exits non-zero; preserves SKIP-bypass guard wiring (the existing SKIP semantics from the complexity-reduction-xenon chore are honored unchanged). The hook calls `gz complexity-advise --auto-chain` which signals to the advisor that the invocation is auto-fired (different presentation defaults than ad-hoc).

**OBPI-0.0.29-06 — Operator-invocable ad-hoc path:** `gz complexity-advise <path>` for preview-before-fail. Distinct presentation defaults from auto-chain (verbose preview vs. trigger-time fail-fast). Tested independently from the auto-chain pathway.

**OBPI-0.0.29-07 — Two-path intrinsic-complexity attestation:** `@intrinsic_complexity(reason=..., attestor=...)` decorator (the pre-attested path) and `gz complexity-advise --attest-intrinsic` commit-time flag (the in-flight path). Both paths persist the attestation (decorator: in code; commit-time: in `.gzkit/ledger.jsonl` via canonical event emission). Gate 5 follow-up at brief-level for foundation-kind rigor.

**OBPI-0.0.29-08 — Verdict ↔ proof binding:** Every `AdvisorDiagnosis` carries a non-empty `proof: tuple[ProofRange, ...]` field. The engine fails closed if it cannot produce proof for a diagnosis (no "plausible-looking advice without traceable evidence"). Tested with synthetic AST fixtures.

**OBPI-0.0.29-09 — Pre-commit timeout / fallback / failure-logging:** The pre-commit hook (OBPI-05) wraps the advisor invocation in a configurable timeout (default 30s); on timeout the hook fails open with a logged warning (commit proceeds; defect surface is the log) per the 2am Scenario-1 amelioration. Logs land at `.gzkit/insights/advisor-failures.jsonl`. The fail-open is deliberate: blocking commits on advisor failure is worse than letting them through with a logged warning.

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-08 (proof binding lands with engine) → OBPI-03 → OBPI-04 → OBPI-05 → OBPI-09 (timeout binds with auto-chain) → OBPI-06 → OBPI-07. The diagram is sequential at the schema/engine layer, parallel-able at the surface layer (CLI/skill/hooks).

**Lane: Heavy.** New CLI subcommand + new skill + new pre-commit hook + new ledger event family (intrinsic-attestation events) + new schema. All four trigger heavy-lane rigor per `.gzkit/rules/cli.md`. Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.18.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the corpus selection methodology — that is ADR-0.0.27's scope.
- Does NOT specify the threshold values or trigger semantics — that is ADR-0.0.28's scope.
- Does NOT author the authoring-time guidance surface — that is ADR-0.0.30's scope.
- Does NOT modify the existing `complexity-reduction-xenon` chore's xenon-as-gate behavior — the chore continues to fire xenon at gate time; this ADR adds the advisor on the failure path, not in place of xenon.
- Does NOT specify the refactor-archetype detection rules' empirical validation — the rules are doctrine; their empirical fit is measured at the next distillation pass per ADR-0.0.27 OBPI-04.
- Does NOT vendor or reimplement xenon — xenon-as-gate remains the chosen substrate per ADR-0.0.28's scope boundary.

### Q: What good things result from this decision? List benefits.

**A:** 1. **Trigger-time doctrinal frame replaces opaque numeric verdicts.** When a metric crosses the warn band, the developer gets `(authority, refactor archetype, proof range, recommended move)`, not just `CC=14`. Closes the canonical training-corpus failure mode at the trigger-time response layer.

2. **Auto-chain from xenon-as-gate failure preserves SKIP-bypass wiring.** The existing chore's escape-hatch for known-irreducible code continues to work; the advisor adds diagnosis on the genuine-failure path, not on the SKIP path.

3. **Two-path intrinsic-complexity attestation honors both pre-attested and in-flight cases.** A decorator path for known-irreducible functions; a commit-time path for newly-discovered ones. Both attest at Gate 5; neither produces a silent escape hatch.

4. **Verdict ↔ proof binding closes the "plausible advice without evidence" failure class.** Every diagnosis carries AST nodes / line ranges; the operator can audit the advisor's reasoning at trigger time. Mirrors AGENTS.md § Attestation receipt-ID discipline at the diagnosis-time layer.

5. **Pre-commit timeout / fallback / failure-logging closes the 2am Scenario-1 reality.** The advisor never blocks an operator's commit indefinitely; failure surfaces as a logged warning, not a wedged terminal.

6. **The advisor consumes ThresholdTable directly.** Parser-divergence drift across the cluster is closed at the ADR-0.0.28-02 layer; the advisor binds against the frozen Pydantic model, not a JSON re-parse.

7. **Refactor-archetype detection rules are data-driven doctrine.** The rule table at `data/advisor_archetype_rules.json` is amendable through the doctrine-amendment-protocol pool stub, not silent code edits.

8. **Operator-invocable ad-hoc path enables preview-before-fail.** OEE-doctrine-aligned: the developer can preview advisor diagnosis before xenon would fail it, bandwidth-protecting the commit moment.

9. **Foundation-kind brief-level Gate 5 across nine OBPIs.** Each invariant gets independent witness per ADR-0.0.18; the cluster's mantra (ceremony is the deliverable) holds at the largest single ADR in the cluster.

10. **The cluster's third-of-four foundation lands as the trigger-time response surface.** Every layer below it (corpus, threshold) is consumed, not relitigated; every layer above (authoring-guidance) consumes its diagnostic schema.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **Nine OBPIs is the largest single-ADR ceremony in the cluster.** Operator bandwidth cost is real; bounded by the foundation-kind decomposition discipline (each OBPI is a separable invariant, not a fragmentation move).

2. **Refactor-archetype detection rules are heuristic.** First-distillation cold-start (per ADR-0.0.27 § Negative #9) means the initial rule table is calibrated against literature canon, not against measured archetype-frequency in the corpus. Future distillation passes can refine the rules' empirical fit.

3. **The advisor binds to ADR-0.0.27 OBPI-04 + ADR-0.0.28-02.** Citation-graph density is acknowledged; the link-integrity validator (OBPI-0.0.27-07) is the structural defense.

4. **Auto-chain hook adds pre-commit time.** Real cost in seconds; bounded by OBPI-09's timeout (default 30s with fail-open). Acceptable per the mantra (5:1 governance-to-output ratio is the product).

5. **Commit-time intrinsic-attestation requires ledger event emission.** Every `--attest-intrinsic` invocation emits an `intrinsic-complexity-attestation` ledger event; the event family extends the ledger schema (managed within OBPI-07). Forward-cost: every future ADR consuming intrinsic-attestation events binds against the schema.

6. **Pre-commit hook interaction with developer git workflows is fragile.** Hooks that fail silently or hang frustrate developers; OBPI-09's timeout/fallback/log is the structural defense, but pre-commit-hook interaction is genuinely difficult to make perfectly invisible. Mitigation: the auto-chain hook is opt-in (operator installs it explicitly), not auto-applied at `gz init`.

7. **Default 30s timeout may be too long or too short for some codebases.** Configurable via `.gzkit/config` per the cluster's existing config conventions; calibration against operator workflows is a forward-iteration concern.

8. **The intrinsic-attestation decorator persists in code.** A function decorated with `@intrinsic_complexity` remains attested across rebases/refactors — but if the function changes shape (e.g. CC drops from 24 to 12 after refactoring), the attestation is stale doctrine. Pool stub forward-reference: a future `gz validate --intrinsic-attestation-current` scope would close the stale-attestation failure class.

9. **Verdict ↔ proof binding requires AST traversal at diagnosis time.** Performance cost on large modules; bounded by the metric-crossing precondition (the advisor only fires on warn-or-block crossings, not on every commit). Future optimization (caching parsed ASTs) is a downstream-OBPI concern.

10. **Foundation-kind attestation across nine OBPIs.** Attestation fatigue across nine Gate 5 walkthroughs is a real operator cost; pool stub `ADR-pool.attestation-quality-measurement` is the forward-reference if it materializes (the same forward-reference ADR-0.0.27 § Negative #5 named).

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Advisor diagnosis schema (frozen Pydantic AdvisorDiagnosis, RefactorArchetype enum, DoctrinalFrame, ProofRange; JSON Schema mirror)
2. Diagnosis engine (binds ThresholdTable + distilled-characteristics; refactor-archetype rules data-driven at data/advisor_archetype_rules.json)
3. `gz complexity-advise` CLI verb (Heavy-lane new subcommand: ADR + manpage + smoke + release notes)
4. `complexity-advisor` skill (vendor-mirrored; Output Contract declared; auto-chain + ad-hoc + intrinsic-attestation guidance)
5. Auto-chain from xenon-as-gate failure (pre-commit hook; preserves SKIP-bypass guard wiring)
6. Operator-invocable ad-hoc path (preview-before-fail; distinct presentation defaults from auto-chain)
7. Two-path intrinsic-complexity attestation (`@intrinsic_complexity` decorator + `--attest-intrinsic` commit-time flag; both Gate 5 follow-up)
8. Verdict ↔ proof binding (every diagnosis carries non-empty proof: tuple[ProofRange, ...]; engine fails closed if proof unavailable)
9. Pre-commit timeout / fallback / failure-logging (default 30s; fail-open with log to `.gzkit/insights/advisor-failures.jsonl`)

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Single-OBPI advisor (rule + engine + CLI + skill + hooks bundled).** REJECTED: bundles nine separable invariants under one Gate 5 witness; obscures the dependency graph; produces one foundation-kind ceremony for what is structurally nine distinct invariants. The mantra (ceremony is the deliverable) binds toward decomposition, not bundling.

2. **Advisor as a sub-command of `gz validate` instead of its own CLI verb.** REJECTED: dilutes operator-facing diagnostic naming (`gz validate --advisor` reads as a validation scope; the advisor is a diagnosis surface, not a validation pass). Heavy-lane subcommand-naming discipline per `.claude/rules/cli.md`.

3. **Manual-only invocation (no auto-chain from xenon-as-gate).** REJECTED at design dialogue: an advisor that requires manual invocation has the same failure shape as a validator that exists but never fires. The operator's locked decision in the handoff ratifies auto-chain as the load-bearing trigger.

4. **Auto-chain replaces xenon-as-gate (advisor IS the gate).** REJECTED at design dialogue: replacing xenon widens the blast radius (existing chore behavior breaks) and breaks the SKIP-bypass guard wiring developers depend on. Auto-chain on xenon failure preserves the existing gate; the advisor is additive, not substitutive.

5. **One-path intrinsic-complexity attestation (decorator-only).** REJECTED at design dialogue: forces the developer to amend code before commit even when the complexity is genuinely irreducible at the moment of discovery. The two-path approach honors both pre-attested and in-flight cases.

6. **One-path intrinsic-complexity attestation (commit-time-only).** REJECTED at design dialogue: forces re-attestation per commit for known-irreducible functions; produces attestation fatigue across the codebase's lifecycle. The decorator path persists across rebases.

7. **No verdict ↔ proof binding (advisor produces prose-only diagnosis).** REJECTED: an advisor that recommends without showing why is the same training-corpus failure mode the mantra forbids. Proof field is the structural defense.

8. **Refactor-archetype detection rules embedded in code (not data-driven).** REJECTED: rule amendments require code patches and test changes; data-driven rules amendable through the doctrine-amendment-protocol pool stub mirror the cluster's pattern (rule = doctrine, not configuration; amendments witnessed at brief level).

9. **Pre-commit hook fails closed on advisor timeout (block commit if advisor times out).** REJECTED: blocking the developer's commit on advisor own-failure is worse than letting it through with a logged warning. Fail-open + log is the 2am Scenario-1 amelioration.

10. **Refactor-archetype enum extends to all 70+ Fowler refactorings.** REJECTED at design dialogue: ten archetype values cover ~80% of observed crossings per the design dialogue's WWHTBT pass; admitting all 70+ produces ceremony without discrimination value. Future amendments via the doctrine-amendment-protocol pool stub.

11. **Advisor diagnosis is text-only (no JSON output).** REJECTED: the cluster's downstream consumers (`complexity-reduction-xenon` chore strengthening, future authoring-guidance integration) need machine-parseable output; `--json` mode emits the canonical Pydantic serialization.

12. **Intrinsic-attestation events recorded as ARB receipts instead of ledger events.** REJECTED: ARB receipts are command-execution evidence (lint/test/typecheck); intrinsic-attestation is a doctrinal claim with operator authority — ledger event family is the canonical home. Mirrors the existing `adr-evaluation` event precedent (ADR-0.0.26).


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Single-OBPI advisor (rule + engine + CLI + skill + hooks bundled).** REJECTED: bundles nine separable invariants under one Gate 5 witness; obscures the dependency graph; produces one foundation-kind ceremony for what is structurally nine distinct invariants. The mantra (ceremony is the deliverable) binds toward decomposition, not bundling.

2. **Advisor as a sub-command of `gz validate` instead of its own CLI verb.** REJECTED: dilutes operator-facing diagnostic naming (`gz validate --advisor` reads as a validation scope; the advisor is a diagnosis surface, not a validation pass). Heavy-lane subcommand-naming discipline per `.claude/rules/cli.md`.

3. **Manual-only invocation (no auto-chain from xenon-as-gate).** REJECTED at design dialogue: an advisor that requires manual invocation has the same failure shape as a validator that exists but never fires. The operator's locked decision in the handoff ratifies auto-chain as the load-bearing trigger.

4. **Auto-chain replaces xenon-as-gate (advisor IS the gate).** REJECTED at design dialogue: replacing xenon widens the blast radius (existing chore behavior breaks) and breaks the SKIP-bypass guard wiring developers depend on. Auto-chain on xenon failure preserves the existing gate; the advisor is additive, not substitutive.

5. **One-path intrinsic-complexity attestation (decorator-only).** REJECTED at design dialogue: forces the developer to amend code before commit even when the complexity is genuinely irreducible at the moment of discovery. The two-path approach honors both pre-attested and in-flight cases.

6. **One-path intrinsic-complexity attestation (commit-time-only).** REJECTED at design dialogue: forces re-attestation per commit for known-irreducible functions; produces attestation fatigue across the codebase's lifecycle. The decorator path persists across rebases.

7. **No verdict ↔ proof binding (advisor produces prose-only diagnosis).** REJECTED: an advisor that recommends without showing why is the same training-corpus failure mode the mantra forbids. Proof field is the structural defense.

8. **Refactor-archetype detection rules embedded in code (not data-driven).** REJECTED: rule amendments require code patches and test changes; data-driven rules amendable through the doctrine-amendment-protocol pool stub mirror the cluster's pattern (rule = doctrine, not configuration; amendments witnessed at brief level).

9. **Pre-commit hook fails closed on advisor timeout (block commit if advisor times out).** REJECTED: blocking the developer's commit on advisor own-failure is worse than letting it through with a logged warning. Fail-open + log is the 2am Scenario-1 amelioration.

10. **Refactor-archetype enum extends to all 70+ Fowler refactorings.** REJECTED at design dialogue: ten archetype values cover ~80% of observed crossings per the design dialogue's WWHTBT pass; admitting all 70+ produces ceremony without discrimination value. Future amendments via the doctrine-amendment-protocol pool stub.

11. **Advisor diagnosis is text-only (no JSON output).** REJECTED: the cluster's downstream consumers (`complexity-reduction-xenon` chore strengthening, future authoring-guidance integration) need machine-parseable output; `--json` mode emits the canonical Pydantic serialization.

12. **Intrinsic-attestation events recorded as ARB receipts instead of ledger events.** REJECTED: ARB receipts are command-execution evidence (lint/test/typecheck); intrinsic-attestation is a doctrinal claim with operator authority — ledger event family is the canonical home. Mirrors the existing `adr-evaluation` event precedent (ADR-0.0.26).

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.29 | Pending | | | |
