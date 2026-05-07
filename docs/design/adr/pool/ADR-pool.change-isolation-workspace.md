---
id: ADR-pool.change-isolation-workspace
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: openspec, openai/symphony
amendments:
  - 2026-05-02 — added § Amendment 2026-05-02 (per-OBPI git-worktree isolation)
---

# ADR-pool.change-isolation-workspace: Filesystem Change Isolation

## Status

Pool

## Date

2026-03-08 (original) / 2026-05-02 (worktree amendment — see Amendment History)

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Adopt OpenSpec's change isolation pattern: `gz plan` creates a `changes/<adr-slug>/`
workspace containing the ADR, tasks, and scratchpad. On `gz closeout`, the ADR merges
into the canonical `docs/design/adr/` tree. This physically separates in-flight work
from completed decisions, reducing context confusion for both humans and AI agents.

---

## Target Scope

- `gz plan` creates `changes/<slug>/` with ADR, tasks, and a scratchpad.md
- `gz closeout` moves the ADR from changes/ to canonical docs/design/adr/
- Ledger records workspace creation and merge events
- Existing ADR workflow remains functional (changes/ is additive, not mandatory)

---

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No changes to the existing pool/ or canonical ADR directory structures.
- No mandatory adoption — changes/ is opt-in alongside existing direct creation.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Workspace lifecycle (create → merge) is accepted.
3. Backward compatibility with existing ADR creation is confirmed.

---

## Inspired By

[OpenSpec](https://github.com/Fission-AI/OpenSpec) — `changes/` directory pattern
for isolating pending modifications from current system state.

---

## Notes

- OpenSpec's killer feature — prevents AI context drift by physical separation
- Must preserve backward compatibility: existing pool/ ADRs and direct creation still work
- Consider: should `changes/` be gitignored or committed? (Committed — it's documentation)

---

## Amendment 2026-05-02: Per-OBPI git-worktree isolation

The original scope isolates *documents* (ADR / tasks / scratchpad) under
`changes/<adr-slug>/`. The `openai/symphony` SPEC.md (released 2026-04-23,
[github.com/openai/symphony](https://github.com/openai/symphony)) supplies
the missing axis: isolate the *code workspace* per implementation unit, not
just the design artifacts. Each open issue in Symphony maps to a per-issue
filesystem directory under a configurable workspace root, with prefix-checked
`cwd`, sanitized workspace key, and lifecycle hooks.

The gzkit appropriation is **per-OBPI git worktrees**, not Symphony's plain
filesystem dirs — gzkit already has [`atomic-obpi-commits`](ADR-pool.atomic-obpi-commits.md)
proposing per-OBPI commit boundaries on the active branch, and worktrees are
the strict superset (per-OBPI branch isolation + per-OBPI commit boundary +
filesystem `cwd` separation in one mechanism). Worktrees are also stdlib-first
relative to alternatives — git is already a hard dependency, no new tool is
adopted.

### Extended Target Scope

In addition to the original document-isolation scope:

- **Worktree spawn on OBPI lock claim.** When `gz-obpi-lock` claims an OBPI,
  the runtime spawns `worktrees/OBPI-X.Y.Z-NN/` via `git worktree add` on a
  branch named `obpi/<OBPI-ID>` rooted at the lock-claim commit. The
  `obpi_lock_claimed` ledger event records the worktree path and base SHA.
- **Sanitized worktree key.** OBPI ID is the worktree key; only
  `[A-Za-z0-9._-]` permitted; other chars rejected, not silently rewritten
  (gzkit is fail-closed where Symphony is permissive). Path validated as a
  prefix of the configured worktree root.
- **`gz-obpi-pipeline` runs in the worktree `cwd`.** Stages 1-4 (implement,
  verify, present evidence, attest) execute with `cwd` = worktree path. The
  runtime asserts the prefix invariant before each stage; out-of-prefix
  writes are a fail-closed pipeline error, not a warning.
- **Stage 5 sync = `gz git-sync` flushes worktree → main, then prunes.**
  The existing `gz git-sync --apply --lint --test` pipeline becomes the
  worktree-merge surface. Atomic-commit metadata from
  [`atomic-obpi-commits`](ADR-pool.atomic-obpi-commits.md) is produced inside
  the worktree; the merge to main carries the structured trailer through.
- **Worktree pruning on lock release.** `obpi_lock_released` triggers
  `git worktree remove`; the branch persists for audit replay until a
  configurable retention horizon, then is pruned by the same Stage-5 ceremony.
- **Allowed-Paths becomes a fail-closed filesystem invariant, not a brief
  rule.** Symphony's prefix check is the model: a write outside the brief's
  Allowed Paths is impossible because the worktree is the prefix. The
  honor-system reading of Allowed Paths is retired in favor of the structural
  invariant.

### Coupled-surface coherence

- **[`atomic-obpi-commits`](ADR-pool.atomic-obpi-commits.md)** — stacked
  enabler. Worktree gives the per-OBPI branch; atomic-obpi-commits gives the
  per-OBPI commit shape inside it. Promote together or sequence
  worktree-first.
- **[`obpi-state-machine`](ADR-pool.obpi-state-machine.md)** — the
  `obpi_lock_claimed` / `obpi_lock_released` events become the canonical
  transitions that emit worktree spawn/prune as postconditions.
- **[`sandboxed-delegation`](ADR-pool.sandboxed-delegation.md)** — its
  explicit non-goal *"No container-level isolation — gzkit subagents run in
  the same filesystem"* still holds. Worktrees are filesystem-separated
  paths inside the same mount, not container/VM isolation.
- **[`filesystem-checkpoints`](ADR-pool.filesystem-checkpoints.md)** —
  orthogonal. Checkpoints are per-operation rollback safety net; worktrees
  are per-OBPI scope-fence. Both can coexist.
- **[`pause-resume-handoff-runtime`](ADR-pool.pause-resume-handoff-runtime.md)** —
  worktree path becomes a first-class field in the handoff schema; resume
  re-attaches to the existing worktree rather than re-deriving working set
  from commits-since-handoff.

### Non-Goals (extended)

- No container or VM isolation (deferred to
  [`controlled-agency-recovery`](ADR-pool.controlled-agency-recovery.md)).
- No per-OBPI virtual environment — the parent project's `uv`-managed venv
  is shared across worktrees (consistent with [`sandboxed-delegation`](ADR-pool.sandboxed-delegation.md)
  same-filesystem posture).
- No mid-pipeline worktree relocation — the worktree path is fixed at
  lock-claim time and immutable until lock-release. Hot-relocation is the
  Symphony hot-reload pattern gzkit deliberately rejects (doctrine drift =
  invariant drift, `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT operative
  claim 3).

### Distinct from Symphony

- **Worktree, not plain dir.** Gives branch isolation + replay-able audit
  trail for free.
- **Fail-closed, not permissive.** Symphony silently rewrites invalid
  workspace keys with `_`; gzkit rejects them. Anti-vibing posture.
- **Single shared venv, not per-workspace process tree.** Symphony spawns
  `codex app-server` per workspace; gzkit's runtime is one Python process
  navigating worktrees as `cwd`.
- **No hot reload of WORKFLOW.md analog.** Symphony reloads `WORKFLOW.md`
  live; gzkit's `.gzkit/manifest.json` + `.claude/rules/` are deliberately
  pinned for the duration of the pipeline run.

### Inspired By (extended)

[openai/symphony SPEC.md](https://github.com/openai/symphony/blob/main/SPEC.md)
§ Workspace Manager and § Agent Runner — per-issue workspace as a first-class
isolation primitive. Apache-2.0; reference-implementation posture, not a
maintained product.

---

## Amendment 2026-05-07: Operator-first spec workspace

Spec Kit, Kiro, and betterspec-style tools are strongest at the front door:
they let the operator begin with an intent packet and get a visible
spec/plan/tasks workspace quickly. gzkit should absorb that strength here, not
by reducing ceremony, but by making the workspace the first witnessed object in
the governance chain.

### Additional target scope

- `gz plan workspace <slug>` creates a change workspace with `intent.md`,
  `spec.md`, `plan.md`, `tasks.md`, and `witness.json`.
- `witness.json` records the source prompt hash, operator-confirmed scope,
  generated artifact paths, and the target destination (`pool`, `foundation`,
  or `feature`) once chosen.
- Promotion from the workspace into ADR/OBPI artifacts requires
  `gz workflow validate` once `ADR-pool.workflow-specification` lands; until
  then, the workspace carries an explicit manual checklist proving spec, plan,
  and tasks are in sync.
- The workspace is additive. It does not replace ADR promotion, OBPI briefs,
  ledger events, receipts, or Gate 5.

### Identity-preserving rule

A workspace that improves operator ergonomics but lacks `witness.json` is not a
gzkit workspace. It is a scratch folder and cannot be promoted.
