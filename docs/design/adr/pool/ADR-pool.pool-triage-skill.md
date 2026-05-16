---
id: ADR-pool.pool-triage-skill
status: Superseded
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
promoted_to: ADR-0.0.48-gz-adr-pool-triage
---

# ADR-pool.pool-triage-skill: Pool Triage Skill — Cognitive Wrapper for Pool Promotion Recommendation
> Promoted to `ADR-0.0.48-gz-adr-pool-triage` on 2026-05-16. This pool file is retained as historical intake context.


## Status

Superseded

## Date

2026-05-11 (authored via routing-receipt close of GHI #452)

## Intent

Capture design intent for a `pool-triage` skill that answers *"which pool ADR
to promote next?"* the same way `ghi-triage` answers *"which open GHI to
address next?"*. The skill is a cognitive+rendering wrapper that composes
the CLI surfaces proposed in `ADR-pool.pool-management` (`gz pool triage`,
`gz pool rank`) and `ADR-pool.pool-dag-promotion-routing` (`gz pool graph
--ready`, `--path`, `--tags`) with the read-each-body cognitive pass and
deterministic markdown deliverable pattern hardened in `ghi-triage`'s
round-3 work (GHI #424 — structural-only rank input, chat-silence
enforcement).

**Motivation.** The pool currently contains 75+ pool ADRs. When the operator
finishes the current foundation + feature backlog and is ready to pull from
the pool, the question "which pool ADR to promote next?" is unanswered
today. There is no triage mechanism analogous to `ghi-triage` for pool
ADRs. The two upstream pool ADRs author the underlying CLI surfaces; this
ADR captures the *skill layer* — the cognitive pattern that wraps the CLI
output into an operator-facing ranked deliverable.

Per operator framing (2026-05-11): *"the pool is so large now, that we
almost need pool triage in the same way we have the ghi-triage skill now
[...] I am currently trying to get foundation ADRs complete. but a pool
triage should ultimately be 'which to do next?'"*

## Decision

Author a `pool-triage` skill in `.gzkit/skills/pool-triage/SKILL.md`
following the canonical three-step pattern from `ghi-triage`:

## Proposed OBPI Decomposition

| # | Slug | Description | Lane |
|---|------|-------------|------|
| 01 | triage-prepass-contract | Define the single mechanical pre-pass record set that composes ready-pool graph output and pool-overlap triage output. | Heavy |
| 02 | candidate-cognitive-pass | Author the skill's read-each-candidate procedure, requiring Intent and Decision review before structural-only rank input is produced. | Heavy |
| 03 | deterministic-renderer | Implement the deterministic markdown renderer for the ranked promotion recommendation deliverable. | Heavy |
| 04 | blocked-foundation-filter | Add the dependency cross-check that filters or annotates candidates blocked by in-flight foundation work. | Heavy |
| 05 | skill-surface-sync | Add the canonical gz ADR pool triage skill, sync mirrors, and expose the operator invocation surface. | Heavy |
| 06 | docs-validation-fixtures | Add docs, examples, fixtures, and validation coverage for full-pool and tag-filtered pool triage runs. | Heavy |

## Target Scope

- **triage-prepass-contract** — Define the single mechanical pre-pass record set that composes ready-pool graph output and pool-overlap triage output.
- **candidate-cognitive-pass** — Author the skill's read-each-candidate procedure, requiring Intent and Decision review before structural-only rank input is produced.
- **deterministic-renderer** — Implement the deterministic markdown renderer for the ranked promotion recommendation deliverable.
- **blocked-foundation-filter** — Add the dependency cross-check that filters or annotates candidates blocked by in-flight foundation work.
- **skill-surface-sync** — Add the canonical gz ADR pool triage skill, sync mirrors, and expose the operator invocation surface.
- **docs-validation-fixtures** — Add docs, examples, fixtures, and validation coverage for full-pool and tag-filtered pool triage runs.

### Step 1 — Mechanical pre-pass (single CLI call)

Compose `gz pool graph --ready --json` (per `pool-dag-promotion-routing`)
with `gz pool triage --overlap --json` (per `pool-management`) into a
single JSON record set per pool ADR. Per-record fields:

- `id`, `status`, `lane`, `tags`
- `depends_on`, `complements`, `blocks`
- `age_class` — `fresh` (<3mo) / `aging` (3-6mo) / `stale` (>6mo)
- `overlap_cluster_id` (if any)
- `intent_summary`, `decision_summary`

### Step 2 — Agent cognitive pass

For each candidate ADR (ready + non-stale + non-superseded), read the
Intent + Decision sections. Compose a rank-input JSON document with one
entry per recommended-promotion ADR, in agent-recommended order.

**Structural-only schema** (mirroring `ghi-triage` round-3 hardening per
GHI #424): `{id, severity}` where severity is one of `urgent` /
`next-quarter` / `latent`. No prose, no narrative. The rank list IS the
deliverable.

### Step 3 — Deterministic markdown renderer

Pass the rank input to the renderer; produce a chat-renderable markdown
deliverable. Renderer is deterministic — same input always yields same
output. Operator copies the ranked list into the next planning session.

### Optional cross-check

If a candidate ADR's `depends_on` references an in-flight ADR, elevate to
severity `urgent` only if the in-flight ADR is near closeout; otherwise
mark as `blocked-on-foundation` and skip recommendation.

### Invocation surface

- `/pool-triage` — triage the full pool
- `/pool-triage --tags <theme>` — filter to a thematic subset (e.g.
  `velocity`, `vendor-alignment`, `governance`)

### Exclusions from candidate set

- Pool ADRs in `Superseded` or `Archived` status
- Pool ADRs whose `depends_on` includes unsatisfied in-flight foundation
  work (surfaced as `blocked-on-foundation` annotation)

## Alternatives Considered

### A. Extend `ghi-triage` to cover both GHIs and pool ADRs

**Rejected.** Different artifact shapes (open GHIs vs. pool ADRs), different
candidate-set rules (severity classification vs. promotion readiness),
different rendering conventions (issue numbers vs. ADR slugs). Conflating
them into one skill would force both surfaces to compromise. Better to
mirror the pattern in a sibling skill.

### B. Skip the skill; rely on raw `gz pool rank` / `gz pool graph --ready`
CLI output

**Rejected.** Raw CLI output answers "which are ready?" — not "which is
most worth promoting next?" The cognitive pass (reading Intent + Decision,
weighing against current roadmap, surfacing blocked-on-foundation
annotations) is exactly the value `ghi-triage` adds over `gh issue list`.
The same logic applies here.

### C. Author the `pool-triage` chore (already proposed in
`pool-management` § 8) and treat that as sufficient

**Rejected for the skill scope.** The chore (per `pool-management` § 8) is
a read-only drift-detection surface — it surfaces stale, unarchived-
superseded, newly-unblocked, duplicate-scope signals. It is *not* a
ranked-promotion-recommendation surface. The skill consumes the chore's
output (plus the CLI surfaces) but adds the cognitive ranking layer the
chore explicitly defers. The chore and skill are complementary, not
substitutable.

### D. Wait for pool-management + pool-dag-promotion-routing to promote
before authoring this design intent

**Rejected.** The skill design is upstream-bounded but downstream-distinct.
Authoring the skill design intent now captures the cognitive-pattern
mirror to `ghi-triage` while it's fresh; promotion of the two upstream
pool ADRs writes the underlying CLI; this skill design then has a
homed destination when the operator is ready to build. Deferring the
design intent risks losing the routing receipt for GHI #452.

## Dependencies

This pool ADR is **downstream of** two existing pool ADRs and cannot be
promoted into active work until both have promoted:

- **`ADR-pool.pool-management`** — provides `gz pool triage --overlap
  --json`, `gz pool rank --json`, staleness thresholds, supersession
  protocol, priority-ranking model. The Step 1 mechanical pre-pass
  invokes these CLIs.
- **`ADR-pool.pool-dag-promotion-routing`** — provides `gz pool graph
  --ready --json`, machine-readable `depends_on` / `complements` /
  `blocks` / `tags` frontmatter, DAG query surface. The Step 1
  mechanical pre-pass invokes these CLIs; the cross-check uses the
  `depends_on` field.

**Complements (cognitive pattern mirror):**

- `.gzkit/skills/ghi-triage/SKILL.md` — canonical analog this skill
  mirrors. Same three-step procedure, same round-3 hardening (structural-
  only rank input, chat-silence enforcement).

## Non-Goals

- Implementing the skill in this ADR. This ADR is design intent only;
  implementation runs through standard skill-authoring path (`.gzkit/
  skills/pool-triage/SKILL.md` + canonical/mirror sync via `gz agent sync
  control-surfaces`) once the two upstream pool ADRs promote.
- Authoring the underlying CLI surfaces. Those belong to
  `ADR-pool.pool-management` and `ADR-pool.pool-dag-promotion-routing`.
- Extending pool ADR frontmatter. The frontmatter schema lives in
  `pool-dag-promotion-routing`; this ADR consumes it.
- Auto-promoting pool ADRs. The skill produces ranked recommendations;
  promotion remains operator-decided per ADR-0.6.0-pool-promotion-protocol.

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Both upstream pool ADRs (`pool-management`, `pool-dag-promotion-
   routing`) have promoted and their CLI surfaces are landed.
2. `.gzkit/skills/ghi-triage/SKILL.md` is stable and its round-3
   hardening (structural-only rank input, chat-silence enforcement) is
   the canonical pattern.
3. Operator demand signal exists — operator is ready to pull from the
   pool and wants the cognitive-ranking surface.
4. A SemVer ADR ID is assigned for active implementation.

## Notes

- Routing receipt: this ADR was authored under GHI #452 close. See the
  GHI's close comment for the routing chain.
- The skill's existence does not change pool promotion mechanics
  (ADR-0.6.0) — it changes only the operator-facing recommendation
  surface.
- Multiple pool ADRs may route here in the future: any GHI surfacing
  "we need pool triage cognition" should close `superseded` against this
  ADR.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
