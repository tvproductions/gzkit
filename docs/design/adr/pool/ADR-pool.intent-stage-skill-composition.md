---
id: ADR-pool.intent-stage-skill-composition
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.intent-stage-skill-composition: Intent-Stage Skill Composition Contract

## Status

Pool

## Date

2026-05-11

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Define the artifact-graph composition contract for the four skills that
together perform the Intent stage of a gzkit project: `gz-prd`,
`gz-constitute`, `gz-design`, and `gz-adr-create`. Today these four skills
are narrated by the storybook (`docs/user/storybook/from-init-to-first-attested-release.md`
§ Stage 2 — Intent) as a smooth pipeline — PRD records project-level intent,
Constitution captures invariants, Design produces an ADR draft, ADR-Create
lands it. The narration implies cohesion that the skill surfaces do not
mechanically deliver.

Verification (GHI #429) shows:

- `gz-prd` SKILL.md and `gz-constitute` SKILL.md are stub-level (each ~33
  lines) with **no documented Inputs or Outputs** and **no documented
  downstream handoff** to the next skill in the stage.
- `gz-design` SKILL.md is detailed but its Step 1 ("Explore Context") reads
  `gz status`, `gz state`, pool ADRs, and source files. It does **not** read
  the PRD or Constitution artifacts produced by the prior two skills, and
  contains zero references to either.
- `gz-adr-create` SKILL.md is detailed but its Inputs section lists only
  `adr_id`, `title`, `series`, `brief_count`. It contains zero references to
  consuming PRD or Constitution evidence. The handoff from `gz-design`
  is implicit (the design conversation populates Intent/Decision/Rationale
  sections at authoring time) but is not declared as a contract.

The CLI verbs `gz prd` and `gz constitute` exist and produce real artifacts.
The seam is **not** absent verbs — it is **absent contracts between the
skills' artifact graphs**. The Intent stage is a narrative pipeline, not a
mechanical one.

This pool ADR is the design home for that contract conversation. It does
not pre-decide the answer; the right shape (frontmatter `inputs:` /
`outputs:` blocks; a skill-frontmatter convention; runtime artifact-presence
checks; a `gz-design` Step 1 expansion that ingests PRD/Constitution; or a
combination) is the design discussion this pool ADR triggers when promoted.

---

## Target Scope

### Composition contract — what each Intent-stage skill consumes and produces

For each of `gz-prd`, `gz-constitute`, `gz-design`, `gz-adr-create`, declare:

- **Inputs:** prior-stage artifact path(s), required frontmatter fields, and
  required content sections the downstream skill reads.
- **Outputs:** artifact path, frontmatter shape, and the sections downstream
  skills must be able to consume.
- **Handoff verification:** the mechanical check that confirms an upstream
  artifact exists and carries the expected shape before the next skill runs.

### Skill-level wiring updates

- `gz-prd` SKILL.md must declare its output artifact path, frontmatter
  shape, and which sections feed `gz-constitute` (project intent, success
  criteria, scope statement, non-goals).
- `gz-constitute` SKILL.md must declare its input contract against the PRD
  (what PRD content shapes invariants) and its output artifact path /
  frontmatter / invariant-section shape that `gz-design` ingests.
- `gz-design` SKILL.md Step 1 ("Explore Context") must extend to read the
  active PRD and Constitution before the dialogue begins. The "Explore
  Context" list is the load-bearing handoff surface; today it is silent on
  upstream Intent artifacts.
- `gz-adr-create` SKILL.md Inputs section must declare the design-session
  outputs it consumes (or the upstream `gz-design` invocation it requires)
  rather than treating ADR creation as a context-free authoring action.

### Storybook narrative alignment

The storybook's Stage 2 — Intent narrative either (a) remains and the
underlying skills are wired to honor it, or (b) is hedged where the
mechanical wiring intentionally stops short. The choice between (a) and (b)
is part of this pool ADR's design conversation.

### Validator / freshness check (optional, design-conversation outcome)

A `gz validate --intent-stage-coherence` audit could mechanically enforce
that PRD → Constitution → Design → ADR-Create handoffs declare and consume
their contracts. Whether this is worth the validator surface is a design
question, not a pre-decided promotion criterion.

---

## Non-Goals

- This pool ADR does **not** propose new CLI verbs. `gz prd`, `gz constitute`,
  `gz design`, and `gz adr-create` (via `gz plan create` / `gz adr promote`)
  already exist and produce artifacts.
- This pool ADR does **not** subsume GHI #428 (missing operator-runbook
  first-time-operator entry). That is an operator-facing documentation
  defect; this pool ADR is about the skill-to-skill artifact-graph contract.
- No OBPI briefs. OBPIs begin only after promotion to a SemVer ADR.
- No retroactive rewrite of PRD-GZKIT-1.0.0 or existing constitution
  artifacts — the scope is the **handoff contracts**, not the artifacts
  already authored under the current arrangement.

---

## Dependencies

- **Blocks on**: None.
- **Blocked by**: None.
- **Related**:
  - GHI #428 (operator-runbook first-time-operator entry — sibling
    documentation defect surfaced from the same storybook strawman; same
    Stage 2 surface, different layer).
  - GHI #430 (first-release ceremony undocumented — sibling Stage 8 storybook
    finding; useful comparison for "narrative implies cohesion the graph
    does not deliver" pattern).
  - ADR-0.0.42 (storybook doctrine — the storybook's job is precisely to
    surface this class of gap; this pool ADR is the storybook doing its job).
  - ADR-pool.research-skill-composition — separate skill-composition design
    on the research surface; reference pattern for how a multi-skill
    composition pool ADR is shaped.

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. The Inputs / Outputs contract shape for Intent-stage skills is agreed
   (frontmatter block vs. body-section convention vs. runtime check).
3. A walkthrough of the Intent stage on a real new project — empty directory
   through first ADR — has been performed (the GHI #429 body's prescribed
   verification depth, which was not exhaustively performed at filing).
4. The storybook narrative posture for Stage 2 is chosen: tighten the
   mechanical wiring to match, hedge the narrative to match the wiring, or
   a mixed path.

---

## Verification status at pool entry

GHI #429 prescribed two verification options: (1) the wiring is documented,
or (2) the wiring has seams. The surface-level inspection performed at
filing established option (2) at the **skill SKILL.md / frontmatter / cross-
reference layer**. The deeper "empty directory → first ADR walkthrough"
verification the GHI body proposed was **not** exhaustively performed; that
runtime walkthrough is folded into Promotion Criterion 3 above so it
happens once, in the design conversation, rather than twice (once to file,
once to design).

---

## Notes

- The pattern this pool ADR closes is broader than the Intent stage:
  *narrative skill-chains whose artifact-graph composition is implicit*.
  The Intent stage is the most visible instance because the storybook
  spotlights it; similar audits should run against the Decomposition stage
  (ADR → OBPI) and the Implementation stage (OBPI → pipeline) when this
  ADR is promoted. Out-of-scope here, but worth surfacing.
- Pool ADRs are backlog items — this carries no `semver:` or `kind:`
  frontmatter. Promotion into the active tree (foundation or feature) is
  performed via `gz adr promote`, which rewrites the frontmatter with the
  chosen taxonomy.
