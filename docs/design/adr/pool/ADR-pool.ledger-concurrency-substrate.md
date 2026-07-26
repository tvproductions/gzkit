---
id: ADR-pool.ledger-concurrency-substrate
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: unclebob/swarm-forge handoffd single-writer coordination
---

# ADR-pool.ledger-concurrency-substrate: Ledger Concurrency Substrate (Single-Writer-by-Construction)

## Status

Pool

## Date

2026-07-26

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

gzkit cannot safely run more than one agent at a time against the same
repository because the system-of-record is not concurrency-safe.
`.gzkit/ledger.jsonl` is an append-only file written on the single-writer
assumption, and the OBPI-lock system (`.gzkit/locks/`) is advisory. Two agents
working concurrently — e.g. two worktrees both reaching `gz obpi complete` —
would interleave writes to Layer-2, corrupting the append-only invariant the
whole trust model rests on.

This pool ADR captures the enabling invariant that any write-heavy multi-agent
parallelism (see [ADR-pool.worktree-parallel-agents](ADR-pool.worktree-parallel-agents.md))
must sit on. It is deliberately the **substrate, not the feature**: it makes
concurrent Layer-2 mutation impossible-by-construction rather than merely
coordinated.

---

## Decision

Adopt **single-writer-by-construction** for the ledger, with **no resident
daemon**.

1. Parallel/worktree agents write **zero** Layer-2 ledger events during their
   parallel phase. Their output is code, findings, and worktree-local artifacts
   only.
2. The only surface that appends to `.gzkit/ledger.jsonl` is the **serialized
   merge-to-main step**. Concurrency is resolved by construction: there is
   exactly one writer because there is exactly one merge lane (`main`).
3. This is not a new invariant — it makes an existing architectural boundary
   load-bearing. AGENTS.md § Architectural Boundaries #6 and
   `docs/governance/state-doctrine.md` already hold that derived views are
   Layer-3 and that Layer-2 facts originate from governed writes. Here we add:
   parallel work is Layer-3 scratch until it merges; only the merge writes
   Layer-2.
4. **No `handoffd`-style daemon.** swarm-forge needs a daemon because tmux is a
   shared live socket every agent must reach concurrently; gzkit's ledger is a
   file whose writes can be funnelled through a single logical lane (merge)
   without a resident process. Choosing the daemon would incur a STDLIB-FIRST
   cost (a long-lived process, its lifecycle, its failure modes) to solve a
   problem the merge-lane funnel already solves.

---

## Alternatives Considered

1. **Daemon-owned ledger writer** (direct swarm-forge `handoffd` analog): a
   single long-lived process owns `.gzkit/ledger.jsonl`; parallel agents enqueue
   events it serializes. **Rejected as the pool default** — most faithful to
   swarm-forge, but adds a resident process and its lifecycle/failure surface: a
   STDLIB-FIRST departure that would need foundation attestation, and the
   merge-lane funnel already achieves serialization without it. Kept on record
   as the fallback **if** a future mode genuinely needs mid-flight Layer-2
   writes.
2. **Advisory worktree-scoped locks only**: extend the existing OBPI-lock system
   to worktree scope and rely on cooperation. **Rejected** — cheapest, but locks
   remain advisory; it leaves exactly the race window this ADR exists to close.
3. **External transactional store (SQLite/Dolt) for the ledger**: **Rejected**
   as over-reach and a direct contradiction of the append-only-JSONL
   system-of-record and the
   [ADR-pool.storage-simplicity-profile](ADR-pool.storage-simplicity-profile.md)
   posture.

---

## Dependencies

- **Blocks on**: None.
- **Blocked by**: None.
- **Enables**: [ADR-pool.worktree-parallel-agents](ADR-pool.worktree-parallel-agents.md)
  — specifically its **write-heavy** modes (parallel OBPI implementation,
  parallel GHI fixes, parallel ADR pipelines). That ADR's **read-only** review
  fan-out mode does NOT depend on this substrate (reviewers emit no Layer-2
  events).

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. A human assigns a SemVer ADR ID for active implementation.
2. The merge-lane accounting transaction is designed: how deferred Layer-2
   events for merged work are emitted atomically at merge time, and what happens
   when that emission fails partway (all-or-nothing; leave the worktree for
   retry).
3. The disposition of the advisory OBPI-lock system is decided in light of the
   by-construction guarantee (retire / keep as courtesy signal / upgrade to
   worktree-scoped).

---

## Inspired By

[unclebob/swarm-forge](https://github.com/unclebob/swarm-forge) — Robert C.
Martin. swarm-forge's handoff daemon (`handoffd`) owns the single shared mutable
surface (the tmux socket); agents never touch it directly — they enqueue
validated requests the daemon serializes. That is the load-bearing idea borrowed
here — **one writer for the shared mutable state** — but gzkit reaches it by a
different mechanism (the merge-to-main funnel) because its shared surface is a
file, not a live socket, so no resident process is required. Ideas only;
swarm-forge ships no license. The daemon design itself is recorded above as the
rejected alternative and the named fallback.

[obra/superpowers](https://github.com/obra/superpowers) — Jesse Vincent (MIT).
Its worktree-per-agent model is what surfaces the ledger-concurrency question in
the first place: the moment parallel agents become possible, the shared
append-only ledger becomes the contended surface this ADR protects.

---

## Notes

- The honest coupling: the primary motivating use case for parallelism
  (read-only review personas) does **not** need this substrate at all. This ADR
  is the prerequisite for the *write-heavy* modes only. It is separated from the
  capability ADR precisely so the cheap read-only capability can land first and
  this can be promoted independently when a write-heavy mode is actually pulled.
- The new implicit rule this introduces ("parallel work is Layer-3 until merge")
  must be taught **and** mechanically gated — a fail-closed validator that
  refuses a Layer-2 event emitted from a worktree/parallel context outside the
  merge lane — or it silently decays (the staging-flag anti-pattern).
- Observability cost to weigh at promotion: parallel agents cannot emit
  progress/telemetry to the shared ledger mid-flight; their governance footprint
  is invisible until merge. If long parallel runs need mid-flight visibility, the
  rejected daemon alternative reopens.
- Interview artifact: `ledger-concurrency-substrate-interview.json` (this
  directory) records the Step-0 forcing functions.

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
