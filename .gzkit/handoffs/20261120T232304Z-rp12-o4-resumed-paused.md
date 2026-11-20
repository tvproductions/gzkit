---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-20T23:23:04Z'
agent: claude-code
session_id: 6bd39832-17e5-4522-baa3-7d1b0f6ed594
continues_from: .gzkit/handoffs/20261120T204504Z-rp12-o4-ghis-filed.md
---

## Current State Summary

Since handoff 20261120T204504Z (RP-12 O4's three GHIs filed): that handoff was resumed and every claim checked against Layer 2, all VERIFIED. GHIs #1331, #1332 and #1333 are OPEN with their titles; git count-objects -v reports garbage 0; origin/main...HEAD reads 0 0 after a fresh fetch; no OBPI lock is held, no tag is issued, no work package is in flight; CI's last three runs on main are green. The operator ruled pause, booked with gz handoff decide, setting aside O4 task 3. A statusline-setup agent was run on the operator's /statusline command; it found no PS1 in ~/.zshrc, ~/.bash_profile or ~/.profile (~/.bashrc does not exist) and changed nothing, leaving the existing statusLine command in ~/.claude/settings.json in place. No repository code changed. O4 task 3, the carry, is still next.

## Important Context

Safe mode is open (contract docs/governance/harbor-pilotage-candidate-2026-10-15.md); every act is one commit with Task: TASK-rnd-repair-work-organization. The MX session lease was last renewed 2026-11-20T05:38:21Z for 1440 minutes, so it expires near 2026-11-21T05:38Z; the hangar's advisory debt passed 828 hours. gz mx has no status subcommand (enter, exit, renew, repair); the lease is read from the ledger's mx_session_lease_renewed and mx_session_lease_expired events. Shift turnover review: gz wp tag show --all reports no tag issued, gz wp runs reports no work package in flight, gz obpi lock list reports no active locks.

## Decisions Made

- [operator-ruled] Pause the resumed handoff: write the successor handoff and git sync rather than open O4 task 3 (verbatim: "create handoff and git sync").

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide; the MX lease expires near 2026-11-21T05:38Z, so renew it through the gz-mx skill if the session runs that late.
2. Read CI on the synced HEAD with gh run list --workflow CI --limit 3; if check is red, repair it first.
3. Open O4 task 3, the carry (rulings 30, 142, 171): read gzkit.order_ledger.hung_tag_refusal, _check_accepted, _check_closed and gzkit.work_package_ledger._check_repair_close, and put task 3's opening questions to the operator one at a time.

## Pending Work / Open Loops

GHIs #1331, #1332 and #1333 are filed and unselected; none is being worked. GhUnansweredError subclasses OSError, so a future caller that lets it escape exits 1, not 2 (quality re-review, info). The status line's effort and rate-limit groups remain unconfirmed against Claude Code's statusLine input. The MX lease and advisory debt keep aging; renewal or exit is the operator's through gz-mx.

## Verification Checklist

uv run gz handoff resume shows this document Fresh; gh issue view 1331, 1332 and 1333 each open; git rev-list --left-right --count origin/main...HEAD reads 0 0 after sync; gh run list --workflow CI --limit 3; grep the ledger for the handoff_resume_decided event on 20261120T204504Z with decision pause.

## Evidence / Artifacts

Predecessor `.gzkit/handoffs/20261120T204504Z-rp12-o4-ghis-filed.md`; the handoff_resume_decided event (decision pause) in `.gzkit/ledger.jsonl`; GHIs https://github.com/tvproductions/gzkit/issues/1331, https://github.com/tvproductions/gzkit/issues/1332, https://github.com/tvproductions/gzkit/issues/1333.

## Settled Rulings

2389 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
