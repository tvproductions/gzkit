# CHORE-LOG: failure-class-index

## 2026-10-10T06:28:08-05:00
- Status: PASS
- Chore: failure-class-index
- Title: Failure-Class Index (GHI recurrence chains)
- Lane: lite
- Version: 1.1.0
- Criteria Results:
  - [PASS] `uv run -m unittest tests/chores/test_failure_class_index.py -q` => rc=0 (0.07s) -- exit 0 == 0
  - [PASS] `uv run -m unittest tests.chores.test_failure_class_index.TestChains -q` => rc=0 (0.07s) -- exit 0 == 0
  - [PASS] `uv run -m unittest tests.chores.test_failure_class_index.TestRecurrenceDetection -q` => rc=0 (0.07s) -- exit 0 == 0
  - [PASS] `uv run gz validate --chores-layout` => rc=0 (0.41s) -- exit 0 == 0

```text
[uv run -m unittest tests/chores/test_failure_class_index.py -q] stderr:
----------------------------------------------------------------------
Ran 25 tests in 0.003s

OK
[uv run -m unittest tests.chores.test_failure_class_index.TestChains -q] stderr:
----------------------------------------------------------------------
Ran 4 tests in 0.000s

OK
[uv run -m unittest tests.chores.test_failure_class_index.TestRecurrenceDetection -q] stderr:
----------------------------------------------------------------------
Ran 5 tests in 0.000s

OK
[uv run gz validate --chores-layout] stdout:
Validated: chores_layout

✓ All validations passed (1 scopes).
```

## 2026-10-10 — maintenance visit C: snapshot, report, routing (step 5)

Snapshot: `gh issue list --state all --limit 2000` → 1184 records (max #1189; a first pass at
`--limit 1000` returned exactly 1000 and was discarded as a capped page, GHI #972). Written outside the
repo. Report `proofs/failure-class-index-2026-10-10.md`, telemetry `run-2026-10-10.json`: read 1184,
indexed 751, 165 declaring recurrence (22%), 114 chains, **19 with ≥ 3 authored diagnoses** (12 on
2026-08-08), deepest 13.

Against 2026-08-08: one family grew 3 → 13 (#677 … #803: gates and verbs that exit 0 while their own
output reports failure, or whose witness checks a marker rather than the act); one grew 5/7 → 6/8
(+#1084); **seven new families**, two large: #589 … #1152 (11: a verifier's exit status masked by a
pipe, a chain, an aggregate, or a missing receipt — the family the `verifier-pipe-gate` hook answers,
still producing instances on 2026-10-07) and #785 … #1027 (6: ARB and gate canon out of lockstep with
what runs). Smaller: Windows path and line-ending hazards (5), content-ownership prose prescribing a
refused step (4), handoff/receipt accumulation with no archive (3), task-envelope channels unused (3),
drift readers admitting witnessless entries (3), Stage-2 dispatch state in a Layer-3 marker (3), and
demo/replay running in the live checkout (3, newest: #1156, #1157).

Routing proposed, not performed: the #589 family and the #677 family are the two whose members are
still producing instances; both sit under the campaign's `doctrine-declared-without-mechanism` box
and each deserves a named row there rather than a fresh GHI per instance. The rest are recorded here
so the next run compares against this one instead of re-deriving.
