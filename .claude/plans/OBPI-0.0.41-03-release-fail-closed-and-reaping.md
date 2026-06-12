# Plan — OBPI-0.0.41-03-release-fail-closed-and-reaping

OBPI: `OBPI-0.0.41-03-release-fail-closed-and-reaping`
Parent ADR: `ADR-0.0.41-token-block-lock-discipline` (foundation, heavy)

## Destination-in-mind (plan-audit Step 6a disclosure)

Before writing this plan I had already concluded the implementation shape from
reading the brief + OBPI-02 surfaces: flip the existing warning branch in
`obpi_lock_release_cmd` to `sys.exit(3)`, and rewrite `reap_expired_locks` to
write-handoff → emit-event → unlink with fail-closed ordering, threading a
`Ledger` + reaper-agent through its signature. The approach is dictated by the
brief's Allowed Paths and the OBPI-02 primitives already on disk
(`write_degenerate_handoff`, `obpi_lock_released_event`, the `reaping` abandon
category).

## Rejected alternatives

1. **Extend `write_degenerate_handoff` in `handoff_validation.py` to add the
   reaping fields (`abandoned_by`, `abandoned_at`, `previous_agent`).** Rejected
   — `handoff_validation.py` is NOT in this OBPI's Allowed Paths; the brief fences
   the reaping-handoff writer into `lock_manager.py`. Write the reaping handoff
   inline there.
2. **Keep `reap_expired_locks(project_root)` signature and build the Ledger
   inside it from a hard-coded config path.** Rejected — the caller
   (`obpi_lock_list_cmd`) already resolves config; threading the `Ledger` (and
   reaper agent) as params keeps the function testable and avoids a hidden
   config dependency. Provide a thin default so the one caller stays simple.
3. **Make `handoff_path` mandatory by raising in `obpi_lock_released_event`.**
   Rejected — additive-optional signature stays (OBPI-04's validator enforces
   "every release event carries handoff_path" at the ledger level). OBPI-03's job
   is to make every *emission site* pass it, not to break the event constructor.

## Files (all within brief Allowed Paths)

- `src/gzkit/commands/obpi_lock.py` — flip warning branch to exit 3 (REQ-01).
- `src/gzkit/lock_manager.py` — rewrite `reap_expired_locks` (REQ-02/03/04); add
  reaping-handoff writer + ledger emission + fail-closed ordering. Thread Ledger
  + reaper agent. Update the single caller at `obpi_lock.py:290`.
- `docs/user/manpages/obpi-lock-release.md` — exit-3 row + Reaping subsection (REQ-06).
- `docs/user/manpages/obpi-lock-list.md` — note ledger emission on reaping (REQ-06).
- `tests/test_obpi_lock_cmd.py` — release fail-closed test (REQ-01).
- `tests/test_lock_manager.py` — reap writes handoff / emits event / handoff_path (REQ-02/03).
- `tests/governance/test_token_block_discipline.py` — reap fail-closed on write error (REQ-04); no ADR-package handoff writes (REQ-05).

## Steps (TDD: RED before GREEN)

1. **REQ-01 fail-closed release.** RED: `test_release_fail_closed_without_handoff_or_abandon`
   asserts exit 3 + stderr names `gz-session-handoff` skill AND `--abandon`. GREEN:
   replace the `missing_handoff_warning` print+continue with `sys.exit(3)` after a
   `[red]` stderr message; preserve `--abandon` happy path + found-handoff path.
2. **REQ-02/03 reaping symmetry.** RED: `test_reap_writes_abandoned_by_reaper_handoff`
   (frontmatter `abandoned: true`, `category: reaping`, `abandoned_by`, `abandoned_at`,
   `previous_agent`, min-info fields) + `test_reap_emits_ledger_event_with_handoff_path`.
   GREEN: rewrite `reap_expired_locks(project_root, *, ledger=None, reaper_agent=None)`:
   for each expired lock → write reaping handoff under `.gzkit/handoffs/` → emit
   `obpi_lock_released_event(handoff_path=...)` → then `unlink()`. Update caller.
3. **REQ-04 fail-closed on write error.** RED:
   `test_reap_fails_closed_when_handoff_write_fails` — handoff write raises OSError →
   lock file survives, no ledger event, lock NOT in reaped list. GREEN: wrap the
   write in try/except; on failure skip unlink + skip event (preserve lock).
4. **REQ-05 no ADR-package writes.** RED: `test_no_adr_package_handoff_writes`
   (static grep assertion: no `{ADR-package}/handoffs/` write target in src/). GREEN:
   confirm all writes target `.gzkit/handoffs/` (already true post-step-2).
5. **REQ-06 docs.** Update both manpages (exit-3 table row; Reaping subsection;
   list-emits-ledger note).
6. **Fold-in (operator decision):** add the OBPI-05 runbook crumb? NO — runbook is
   OBPI-05's Allowed Path / OBPI-03's Denied Path. The "fold runbook docs into 03"
   idea from the A.5 assessment is deferred: manpages (03's surface) carry the lock
   docs; the runbook refresh stays parked with 05. Do not touch `docs/user/runbook.md`.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz covers OBPI-0.0.41-03-release-fail-closed-and-reaping --json
uv run gz validate --documents
```

## Notes

- STOP-on-BLOCKERS satisfied: OBPI-02 landed (`--abandon`, degenerate-handoff
  writer, `reaping` category, optional `handoff_path` all present).
- Boundary fence: do NOT touch `scripts/session_orientation.py`, the handoff skill,
  the runbook, the validator (`lock_handoff_coupling.py`), the parent ADR, or
  `write_lock`/`--abandon` registration — those belong to OBPI-02/04/05.
