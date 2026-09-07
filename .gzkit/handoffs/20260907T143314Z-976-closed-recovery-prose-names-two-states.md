---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-07T14:33:14Z'
agent: claude-code
session_id: ef5296e8-5d8e-4932-aeb6-4f11141ecf6d
continues_from: .gzkit/handoffs/20260907T135221Z-972-corrected-951-closed-894-awaits-ruling.md
---

## Current State Summary

GHI #976 closed against c8cc88ac (receipts ca3ec4c8), both pushed, origin/main 0 0. The loader's growth refusal (src/gzkit/content/ownership.py, lifted into _refuse_grown_or_flipped_span to hold load_declaration at xenon rank C) now lists every unowned section with its live span, names the two states behind one arithmetic -- a section hand-flipped to 'unowned' outside the governed path, or an unowned section that grew -- says which verb can act in which state, and prescribes a recovery for each: git checkout -- <tracked declaration> then gz content unown for an edited map; shrink, or gz content remember every uncovered line then gz content own, for a grown section. gz content unown --help attributes the decrease-or-equal path to gz content own and states gz content remember never touches the declaration; docs/user/manpages/content.md mirrors both with the captured refusal. Both recoveries were driven through the real command path in an isolated git-initialised copy before editing (flipped: restore -> loads -> unown exit 0, floor 6005 -> 7586; grown: own refused naming 4 lines -> 4 captures -> own exit 0, floor 6005 -> 5882). Validation order, the ratchet and the transition set are unchanged. Operator ruling booked on the resumed handoff (proceed, session ef5296e8).

## Important Context

QUEUE NOTES CORRECTED (operator, 2026-09-07): #921 and #922 remain OPEN for delivery; OBPI-0.35.0-12-rules-corpus-onboarding and OBPI-0.35.0-11-corpus-shape-witness are already authored (gz adr status lists both with no completion proof) -- landing them is OBPI work and under the IRON LAW only the operator initiates it. #810's eligibility remains incompletely assessed. #767 and #766 retain their separately recorded dispositions (parked behind ADR-pool.primary-source-corroboration; #766 blocked by #767). Exactly three live corrections remain held on #611 (#930 folded in); none applied. #894 still awaits its ruling. Sibling family NOT folded into #976 (operator scoped the pass to the two named surfaces): the witness-chain refusals in ownership.py (_refuse_unwitnessed_section_map, _refuse_wrong_direction_witness, _refuse_non_migration_reanchor, _refuse_unattested_map_change, and the resolving/type/surface/floor-mismatch arms of load_declaration) name gz content unown or own for states the loader refuses before either verb can act, several offering a declaration hand-edit; recorded 2026-09-07T14:18:12Z in .gzkit/insights/agent-insights.jsonl (scope content-ownership, type defect) with the prescribed repair shape. Receipts for c8cc88ac read dirty TRUE: the only unstaged paths at mint time were the insights record and the ledger's handoff_resume_decided row, both carried by ca3ec4c8; no test count was transcribed because the receipt tails carry none. #815 re-measured this session: gz validate --instructions-files-budget reports AGENTS.md 47851 B against the codex cap 65536 B, whole surface delivered -- the observed breach no longer reproduces and #962 is CLOSED 2026-09-05; #815 is REOPENED and its standing guidance was superseded on-thread, so its disposition needs the full thread read before it is drawn.

## Decisions Made

- [operator-ruled] #976 selected for direct repair for this cleanup-sweep pass (verbatim: 'For this cleanup-sweep pass, **I explicitly select #976 for direct repair**.'); #972 and #951 accepted as complete; the '2 tests' annotation stays disclosed, not rewritten.
- [operator-ruled] Repair scope: both named surfaces, prose-and-coupled-verification only; reproduce in disposable fixtures first; verify each recovery through the real command path; for an invalid map change use the established governed recovery, never a hand-edit or a command the loader refuses before it can act (verbatim: 'Do not weaken ownership validation, raise the ratchet, or introduce another transition mechanism.').
- [operator-ruled] No ADR/OBPI machinery, no other GHI repair; stop after #976 is closed and synced.
- [agent-chose] The restore incantation is git checkout -- <tracked declaration>: the one recovery shape gzkit already prescribes for a torn governed artifact (foundation/sunset_migrate.py) and the committed copy is what TestCommittedDeclarationLoadsCleanly proves loadable on every gz check; own cannot recover a flip because the on-disk map is not the one its floor_event_id witnesses (observed, exit 1).
- [agent-chose] The sibling witness-chain refusals were tracked via gz insights remember rather than repaired, honouring the operator's scoping; they are the same class and named as an unclaimed row in #976's cause-to-test table.
- [agent-chose] Lifted the refusal into a helper only because the pre-commit xenon hook refused rank D; no other code moved.

## Immediate Next Steps

1. Re-establish repository truth BEFORE acting: git status --short, git log --oneline -6, git rev-list --left-right --count origin/main...HEAD, uv run gz obpi lock list. This handoff ADVISES; it does not authorize.
2. Re-derive the open queue with the refusing census form (gh-cli.md 0.5.1): gh api -X GET search/issues -f q='repo:tvproductions/gzkit is:issue is:open' --jq 'if .incomplete_results then error("incomplete_results: no count obtained") else .total_count end'. Measured this session: 39 before #976 [settled] closed.
3. Obtain the operator's ruling before drawing work and book it with uv run gz handoff decide --handoff <this file> --session-id <id> --decision proceed --operator-text "<their exact words>".
4. Next candidate, prerequisites assessed: the sibling ownership-refusal family needs a GHI first -- when the operator draws it, author via /ghi-author from the 2026-09-07T14:18:12Z insights record, then repair as #976 [settled] did (fixture per state, real command path). #815: re-read the full thread (guidance superseded on-thread; observed breach no longer reproduces at 47851 B / 65536 B; #962 [settled] closed) before choosing a disposition. #939 is blocked on an operator ruling between two remedies. #973 is coupled to #611's held corrections.
5. #894 needs a RULING before it can be drawn (the _is_named relocation versus OBPI-0.35.0-08's read-only declaration); separate from held correction (a) on #611 and from any brief amendment.
6. #921 and #922 remain open for delivery; OBPI-0.35.0-12 and OBPI-0.35.0-11 are already authored -- do not re-author; landing them is operator-initiated OBPI work. #810's eligibility remains incompletely assessed. #767 and #766 keep their recorded dispositions. The three live corrections on #611 (#930 folded in) remain the operator's to rule on; apply none.
7. When the operator draws it, route the ghi-triage census member through /ghi-author (insights record 2026-09-07T12:57:26Z, scope ghi-triage).

## Pending Work / Open Loops

- Sibling ownership-refusal family (insights 2026-09-07T14:18:12Z, scope content-ownership): tracked, no GHI yet.
- GHI #611 OPEN with three live corrections held; #930 OPEN, folded in. Untouched this session.
- GHI #894 OPEN, awaiting an operator ruling.
- GHI #921 and #922 OPEN for delivery; OBPI-0.35.0-12 and -11 authored, unlanded.
- GHI #810 OPEN, eligibility incompletely assessed.
- GHI #767 OPEN (parked); GHI #766 OPEN (blocked by #767).
- GHI #815 OPEN/REOPENED; observed breach no longer reproduces; full-thread read required before disposition.
- ghi-triage census defect tracked only in insights (2026-09-07T12:57:26Z); no GHI yet.
- Claude-Session trailer conflict between the harness reminder and task-discovery.md remains standing.

## Verification Checklist

Run each and read its own exit status, never a shell aggregate:

    uv run gz check
    uv run python -m unittest tests.commands.test_content_own tests.content.test_ownership
    uv run gz content unown --help
    gh issue view 976 --json state
    gh api -X GET search/issues -f q='repo:tvproductions/gzkit is:issue is:open' --jq 'if .incomplete_results then error("incomplete_results: no count obtained") else .total_count end'
    git rev-list --left-right --count origin/main...HEAD

Expected at ca3ec4c8: quality gate exit 0; the two suites OK; the unown help names gz content own as the decrease-or-equal path and says gz content remember never touches the declaration; #976 CLOSED; a total or a jq error, never a page count; ahead/behind 0 0. Read ARB receipt exit_status from the receipt JSON directly.

## Evidence / Artifacts

Commit c8cc88ac -- fix(content-ownership): growth refusal and unown help each prescribe a path that acts (GHI #976): src/gzkit/content/ownership.py, src/gzkit/commands/content/__init__.py, docs/user/manpages/content.md, tests/commands/test_content_own.py, .gzkit/ledger.jsonl (session_exit_bookmark_skipped).
Commit ca3ec4c8 -- receipts, exit_status read from the JSON, each 0, git commit c8cc88ac dirty true (insights + ledger rows only): artifacts/receipts/arb-ruff-997abecd5f2a4c618946a6d757770f6b.json, artifacts/receipts/arb-step-typecheck-62e4e215e46842c3a82f04010aaaa6af.json, artifacts/receipts/arb-step-unittest-02e10a268c3a4834a3180b0952115781.json, artifacts/receipts/arb-step-mkdocs-314aae76759c4a38b5db8500bdc3b9e9.json, artifacts/receipts/arb-step-coverage-b57141c14946474ebf26ef639177f24c.json; .gzkit/insights/agent-insights.jsonl; .gzkit/ledger.jsonl (handoff_resume_decided).
GHI #976 close comment (2026-09-07T14:30:47Z) carries the re-derived preconditions, before/after observed output and the cause-to-test table with the unclaimed sibling row.

## Settled Rulings

794 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
