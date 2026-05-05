# Plan — OBPI-0.0.27-04-distillation-pass

OBPI: `OBPI-0.0.27-04-distillation-pass`
Parent ADR: `ADR-0.0.27-exemplar-corpus-doctrine`
Lane: Heavy
Kind: Foundation (brief-level Gate 5 attestation required, three-axis: foundation+heavy)
Plan date: 2026-05-04
Brief amendment: 2026-05-04 — added `docs/governance/complexity/baselines/{YYYY-MM-DD}/baseline.json` and `baseline.summary.md` to Allowed Paths under operator-selected Option B (resolves OBPI-03↔04 scaffold-time contradiction; OBPI-03 brief line 35 said "first dated baseline lands at OBPI-04 invocation" but OBPI-04 STOP-on-BLOCKERS at line 56 named the artifact a precondition).

## Context

### Destination-in-mind (per § Plan-Before-Exploration Ordering)

Before authoring this plan I had this approach in mind: invoke the OBPI-03 `measure_corpus()` pipeline against the live 13-project corpus to land the first dated baseline at `docs/governance/complexity/baselines/2026-05-04/`, then TDD-author a `distillation.py` diff-narration module and a per-metric structured `distilled-characteristics-2026-05-04.md` document where the agent drafts the metric-aggregate prose and the operator attests the practitioner-eye observation per metric at Gate 5.

### Rejected alternatives

1. **Synthetic-only baseline.** Rejected — fails the foundation-doctrine "load-bearing artifact cited by ADR-0.0.28/0.0.29/0.0.30" constraint. Tests use synthetic fixtures (REQ-08), but the production document needs a real baseline.
2. **Manual operator-typed boundaries.** Rejected — violates OEE doctrine (agent drafts substantively; operator reviews). Operator's typing budget is the scarce resource.
3. **Skip the measurement clone, invoke measurement against a single local-checkout subset.** Rejected — corpus is the doctrine; the baseline that anchors ADRs 28/29/30 must be the full 13-project measurement, not a partial one. Operator green-lit the full clone via Option B selection.
4. **Single combined module + tests + doc commit.** Rejected — TDD discipline (REQ-08) and Gate 5 walkthrough (per-metric attestation) require a staged authoring sequence with the operator in the loop.
5. **Defer distillation.py until the diff mechanism actually fires.** Rejected — REQ-04 explicitly canonizes the cold-start no-op presence; first-run absence-of-mechanism is a documented audit-trail surface, not deferred work.

## Files

### Created

- `docs/governance/complexity/baselines/2026-05-04/baseline.json` — first dated baseline artifact, produced by `measure_corpus()` against `data/exemplar_corpus.json`
- `docs/governance/complexity/baselines/2026-05-04/baseline.summary.md` — companion summary
- `docs/governance/complexity/distilled-characteristics-2026-05-04.md` — first distilled doctrine document with frontmatter, per-metric triples, citation form, cold-start diff section
- `src/gzkit/complexity/distillation.py` — diff-narration mechanism (cold-start no-op; full diff in subsequent runs)
- `tests/complexity/test_distillation.py` — REQ-derived assertions on document shape and diff mechanism (each test `@covers(REQ-0.0.27-04-NN)`)

### Modified

- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-04-distillation-pass.md` — Evidence sections (Implementation Summary, Key Proof, Closing Argument, Gate 1-5 evidence) populated at Stage 4-5

## Steps

### 1. RED: author failing tests (`tests/complexity/test_distillation.py`)

Write one test per REQ that the tests cover, each decorated with `@covers("REQ-0.0.27-04-NN")`. Test scope (per REQ-07):

- `test_document_frontmatter_validates_against_schema` — REQ-01: frontmatter declares `corpus_revision`, `baseline_artifact_path`, `distillation_date`, `prior_distillation_path`
- `test_per_metric_triple_present_for_each_canonical_metric` — REQ-02: each metric section has (a) percentile + absolute boundary, (b) qualitative band, (c) doctrinal frame
- `test_cold_start_diff_section_states_no_prior_distillation` — REQ-03/04: first-run document carries cold-start sentinel
- `test_subsequent_run_diff_section_lists_boundary_movements` — REQ-04: synthetic shifted baseline produces narrated movements > 10%
- `test_existing_dated_document_not_overwritten` — REQ-05: rerunning on same date produces `-1`-suffixed file or rejects
- `test_citation_form_section_quotes_canonical_tuple` — REQ-06: `(file path, section anchor, corpus_revision)`
- `test_practitioner_eye_block_required_for_every_metric` — REQ-10: agent never fabricates the practitioner-eye block

Tests use synthetic baseline fixtures via `tempfile.TemporaryDirectory` (REQ-08). No live-tool dependency, no real-clone dependency in the unit tier.

Verify: `uv run -m unittest tests.complexity.test_distillation -v` — expected failures (RED).

### 2. GREEN: implement `src/gzkit/complexity/distillation.py`

Module functions:

- `class DistilledCharacteristics(BaseModel)` with `ConfigDict(frozen=True, extra="forbid")` for the document's frontmatter contract.
- `class PerMetricTriple(BaseModel)` — `(percentile, absolute, band, doctrinal_frame)`.
- `def render_document(baseline: BaselineArtifact, prior_distillation: Path | None, output_path: Path) -> Path` — canonical entrypoint. Asserts no overwrite (REQ-05); on collision, writes a `-1`-suffixed sibling.
- `def render_diff_section(prior_distillation: Path | None, current_baseline: BaselineArtifact) -> str` — cold-start branch returns the canonical sentinel; subsequent-run branch lists every metric whose boundary moved > 10% with operator narration placeholders.
- `def render_metric_triple(metric_name: str, distribution: dict) -> str` — formats `(percentile-of-corpus AND absolute-number-at-that-percentile, qualitative band, doctrinal frame)`. The doctrinal frame is selected from a static map citing Fowler / Martin / Page-Jones / Constantine per metric.
- `def write_practitioner_eye_placeholder(metric_name: str) -> str` — emits a `<!-- OPERATOR: practitioner-eye observation here per OEE doctrine -->` placeholder (NOT agent prose).

Function size discipline per `.claude/rules/pythonic.md` (≤ 50 lines per function, ≤ 600-line module).

Verify: tests now PASS.

### 3. REFACTOR: ensure module passes lint/typecheck

```bash
uv run ruff check src/gzkit/complexity/distillation.py tests/complexity/test_distillation.py --fix
uv run ruff format src/gzkit/complexity/distillation.py tests/complexity/test_distillation.py
uv run ty check
```

### 4. Land the first dated baseline (operator-greenlit clone of 13 corpus projects)

```bash
uv run python -c "
from pathlib import Path
from gzkit.models.exemplar import load_corpus
from gzkit.complexity.measurement import measure_corpus
corpus = load_corpus(Path('data/exemplar_corpus.json'))
output_dir = Path('docs/governance/complexity/baselines/2026-05-04')
output_dir.mkdir(parents=True, exist_ok=True)
artifact = measure_corpus(corpus, output_dir)
print(f'Baseline written: {output_dir}/baseline.json')
"
```

Tools (`radon`, `lizard`, `cohesion`) verified installed at Stage 1. Network/clone time: 13 pinned-SHA repositories. Caches reused across re-invocations.

### 5. Render the cold-start distilled-characteristics document

Invoke `distillation.render_document(baseline, prior_distillation=None, output_path=Path("docs/governance/complexity/distilled-characteristics-2026-05-04.md"))`. The agent fills metric-aggregate prose per metric (median, p75, p90, p95, p99 with inter-project variance commentary) and inserts the operator-attested-practitioner-eye placeholders.

Document sections:

- YAML frontmatter (`corpus_revision: 1`, `baseline_artifact_path: docs/governance/complexity/baselines/2026-05-04/baseline.json`, `distillation_date: 2026-05-04`, `prior_distillation_path: null`)
- One section per canonical metric in the OBPI-03 baseline, each with the per-metric triple + agent-drafted percentile prose + practitioner-eye placeholder for the operator
- "Diff against prior distillation" section — cold-start sentinel
- "Citation form" section quoting `.gzkit/rules/complexity-doctrine.md`

### 6. Heavy-lane gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.complexity.test_distillation -v
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
```

BDD (Gate 4) — REQ-07 mentions the second-run diff scenario; the brief allows registering a behave waiver if real-clone is too heavy for CI. Decision recorded at brief amendment time: register waiver in `data/behave_coverage_waivers.json` consistent with OBPI-01/02 precedents under the same parent ADR.

### 7. Stage 4 ceremony — operator practitioner-eye attestation per metric

Render the Stage 4 evidence ceremony using the canonical OBPI-pipeline template. Each metric requires the operator's practitioner-eye observation to be authored verbatim into the distilled document and to be attested at Gate 5. The agent never authors the practitioner-eye prose — only the placeholder. PTY + `ATTEST` (or `--attestor-present` per the active pipeline marker — GHI #292) for each foundation+heavy attestation transaction.

### 8. Stage 5 — `gz obpi precomplete`, `gz obpi complete`, lock release, two-sync pattern

Standard OBPI-pipeline Stage 5: precomplete check; closure-narrative gate (Implementation Summary + Key Proof preview); `gz obpi complete OBPI-0.0.27-04-distillation-pass --attestor-present --attestation-text "<operator-verbatim — em-dash — concrete enrichment with arb-ruff-* / arb-step-typecheck-* / arb-step-unittest-* / arb-step-mkdocs-* receipt IDs>"`; lock release; marker cleanup; git-sync #1; `gz obpi reconcile`; `gz adr status ADR-0.0.27 --json`; git-sync #2.

## Verification

```bash
uv run gz arb ruff                                                            # arb-ruff-*
uv run gz arb typecheck                                                       # arb-step-typecheck-*
uv run gz arb step --name unittest -- uv run -m unittest tests.complexity.test_distillation -v  # arb-step-unittest-*
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict              # arb-step-mkdocs-*
uv run gz validate --documents
test -f docs/governance/complexity/baselines/2026-05-04/baseline.json
test -f docs/governance/complexity/distilled-characteristics-2026-05-04.md
uv run gz covers OBPI-0.0.27-04-distillation-pass --json   # parity gate
uv run gz obpi precomplete OBPI-0.0.27-04-distillation-pass
```

## Notes

- The plan's REAL clone of 13 corpus projects is the long-pole step. Network access required. Operator-greenlit at Option B selection; if the clone fails for any project, the brief's STOP-on-BLOCKERS doctrine and the corpus pinning (REQ-08 of OBPI-03) require the run to fail closed, not to silently fall back to a partial baseline.
- `distillation.py` carries the diff-narration mechanism even on first run — cold-start branch is canonized in REQ-04 as a structural surface, not a temporary affordance.
- BDD waiver follows the OBPI-01/02 precedent in `data/behave_coverage_waivers.json` for the same parent ADR; cross-clone heavy scenarios are too costly for CI, real-clone integration coverage is structurally validated by the live measurement run that produces the baseline.
- The `docs/governance/complexity/distilled-characteristics.md` symlink/pointer file (named in OBPI-04 Allowed Paths as optional) is deferred to OBPI-06 (`gz-complexity-distill` skill) where the operator-runnable invocation has the natural seam to maintain the pointer. Recording the deferral here so the OBPI-04 brief's "optional; pattern decided in this OBPI" clause is closed: pattern decided is "OBPI-06 owns the pointer."
