# eval-feedback-cluster

Cluster recurring weak-dimension and confusion-shape patterns from
`adr-evaluation` ledger events and `gz-justify` artifacts. Emits structured
proposal records to `.gzkit/chores/eval-feedback-cluster/proofs/` when a
pattern recurs ≥3 times across distinct artifacts (ADR-0.0.26).

## Quick Start

```bash
uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q
```

## Lane

**medium**
