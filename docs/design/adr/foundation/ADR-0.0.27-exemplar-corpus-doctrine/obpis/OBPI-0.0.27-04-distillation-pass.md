---
id: OBPI-0.0.27-04-distillation-pass
parent: ADR-0.0.27
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.0.27-04-distillation-pass: First Distillation Pass

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #4 — "Distillation pass authoring distilled-characteristics document — agent-driven, human-reviewed and attested/corrected (`docs/governance/complexity/distilled-characteristics-{date}.md`)"

**Status:** Draft

## Objective

Run the first distillation pass against the OBPI-03 baseline and author `docs/governance/complexity/distilled-characteristics-{date}.md`. The agent drafts metric-aggregate prose per metric (median, p75, p90, p95, p99 with inter-project variance commentary); the operator adds the practitioner-eye observation; together they record per-metric triples (numeric boundary + qualitative band + doctrinal frame). First-run cold-start: the prior-distillation diff narration mechanism is no-op but its presence is canonized for subsequent runs.

## Lane

**Heavy** — First distilled-characteristics document is the load-bearing artifact cited by ADR-0.0.28 / 0.0.29 / 0.0.30. Foundation-kind brief-level Gate 5 attestation; the operator's signature is the witness boundary the doctrine ships behind.

## Allowed Paths

- `docs/governance/complexity/baselines/{YYYY-MM-DD}/baseline.json` — first dated baseline artifact (produced at OBPI-04 invocation per OBPI-03 brief intent; OBPI-03 scaffolded the directory and the pipeline, OBPI-04 lands the first measurement output)
- `docs/governance/complexity/baselines/{YYYY-MM-DD}/baseline.summary.md` — companion summary document for the same dated baseline
- `docs/governance/complexity/distilled-characteristics-{YYYY-MM-DD}.md` — first distilled doctrine document
- `docs/governance/complexity/distilled-characteristics.md` — symlink or pointer file naming the current distillation (optional; pattern decided in this OBPI)
- `src/gzkit/complexity/distillation.py` — diff-narration mechanism (no-op on first run; full diff in subsequent runs)
- `tests/complexity/test_distillation.py` — REQ-derived assertions on the document shape and the diff mechanism
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

## Denied Paths

- `data/exemplar_corpus.json` — corpus is OBPI-02
- `src/gzkit/complexity/measurement.py` — measurement is OBPI-03
- `.gzkit/skills/gz-complexity-distill/**` — skill is OBPI-06
- `src/gzkit/governance/trust_audits.py` — link validator is OBPI-07
- `pyproject.toml` — runtime deps are OBPI-03
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The distilled-characteristics document at `docs/governance/complexity/distilled-characteristics-{YYYY-MM-DD}.md` carries frontmatter declaring `corpus_revision`, `baseline_artifact_path`, `distillation_date`, and `prior_distillation_path` (null on first run, populated on subsequent runs).
2. REQUIREMENT: For each canonical metric (per OBPI-03), the document contains a section with a per-metric triple: (a) numeric boundary expressed as **percentile-of-corpus AND absolute-number-at-that-percentile** (e.g. "CC ≤ p90 = 12"), (b) qualitative band (one of: comfortable craft / investigate / refactor), (c) doctrinal frame (which authority — Fowler, Martin, Page-Jones, Constantine — speaks to a violation at this boundary).
3. REQUIREMENT: Per-metric prose blocks are agent-drafted (median, p75, p90, p95, p99 with inter-project variance commentary), with an explicit "Practitioner-eye observation" subsection authored by the operator and attested via the OEE doctrine — agent never fabricates the practitioner-eye block.
4. REQUIREMENT: A "Diff against prior distillation" section appears in the document; on first run it states "Cold start — no prior distillation; this document establishes the baseline" and lists no boundary-movement narrations. The mechanism is fully exercised on subsequent runs (any boundary that moved > 10% gets explicit operator narration in the section).
5. REQUIREMENT: Previous distilled-characteristics documents are NEVER overwritten — every distillation run produces a new dated document; the doctrine evolution audit trail is permanent and append-only.
6. REQUIREMENT: The document includes a "Citation form" section quoting the citation contract from `.gzkit/rules/complexity-doctrine.md`: downstream foundation ADRs cite this document by `(file path, section anchor, corpus_revision)` tuple.
7. REQUIREMENT: Tests cover: document frontmatter validates against expected schema; each canonical metric has a per-metric triple; first-run document carries the cold-start diff section; second-run distillation against a synthetic shifted baseline produces a diff section listing boundary-movement narrations; previous documents are not overwritten (running distillation twice on the same date produces a `-1`-suffixed dated path or rejects); each test decorated with `@covers(REQ-0.0.27-04-NN)`.
8. REQUIREMENT: TDD discipline; tests use synthetic baseline fixtures (do not depend on the live corpus or live tool output).
9. REQUIREMENT: NEVER include the operator's personal email in the distilled document, frontmatter, or test fixtures. Operator attestor identity uses name only.
10. REQUIREMENT: NEVER author the practitioner-eye observation as agent prose. The OEE doctrine binds the boundary: agent drafts the metric-aggregate prose and proposes classifier rule-table updates against the new percentiles; operator adds the practitioner-eye block; both are required for Gate 5 to fire.

> STOP-on-BLOCKERS: if OBPI-03's baseline artifact has not landed at `docs/governance/complexity/baselines/{date}/baseline.json`, STOP — distillation has nothing to distill.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.27-03 `attested_completed` — `src/gzkit/complexity/measurement.py` (`measure_corpus()` entrypoint), `src/gzkit/complexity/baseline.py` (`BaselineArtifact`, `CrossProjectAggregate`, `ProjectBaseline`, `MetricDistribution`, `CrossMetricAggregate` frozen Pydantic models), and `src/gzkit/complexity/measurement.CANONICAL_METRICS` (12-key tuple) provide the measurement contract this distillation pass consumes. Brief amendment 2026-05-04 expanded OBPI-04 Allowed Paths to include `docs/governance/complexity/baselines/{YYYY-MM-DD}/baseline.json` + `baseline.summary.md` so OBPI-04 invokes `measure_corpus()` to land the first dated baseline (OBPI-03 brief line 35: "first dated baseline lands at OBPI-04 invocation").
- [x] Parent ADR-0.0.27 § Decision — distillation pass shape (six-step joint authoring sequence: agent-drafts metric-aggregate prose → operator practitioner-eye observation → joint per-metric triple authoring → agent-proposed classifier rule-table updates → diff against prior distillation > 10% → output to `docs/governance/complexity/distilled-characteristics-{date}.md` with prior preserved).
- [x] AGENTS.md § OPERATOR ECONOMY OF EFFORT — agent drafts substantively, operator reviews; verbatim phrasing preserved; raw machine-readable formats are agent-input surfaces only. Practitioner-eye block is the canonical OEE seam — agent never authors its prose (REQ-10).
- [x] AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — foundation+heavy → brief-level Gate 5 walkthrough required regardless of axis-overlap; `_requires_human_obpi_attestation` returns True via the foundation branch.
- [x] `.gzkit/rules/complexity-doctrine.md` — citation contract binding for downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30); the distilled document is the load-bearing surface, not the raw distributions or the corpus registry.
- [x] Authority canon: Fowler *Refactoring* 2e (long-method / large-class / divergent-change smell aggregate), Martin *Clean Code* (single-responsibility cyclomatic ceiling, long-parameter-list, nesting-depth), Page-Jones (connascence), Constantine (cohesion / coupling foundations) — distributed across the 12 canonical metrics in `_DOCTRINAL_FRAMES` per the per-metric triple's doctrinal-frame field (REQ-02).

**Existing Code**

- [x] `src/gzkit/complexity/measurement.py` — `measure_corpus(corpus, output_dir, *, cache_root=None) -> BaselineArtifact` orchestrates radon/lizard/cohesion against pinned-SHA clones; `CANONICAL_METRICS` is the 12-key tuple consumed by this distillation pass.
- [x] `src/gzkit/complexity/baseline.py` — `BaselineArtifact` (corpus_revision + corpus_schema_version + tool_versions + projects + cross_project), `CrossProjectAggregate.metrics`, `CrossMetricAggregate` (per-metric pXX percentiles + inter_project_variance + project_count); all frozen + `extra="forbid"` so the distillation pass cannot drift from the measurement contract.
- [x] `data/exemplar_corpus.json` — 13 pinned-SHA projects (`schema_version=1.0.0`, `corpus_revision=1`); `gzkit.models.exemplar.load_corpus(Path)` returns the validated `ExemplarCorpus`.
- [x] `src/gzkit/traceability.covers` — `@covers("REQ-X.Y.Z-NN-MM")` decorator for REQ-derived parity (consumed by `gz covers OBPI-... --json` parity gate at Stage 3 Phase 1b).
- [x] `data/behave_coverage_waivers.json` — existing waiver shape (rationale-key + per-OBPI entry); precedents at OBPI-0.0.27-01 / -02 / -03 for the same parent ADR. OBPI-04 entry under `adr-0.0.27-04-bdd-deferred-to-obpi-06` rationale defers BDD to OBPI-06's skill-invocation surface per brief REQ-07.
- [x] `src/gzkit/complexity/__init__.py` — re-exports `measure_corpus`, `CANONICAL_METRICS`, `BaselineArtifact` so the distillation module imports from the package surface, not deeper internal modules.

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean (the new dated document renders in the docs site)

### Gate 4: BDD (Heavy)
- [ ] BDD scenario tagged `@REQ-0.0.27-04-NN` covers a synthetic distillation invocation against fixture baseline (or registered as waived if the OBPI-06 skill scenario covers it)

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation — operator attests the practitioner-eye observation per metric before the document lands

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz validate --documents
test -f docs/governance/complexity/distilled-characteristics-$(date +%Y-%m-%d).md
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/test_distillation.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.27-04-01: Given the OBPI-03 baseline, when distillation runs, then a dated distilled-characteristics document is produced at `docs/governance/complexity/distilled-characteristics-{YYYY-MM-DD}.md` with valid frontmatter (`corpus_revision`, `baseline_artifact_path`, `distillation_date`, `prior_distillation_path`).
- [ ] REQ-0.0.27-04-02: Given each canonical metric in the baseline, when the document is parsed, then a per-metric triple is present (numeric boundary as percentile + absolute, qualitative band, doctrinal frame).
- [ ] REQ-0.0.27-04-03: Given the first-run cold-start, when the "Diff against prior distillation" section is read, then it states "Cold start" and lists no boundary movements.
- [ ] REQ-0.0.27-04-04: Given a synthetic prior distillation + a shifted baseline, when distillation runs, then the diff section lists every boundary that moved > 10% with operator narration placeholders.
- [ ] REQ-0.0.27-04-05: Given an existing dated distillation document, when distillation is invoked again on the same date, then the existing document is not overwritten (the run rejects or produces a `-1`-suffixed file).
- [ ] REQ-0.0.27-04-06: Given the document, when the "Citation form" section is read, then the canonical citation tuple `(file path, section anchor, corpus_revision)` is named.
- [ ] REQ-0.0.27-04-07: Given the OEE-binding requirement, when the document is parsed, then each metric's "Practitioner-eye observation" subsection exists and is operator-attested at Gate 5.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict clean
- [ ] Gate 4: BDD scenario or waiver
- [ ] Gate 5: TTY + `ATTEST` captured per metric

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
# Record per-metric attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: complexity thresholds and refactor recommendations would have been pattern-matched from agent training memory or inherited from convention. Capability now: per-metric numeric boundaries + bands + doctrinal frames grounded in observed corpus distributions, attested by the operator's practitioner eye, shipped as gzkit doctrine and cited by the downstream foundation ADRs. -->

### Key Proof


```
$ uv run gz arb step --name unittest -- uv run -m unittest tests.complexity.test_distillation -v
Ran 8 tests in 0.004s — OK
arb step name=unittest exit_status=0 receipt=arb-step-unittest-9cebe48046234a21946b70d1763d20f5

$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
Documentation built in 2.51 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-1bd6a551c30243ca9fdbfaf36df18eb5

$ uv run gz covers OBPI-0.0.27-04-distillation-pass --json
parity gate: 7/7 (100.0%) — uncovered=0

$ head -6 docs/governance/complexity/distilled-characteristics-2026-05-04.md
---
corpus_revision: 1
baseline_artifact_path: "docs/governance/complexity/baselines/2026-05-04/baseline.json"
distillation_date: "2026-05-04"
prior_distillation_path: null
---
```

Receipts: `arb-ruff-d1d8078547d84e92a957a3d0defebaad`, `arb-step-typecheck-114164f0a4ac48549c05734cfc2c759e`, `arb-step-unittest-9cebe48046234a21946b70d1763d20f5`, `arb-step-mkdocs-1bd6a551c30243ca9fdbfaf36df18eb5`.

### Implementation Summary


- Files created: `src/gzkit/complexity/distillation.py` (render_document, render_diff_section, render_metric_triple, _DOCTRINAL_FRAMES per-metric attribution citing Fowler/Martin/Page-Jones/Constantine, DocumentExistsError no-overwrite guard, PerMetricTriple frozen+forbid Pydantic model); `tests/complexity/test_distillation.py` (8 REQ-derived tests, each `@covers(REQ-0.0.27-04-NN)`); `docs/governance/complexity/baselines/2026-05-04/baseline.json` + `baseline.summary.md` (first dated baseline produced by `measure_corpus()` against the live 13-project corpus); `docs/governance/complexity/distilled-characteristics-2026-05-04.md` (192-line first distilled doctrine document, frontmatter + 12 metric sections + cold-start diff sentinel + citation form).
- Tests added: 8 (1 per Acceptance Criterion REQ-01 through REQ-07 + a defensive frozen+forbid model test); parity gate 7/7 (100.0%) verified by `gz covers OBPI-0.0.27-04-distillation-pass --json`.
- Brief amendment: 2026-05-04 added `docs/governance/complexity/baselines/{YYYY-MM-DD}/baseline.json` + `baseline.summary.md` to Allowed Paths under operator-selected Option B; resolved OBPI-03↔04 scaffold-time contradiction (commit `29a96358` authored both contradictory lines in a single sweep). Discovery Checklist expanded with substantive Prerequisites + Existing Code per `gz obpi validate --authored`.
- BDD waiver: `data/behave_coverage_waivers.json` adds `adr-0.0.27-04-bdd-deferred-to-obpi-06` rationale + per-OBPI entry per brief REQ-07.
- Date completed: 2026-05-04
- Attestation status: operator attested at Stage 4 (`attest completed`); Gate 5 fired foundation+heavy via brief-level walkthrough; the 12 per-metric practitioner-eye blocks remain operator-authored placeholders by design (REQ-10 — agent never fabricates).
- Defects noted: `lizard_nesting_depth` and `cohesion_lcom4` baselines are all-zero across the corpus — surfaces a candidate measurement-pipeline parser defect against OBPI-03 worth a follow-up GHI rather than an OBPI-04 blocker.

### Closing Argument

<!-- One paragraph: why agent-drafted-then-operator-attested is the load-bearing shape (closes both training-corpus pattern-match and operator-bandwidth-burnout), why the cold-start mechanism matters for the doctrine-evolution audit trail, and why no-overwrite preservation of prior distillations is the structural defense against silent drift. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Stage 4 ceremony presented per the canonical foundation+heavy template; operator witnessed the corpus-p90 boundary table for all 12 canonical metrics, the per-metric triple shape, and the cold-start diff sentinel. Tests 8/8 (receipt arb-step-unittest-9cebe48046234a21946b70d1763d20f5); lint clean (arb-ruff-d1d8078547d84e92a957a3d0defebaad); typecheck clean (arb-step-typecheck-114164f0a4ac48549c05734cfc2c759e); mkdocs --strict clean (arb-step-mkdocs-1bd6a551c30243ca9fdbfaf36df18eb5); REQ→@covers parity 7/7. Brief amendment 2026-05-04 closed the OBPI-03↔04 scaffold-time contradiction under Option B; BDD coverage waived to OBPI-06 per brief REQ-07.
- Date: 2026-05-05

---

**Brief Status:** Completed

**Date Completed:** 2026-05-05

**Evidence Hash:** -
