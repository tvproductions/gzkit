---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-06T21:43:07Z'
agent: claude-code
session_id: 10884427-f590-42f3-a3dc-3c0be043c793
continues_from: .gzkit/handoffs/20260906T203907Z-611-primitive-landed-live-corrections-held.md
---

## Current State Summary

Corrective pass on the four remaining gaps the operator's review of 47214176 reproduced, landed as 13771720 on main and pushed. The ahead/behind count against origin/main reads 0 0. Full quality gate exit 0; 9687 tests. ARB receipt exit_status read directly from the receipt JSON, each 0: arb-ruff-65f1f339142d43ed828039939fed2276, arb-step-typecheck-c93b4d2c1ecc4fb98585a6e23723bab2, arb-step-unittest-6e034343c7ec45afbb45e9eea34a9101.

What landed, one line each: (1) the airlock override producer's three fields are declared on both contracts and the static producer audit now follows a same-module helper return and an update() merge, with its blind spots enumerated in its own docstring; (2) nine array properties gained an items declaration — the review named four, five more were the same defect uncounted — fenced as a declaration-coherence property rather than nine verdicts; (3) the correction reader no longer stringifies, so null/number/bool/object attribution and a numeric subject_id are inert instead of state-changing, the factory rejects whitespace-only content on all five fields, and the ledger validator now enforces the three cross-row shapes the correct verb refuses; (4) state, evidence and history are three named readings on the reader boundary, with the two lock-release consumers moved to evidence and the two reconciliation readers reached at all for the first time; (5) the contradictory baseline prose is gone from both distributed copies.

NO LIVE LEDGER ROW WAS CORRECTED. The hold stands, unchanged from the predecessor handoff. The never-fired baseline is still 11 of 11 — nothing drained, nothing raised.

## Important Context

The four defects share ONE shape and it is worth carrying forward: a fence that reads the wrong SURFACE reports green while the defect it names is live. The producer audit scanned call sites and the payload was built in a helper. The committed-row fence read history and the producer had never fired. The reader-parity matrix ran on one field and the class had nine. The corrected stream became the default and two of the four affected consumers never touch the Ledger class at all. In each case the green was true about what was measured and silent about what mattered.

The live-versus-evidence distinction is the one most likely to be re-collapsed by a future reader. A void correction says a row records something that was NEVER THE CASE; a discharged one says it was TRUE when written and its condition later ended. The default reader drops both, and that default is deliberate — netting per call site fails OPEN, so a consumer written next year is correction-blind unless its author remembers. But the live reading is the NARROWEST, so the flip could only ever mis-serve in one direction: an evidence consumer silently loses discharged rows. That is exactly what happened to the handoff-archive lock-path reader.

The new public tolerant reader's tolerance is load-bearing, not incidental: the Ledger class validates every row through its event model, so one malformed line aborts the read — correct for a governance command, wrong inside a pipeline gate or commit hook where an exception blocks all work rather than reporting a finding. That is why the reconciliation readers parse the JSONL themselves, and why the fix was to give them a corrected tolerant reader rather than to route them through the class.

Two project fences caught this session's work and both were right. The import-boundary ratchet refused a cross-package private import and its own message named the correct fix — promote the symbol, do not widen the shrink-only roster. The tautological-test audit refused two prose-grep tests, correctly per the test policy's discriminator; the mirror-identity check one of them attempted is already covered by the distribution validator, which walks the packaged chores tree.

The harness asked for a Claude-Session commit trailer. The task-discovery rule closes the trailer set to Task, Ceremony and Eval-feedback-source, and says to strip a harness-injected session trailer. Repo canon was followed; expect the same conflict next session.

## Decisions Made

- [operator-ruled] All live corrections stay on hold (verbatim: "Keep **all live corrections on hold**."; "No live correction is authorized by this prompt. Stop after the correction pass."). No ledger row was corrected; the three dry-run targets carried on the predecessor handoff are untouched.
- [operator-ruled] The baseline may not grow through recovery prose (verbatim: "Do not authorize baseline growth through recovery prose or apply a live correction to clear a gate."). Both distributed copies now name only the two recoveries that exist — wire the producer, or retire the declaration — and say a raise is an operator ruling.
- [operator-ruled] Evidence is per-counterexample, never an aggregate (verbatim: "Do not replace that evidence with a passing aggregate suite."). Each item carries its own failing test and its own before/after observation; the aggregate gate is reported alongside, never instead.
- [operator-ruled] Direct repair through GHI workflows; 611 stays open; no ADR/OBPI work (verbatim: "Use the matching GHI workflows for direct repair. Preserve ledger history, keep #611 open, and do not initiate ADR/OBPI work."). Routed as a direct fix; no OBPI machinery was engaged and no lock was claimed.
- [operator-ruled] The static audit's limits stay explicit (verbatim: "A helper-produced payload falling outside its scan does not discharge a known producer defect."). The producer audit now states in its docstring that a zero-finding run is evidence of absence only within the shapes it reads, and enumerates the five it cannot.
- [agent-chose] Repaired nine array declarations, not the four named. The ghi_summary, red_team_challenges_fired, inspection_scope, test_names and set_aside properties carried the identical defect and were uncounted. Fenced as a declaration property so the class cannot recur; mutation-checked three ways, each killed 1 / survived 0 / invalid 0 / inconclusive 0.
- [agent-chose] Fixed the bool-coercion disagreement the new matrix surfaced. Pydantic lax mode coerces the string yes to True where the schema declares boolean and refuses it. Routed direct-fix (one module, 512 precedent commits, in-flight); six fields made strict, measured at zero affected committed rows first.
- [agent-chose] Implemented the conservative EVIDENCE reading for a discharged reconciliation receipt, and surfaced the semantic choice rather than ruling on it. Recorded with a recommendation in the new consumer-inventory doctrine page. Widening the gate later is safe; discovering a silently narrowed one is not.
- [agent-chose] Promoted the tolerant reader to a public name when the import-boundary ratchet refused the private cross-package reach, rather than adding the edge to the shrink-only roster.
- [agent-chose] Deleted two prose-grep tests the tautological-test audit flagged rather than waiving it, and left the ratchet fenced by behavior tests over the re-baseline path.
- [agent-chose] Decomposed the payload-key scanner when xenon refused rank D, rather than suppressing the complexity ceiling.

## Immediate Next Steps

1. Rule on the three live corrections for GHI #611, unchanged and still held from the predecessor handoff. Re-derive each with a dry run before applying; do not trust any tuple transcribed into a handoff. They are, per the issue's newest comment: (a) a pipeline_launched row on OBPI-0.35.0-08-remember-post-append-advisory to void / agent-error (the IRON LAW un-start, GHI #930); (b) and (c) two task_blocked rows on TASK-0.35.0-08-05-01 and TASK-0.35.0-08-06-01 to discharged / condition-resolved.
2. If (a) is approved, decide separately whether the OBPI-0.35.0-08 Layer-1 brief frontmatter also moves. Voiding the launch returns Layer 2 to pending while the frontmatter still reads status Active. That is a separate act and the operator's call.
3. Rule on the unresolved semantic choice this session surfaced rather than decided: what a discharged disposition means on a reconciliation receipt. The recommendation and its three reasons are in the new consumer-inventory doctrine page. Implemented conservatively; a ruling either confirms it or widens the gate.
4. Close GHI #611 and GHI #930 together once the corrections land — 930 was folded into 611 by operator ruling 2026-09-02. Both would close against cbbdbb20, 47214176 and 13771720 plus whatever corrections are applied. Applying correction (a) also drains the correction event type from the never-fired disclosure, dropping that baseline from 11 to 10.
5. Then resume the campaign queue in the order carried forward: 894, 939, 922, 921, 815, 933, 953, 952, 951, 767, 766, with 972 and 973 also queued.

## Pending Work / Open Loops

- GHI #611 stays OPEN and its three live corrections remain unapplied. Nothing in this session touched them.
- GHI #930 stays OPEN, folded into GHI #611 by operator ruling 2026-09-02; it closes with 611.
- The consumer classification in the new doctrine page is a READING, not a mechanically enforced partition. The four repaired consumers are pinned by tests; a fifth taking the wrong stream is not caught. The default is chosen to make that mistake the safe one, never impossible. Reclassify on an observed instance.
- The producer audit resolves helpers ONE level, same module, by name. Five shapes stay invisible and are named in its docstring: a runtime-computed key, a kwargs spread, a cross-module helper, a helper reached through a second helper, and a dict built by comprehension. It accompanies the committed-row fence; neither subsumes the other.
- The commit-hook TASK-trailer reader still parses the ledger JSONL itself instead of using the new public tolerant reader. It applies the live netting correctly, so this is duplication rather than a defect; refactoring a commit-hook path was out of this pass's scope.
- The spec-test-code drift advisory reports 706 unlinked REQs and 10 unjustified code changes. Advisory, does not affect exit code, and unchanged in character by this session.

## Verification Checklist

Run each and read its own exit status, never a shell aggregate:

    uv run gz check
    uv run gz validate --ledger
    uv run gz validate --producer-fields
    uv run python -m unittest tests.test_ledger_corrections
    uv run python -m unittest tests.test_ledger_correction_consumers
    uv run python -m unittest tests.governance.test_ledger_reader_parity
    uv run python -m unittest tests.chores.test_ledger_vocabulary_inertness
    uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py
    uv run gz obpi lock list
    git rev-list --left-right --count origin/main...HEAD

Expected at 13771720: quality gate exit 0 with 9687 tests; ledger and producer-fields validation exit 0; test counts 70, 11, 19 and 4 respectively; the inertness chore reporting never-fired 11 against baseline 11; no active locks; ahead/behind 0 0.

Read ARB receipt exit_status from the receipt JSON directly. Do not pipe a verifier into a filter — the verifier-pipe-gate hook refuses it, and the reason is that the status read back would be the filter's.

## Evidence / Artifacts

Commit 13771720 — 18 files, 1722 insertions.

Source repaired:
- `src/gzkit/ledger_corrections.py`
- `src/gzkit/ledger.py`
- `src/gzkit/validate_pkg/ledger_check.py`
- `src/gzkit/events.py`
- `src/gzkit/schemas/ledger.json`
- `src/gzkit/governance/trust_audits/events.py`
- `src/gzkit/handoff_archive.py`
- `src/gzkit/governance/trust_audits/lock_exchange_coupling.py`
- `src/gzkit/pipeline_runtime.py`
- `src/gzkit/commands/obpi_complete.py`
- `src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py`
- `.gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py`

Tests (70, 11 new, 19, 4 new):
- `tests/test_ledger_corrections.py`
- `tests/test_ledger_correction_consumers.py`
- `tests/governance/test_ledger_reader_parity.py`
- `tests/chores/test_ledger_vocabulary_inertness.py`

Doctrine authored — inventory, classification, and the unresolved semantic choice:
- `docs/governance/ledger-correction-consumers.md`

Receipts, exit_status read from the JSON, each 0:
- `artifacts/receipts/arb-ruff-65f1f339142d43ed828039939fed2276.json`
- `artifacts/receipts/arb-step-typecheck-c93b4d2c1ecc4fb98585a6e23723bab2.json`
- `artifacts/receipts/arb-step-unittest-6e034343c7ec45afbb45e9eea34a9101.json`

Course correction recorded before the work:
- `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

775 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
