---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-24T08:35:41Z'
agent: claude-code
session_id: 60616519-0120-43a2-982b-5d9453723eb2
continues_from: .gzkit/handoffs/20260924T074009Z-budget-held-under-stay-cards-current.md
---

## Current State Summary

Resumed 20260924T074009Z and worked three of its four advised steps under operator rulings. Step 1 (escalate REQ-0.0.54-01-03) was SET ASIDE: nothing fails and the budget values sit under the pre-1.0 stay. Step 2 landed as b1e9bd1e2 and closed GHI #1087 fixed: a dated stay-site census in the budget history plus a Movement D amendment requiring enforcement-staying rulings to name their sites. Step 3 landed as c4f769263 and closed GHI #1085 fixed: the 35-scenario @wip file features/brief_reconcile.feature is deleted and behave.ini's tracking-reference claim is demoted to advisory. Behave now runs 73 features and 433 scenarios with 0 skipped. Step 4, the next IEEE measurement, is unruled. At the operator's request, 245275c93 committed docs/evals/test-suite-integrity-audit-2026-09-24.md, a 977 KB diagnostic another session wrote under operator authorization.

## Important Context

The test-suite integrity audit is diagnostic only. Its pin is 5d9885a08, and it says it made no fixes, commits or ledger events. Its verdict: a green unit run is not sufficient evidence that required behavior is protected. It names a constant assertTrue(True), a vacuous scanner assertion, an exemption test with no specimen, a loosened command-count oracle (53 exact became at least 50 at 9e539d066), two surviving behavior-changing req_coverage mutants, and a completion gate that warns instead of stopping a lite OBPI missing BEHAVIOR proof. Its random-sample confirmed defect rate is 1/300, so it does not support a claim that most tests verify nothing. Sections 5 (twenty confirmed tests), 9 (an unapplied pool-ADR diff) and 10 (proposed CI gates) are all offered for operator disposition, and none is enabled. mkdocs build --strict passes with it present; its 3,182 absolute /Users/jeff links and two broken in-page anchors raise INFO only. The predecessor's standing cautions carry unchanged: gz check is the per-change scope and --full precedes any CLI or contract push; D-01 and D-05 remain UNRESOLVED; Phase 4 is unauthorised. git add -A in a checkout another session writes to stages that session's files. It did so this session and the end-of-file hook rewrote the audit file's trailing newline, so stage paths explicitly.

## Decisions Made

- [operator-ruled] Set aside the REQ-0.0.54-01-03 escalation (verbatim: "set it aside"), after the operator asked why an older foundation ADR was being revisited when nothing failed.
- [operator-ruled] GHI #1087 takes shape C, a dated manual census, with the Movement D amendment (verbatim: "C with the Movement D amendment").
- [operator-ruled] GHI #1085: delete the 35 @wip scenarios and demote behave.ini's tracking-reference claim to advisory rather than build a validator (verbatim: "A + ii").
- [agent-chose] Closed #1087 and #1085 as fixed under operator-amended contracts, recording the declined mechanism as the uncovered row of each cause table rather than leaving either issue open.
- [agent-chose] Landed the audit report as authored apart from what the commit hooks changed: one end-of-file newline and trailing spaces on 32 lines, with git diff -w empty. Its absolute links and broken anchors are recorded here, not repaired.

## Immediate Next Steps

1. Choose the next IEEE measurement from M-A to M-G; M-D stays blocked on its method problem.
2. Dispose section 5 of docs/evals/test-suite-integrity-audit-2026-09-24.md, the twenty confirmed tests, starting with the constant assertTrue(True) in tests/governance/test_tautological_tests.py:29 and the loosened oracle in tests/test_doc_coverage.py:190; route each through ghi-author or direct repair as the operator rules.
3. Rule on the audit's section 9, an unapplied diff to the test-integrity-tooling pool ADR, and section 10, ten proposed scriptable CI gates; each is a proposal, not a booking.
4. Rule on the audit's finding that the completion coverage gate warns instead of stopping a lite OBPI missing BEHAVIOR proof; AGENTS.md says that REQ-coverage gate cannot be waived, so the finding reads as a defect against canon.

## Pending Work / Open Loops

The handoff decide record for steps 3 and 4 of the predecessor carried --set-aside by mistake; step 3 was then ruled proceed and worked, and step 4 is still open. Carried from the predecessor and still unfiled: gz git-sync auto-add stages files another session wrote, which recurred this session through git add -A; scorecard row 37a stays Promotable until a negative control pins Behave in the change scope's skips; whether to author a finding for D-08 now that M-F has run; the Sonnet tier's frontier scope is unruled. Two coupled observations from the REQ-0.0.54-01-03 read, not filed: docs/governance/req-scope-discipline.md line 140 cites REQ-0.0.54-01-03 as a SUPPORT example about scorecard row 58, which is not what that REQ says; the covering test's docstring names a 32768 B Codex cap while the validator reports 65536 B.

## Verification Checklist

git rev-list --left-right --count origin/main...HEAD reads 0 0 and git status --short is empty after the sync. gh issue view 1085 and 1087 each show CLOSED. uv run -m behave features/ exits 0 with 0 skipped scenarios. grep -rln @wip features/ returns nothing. uv run gz validate --instructions-files-budget exits 0 with one AGENTS.md WARNING, the ruled state. uv run mkdocs build --strict exits 0 with the audit file committed. gh run list --branch main --workflow CI shows b1e9bd1e2, c4f769263, 245275c93 and the sync commit green.

## Evidence / Artifacts

Census and set-aside record: `docs/governance/instructions-files-budget-history.md` (entry 2026-09-24 (2)). Movement D amendment: `docs/governance/build-to-1.0-campaign-2026-09-20.md` (Amendments 2026-09-24). Demoted @wip claim: `behave.ini`. Integrity audit: `docs/evals/test-suite-integrity-audit-2026-09-24.md`. Predecessor: `.gzkit/handoffs/20260924T074009Z-budget-held-under-stay-cards-current.md`. Commits: b1e9bd1e2 (GHI #1087), c4f769263 (GHI #1085), 245275c93 (audit).

## Settled Rulings

1048 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
