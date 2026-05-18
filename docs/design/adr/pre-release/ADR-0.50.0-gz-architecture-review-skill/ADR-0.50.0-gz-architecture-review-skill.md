---
id: ADR-0.50.0-gz-architecture-review-skill
status: Proposed
kind: feature
semver: 0.50.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-18
promoted_from: ADR-pool.gz-architecture-review-skill
---

# ADR-0.50.0-gz-architecture-review-skill: gz-architecture-review skill (deep/shallow modules, deletion test)

## Persona

`quality-reviewer` — read `.gzkit/personas/quality-reviewer.md`. Architectural-rigor, SOLID principles, and maintainability assessment are not rules to follow — they are who you are while reviewing. The architecture-review skill makes structural seam recommendations grounded in the deletion test and the deep-vs-shallow module heuristic, presents numbered candidates for operator selection, and grills the chosen candidate through a design tree conversation.

## Intent

gzkit has multiple code-quality review skills — `gz-tech-debt-review`
(synthesizer), `gz-pythonic-pattern-detect` (AST-class patterns),
`gz-complexity-advisor` (cyclomatic/cognitive metrics), `gz-obpi-simplify`
(brief-scoped review). None operate at the **module-boundary / architectural
seam tier** — proposing deeper interfaces, surfacing shallow modules that
should be deepened or deleted, naming where seams should live.

This ADR scaffolds `gz-architecture-review` — a new code-quality skill
inspired by Matt Pocock's `improve-codebase-architecture` skill
(https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md)
adapted for gzkit's governance posture. The skill is the canonical
architectural-tier review dispatched by ADR-0.0.51's milestone-maintenance
pipeline.

## Decision

Create `gz-architecture-review` skill with:

- **Persona**: `quality-reviewer`
- **Adopted from Pocock (canonical)**:
  - Deep-vs-shallow module vocabulary (Ousterhout): module / interface /
    implementation / depth / seam / adapter / leverage / locality
  - **Deletion test** as named heuristic: "Imagine deleting the module. If
    complexity vanishes, it was a pass-through. If complexity reappears across
    N callers, it was earning its keep."
  - **One adapter = hypothetical seam, two adapters = real seam** — guards
    against premature abstraction (aligns with CLAUDE.md "three similar lines
    is better than a premature abstraction").
  - **Three-phase workflow**: Explore → Numbered Candidates → Grilling Loop
    on one selected candidate. Operator gate at Present Candidates respects
    Operator Economy of Effort doctrine.
- **Adapted for gzkit (NOT taken wholesale)**:
  - Reads `AGENTS.md` + `docs/design/adr/{foundation,pre-release}/**` for
    domain context (NOT Pocock's `CONTEXT.md` / `LANGUAGE.md` assumptions).
  - Routing of findings follows gzkit's existing thresholds: trivial →
    fix-in-place, tracked → GHI via `/ghi-author`, architectural absence →
    ADR draft via `/gz-design`. NOT raw GitHub-issue RFCs (would conflict
    with `gz-tech-debt-review`'s "≤1 GHI per run, never directly to OBPI"
    routing).
  - **Rejection-with-load-bearing-reason → offer ADR** loop (Pocock's
    highest-leverage idea) — when operator rejects a deepening candidate with
    a structural reason, agent offers to record the rejection as an ADR so
    future architecture reviews don't re-suggest it.
- **Scope boundary statement** (per session decision, prevents skill-bloat):
  - **In scope**: module-seam tier — where do shallow modules need deepening,
    where should new seams live, what's the deletion-test verdict on each
    suspected pass-through.
  - **Out of scope**: pattern-level (covered by `gz-pythonic-pattern-detect`),
    metric-level (covered by `gz-complexity-advisor`), aggregation
    (covered by `gz-tech-debt-review`), brief-scoped (covered by
    `gz-obpi-simplify`).

## Consequences

### Positive

- Fills the named architectural-tier review gap. Existing review skills (`gz-tech-debt-review`, `gz-pythonic-pattern-detect`, `gz-complexity-advisor`, `gz-obpi-simplify`) cover pattern / metric / synthesis / brief-scope tiers; the module-seam tier had no canonical home until this skill.
- Lands the canonical first dispatched skill in ADR-0.0.51's milestone-maintenance sweep manifest `foundation` block. Without it, the milestone pipeline has no architecture-tier check at all.
- The rejection-with-load-bearing-reason → ADR-draft loop closes a recurring failure: architecture suggestions that get re-proposed every review cycle because the prior rejection wasn't captured as canon.
- Anti-pattern guard: the deletion-test heuristic gives operators a concrete grip on "is this module shallow." Without that grip, "shallow" is a taste call and review devolves into preference debates.
- Scope-boundary statement (`In scope: module-seam tier; Out of scope: pattern/metric/aggregation/brief-scope`) is named in the skill body and validated, preventing the bloat that has killed similar review skills in other projects.

### Negative

- New skill surface to maintain. The deletion-test and deep-shallow heuristics are durable (Ousterhout's original definitions are stable) but the skill body will accumulate gzkit-specific adaptations over time. Mitigated by the scope-boundary statement and follow-on tech-debt sweeps on the skill itself.
- The three-phase workflow (Explore → Numbered Candidates → Grilling Loop) is operator-supervised — not autonomous. Operators who want push-button review will feel friction. Mitigated: this is by design (Operator Economy of Effort: agent drafts candidates, operator picks; never autonomous architectural decisions).

### Anti-patterns this ADR forbids

- Reviewing architecture at the brief-scope or method-scope tier (those have their own skills); pulling architectural-tier judgment into a brief review.
- Auto-applying suggested deepenings without operator review — architectural seams are structural decisions; the operator decides, the skill drafts.
- Adopting the Pocock skill wholesale (CONTEXT.md/LANGUAGE.md/flat ADR dir/raw GitHub-issue RFC outputs). The adaptation rules in § Decision are binding.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 7
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.50.0-01: `gz-architecture-review` skill body + persona binding (`quality-reviewer`)
- [ ] OBPI-0.50.0-02: Three-phase workflow implementation (Explore → Numbered Candidates → Grilling Loop) with deletion-test and seam-doubling-rule heuristics
- [ ] OBPI-0.50.0-03: Findings-routing thresholds (trivial → fix-in-place, tracked → GHI via `/ghi-author`, architectural absence → ADR draft via `/gz-design`)
- [ ] OBPI-0.50.0-04: Integration into ADR-0.0.51 sweep manifest + rejection-with-reason → ADR-draft loop

## Target Scope

Create `gz-architecture-review` skill (module-seam tier code-quality review) as the canonical first dispatched skill in ADR-0.0.51's milestone-maintenance sweep manifest `foundation` block. Pocock-inspired highlights adapted for gzkit's surfaces (AGENTS.md + structured ADR packages, not Pocock's CONTEXT.md / LANGUAGE.md assumptions); routing of findings follows gzkit's existing thresholds. The scope decomposes into four OBPIs — each bullet below becomes one OBPI slug at promotion time. Detailed specification lives in § Decision above.

- `gz-architecture-review` skill body + persona binding (`quality-reviewer`)
- Three-phase workflow implementation (Explore → Numbered Candidates → Grilling Loop) with deletion-test and seam-doubling-rule heuristics
- Findings-routing thresholds (trivial → fix-in-place, tracked → GHI via `/ghi-author`, architectural absence → ADR draft via `/gz-design`)
- Integration into ADR-0.0.51 sweep manifest + rejection-with-reason → ADR-draft loop

## Notes

**Session context (2026-05-18):** This pool ADR preserves framing established
during the design dialogue that authored ADR-0.0.50 (validation pipeline)
and ADR-0.0.51 (milestone maintenance pipeline). The architecture-review
skill is the canonical dispatched skill for the milestone-maintenance
pipeline's architecture-tier check; the pipeline ADR cites this pool ADR.

Originated from the operator's invocation of Matt Pocock's
`skills/engineering/improve-codebase-architecture` as a candidate for
adoption — "to adopt highlights from, not wholesale inclusion."

Promotion path: feature kind, semver TBD (next available `0.Y.0` after
0.42.0). Promote when the milestone-maintenance pipeline (ADR-0.0.51)
reaches Stage-1 implementation and needs its first canonical dispatched
review skill.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.gz-architecture-review-skill` on 2026-05-18; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- **Extend `gz-tech-debt-review` to cover architectural seams.** Rejected. Tech-debt review is a synthesizer of existing analyzer output (chores, validators, ruff, ty, xenon, radon). The architectural-seam tier needs AST-walking and semantic-grouping analysis that's not in any existing analyzer; bundling it inflates tech-debt-review's scope and breaks its "synthesize, don't analyze" boundary.
- **Adopt Pocock's skill wholesale.** Rejected per session decision. His skill assumes `CONTEXT.md` / `LANGUAGE.md` and a flat `docs/adr/`; gzkit's surfaces (AGENTS.md, structured ADR packages, GHI/OBPI routing) differ enough that wholesale adoption would produce a skill that fights the host governance. Adopt the highlights, adapt the rest.
- **Skip the skill, rely on operator/ad-hoc architectural review.** Rejected. Architectural-tier review is the named gap in the milestone-maintenance pipeline (ADR-0.0.51) and is the cohort that started the design conversation (operator's original Matt Pocock thread on 2026-05-18). Skipping leaves the milestone pipeline without its canonical architectural review step.
- **Build the skill as foundation tier (a port) rather than feature (a adapter).** Rejected. The architectural-review skill IS a adapter into ADR-0.0.51's sweep manifest port. Pocock's contributions (deletion test, deep-vs-shallow vocabulary) are doctrine-shaped but they're a SPECIFIC adapter's design philosophy, not a port that other adapters would extend. If a second architecture-review skill ever lands (unlikely), the port consideration could be revisited.
- **Auto-apply trivial deepenings without operator review.** Rejected. Architectural decisions are structural and the operator must own them. The agent drafts candidates and grills the selected one; the operator decides. Per Operator Economy of Effort: agent drafts, operator chooses; never autonomous structural rewrites.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.50.0 | Pending | | | |
