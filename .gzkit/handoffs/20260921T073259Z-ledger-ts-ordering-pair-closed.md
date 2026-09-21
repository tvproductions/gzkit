---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-21T07:32:59Z'
agent: claude-code
session_id: c8bf04f5-d0b7-4cba-8ddc-cfd06c1ff793
continues_from: .gzkit/handoffs/20260921T010935Z-qc-gate-cost-measured-instrumentation-ruled.md
---

## Current State Summary

The ledger's two ts-ordering defects were both closed and pushed: GHI #1075 (merge driver refused an additive ts-ordered insertion) at a6ab472b0, and GHI #1074 (ts stamped outside append's lock) at 51999d357. The session opened on /git-sync, which blocked on a real ledger rebase conflict the merge driver refused; the operator authorized a one-time union outside a gz command, and that unblocked sync is what exposed both defects. HEAD is bbcadab04, level with origin/main, clean tree, gz check green at real exit 0. The prior chain's ruled-and-parked option A gate instrumentation was NOT touched and is still unimplemented.

## Important Context

WHY THE UNION WAS HAND-RESOLVED, AND WHAT IT COST. The driver refused a conflict whose two sides had only ADDED rows: upstream (cd8cddc58) held a ts-ordered backfill mid-file at line 15381, which broke the strict-prefix ancestry test. Its refusal message named causes that had not occurred. No gz verb could resolve that shape, and re-invoking the driver with the common prefix as ancestor would have duplicated ~1615 shared rows, so AGENTS.md's ledger-only-through-gz rule and the git-sync skill's resolve-as-a-ts-ordered-union instruction could not both be satisfied. The operator ruled to apply the verified union. It was verified before writing (17017 rows, ts non-decreasing, every row of all three sides present) and gz validate --ledger confirmed it at exit 0. FRONT DELTAS. ghi triage: the open queue is 56; two were closed by this session, none filed. handoff system: this session resumed 20260920T160721Z, which the SessionStart caveat correctly flagged as stale behind 16 commits; three newer handoffs (20260921T002935Z, 005611Z, 010935Z) arrived with the pull and were read only at the point of chaining, not consumed as advice. adr/obpi campaign: untouched, no OBPI initiated, no ADR authored. new R&D: untouched. THE ADR-0.39.0 INTERVIEW WAS NOT ADVANCED. The resumed handoff advised finishing it (7 of 19 fields outstanding); the operator directed git-sync and then the two fixes instead, and no gz handoff decide ruling was ever booked against that document, so its advice stands unruled rather than set aside.

## Decisions Made

[operator] Authorized a one-time ledger write outside a gz command to resolve the rebase conflict, after being shown both conflicting rule texts verbatim and the three routing options; chose the verified union over rebase --skip (which would have destroyed the bookmark row) and over aborting to fix the driver first. [operator] Directed the driver defect be fixed (#1075), then the upstream cause (#1074). [operator] Asked why the stamp-and-embed idiom was not a function call; that duplication was the reason #1074 spanned twenty sites, so _timestamped_id and ledger_row replaced it rather than editing each site in place. [operator] Ruled the two carried-forward items be kept as notes on the closed GHIs rather than filed as new issues; the same was then done for #1075's retained no-dedup decision. [agent] Retained ledger_merge's no-deduplication rule unchanged, having no witness to overturn documented doctrine. [agent] Did not add a mechanical fence against a future constructor stating a ts; recommended instead of built, to hold scope.

## Immediate Next Steps

1. Rule on the two notes now parked on closed issues. #1074 [settled]'s note asks whether to build the missing fence (a tests/governance audit asserting no production constructor reaching Ledger.append states a ts, with an allowlist; test_subprocess_errors_replace.py is the precedent shape) and whether agent-insights.jsonl and corpus/*.jsonl claim the ledger's ordering invariant at all — that answer decides whether their three construction-time stamps are a defect or correct. #1075 [settled]'s note asks whether byte-identical additions present in both sides should be deduplicated. 2. The prior chain's option A gate instrumentation is still unimplemented and still invisible to every queue; it has an operator ruling and this chain as its only destination. Read src/gzkit/check_fingerprint.py first. 3. Decide the ADR-0.39.0 config-surface interview: finish the 7 outstanding fields, or book a ruling that sets the advice aside. It has now survived two sessions unruled. 4. Verify or drop the carried claim that the pre-commit hook chain runs no unit tier while the git-sync skill says it does. This session bumped that skill to 1.4.0 for an unrelated reason and did not touch the claim.

## Pending Work / Open Loops

CLOSED WITH NOTES, NOT FULLY SETTLED. GHI #1074 [settled] and GHI #1075 [settled] are both closed against real commits, but each carries a Carried forward comment holding a doctrine question only the operator can answer. Those questions are deliberately not issues, per the operator's ruling, so they live only on closed issues and in the insights store next_action fields — the longest-lived place a stale item hides. RULED AND PARKED IN THIS CHAIN, STILL UNIMPLEMENTED. The option A gate instrumentation from the previous handoff. Untouched by this session. CARRIED, STILL UNROUTED. The pre-commit-hook-runs-no-unit-tier claim against the git-sync skill's Red Flags table, and the Settled Rulings pointer count rendered before a document's own rulings are booked. DEFERRED BY RULING, NOT CLOSED. GHI #1069, open, two implementation choices unruled. NOT ADVANCED. The ADR-0.39.0 interview, 7 of 19 fields outstanding, its advising handoff never ruled on.

## Verification Checklist

Ran and observed, not inferred: uv run gz validate --ledger on the resolved union -> All validations passed, real exit 0, 17017 rows. uv run gz ledger merge-driver replayed against the incident's own three stage files after the #1075 fix -> real exit 0, output byte-identical (cmp clean) to the operator-authorized union. Both #1074 ordering tests observed FAILING against pre-fix code on genuine descending pairs before the fix landed, which is the control its closure contract required. uv run gz test -> Ran 10627 tests in 84.151s, OK (skipped=4), real exit 0. uv run gz check -> All checks passed, real exit 0, after an intermediate run failed Lint and Format because the agent had formatted src/gzkit only and not tests/. Old-versus-new duplication behaviour and the validator's silence on a duplicated row were both measured against the extracted pre-fix module rather than asserted. NOT VERIFIED: that the sibling stores' construction-time stamps are a defect; that no mechanical fence is needed; the carried pre-commit-tier claim.

## Evidence / Artifacts

Commits, all pushed, HEAD bbcadab04 level with origin/main: 040ebd676 (rebased ledger union plus the session-exit bookmark, exactly one added ledger row), 252043484 (insights), a6ab472b0 (fix(ledger): merge an additive ts-ordered insertion, GHI #1075; 12 files), 2bd69bb3c (insights), 51999d357 (fix(ledger): fix ts under the write lock, not at construction, GHI #1074; 7 files, 212 insertions), bbcadab04 (insights). Issues: GHI #1075 closed with disposition fixed plus a Carried forward note; GHI #1074 closed with disposition fixed plus a Carried forward note; cross-link comments posted at authoring time on #1074, #973. Source: src/gzkit/ledger_merge.py (_additions, _placed replacing _is_prefix), src/gzkit/ledger.py (ledger_row, the in-lock stamp, append and LedgerEvent docstrings), src/gzkit/ledger_events.py (_timestamped_id), src/gzkit/governance/events.py, src/gzkit/ontology/work.py, src/gzkit/commands/task.py, src/gzkit/commands/obpi_complete_adversarial.py. Tests: tests/test_ledger_merge.py (4 new), tests/test_ledger_transaction_boundary.py::TestTsIsFixedUnderTheWriteLock (3 new). Skill: .gzkit/skills/git-sync/SKILL.md 1.3.1 to 1.4.0, mirrors regenerated via gz agent sync control-surfaces and verified at parity. Docs: docs/user/manpages/ledger-merge-driver.md, docs/user/runbook.md, docs/governance/governance_runbook.md. Insights: four records under scopes gzkit.ledger_merge and gzkit.ledger.

## Settled Rulings

1015 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
