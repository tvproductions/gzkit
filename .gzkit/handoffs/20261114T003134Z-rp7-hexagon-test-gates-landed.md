---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-14T00:31:34Z'
agent: claude-code
session_id: 7d61ad27-4842-41ba-a915-ffa2adb85c21
continues_from:
- .gzkit/handoffs/20261113T100108Z-ghi1267-held-and-dispatcher-injected.md
- .gzkit/handoffs/20261113T101223Z-session-exit-bookmark.md
- .gzkit/handoffs/20261113T101731Z-session-exit-bookmark.md
---

## Current State Summary

RP-7's hexagon test gates landed and passed independent review: gz validate --hexagon-tests runs in the default tier of every per-change gz check, with 6,136 findings in 164 test modules (3,540 labels, 2,295 covers, 301 mock, all through gzkit.cli) held in the shrink-only data/hexagon_test_baseline.json (f8d1a8f14, d6eb328eb, eb76acdd5, 19ef2fddc, 95a0acdce). The first review returned CONCERNS (inner mock reach through import unittest, keyword patch targets, missing doubles, a control that planted no adapter patch); all four were repaired test-first and the second review returned PASS. RP-7's blocks-return-to-service line records the landing and stays open until cleared with the alarms on. Earlier in the session, before the operator's correction back to drydock work, GHIs 1318 to 1324 were routed (d0a9b2ffe), #1320 was fixed and closed (9a6468d67, 525d1ecec, a6f1418a6), and #1318 was fixed and closed (bf6e5c588, 305b7fbe2, c6aedfb52). Everything is pushed; main is level with origin at 95a0acdce.

## Important Context

Safe mode is active; every act is one commit with the Task: TASK-ro6-classic-adr trailer, and a contract edit books an mx_contract_amended ledger pin that needs its own commit. GitHub reads closing-keyword shapes in a commit body: the routing commit d0a9b2ffe ('direct fix: #1318, #1321, #1324') auto-closed all three on push; #1321 and #1324 were reopened with a correction comment. Scan unpushed commit bodies for closing keywords before every push. On resume with safe mode open, rank the handoff's advised options against the contract's repair orders first and name which are drydock work (the operator corrected this session: 'Back to drydock'). The hexagon test checker judges coverage from import statements only, and a string patch target by its prefix; both limits are stated in the validate manpage. Shift turnover: no tag-out log or work-package record exists yet (RO-12); in their place I read the contract's List of discrepancies RP-7 lines and gz obpi lock list (mx-session held by claude-code-55f2e5b3, lease renewed earlier today); this session hung no tag.

## Decisions Made

- [operator-ruled] Proceed on the ghi1267-held-and-dispatcher-injected handoff (verbatim: "Proceed").
- [operator-ruled] Route GHIs 1318 to 1324 next (verbatim: "Route GHIs 1318-1324").
- [operator-ruled] GHIs 1318, 1321 and 1324 are direct fixes (verbatim, for each: "Direct fix now").
- [operator-ruled] GHI 1319 goes on a line on RP-14, due with tranche 3 (verbatim: "Line on RP-14").
- [operator-ruled] GHI 1320 is verified and closed (verbatim: "Verify and close").
- [operator-ruled] GHIs 1322 and 1323 become work orders after return to service (verbatim, for each: "Work order after RTS").
- [operator-ruled] Record the routing on the contract and post a comment on each GHI (verbatim: "Yes, record it").
- [operator-ruled] Amend only ADR-0.0.3's injection-seam callout, leaving its sealed briefs (verbatim: "Amend ADR callout only").
- [operator-ruled] GHI 1318 is repaired by demoting @advances to an optional annotation and keeping the decorator (verbatim: "Demote, keep decorator").
- [operator-ruled] Return from GHI work to drydock work (verbatim: "Back to drydock").
- [operator-ruled] RP-7's hexagon test gates move next (verbatim: "RP-7 hexagon test gates").
- [operator-ruled] The hexagon test gates hold every region, adapters included (verbatim: "Regions incl. adapters").
- [operator-ruled] The hexagon test gates exclude the kernel (verbatim: "Exclude the kernel").
- [operator-ruled] The fakes-only gate judges mocks per patch target (verbatim: "Per patch target").
- [operator-ruled] A fake adapter's tests declare their @covers exemption with a module comment marker (verbatim: "Module comment marker").
- [agent-chose] Built one gz validate scope with three rules and one shrink-only baseline, following RP-15 tranche 6's --hexagon-dependencies pattern, and placed the checker in gzkit.governance.trust_audits rather than the kernel, because the specification keeps gzkit governance concepts such as @covers out of the kernel.
- [agent-chose] Pruned the private-import ratchet baseline edge that #1267 item (c) had removed (28cecb859), found failing at HEAD while verifying #1320.
- [agent-chose] Recorded the closing-keyword auto-close, the superseded pool ADR's stale canon pointers and the operator's drydock correction as insight records rather than GHIs.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide under the new session's own id.
2. Ask which drydock work moves next, ranked against the contract's open blocks-return-to-service lines: RP-7's held rulings H1 to H14; RP-7's findings F2 (five gz validate scopes on no gate) and F3/F4 (the empty security walkthrough); RP-14's work-package-pipeline line, which may be partly stale since gz wp now lists dispatch, block, unblock and acceptance; RP-5, RP-11 and RP-13's lines.
3. Offer to file through ghi-author the two untracked process defects: gz lint --fix rewriting dated evidence scripts, and the absent commit-msg check for GitHub closing keywords.
4. Name GHIs 1321 and 1324 as routed direct fixes outside the repair orders, to be taken only on the operator's word.

## Pending Work / Open Loops

GHIs 1321 (formatter port takes Rich's Table) and 1324 (OBPI template's AirlineOps checkpoint) are open, routed as direct fixes, not started. GHI 1319 is held on its RP-14 line; GHIs 1322 and 1323 wait for work orders after return to service. RP-7's hexagon test gate line is open until cleared with the alarms on; the variant gate (#91c) is due by the first hexagon REQ admitted; the 6,136-finding baseline drains under the waiver-ratchet-drawdown chore. GHI 1267 is held to migration and RP-15 tranche 6's structures line stays open. gz lint --fix rewrites dated evidence scripts and no GHI tracks it; nothing refuses a closing keyword in a commit body (insight recorded). The diagnose --json keys still label @advances as ch1. The ratchet-drawdown workflow's first run on GitHub has not been observed.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD reads 0 0; uv run gz validate --hexagon-tests exits 0; uv run -m unittest tests.governance.test_audit_hexagon_tests passes (27 tests); uv run gz validate --waiver-ratchet passes; gh issue view 1318 and 1320 show CLOSED, 1321 and 1324 show OPEN.

## Evidence / Artifacts

- `src/gzkit/governance/trust_audits/hexagon_tests.py`
- `tests/governance/test_audit_hexagon_tests.py`
- `data/hexagon_test_baseline.json`
- `docs/governance/harbor-ro7-placement.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/user/manpages/validate.md`
- `.gzkit/rules/tests.md`
- `.gzkit/rules/task-discovery.md`
- `docs/governance/hexagonal-architecture.md`
- Commits d0a9b2ffe, 9a6468d67, 525d1ecec, a6f1418a6, 28cecb859, bf6e5c588, 305b7fbe2, c6aedfb52, f8d1a8f14, d6eb328eb, eb76acdd5, 19ef2fddc, 95a0acdce.

## Settled Rulings

2206 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
