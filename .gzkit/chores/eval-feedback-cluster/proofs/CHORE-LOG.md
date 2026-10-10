# CHORE-LOG: eval-feedback-cluster

## 2026-05-03T19:22:43-05:00
- Status: PASS
- Chore: eval-feedback-cluster
- Title: Evaluation Feedback Clustering (ADR-0.0.26)
- Lane: medium
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q` => rc=0 (1.60s) -- exit 0 == 0
  - [PASS] `uv run gz validate --chores-layout` => rc=0 (1.36s) -- exit 0 == 0

```text
[uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q] stderr:
----------------------------------------------------------------------
Ran 10 tests in 1.138s

OK
[uv run gz validate --chores-layout] stdout:
Validated: chores_layout

✓ All validations passed (1 scopes).
```
## 2026-05-10T13:09:49-05:00
- Status: PASS
- Chore: eval-feedback-cluster
- Title: Evaluation Feedback Clustering (ADR-0.0.26)
- Lane: medium
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q` => rc=0 (2.45s) -- exit 0 == 0
  - [PASS] `uv run gz validate --chores-layout` => rc=0 (2.44s) -- exit 0 == 0

```text
[uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q] stderr:
----------------------------------------------------------------------
Ran 10 tests in 1.887s

OK
[uv run gz validate --chores-layout] stdout:
Validated: chores_layout

✓ All validations passed (1 scopes).
```
## 2026-06-29T21:53:45-05:00
- Status: PASS
- Chore: eval-feedback-cluster
- Title: Evaluation Feedback Clustering (ADR-0.0.26)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q` => rc=0 (0.33s) -- exit 0 == 0
  - [PASS] `uv run gz validate --chores-layout` => rc=0 (0.29s) -- exit 0 == 0

```text
[uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q] stderr:
----------------------------------------------------------------------
Ran 10 tests in 0.107s

OK
[uv run gz validate --chores-layout] stdout:
Validated: chores_layout

✓ All validations passed (1 scopes).
```
## 2026-07-07T06:19:24-05:00
- Status: PASS
- Chore: eval-feedback-cluster
- Title: Evaluation Feedback Clustering (ADR-0.0.26)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q` => rc=0 (0.37s) -- exit 0 == 0
  - [PASS] `uv run gz validate --chores-layout` => rc=0 (0.31s) -- exit 0 == 0

```text
[uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q] stderr:
----------------------------------------------------------------------
Ran 10 tests in 0.116s

OK
[uv run gz validate --chores-layout] stdout:
Validated: chores_layout

✓ All validations passed (1 scopes).
```
## 2026-07-31T19:12:04-05:00
- Status: PASS
- Chore: eval-feedback-cluster
- Title: Evaluation Feedback Clustering (ADR-0.0.26)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q` => rc=0 (0.35s) -- exit 0 == 0
  - [PASS] `uv run gz validate --chores-layout` => rc=0 (0.31s) -- exit 0 == 0

```text
[uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q] stderr:
----------------------------------------------------------------------
Ran 10 tests in 0.118s

OK
[uv run gz validate --chores-layout] stdout:
Validated: chores_layout

✓ All validations passed (1 scopes).
```
## 2026-10-10T06:28:09-05:00
- Status: PASS
- Chore: eval-feedback-cluster
- Title: Evaluation Feedback Clustering (ADR-0.0.26)
- Lane: lite
- Version: 1.1.0
- Criteria Results:
  - [PASS] `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q` => rc=0 (0.55s) -- exit 0 == 0
  - [PASS] `uv run gz validate --chores-layout` => rc=0 (0.37s) -- exit 0 == 0

```text
[uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q] stderr:
----------------------------------------------------------------------
Ran 13 tests in 0.134s

OK
[uv run gz validate --chores-layout] stdout:
Validated: chores_layout

✓ All validations passed (1 scopes).
```

## 2026-10-10 — maintenance visit C: first clustering of the real ledger

`run_cluster()` called directly (no verb runs it; see the defect insight, scope
`chores/eval-feedback-cluster`): 168 `adr-evaluation` events (110 from 2026-05, 35 from 06, 15 from 07,
4 each from 08 and 09) and 6 justify artifacts → 7 buckets, 4 at or above `cluster_min_recurrence` 3:

| cluster | distinct artifacts |
|---|---|
| `dim:Architectural Alignment:critical` | 14 |
| `dim:Problem Clarity:critical` | 12 |
| `dim:Decision Justification:critical` | 10 |
| `dim:Feature Checklist:critical` | 5 |

Four `proposal-20261010T112643*.json` records written (`filed: false`). Reading: the three largest
clusters are the three dimensions `gz justify` scores first, and 110 of the 168 events are the May
evaluation sweep over the pre-1.0 corpus, so the recurrence is as much a property of that sweep's
rubric as of the ADRs. Routing is the operator's: `gz chores propose-ghi eval-feedback-cluster` files
them (TTY, PROPOSE confirmation) or marks them advisory. Below threshold: `OBPI Decomposition` (2),
`Evidence Requirements` (2), `jk:uncertain` (1).
