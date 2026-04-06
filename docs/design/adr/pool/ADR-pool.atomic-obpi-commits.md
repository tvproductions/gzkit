# ADR-pool.atomic-obpi-commits

- **Status:** Pool
- **Lane:** Lite
- **Date:** 2026-04-05
- **Origin:** GSD v1 comparative analysis — atomic commit discipline adaptation

## Intent

Establish a per-OBPI atomic commit discipline where each OBPI completion produces
exactly one commit (or a clean commit sequence) with structured metadata linking
the commit to its OBPI. Currently, `git-sync` batches changes from a session into
a single commit regardless of how many OBPIs were completed. This creates a git
history where OBPI boundaries are invisible — `git bisect` can't isolate which OBPI
introduced a regression, `git log` doesn't show the governance trail, and rollback
granularity is per-session rather than per-work-unit.

## Target Scope

### Commit Convention

Each OBPI completion produces a commit with structured metadata:

- **Message format:**
  ```
  feat(OBPI-X.Y.Z-nn): <brief description>

  ADR: ADR-X.Y.Z
  OBPI: OBPI-X.Y.Z-nn-<slug>
  Lane: <lite|heavy>
  Gate-2: <pass|fail>
  ```
- **Scope:** Only files within the OBPI's allowed paths are included.
  Changes outside allowed paths are a scope violation, flagged before commit.
- **Atomicity:** The commit represents a complete, testable increment. Tests
  pass at this commit. Partial OBPI work is not committed (stays in working tree
  until the OBPI is complete).

### Pipeline Integration

Modify the OBPI pipeline's Stage 5 (Sync) to commit per-OBPI rather than batching:

- After Stage 4 (Present Evidence), if the OBPI is self-closed or attested:
  1. Stage files within the OBPI's allowed paths
  2. Run `gz gates --adr ADR-X.Y.Z` to confirm Gate 2 passes at this commit boundary
  3. Create commit with structured message
  4. If SVFR mode with multiple completed OBPIs, each gets its own commit in sequence
- `git-sync` still handles the push, but operates on a clean series of OBPI commits
  rather than creating a single batch commit.

### Scope Enforcement

Before committing, verify that staged files are within the OBPI's declared allowed paths:

- Files outside allowed paths → warning + prompt for operator decision
  (include with justification, or unstage)
- Files within denied paths → hard block, cannot commit
- Untracked files not in any OBPI's scope → separate "housekeeping" commit
  or held for the next sync

### Commit Log Surface

`gz log --adr ADR-X.Y.Z` shows OBPI-annotated git history:

- Filters commits by ADR/OBPI metadata
- Shows governance state at each commit (which gates passed, which OBPI completed)
- Supports `--since` and `--until` for time-bounded queries
- Machine-readable with `--json`

## Non-Goals

- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No squash-on-merge policy — atomic commits are preserved in the branch. Merge
  strategy is a project-level decision.
- No retroactive commit rewriting — this applies to new OBPIs only.
- No commit signing or verification beyond standard git configuration.
- Does not replace `git-sync` — atomic commits are created locally, sync handles
  remote push with quality gates.

## Dependencies

- **Prerequisite:** OBPI pipeline with Stage 5 (already implemented)
- **Prerequisite:** OBPI brief allowed paths (already standard)
- **Complements:** ADR-pool.svfr-quick-adhoc (quick OBPIs produce atomic commits
  under the maintenance ADR)
- **Complements:** ADR-pool.wave-dependency-execution (each wave's parallel OBPIs
  commit independently, creating a clean commit sequence per wave)

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Commit message format and metadata fields are accepted.
3. Scope enforcement behavior is defined — what happens when files outside
   allowed paths are modified? Warning vs. block vs. separate commit?
4. Interaction with `git-sync` skill is designed — sync must not re-batch
   what the pipeline already committed atomically.
5. Tested against at least 3 real SVFR sessions with multiple OBPIs to confirm
   the commit sequence is clean and `git bisect`-friendly.

## Inspired By

- [GSD](https://github.com/gsd-build/get-shit-done) atomic commits — every task in a plan gets its own commit, creating a clean git history where each commit maps to one plan item. Implementation history is preserved for debugging and rollback.
- [Conventional Commits](https://www.conventionalcommits.org/) — structured commit
  messages with type, scope, and metadata. gzkit extends this with OBPI and ADR
  traceability.

## Notes

- The primary tension: atomic commits per OBPI vs. the current `git-sync` batch
  model. Some operators prefer clean, squashed history. This ADR makes per-OBPI
  commits the default but doesn't prohibit squash-on-merge at the project level.
- Consider: `gz commit --obpi OBPI-X.Y.Z-nn` as an explicit command for operators
  who want to commit mid-OBPI (e.g., at a natural checkpoint). The pipeline's
  auto-commit happens at OBPI completion.
- Risk: if allowed path enforcement is too strict, legitimate cross-cutting changes
  (updating a shared import, fixing a test helper) get blocked. The "housekeeping
  commit" escape valve addresses this.
- This pool ADR has the lowest complexity of the GSD-inspired set — it's primarily
  a convention change to the sync pipeline, not a new system.
