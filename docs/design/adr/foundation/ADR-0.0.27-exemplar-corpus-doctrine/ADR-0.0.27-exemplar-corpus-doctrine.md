---
id: ADR-0.0.27-exemplar-corpus-doctrine
status: Validated
kind: foundation
semver: 0.0.27
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-04-25
---

# ADR-0.0.27: Exemplar-Corpus Doctrine

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. Treats complexity decisions as doctrine to be calibrated against observation, not against training-corpus pattern-match. Distinguishes the corpus (this ADR — *what gzkit learns from*) from the dependency surface (governed by Stdlib-First — *what gzkit runs on*); these are independent relationships and conflating them is the canonical training-corpus failure mode. Distillation is an agent-driven, human-reviewed and attested/corrected ceremony — the agent supplies metric-aggregate prose; the operator supplies the practitioner-eye observation; both are required. The pytest-mention demerit during this ADR's design dialogue is the canonical lesson encoded in the project-doctrine-fitness criterion: agent training-corpus bias produces systemically over-popular nominations regardless of project-canon fit, and operator audit is the doctrine's structural defense.

This ADR is a Foundation addition and the most foundational of the four-ADR complexity-doctrine cluster (0.0.27 / 0.0.28 / 0.0.29 / 0.0.30). Foundations codify app/system invariants — ADR-0.0.18 (taxonomy doctrine), ADR-0.0.9 (state doctrine), and the MAKE LLM STOCHASTIC VIBES INERT mantra demonstrated that empirically-grounded doctrine closes failure classes that authority-citation alone cannot. This ADR extends the pattern to complexity calibration: an exemplar-corpus-grounded methodology, distilled into citable doctrine, mechanically refreshed via skill-driven cadence and signal-trigger drift detection, and attested at every increment under foundation-kind brief-level Gate 5. Downstream foundation ADRs (0.0.28 threshold, 0.0.29 advisor, 0.0.30 authoring guidance) cite this ADR's distilled-characteristics document as their empirical basis.

## Why foundation tier?

Without this ADR, complexity thresholds are gut-feel — the advisor's verdict bands have no empirically grounded reference corpus, and "is McCabe 11 high?" answers reflect training-corpus drift rather than measured exemplar projects.

This ADR authors a port: the exemplar-corpus contract (seven selection criteria, pinned commit SHAs) that every complexity calibration must derive from.

## Intent

gzkit's complexity-doctrine cluster (this ADR plus the threshold doctrine ADR-0.0.28 and the advisor doctrines ADR-0.0.29 / ADR-0.0.30) requires an empirical basis for calibrating its thresholds, classifier boundaries, and refactor recommendations. Two grounding modes are available: text-grounded (citing canonical authorities — Fowler *Refactoring* 2e, Martin SOLID, Page-Jones connascence taxonomy, Constantine coupling/cohesion modes) and behavior-grounded (measuring well-architected Python projects whose code has aged well across multiple Python eras). Authority citation alone produces doctrine whose specific numeric thresholds are inherited from convention or pattern-matched from training corpus — the canonical training-corpus failure mode the MAKE LLM STOCHASTIC VIBES INERT mantra forbids. Behavior-grounded measurement provides empirical boundaries calibrated against what excellent Python actually looks like at the metric level. This ADR codifies the meta-foundation of the cluster: gzkit calibrates complexity decisions against an empirically-grounded exemplar corpus of well-architected Python projects, distilled into doctrine prose and citable numeric boundaries. Authority citation supplies the diagnostic vocabulary; the corpus supplies the empirical boundaries. Both grounding modes are required; the corpus is the load-bearing addition this ADR introduces.

The corpus is a *learning relationship*, not an *adoption relationship* — gzkit measures click's design metrics to inform CLI doctrine; gzkit does not depend on click. Corpus inclusion records what gzkit learns from; dependency inclusion records what gzkit runs on (the latter governed by the Stdlib-First Doctrine landed at AGENTS.md). The corpus is consulted at distillation time, not at every advisor invocation; the distilled characteristics ship as gzkit doctrine and are cited by ADR-0.0.28 / 0.0.29 / 0.0.30 as their empirical basis. Distillation is an agent-driven, human-reviewed and attested/corrected ceremony — the agent drafts metric-aggregate prose, the operator audits, adds practitioner-eye observations, and signs the resulting distilled-characteristics document at Gate 5.

This ADR is the most foundational of the four-ADR cluster because both threshold and advisor doctrines cite it. Renumbering during design dialogue (the cluster was originally headed by the advisor) reflects dependency-order: the most-cited foundation gets the lowest semver. Renumbering ratified before any artifact landed.

## Decision

Codify the exemplar-corpus methodology, the pinned initial corpus, the measurement protocol, the distillation pass shape, and the citation contract that downstream complexity-cluster ADRs honor. Mechanize each invariant as a separate OBPI under foundation-kind brief-level Gate 5 attestation.

**The invariant (canonical statement):** gzkit calibrates complexity decisions against an empirically-grounded corpus of well-architected Python projects, distilled into doctrine prose and citable numeric boundaries. The corpus is operator-curated against an auditable selection methodology, not agent-pattern-matched from training corpus. Distilled characteristics ship as gzkit doctrine; downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) cite the doctrine, not the corpus directly.

**Selection methodology (binding):** Projects qualify for the corpus only when ALL of the following hold:
- **Longevity:** ≥ 5 years active development OR explicitly archived as a reference
- **Maintenance health:** active releases in last 12 months OR project explicitly declares done state
- **Practitioner reputation:** cited in PEPs, in published reference works (*Fluent Python*, *Effective Python*, *Architecture Patterns with Python*), OR by recurring conference talks (PyCon, EuroPython, PyData). Specifically NOT by GitHub-star count.
- **Pure-Python predominance:** Python content is the primary artifact (≥ 80% of LOC). Excludes thin wrappers around C/Rust where the Python part is glue.
- **Author craftsmanship signal:** maintainer history shows design discipline (PEP authorship, well-known design talks, mentorship reputation). The most subjective criterion; mitigated by the agent-drafted-then-operator-audited pattern.
- **Project doctrine fitness:** the project does not violate gzkit's existing doctrinal commitments. A project whose foundational design choices contradict Stdlib-First or other gzkit canon is excluded regardless of other strengths. The pytest-mention demerit during this session's design dialogue was the canonical failure this criterion closes.
- **Pinned to a specific commit SHA at corpus-authoring time** — distributions are reproducible from the SHA.

**Corpus authoring is at the project + module-subset level, not whole-project.** Each project enters the corpus with explicit per-project path filters declaring which paths enter the measurement set and which are excluded with rationale. Strategically-complex modules (Django ORM query compiler, mypy unification core) are correctly excluded — they encode irreducible algorithmic complexity that would pull metric distributions toward leniency if measured.

**Diversity-of-styles mandate:** The corpus must include projects across distinct domains so no single idiom dominates. Ten archetypal cells are the diversity frame for the initial corpus authoring (any cell may stay vacant if no candidate clears the criteria; cells are amendable):
1. Framework — sync web (e.g. Django)
2. Framework — async web (e.g. Starlette)
3. HTTP library (e.g. httpx)
4. CLI tooling (e.g. click)
5. Type-strict data modeling (e.g. attrs)
6. Stdlib-style core library (selected CPython modules — pathlib, dataclasses, functools, contextlib)
7. Testing / property-based (e.g. hypothesis — pytest deliberately excluded per Stdlib-First)
8. Console rendering / TUI (e.g. rich)
9. Static analysis / type checker (e.g. mypy)
10. Build / packaging (e.g. flit)

**Corpus size target:** 12-15 projects. Statistical adequacy basis: enough for inter-project variance estimation, enough domain coverage for diversity, manageable operator audit at amendment time. Operator may amend cells, add archetypal cells, or substitute candidates per the methodology.

**Anti-patterns in corpus selection (binding):**
- Selecting projects that confirm a pre-decided threshold (post-hoc fitting)
- Selecting by GitHub-star count (popularity ≠ design quality)
- Selecting only modern projects (loses the 'test of time' signal)
- Selecting only legacy projects (misses current best-practice idioms)
- Selecting projects all from the same domain (monoculture; over-fits to one idiom)
- Agent supplying the project list from training memory without operator audit (the corpus is doctrine and must be operator-witnessed)
- Including any project that violates gzkit's existing doctrinal commitments (project doctrine fitness)

**Measurement protocol (binding):** For each project at its pinned SHA, applied to the included paths only:
- `radon cc` — full per-function CC distribution
- `radon mi` — per-module Maintainability Index
- `radon hal` — Halstead volume, difficulty, effort
- `radon raw` — NLOC, LLOC
- `lizard` — per-function NLOC, parameter count, nesting depth, CCN
- `cohesion` — per-class LCOM4

Aggregate per-project, then aggregate across projects: per-metric percentiles (p50, p75, p90, p95, p99), per-metric distribution shape, inter-project variance per metric. Output: dated raw distribution artifacts under `docs/governance/complexity/baselines/{date}/` (or equivalent canonical path).

**Distillation pass shape (binding) — agent-driven, human-reviewed and attested/corrected:**
1. Agent drafts metric-aggregate prose per metric (median, p75, p90, p95, p99 with inter-project variance commentary)
2. Operator adds the practitioner-eye observation (which functions cluster at p90 and why; what makes high-percentile complexity defensible)
3. Joint authoring of actionable characteristics per metric: numeric boundary (corpus percentile + absolute number at that percentile), qualitative band (comfortable craft / investigate / refactor), doctrinal frame (which authority speaks to a violation at this boundary)
4. Agent proposes classifier rule-table boundary updates against new percentiles; operator audits
5. Diff against previous distillation: any boundary that moved >10% gets explicit operator narration
6. Output: `docs/governance/complexity/distilled-characteristics-{date}.md`. Previous documents preserved (never overwritten) — doctrine evolution has a permanent audit trail.

**Cadence (binding):** Two triggers, either of which fires re-distillation. Calendar default: annual (Python ecosystem evolves on roughly annual cycles; semi-annual over-eager, biennial risks doctrine staleness). Signal trigger: advisor verdict-frequency drift > 25% from baseline of last distillation, with minimum re-distillation interval of 6 months to prevent thrashing. Operator may also trigger ad-hoc when a ground-breaking project emerges that warrants corpus amendment. Cadence is itself amendable per OBPI-01 protocol.

**Citation contract (binding):** Downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) cite the distilled-characteristics document, NOT the raw distributions and NOT the corpus directly. The link-integrity validator (`gz validate --complexity-doctrine-links`) fails closed when the cited document does not exist or is out of date.

**Mechanical surfaces (what changes in code):**
- `data/exemplar_corpus.json` (new): registry of pinned project metadata (URL, commit SHA, included paths, excluded paths with rationale, craftsmanship justification). Pydantic model `ExemplarProject` with `ConfigDict(frozen=True, extra='forbid')`. Edits governed by the doctrine itself.
- `src/gzkit/complexity/measurement.py` (new): measurement pipeline orchestrating radon/lizard/cohesion against pinned SHAs.
- `pyproject.toml`: pinned major versions of `radon`, `lizard`, `cohesion` as runtime dependencies (Stdlib-First named departures with rationale: stdlib does not provide cyclomatic complexity / nesting depth / LCOM4 metrics).
- `.gzkit/skills/gz-complexity-distill/` (new): operator-runnable skill carrying corpus list, per-project path filters, methodology rationale, distillation cadence triggers; mirrored to `.claude/skills/`, `.agents/skills/`, `.github/skills/` per skill-surface-sync rules.
- `docs/governance/complexity/` (new directory): home for raw baseline artifacts and dated distilled-characteristics documents.
- `src/gzkit/governance/trust_audits/complexity_doctrine_links.py`: add `validate_complexity_doctrine_links` for `gz validate --complexity-doctrine-links` scope; fail-closed (exit 3) on broken cross-references.
- `.gzkit/rules/complexity-doctrine.md` (new): canonical rule file declaring corpus methodology, distillation cadence, citation contract.
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.

**Seven OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.27-01 — Selection methodology + criteria + anti-patterns + refresh cadence + project-doctrine-fitness criterion:** Author `.gzkit/rules/complexity-doctrine.md` codifying the methodology, criteria, anti-patterns, refresh cadence, and project-doctrine-fitness rule; advisory-rules-audit.md scorecard entry; foundation-kind brief-level Gate 5 attestation.

**OBPI-0.0.27-02 — Initial corpus authoring (operator pins projects + SHAs + per-project path filters):** Operator applies methodology to nominate ~12-15 projects across the ten archetypal cells; per-project path filters with rationale; pinned SHAs at authoring time; craftsmanship justifications recorded; `data/exemplar_corpus.json` lands; Pydantic schema validates entries; pre-mortem #1 (corpus contamination) and demerit-lesson (no doctrinally-incompatible projects) addressed by the criteria. Books the six pool stubs at this OBPI's land (forward-references in citation graph).

**OBPI-0.0.27-03 — Measurement pipeline (radon/lizard/cohesion against pinned SHAs):** `src/gzkit/complexity/measurement.py`; pinned dep declarations in `pyproject.toml`; deterministic JSON output schema; raw baseline artifact lands at `docs/governance/complexity/baselines/{date}/`; behavioral tests confirm reproducibility from SHA; tooling honors per-project path filters from OBPI-02.

**OBPI-0.0.27-04 — Distillation pass authoring (agent-driven, human-reviewed and attested/corrected):** Authors first distilled-characteristics document at `docs/governance/complexity/distilled-characteristics-{date}.md`; documents the joint authoring sequence; prior-distillation diff narration mechanism (no-op on first run); per-metric triple (boundary + band + doctrinal frame); tested on the OBPI-03 baseline.

**OBPI-0.0.27-05 — Citation contract (how downstream ADRs cite the distilled characteristics):** Specifies the citation form (file path + section anchor + corpus revision number); requires downstream ADRs to cite percentile-grounded boundaries with both percentile-of-corpus AND absolute-number-at-that-percentile (so boundaries are portable across corpus refresh); behavioral tests confirm citation form is consistent.

**OBPI-0.0.27-06 — `gz-complexity-distill` skill (ad-hoc + scheduled invocation):** Skill at `.gzkit/skills/gz-complexity-distill/`; carries corpus list + path filters + methodology rationale; operator-invocable ad-hoc; documents calendar (annual) + signal (drift > 25%) + judgment (ground-breaking project) triggers; output to `docs/governance/complexity/`; `gz agent sync control-surfaces` propagates to vendor mirrors.

**OBPI-0.0.27-07 — `gz validate --complexity-doctrine-links` validator (link-integrity scope, 2am-scenario amelioration):** `validate_complexity_doctrine_links` at `src/gzkit/governance/trust_audits/complexity_doctrine_links.py`; CLI flag registration; fail-closed (exit 3) when downstream ADRs cite documents that do not exist or are out of date; integrates into `gz validate --all` and `gz check`; closes the 2am-Scenario-2 failure mode (advisor diagnosis references missing artifact).

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-03 → OBPI-04 → OBPI-05 → OBPI-06 → OBPI-07. OBPI-02 books the six pool stubs as forward-references at land time.

**Six pool stubs booked at OBPI-02 (forward-references in citation graph):**
- `ADR-pool.attestation-quality-measurement` — activates if attestation fatigue empirically materializes (WWHTBT rejected condition #4)
- `ADR-pool.doctrine-amendment-protocol` — codifies how foundation doctrine is amended without breaking citing ADRs (reversibility forcing function)
- `ADR-pool.complexity-doctrine-validate-suite` — aggregates additional `gz validate` scopes (`--classifier-schema-frozen`, `--corpus-shas-pinned`, `--distillation-cadence`)
- `ADR-pool.canon-pillar-codification` — open question whether five top-level pillars warrant retroactive foundation ADRs (deferred unless ledger demands per-pillar introduction event)
- `ADR-pool.complexity-doctrine-meets-chore-system` — future foundation question on chore system as broader doctrine-consumer
- `ADR-pool.complexity-guide-obpi-authoring-integration` — future feature question on `gz complexity-guide` integration with OBPI authoring workflow

**Lane: Heavy.** New CLI scope (`gz validate --complexity-doctrine-links`) is a contract change; new skill is an operator-facing surface; new runtime dependencies extend the wheel; new schema for `data/exemplar_corpus.json` is a data contract. All four trigger heavy-lane rigor per `.gzkit/rules/cli.md` and `.gzkit/rules/gate5-runbook-code-covenant.md`. Foundation-kind rigor stacks on top per ADR-0.0.18 — closeout walkthrough at brief level + ADR closeout regardless of lane.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the threshold values or trigger semantics — that is ADR-0.0.28's scope.
- Does NOT author the complexity advisor or its CLI surface — that is ADR-0.0.29's scope.
- Does NOT author the authoring-time guidance surface — that is ADR-0.0.30's scope.
- Does NOT vendor or reimplement the radon/lizard/cohesion metric tools — pinned dependency posture is the chosen approach (Q4 of design dialogue).
- Does NOT fold the canon-pillar codification question into the cluster — that pool stub is a forward question, not in-scope here.
- Does NOT enforce a measurement-tool replacement path — the methodology binds the choice of `radon`/`lizard`/`cohesion` to corpus-amendment ceremony.

## Consequences

### Positive

1. **Empirical grounding replaces training-corpus pattern-matching at the doctrine layer.** Numeric thresholds, classifier boundaries, and refactor recommendations derive from corpus distribution percentiles, not from agent training memory. Closes the canonical vibing-leak class the MAKE LLM STOCHASTIC VIBES INERT mantra forbids, at the deepest layer of the complexity-doctrine cluster.

2. **Authority citation + corpus measurement combine.** Diagnostic vocabulary (Long Parameter List, Arrowhead, Switch-on-Type) grounded in canonical literature (Fowler, Martin, Page-Jones, Constantine); numeric boundaries grounded in observation. Both grounding modes serve different doctrine functions and reinforce each other.

3. **Distilled characteristics ship as doctrine; runtime does not re-query the corpus.** The advisor (ADR-0.0.29) and authoring-guidance surface (ADR-0.0.30) consume the distilled-characteristics document at runtime. Foundation drift events are dated and witnessed at distillation pass time, not at every advisor invocation.

4. **Refresh cadence + signal-trigger drift detection prevents doctrine staleness without forcing constant churn.** Annual calendar default with 25% drift signal trigger; ad-hoc operator-judgment trigger for ground-breaking projects. The skill is the surface for all three trigger types.

5. **Corpus inclusion ≠ dependency adoption.** gzkit measures click's design metrics to inform CLI doctrine without adopting click as a runtime dependency. Mirrors the Stdlib-First Doctrine landed in this session and prevents the corpus from becoming a backdoor dependency-adoption surface.

6. **Foundation-kind brief-level Gate 5 attestation at every increment.** Each OBPI codifies one invariant; each invariant gets an independent witness. The corpus methodology, the pinned corpus, the measurement pipeline, the distillation pass, the citation contract, the distill skill, and the link validator are seven distinct attestable invariants.

7. **Forward-references via six pool stubs make the citation graph honest from day one.** Future foundation amendments do not surface as surprises; the doctrine acknowledges its own anticipated amendment paths at land time.

8. **The link-integrity validator closes the 2am-Scenario-2 failure mode at land time.** Operator at 2am following an advisor diagnosis to a referenced document never lands on a broken cross-reference. The validator fail-closes on broken citation, surfacing the defect at next operator session.

9. **Project-doctrine-fitness criterion closes the demerit-lesson failure pattern.** No project enters the corpus that violates gzkit's existing canon. The pytest-mention failure during this session's design dialogue is structurally prevented from recurring at corpus-authoring time.

10. **The agent-drafted-then-operator-audited shape models the Operator Economy of Effort doctrine.** Distillation embodies the canon — agent drafts substantive prose; operator reviews, adds practitioner-eye observation, attests at Gate 5. The doctrine's authoring process is itself a worked example of OEE.

### Negative

1. **Operator audit cost at corpus authoring.** Applying selection methodology to 12-15 candidate projects, witnessing each project's craftsmanship signal, pinning SHAs, authoring per-project path filters with rationale. Real bandwidth cost on OBPI-02; bounded by the methodology's transparency. Mitigated by agent-drafted nominations + operator-audit pattern.

2. **Three new pinned dependencies (radon, lizard, cohesion) in pyproject.toml.** Increases gzkit's wheel size and downstream consumer install footprint. Pinned major versions (e.g. `radon>=6.0,<7.0`) make upstream drift visible at dep-bump time, not at invocation time. Stdlib-First named departures: stdlib does not provide cyclomatic complexity / nesting depth / LCOM4 metrics; rationale recorded.

3. **Corpus contamination risk if path filtering is incomplete.** Strategically-complex modules (Django ORM query compiler, mypy unification core) could pull metric distributions toward leniency if not filtered. Pre-mortem #1 flagged this. Mitigation: per-project path filtering protocol declared in OBPI-01 methodology; operator audit at OBPI-02; classifier-schema-frozen validate scope (pool stub) provides amelioration if observed.

4. **Annual distillation cadence is a calendar default that may not match Python idiom evolution rate.** Annual is an estimate; signal-trigger (drift > 25%) is the load-bearing trigger. If idiom evolution is slower than language evolution, annual re-runs produce churn without signal; if faster, calendar trigger lags behind ecosystem reality. Cadence amendable per OBPI-01 protocol.

5. **Distillation pass is foundation-kind ceremony at every recurrence.** Operator bandwidth cost on every refresh cycle; mitigated by agent-drafted-then-human-reviewed shape and pre-distillation evidence assembly. Attestation fatigue across recurrences is a real risk — pool stub `ADR-pool.attestation-quality-measurement` is the forward-reference for if this materializes (WWHTBT rejected condition #4).

6. **Authority citation may not carry weight with all future operators.** Fowler/Martin/Page-Jones/Constantine canon may not be shared by later contributors who anchor on different references (Hickey simplicity, Sandi Metz POODR, modern type-driven design). Mitigation: distilled-characteristics document includes self-contained examples per characteristic, not just citations; the corpus's percentile-based boundaries function as evidence even when the cited authority is unfamiliar.

7. **Citation graph density across 0.0.27 / 0.0.28 / 0.0.29 / 0.0.30 means corpus refresh has citation-update cost in three downstream foundation ADRs.** Reversibility forcing function flagged this as the primary one-way-door element. Formalized via the doctrine-amendment-protocol pool stub (forward-reference book at OBPI-02).

8. **Foundation-kind attestation across 7 OBPIs.** Per-increment Gate 5 witness across the OBPI sequence is heavier ceremony than feature-kind would have produced — but the kind decision was deliberate (Q1 of design dialogue) and the heaviness is the deliverable per the mantra. Consequence rather than cost.

9. **First-distillation cold-start.** OBPI-04 produces the first distilled-characteristics document with no prior-distillation diff to compare against. The diff-narration mechanism is no-op on first run; the first distillation establishes the baseline rather than detecting drift. Documented in OBPI-04's brief.

10. **The corpus's sample size (12-15 projects) is statistically modest.** Per-project distributions internally have thousands of functions and produce stable per-project percentiles, but cross-project variance estimation with 12-15 projects has uncertainty. The corpus is a calibration anchor, not a statistical population sample. Future amendments can grow the corpus toward 20+ if cross-project variance estimates need tightening — bounded by the operator audit cost noted in (1).

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
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 2
- Final Target OBPI Count: 7

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.27-01 — Selection methodology + criteria + anti-patterns + refresh cadence + project-doctrine-fitness criterion (`.gzkit/rules/complexity-doctrine.md`)
- [ ] OBPI-0.0.27-02 — Initial corpus authoring with pinned SHAs and per-project path filters; books the six pool stubs as forward-references (`data/exemplar_corpus.json`)
- [ ] OBPI-0.0.27-03 — Measurement pipeline producing raw distribution artifacts (`src/gzkit/complexity/measurement.py`, `docs/governance/complexity/baselines/`)
- [ ] OBPI-0.0.27-04 — Distillation pass authoring distilled-characteristics document — agent-driven, human-reviewed and attested/corrected (`docs/governance/complexity/distilled-characteristics-{date}.md`)
- [ ] OBPI-0.0.27-05 — Citation contract specifying how downstream foundation ADRs cite the corpus (percentile + absolute-number pairing for portability across refresh)
- [ ] OBPI-0.0.27-06 — `gz-complexity-distill` skill (ad-hoc + scheduled invocation, vendor-mirrored)
- [ ] OBPI-0.0.27-07 — `gz validate --complexity-doctrine-links` validator (link-integrity scope; closes 2am-Scenario-2 failure mode)

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-04-25T14:32:42.337863*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.27

### Q: What is the title of this ADR?

**A:** Exemplar-Corpus Doctrine

### Q: What is the semantic version?

**A:** 0.0.27

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's complexity-doctrine cluster (this ADR plus the threshold doctrine ADR-0.0.28 and the advisor doctrines ADR-0.0.29 / ADR-0.0.30) requires an empirical basis for calibrating its thresholds, classifier boundaries, and refactor recommendations. Two grounding modes are available: text-grounded (citing canonical authorities — Fowler *Refactoring* 2e, Martin SOLID, Page-Jones connascence taxonomy, Constantine coupling/cohesion modes) and behavior-grounded (measuring well-architected Python projects whose code has aged well across multiple Python eras). Authority citation alone produces doctrine whose specific numeric thresholds are inherited from convention or pattern-matched from training corpus — the canonical training-corpus failure mode the MAKE LLM STOCHASTIC VIBES INERT mantra forbids. Behavior-grounded measurement provides empirical boundaries calibrated against what excellent Python actually looks like at the metric level. This ADR codifies the meta-foundation of the cluster: gzkit calibrates complexity decisions against an empirically-grounded exemplar corpus of well-architected Python projects, distilled into doctrine prose and citable numeric boundaries. Authority citation supplies the diagnostic vocabulary; the corpus supplies the empirical boundaries. Both grounding modes are required; the corpus is the load-bearing addition this ADR introduces.

The corpus is a *learning relationship*, not an *adoption relationship* — gzkit measures click's design metrics to inform CLI doctrine; gzkit does not depend on click. Corpus inclusion records what gzkit learns from; dependency inclusion records what gzkit runs on (the latter governed by the Stdlib-First Doctrine landed at AGENTS.md). The corpus is consulted at distillation time, not at every advisor invocation; the distilled characteristics ship as gzkit doctrine and are cited by ADR-0.0.28 / 0.0.29 / 0.0.30 as their empirical basis. Distillation is an agent-driven, human-reviewed and attested/corrected ceremony — the agent drafts metric-aggregate prose, the operator audits, adds practitioner-eye observations, and signs the resulting distilled-characteristics document at Gate 5.

This ADR is the most foundational of the four-ADR cluster because both threshold and advisor doctrines cite it. Renumbering during design dialogue (the cluster was originally headed by the advisor) reflects dependency-order: the most-cited foundation gets the lowest semver. Renumbering ratified before any artifact landed.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Codify the exemplar-corpus methodology, the pinned initial corpus, the measurement protocol, the distillation pass shape, and the citation contract that downstream complexity-cluster ADRs honor. Mechanize each invariant as a separate OBPI under foundation-kind brief-level Gate 5 attestation.

**The invariant (canonical statement):** gzkit calibrates complexity decisions against an empirically-grounded corpus of well-architected Python projects, distilled into doctrine prose and citable numeric boundaries. The corpus is operator-curated against an auditable selection methodology, not agent-pattern-matched from training corpus. Distilled characteristics ship as gzkit doctrine; downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) cite the doctrine, not the corpus directly.

**Selection methodology (binding):** Projects qualify for the corpus only when ALL of the following hold:
- **Longevity:** ≥ 5 years active development OR explicitly archived as a reference
- **Maintenance health:** active releases in last 12 months OR project explicitly declares done state
- **Practitioner reputation:** cited in PEPs, in published reference works (*Fluent Python*, *Effective Python*, *Architecture Patterns with Python*), OR by recurring conference talks (PyCon, EuroPython, PyData). Specifically NOT by GitHub-star count.
- **Pure-Python predominance:** Python content is the primary artifact (≥ 80% of LOC). Excludes thin wrappers around C/Rust where the Python part is glue.
- **Author craftsmanship signal:** maintainer history shows design discipline (PEP authorship, well-known design talks, mentorship reputation). The most subjective criterion; mitigated by the agent-drafted-then-operator-audited pattern.
- **Project doctrine fitness:** the project does not violate gzkit's existing doctrinal commitments. A project whose foundational design choices contradict Stdlib-First or other gzkit canon is excluded regardless of other strengths. The pytest-mention demerit during this session's design dialogue was the canonical failure this criterion closes.
- **Pinned to a specific commit SHA at corpus-authoring time** — distributions are reproducible from the SHA.

**Corpus authoring is at the project + module-subset level, not whole-project.** Each project enters the corpus with explicit per-project path filters declaring which paths enter the measurement set and which are excluded with rationale. Strategically-complex modules (Django ORM query compiler, mypy unification core) are correctly excluded — they encode irreducible algorithmic complexity that would pull metric distributions toward leniency if measured.

**Diversity-of-styles mandate:** The corpus must include projects across distinct domains so no single idiom dominates. Ten archetypal cells are the diversity frame for the initial corpus authoring (any cell may stay vacant if no candidate clears the criteria; cells are amendable):
1. Framework — sync web (e.g. Django)
2. Framework — async web (e.g. Starlette)
3. HTTP library (e.g. httpx)
4. CLI tooling (e.g. click)
5. Type-strict data modeling (e.g. attrs)
6. Stdlib-style core library (selected CPython modules — pathlib, dataclasses, functools, contextlib)
7. Testing / property-based (e.g. hypothesis — pytest deliberately excluded per Stdlib-First)
8. Console rendering / TUI (e.g. rich)
9. Static analysis / type checker (e.g. mypy)
10. Build / packaging (e.g. flit)

**Corpus size target:** 12-15 projects. Statistical adequacy basis: enough for inter-project variance estimation, enough domain coverage for diversity, manageable operator audit at amendment time. Operator may amend cells, add archetypal cells, or substitute candidates per the methodology.

**Anti-patterns in corpus selection (binding):**
- Selecting projects that confirm a pre-decided threshold (post-hoc fitting)
- Selecting by GitHub-star count (popularity ≠ design quality)
- Selecting only modern projects (loses the 'test of time' signal)
- Selecting only legacy projects (misses current best-practice idioms)
- Selecting projects all from the same domain (monoculture; over-fits to one idiom)
- Agent supplying the project list from training memory without operator audit (the corpus is doctrine and must be operator-witnessed)
- Including any project that violates gzkit's existing doctrinal commitments (project doctrine fitness)

**Measurement protocol (binding):** For each project at its pinned SHA, applied to the included paths only:
- `radon cc` — full per-function CC distribution
- `radon mi` — per-module Maintainability Index
- `radon hal` — Halstead volume, difficulty, effort
- `radon raw` — NLOC, LLOC
- `lizard` — per-function NLOC, parameter count, nesting depth, CCN
- `cohesion` — per-class LCOM4

Aggregate per-project, then aggregate across projects: per-metric percentiles (p50, p75, p90, p95, p99), per-metric distribution shape, inter-project variance per metric. Output: dated raw distribution artifacts under `docs/governance/complexity/baselines/{date}/` (or equivalent canonical path).

**Distillation pass shape (binding) — agent-driven, human-reviewed and attested/corrected:**
1. Agent drafts metric-aggregate prose per metric (median, p75, p90, p95, p99 with inter-project variance commentary)
2. Operator adds the practitioner-eye observation (which functions cluster at p90 and why; what makes high-percentile complexity defensible)
3. Joint authoring of actionable characteristics per metric: numeric boundary (corpus percentile + absolute number at that percentile), qualitative band (comfortable craft / investigate / refactor), doctrinal frame (which authority speaks to a violation at this boundary)
4. Agent proposes classifier rule-table boundary updates against new percentiles; operator audits
5. Diff against previous distillation: any boundary that moved >10% gets explicit operator narration
6. Output: `docs/governance/complexity/distilled-characteristics-{date}.md`. Previous documents preserved (never overwritten) — doctrine evolution has a permanent audit trail.

**Cadence (binding):** Two triggers, either of which fires re-distillation. Calendar default: annual (Python ecosystem evolves on roughly annual cycles; semi-annual over-eager, biennial risks doctrine staleness). Signal trigger: advisor verdict-frequency drift > 25% from baseline of last distillation, with minimum re-distillation interval of 6 months to prevent thrashing. Operator may also trigger ad-hoc when a ground-breaking project emerges that warrants corpus amendment. Cadence is itself amendable per OBPI-01 protocol.

**Citation contract (binding):** Downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) cite the distilled-characteristics document, NOT the raw distributions and NOT the corpus directly. The link-integrity validator (`gz validate --complexity-doctrine-links`) fails closed when the cited document does not exist or is out of date.

**Mechanical surfaces (what changes in code):**
- `data/exemplar_corpus.json` (new): registry of pinned project metadata (URL, commit SHA, included paths, excluded paths with rationale, craftsmanship justification). Pydantic model `ExemplarProject` with `ConfigDict(frozen=True, extra='forbid')`. Edits governed by the doctrine itself.
- `src/gzkit/complexity/measurement.py` (new): measurement pipeline orchestrating radon/lizard/cohesion against pinned SHAs.
- `pyproject.toml`: pinned major versions of `radon`, `lizard`, `cohesion` as runtime dependencies (Stdlib-First named departures with rationale: stdlib does not provide cyclomatic complexity / nesting depth / LCOM4 metrics).
- `.gzkit/skills/gz-complexity-distill/` (new): operator-runnable skill carrying corpus list, per-project path filters, methodology rationale, distillation cadence triggers; mirrored to `.claude/skills/`, `.agents/skills/`, `.github/skills/` per skill-surface-sync rules.
- `docs/governance/complexity/` (new directory): home for raw baseline artifacts and dated distilled-characteristics documents.
- `src/gzkit/governance/trust_audits/complexity_doctrine_links.py`: add `validate_complexity_doctrine_links` for `gz validate --complexity-doctrine-links` scope; fail-closed (exit 3) on broken cross-references.
- `.gzkit/rules/complexity-doctrine.md` (new): canonical rule file declaring corpus methodology, distillation cadence, citation contract.
- `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.

**Seven OBPIs decompose the decision (1:1 with Feature Checklist):**

**OBPI-0.0.27-01 — Selection methodology + criteria + anti-patterns + refresh cadence + project-doctrine-fitness criterion:** Author `.gzkit/rules/complexity-doctrine.md` codifying the methodology, criteria, anti-patterns, refresh cadence, and project-doctrine-fitness rule; advisory-rules-audit.md scorecard entry; foundation-kind brief-level Gate 5 attestation.

**OBPI-0.0.27-02 — Initial corpus authoring (operator pins projects + SHAs + per-project path filters):** Operator applies methodology to nominate ~12-15 projects across the ten archetypal cells; per-project path filters with rationale; pinned SHAs at authoring time; craftsmanship justifications recorded; `data/exemplar_corpus.json` lands; Pydantic schema validates entries; pre-mortem #1 (corpus contamination) and demerit-lesson (no doctrinally-incompatible projects) addressed by the criteria. Books the six pool stubs at this OBPI's land (forward-references in citation graph).

**OBPI-0.0.27-03 — Measurement pipeline (radon/lizard/cohesion against pinned SHAs):** `src/gzkit/complexity/measurement.py`; pinned dep declarations in `pyproject.toml`; deterministic JSON output schema; raw baseline artifact lands at `docs/governance/complexity/baselines/{date}/`; behavioral tests confirm reproducibility from SHA; tooling honors per-project path filters from OBPI-02.

**OBPI-0.0.27-04 — Distillation pass authoring (agent-driven, human-reviewed and attested/corrected):** Authors first distilled-characteristics document at `docs/governance/complexity/distilled-characteristics-{date}.md`; documents the joint authoring sequence; prior-distillation diff narration mechanism (no-op on first run); per-metric triple (boundary + band + doctrinal frame); tested on the OBPI-03 baseline.

**OBPI-0.0.27-05 — Citation contract (how downstream ADRs cite the distilled characteristics):** Specifies the citation form (file path + section anchor + corpus revision number); requires downstream ADRs to cite percentile-grounded boundaries with both percentile-of-corpus AND absolute-number-at-that-percentile (so boundaries are portable across corpus refresh); behavioral tests confirm citation form is consistent.

**OBPI-0.0.27-06 — `gz-complexity-distill` skill (ad-hoc + scheduled invocation):** Skill at `.gzkit/skills/gz-complexity-distill/`; carries corpus list + path filters + methodology rationale; operator-invocable ad-hoc; documents calendar (annual) + signal (drift > 25%) + judgment (ground-breaking project) triggers; output to `docs/governance/complexity/`; `gz agent sync control-surfaces` propagates to vendor mirrors.

**OBPI-0.0.27-07 — `gz validate --complexity-doctrine-links` validator (link-integrity scope, 2am-scenario amelioration):** `validate_complexity_doctrine_links` at `src/gzkit/governance/trust_audits/complexity_doctrine_links.py`; CLI flag registration; fail-closed (exit 3) when downstream ADRs cite documents that do not exist or are out of date; integrates into `gz validate --all` and `gz check`; closes the 2am-Scenario-2 failure mode (advisor diagnosis references missing artifact).

**Sequencing:** OBPI-01 → OBPI-02 → OBPI-03 → OBPI-04 → OBPI-05 → OBPI-06 → OBPI-07. OBPI-02 books the six pool stubs as forward-references at land time.

**Six pool stubs booked at OBPI-02 (forward-references in citation graph):**
- `ADR-pool.attestation-quality-measurement` — activates if attestation fatigue empirically materializes (WWHTBT rejected condition #4)
- `ADR-pool.doctrine-amendment-protocol` — codifies how foundation doctrine is amended without breaking citing ADRs (reversibility forcing function)
- `ADR-pool.complexity-doctrine-validate-suite` — aggregates additional `gz validate` scopes (`--classifier-schema-frozen`, `--corpus-shas-pinned`, `--distillation-cadence`)
- `ADR-pool.canon-pillar-codification` — open question whether five top-level pillars warrant retroactive foundation ADRs (deferred unless ledger demands per-pillar introduction event)
- `ADR-pool.complexity-doctrine-meets-chore-system` — future foundation question on chore system as broader doctrine-consumer
- `ADR-pool.complexity-guide-obpi-authoring-integration` — future feature question on `gz complexity-guide` integration with OBPI authoring workflow

**Lane: Heavy.** New CLI scope (`gz validate --complexity-doctrine-links`) is a contract change; new skill is an operator-facing surface; new runtime dependencies extend the wheel; new schema for `data/exemplar_corpus.json` is a data contract. All four trigger heavy-lane rigor per `.gzkit/rules/cli.md` and `.gzkit/rules/gate5-runbook-code-covenant.md`. Foundation-kind rigor stacks on top per ADR-0.0.18 — closeout walkthrough at brief level + ADR closeout regardless of lane.

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT specify the threshold values or trigger semantics — that is ADR-0.0.28's scope.
- Does NOT author the complexity advisor or its CLI surface — that is ADR-0.0.29's scope.
- Does NOT author the authoring-time guidance surface — that is ADR-0.0.30's scope.
- Does NOT vendor or reimplement the radon/lizard/cohesion metric tools — pinned dependency posture is the chosen approach (Q4 of design dialogue).
- Does NOT fold the canon-pillar codification question into the cluster — that pool stub is a forward question, not in-scope here.
- Does NOT enforce a measurement-tool replacement path — the methodology binds the choice of `radon`/`lizard`/`cohesion` to corpus-amendment ceremony.

### Q: What good things result from this decision? List benefits.

**A:** 1. **Empirical grounding replaces training-corpus pattern-matching at the doctrine layer.** Numeric thresholds, classifier boundaries, and refactor recommendations derive from corpus distribution percentiles, not from agent training memory. Closes the canonical vibing-leak class the MAKE LLM STOCHASTIC VIBES INERT mantra forbids, at the deepest layer of the complexity-doctrine cluster.

2. **Authority citation + corpus measurement combine.** Diagnostic vocabulary (Long Parameter List, Arrowhead, Switch-on-Type) grounded in canonical literature (Fowler, Martin, Page-Jones, Constantine); numeric boundaries grounded in observation. Both grounding modes serve different doctrine functions and reinforce each other.

3. **Distilled characteristics ship as doctrine; runtime does not re-query the corpus.** The advisor (ADR-0.0.29) and authoring-guidance surface (ADR-0.0.30) consume the distilled-characteristics document at runtime. Foundation drift events are dated and witnessed at distillation pass time, not at every advisor invocation.

4. **Refresh cadence + signal-trigger drift detection prevents doctrine staleness without forcing constant churn.** Annual calendar default with 25% drift signal trigger; ad-hoc operator-judgment trigger for ground-breaking projects. The skill is the surface for all three trigger types.

5. **Corpus inclusion ≠ dependency adoption.** gzkit measures click's design metrics to inform CLI doctrine without adopting click as a runtime dependency. Mirrors the Stdlib-First Doctrine landed in this session and prevents the corpus from becoming a backdoor dependency-adoption surface.

6. **Foundation-kind brief-level Gate 5 attestation at every increment.** Each OBPI codifies one invariant; each invariant gets an independent witness. The corpus methodology, the pinned corpus, the measurement pipeline, the distillation pass, the citation contract, the distill skill, and the link validator are seven distinct attestable invariants.

7. **Forward-references via six pool stubs make the citation graph honest from day one.** Future foundation amendments do not surface as surprises; the doctrine acknowledges its own anticipated amendment paths at land time.

8. **The link-integrity validator closes the 2am-Scenario-2 failure mode at land time.** Operator at 2am following an advisor diagnosis to a referenced document never lands on a broken cross-reference. The validator fail-closes on broken citation, surfacing the defect at next operator session.

9. **Project-doctrine-fitness criterion closes the demerit-lesson failure pattern.** No project enters the corpus that violates gzkit's existing canon. The pytest-mention failure during this session's design dialogue is structurally prevented from recurring at corpus-authoring time.

10. **The agent-drafted-then-operator-audited shape models the Operator Economy of Effort doctrine.** Distillation embodies the canon — agent drafts substantive prose; operator reviews, adds practitioner-eye observation, attests at Gate 5. The doctrine's authoring process is itself a worked example of OEE.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **Operator audit cost at corpus authoring.** Applying selection methodology to 12-15 candidate projects, witnessing each project's craftsmanship signal, pinning SHAs, authoring per-project path filters with rationale. Real bandwidth cost on OBPI-02; bounded by the methodology's transparency. Mitigated by agent-drafted nominations + operator-audit pattern.

2. **Three new pinned dependencies (radon, lizard, cohesion) in pyproject.toml.** Increases gzkit's wheel size and downstream consumer install footprint. Pinned major versions (e.g. `radon>=6.0,<7.0`) make upstream drift visible at dep-bump time, not at invocation time. Stdlib-First named departures: stdlib does not provide cyclomatic complexity / nesting depth / LCOM4 metrics; rationale recorded.

3. **Corpus contamination risk if path filtering is incomplete.** Strategically-complex modules (Django ORM query compiler, mypy unification core) could pull metric distributions toward leniency if not filtered. Pre-mortem #1 flagged this. Mitigation: per-project path filtering protocol declared in OBPI-01 methodology; operator audit at OBPI-02; classifier-schema-frozen validate scope (pool stub) provides amelioration if observed.

4. **Annual distillation cadence is a calendar default that may not match Python idiom evolution rate.** Annual is an estimate; signal-trigger (drift > 25%) is the load-bearing trigger. If idiom evolution is slower than language evolution, annual re-runs produce churn without signal; if faster, calendar trigger lags behind ecosystem reality. Cadence amendable per OBPI-01 protocol.

5. **Distillation pass is foundation-kind ceremony at every recurrence.** Operator bandwidth cost on every refresh cycle; mitigated by agent-drafted-then-human-reviewed shape and pre-distillation evidence assembly. Attestation fatigue across recurrences is a real risk — pool stub `ADR-pool.attestation-quality-measurement` is the forward-reference for if this materializes (WWHTBT rejected condition #4).

6. **Authority citation may not carry weight with all future operators.** Fowler/Martin/Page-Jones/Constantine canon may not be shared by later contributors who anchor on different references (Hickey simplicity, Sandi Metz POODR, modern type-driven design). Mitigation: distilled-characteristics document includes self-contained examples per characteristic, not just citations; the corpus's percentile-based boundaries function as evidence even when the cited authority is unfamiliar.

7. **Citation graph density across 0.0.27 / 0.0.28 / 0.0.29 / 0.0.30 means corpus refresh has citation-update cost in three downstream foundation ADRs.** Reversibility forcing function flagged this as the primary one-way-door element. Formalized via the doctrine-amendment-protocol pool stub (forward-reference book at OBPI-02).

8. **Foundation-kind attestation across 7 OBPIs.** Per-increment Gate 5 witness across the OBPI sequence is heavier ceremony than feature-kind would have produced — but the kind decision was deliberate (Q1 of design dialogue) and the heaviness is the deliverable per the mantra. Consequence rather than cost.

9. **First-distillation cold-start.** OBPI-04 produces the first distilled-characteristics document with no prior-distillation diff to compare against. The diff-narration mechanism is no-op on first run; the first distillation establishes the baseline rather than detecting drift. Documented in OBPI-04's brief.

10. **The corpus's sample size (12-15 projects) is statistically modest.** Per-project distributions internally have thousands of functions and produce stable per-project percentiles, but cross-project variance estimation with 12-15 projects has uncertainty. The corpus is a calibration anchor, not a statistical population sample. Future amendments can grow the corpus toward 20+ if cross-project variance estimates need tightening — bounded by the operator audit cost noted in (1).

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Selection methodology + criteria + anti-patterns + refresh cadence + project-doctrine-fitness criterion (`.gzkit/rules/complexity-doctrine.md`)
2. Initial corpus authoring with pinned SHAs and per-project path filters; books the six pool stubs as forward-references (`data/exemplar_corpus.json`)
3. Measurement pipeline producing raw distribution artifacts (`src/gzkit/complexity/measurement.py`, `docs/governance/complexity/baselines/`)
4. Distillation pass authoring distilled-characteristics document — agent-driven, human-reviewed and attested/corrected (`docs/governance/complexity/distilled-characteristics-{date}.md`)
5. Citation contract specifying how downstream foundation ADRs cite the corpus (percentile + absolute-number pairing for portability across refresh)
6. `gz-complexity-distill` skill (ad-hoc + scheduled invocation, vendor-mirrored)
7. `gz validate --complexity-doctrine-links` validator (link-integrity scope; closes 2am-Scenario-2 failure mode)

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Authority-citation-only doctrine (no exemplar corpus).** Cite Fowler/Martin/Page-Jones/Constantine and pick numeric thresholds from craft heuristics. REJECTED at design dialogue Q5: pattern-matching numeric thresholds from training corpus is the canonical vibing-leak the mantra forbids. Authority citation supplies vocabulary; observation supplies boundaries. Both are required.

2. **Single foundation ADR absorbing corpus + threshold + advisor + authoring guidance under one ceremony.** REJECTED: bundles four distinct invariants under one foundation rigor; violates the 'one OBPI per invariant' discipline; obscures the citation graph; produces an enormous ADR with too many distinct invariants under one Gate 5 witness. The mantra says ceremony is the deliverable — fragmentation in service of more witness points is correct, not excessive.

3. **Corpus included as an evidence artifact (not foundation doctrine).** Treat the corpus as a one-off measurement artifact under `artifacts/baselines/`, with the threshold-and-advisor ADRs citing it directly. REJECTED: the methodology and the choice of authorities are doctrine, not just evidence; foundation-kind rigor at brief level is the right home for the choice of which authorities govern modularization across the codebase.

4. **Optional dependency posture for radon/lizard/cohesion (graceful degradation if absent).** REJECTED at design dialogue Q4: graceful degradation produces situational doctrine — an operator on a stripped install gets a verdict that pattern-matches as 'the doctrine ran' but is missing layers entirely. Foundation-kind doctrine cannot be situational; situational doctrine is doctrine drift by another name.

5. **Vendored or reimplemented metric layer (gzkit owns its measurement).** DEFERRED: more thorough on the upstream-drift axis, but reimplementing solved work (radon's CC traversal, lizard's nesting counter, cohesion's LCOM4 formula) introduces a different vibing surface — agent-authored AST tooling that was not the original intent of gzkit. If the operator wants this, separate foundation ADR; the pinned-major-version posture closes the immediate drift class.

6. **Smaller corpus (3-5 projects).** REJECTED: insufficient for inter-project variance estimation; single outlier project skews aggregate; cannot fill the diversity-of-styles mandate.

7. **Larger corpus (25+ projects).** REJECTED: diminishing returns on marginal information from project N=20; operator audit cost (path filtering, craftsmanship-signal witness, SHA pinning) scales linearly with project count; attestation-quality risk grows with audit fatigue.

8. **Agent-supplied corpus list without operator audit.** REJECTED at design dialogue: the demerit lesson from the pytest-mention failure during this session — agent training-corpus bias produces systemically over-popular nominations; operator audit is the doctrine's structural defense. The agent's role is to draft the methodology; the operator's role is to apply it and audit each nomination.

9. **Real-time corpus query at every advisor invocation.** REJECTED: couples runtime to corpus availability; doctrine should ship as distilled characteristics, not runtime queries; corpus refresh would silently shift advisor verdicts without a witness. The distillation pass is the witness boundary.

10. **Project-list selected by GitHub-star count (popularity proxy).** REJECTED: explicit anti-pattern in selection methodology. Popularity ≠ design quality; selection bias toward novelty; conflates 'most-used' with 'most well-architected.' The criteria-based methodology is structurally orthogonal to popularity.

11. **Re-distillation on every gzkit release (continuous distillation cadence).** REJECTED: produces churn without signal — corpus distributions do not meaningfully shift release-to-release; attestation fatigue degrades witness quality. Annual + signal-trigger is the calibrated cadence.

12. **Whole-project corpus measurement (no per-project path filtering).** REJECTED: corpus contamination risk — strategically-complex modules pull distributions toward leniency. The per-project path-filtering protocol is the structural defense; operator audit at OBPI-02 is the witness.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Authority-citation-only doctrine (no exemplar corpus).** Cite Fowler/Martin/Page-Jones/Constantine and pick numeric thresholds from craft heuristics. REJECTED at design dialogue Q5: pattern-matching numeric thresholds from training corpus is the canonical vibing-leak the mantra forbids. Authority citation supplies vocabulary; observation supplies boundaries. Both are required.

2. **Single foundation ADR absorbing corpus + threshold + advisor + authoring guidance under one ceremony.** REJECTED: bundles four distinct invariants under one foundation rigor; violates the 'one OBPI per invariant' discipline; obscures the citation graph; produces an enormous ADR with too many distinct invariants under one Gate 5 witness. The mantra says ceremony is the deliverable — fragmentation in service of more witness points is correct, not excessive.

3. **Corpus included as an evidence artifact (not foundation doctrine).** Treat the corpus as a one-off measurement artifact under `artifacts/baselines/`, with the threshold-and-advisor ADRs citing it directly. REJECTED: the methodology and the choice of authorities are doctrine, not just evidence; foundation-kind rigor at brief level is the right home for the choice of which authorities govern modularization across the codebase.

4. **Optional dependency posture for radon/lizard/cohesion (graceful degradation if absent).** REJECTED at design dialogue Q4: graceful degradation produces situational doctrine — an operator on a stripped install gets a verdict that pattern-matches as 'the doctrine ran' but is missing layers entirely. Foundation-kind doctrine cannot be situational; situational doctrine is doctrine drift by another name.

5. **Vendored or reimplemented metric layer (gzkit owns its measurement).** DEFERRED: more thorough on the upstream-drift axis, but reimplementing solved work (radon's CC traversal, lizard's nesting counter, cohesion's LCOM4 formula) introduces a different vibing surface — agent-authored AST tooling that was not the original intent of gzkit. If the operator wants this, separate foundation ADR; the pinned-major-version posture closes the immediate drift class.

6. **Smaller corpus (3-5 projects).** REJECTED: insufficient for inter-project variance estimation; single outlier project skews aggregate; cannot fill the diversity-of-styles mandate.

7. **Larger corpus (25+ projects).** REJECTED: diminishing returns on marginal information from project N=20; operator audit cost (path filtering, craftsmanship-signal witness, SHA pinning) scales linearly with project count; attestation-quality risk grows with audit fatigue.

8. **Agent-supplied corpus list without operator audit.** REJECTED at design dialogue: the demerit lesson from the pytest-mention failure during this session — agent training-corpus bias produces systemically over-popular nominations; operator audit is the doctrine's structural defense. The agent's role is to draft the methodology; the operator's role is to apply it and audit each nomination.

9. **Real-time corpus query at every advisor invocation.** REJECTED: couples runtime to corpus availability; doctrine should ship as distilled characteristics, not runtime queries; corpus refresh would silently shift advisor verdicts without a witness. The distillation pass is the witness boundary.

10. **Project-list selected by GitHub-star count (popularity proxy).** REJECTED: explicit anti-pattern in selection methodology. Popularity ≠ design quality; selection bias toward novelty; conflates 'most-used' with 'most well-architected.' The criteria-based methodology is structurally orthogonal to popularity.

11. **Re-distillation on every gzkit release (continuous distillation cadence).** REJECTED: produces churn without signal — corpus distributions do not meaningfully shift release-to-release; attestation fatigue degrades witness quality. Annual + signal-trigger is the calibrated cadence.

12. **Whole-project corpus measurement (no per-project path filtering).** REJECTED: corpus contamination risk — strategically-complex modules pull distributions toward leniency. The per-project path-filtering protocol is the structural defense; operator audit at OBPI-02 is the witness.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.27 | Validated | Jeffry Babb | 2026-05-05 | Audit accepted — see `audit/AUDIT.md`; all 7 OBPIs attested-completed, 50/50 REQs covered, validator scopes clean, value demonstrated. |
