---
mode: CREATE
adr_id: ADR-0.0.41
branch: main
timestamp: "2026-06-28T19:48:58Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: 6d490278
session_id:
continues_from: .gzkit/handoffs/20260628T110626Z-movement-ii-cut1-antibody-complete.md
---

<!-- Handoff document for ADR-0.0.41 — created by claude-code at 2026-06-28T19:48:58Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

## Current State Summary

This session worked Movement II of the Build-to-1.0 campaign (continuing from the
antibody-cut handoff) and shipped **two of the five token-block lock defects** from
`docs/governance/state-of-gzkit-2026-06-20.md` §1d, both as direct fixes with GHIs
closed:

- **GHI #619** (commit `74e428fb`) — completion is now the token-block exit edge:
  `gz obpi complete` mechanically writes a register-entry completion handoff and,
  if a lock is held, releases it and emits `obpi_lock_released` citing that
  handoff. The manual `gz obpi lock release` chore at pipeline close is gone.
- **GHI #604** (commit `6d490278`) — the lock TTL default was corrected from 120m
  to 1440m (24h canon) via one shared constant `DEFAULT_LOCK_TTL_MINUTES` in
  `lock_manager.py`, referenced by the CLI claim default, the preflight expiry
  fallback, and the MX session lock.

Tree is clean and synced with `origin/main` at HEAD `6d490278`; `gz check` was
green (38/38) at both commits. No active OBPI lock, no pipeline in progress.

This handoff exists to capture the **two remaining lock defects** (4 and 5) that
were deliberately deferred this session, so the operator can pick them up later.

## Important Context

- The five lock defects are catalogued in
  `docs/governance/state-of-gzkit-2026-06-20.md` §1d. Three are now resolved: #619,
  #604, and the framing correction that this work is **not** a "lease re-model" and
  **not** a reversal of ADR-0.0.41 — completion produces its register entry
  mechanically; the fail-closed manual release path stays for mid-traversal
  surrender (token-block-discipline.md § Sub-Invariant 6, added this session).
- **Defect 4 — two divergent reapers.** `lock_manager.reap_expired_locks` is the
  canonical reaper: it writes an `abandoned_by_reaper` register entry, then deletes
  the lock, then emits `obpi_lock_released` (fail-closed ordering). But
  `preflight._apply_cleanup` independently raw-deletes expired lock files via
  `path.unlink(missing_ok=True)` with zero ledger event and zero handoff. The
  preflight path is a silent bypass of the token-block audit-coupling invariant: a
  lock can vanish with no `obpi_lock_released` event in the ledger.
- **Defect 5 — SessionStart auto-reap is fiction.** token-block-discipline.md
  § Sub-Invariant 4 says the SessionStart hook auto-reaps expired locks at the 24h
  TTL, but `scripts/session_orientation.py` hardcodes `"obpi_locks": []` and never
  calls `reap_expired_locks`. The only caller of `reap_expired_locks` is
  `obpi_lock_list_cmd` (`gz obpi lock list`), so locks are reaped only if a human
  runs that command — the advertised automatic cadence does not exist.
- TTL is now 1440 (24h) everywhere via `lock_manager.DEFAULT_LOCK_TTL_MINUTES`; the
  reapers read `ttl_minutes` off each lock, so they already honor the canon once
  consolidated.

## Decisions Made

- **Decision:** Defer defects 4 and 5 to a later operator-driven session.
  **Rationale:** the operator scoped this session to the completion-ceremony
  correction (#619) and the TTL drift (#604); 4 and 5 are the abandonment-backstop
  machinery, a separable concern.
  **Alternatives rejected:** bundling all five into one sweep — the operator
  explicitly narrowed scope to the close ceremony.
- **Decision:** Do not file GHIs for 4 and 5 now; this handoff is the work order.
  **Rationale:** operator moratorium on reflexive GHI-filing (2026-06-01).
  **Alternatives rejected:** filing two GHIs to satisfy a trailer.
- **Decision:** Route each as a direct fix when picked up.
  **Rationale:** each is a single named surface with a small diff, meeting the
  direct-fix thresholds and the operator's defect-repair doctrine.
  **Alternatives rejected:** OBPI ceremony.

## Immediate Next Steps

<!-- ADVISORY ONLY — present to the operator and await authorization. -->

1. **Defect 4 — consolidate the reapers.** Route `preflight._apply_cleanup`
   expired-lock deletion through `lock_manager.reap_expired_locks` (or a shared
   helper) so every lock surrender writes a register entry and emits
   `obpi_lock_released`. Remove the raw `path.unlink` for locks in
   `src/gzkit/commands/preflight.py`. TDD: `gz preflight --apply` over an expired
   lock must leave an `obpi_lock_released` event in the ledger and a reaping handoff
   on disk, not a silent unlink.
2. **Defect 5 — make SessionStart auto-reap real.** Wire
   `scripts/session_orientation.py` to call `lock_manager.reap_expired_locks` (and
   read real locks via `list_locks`) instead of hardcoding `"obpi_locks": []`.
   Surface actually-held locks in orientation and reap past-TTL ones per
   Sub-Invariant 4. TDD: orientation over an expired lock reaps or reports it rather
   than printing "(no active locks)".
3. **Before either:** confirm the floor is green (`uv run gz check` exit 0) and
   re-read state-of-gzkit §1d plus token-block-discipline.md § Sub-Invariant 3 and 4
   for the reaping register-entry and cadence contract.
4. Land each as `fix(<scope>): <summary>` with a `Task:` trailer; attach a GHI only
   if the operator wants one (moratorium otherwise).

## Pending Work / Open Loops

- **Defect 4** (two divergent reapers) — open.
- **Defect 5** (SessionStart auto-reap is fiction) — open.
- These are the last two of the original five lock defects (state-of-gzkit §1d); the
  other three are closed as of this session.
- No active OBPI lock, no active pipeline, no blockers. The campaign's Movement II
  has now drained the lock-category items down to these two backstop defects.

## Verification Checklist

- [ ] `uv run gz check` exits 0 (floor green)
- [ ] Branch matches: `git branch --show-current` returns `main`
- [ ] `git rev-parse --short HEAD` returns `6d490278` (or later; operator explains drift)
- [ ] GHIs #619 and #604 are closed (`gh issue view 619`, `gh issue view 604`)
- [ ] Defect 4 still present: `path.unlink` for expired locks in `src/gzkit/commands/preflight.py` `_apply_cleanup`
- [ ] Defect 5 still present: `scripts/session_orientation.py` hardcodes `obpi_locks` empty

## Evidence / Artifacts

- `docs/governance/state-of-gzkit-2026-06-20.md` — §1d catalogs the five lock defects (source of truth for this work).
- `src/gzkit/lock_manager.py` — the canonical reaper `reap_expired_locks` and `DEFAULT_LOCK_TTL_MINUTES`.
- `src/gzkit/commands/preflight.py` — `_apply_cleanup` raw-unlinks expired locks (defect 4 surface).
- `scripts/session_orientation.py` — hardcodes `obpi_locks` empty (defect 5 surface).
- `.gzkit/rules/token-block-discipline.md` — § Sub-Invariant 3 (reaping register entry) and § Sub-Invariant 4 (TTL and reaping cadence): the canon the fixes must honor.

## Environment State

Python 3.13 / uv. HEAD `6d490278` on `main`, synced with `origin`. This session
shipped `74e428fb` (GHI #619) and `6d490278` (GHI #604).
