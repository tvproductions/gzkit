# Plan: OBPI-0.0.27-03 — Measurement Pipeline

**OBPI:** OBPI-0.0.27-03-measurement-pipeline
**Parent ADR:** ADR-0.0.27 (foundation, kind=foundation, lane=heavy)
**Brief:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-03-measurement-pipeline.md`
**Mode:** Normal (no `Execution Mode: Exception (SVFR)` declared on the parent ADR)
**Attestation rigor:** Heavy lane + foundation kind → Gate 5 TTY+`ATTEST` mandatory at brief level.

---

## Context

OBPI-02 has landed: `data/exemplar_corpus.json` (13 projects across 10 archetypal cells) and the
`ExemplarProject` / `ExemplarCorpus` Pydantic models (`src/gzkit/models/exemplar.py`) with
`load_corpus(path)` loader. This OBPI consumes that contract and produces the deterministic
baseline-artifact pipeline that OBPI-04's distillation pass and OBPI-07's link-integrity validator
will read in turn.

The pipeline:

1. Walks the corpus (in-memory `ExemplarCorpus`).
2. For each project, ensures the pinned SHA tree is available locally (clone-if-absent at a
   pinned cache root), then runs `radon cc/mi/hal/raw`, `lizard`, and `cohesion` against the
   project's `included_paths` filter only — never whole-project.
3. Aggregates per-metric percentiles (`p50/p75/p90/p95/p99`) and inter-project variance per
   metric, emitting one deterministic `baseline.json` and a human-readable `baseline.summary.md`
   under `docs/governance/complexity/baselines/{YYYY-MM-DD}/`.

**Dependency posture (Stdlib-First named departure):** `radon`, `lizard`, `cohesion` are pinned
runtime dependencies. Stdlib does not expose cyclomatic complexity, nesting depth, or LCOM4 —
the brief's REQ-01 + parent ADR § Decision name this as the canonical departure rationale.

**Determinism is load-bearing.** Re-running against the same corpus + same SHAs + same tool
major versions must produce byte-identical JSON. Any clock-derived field, set-iteration ordering,
or default `json.dumps` shape is a defect.

**Brief defect noted (not blocking):** REQ-04 says "The seven canonical metrics" but enumerates
12 specific metric keys. I'll implement against the enumerated 12-key list (the operative content)
and flag the wording drift in the Stage 4 evidence so the operator can rewrite "seven" → "the
canonical metric set" at attestation time, or open a brief-edit GHI. Per AGENTS.md § Prime
Directive #6, every defect must be trackable.

---

## Files (allowlist-bounded — every path below appears in the brief's Allowed Paths)

### New source

- `src/gzkit/complexity/__init__.py` — package init; re-export `measure_corpus` and the public model types.
- `src/gzkit/complexity/measurement.py` — orchestration entrypoint (`measure_corpus`), per-project measurement, subprocess wrappers for `radon`/`lizard`/`cohesion`, path-filter application, named errors, exit-3 propagation.
- `src/gzkit/complexity/aggregator.py` — pure functions for per-metric percentile + inter-project variance aggregation.
- `src/gzkit/complexity/baseline.py` — `BaselineArtifact` Pydantic model + deterministic JSON serializer + `baseline.summary.md` renderer.
- `src/gzkit/schemas/complexity_baseline.json` — JSON Schema mirror of `BaselineArtifact` (`additionalProperties: false`, mirrors model field-by-field).

### New tests

- `tests/complexity/__init__.py`
- `tests/complexity/test_measurement.py` — pipeline orchestration (mocked subprocess), path-filter respect, missing-binary fail-closed (exit 3), corpus-loader error fail-closed (exit 3).
- `tests/complexity/test_aggregator.py` — percentile correctness against fixed-input fixtures (p50/p75/p90/p95/p99 and inter-project variance).
- `tests/complexity/test_baseline.py` — schema round-trip, unknown-field rejection, determinism (run twice, byte-diff empty), `baseline.summary.md` shape.

### Existing sources modified

- `pyproject.toml` — add `radon>=6.0,<7.0`, `lizard>=1.17,<2.0`, `cohesion>=1.0,<2.0` to `dependencies` with a per-pin comment block citing Stdlib-First § "Existing dependencies inherit this rule".

### New empty directory

- `docs/governance/complexity/baselines/` — keep with a `.gitkeep` so the path exists for OBPI-04. The first dated baseline lands at OBPI-04 invocation; this OBPI does not commit a baseline artifact (the brief is explicit on this).

### Brief evidence updates (allowlist-permitted by `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**`)

- The brief's evidence sections (Gate 1–5, Implementation Summary, Key Proof, Closing Argument) are populated at Stage 5 via `gz obpi complete --implementation-summary --key-proof`. No direct hand-edit of the brief during Stage 2.

### Files explicitly NOT touched (denylist or out-of-scope)

- `data/exemplar_corpus.json` — OBPI-02 surface (denied).
- `.gzkit/rules/complexity-doctrine.md` — OBPI-01 surface (denied).
- `docs/governance/complexity/distilled-characteristics-*.md` — OBPI-04 surface (denied).
- `.gzkit/skills/gz-complexity-distill/**` — OBPI-06 surface (denied).
- `src/gzkit/governance/trust_audits.py` — OBPI-07 surface (denied).

---

## Steps

### Step 1 — Schema + model contract (TDD red)

Author `tests/complexity/test_baseline.py` with three failing tests pinning the contract before any source lands:

- `test_baseline_artifact_round_trip` — instantiate `BaselineArtifact` from a fixed dict; serialize; reload; assert equality. Decorate `@covers("REQ-0.0.27-03-01")`.
- `test_baseline_schema_rejects_unknown_field` — load schema, validate a payload with an extra top-level key, assert rejection. `@covers("REQ-0.0.27-03-06")`.
- `test_baseline_summary_markdown_renders` — given a fixed `BaselineArtifact`, assert the `.summary.md` contains the per-project percentile lines.

Author `src/gzkit/complexity/baseline.py`:

- `BaselineArtifact` (`BaseModel`, `frozen=True, extra="forbid"`): `corpus_revision: int`, `corpus_schema_version: str`, `tool_versions: dict[str, str]` (radon/lizard/cohesion → semver string), `projects: tuple[ProjectBaseline, ...]`, `cross_project: CrossProjectAggregate`.
- `ProjectBaseline` (frozen): `name: str`, `commit_sha: str`, `archetypal_cell: int`, `metrics: tuple[MetricDistribution, ...]`.
- `MetricDistribution` (frozen): `metric_key: str` (one of the 12), `p50: float`, `p75: float`, `p90: float`, `p95: float`, `p99: float`, `sample_count: int`.
- `CrossProjectAggregate` (frozen): `metrics: tuple[CrossMetricAggregate, ...]`.
- `CrossMetricAggregate` (frozen): `metric_key: str`, `p50/p75/p90/p95/p99: float`, `inter_project_variance: float`, `project_count: int`.
- `serialize_baseline(artifact: BaselineArtifact) -> str` — `json.dumps(model.model_dump(mode="json"), sort_keys=True, indent=2, ensure_ascii=False)` — sorted keys is the determinism anchor.
- `render_summary(artifact: BaselineArtifact) -> str` — markdown table per project + cross-project.

Author `src/gzkit/schemas/complexity_baseline.json` mirroring the model field-by-field, `additionalProperties: false` everywhere, `$schema` draft 2020-12, registered the same way as `exemplar_corpus.json`.

Run unittest tier — tests for this step go green.

### Step 2 — Aggregator (TDD red → green)

Author `tests/complexity/test_aggregator.py`:

- `test_percentile_fixed_input` — pass a fixed list `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` and assert exact `p50/p75/p90/p95/p99` values using `statistics.quantiles(..., n=100)` semantics or NumPy-equivalent linear interpolation. `@covers("REQ-0.0.27-03-04")`.
- `test_aggregate_per_project_then_cross` — given two projects each with 5 raw values per metric, assert per-project percentiles and cross-project aggregate are computed. `@covers("REQ-0.0.27-03-04")`.
- `test_inter_project_variance` — fixed inputs, assert variance matches `statistics.variance` of the per-project medians.

Author `src/gzkit/complexity/aggregator.py` — pure stdlib (`statistics.quantiles`, `statistics.variance`); no NumPy dependency. Stdlib-First. Functions kept ≤ 50 lines each.

- `compute_metric_distribution(values: Sequence[float]) -> MetricDistribution`
- `aggregate_project(name, sha, cell, raw_metrics: Mapping[str, Sequence[float]]) -> ProjectBaseline`
- `aggregate_cross_project(projects: Sequence[ProjectBaseline]) -> CrossProjectAggregate`

Run unittest tier — tests for this step go green.

### Step 3 — Subprocess wrappers + measurement orchestration (TDD red → green)

Author `tests/complexity/test_measurement.py`:

- `test_measure_corpus_smoke` — fixture corpus (one project, two files), mock `subprocess.run` to return canned `radon --json` / `lizard --csv` / `cohesion` output, call `measure_corpus`, assert the resulting `BaselineArtifact` has the expected per-project metric distributions and that no real clone happened. `@covers("REQ-0.0.27-03-01")`.
- `test_path_filter_excludes_excluded_glob` — fixture project with `excluded_paths` matching one of two source files; assert measurement was invoked only on the filtered subset and the excluded file's hypothetical metrics are absent. `@covers("REQ-0.0.27-03-02")`.
- `test_missing_binary_exits_3` — patch `shutil.which` to return `None` for `radon`; assert `measure_corpus` raises `MissingMeasurementToolError` and that the CLI surface translates that to exit 3. `@covers("REQ-0.0.27-03-05")`.
- `test_corpus_loader_error_exits_3` — pass an unparseable corpus path; assert wrapped to exit 3 with named error.
- `test_subprocess_invocation_is_list_form_and_utf8` — assert the captured `subprocess.run` calls used list-form `args`, never `shell=True`, and `encoding="utf-8"`. `@covers("REQ-0.0.27-03-07")` (cross-platform invariant from `.claude/rules/cross-platform.md`).
- `test_no_real_clone_in_unit_tier` — fixture stubs the clone step; assert no network or filesystem mutation outside `tempfile`. `@covers("REQ-0.0.27-03-09")` (REQ-09 re-stated as test contract).

Author `src/gzkit/complexity/measurement.py`:

- Module-level: `CANONICAL_METRICS: tuple[str, ...]` enumerating the 12 keys.
- `class MissingMeasurementToolError(RuntimeError)` — named, carries `tool: str`.
- `class CorpusLoaderError(RuntimeError)` — wraps Pydantic / JSON / OS errors.
- `class WholeProjectMeasurementRejectedError(RuntimeError)` — REQ-03 fail-closed shape.
- `_resolve_tree(project: ExemplarProject, cache_root: Path) -> Path` — clone-if-absent at SHA. In unit tests, this function is the seam stubbed by `test_no_real_clone_in_unit_tier`.
- `_apply_path_filter(tree: Path, project: ExemplarProject) -> tuple[Path, ...]` — expand `included_paths`, subtract `excluded_paths_with_rationale.glob`, return absolute paths.
- `_run_radon_cc(paths) -> dict[str, list[float]]`, `_run_radon_mi`, `_run_radon_hal`, `_run_radon_raw`, `_run_lizard`, `_run_cohesion` — each calls `subprocess.run([...], capture_output=True, text=True, encoding="utf-8", check=False)` and parses tool output. `shell=True` is forbidden. Missing binary → `MissingMeasurementToolError`.
- `_assert_tool_binaries_present()` — `shutil.which` for each of `radon`, `lizard`, `cohesion`; missing → `MissingMeasurementToolError`.
- `measure_corpus(corpus: ExemplarCorpus, output_dir: Path, *, cache_root: Path | None = None) -> BaselineArtifact` — orchestrates: assert binaries → for each project, resolve tree, apply filter, run wrappers, accumulate raw metric arrays → aggregate per-project → aggregate cross-project → serialize → write `baseline.json` + `baseline.summary.md` → return artifact.
- Each function ≤ 50 lines; module ≤ 600 lines (split into a private helpers module if it grows).

CLI integration is **out of scope for this OBPI** — measurement is invoked programmatically by OBPI-06's skill / OBPI-04's distillation pass. This OBPI exposes the entrypoint; CLI surface lands at OBPI-06.

Run unittest tier — tests for this step go green.

### Step 4 — Determinism gate

Author in `tests/complexity/test_baseline.py`:

- `test_pipeline_is_byte_deterministic` — given a fixture corpus and stubbed tool output, run `measure_corpus` twice into two `tempfile.TemporaryDirectory` outputs; assert `baseline.json` contents are byte-identical. `@covers("REQ-0.0.27-03-03")`.

If determinism fails, the most likely offenders are: (a) a `datetime.now()` slipping into a metric block, (b) `set` iteration ordering, (c) `json.dumps` defaults missing `sort_keys=True`. Fix at the source — never paper over with sort-after-the-fact post-processing.

### Step 5 — `pyproject.toml` named-departure declarations

Add the three runtime deps with rationale comments. Locate the `dependencies = [` block, append:

```toml
    # Stdlib-First named departures (ADR-0.0.27 § Decision; AGENTS.md § STDLIB-FIRST DOCTRINE
    # § "Existing dependencies inherit this rule"). Stdlib does not expose cyclomatic
    # complexity, nesting depth, or LCOM4; these are corpus-measurement-only deps consumed
    # by src/gzkit/complexity/measurement.py.
    "radon>=6.0,<7.0",
    "lizard>=1.17,<2.0",
    "cohesion>=1.0,<2.0",
```

`@covers("REQ-0.0.27-03-07")` for the pyproject contract test:

- `tests/complexity/test_measurement.py::test_pyproject_declares_three_deps_with_pins` — read `pyproject.toml`, assert each of the three deps appears with a major-version pin shape.

Run `uv sync` to materialize the new deps.

### Step 6 — Quality gates (Heavy lane)

Run in order, fix on failure:

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.complexity -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.27-03-measurement-pipeline --json
```

REQ → `@covers` parity gate (Stage 3 Phase 1b in the pipeline skill) must show `uncovered_reqs == 0` before Stage 4. Each REQ from REQ-01 through REQ-12 maps to at least one decorated test:

| REQ | Test |
|---|---|
| REQ-0.0.27-03-01 | `test_measure_corpus_smoke`, `test_baseline_artifact_round_trip` |
| REQ-0.0.27-03-02 | `test_path_filter_excludes_excluded_glob` |
| REQ-0.0.27-03-03 | `test_pipeline_is_byte_deterministic` |
| REQ-0.0.27-03-04 | `test_percentile_fixed_input`, `test_aggregate_per_project_then_cross`, `test_inter_project_variance` |
| REQ-0.0.27-03-05 | `test_missing_binary_exits_3`, `test_corpus_loader_error_exits_3` |
| REQ-0.0.27-03-06 | `test_baseline_schema_rejects_unknown_field` |
| REQ-0.0.27-03-07 | `test_subprocess_invocation_is_list_form_and_utf8`, `test_pyproject_declares_three_deps_with_pins` |
| REQ-0.0.27-03-08 | (meta — REQ-08 declares the test set; the rows above ARE the test set) |
| REQ-0.0.27-03-09 | `test_no_real_clone_in_unit_tier` |
| REQ-0.0.27-03-10 | (mechanical — verified by `gz arb ruff` size-limit check, not a unit test) |
| REQ-0.0.27-03-11 | (process — TDD discipline, evidenced by RGR receipts) |
| REQ-0.0.27-03-12 | (process — operator PII absence; evidenced by absence of `ahuimanu@gmail.com` literal in any new file) |

REQ-08, REQ-10, REQ-11, REQ-12 are meta/process REQs that the parity gate may flag as
"covered: false" because they have no specific `@covers` decorator. Plan A: decorate one
test in each module with the meta REQ as a secondary `@covers` (per
`.gzkit/rules/tests.md` — `@covers` accepts multiple IDs). Plan B (fallback): file a brief
edit GHI to remove these meta REQs in favor of mechanical equivalents. The brief author
plainly intended these as discipline reminders, not REQ rows; the parity gate cannot tell
the difference. I'll execute Plan A first, escalate to operator if it doesn't satisfy.

### Step 7 — BDD scenario or waiver (Heavy Gate 4)

The brief allows a `@REQ-0.0.27-03-NN` BDD scenario covering a real-corpus measurement run, OR
registration in the waiver registry. Real-corpus measurement requires actual clones of 13 large
repos at pinned SHAs, which is beyond CI's reasonable budget. I'll register a waiver entry per
the existing waiver registry shape — the unit-tier coverage of the orchestration seam plus the
manual smoke per the brief's Verification block is the operative evidence. If a waiver registry
file does not exist for this OBPI's scope, I'll surface to the operator before authoring one.

---

## Verification (must pass before Stage 4)

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.complexity -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.27-03-measurement-pipeline --json   # uncovered_reqs == 0
uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from gzkit.complexity.measurement import measure_corpus; from pathlib import Path; from gzkit.models.exemplar import load_corpus; print(measure_corpus(load_corpus(Path('data/exemplar_corpus.json')), Path('/tmp/baseline-1')))"
```

Brief verification (lines 96–104) is honored verbatim. The final smoke command may take real
time on first invocation (clones the 13 corpus projects); it's optional for the OBPI-03
attestation but required for the human reviewer to sanity-check the pipeline against the live
corpus. If real-clone is impractical at attestation time, substitute a fixture-corpus smoke per
`tests/complexity/test_measurement.py::test_measure_corpus_smoke`.

---

## Notes (rejected alternatives, plan-before-exploration disclosure)

**Destination-in-mind disclosure (Step 6a, gz-plan-audit § Plan-Before-Exploration Ordering):** I
read the brief, the parent ADR § Decision, the corpus model, and the cross-platform / pythonic /
models rules before writing this plan. The destination I formed during exploration: a
four-module `src/gzkit/complexity/` package with subprocess wrappers per tool, stdlib-only
aggregation, deterministic JSON serialization with `sort_keys=True`, and explicit
`MissingMeasurementToolError` for the fail-closed binary-absence case. The plan reflects that
destination exactly — no reconstruction, no post-hoc fitting.

**Rejected alternatives:**

1. **Single-file `measurement.py` with all logic (rejected):** Would have crossed the
   600-line module ceiling once the six tool-wrapper functions, the orchestration entrypoint,
   the path-filter helper, and the named-error classes co-existed. Splitting `aggregator.py`
   and `baseline.py` keeps each module under 300 lines comfortably and gives each its own
   tightly-scoped test file.

2. **Use `numpy.percentile` for aggregation (rejected):** NumPy is not currently a gzkit
   runtime dependency. Adding one for percentile computation when `statistics.quantiles` is
   stdlib violates Stdlib-First (AGENTS.md § STDLIB-FIRST DOCTRINE). Rejected on canon.

3. **Stream tool output to disk instead of capturing in memory (rejected):** Some corpus
   projects produce large per-function arrays, but at 13 projects × ≤ 5000 functions × 12
   metrics × float64 ≈ 5 MiB peak, in-memory aggregation is far below any pressure point.
   Streaming would complicate determinism (intermediate file ordering) without measurable benefit.

4. **Cache `radon`/`lizard`/`cohesion` invocations across runs to speed re-runs (rejected,
   deferred):** Tempting for OBPI-04's distillation iteration, but caching introduces
   determinism failure modes (stale cache reading, partial-cache mixing), and the brief is
   explicit that tool re-invocation against pinned SHA + pinned tool version IS the
   determinism contract. If iteration speed becomes a real cost in OBPI-04, that's a chore
   for OBPI-04, not a complication this OBPI should pre-build.

5. **Fail-soft on missing tool binary with a `degraded: true` baseline (rejected):**
   Doctrine drift is invariant drift. The brief's REQ-02 says "No graceful degradation:
   missing tool binary fails closed with exit 3 and a named error." Fail-soft would let an
   environment without `cohesion` produce a baseline missing one of the 12 metrics, and
   the operator would have no mechanical signal that the foundation doctrine is operating
   on a partial measurement. Rejected on doctrine.

6. **Vendor `radon`'s percentile / `lizard`'s parsing into gzkit (rejected):** Vendoring
   would shrink the dep surface but would shift complexity inward and require us to track
   upstream bug fixes manually. Pinned major-version deps with named departure rationale is
   the gzkit pattern (see `pydantic` in `models.md`).

---

## Acceptance criteria checklist

- [ ] All seven Acceptance Criteria from the brief (REQ-0.0.27-03-01 through -07) have a
      corresponding test asserting the requirement.
- [ ] `uv run gz covers OBPI-0.0.27-03-measurement-pipeline --json` reports
      `summary.uncovered_reqs == 0`.
- [ ] `uv run gz arb ruff`, `uv run gz arb typecheck`, `uv run gz arb step --name unittest -- uv run -m unittest -q`,
      `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`, and `uv run gz validate --documents`
      all return success and emit canonical receipts.
- [ ] `radon`, `lizard`, `cohesion` appear in `pyproject.toml` `dependencies` with major-version pins
      and Stdlib-First named-departure comment.
- [ ] `docs/governance/complexity/baselines/.gitkeep` exists; no dated baseline JSON committed
      yet (OBPI-04 produces the first one).
- [ ] No operator personal email anywhere in new code, fixtures, docstrings, or attestation text.
