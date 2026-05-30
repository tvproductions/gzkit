# OBPI-0.0.65-01: canonical-location-migration

## Context

ADR-0.0.65 canonizes `.gzkit/handoffs/` as the single handoff write location
(per ADR-0.0.41 / OBPI-0.0.41-03). This OBPI migrates the 24 legacy per-ADR
session handoffs under `docs/design/adr/**/handoffs/` (10 ADR packages) into the
canonical store, preserving `continues_from:` chain integrity and frontmatter
timestamps, then removes the now-empty source directories.

The skill-canon amendment (`gz-session-handoff/SKILL.md` output-path doctrine)
already landed as a direct fix in commit `e060cdb2` this session, so SKILL.md is
in Denied Paths; REQs touching it are non-regression assertions.

## Destination-in-mind (Step 6a disclosure)

The approach was fixed at brief-authoring time (recorded in the 2026-05-30
handoff Decisions): use `git mv` for relocations to preserve rename detection,
with a Python helper for `continues_from:` frontmatter rewriting. This plan
documents that already-decided approach; the implementation was executed against
it in this session. Not a post-hoc reconstruction of an open design space — the
design space was closed by the operator's Route-A decision and the handoff's
git-mv-plus-Python-helper decision.

## Rejected alternatives

- **Pure-Python `shutil.move`** — rejected: loses git rename detection across 24
  files (dirtier blame chain).
- **Pure-shell `find | xargs git mv`** — rejected: `continues_from:` chain-pointer
  rewriting still needs Python YAML handling anyway.
- **Inline migration in the test module** — rejected in favor of a reusable
  `scripts/migrate_handoffs.py` (idempotent, re-runnable) per REQ #6.
- **Migrate the byte-identical ADR-0.28.0 duplicate as a 24th file** — rejected by
  operator decision (2026-05-30): it is `git rm`'d as a dedup; canonical total is
  34, not 35.

## Files to modify

| File | Action | Detail |
|------|--------|--------|
| `scripts/migrate_handoffs.py` | CREATE | Reusable, idempotent migration: `git mv` relocations, byte-identical dedup via `git rm`, `continues_from:` rewrite, empty-dir cleanup. Fail-closed on differing-content name collision (REQ #9 STOP-on-BLOCKERS). |
| `docs/design/adr/**/handoffs/*.md` (24 files) | MOVE/DELETE | 23 `git mv` into `.gzkit/handoffs/`; 1 byte-identical dup `git rm`. |
| `.gzkit/handoffs/*.md` | EDIT | Rewrite `continues_from:` pointers that referenced the per-ADR tree (10 files). |
| `tests/governance/test_handoff_migration.py` | CREATE | `@covers` tests for REQ-01-01..04 (BEHAVIOR); assertions derive from REQ semantics. |
| `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/obpis/OBPI-0.0.65-01-canonical-location-migration.md` | EDIT | Record dedup decision; correct expected count 35 → 34. |

## Steps

1. Author `scripts/migrate_handoffs.py`; verify with `--dry-run`.
2. Author `tests/governance/test_handoff_migration.py`; observe RED.
3. Amend the brief: 35 → 34 + dedup rationale.
4. Run the migration; observe 23 moved / 1 deduped / 10 rewritten / 9 dirs removed.
5. Run the test suite; observe GREEN (4 pass).
6. SUPPORT proof channel (REQ-01-05): `uv run gz agent sync control-surfaces`
   (emits `agent_sync_completed`) + `uv run gz validate --surfaces` (structural validator).
7. Hand off to `gz obpi pipeline --from verify` for runtime-owned verify → ceremony
   → git-sync → completion. Gate 5 human attestation (heavy/foundation) is the operator's.

## Verification

- `uv run gz validate --documents`
- `uv run gz lint`
- `uv run gz typecheck`
- `uv run -m unittest tests.governance.test_handoff_migration`
- `uv run gz agent sync control-surfaces`
- `uv run gz validate --surfaces`

## Notes

- Scope collision (advisory) with OBPI-0.0.42-04 on the shared tree
  `docs/design/adr/foundation/*/handoffs/`: disjoint at file level (OBPI-0.0.42-04
  creates `STORY.md` stubs inside ADR packages; this OBPI only touches `handoffs/`
  subdirectories). No real overlap.
- Order dependency: OBPI-0.0.65-04 (orientation single-location scan) cannot run
  until this OBPI empties the per-ADR sources.
