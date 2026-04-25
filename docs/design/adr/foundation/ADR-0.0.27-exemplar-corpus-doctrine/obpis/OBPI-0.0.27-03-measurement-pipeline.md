---
id: OBPI-0.0.27-03-measurement-pipeline
parent: ADR-0.0.27
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.27-03-measurement-pipeline: Measurement Pipeline

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #3 — "Measurement pipeline producing raw distribution artifacts (`src/gzkit/complexity/measurement.py`, `docs/governance/complexity/baselines/`)"

**Status:** Draft

## Objective

Implement the measurement pipeline that, given the OBPI-02 corpus, clones each project at its pinned SHA, runs `radon cc/mi/hal/raw`, `lizard`, and `cohesion` against the included paths only, aggregates per-metric percentiles (p50, p75, p90, p95, p99) per project and across projects, and emits dated raw distribution artifacts under `docs/governance/complexity/baselines/{date}/`. Pin `radon`, `lizard`, `cohesion` as runtime dependencies in `pyproject.toml` per Stdlib-First named-departure rationale.

## Lane

**Heavy** — New runtime dependencies extend the wheel; new measurement contract; new on-disk baseline schema. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/__init__.py` — package init
- `src/gzkit/complexity/measurement.py` — orchestration entrypoint + tool wrappers
- `src/gzkit/complexity/aggregator.py` — percentile + variance aggregation logic
- `src/gzkit/complexity/baseline.py` — baseline-artifact serializer (JSON output schema)
- `src/gzkit/schemas/complexity_baseline.json` — JSON Schema for baseline artifacts
- `pyproject.toml` — pinned major-version declarations for `radon`, `lizard`, `cohesion`
- `tests/complexity/test_measurement.py`, `tests/complexity/test_aggregator.py`, `tests/complexity/test_baseline.py`
- `docs/governance/complexity/baselines/` — directory creation only; first dated baseline lands at OBPI-04 invocation
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

## Denied Paths

- `data/exemplar_corpus.json` — corpus is OBPI-02
- `.gzkit/rules/complexity-doctrine.md` — rule file is OBPI-01
- `docs/governance/complexity/distilled-characteristics-*.md` — distillation is OBPI-04
- `.gzkit/skills/gz-complexity-distill/**` — skill is OBPI-06
- `src/gzkit/governance/trust_audits.py` — link validator is OBPI-07
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `pyproject.toml` declares `radon>=6.0,<7.0`, `lizard>=1.17,<2.0`, `cohesion>=1.0,<2.0` (or current major-pin equivalents) under runtime dependencies, with each pin's rationale recorded in a comment citing Stdlib-First § "Existing dependencies inherit this rule" — stdlib does not provide cyclomatic complexity / nesting depth / LCOM4 metrics.
2. REQUIREMENT: `measurement.py` exposes a `measure_corpus(corpus: ExemplarCorpus, output_dir: Path) -> BaselineArtifact` entrypoint that orchestrates per-project measurement and per-project + cross-project aggregation. No graceful degradation: missing tool binary fails closed with exit 3 and a named error.
3. REQUIREMENT: For each project at its pinned SHA, the pipeline applies the project's `included_paths` glob and respects `excluded_paths` glob — measurement runs ONLY against the filtered path set; whole-project measurement is rejected with a named error.
4. REQUIREMENT: Aggregation produces per-metric percentiles `p50, p75, p90, p95, p99` per project AND across projects, plus inter-project variance per metric. The seven canonical metrics: `radon_cc`, `radon_mi`, `radon_hal_volume`, `radon_hal_difficulty`, `radon_hal_effort`, `radon_raw_nloc`, `radon_raw_lloc`, `lizard_nloc`, `lizard_param_count`, `lizard_nesting_depth`, `lizard_ccn`, `cohesion_lcom4`.
5. REQUIREMENT: Baseline artifacts are written to `docs/governance/complexity/baselines/{YYYY-MM-DD}/baseline.json` and `baseline.summary.md`. JSON conforms to `src/gzkit/schemas/complexity_baseline.json`; the schema is `extra="forbid"` equivalent (no unknown fields permitted).
6. REQUIREMENT: Baseline output is deterministic for a fixed corpus + tool versions: re-running the pipeline against the same corpus + same SHAs + same tool major versions produces byte-identical JSON (sorted keys, fixed numeric formatting, no timestamps inside the metric blocks). Determinism asserted by a test that runs the pipeline twice and `diff`s the outputs.
7. REQUIREMENT: Tool subprocess invocation uses list-form `subprocess.run` with `encoding="utf-8"` per `.claude/rules/cross-platform.md`; never `shell=True`.
8. REQUIREMENT: Tests cover: pipeline orchestration with mocked tool output; aggregator percentile correctness against fixed-input fixtures; baseline schema round-trip; determinism (run twice, diff empty); path-filter respect (a project with excluded path X must produce no metrics from X); failure modes (missing tool binary → exit 3; corpus loader error → exit 3; unknown JSON field → schema rejection). Each test decorated with `@covers(REQ-0.0.27-03-NN)`.
9. REQUIREMENT: Tests do NOT clone real repositories during the unit tier — fixtures stub the clone-and-measure step. Real-clone integration coverage is deferred to a behave scenario gated under a tag waivable per existing waiver registry.
10. REQUIREMENT: Function size discipline per `.claude/rules/pythonic.md` — measurement.py respects ≤ 50-line functions, ≤ 600-line modules.
11. REQUIREMENT: TDD discipline; `tempfile`-backed temp dirs for baseline outputs in tests.
12. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, or docstrings.

> STOP-on-BLOCKERS: if OBPI-02's `data/exemplar_corpus.json` and `ExemplarProject` model have not landed, STOP — the pipeline consumes the corpus contract.

## Discovery Checklist

- [ ] OBPI-02: `ExemplarProject` model + corpus file shape
- [ ] Parent ADR § Decision — measurement protocol block (radon/lizard/cohesion subcommands and outputs)
- [ ] `radon` / `lizard` / `cohesion` upstream documentation for their JSON-or-equivalent output formats
- [ ] `.claude/rules/cross-platform.md` — subprocess list-form + UTF-8 invariants
- [ ] `.claude/rules/pythonic.md` — function/module size ceilings
- [ ] AGENTS.md § STDLIB-FIRST DOCTRINE — named-departure rationale convention

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle per assertion; tests pass

### Code Quality
- [ ] Lint/type clean; size limits respected

### Gate 3: Docs (Heavy)
- [ ] `mkdocs build --strict` clean
- [ ] Manpage / runbook stub for `gz-complexity-distill` invocation deferred to OBPI-06; this OBPI documents the measurement contract in the ADR evidence

### Gate 4: BDD (Heavy)
- [ ] BDD scenario tagged `@REQ-0.0.27-03-NN` covers a measurement run against a small fixture corpus (or registered as waived if real-clone is too heavy for CI)

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity -v
# Determinism smoke
uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from gzkit.complexity.measurement import measure_corpus; from pathlib import Path; from gzkit.models.exemplar import load_corpus; print(measure_corpus(load_corpus(Path('data/exemplar_corpus.json')), Path('/tmp/baseline-1')))"
```

## Acceptance Criteria

- [ ] REQ-0.0.27-03-01: Given the corpus and a target output directory, when `measure_corpus` runs, then a baseline artifact is produced at `{output_dir}/baseline.json` validating against `src/gzkit/schemas/complexity_baseline.json`.
- [ ] REQ-0.0.27-03-02: Given a project's `excluded_paths`, when measurement runs, then no metric for any path matching the exclusion glob appears in the baseline.
- [ ] REQ-0.0.27-03-03: Given the same corpus + same tool major versions, when the pipeline runs twice into two output dirs, then `diff baseline-1/baseline.json baseline-2/baseline.json` is empty.
- [ ] REQ-0.0.27-03-04: Given each canonical metric, when the aggregator runs, then `p50, p75, p90, p95, p99` and inter-project variance are present per metric per project and aggregated across projects.
- [ ] REQ-0.0.27-03-05: Given a missing `radon`/`lizard`/`cohesion` binary, when the pipeline runs, then it exits with code 3 and a named error; no baseline file is written.
- [ ] REQ-0.0.27-03-06: Given a baseline JSON containing an unknown field, when validation runs, then the schema rejects it.
- [ ] REQ-0.0.27-03-07: Given `pyproject.toml`, when parsed, then the three pinned dependencies appear with major-version pins and rationale citing Stdlib-First.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean; size limits respected
- [ ] Gate 3: mkdocs --strict clean
- [ ] Gate 4: BDD scenario or waiver entry
- [ ] Gate 5: TTY + `ATTEST` captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)
```text
# Paste behave output or waiver entry
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: corpus existed only as a list of pinned projects with no measurement contract; the doctrine had no way to ground numeric thresholds in observation. Capability now: a deterministic measurement pipeline that produces dated baseline artifacts consumed by OBPI-04's distillation pass and re-runnable across distillation cadence cycles. -->

### Key Proof

<!-- Paste the tail of a representative baseline.json showing per-metric percentiles + inter-project variance for at least three corpus entries. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why determinism is the load-bearing property (re-runnability across years), why fail-closed on missing tools beats graceful degradation (situational doctrine = doctrine drift), why per-project path filters at this layer beat a "measure everything and filter later" alternative. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires TTY + ATTEST)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
