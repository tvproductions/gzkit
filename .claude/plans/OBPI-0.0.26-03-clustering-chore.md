# Plan: OBPI-0.0.26-03-clustering-chore

**OBPI:** OBPI-0.0.26-03-clustering-chore
**Parent ADR:** ADR-0.0.26-evaluation-feedback-loop-doctrine
**Lane:** Heavy (foundation-kind parent)
**Date:** 2026-05-03

## Context

OBPI-0.0.26-01 (persist `adr-evaluation` ledger events) is ATTESTED COMPLETED —
event shape confirmed stable. `AdrEvaluationEvent` fields: `artifact_id`,
`artifact_type`, `dimensions: dict[str, float]`, `scores: dict[str, float]`,
`weighted_total`, `red_team_challenges_fired: list[str]`, `evaluator_persona`,
`timestamp`. Ledger stores as `event == "adr-evaluation"`.

`gz-justify` artifacts live at `artifacts/justify/<slug>-<timestamp>.md` with
YAML frontmatter (`anchor_id`, `anchor_kind`, `generated_at`, `scaffold_version`)
followed by 8 markdown sections.

`data/eval_feedback_thresholds.json` exists with `low_score_threshold` and
`red_team_count_threshold`; needs `cluster_min_recurrence: 3` added.

Chore two-surface layout (ADR-0.0.21): canonical package at
`src/gzkit/chores/eval-feedback-cluster/`, project overlay at
`.gzkit/chores/eval-feedback-cluster/`. `proofs/` is always project-local only.

## Files

### New files
- `src/gzkit/chores/eval_feedback_cluster_lib.py` — clustering engine
- `src/gzkit/chores/eval-feedback-cluster/CHORE.md`
- `src/gzkit/chores/eval-feedback-cluster/acceptance.json`
- `src/gzkit/chores/eval-feedback-cluster/README.md`
- `.gzkit/chores/eval-feedback-cluster/proofs/.gitkeep`
- `tests/chores/test_eval_feedback_cluster.py`

### Modified files
- `data/eval_feedback_thresholds.json` — add `cluster_min_recurrence: 3`
- `src/gzkit/chores/registry.json` — add `eval-feedback-cluster` entry

## Steps

### Step 1 — TDD Red: write failing tests

**File:** `tests/chores/test_eval_feedback_cluster.py`

Write 6 test methods in class `TestEvalFeedbackCluster`, each decorated with
`@covers("REQ-0.0.26-03-NN")`. All tests use `tempfile.TemporaryDirectory` for
ledger and justify-artifact fixtures. No network, no real ledger.

Helper: `_write_ledger(path, events)` — writes list of dicts as JSONL.
Helper: `_write_justify(dir, anchor_id, sections)` — writes a minimal justify
markdown with frontmatter + section content.

Test list:

1. `test_zero_evidence_no_proposals` — empty ledger + no justify artifacts →
   `run_cluster()` returns `[]`. Covers REQ-0.0.26-03-08 (zero-evidence run).

2. `test_below_threshold_no_proposal` — 2 distinct artifacts with same
   dimension/score_band (below `cluster_min_recurrence=3`) → returns `[]`.
   Covers REQ-0.0.26-03-02 (below threshold).

3. `test_at_threshold_emits_proposal` — 3 distinct `adr-evaluation` events
   sharing `(dimension_name="clarity", score_band="low")` → returns exactly one
   `ProposalRecord` with all schema fields populated and all 3 source IDs.
   Covers REQ-0.0.26-03-03, REQ-0.0.26-03-05 (at threshold + schema).

4. `test_multiple_clusters_multiple_proposals` — two independent clusters each
   at threshold → returns exactly two proposals.
   Covers REQ-0.0.26-03-04 (multiple proposals).

5. `test_idempotent_rerun` — run once, write proposals to proofs dir, run again
   with identical evidence → second run returns 0 new proposals written (dedup
   by content hash).
   Covers REQ-0.0.26-03-06 (idempotency).

6. `test_readonly_constraint` — `run_cluster()` with a read-only ledger path
   succeeds (reads only) and never writes outside `proofs_dir`.
   Covers REQ-0.0.26-03-07 (read-only at ledger/ADR surfaces).

Run: `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -v` →
expect 6 failures (ImportError or AttributeError — lib does not exist yet).

### Step 2 — Implement `src/gzkit/chores/eval_feedback_cluster_lib.py`

Keep module under 600 lines (pythonic.md). All models use
`ConfigDict(frozen=True, extra="forbid")`.

**`ProposalRecord` model** (REQ-0.0.26-03-05):
```python
class ProposalRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    cluster_key: str
    recurrence_count: int
    source_artifact_ids: list[str]
    source_artifact_paths: list[str]
    summary: str
    proposed_rule_target: str
```

**`_score_band(score: float) -> str`**: maps score to band:
- `< 1.5` → `"critical"`, `< 2.5` → `"very_low"`, `< 3.0` → `"low"`.

**`_read_adr_evaluation_events(ledger_path: Path) -> list[dict]`**:
Read ledger.jsonl line-by-line; filter `event == "adr-evaluation"`. Return list.
Pure read — no writes.

**`_walk_justify_artifacts(justify_root: Path) -> list[dict]`**:
Walk `justify_root` for `*.md` files. Parse YAML frontmatter (between `---` delimiters).
Return list of `{"path": ..., "anchor_id": ..., "sections": ..., "raw": ...}`.

**`_extract_confusion_keywords(sections_text: str) -> list[str]`**:
Simple keyword scan over a predefined vocabulary set:
`{"unclear", "ambiguous", "confusing", "scope drift", "boundary unclear",
"not sure", "uncertain", "vague", "unresolved", "conflicting"}`.
Returns sorted list of matched keywords present in the text.

**`_build_buckets(events, justify_artifacts, score_threshold: float) -> dict[str, list[dict]]`**:
Returns `{cluster_key: [{"artifact_id": ..., "artifact_path": ...}, ...]}`.
Three bucket families:
- `dim:{dimension_name}:{score_band}` — for each `adr-evaluation` event, for each
  dimension with score < `score_threshold`.
- `rt:{challenge_id}` — for each entry in `red_team_challenges_fired`.
- `jk:{keyword}` — for each justify artifact, for each confusion keyword found.

**`_content_hash(cluster_key: str, artifact_ids: list[str]) -> str`**:
`hashlib.sha256(json.dumps([cluster_key, sorted(artifact_ids)]).encode()).hexdigest()[:16]`

**`_load_existing_hashes(proofs_dir: Path) -> set[str]`**:
Read all `proposal-*.json` in `proofs_dir`. Return set of
`content_hash` field values.

**`run_cluster(project_root: Path, *, ledger_path: Path | None = None, justify_root: Path | None = None, proofs_dir: Path | None = None, cluster_min_recurrence: int = 3, score_threshold: float = 3.0) -> list[ProposalRecord]`**:
1. Resolve defaults from `project_root`.
2. Read events and artifacts.
3. Build buckets.
4. Load existing hashes.
5. For each bucket with `len(members) >= cluster_min_recurrence`:
   - Compute `content_hash`.
   - Skip if hash already in existing hashes.
   - Build `ProposalRecord`.
   - Write to `proofs_dir/proposal-<utc_timestamp>.json`.
6. Return list of new `ProposalRecord` instances written.

Write proofs only to `proofs_dir` — never to `ledger_path` or `justify_root`.

### Step 3 — TDD Green: run tests, iterate to passing

```bash
uv run -m unittest tests/chores/test_eval_feedback_cluster.py -v
uv run ruff check . --fix && uv run ruff format .
uvx ty check . --exclude 'features/**'
```

All 6 tests must pass.

### Step 4 — Add `cluster_min_recurrence` to `data/eval_feedback_thresholds.json`

Add `"cluster_min_recurrence": 3` to the existing JSON object.

### Step 5 — Create chore package `src/gzkit/chores/eval-feedback-cluster/`

**`CHORE.md`** — slug: `eval-feedback-cluster`, lane: Medium (reads ledger,
walks artifacts; no network), version 1.0.0. Include: overview, policy/guardrails
(read-only at ledger/ADR), workflow (run → review proposals), acceptance criteria
table, evidence commands referencing proofs dir.

**`acceptance.json`** — two criteria:
1. `exitCodeEquals`, `uv run -m unittest tests/chores/test_eval_feedback_cluster.py -q`, `0`
2. `exitCodeEquals`, `uv run gz validate --chores-layout`, `0`

**`README.md`** — one-paragraph summary, quick-start command.

### Step 6 — Create project-local overlay `.gzkit/chores/eval-feedback-cluster/`

Create directory + `proofs/.gitkeep`.

### Step 7 — Register chore in `src/gzkit/chores/registry.json`

Add entry at end of `"chores"` array:
```json
{
    "slug": "eval-feedback-cluster",
    "title": "Evaluation Feedback Clustering (ADR-0.0.26-03)",
    "version": "1.0.0",
    "path": ".gzkit/chores/eval-feedback-cluster",
    "lane": "medium"
}
```

### Step 8 — Full quality sweep

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --chores-layout
uv run gz chores show eval-feedback-cluster
uv run gz chores run eval-feedback-cluster
```

## Verification

Per brief:
```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/chores/test_eval_feedback_cluster.py -v
uv run gz validate --chores-layout
uv run gz chores show eval-feedback-cluster
uv run gz chores run eval-feedback-cluster
```

## Notes

- `score_band` mapping is a derived heuristic; the threshold for what counts
  as "low" is `score_threshold` from `eval_feedback_thresholds.json`
  (`low_score_threshold: 3.0`). Scores below that threshold are bucketed by
  band subdivision.
- Confusion-keyword vocabulary is a static set; no ML, no network.
- `cluster_min_recurrence` (default 3) mirrors the ADR's "≥3 times across
  distinct artifacts" language verbatim.
- Cross-platform: all paths via `pathlib.Path`, UTF-8 encoding explicit.
- No `shell=True` in any subprocess; no subprocesses needed (pure Python).
