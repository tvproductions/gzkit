---
id: ADR-pool.worktree-parallel-agents
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: unclebob/swarm-forge worktree-per-agent isolation; obra/superpowers using-git-worktrees + dispatching-parallel-agents
---

# ADR-pool.worktree-parallel-agents: Worktree-Isolated Parallel Agents

## Status

Pool

## Date

2026-07-26

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

gzkit runs one agent at a time against the working tree; it has no isolation
substrate for concurrent agent work. Two external tools — swarm-forge (Robert
C. Martin) and superpowers (Jesse Vincent) — both obtain parallel agents
essentially for free by giving each agent its own git worktree. This pool ADR
captures adopting that substrate.

The **primary** motivating use case is deliberately the **safest** one:
**parallel review personas** — run `spec-reviewer`, `quality-reviewer`, and
other review subagents concurrently against one change. That mode is read-only
fan-out (reviewers produce findings, not ledger events), so it needs only
worktree isolation and does **not** depend on
[ADR-pool.ledger-concurrency-substrate](ADR-pool.ledger-concurrency-substrate.md).
Write-heavy modes are recorded as future scope and do depend on that substrate.

---

## Decision

1. Adopt **ephemeral git worktrees** as the isolation substrate: scratch
   checkouts (e.g. under `.worktrees/<slug>`), each with its own clean baseline,
   **never pushed as a remote branch**, landing on `main` via fast-forward/squash
   at merge.
2. This preserves the intent of the standing operator directive *"Never create
   feature branches — work directly on main"*, which bans the
   PR/squash-merge/delete **branch dance**, not physical scratch checkouts.
   **Promotion of this ADR requires an operator-ratified doctrine carve-out**
   amending that directive to permit ephemeral worktrees explicitly. This is a
   hard governance gate, not a technical one.
3. **Primary mode (lands first): parallel read-only review personas.** gzkit
   already owns the review topology — `spec-reviewer` + `quality-reviewer`
   subagents, the same two-stage "spec compliance then code quality" shape
   superpowers ships. Only the worktree substrate that lets them run
   concurrently against clean, identical baselines is new.
4. **Write-heavy modes (deferred, dependent):** parallel OBPI implementation
   under one ADR; parallel independent GHI fixes; parallel ADR pipelines. Each
   depends on
   [ADR-pool.ledger-concurrency-substrate](ADR-pool.ledger-concurrency-substrate.md)
   (single-writer-by-construction) to keep Layer-2 consistent.
5. Worktrees are **Layer-3 scratch**: nothing in a worktree is source-of-truth
   until it merges to `main` (`docs/governance/state-doctrine.md`).

---

## Alternatives Considered

1. **Separate full clones per agent** instead of worktrees: **Rejected** —
   heavier (a full clone per agent), and merging back across clones is more
   complex than a worktree fast-forward. Worktrees share one object store.
2. **Single shared working tree with advisory locks / turn-taking**:
   **Rejected** — that is the status quo (no real parallelism) plus a race; it
   is exactly what worktree isolation removes.
3. **Decline worktrees; borrow only the coordination-substrate ideas**:
   **Rejected** as the *capability* ADR (that path is the substrate ADR,
   [ADR-pool.ledger-concurrency-substrate](ADR-pool.ledger-concurrency-substrate.md)).
   Recorded because the operator noted parallelism itself is not the main draw —
   but the read-only review fan-out is cheap enough (needs no substrate work) to
   be worth adopting.

---

## Dependencies

- **Blocks on**:
  [ADR-pool.ledger-concurrency-substrate](ADR-pool.ledger-concurrency-substrate.md)
  — for the **write-heavy** modes only (parallel OBPI implementation, parallel
  GHI fixes, parallel ADR pipelines).
- **Blocked by**: an operator-ratified doctrine carve-out permitting ephemeral
  worktrees (amends *"Never create feature branches — work directly on main"*).
  Blocks **promotion**, not authoring.
- **Read-only review-persona mode is exempt** from the substrate dependency —
  reviewers emit no Layer-2 events, so it can land first.

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. A human assigns a SemVer ADR ID for active implementation.
2. The doctrine carve-out permitting ephemeral worktrees is authored and
   operator-ratified.
3. The worktree lifecycle is specified: create from a pinned commit, verify a
   clean test baseline, tear down on completion, and reap orphaned worktrees
   left by a crashed agent.
4. For the read-only review mode specifically: a mechanism to pin all reviewers
   to the **same** commit (divergent trees produce non-comparable findings).

---

## Inspired By

[unclebob/swarm-forge](https://github.com/unclebob/swarm-forge) — Robert C.
Martin. Each swarm-forge agent works in its own git worktree under
`.worktrees/<role>`, sidestepping merge conflicts by construction while keeping
one repository. That worktree-per-agent isolation is the substrate borrowed
here. Ideas only; swarm-forge ships no license.

[obra/superpowers](https://github.com/obra/superpowers) — Jesse Vincent (MIT).
Its `using-git-worktrees` skill activates **after design approval** and "creates
an isolated workspace on a new branch, runs project setup, verifies a clean test
baseline"; `dispatching-parallel-agents` runs concurrent workflows; and its
`subagent-driven-development` uses a two-stage review (spec compliance, then code
quality). gzkit already mirrors that review topology via its `spec-reviewer` and
`quality-reviewer` subagents — so what is genuinely new to gzkit is only the
worktree substrate, not the review methodology.

---

## Notes

- The honest coupling with the substrate ADR: the **primary** (read-only review)
  mode barely needs the substrate — reviewers write nothing to Layer-2. The
  substrate unblocks the **write-heavy** modes. The two ADRs are separated so the
  cheap read-only capability can land first and each can promote independently.
- The doctrine carve-out is the load-bearing risk, not the code. Adopting
  ephemeral worktrees without ratifying the carve-out first risks a
  `.worktrees/<slug>` being pushed as a remote branch during git-sync —
  reintroducing the exact branch dance the operator banned. The merge path must
  be push-to-`main`-only, never a branch publish.
- gzkit already has the review subagents (`spec-reviewer`, `quality-reviewer`,
  `narrator`, `quality-reviewer`) and a subagent dispatch model; this ADR adds
  concurrency + isolation, not new agent roles.
- Interview artifact: `worktree-parallel-agents-interview.json` (this directory)
  records the Step-0 forcing functions.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
