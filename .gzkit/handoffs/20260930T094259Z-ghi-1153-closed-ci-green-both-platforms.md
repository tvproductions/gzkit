---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-30T09:42:59Z'
agent: claude-code
session_id: 19812a39-411d-4c2a-91b5-5fffcfc3383b
continues_from: .gzkit/handoffs/20260930T031736Z-arb-red-receipts-and-annotation-fix.md
---

## Current State Summary

Resumed the arb-red handoff; the operator ruled 'close 1153'. Fixed and closed GHI #1153 (9f9403b61): gz arb red --commit keeps the whole-hunk revert first, and a hunk whose revert cannot be graded on a green baseline is re-mutated one guard statement at a time (unit: statement); a hunk with no guard statement is a declaration row outside the verdict. Re-running 73aaab093 and 92f64debc now grades undriven (was inconclusive) and names three untested guards, recorded as insights. The push-time tautological-debt ratchet (232 vs ceiling 231) was drained in ab1db98bd, which also fixed a $schema mismatch in the complexity-thresholds JSON Schema. Windows CI had been failing since before this session; the cause was CRLF checkouts not matching LF mutation text, fixed in 576a515b2. CI run 36695663620 is green on ubuntu and windows. main is 0/0 with origin before this handoff's sync.

## Important Context

The commit witness now writes each production file's blob text into its worktree before sweeping, because mutations are built from git show text (LF) and a checkout without eol=lf is CRLF on Windows; gzkit's own .gitattributes pins eol=lf, fixture repos and adopter repos may not. HunkWitness has a unit field (hunk | statement | declaration); declaration rows never enter the aggregate verdict; the receipt schema carries unit as optional. A statement revert that raises still reads inconclusive by design (GHI #963 classification is run-wide, so one ERROR in the run makes the whole mutant inconclusive). The tautological-debt ceiling in data/tautological_test_debt_target.json falls daily and gz check fails on breach, so a push can go red with no code change. No gz verb emits chore_decommission_processed; the drain is measured by the scan only. A pasted CI diagnosis blaming NCSurface.md was wrong: that path is a test fixture's temp directory and the message is advisory.

## Decisions Made

- [operator-ruled] Close GHI #1153 (verbatim: 'close 1153').
- [operator-ruled] Mutation unit for GHI #1153 is statement fallback (verbatim selection: 'Statement fallback (Recommended)').
- [agent-chose] Reported a hunk with no guard statement as a declaration row outside the aggregate, so a signature-only hunk does not force inconclusive; recorded as a contract amendment on the GHI before implementing.
- [agent-chose] Dropped the elif exclusion: replacing an elif branch with pass is a valid program and a real guard mutation.
- [agent-chose] Drained one tautological op by converting tests/complexity/test_thresholds.py's schema test into a behavior test, which surfaced and fixed the $schema mismatch.
- [agent-chose] Did not act on the pasted NCSurface.md diagnosis: its target file does not exist and the failing tests were the commit-witness CRLF defect.

## Immediate Next Steps

1. Ask the operator whether to draw the next ADR-0.35.0 OBPI; OBPI-0.35.0-10 also carries retention-scope REQs 08-10.
2. When OBPI-0.35.0-10 lands, add ADR-0.0.33's six anti-pattern rows to the scorecard as a direct fix under GHI #799.
3. Ask the operator whether to add tests for the three undriven guards the witness found (73aaab093: ast.Attribute decorator branch, vararg/kwarg annotation drop; 92f64debc: seen-dedupe in validate_cmd.py).
4. Ask the operator how to close the chore_decommission_processed emitter gap: add an emitting verb or amend the chore to name the scan as the record.

## Pending Work / Open Loops

Three undriven guards and the missing chore_decommission_processed emitter are recorded only as insights in .gzkit/insights/agent-insights.jsonl (2026-09-30), not GHIs. GHI #799 open, waiting on OBPI-0.35.0-10. Tautological debt sits exactly at its ceiling (231) and the ceiling keeps falling, so the next push after a ceiling step fails gz check unless another op is drained. AGENTS.md exceeds its advisory instructions budget (gz-context-diet if wanted). Carried: ADR-pool.handoff-resume-assessment awaits promotion; #611 clause 4 and held item (a); #1149 and #1125 open; pool promotion-triage facility owed by ADR-pool.pool-management section 9; gz obpi precomplete has no manpage; GovZero docs cite AirlineOps-era ADR numbers.

## Verification Checklist

gh issue view 1153 (expect CLOSED); gh run view 36695663620 --json jobs (expect both check jobs success); uv run -m unittest tests.test_commit_witness tests.test_schemas tests.complexity.test_thresholds (expect OK); uv run gz arb red --commit 9f9403b61 (expect undriven with only the two disclosed survivors, lines 46-52 and 343-344); git rev-list --left-right --count origin/main...HEAD (expect 0 0); uv run gz check (expect exit 0).

## Evidence / Artifacts

Predecessor: `.gzkit/handoffs/20260930T031736Z-arb-red-receipts-and-annotation-fix.md`. GHI #1153 fix: `src/gzkit/commit_witness.py`, `tests/test_commit_witness.py`, `data/schemas/arb_red_commit_receipt.schema.json`, `docs/user/manpages/arb-red.md`, `.gzkit/skills/ghi-close/SKILL.md`. Debt drain: `tests/complexity/test_thresholds.py`, `src/gzkit/schemas/complexity_thresholds.json`. Insights: `.gzkit/insights/agent-insights.jsonl`.

## Settled Rulings

1223 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
