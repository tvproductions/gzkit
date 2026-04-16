---
id: ADR-pool.filesystem-checkpoints
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
inspired_by: nousresearch/hermes-agent checkpoint_manager.py
---

# ADR-pool.filesystem-checkpoints: Per-Operation Filesystem Checkpoints

## Status

Pool

## Date

2026-04-16

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Add transparent per-operation filesystem snapshots via shadow git repos so
that destructive operations (file edits, ledger writes, config changes) can be
rolled back to a known-good state without depending on the main repository's
commit history.

---

## Target Scope

- Implement a checkpoint manager that auto-snapshots tracked paths before mutating operations.
- Use shadow git repos (e.g., `.gzkit/checkpoints/`) — lightweight, requires no external dependencies, leverages git's content-addressable storage for deduplication.
- Auto-checkpoint triggers: before file writes via `gz` commands, before ledger event emission, before config mutation.
- Add `gz checkpoint list` and `gz checkpoint restore <id>` CLI surfaces.
- Checkpoint metadata: timestamp, triggering operation, affected paths, session ID.
- Infrastructure-only — the LLM agent does not see or interact with checkpoints. Rollback is a human-initiated recovery operation.

---

## Non-Goals

- No replacement for git commits — checkpoints are a safety net, not a version control system.
- No pool OBPIs. OBPIs begin only after promotion to a SemVer ADR.
- No cross-session checkpoint persistence — checkpoints are pruned after a configurable retention period.
- No checkpoint diffing UI — `git diff` against the shadow repo is sufficient.

---

## Dependencies

- **Blocks on**: None
- **Blocked by**: None
- **Related**: ADR-pool.change-isolation-workspace (workspace isolation for planning; checkpoints are per-operation rollback points — different lifecycle moment)

---

## Promotion Criteria

This pool ADR can be promoted when all are true:

1. Human assigns a SemVer ADR ID for active implementation.
2. Checkpoint storage location and retention policy are agreed upon.
3. Trigger points (which operations auto-checkpoint) are enumerated.

---

## Inspired By

[NousResearch/hermes-agent](https://github.com/nousresearch/hermes-agent) —
`tools/checkpoint_manager.py` implements transparent filesystem snapshots via
shadow git repos under `~/.hermes/checkpoints/`. Auto-snapshots fire before
every file-mutating tool call (write_file, patch), once per conversation turn.
The LLM never sees the checkpoint tool — it is pure infrastructure. The
pattern provides a safety net that is invisible during normal operation and
available for recovery when needed.

---

## Notes

- Hermes checkpoints once per conversation turn. gzkit should checkpoint per-operation — governance operations are less frequent but higher stakes than general file edits.
- Shadow git repos deduplicate content naturally. A checkpoint of 50 files where only 2 changed stores only the 2 diffs.
- Retention policy matters: unbounded checkpoints bloat `.gzkit/`. A 7-day or 50-checkpoint cap with FIFO eviction is reasonable.
- The checkpoint directory should be gitignored — it is a local safety net, not a shared artifact.
- Consider: should `gz checkpoint restore` emit a ledger event? A rollback is a governance-significant action.
