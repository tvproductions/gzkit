---
id: ADR-pool.gz-architecture-review-skill
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.gz-architecture-review-skill: gz-architecture-review skill (deep/shallow modules, deletion test)

## Status

Superseded

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

## Target Scope

Create `gz-architecture-review` skill (module-seam tier code-quality review) as the canonical first dispatched skill in ADR-0.0.51's milestone-maintenance sweep manifest `foundation` block. Pocock-inspired highlights adapted for gzkit's surfaces (AGENTS.md + structured ADR packages, not Pocock's CONTEXT.md / LANGUAGE.md assumptions); routing of findings follows gzkit's existing thresholds. The scope decomposes into four OBPIs — each bullet below becomes one OBPI slug at promotion time. Detailed specification lives in § Decision above.

- `gz-architecture-review` skill body + persona binding (`quality-reviewer`)
- Three-phase workflow implementation (Explore → Numbered Candidates → Grilling Loop) with deletion-test and seam-doubling-rule heuristics
- Findings-routing thresholds (trivial → fix-in-place, tracked → GHI via `/ghi-author`, architectural absence → ADR draft via `/gz-design`)
- Integration into ADR-0.0.51 sweep manifest + rejection-with-reason → ADR-draft loop

## Alternatives Considered

- **Extend `gz-tech-debt-review` to cover architectural seams** — rejected.
  Tech-debt review is a synthesizer of existing analyzer output (chores,
  validators, ruff, ty, xenon, radon). The architectural-seam tier needs
  AST-walking and semantic-grouping analysis that's not in any existing
  analyzer; bundling it inflates tech-debt-review's scope and breaks its
  "synthesize, don't analyze" boundary.
- **Adopt Pocock's skill wholesale** — rejected per session decision. His
  skill assumes `CONTEXT.md` / `LANGUAGE.md` and a flat `docs/adr/`; gzkit's
  surfaces (AGENTS.md, structured ADR packages, GHI/OBPI routing) differ
  enough that wholesale adoption would produce a skill that fights the host
  governance. Adopt the highlights, adapt the rest.
- **Skip the skill, rely on operator/ad-hoc architectural review** —
  rejected. Architectural-tier review is one of the named gaps in the
  milestone-maintenance pipeline (ADR-0.0.51) and is the cohort that started
  the design conversation (operator's original Matt Pocock thread). Skipping
  leaves the milestone pipeline without its canonical architectural review
  step.

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
