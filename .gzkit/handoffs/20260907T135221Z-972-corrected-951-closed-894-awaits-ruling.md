---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-07T13:52:21Z'
agent: claude-code
session_id: 42d22ad1-3e28-4c81-bb38-6ab677307a26
continues_from: .gzkit/handoffs/20260907T131513Z-972-census-guidance-landed-gh-cli-0-5-0.md
---

## Current State Summary

Two dispositions landed and synced. (1) GHI #972 reopened for a bounded correction and closed again against cfab17e8: gh-cli.md 0.5.0 -> 0.5.1 — the count form now refuses to print a number on incomplete_results (jq exit 5 on an incomplete fixture, the total on a complete search), and the at-limit claim was withdrawn: equality proves nothing either way, completeness is unproven until pagination or an authoritative total establishes it. (2) GHI #951 closed against a6cb5e3e with receipts in 299bd25d: the session-exit bookmark records a portable transcript reference (`<session_id>.jsonl` plus a resolver sentence) through one redaction helper, never the host's absolute path; 4/4 mutants killed. Open queue 39 by the refusing total_count form at 2026-09-07T13:52Z. ahead/behind 0 0. NO LIVE LEDGER ROW WAS CORRECTED — exactly three live corrections remain held. No OBPI machinery, no lock, no ADR touched.

## Important Context

QUEUE NARRATIVE CORRECTED (operator, 2026-09-07): GHI #894 is AWAITING A RULING, not 'next eligible'. Its remedy relocates _is_named out of src/gzkit/commands/content/retire.py, which the live brief OBPI-0.35.0-08 declares READ-ONLY naming that symbol; Layer-2 reads that OBPI IN PROGRESS. A void of OBPI-08's pipeline_launched row (held correction (a) on #611) would NOT authorize relocating _is_named and would NOT amend the brief's read-only declaration — those are three separate operator decisions and must stay separate. #951's fix deliberately added no frontmatter field: the structured transcript reference is #767's surface, parked behind ADR-pool.primary-source-corroboration ('do not build ahead of it'), and #766 (constant sections) stays blocked by #767; both carry cross-link comments dated 2026-09-07 stating exactly what remains. 176 committed bookmarks under .gzkit/handoffs/ still carry absolute paths as historical records — never rewrite them. The 299bd25d receipt commit message annotates the coverage receipt '(2 tests)' — a regex artifact of a truncated tail, disclosed in #951's close comment; the unittest receipt (9844) is the count of record. Claude-Session trailer conflict recurred; repo canon (task-discovery.md, operator verbatim 'never') was followed and no trailer authored. The ghi-triage census member is still tracked only in .gzkit/insights/agent-insights.jsonl (2026-09-07T12:57:26Z) and was not broadened into this pass.

## Decisions Made

- [operator-ruled] #972 correction bounded to two statements, verified across complete, incomplete, and exactly-at-limit cases (verbatim: "Provide a verified command that either exposes both fields or refuses to return a usable count when results are incomplete."; "State that **completeness is unproven** until pagination or comparison with an authoritative total establishes it."). Landed as gh-cli.md 0.5.1.
- [operator-ruled] #951 worked through the GHI skill, reading #767 and #766 first; neither auto-closed (verbatim: "Do not automatically close #767 or #766 because they share the writer; report precisely what remains in each.").
- [operator-ruled] Historical evidence preserved; no ledger rewrite, no history purge (verbatim: "Do not rewrite historical ledger rows or initiate a history purge.").
- [operator-ruled] #894 is awaiting a ruling, and the three decisions around it stay separate (verbatim: "A void of OBPI-08's launch would not authorize relocating `_is_named` or amend the brief's read-only declaration. Keep those decisions separate.").
- [operator-ruled] Exactly three live corrections remain held; no ADR/OBPI machinery; no reopening of completed repairs.
- [agent-chose] Reopened #972 rather than filing a fresh GHI (ghi-author Step 0: a <=30-day close of the same root cause is reopened, never duplicated) and closed it again citing cfab17e8.
- [agent-chose] Verified the incomplete case against a fixture response through the identical jq filter, since the live API cannot be made to report incomplete_results on demand; recorded as bounded verification, not a census subsystem.
- [agent-chose] Redacted to the transcript's final component with a resolver sentence rather than to the session id alone, so the artifact keeps the file identity (mutant redaction-drops-identity killed) without any directory of the host path; split on both separators for Windows harnesses.
- [agent-chose] Ran a four-mutant sweep via gzkit.mutation_witness; first pass read inconclusive only because expected_tests match by bare method name — re-run with bare names, 4 killed.

## Immediate Next Steps

1. Re-establish repository truth BEFORE acting: `git status --short`, `git log --oneline -6`, `git rev-list --left-right --count origin/main...HEAD`, `uv run gz obpi lock list`. This handoff ADVISES; it does not authorize.
2. Re-derive the open queue with the refusing form from gh-cli.md 0.5.1 § Census queries: `gh api -X GET search/issues -f q='repo:tvproductions/gzkit is:issue is:open' --jq 'if .incomplete_results then error("incomplete_results: no count obtained") else .total_count end'`. A `gh issue list` page is never the queue; equality with a --limit proves nothing.
3. Obtain the operator's ruling before drawing work and book it with `uv run gz handoff decide --handoff <this file> --session-id <id> --decision proceed --operator-text "<their exact words>"`.
4. #894 needs a RULING before it can be drawn: whether the _is_named relocation lands as GHI-direct repair while OBPI-0.35.0-08 is live and its brief declares retire.py read-only. That ruling is separate from held correction (a) on #611 and separate from any amendment to the brief. Do not infer one from another.
5. Carried order behind it, re-resolve each before drawing: 939, 922, 921, 815 open; 933, 953, 952 closed; 767, 766 open and parked behind ADR-pool.primary-source-corroboration; 973 queued.
6. The three live corrections for #611 (and #930 folded into it) remain the operator's to rule on.
7. When the operator draws it, route the ghi-triage census member through /ghi-author (insights record 2026-09-07T12:57:26Z, scope ghi-triage).

## Pending Work / Open Loops

- GHI #611 OPEN with its three live corrections held; GHI #930 OPEN, folded into #611. Untouched this session.
- GHI #894 OPEN, awaiting an operator ruling on the _is_named relocation versus OBPI-0.35.0-08's read-only declaration.
- GHI #767 OPEN (structured frontmatter transcript reference, parked); GHI #766 OPEN (constant sections, blocked by #767). Cross-link comments posted 2026-09-07.
- ghi-triage fetch() census defect tracked ONLY in .gzkit/insights/agent-insights.jsonl — no GHI yet.
- 299bd25d's commit message carries a misleading '(2 tests)' annotation on the coverage receipt; disclosed in #951 [settled]'s close comment, not amendable (pushed).
- Claude-Session trailer conflict between the harness reminder and task-discovery.md remains standing.

## Verification Checklist

Run each and read its own exit status, never a shell aggregate:

    uv run gz check
    uv run python -m unittest tests.governance.test_session_exit
    uv run python -m unittest tests.commands.test_issue_cmd
    gh issue view 972 --json state
    gh issue view 951 --json state
    gh api -X GET search/issues -f q='repo:tvproductions/gzkit is:issue is:open' --jq 'if .incomplete_results then error("incomplete_results: no count obtained") else .total_count end'
    grep -c 'rule-version: 0.5.1' .gzkit/rules/gh-cli.md .claude/rules/gh-cli.md src/gzkit/rules/gh-cli.md
    git rev-list --left-right --count origin/main...HEAD

Expected at 299bd25d: quality gate exit 0 (60 steps); 27 tests OK; 25 tests OK; #972 CLOSED; #951 CLOSED; a total or a jq error, never a page count; each gh-cli.md copy reports 1; ahead/behind 0 0. Read ARB receipt exit_status from the receipt JSON directly; never pipe a verifier into a filter.

## Evidence / Artifacts

Commit cfab17e8 — fix(gh-cli): count form exposes incomplete_results; at-limit equality proves nothing (GHI #972, reopened): .gzkit/rules/gh-cli.md, .claude/rules/gh-cli.md, src/gzkit/rules/gh-cli.md, .github/AGENTS.md, docs/design/adr/AGENTS.md, docs/governance/advisory-rules-audit.md, docs/governance/rule-version-history.md, .gzkit/ledger.jsonl (agent_sync_completed).
Commit a6cb5e3e — fix(session-exit): record a portable transcript reference, never the host's absolute path (GHI #951): src/gzkit/session_exit.py, tests/governance/test_session_exit.py.
Commit 299bd25d — receipts, exit_status read from the JSON, each 0, git commit a6cb5e3e dirty false: artifacts/receipts/arb-ruff-80097161d1d84437bebba862016e60a0.json, artifacts/receipts/arb-step-typecheck-54923b9952474fc6b68f10ef5c572b39.json, artifacts/receipts/arb-step-unittest-e80f0c3971b04833b94202e72f2044ad.json (9844 tests), artifacts/receipts/arb-step-mkdocs-abd1f4d4efa445568e3d2f730c548f06.json, artifacts/receipts/arb-step-coverage-9899a45629b74ee2adf67d72fb01c0c8.json.
GHI #972 close comment (2026-09-07T13:33:33Z) carries the seven-case verification table; GHI #951 close comment (2026-09-07T13:51:14Z) carries the before/after artifact and the cause-to-test table.

## Settled Rulings

789 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
