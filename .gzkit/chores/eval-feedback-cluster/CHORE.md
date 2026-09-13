# CHORE: eval-feedback-cluster — Evaluation Feedback Clustering

**Lane:** Lite
**Slug:** `eval-feedback-cluster`

---

## Overview

Periodically scan recent `adr-evaluation` ledger events and `gz-justify`
artifacts, cluster by recurring weak-dimension or confusion-shape patterns,
and emit structured proposal records when a pattern recurs ≥3 times across
distinct artifacts (ADR-0.0.26 Decision §3).

## Policy and Guardrails

- **Lane:** Lite — read-only audit over ledger and justify artifacts; unit-tier only, no behave/network
- **Timeout:** 300s — explicit per-chore `timeoutSeconds` (was lane-derived 300 under the removed medium tier); GHI #447
- **Read-only** at `.gzkit/ledger.jsonl` and `docs/design/adr/**`; only writes to its own proofs directory.
- No duplicate proposals: idempotent by content hash over `(cluster_key, sorted source_artifact_ids)`.
- Threshold configurable via `data/eval_feedback_thresholds.json` (`cluster_min_recurrence`, default 3).

## Workflow

### 1. Run clustering

```bash
uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q
```

### 2. Review proposals

```bash
ls .gzkit/chores/eval-feedback-cluster/proofs/
```

Proposals are JSON files: `proposal-<timestamp>.json` with schema:
`cluster_key`, `recurrence_count`, `source_artifact_ids`, `source_artifact_paths`,
`summary`, `proposed_rule_target`.

### 3. Validate layout

```bash
uv run gz validate --chores-layout
```

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan eval-feedback-cluster`. This section explains them and does not restate them (GHI #1002).

## Evidence Commands

```bash
ls .gzkit/chores/eval-feedback-cluster/proofs/
```

---

**End of CHORE: eval-feedback-cluster**
