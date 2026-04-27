---
id: ADR-pool.skill-control-surface-contract
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
complements:
  - ADR-pool.skill-feedback-loop
  - ADR-pool.skill-tuning-feedback-loop
  - ADR-pool.skill-behavioral-hardening
inspired_by: arXiv:2603.28052v1 Meta-Harness
---

# ADR-pool.skill-control-surface-contract: Skill Control Surface Contract

## Status

Pool

## Intent

Adopt a canonical structure doctrine for gzkit skills as agent-control
surfaces.

The broader Meta-Harness recommendation is not only "tune skills
empirically." It is that skill text is the primary steering interface for
agent behavior and should define the role, directory layout, CLI commands,
output format, forbidden behavior, artifacts, and objectives while leaving
diagnosis open to repository evidence. gzkit already treats skills as
agent-called infrastructure; this pool item makes their structural contract
explicit.

This complements:

- `ADR-pool.skill-feedback-loop`: qualitative intake for skill friction.
- `ADR-pool.skill-tuning-feedback-loop`: empirical candidate comparison.
- `ADR-pool.skill-behavioral-hardening`: rationalization defenses and circuit
  breakers.

The missing layer is the canonical shape every serious gzkit skill should
converge toward before feedback, tuning, or hardening can work reliably.

## Decision

Define `SKILL.md` as an agent-control surface with a mandatory structural
contract for non-alias skills.

Every serious gzkit skill should converge toward this shape:

```text
Purpose
When To Use
Scope And Authority
Inputs
Allowed Paths / Surfaces
Forbidden Actions
Procedure
Diagnostic Freedom
Output Contract
Evidence / Receipts
Failure Modes
Circuit Breakers
Related Skills
```

Section responsibilities:

- Purpose states the capability and why it exists.
- When To Use provides routing triggers in operator and agent vocabulary.
- Scope And Authority names whether the skill is read-only, mutating,
  advisory, ceremony-owning, or pipeline-owning.
- Inputs names required identifiers, artifacts, environment assumptions, and
  preconditions.
- Allowed Paths / Surfaces defines where the skill may read or write when it
  performs mutating work.
- Forbidden Actions states non-negotiable boundaries: ledger direct edits,
  Gate 5 bypass, scope expansion, autonomous promotion, or other skill-specific
  hazards.
- Procedure gives the workflow, but only to the level needed to preserve
  governance order.
- Diagnostic Freedom is the new structural doctrine: the skill constrains
  outputs, safety boundaries, artifacts, and objectives; it does not prescribe
  which evidence the agent must inspect first. The agent may inspect scores,
  traces, prior attempts, logs, source files, ARB receipts, insights, and
  relevant ADR/OBPI state as needed.
- Output Contract states the exact artifact, report, command result, evidence
  table, or review surface the skill must produce.
- Evidence / Receipts names required ARB receipts, observed-output rules, or
  proof locations.
- Failure Modes names predictable drift and underperformance shapes.
- Circuit Breakers names when the agent must stop, report, and wait for
  operator direction.
- Related Skills names adjacent skills and routing boundaries.

This doctrine should be implemented through the existing skill-quality surfaces
rather than a parallel system:

1. `skill-authoring-quality` gains checks for role, authority, forbidden
   actions, diagnostic freedom, output contract, failure modes, and circuit
   breakers.
2. `skill-trigger-testing` uses the `When To Use` and `Scope And Authority`
   sections to evaluate undertrigger, overtrigger, and wrong-authority behavior.
3. `ADR-pool.skill-tuning-feedback-loop` uses this structure as candidate
   validation before empirical tuning.
4. `ADR-pool.skill-behavioral-hardening` consumes `Forbidden Actions`,
   `Failure Modes`, and `Circuit Breakers` as the placement home for
   anti-rationalization patterns.

## Alternatives Considered

1. Fold this into `ADR-pool.skill-behavioral-hardening` - rejected. Behavioral
   hardening is about rationalization defenses. The skill-control-surface
   contract is broader: it defines shape, authority, outputs, and diagnostic
   freedom for every serious skill.
2. Fold this into `ADR-pool.skill-tuning-feedback-loop` - rejected. Tuning is a
   quantitative feedback loop. It needs a canonical skill shape to validate
   candidates against, but it should not own that doctrine.
3. Keep the structure as chore guidance only - rejected. Chores can audit the
   shape, but the shape itself is doctrine. Without an ADR home, every audit is
   an implementation preference rather than a governed decision.
4. Require one rigid template for all skills - rejected. Some skills are thin
   aliases or command routers. The doctrine applies to non-alias skills and
   should allow sections to be explicitly marked not applicable when the reason
   is structural and documented.

## Proposed OBPI Decomposition

| Slug | Description |
|------|-------------|
| `canonical-section-contract` | Define canonical section expectations for non-alias `SKILL.md` files, including required, optional, and explicitly-not-applicable sections. |
| `diagnostic-freedom-doctrine` | Add the `Diagnostic Freedom` doctrine so skills constrain outputs, safety, artifacts, and objectives without over-prescribing evidence inspection order. |
| `skill-authority-modes` | Classify skill authority modes: read-only, advisory, mutating, ceremony-owning, and pipeline-owning, with scope-expansion implications for each. |
| `skill-quality-chore-checks` | Extend skill-quality chores to audit structure, authority, forbidden actions, output contract, failure modes, and circuit breakers. |
| `template-and-authoring-guidance` | Update skill templates and authoring guidance so new skills are born in the contract shape instead of retrofitted later. |
| `mirror-sync-preservation` | Preserve existing `skill-version` and mirror-sync discipline while adding the structural contract. |

## Non-Goals

- No immediate rewrite of every existing skill.
- No autonomous skill edit or promotion behavior.
- No replacement for `ADR-pool.skill-feedback-loop`,
  `ADR-pool.skill-tuning-feedback-loop`, or `ADR-pool.skill-behavioral-hardening`.
- No vendor-specific skill format that only works in one agent harness.
- No mandate that thin alias skills carry every section when they intentionally
  delegate to a CLI surface.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. The operator accepts the split between structure doctrine, qualitative
   feedback, quantitative tuning, and behavioral hardening.
2. The canonical section list is accepted or revised.
3. The first migration target set is chosen; recommended first targets are
   `gz-design`, `gz-obpi-pipeline`, `ghi-close`, `gz-justify`, and `git-sync`.
4. The alias-vs-serious-skill boundary is defined so thin wrappers are not
   forced into artificial bulk.
5. Chore-level acceptance checks can be specified without making existing
   skills fail before a staged migration exists.

## Design Notes

The most important new section is `Diagnostic Freedom`.

Meta-Harness argues that a skill should specify what is forbidden, what
artifacts to produce, and what objectives to optimize, while leaving the agent
free to inspect scores, traces, and prior code as needed. gzkit's translation is
that a skill may constrain governance order and safety boundaries, but it should
not collapse diagnosis into a fixed checklist when the correct move is to read
the evidence surface.

The target failure class is an overfitted skill that looks complete but causes
the agent to skip the actual evidence because the skill preselected the wrong
evidence path. The doctrine keeps the output contract tight and the diagnostic
search open.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
