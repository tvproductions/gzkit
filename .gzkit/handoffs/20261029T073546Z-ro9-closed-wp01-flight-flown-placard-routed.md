---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-29T07:35:46Z'
agent: claude-code
session_id: fe40d249-a9b4-4f1c-aabd-1b207be9e01a
continues_from: .gzkit/handoffs/20261029T053948Z-ro9-tranche-7-checkpoint-committed.md
---

## Current State Summary

RO-9 is closed. Tranche 7 was finished (82bb9eddc: 11 tests, the init manpage, adopter docs on uv tool install and uvx only, a behave scenario; 750b93a4b: 9 gap tests and a mutation sweep of the checkpoint's 15 surviving hunks, 13 killed and 2 accepted survivors; 15ea1131b: the tranche 7 record). CI run 40830666171 on 5427c7a15 is green (ubuntu gz check --full, windows gz check --cross-platform). RO-5's witness flight was finished as a TEST FLIGHT under safe mode: WP-01-astral-toolchain was accepted (94b06d279) and closed through the operator's Gate 5 (af1e7dbcf), which closes RO-9. The mx-session lease was renewed on the operator's word (9276d47c2). Two GHIs were filed: #1298 (the ty LSP serves a stale buffer) and #1299 (no placard shows the mode an act runs under), the latter re-scoped by the operator to a broad mode-contract design. A first gz wp-local fix for #1299 was reverted before commit. Everything is committed; the tree holds only the session's ledger rows.

## Important Context

Safe mode is still open (drydock, contract docs/governance/harbor-pilotage-candidate-2026-10-15.md). Shift turnover: this session hung no tag, holds no finding awaiting buy-back, and leaves no commenced work package (WP-01 is closed; it was the only one); the tag-out log is RO-12's and does not exist yet, so the review read gz obpi lock list (mx-session only) and the contract's § List of discrepancies. The mx-session lock is held by claude-code-fe40d249, renewed 2026-10-29 at a 24h lease. Placarding is the interim procedure until #1299's design lands: every test-flight or sea-trial act carries a placard at the top of the message, in the commit subject and in the recorded evidence (operator: 'that's why the placarding would really help'). New fittings such as gz wp are tested under named flights, which the operator accepts; what must not happen is presenting them as resumed civil ceremony. The ty LSP (server PID 9933, started 2026-10-27) answers from a buffer that no longer matches disk for files changed out of band (#1298); verify Python facts with uv run ty check and the file itself until the server is restarted. The two operator-sourced insights of this session are in .gzkit/insights/agent-insights.jsonl (file a found defect without asking; a mode indication is broad MX design, not a civil verb's flag).

## Decisions Made

- [operator-ruled] Proceed with advised step 1, finishing tranche 7 (verbatim: "1").
- [operator-ruled] Renew the mx-session lease (verbatim: "renew lock", then "renew mx drydock"), done once through gz mx renew --attestor g0.
- [operator-ruled] Witness the checkpoint's hunks with new tests and a mutation sweep (verbatim: "a").
- [operator-ruled] Proceed with step 2 after the big-picture read (verbatim: "proceed with step 2").
- [operator-ruled] Finish RO-5's witness flight through accept and the Gate 5 close (verbatim: "finish the witness flight").
- [operator-ruled] Gate 5 on WP-01, closing RO-9, with the drafted residual risk (verbatim: "revert, comment on 1299, close WP-01 placarded, then handoff"; residual risk "yes").
- [operator-ruled] The placard is a broad MX safe-mode design question, not part of gz wp (verbatim: "that is a broad indictation during mx safemode, not a normal part of gz wp"); marking a particular tool or procedure as in safe mode is also legitimate, and the design may yield one or more orders.
- [agent-chose] Recorded the sweep under docs/governance/ro9-tranche7-red-sweep-2026-10-29-evidence/ with machine-local paths stripped, because they carry the operator's name.
- [agent-chose] Did not restart the stale ty server; it is the operator's harness process.

## Immediate Next Steps

1. Ask the operator to review the supply-chain-audit and supply-chain-audit-ignored canaries through gz canary review (carried from the predecessor's step 4).
2. Put the post-RO-9 sort to the operator: which remaining orders (RO-1, RO-4, RO-6, RO-7, RO-8, RO-11, RO-12, RO-13) must close before exit, and which carry over as work packages at the handback; RO-13 is the order that makes waiting expensive.
3. Clear the 2026-10-27 gz check --full failures from the contract: CI's ubuntu gz check --full is now green, so trace which commits cleared each of the nine and record it.
4. When the operator selects it, carry #1299 into the mode-contract design (RO-12's specification or RO-13's), using the operator's words on the issue; until then placard every flight act by hand.

## Pending Work / Open Loops

- GHI #1298 (ty LSP stale buffer): filed, eligible, not selected; workaround is a server restart or verifying with uv run ty check.
- GHI #1299 (mode placards): re-scoped on the issue to the broad design; not selected.
- RO-9's seven § List of discrepancies lines stay open until cleared with the alarms on at gz mx exit (WP-01's residual risk).
- The CI matrix has no macOS job; macOS was covered only by local runs.
- The non-blocking rendition-lineage advisory on NCSurface.md/root appears in every gz check and CI log; not investigated.
- RO-5 itself still closes through its own Gate 5; its witness flight is now flown end to end.
- 31 chores overdue; the MX advisory debt is about 290h old.

## Verification Checklist

- uv run gz wp show WP-01-astral-toolchain reads state closed.
- uv run gz validate --astral-discipline exits 0 and data/astral_discipline_baseline.json holds 0 rows.
- gh run view 40830666171 shows both jobs success.
- git rev-list --left-right --count origin/main...HEAD reads 0 0 after this handoff's sync.
- uv run gz obpi lock list shows mx-session held by claude-code-fe40d249.
- gh issue view 1298 and gh issue view 1299 are open.

## Evidence / Artifacts

- `docs/governance/harbor-ro9-astral-toolchain.md` (status line: RO-9 closed; § Ruled for tranche 7)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (passage-log rows for tranche 7 and the test flight; RO-9 discrepancy line for the replaced scaffold)
- `docs/governance/ro9-tranche7-red-sweep-2026-10-29-evidence/README.md`
- `tests/commands/test_init.py`
- `features/init.feature`
- `docs/user/manpages/init.md`
- `data/catalog/work_packages.json`
- Commits 82bb9eddc, 9276d47c2, 750b93a4b, 15ea1131b, 5427c7a15, 94b06d279, e2716c8c0, af1e7dbcf; receipts arb-red-commit-b5d6335cfb83-33b9efa3129b40bb801ad40cf89edbb3, arb-step-mkdocs-e40a8b04048d46dc87c03c1f214320b5, arb-step-mkdocs-d649a0e075704e7fa529dafc41b0c27f, arb-step-mkdocs-754f5f59ec654b20b0a323b1f3d2c0d5

## Settled Rulings

1817 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
