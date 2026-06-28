---
mode: CREATE
adr_id: ADR-0.0.41
branch: main
timestamp: "2026-06-28T20:56:47Z"
agent: claude-code
obpi_id:
last_lock_event_timestamp:
last_commit_sha: 6ba97c87
session_id:
continues_from: .gzkit/handoffs/20260628T194858Z-token-block-reaper-defects.md
---

<!-- Handoff document for ADR-0.0.41 — created by claude-code at 2026-06-28T20:56:47Z -->

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

This session closed the **last two token-block lock defects** (4 and 5) from
`docs/governance/state-of-gzkit-2026-06-20.md` §1d, draining the entire
five-defect set. Both landed as operator-authorized direct fixes with TDD
(RED observed, then GREEN), and the Movement II campaign item was checked off.

- **Defect 4 — two divergent reapers** (commit `ec83b5e8`):
  `preflight._apply_cleanup` raw-`unlink`ed expired lock files with zero ledger
  event and zero register entry — a silent bypass of the token-block
  audit-coupling invariant. It now routes expired-lock surrender through the
  canonical `lock_manager.reap_expired_locks`, which writes an
  `abandoned_by_reaper` register entry and emits `obpi_lock_released` BEFORE
  removing the lock. Verified end-to-end with a real `gz preflight --apply` over
  an expired lock (lock gone, release event in ledger, reaping handoff on disk).
- **Defect 5 — SessionStart auto-reap is fiction** (commit `b7c20dd3`):
  `scripts/session_orientation.py` hardcoded `"obpi_locks": []` and never reaped.
  New `collect_obpi_locks(repo_root)` mirrors `gz obpi lock list` — reaps past-TTL
  locks (audit-coupled) and surfaces held ones — guarded end-to-end so the boot
  hook never crashes.
- **Push unblocker** (commit `6ba97c87`): the push surfaced a pre-existing,
  unrelated fail-closed gate — the tautological test audit flagging two
  filesystem/source-grep guards in `tests/test_skills.py` (GHI #453). Per
  operator ruling, the two guards were converted to behavioral positive
  assertions over `scaffold_skill` output, preserving the GHI #453 intent and
  clearing the gate.

`gz check` exits 0. Tree is clean and synced with `origin/main` at HEAD
`6ba97c87` (`git rev-list --left-right --count origin/main...HEAD` → `0  0`).
No OBPI lock held this session (direct fixes; no lock claimed). No pipeline in
progress.

## Important Context

- **The five §1d defects are now fully drained.** Prior session (`358332b0`)
  closed #1 (completion never releases → GHI #619, `74e428fb`), #3 (TTL drift
  12× → GHI #604, `6d490278`), and reframed #2 ("release fail-closed without a
  handoff") as *correct-by-design*. This session closed #4 and #5.
- **This was a correction, NOT a literal "lease re-model."** The campaign item
  was titled "Re-model the OBPI lock as a lease (… no handoff-as-evidence tax)."
  The prior session's operator-ratified reframing ruled that framing wrong: the
  O_EXCL claim path and the fail-closed register-entry precondition are correct
  by design, and ADR-0.0.41 is NOT reversed. The category error lived only on
  the *completion* and *reaping* edges. Defect #2 in particular was resolved by
  KEEPING the fail-closed handoff precondition (completion now satisfies it
  mechanically — token-block-discipline.md § Binding Sub-Invariant 6), the
  opposite of the "no handoff-as-evidence tax" the lease framing proposed. Do
  not re-open this as a lease re-model.
- **The canonical reaper is the one true surrender path.** Both defects were
  callers that bypassed `lock_manager.reap_expired_locks`. The fix in both was
  identical in spirit: stop hand-rolling lock deletion; route through the reaper
  that pairs every surrender with a register entry + `obpi_lock_released`.
- **`collect_obpi_locks` reaps on every session boot.** This is intended
  Sub-Invariant 4 behavior. In the common case (no locks) it writes nothing —
  `list_locks` returns empty, the reaper is a no-op, no ledger noise.
- **The tautological audit is advisory standalone but fail-closed at the
  pre-push `gz check` gate.** `gz validate --tautological-test-audit` prints its
  findings and exits 0; the pre-push aggregate treats them as fatal. That split
  is why a clean local `gz check` can still be blocked at push by an unrelated
  latent finding.

## Decisions Made

- **Decision:** Close defects 4 and 5 as direct fixes, not OBPI ceremony.
  **Rationale:** each is a single named surface with a small diff, meeting the
  direct-fix thresholds; 288 `fix(` precedents in 60 days; operator authorized
  the work explicitly.
  **Alternatives rejected:** OBPI ceremony (the handoff named these as direct
  fixes; operator confirmed).
- **Decision:** Convert the two flagged `tests/test_skills.py` guards rather than
  `--no-verify` the push or leave the work unsynced.
  **Rationale:** operator ruling when presented the three options. `--no-verify`
  is an explicit git-sync red flag; leaving work unsynced violates the sync
  ritual.
  **Alternatives rejected:** investigate gate tightening first; file a GHI and
  leave unpushed.
- **Decision:** Convert the guards to behavioral positive assertions over
  `scaffold_skill` output instead of deleting the GHI #453 regression intent.
  **Rationale:** preserves the intent (scaffold inlines a stub, no template
  consumer, no `render_template` path) while removing the proxy tautology; the
  un-flagged sibling test was the model.
  **Alternatives rejected:** weaken or drop the regression guard.
- **Decision:** Check off the campaign item with a `Completed` annotation that
  records the correction framing, preserving the operator's verbatim item text.
  **Rationale:** a silent tick would let the superseded "lease re-model" framing
  read as achieved — the doctrine-drift the campaign's own §5 warns against.

## Immediate Next Steps

<!-- ADVISORY ONLY — present to the operator and await authorization. -->

1. **Pull the next Movement II item under operator direction.** The campaign
   (`docs/governance/build-to-1.0-campaign-2026-06-20.md`, Movement II) now shows
   the lock item checked. The remaining open Movement II items in document order
   are: **CMS OKF documentation knowledge structure** (line 234) and the
   **Kind-blind behave gate** (~3 lines, line 240). The campaign governs the pull
   order; confirm with the operator which to pull — do not assume document order
   is pull order.
2. **If the Kind-blind behave gate is chosen:** it is described as ~3 lines
   mirroring the SUPPORT/STRUCTURAL-FENCE exemption already present in the behave
   gate. Scope it as a direct fix; locate the behave-req-tags gate logic
   (`gz validate --behave-req-tags`) and mirror the existing kind-aware exemption
   (see `.claude/rules/tests.md` § Behave scenario tagging, GHI #636).
3. **Before either:** confirm the floor is green (`uv run gz check` exit 0) and
   re-read the chosen item's linked design note.

## Pending Work / Open Loops

- **All five §1d lock defects: closed.** No lock-category work remains in
  Movement II.
- **CMS OKF documentation knowledge structure** (campaign line 234) — open;
  awaits MX substrate and operator pull.
- **Kind-blind behave gate** (campaign line 240) — open; ~3-line direct fix.
- **Remaining state-of-gzkit cut order** (campaign line 241) — open backlog,
  each as a patch with live-NC proof.
- No active OBPI lock, no active pipeline, no blockers.

## Verification Checklist

- [ ] `uv run gz check` exits 0 (floor green)
- [ ] Branch matches: `git branch --show-current` returns `main`
- [ ] `git rev-parse --short HEAD` returns `6ba97c87` (or later; operator explains drift)
- [ ] Synced: `git rev-list --left-right --count origin/main...HEAD` returns `0  0`
- [ ] Defect 4 fixed: `git show ec83b5e8 -- src/gzkit/commands/preflight.py` shows reaper routing, no raw lock `unlink`
- [ ] Defect 5 fixed: `scripts/session_orientation.py` defines `collect_obpi_locks` and `collect_state` calls it (no hardcoded `"obpi_locks": []`)
- [ ] Tautological audit clean: `uv run gz validate --tautological-test-audit` reports all validations passed

## Evidence / Artifacts

- `src/gzkit/commands/preflight.py` — `_apply_cleanup` now routes expired-lock surrender through `reap_expired_locks` (Defect 4 fix).
- `scripts/session_orientation.py` — `collect_obpi_locks` reaps past-TTL locks and surfaces held ones (Defect 5 fix).
- `tests/commands/test_preflight.py` — adds `test_apply_reaps_expired_lock_with_audit_trail` (asserts release event + register entry, not just a gone file).
- `tests/scripts/test_session_orientation.py` — adds `TestCollectObpiLocks` (reap-with-audit-trail, surface-active, empty-degrade).
- `tests/test_skills.py` — two GHI #453 guards converted to behavioral assertions over `scaffold_skill` output.
- `docs/governance/build-to-1.0-campaign-2026-06-20.md` — Movement II lock item checked with the correction-framing `Completed` annotation.
- `docs/governance/state-of-gzkit-2026-06-20.md` — §1d catalogs the five lock defects (source of truth; all now drained).
- `.claude/rules/token-block-discipline.md` — § Binding Sub-Invariant 3 (reaping register entry), § Sub-Invariant 4 (TTL + cadence), § Sub-Invariant 6 (mechanical completion surrender): the canon the fixes honor.
- `.gzkit/handoffs/20260628T194858Z-token-block-reaper-defects.md` — predecessor handoff (the work order for defects 4 and 5).

## Environment State

Python 3.13 / uv. HEAD `6ba97c87` on `main`, synced with `origin`. This session
shipped `ec83b5e8` (Defect 4), `b7c20dd3` (Defect 5), and `6ba97c87` (the
tautological-audit push unblocker).
