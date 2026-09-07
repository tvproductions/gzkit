---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-07T13:15:13Z'
agent: claude-code
session_id: 42d22ad1-3e28-4c81-bb38-6ab677307a26
continues_from: .gzkit/handoffs/20260906T214307Z-611-877-coherence-pass-landed-corrections-still-held.md
---

## Current State Summary

GHI #972 closed fixed against 5982340f (gh-cli.md 0.4.0 -> 0.5.0, new binding § Census queries) with the five ARB receipts in cedbd79f; both on origin/main, ahead/behind 0 0, full quality gate exit 0 across 60 steps, 9839 tests. Open queue measured 40 by `gh api -X GET search/issues -f q='repo:tvproductions/gzkit is:issue is:open' --jq '.total_count'` at 2026-09-07T13:15Z (incomplete_results false) — the default `gh issue list` page read 30 at the same moment and is NOT the queue. #946 had closed 2026-09-06T16:18Z, so #972's deferral was moot when re-derived. NO LIVE LEDGER ROW WAS CORRECTED; the hold on #611's three corrections stands unchanged. No OBPI machinery engaged, no lock claimed, no ADR touched.

## Important Context

Four predecessor handoffs in this chain (20260906T155304Z § Immediate Next Steps 2, and the three 2026-08-03 triage handoffs' Verification Checklists) carry `gh issue list --state open --json number --jq 'length'` as the way to re-derive or verify the open queue. That command counts a 30-row page, not the queue: measured 2026-09-07T12:51Z it returned 30 while the search total_count was 41. Those handoffs are PRESERVED UNEDITED as dated historical records; this handoff and its settled ruling are the correction, and gh-cli.md 0.5.0 § Census queries is the rule home. Read any count a handoff carries as a page unless it names its method. Row 51c is scored Judgment: the recommended commands were verified to return the complete result, which proves the guidance correct, not enforced — a census is a reading of the consumer's intent gzkit does not model, and the syntactic hook arm was rejected because `--limit 200` passes it and still truncates. The Claude-Session trailer conflict recurred exactly as the predecessor predicted: the harness reminder asked for the trailer, task-discovery.md 0.8.0+ closes the trailer set (operator verbatim 'never'); repo canon was followed and no trailer was authored. The code-surface member of the same class — ghi-triage's fetch() rendering 'N ranked of N open' from one --limit 100 page — is tracked in .gzkit/insights/agent-insights.jsonl (2026-09-07T12:57:26Z, scope ghi-triage), not repaired: the operator bounded this pass to #972.

## Decisions Made

- [operator-ruled] #972 drawn by explicit selection for direct repair; #977 is complete and stays closed (verbatim: "For this cleanup-sweep pass, I explicitly select #972 for direct repair. #977 is complete; do not reopen it."). Booked as handoff_resume_decided on the 20260906T214307Z handoff with steps 1-4 set aside.
- [operator-ruled] Census guidance must establish completeness (verbatim: "guidance for a whole-queue count or inventory must establish completeness, rather than count a silently capped page."; "An explicit `--limit` alone is insufficient. Replacing 30 with 200 merely moves the failure threshold."; "A capped prior-art search cannot support a claim that no matching issue exists without establishing completeness."). Landed as gh-cli.md 0.5.0 § Census queries.
- [operator-ruled] Enforcement assessed honestly (verbatim: "written guidance is not Mechanical merely because the recommended command works."). Row 51c scored Judgment, with the rejected Promotable arm named in its notes.
- [operator-ruled] Historical handoffs preserved; correction recorded through the governed mechanism (verbatim: "Preserve historical handoffs. Record the correction to their defective census instruction through the governed mechanism so future sessions receive the corrected guidance."). No handoff file was edited; this handoff seats the settled ruling.
- [operator-ruled] Scope held to #972 (verbatim: "Keep this bounded to #972. #951 remains open. The mutation-witness finding stays separately tracked. Do not reopen completed repairs, initiate ADR/OBPI machinery, or apply any of the three held live corrections.").
- [agent-chose] Bumped 0.4.0 -> 0.5.0 (minor) because a binding clause was added, matching the rule's own prior bump convention; the coupled version-history entry, Coverage Ledger version, row 51c and Summary recount landed in the same commit so the advisory-scorecard gate never saw an intermediate state.
- [agent-chose] Verified the prescribed methods against the live repo before documenting them (default page 30, --limit 10 -> 10, --limit 200 -> 41, search total_count 41 with incomplete_results false, --paginate 41) rather than transcribing the GHI body's 44, which was true on 2026-09-06 and is not the queue today.
- [agent-chose] Left the ghi-triage class member unrepaired and recorded it via gz insights remember with a /ghi-author next-action, rather than filing a GHI inside a pass the operator bounded to one issue.
- [agent-chose] Followed repo canon over the harness reminder on the Claude-Session trailer, and surfaced the conflict in the session report rather than resolving it silently.

## Immediate Next Steps

1. Re-establish repository truth BEFORE acting: `git status --short`, `git log --oneline -4`, `git rev-list --left-right --count origin/main...HEAD`, `uv run gz obpi lock list`. This handoff ADVISES; it does not authorize.
2. Re-derive the open queue by the search total (never a list page): `gh api -X GET search/issues -f q='repo:tvproductions/gzkit is:issue is:open' --jq '.total_count'`; refuse to book the figure if incomplete_results is true. Name the method beside the number.
3. Obtain the operator's ruling before drawing work and book it with `uv run gz handoff decide --handoff <this file> --session-id <id> --decision proceed --operator-text "<their exact words>"`.
4. Carried campaign-linked GHI order, states re-resolved at authoring time and recorded in the session report: 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766, with 973 queued. Re-resolve each with `gh issue view <N> --json state` before drawing; do not trust this list.
5. The three live corrections for GHI #611 (and #930 folded into it) remain the operator's to rule on; nothing here changed them.
6. When the operator draws it, route the ghi-triage census member through /ghi-author (insights record 2026-09-07T12:57:26Z, scope ghi-triage).

## Pending Work / Open Loops

- GHI #611 OPEN with its three live corrections still held; GHI #930 OPEN, folded into #611. Untouched this session.
- GHI #951 OPEN by operator instruction; the mutation-witness finding is tracked separately from this pass.
- ghi-triage fetch() census defect is tracked ONLY in .gzkit/insights/agent-insights.jsonl — no GHI yet; it needs one before repair.
- The 20260907T124952Z floor bookmark from the predecessor session was committed as-is in 5982340f (mechanical CHECKPOINT, never a surrender).
- Claude-Session trailer conflict between the harness reminder and task-discovery.md remains a standing conflict every session must resolve toward canon.

## Verification Checklist

Run each and read its own exit status, never a shell aggregate:

    uv run gz check
    uv run gz validate --advisory-scorecard --distribution --surfaces --documents --invariant-coherence
    uv run python -m unittest tests.commands.test_issue_cmd
    gh issue view 972 --json state
    gh api -X GET search/issues -f q='repo:tvproductions/gzkit is:issue is:open' --jq '.total_count'
    grep -c 'Census queries' .gzkit/rules/gh-cli.md .claude/rules/gh-cli.md src/gzkit/rules/gh-cli.md
    git rev-list --left-right --count origin/main...HEAD

Expected at cedbd79f: quality gate exit 0 (60 steps); 5 validate scopes pass; 25 tests OK; #972 CLOSED; total_count equal to the figure in this handoff's summary or lower as issues close (any 30 is a page, not a count); each of the three gh-cli.md copies reports 2 hits; ahead/behind 0 0. Read ARB receipt exit_status from the receipt JSON directly; never pipe a verifier into a filter.

## Evidence / Artifacts

Commit 5982340f — fix(gh-cli): census queries establish completeness, never count a page (GHI #972): .gzkit/rules/gh-cli.md, .claude/rules/gh-cli.md, src/gzkit/rules/gh-cli.md, .github/AGENTS.md, docs/design/adr/AGENTS.md, docs/governance/advisory-rules-audit.md, docs/governance/rule-version-history.md, .gzkit/insights/agent-insights.jsonl, .gzkit/ledger.jsonl (handoff_resume_decided + agent_sync_completed), .gzkit/handoffs/20260907T124952Z-session-exit-bookmark.md.
Commit cedbd79f — receipts, exit_status read from the JSON, each 0, git commit 5982340f dirty false: artifacts/receipts/arb-ruff-5774a22159cf4959a9cef578c2540a86.json, artifacts/receipts/arb-step-typecheck-b9d2cc00cc804c8eb60fdb03e7240be1.json, artifacts/receipts/arb-step-unittest-9e09a1e9601149ffb3e55b691b82946c.json (9839 tests, 4 skipped), artifacts/receipts/arb-step-mkdocs-7cd5a4d4457b408a953234bf94bbca6a.json, artifacts/receipts/arb-step-coverage-de6e5e4cb79f4ab5b6f3034505136f75.json.
GHI #972 close comment (2026-09-07T13:13:58Z) carries the reproduction and the cause-to-witness table.

## Settled Rulings

781 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
