---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-20T14:42:45Z'
agent: claude-code
session_id: 6bd39832-17e5-4522-baa3-7d1b0f6ed594
continues_from: .gzkit/handoffs/20261120T112814Z-rp12-o4-task2-built.md
---

## Current State Summary

RP-12 O4 task 2 (the list of discrepancies) is built and its independent review answered. CI, red at 0bfe68f1c on a hexagon boundary (gzkit.cli.parser_wp_discrepancy importing gzkit.events), was repaired in d03044679 and went green. Four reviews ran: spec (CONFIRMED, two findings), quality (five findings), and, by the operator's selection, a third review split in two over the tests and the schema (eleven findings). Every finding is answered in its own commit with its witness run, and ruling 182 was booked and implemented. Task 2 awaits the operator's word on whether the review is complete before task 3 opens.

## Important Context

Safe mode is open (contract docs/governance/harbor-pilotage-candidate-2026-10-15.md); every act is one commit with Task: TASK-rnd-repair-work-organization. The gh issue reader is now one function, gzkit.commands.reference_checker.gh_issue_read, over gh api --include: 404/410 and a pull request read missing, no status line reads unanswered (ruling 182); gh_issue_state keeps its signature for handoff and status callers. The ledger validator enforces type, min_length, named, min, items and enum but no pattern keyword (insight recorded 2026-11-20T14:42:13). Review subagents hit a 15-turn limit; brief them narrowly and tell them to report by turn 12.

## Decisions Made

- [operator-ruled] Handoff 20261120T112814Z resumed (verbatim: "proceed. CI repair first, then reviews.").
- [operator-ruled] Ruling 182, an issue the API says does not exist is refused at 3 and only an unanswered gh call exits 2 (verbatim: "A: Split the cases (Rec.)").
- [operator-ruled] A third review of task 2's tests and schema (verbatim: "A: Dispatch it now (Rec.)").
- [agent-chose] The discrepancy parser spells its two closed sets out, as the sibling wp parsers do, held to the Literals by DiscrepancyChoicesTests, rather than importing gzkit.events across the hexagon boundary.
- [agent-chose] The third review ran as two reviewers, one over the writer tests and schema and one over the CLI and probe tests, to fit the turn budget.
- [agent-chose] The schema states the id patterns for agreement though the validator does not enforce pattern; the enforcement gap is recorded, not widened into this task.

## Immediate Next Steps

1. Put this handoff to the operator and book the ruling with uv run gz handoff decide; renew the mx-session lease through the gz-mx skill if it is near expiry.
2. Read CI on the synced HEAD with gh run list --workflow CI --limit 3; if check is red, repair it first.
3. Ask the operator whether task 2's review is complete or wants a re-review of the repairs (commits e2aebd8a5 to 1f547f7e2), as O4 task 1 took a spec re-review of its repairs.
4. Then open O4 task 3, the carry (rulings 30, 142, 171): read gzkit.order_ledger.hung_tag_refusal, _check_accepted, _check_closed and gzkit.work_package_ledger._check_repair_close, and put task 3's opening questions to the operator one at a time.

## Pending Work / Open Loops

- On the operator's word, file GHIs through ghi-author for: gz validate --ledger enforcing no pattern keyword (insight 2026-11-20T14:42:13); the ten off-by-default ty rules still reporting 2,612 findings (missing-type-argument 738, missing-override-decorator 645, truthiness-test-of-none-union 557, dynamic-function-decorator-return 316, unsound-return 245, unsound-assignment 60, redundant-condition-strict 43, blanket-ignore-comment 6, unsound-yield 1, possibly-unresolved-reference 1); pre-commit language system renamed unsupported and pre-commit-hooks pinned at v5.0.0; scripts/session_orientation.py reporting ahead/behind from cached refs without a fetch.
- Shift turnover: gz wp tag show --all reported no tag issued and gz wp runs no package in flight at this session's start; gz obpi lock list reported no active locks. Findings awaiting buy-back were not re-read this session; the contract's List of discrepancies stands in for the buy-back record.
- Commit 10a7f5f99 carries the author name Jeffry Babb from an earlier sync (noreply email, no PII leak); not rewritten, since that needs a force push.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.
- gh run list --workflow CI --limit 3: check jobs green on the synced HEAD (full-strength-report fails as a standing report on every run).
- uv run -m unittest tests.test_discrepancies tests.commands.test_wp_discrepancy tests.test_ledger_producer_probe tests.commands.test_reference_checker tests.commands.test_insights_recurrence tests.test_schemas passes.
- uv run gz validate --hexagon-dependencies --hexagon-tests --ledger exits 0.

## Evidence / Artifacts

- `src/gzkit/mx/discrepancies.py`
- `src/gzkit/commands/wp_discrepancy.py`
- `src/gzkit/cli/parser_wp_discrepancy.py`
- `src/gzkit/commands/reference_checker.py`
- `src/gzkit/commands/insights.py`
- `src/gzkit/schemas/ledger.json`
- `src/gzkit/ledger_producer_probe.py`
- `tests/test_discrepancies.py`
- `tests/commands/test_wp_discrepancy.py`
- `tests/test_ledger_producer_probe.py`
- `docs/governance/harbor-ro12-contractor-kit.md`
- Commits: d03044679 (CI repair), e2aebd8a5, b476f63b1, dfb9b0900, b2951ee2e, 457e37806, 1eb0adbf5 (first reviews), a5cd6bae2 and a7f77b70d (ruling 182), f52ac7113, 9db185765, b5d68b6a7, 04f79e67a, 1f547f7e2 (third review).

## Settled Rulings

2383 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
