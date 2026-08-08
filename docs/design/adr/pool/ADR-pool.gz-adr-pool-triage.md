---
id: ADR-pool.gz-adr-pool-triage
status: Pool
lane: lite
parent: PRD-GZKIT-1.0.0
bounded_context: governance-triage
promoted_from: ADR-pool.pool-triage-skill
---

# ADR-pool.gz-adr-pool-triage: gz ADR Pool Triage

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

**Active driver:** `main-session` — see `.gzkit/personas/main-session.md`.

Agents working on this ADR author the `pool-triage` skill as a cognitive+rendering wrapper that composes mechanical CLI surfaces from ADR-0.0.46 and ADR-0.0.47, not as a re-implementation of them. The craftsperson trait demands that the three-step pattern (mechanical pre-pass → agent cognitive pass → deterministic rendering) stay disciplined: skipping the cognitive pass — even when the mechanical signals look conclusive — is the round-3-hardening failure mode named in GHI #424. Structural-only rank input is binding; per-entry prose rationale fields are a vibing leak the skill exists to seal. Renderer determinism (same JSON → same markdown) is a contract, not a guideline; if two runs disagree, the renderer is broken, not the input.

## Why foundation tier?

Without this ADR, pool triage is ad-hoc operator judgment — there's no skill, no rendered surface, no mechanical pass that ranks pool entries by readiness/dependency/staleness for the operator's next promotion choice.

This ADR authors a port: the `gz-adr-pool-triage` ceremony contract every pool-triage invocation honors.

## Intent

Capture design intent for a `pool-triage` skill that answers *"which pool ADR
to promote next?"* the same way `ghi-triage` answers *"which open GHI to
address next?"*. The skill is a cognitive+rendering wrapper that composes
the CLI surfaces specified by `ADR-0.0.46-pool-management` (`gz pool triage`,
`gz pool rank`) and `ADR-0.0.47-pool-dag-promotion-routing` (`gz pool graph
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
following the canonical three-step pattern from `ghi-triage`, with these
binding decisions:

1. Treat `ADR-0.0.46-pool-management` and
   `ADR-0.0.47-pool-dag-promotion-routing` as the only mechanical input
   providers for pool readiness, overlap, rank, and dependency facts.
2. Require an agent cognitive pass over each candidate's Intent and Decision
   sections before producing the structural-only rank input.
3. Keep the renderer deterministic: the same rank-input JSON must produce the
   same markdown deliverable.
4. Surface blocked foundation dependencies explicitly instead of ranking them
   as ready work.
5. Sync the canonical skill and mirrors through the established
   `gz agent sync control-surfaces` path, not by hand-copying skill files.

## Rationale

1. The existing `.gzkit/skills/ghi-triage/SKILL.md` precedent separates
   mechanical pre-pass data from agent judgment and deterministic rendering.
   Pool triage needs the same separation because the pool is too large for
   chat-memory ranking.
2. The interim `src/gzkit/chores/pool-triage/CHORE.md` proves demand for pool
   drift signals, but a chore cannot own an operator-facing promotion
   recommendation workflow.
3. The anti-pattern is "agent reads whichever pool files feel salient and then
   narrates a recommendation." This ADR forces the skill to consume explicit
   pool-management and DAG outputs first, then perform the bounded cognitive
   pass over a known candidate set.
4. Keeping the deliverable deterministic preserves the `ghi-triage` hardening
   lesson from GHI #424: rank order is data, not persuasive prose.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Pool ADR isolation holds — the governed pool-state surface this triage skill composes its ranked recommendation over. | uv run gz validate --pool-adr-isolation | 0 |

## Consequences

### Positive

- Promotion preserves backlog intent as executable ADR scope.
- Checklist items now map 1:1 to generated OBPI briefs immediately.

### Negative

- Promotion fails closed when the pool ADR lacks actionable execution scope.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 6

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.48-01: **triage-prepass-contract** — Define the single mechanical pre-pass record set that composes ready-pool graph output, pool-overlap triage output, GHI occurrence counts, and agent-insights signal counts.
- [ ] OBPI-0.0.48-02: **candidate-cognitive-pass** — Author the skill's read-each-candidate procedure, requiring Intent and Decision review before structural-only rank input is produced; includes port/adapter reclassification check that flags foundation-appropriate pool items.
- [ ] OBPI-0.0.48-03: **deterministic-renderer** — Implement the deterministic markdown renderer for the ranked promotion recommendation deliverable.
- [ ] OBPI-0.0.48-04: **blocked-foundation-filter** — Add the dependency cross-check that filters or annotates candidates blocked by in-flight foundation work.
- [ ] OBPI-0.0.48-05: **skill-surface-sync** — Add the canonical gz ADR pool triage skill, sync mirrors, and expose the operator invocation surface.
- [ ] OBPI-0.0.48-06: **docs-validation-fixtures** — Add docs, examples, fixtures, and validation coverage for full-pool and tag-filtered pool triage runs.

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
- `ghi_occurrence_count` — count of open GHIs whose body or title references
  this pool ADR's ID; higher count signals operator friction with the gap this
  pool item addresses (structured dimension, not LLM ranking prose)
- `insights_signal_count` — count of records in `.gzkit/insights/agent-insights.jsonl`
  whose scope references this pool ADR's design space; higher count signals
  a recurring governance concern that warrants earlier promotion

### Step 2 — Agent cognitive pass

For each candidate ADR (ready + non-stale + non-superseded), read the
Intent + Decision sections. Compose a rank-input JSON document with one
entry per recommended-promotion ADR, in agent-recommended order.

**Structural-only schema** (mirroring `ghi-triage` round-3 hardening per
GHI #424): `{id, severity}` where severity is one of `urgent` /
`next-quarter` / `latent`. No prose, no narrative. The rank list IS the
deliverable.

**Port/adapter reclassification check.** During the cognitive pass, if a
candidate pool ADR's scope matches hexagonal-port characteristics — it
authors an invariant or prerequisite without which downstream features
cannot exist — flag it as `reclassify: foundation` and exclude it from the
promotion-rank list. Reclassified items surface in a separate annotation for
the operator to route via `gz adr promote --kind foundation`.

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

## Non-Goals

- Building the skill before its upstream CLI surfaces exist. OBPI-05 owns the
  standard skill-authoring path (`.gzkit/skills/pool-triage/SKILL.md` +
  canonical/mirror sync via `gz agent sync control-surfaces`) after the
  upstream pool management and pool graph surfaces are available.
- Authoring the underlying CLI surfaces. Those belong to
  `ADR-0.0.46-pool-management` and
  `ADR-0.0.47-pool-dag-promotion-routing`.
- Extending pool ADR frontmatter. The frontmatter schema lives in
  `pool-dag-promotion-routing`; this ADR consumes it.
- Auto-promoting pool ADRs. The skill produces ranked recommendations;
  promotion remains operator-decided per ADR-0.6.0-pool-promotion-protocol.

## Alternatives Considered

### A. Chat-only pool recommendation

Rejected. A chat-only recommendation repeats the failure mode this ADR is meant
to remove: pool priority becomes whatever the current agent remembers or reads
first, not a reproducible pass over governed inputs.

### B. Fold pool triage into `ghi-triage`

Rejected. The cognitive pattern is shared, but GHIs and pool ADRs have different
source facts, blockers, lifecycle terms, and promotion consequences. Reusing the
pattern is correct; merging the skill surfaces would blur two governance queues.

### C. Auto-promote the top-ranked pool ADR

Rejected. Promotion changes active SemVer governance state. The skill may rank
and explain candidates, but ADR-0.6.0 keeps promotion as an operator decision.

## Dependencies

This ADR is **downstream of** two active foundation ADRs. It is promoted now
so the cognitive skill layer has a governed home, but implementation of its
pre-pass and renderer must wait for the underlying pool command surfaces to
land:

- **`ADR-0.0.46-pool-management`** — provides `gz pool triage --overlap
  --json`, `gz pool rank --json`, staleness thresholds, supersession
  protocol, priority-ranking model. The Step 1 mechanical pre-pass
  invokes these CLIs.
- **`ADR-0.0.47-pool-dag-promotion-routing`** — provides `gz pool graph
  --ready --json`, machine-readable `depends_on` / `complements` /
  `blocks` / `tags` frontmatter, DAG query surface. The Step 1
  mechanical pre-pass invokes these CLIs; the cross-check uses the
  `depends_on` field.

**Complements (cognitive pattern mirror):**

- `.gzkit/skills/ghi-triage/SKILL.md` — canonical analog this skill
  mirrors. Same three-step procedure, same round-3 hardening (structural-
  only rank input, chat-silence enforcement).

## Implementation Sequencing Criteria

This ADR is promoted. Its implementation should wait until all are true:

1. Both upstream foundation ADRs (`ADR-0.0.46-pool-management` and
   `ADR-0.0.47-pool-dag-promotion-routing`) have landed the CLI and graph
   surfaces consumed by this skill.
2. `.gzkit/skills/ghi-triage/SKILL.md` is stable and its round-3
   hardening (structural-only rank input, chat-silence enforcement) is
   the canonical pattern.
3. Operator demand signal exists — operator is ready to pull from the
   pool and wants the cognitive-ranking surface.
4. OBPI-05 can sync the canonical skill and mirrors without inventing
   placeholder command contracts.

## Notes

- Routing receipt: this ADR was authored under GHI #452 close. See the
  GHI's close comment for the routing chain.
- The skill's existence does not change pool promotion mechanics
  (ADR-0.6.0) — it changes only the operator-facing recommendation
  surface.
- Multiple pool ADRs may route here in the future: any GHI surfacing
  "we need pool triage cognition" should close `superseded` against this
  ADR.

Lineage note: the originating pool ADR carried no `semver:` or `kind:`
frontmatter. Promotion into this active foundation package was performed via
`gz adr promote`, which rewrote the frontmatter with the chosen taxonomy.

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.pool-triage-skill` on 2026-05-16; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.48 | Pending | | | |
