---
id: ADR-0.0.58-prior-art-sensitivity-invariant
status: Draft
kind: foundation
semver: 0.0.58
lane: heavy
parent: PRD-GZKIT-1.0.0
bounded_context: artifact-authoring
date: 2026-05-22
---

# ADR-0.0.58-prior-art-sensitivity-invariant: Prior-Art Sensitivity Invariant for Artifact-Creating Surfaces

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

## Why foundation tier?

Without this ADR, gzkit's anti-vibing posture carries a class-shaped hole: only one artifact type (GHIs) is mechanically protected from sibling-cut duplication, and every other artifact-creating moment relies on cultural alertness that erodes under fatigue and model change. The project identity — making stochastic LLM vibing structurally inert — depends on prior-art lookup being a mechanical defense at every authoring moment, not a discipline some skills happen to remember. The named regression class (GHI #459/#460) was caught in GHIs but has been re-instantiated *this very session* in ADR design (Optimize / Pool Triage / Foundation Triage initially planned as greenfield, all already covered by prior art). The invariance: every artifact-creating skill MUST open with a corpus sweep against its corpus.

This ADR is a **port**: the prior-art-sensitivity invariant and the validator contract are abstract principles every artifact-creating skill must honor. The `gz validate --prior-art-coverage` scope, the per-skill Step 0 amendments, the `gz-design` corpus opening, and the SessionStart orientation extension are adapters behind this port.

## Intent

Current state: Prior-art lookup is enforced for only one artifact type — GHIs — via ghi-author's Step 0 (canonized in AGENTS.md Behavior Rule 13 after GHIs #459/#460 surfaced the sibling-cut regression). Every other artifact-creating moment relies on cultural alertness: operator memory ('they might be hanging out'), the agent happening to read the corpus before invoking the skill, or post-hoc catches by gz-adr-evaluate's advisory dimensions (OBPI allowed-paths overlap scored 3/4 not fail-closed). Design dialogues open without a corpus sweep; gz-adr-create, gz-plan, gz-prd, gz-specify interview Step 0 does not ask 'what existing artifacts touch this?'; skill/chore/validator authoring has the least ceremony and the most duplication risk. The class of failure is generic; the defenses are point-solutions. Adjacent governance work exists but does not generalize: ADR-pool.brief-authoring-evidence-checks covers OBPI-brief observed-evidence checks (scope-collision, drift validator) but is scoped to brief authoring only; ADR-pool.solved-problem-pattern-corpus proposes a post-hoc aggregated corpus of solved patterns, orthogonal to pre-authoring lookup; ADR-pool.insights-corpus-refresh-cadence governs insights corpus refresh but does not bind it to authoring-moment lookup. The general invariant — that EVERY artifact-creating moment opens with a corpus sweep — has no foundation-level home.

Target state: A foundation-tier invariant — prior-art lookup is mandatory before any artifact-creating skill invocation — backed by mechanical enforcement. gz validate --prior-art-coverage is a registered scope that surfaces near-matches against the artifact's corpus given a working title/slug. Every artifact-creating skill opens with a generalized Step 0 (the ghi-author template). gz-design opens dialogues with a corpus sweep against operator intent before any forcing-function question. SessionStart orientation injects corpus-adjacent state when an active OBPI or design dialogue is in flight. OBPI allowed-paths overlap is fail-closed via the sibling pool ADR ADR-pool.brief-authoring-evidence-checks (which this ADR sequences alongside but does not absorb). Cultural enforcement (Behavior Rule 13) is preserved as the why-frame but no longer the sole defense.

## Decision

1. Author the prior-art-sensitivity foundation invariant as the contract every artifact-creating skill binds to: .gzkit/rules/prior-art-sensitivity.md rule, AGENTS.md § Prior-Art Sensitivity section, advisory-rules-audit scorecard promotion from Promotable to Mechanical.
2. Implement gz validate --prior-art-coverage as a runnable scope: given working title/slug plus corpus scope (ADR registry, pool index, skill catalog, chore catalog, validator catalog), surfaces near-matches with ranking signals (title similarity, recent-by-date, keyword match); wired into gz check.
3. Generalize the ghi-author Step 0 pattern to every artifact-creating skill (gz-design, gz-adr-create, gz-plan, gz-prd, gz-specify, plus skill/chore/validator authoring skills); each skill's Step 0 invokes gz validate --prior-art-coverage scoped to its corpus and presents the result to the operator before any authoring step.
4. Specifically extend gz-design to open dialogues with a corpus sweep against operator intent before any forcing-function question fires; the dialogue's first turn is 'here is what already exists in this area' grounded in the validator output.
5. Extend SessionStart orientation (scripts/session_orientation.py) to inject corpus-adjacent state when an active OBPI or design dialogue is in flight, reducing post-compaction prior-art-blindness.
6. Sequence (not absorb) ADR-pool.brief-authoring-evidence-checks for the OBPI allowed-paths fail-closed validator; cite ADR-pool.solved-problem-pattern-corpus and ADR-pool.insights-corpus-refresh-cadence as future signal sources the prior-art-coverage scope can consume.

## Consequences

### Positive

1. The sibling-cut regression class (GHI #459/#460) becomes structurally inert across all artifact types, not just GHIs.
2. Cultural enforcement (operator memory, agent vigilance) becomes a redundancy on top of mechanical enforcement, not the primary defense — Behavior Rule 13 is preserved as doctrine, not as the only line of defense.
3. Design dialogues converge on routes (promote / amend / create) grounded in corpus reality rather than greenfield-assumption — directly preventing this very session's near-miss pattern (Optimize/Pool Triage/Foundation Triage initially planned as greenfield).
4. Drift between artifact-creation moments collapses: every skill follows the same Step 0 shape; the ghi-author template generalizes instead of remaining a one-off.
5. The gz validate --prior-art-coverage scope is reusable: invokable on demand by operators investigating whether a working idea is genuinely new, not only by skills at authoring time.

### Negative

1. Per-skill Step 0 sweeps add latency to artifact creation — a sweep plus presentation step before every invocation; the validator must be fast enough to not erode operator flow.
2. gz validate --prior-art-coverage is a new fail-closed surface: corpus-too-large or near-match-too-generous could create false-positive friction (must be calibrated; an initial advisory mode is the safer rollout shape).
3. Cultural enforcement might atrophy if operators treat the mechanical defense as sufficient; the doctrine doc must preserve the cultural framing as the why-frame, not let it be replaced.
4. New runtime dependency on the corpus scan in the hot path of artifact creation; if scan is slow, friction compounds across every gz-design / gz-adr-create / gz-plan invocation.
5. The cross-skill amendment surface is broad — five-plus skill SKILL.md files updated under one OBPI risks merge conflicts and partial implementation if not sequenced carefully.

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

- [ ] OBPI-0.0.58-01: **prior-art-invariant-doctrine** — Author `.gzkit/rules/prior-art-sensitivity.md` rule + AGENTS.md § Prior-Art Sensitivity section + advisory-rules-audit scorecard entry (Promotable to Mechanical promotion); update governance runbook; register the artifact-authoring BC vocabulary in PRD-GZKIT-1.0.0 § 2.1 per ADR-0.0.43 cascade contract; the doctrine is the contract every artifact-creating skill binds to.
- [ ] OBPI-0.0.58-02: **gz-validate-prior-art-coverage** — Implement `gz validate --prior-art-coverage` scope (given working title/slug + corpus scope: ADR registry, pool index, skill catalog, chore catalog, validator catalog); surfaces near-matches with ranking signals (title similarity, recent-by-date, keyword match); initial rollout is advisory mode; wired into `gz check` advisory pass; manpage; tests; fixtures.
- [ ] OBPI-0.0.58-03: **artifact-creation-skill-step-zero** — Amend artifact-creating skills (gz-design, gz-adr-create, gz-plan, gz-prd, gz-specify, plus skill/chore/validator authoring skills) to include mandatory Step 0 prior-art sweep invoking the new validator; generalizes the ghi-author Step 0 template (canonical source: .gzkit/skills/ghi-author/SKILL.md lines 108+); update each skill's SKILL.md and Common Rationalizations table.
- [ ] OBPI-0.0.58-04: **gz-design-corpus-opening** — Specifically extend gz-design to open dialogues with a corpus sweep against operator intent before any forcing-function question fires; the dialogue's first turn presents the existing-art landscape grounded in `--prior-art-coverage` output; update gz-design's manpage and rationale doc.
- [ ] OBPI-0.0.58-05: **session-orientation-corpus-injection** — Extend SessionStart orientation (`scripts/session_orientation.py`) to inject corpus-adjacent state when an active OBPI or design dialogue is in flight; update governance runbook; reduces post-compaction prior-art-blindness.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-05-22T20:23:41.067889*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.58-prior-art-sensitivity-invariant

### Q: What is the title of this ADR?

**A:** Prior-Art Sensitivity Invariant for Artifact-Creating Surfaces

### Q: What is the semantic version?

**A:** 0.0.58

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** Current state: Prior-art lookup is enforced for only one artifact type — GHIs — via ghi-author's Step 0 (canonized in AGENTS.md Behavior Rule 13 after GHIs #459/#460 surfaced the sibling-cut regression). Every other artifact-creating moment relies on cultural alertness: operator memory ('they might be hanging out'), the agent happening to read the corpus before invoking the skill, or post-hoc catches by gz-adr-evaluate's advisory dimensions (OBPI allowed-paths overlap scored 3/4 not fail-closed). Design dialogues open without a corpus sweep; gz-adr-create, gz-plan, gz-prd, gz-specify interview Step 0 does not ask 'what existing artifacts touch this?'; skill/chore/validator authoring has the least ceremony and the most duplication risk. The class of failure is generic; the defenses are point-solutions. Adjacent governance work exists but does not generalize: ADR-pool.brief-authoring-evidence-checks covers OBPI-brief observed-evidence checks (scope-collision, drift validator) but is scoped to brief authoring only; ADR-pool.solved-problem-pattern-corpus proposes a post-hoc aggregated corpus of solved patterns, orthogonal to pre-authoring lookup; ADR-pool.insights-corpus-refresh-cadence governs insights corpus refresh but does not bind it to authoring-moment lookup. The general invariant — that EVERY artifact-creating moment opens with a corpus sweep — has no foundation-level home.

Target state: A foundation-tier invariant — prior-art lookup is mandatory before any artifact-creating skill invocation — backed by mechanical enforcement. gz validate --prior-art-coverage is a registered scope that surfaces near-matches against the artifact's corpus given a working title/slug. Every artifact-creating skill opens with a generalized Step 0 (the ghi-author template). gz-design opens dialogues with a corpus sweep against operator intent before any forcing-function question. SessionStart orientation injects corpus-adjacent state when an active OBPI or design dialogue is in flight. OBPI allowed-paths overlap is fail-closed via the sibling pool ADR ADR-pool.brief-authoring-evidence-checks (which this ADR sequences alongside but does not absorb). Cultural enforcement (Behavior Rule 13) is preserved as the why-frame but no longer the sole defense.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** 1. Author the prior-art-sensitivity foundation invariant as the contract every artifact-creating skill binds to: .gzkit/rules/prior-art-sensitivity.md rule, AGENTS.md § Prior-Art Sensitivity section, advisory-rules-audit scorecard promotion from Promotable to Mechanical.
2. Implement gz validate --prior-art-coverage as a runnable scope: given working title/slug plus corpus scope (ADR registry, pool index, skill catalog, chore catalog, validator catalog), surfaces near-matches with ranking signals (title similarity, recent-by-date, keyword match); wired into gz check.
3. Generalize the ghi-author Step 0 pattern to every artifact-creating skill (gz-design, gz-adr-create, gz-plan, gz-prd, gz-specify, plus skill/chore/validator authoring skills); each skill's Step 0 invokes gz validate --prior-art-coverage scoped to its corpus and presents the result to the operator before any authoring step.
4. Specifically extend gz-design to open dialogues with a corpus sweep against operator intent before any forcing-function question fires; the dialogue's first turn is 'here is what already exists in this area' grounded in the validator output.
5. Extend SessionStart orientation (scripts/session_orientation.py) to inject corpus-adjacent state when an active OBPI or design dialogue is in flight, reducing post-compaction prior-art-blindness.
6. Sequence (not absorb) ADR-pool.brief-authoring-evidence-checks for the OBPI allowed-paths fail-closed validator; cite ADR-pool.solved-problem-pattern-corpus and ADR-pool.insights-corpus-refresh-cadence as future signal sources the prior-art-coverage scope can consume.

### Q: What good things result from this decision? List benefits.

**A:** 1. The sibling-cut regression class (GHI #459/#460) becomes structurally inert across all artifact types, not just GHIs.
2. Cultural enforcement (operator memory, agent vigilance) becomes a redundancy on top of mechanical enforcement, not the primary defense — Behavior Rule 13 is preserved as doctrine, not as the only line of defense.
3. Design dialogues converge on routes (promote / amend / create) grounded in corpus reality rather than greenfield-assumption — directly preventing this very session's near-miss pattern (Optimize/Pool Triage/Foundation Triage initially planned as greenfield).
4. Drift between artifact-creation moments collapses: every skill follows the same Step 0 shape; the ghi-author template generalizes instead of remaining a one-off.
5. The gz validate --prior-art-coverage scope is reusable: invokable on demand by operators investigating whether a working idea is genuinely new, not only by skills at authoring time.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Per-skill Step 0 sweeps add latency to artifact creation — a sweep plus presentation step before every invocation; the validator must be fast enough to not erode operator flow.
2. gz validate --prior-art-coverage is a new fail-closed surface: corpus-too-large or near-match-too-generous could create false-positive friction (must be calibrated; an initial advisory mode is the safer rollout shape).
3. Cultural enforcement might atrophy if operators treat the mechanical defense as sufficient; the doctrine doc must preserve the cultural framing as the why-frame, not let it be replaced.
4. New runtime dependency on the corpus scan in the hot path of artifact creation; if scan is slow, friction compounds across every gz-design / gz-adr-create / gz-plan invocation.
5. The cross-skill amendment surface is broad — five-plus skill SKILL.md files updated under one OBPI risks merge conflicts and partial implementation if not sequenced carefully.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. prior-art-invariant-doctrine: Author .gzkit/rules/prior-art-sensitivity.md rule + AGENTS.md § Prior-Art Sensitivity section + advisory-rules-audit scorecard entry (Promotable to Mechanical promotion); update governance runbook; the doctrine is the contract every artifact-creating skill binds to.
2. gz-validate-prior-art-coverage: Implement gz validate --prior-art-coverage scope (given working title/slug + corpus scope: ADR registry, pool index, skill catalog, chore catalog, validator catalog); surfaces near-matches with ranking signals (title similarity, recent-by-date, keyword match); wired into gz check advisory pass; manpage; tests; fixtures.
3. artifact-creation-skill-step-zero: Amend artifact-creating skills (gz-design, gz-adr-create, gz-plan, gz-prd, gz-specify, plus skill/chore/validator authoring skills) to include mandatory Step 0 prior-art sweep invoking the new validator; generalizes the ghi-author Step 0 template; update each skill's SKILL.md and Common Rationalizations table.
4. gz-design-corpus-opening: Specifically extend gz-design to open dialogues with a corpus sweep against operator intent before any forcing-function question fires; the dialogue's first turn presents the existing-art landscape; update gz-design's manpage and rationale doc.
5. session-orientation-corpus-injection: Extend SessionStart orientation (scripts/session_orientation.py) to inject corpus-adjacent state when an active OBPI or design dialogue is in flight; update governance runbook; reduces post-compaction prior-art-blindness.

### Q: What alternatives were considered and why were they rejected?

**A:** 1. Continue cultural enforcement only — rejected: Behavior Rule 13 covered GHIs only and even then needed a sibling-cut regression to be canonized; cultural enforcement does not generalize without mechanical backing. This very session demonstrated the failure: the design dialogue produced a 'create 3 new ADRs' plan without any prior-art check, caught only at orientation by deliberate agent vigilance.
2. Per-skill Step 0 amendments without the central validator — rejected: each skill would reinvent its own prior-art-sweep heuristic; drift between implementations would be the next failure mode (the class-of-failure-not-instance principle, AGENTS.md DO IT RIGHT #1).
3. Validator-only without skill amendments — rejected: a validator that nobody invokes is doctrine drift; the skill amendments are what guarantee invocation at the right moment.
4. Absorb ADR-pool.brief-authoring-evidence-checks into this ADR — rejected: that pool ADR's four defenses (file-size cap, scope-collision, manpage-anchor, drift validator) are mechanical defenses OF brief-authoring observed-evidence discipline, a sibling problem class. Absorbing would conflate two distinct invariants and bloat the OBPI count.
5. Wait for ADR-0.0.43 DDD cascade to mature, then bind prior-art-sensitivity to the cascade vocabulary — rejected as sole approach (partially adopted: this ADR registers its vocabulary in PRD § 2.1 when the cascade lands, but the invariant itself ships independently of the cascade's implementation timing).


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. Continue cultural enforcement only — rejected: Behavior Rule 13 covered GHIs only and even then needed a sibling-cut regression to be canonized; cultural enforcement does not generalize without mechanical backing. This very session demonstrated the failure: the design dialogue produced a 'create 3 new ADRs' plan without any prior-art check, caught only at orientation by deliberate agent vigilance.
2. Per-skill Step 0 amendments without the central validator — rejected: each skill would reinvent its own prior-art-sweep heuristic; drift between implementations would be the next failure mode (the class-of-failure-not-instance principle, AGENTS.md DO IT RIGHT #1).
3. Validator-only without skill amendments — rejected: a validator that nobody invokes is doctrine drift; the skill amendments are what guarantee invocation at the right moment.
4. Absorb ADR-pool.brief-authoring-evidence-checks into this ADR — rejected: that pool ADR's four defenses (file-size cap, scope-collision, manpage-anchor, drift validator) are mechanical defenses OF brief-authoring observed-evidence discipline, a sibling problem class. Absorbing would conflate two distinct invariants and bloat the OBPI count.
5. Wait for ADR-0.0.43 DDD cascade to mature, then bind prior-art-sensitivity to the cascade vocabulary — rejected as sole approach (partially adopted: this ADR registers its vocabulary in PRD § 2.1 when the cascade lands, but the invariant itself ships independently of the cascade's implementation timing).

## Bounded Context

This ADR introduces and belongs to the **`artifact-authoring`** bounded context (per ADR-0.0.43 DDD Domain Cascade). Vocabulary to be codified in PRD-GZKIT-1.0.0 § 2.1 by OBPI-01 with provenance to this ADR: `prior-art-sweep`, `corpus-coverage-scope`, `step-zero-pre-flight`, `sibling-cut-duplicate`, `corpus-similarity-signal`, `artifact-authoring-moment`. The cross-cutting kernel (`rubric-dimension`, `rubric-finding`, `evidence-citation`) registered by the skill-evaluation / governance-triage BCs in ADR-0.51.0 / ADR-0.0.57 is reused here for the validator's ranking output.

## Dependencies

- **`ADR-0.0.43-ddd-domain-cascade`** (Draft, foundation) — Provides the bounded-context frontmatter convention and the `UbiquitousLanguageTerm` schema OBPI-01 registers terms against. Same Path-2 use-pull as ADR-0.51.0 and ADR-0.0.57 — this ADR is another waiting consumer of the cascade infrastructure.
- **`.gzkit/skills/ghi-author/SKILL.md`** § Step 0 (lines 108-115 + 264-282) — The canonical template OBPI-03 generalizes across artifact-creating skills. The named regression (GHI #459/#460) and the operative pattern both live here.
- **AGENTS.md § Behavior Rules — Always #13** — Cultural enforcement of prior-art lookup for GHIs only. OBPI-01 extends this rule into a general section and a `.gzkit/rules/prior-art-sensitivity.md` document.
- **`ADR-pool.brief-authoring-evidence-checks`** (Pool) — **Sequenced sibling, not absorbed.** Its four mechanical defenses (file-size cap, scope-collision, manpage-anchor check, drift validator) cover the OBPI allowed-paths fail-closed surface. This ADR is the general invariant; that pool ADR is the OBPI-specific mechanical surface; they compose. Promotion of that pool ADR is the natural next step after OBPI-02 lands.
- **`ADR-pool.solved-problem-pattern-corpus`** (Pool) — Future signal source the `--prior-art-coverage` scope can consume once it lands.
- **`ADR-pool.insights-corpus-refresh-cadence`** (Pool) — Future calibration source for how often corpus-coverage signals should refresh.

## Implementation Precedent

- `.gzkit/skills/ghi-author/SKILL.md` lines 108-115 (Step 0 prior-art lookup block) — verbatim template OBPI-03 generalizes across artifact-creating skills.
- `AGENTS.md` § Behavior Rules — Always #13 — cultural enforcement source that OBPI-01 promotes from skill-specific to general.
- `src/gzkit/trust_audits.py` — module hosting `gz validate --<scope>` implementations; OBPI-02 adds the `--prior-art-coverage` scope following the established pattern (parallel to `--cli-alignment`, `--taxonomy`, `--documents`).
- `scripts/session_orientation.py` — SessionStart orientation hook OBPI-05 extends with corpus-adjacent state injection.
- `src/gzkit/registry.py` — ADR / pool / skill / chore registry surfaces the validator reads to compute corpus-coverage signals.
- `.gzkit/insights/agent-insights.jsonl` — append-only insight stream the validator may consult for recent-by-date prior-art adjacency.

**Exemplar / Precedent.** The Step-0 template is `ghi-author`'s — proven against GHI #459/#460. The validator pattern follows `gz validate --commit-trailers` / `gz validate --taxonomy` / `gz validate --documents` — established `gz validate --<scope>` plug-in shape. The Promotable→Mechanical promotion follows the precedent in `docs/governance/advisory-rules-audit.md`. The cross-skill amendment pattern mirrors `ADR-0.0.43` OBPI-09 (existing-skill-extensions).

**Anti-pattern.** Do not treat the validator as the only defense — the cultural framing (operator vigilance, Behavior Rule 13) is preserved as the why-frame; the mechanical surface is the how-frame. Do not run `gz validate --prior-art-coverage` as fail-closed in initial rollout — start in advisory mode; calibrate false-positive rate; flip to fail-closed only when corpus scan and ranking are proven. Do not absorb `ADR-pool.brief-authoring-evidence-checks` into this ADR — that conflates two distinct invariants (artifact-creating-moment prior-art lookup vs OBPI-brief observed-evidence coherence). Do not let per-skill Step 0 implementations diverge — they must all invoke the central validator, not reinvent the heuristic per skill.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.58 | Pending | | | |
