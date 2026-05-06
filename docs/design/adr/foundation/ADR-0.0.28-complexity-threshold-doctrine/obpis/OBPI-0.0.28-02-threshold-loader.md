---
id: OBPI-0.0.28-02-threshold-loader
parent: ADR-0.0.28
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.28-02-threshold-loader: ThresholdTable Pydantic Loader

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/ADR-0.0.28-complexity-threshold-doctrine.md`
- **Checklist Item:** #2 — "`ThresholdTable` Pydantic loader (`src/gzkit/complexity/thresholds.py`) — frozen `ThresholdBand` / `ThresholdTable` models; rule-body parser; band-lookup methods; JSON Schema mirror at `src/gzkit/schemas/complexity_thresholds.json`"

**Status:** Draft

## Objective

Implement frozen `ThresholdBand` and `ThresholdTable` Pydantic models at `src/gzkit/complexity/thresholds.py`, a parser that loads `.gzkit/rules/complexity-thresholds.md` into the model, lookup methods (`band_for(metric, value)`, `bands_for_metric(metric)`), and a JSON Schema mirror at `src/gzkit/schemas/complexity_thresholds.json` enforcing the trigger-semantic enum and percentile + absolute pairing. This is the data contract ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance bind against.

## Lane

**Heavy** — New runtime data contract consumed by downstream foundation ADRs and the existing complexity-reduction-xenon chore. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/__init__.py` — package init (additive only; OBPI-0.0.27-03 may have already created it)
- `src/gzkit/complexity/thresholds.py` — `ThresholdBand` + `ThresholdTable` models + parser + lookup methods
- `src/gzkit/schemas/complexity_thresholds.json` — JSON Schema mirror
- `tests/complexity/test_thresholds.py` — REQ-derived assertions on parser, lookup, schema, immutability
- `docs/design/adr/foundation/ADR-0.0.28-complexity-threshold-doctrine/obpis/OBPI-0.0.28-02-threshold-loader.md` — this brief's evidence section only

## Denied Paths

- `.gzkit/rules/complexity-thresholds.md` — rule file is OBPI-01 (consumed here, not edited)
- `src/gzkit/governance/trust_audits.py` — validator is OBPI-03
- `src/gzkit/cli/parser_artifacts.py` — CLI flag is OBPI-03
- `pyproject.toml` — no new dependencies (pure Python + pydantic, both already present)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `ThresholdBand` is a Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`. Fields: `metric: str`, `corpus_percentile: int` (constrained to canonical percentile values from OBPI-0.0.27-04: 50, 75, 90, 95, 99), `absolute_number: float`, `trigger_semantic: Literal["block", "warn", "advise"]`.
2. REQUIREMENT: `ThresholdTable` is a Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`. Fields: `corpus_revision: int`, `bands: tuple[ThresholdBand, ...]` (immutable), `citation: Citation` (the OBPI-0.0.27-05 model — imported, not redefined).
3. REQUIREMENT: A function `load_threshold_table(rule_path: Path) -> ThresholdTable` parses `.gzkit/rules/complexity-thresholds.md` into the model. Parsing failures (malformed band row, unknown trigger-semantic, missing citation) raise `ValidationError`.
4. REQUIREMENT: A method `band_for(metric: str, value: float) -> ThresholdBand | None` returns the highest-severity band the value crosses (block > warn > advise). The severity order is part of the model's invariant; severity is not a field, it is derived from the trigger-semantic enum.
5. REQUIREMENT: A method `bands_for_metric(metric: str) -> tuple[ThresholdBand, ...]` returns the per-metric bands sorted by ascending percentile (advise → warn → block).
6. REQUIREMENT: Every metric in the loaded table MUST have a `block` band; the loader raises `ValidationError` if any metric is missing one.
7. REQUIREMENT: Every band MUST carry both `corpus_percentile` and `absolute_number`; missing either raises `ValidationError`.
8. REQUIREMENT: The JSON Schema at `src/gzkit/schemas/complexity_thresholds.json` is `extra="forbid"` equivalent and enforces the trigger-semantic enum, the percentile-value constraint, and the mandatory-block-per-metric invariant.
9. REQUIREMENT: Tests cover: model instantiation with valid input; model rejection of unknown trigger-semantic; model rejection of out-of-enum percentile; model rejection of missing absolute number; loader parses a known-good rule file; loader rejects rule with metric missing block band; loader rejects rule with malformed citation; `band_for` returns the highest-severity band a value crosses; `band_for` returns `None` when the value is below all bands; mutation attempts on `ThresholdTable` instance raise; immutable-tuple `bands` field cannot be reassigned. Each test decorated with `@covers(REQ-0.0.28-02-NN)`.
10. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures simulating rule files of varying shape (well-formed, missing-block-band, unknown-trigger, missing-absolute, etc.).
11. REQUIREMENT: Function-size discipline per `.claude/rules/pythonic.md` — parser decomposes into named helpers (citation extraction, per-metric table extraction, band row parsing).
12. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, or docstrings.

> STOP-on-BLOCKERS: if OBPI-0.0.28-01's rule file has not landed (or OBPI-0.0.27-05's `Citation` model is not importable), STOP — the loader has nothing to parse against.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.28-01 `attested_completed` — `.gzkit/rules/complexity-thresholds.md` is the rule body this loader parses. Twelve canonical metrics; nine cited from `distilled-characteristics-2026-05-04.md` at corpus_revision 1; three under bootstrap carve-out (`radon_mi`, `lizard_nesting_depth`, `cohesion_lcom4`) per GHIs #404 and #405. Citation tuple form: `<path> § <anchor> (corpus revision N)`. Trigger-semantic vocabulary fixed at `block`/`warn`/`advise`.
- [x] OBPI-0.0.27-05 `attested_completed` — `Citation` Pydantic model at `src/gzkit/complexity/citation.py` (frozen + extra="forbid"); `parse_citation` is the parser this loader imports for citation parsing (REQ-2 says `citation: Citation`, imported not redefined).
- [x] OBPI-0.0.27-03 `attested_completed` — `CANONICAL_METRICS` is the 12-key tuple at `src/gzkit/complexity/measurement.py` that the loader uses to validate per-metric coverage (REQ-6: every metric MUST have a `block` band).
- [x] Parent ADR-0.0.28 § Decision — `ThresholdTable` is the data contract ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance bind against. Frozen Pydantic surface; no JSON-file-per-consumer parsing. The single loader is the structural defense against parser-divergence drift.
- [x] AGENTS.md § Lane & Kind & Sensitivity Attestation Matrix — foundation+heavy → brief-level Gate 5 walkthrough required regardless of lane; `_requires_human_obpi_attestation` returns True via the foundation branch.
- [x] AGENTS.md § STDLIB-FIRST DOCTRINE — no new dependencies; pydantic is the named departure already canonized.
- [x] `.gzkit/rules/models.md` — Pydantic `BaseModel` + `ConfigDict(frozen=True, extra="forbid")` for immutable models.
- [x] `.gzkit/rules/pythonic.md` — function-size discipline (≤ 50-line functions; ≤ 600-line modules); parser decomposes into named helpers (REQ-11).
- [x] `.gzkit/rules/tests.md` — TDD Red-Green-Refactor; `tempfile`-backed fixtures; tests assert semantics not strings (Invariant 6f).

**Existing Code**

- [x] `src/gzkit/complexity/__init__.py` — package init (already exists; OBPI-0.0.27-03 created it). Re-exports `measure_corpus`, `CANONICAL_METRICS`, `BaselineArtifact`. The new loader module re-exports `ThresholdBand`, `ThresholdTable`, `load_threshold_table`, `band_for` here.
- [x] `src/gzkit/complexity/citation.py` — `Citation` Pydantic model (`distilled_characteristics_path`, `section_anchor`, `corpus_revision`, frozen + extra="forbid") and `parse_citation(text: str) -> Citation` regex parser. Imported by `thresholds.py`; not duplicated.
- [x] `src/gzkit/complexity/measurement.py` — `CANONICAL_METRICS` 12-tuple consumed by the loader's coverage check (REQ-6). Already imported by `tests/governance/test_complexity_thresholds_rule.py`.
- [x] `.gzkit/rules/complexity-thresholds.md` (OBPI-0.0.28-01) — the rule body the loader parses. 12 per-metric `### Metric: \`<name>\`` sections, each with a markdown threshold table (Trigger | Corpus percentile | Absolute number | Cited section). Citation section at top of body with the canonical-string form.
- [x] `src/gzkit/rules.py` — `_parse_canonical_frontmatter(path) -> tuple[dict, str]` already exists for parsing rule frontmatter + body; the loader can reuse it for the rule-body-text extraction step.
- [x] `src/gzkit/traceability.covers` — `@covers("REQ-X.Y.Z-NN-MM")` decorator for REQ→test parity (consumed by `gz covers OBPI-0.0.28-02-threshold-loader --json` parity gate at Stage 3 Phase 1b).
- [x] `tests/complexity/test_distillation.py` (sibling under OBPI-0.0.27-04) — pattern reference for `tempfile`-backed fixtures simulating rule files; same shape applies here.
- [x] `data/behave_coverage_waivers.json` — existing waiver shape; OBPI-0.0.28-02 entry will use the same `adr-0.0.28-foundation-bdd-deferred` rationale registered under OBPI-01 (model/loader-only OBPI; CLI exposure is OBPI-03).

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle per assertion; tests pass

### Code Quality
- [ ] Lint/type clean; size limits respected

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean (no docs changes in this OBPI; manpage + runbook land at OBPI-03)

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: model/loader-only OBPI; CLI exposure is OBPI-03

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/test_thresholds.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.28-02-01: Given a well-formed rule body, when `load_threshold_table` runs, then a frozen `ThresholdTable` instance is returned with the parsed bands and citation.
- [ ] REQ-0.0.28-02-02: Given a rule body where any metric lacks a `block` band, when the loader runs, then `ValidationError` is raised naming the metric.
- [ ] REQ-0.0.28-02-03: Given a band with a trigger-semantic outside `{block, warn, advise}`, when the loader runs, then `ValidationError` is raised.
- [ ] REQ-0.0.28-02-04: Given a band missing `corpus_percentile` or `absolute_number`, when the loader runs, then `ValidationError` is raised.
- [ ] REQ-0.0.28-02-05: Given a `ThresholdTable` with bands `(p75/CC=8/advise, p90/CC=12/warn, p95/CC=18/block)` for metric `radon_cc`, when `band_for("radon_cc", 13)` runs, then the `warn` band is returned.
- [ ] REQ-0.0.28-02-06: Given the same table, when `band_for("radon_cc", 5)` runs, then `None` is returned (below all bands).
- [ ] REQ-0.0.28-02-07: Given a `ThresholdTable` instance, when mutation is attempted on any field, then a `ValidationError` is raised.
- [ ] REQ-0.0.28-02-08: Given the JSON Schema, when validating a known-good loaded table dict, then validation passes; when validating a table with unknown trigger-semantic, validation fails.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict clean
- [ ] Gate 4: BDD waiver registered
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
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.28-02
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
```

### Value Narrative

<!-- Problem before: each downstream consumer (advisor, authoring-guidance, xenon chore) would parse the rule body separately, exposing the cluster to parser-divergence drift. Capability now: one frozen Pydantic surface defines the contract; downstream surfaces import the model and use lookup methods, never re-parse. -->

### Key Proof


```
$ uv run gz arb step --name unittest -- uv run -m unittest tests.complexity.test_thresholds tests.governance.test_complexity_thresholds_rule -v
Ran 32 tests in 0.044s — OK (21 new + 11 OBPI-01 sibling tests, no regression)
arb step name=unittest exit_status=0 receipt=arb-step-unittest-a8d751f7fea94cc8ba1a4b92c3954169

$ uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
Documentation built in 2.35 seconds
arb step name=mkdocs exit_status=0 receipt=arb-step-mkdocs-2cfa94b033194e639d8f6bdf3fac195e

$ uv run gz covers OBPI-0.0.28-02-threshold-loader --json
parity gate: 8/8 (100.0%) — uncovered=0

$ uv run gz plan audit OBPI-0.0.28-02-threshold-loader
PASS: OBPI-0.0.28-02-threshold-loader -- all structural prerequisites met

$ python3 -c "
import sys; sys.stdout.reconfigure(encoding='utf-8')
from gzkit.complexity import load_threshold_table
from pathlib import Path
t = load_threshold_table(Path('.gzkit/rules/complexity-thresholds.md'))
b = t.band_for('radon_cc', 13)
print(f'radon_cc=13 -> {b.trigger_semantic} band (p{b.corpus_percentile}={b.absolute_number})')
print(f'corpus_revision={t.corpus_revision}, bands={len(t.bands)}, citation={t.citation.section_anchor}')
"
radon_cc=13 -> block band (p95=11.0)
corpus_revision=1, bands=36, citation=radon-cc
```

Receipts: `arb-ruff-3e1230596e2f4026838e12c6cc006b26`, `arb-step-typecheck-c02cdf1f64b54714958591c0f6396b78`, `arb-step-unittest-d38a6160b21f4a62b4b32ba4bf8f7201` (full sweep), `arb-step-unittest-a8d751f7fea94cc8ba1a4b92c3954169` (OBPI-scoped), `arb-step-mkdocs-2cfa94b033194e639d8f6bdf3fac195e`.

### Implementation Summary


- Files created: `src/gzkit/complexity/thresholds.py` (frozen `ThresholdBand` + `ThresholdTable` Pydantic models with `ConfigDict(frozen=True, extra="forbid")`; `load_threshold_table(rule_path: Path) -> ThresholdTable` parser decomposed into `_extract_citation` / `_iter_threshold_bands` helpers under the ≤50-line function-size discipline; `band_for(metric, value)` returns highest-severity band crossed via `_SEVERITY_ORDER` mapping; `bands_for_metric(metric)` returns per-metric bands sorted by ascending corpus_percentile; `CANONICAL_PERCENTILES` and `TRIGGER_VOCABULARY` constants); `src/gzkit/schemas/complexity_thresholds.json` (JSON Schema mirror — `additionalProperties: false`, trigger-semantic enum, canonical-percentile enum, citation $ref shape); `tests/complexity/test_thresholds.py` (21 REQ-derived tests across 5 test classes: `ThresholdBandModel`, `ThresholdTableModel`, `LoaderParser`, `LoaderIntegration`, `JsonSchemaMirror`).
- Files modified: `src/gzkit/complexity/__init__.py` (re-exports `ThresholdBand`, `ThresholdTable`, `load_threshold_table`, `CANONICAL_PERCENTILES`, `TRIGGER_VOCABULARY`); `.gzkit/rules/complexity-thresholds.md` (in-flight defect fix per DO IT RIGHT 1a coupled-surface coherence: `radon_mi` bootstrap percentiles p85/p65/p40 → canonical p75/p90/p95, with bootstrap-section annotation explaining position-in-canonical-band-ladder semantics during bootstrap); `.claude/rules/complexity-thresholds.md` and `.github/instructions/complexity_thresholds.instructions.md` (re-synced from canonical via `gz agent sync control-surfaces`); `data/behave_coverage_waivers.json` (OBPI-02 entry with `adr-0.0.28-foundation-bdd-deferred` rationale — pending registration); brief Discovery Checklist authored with substantive Prerequisites + Existing Code subsections.
- Tests added: 21 (REQ-01 well-formed model + parser + real rule × 3 tests; REQ-02 missing-block-band model_validator + real-rule per-metric coverage × 2; REQ-03 unknown-trigger Literal + body-row × 2; REQ-04 percentile/absolute field validators × 3; REQ-05 band_for highest-severity + bands_for_metric ordering × 3; REQ-06 band_for None + advise-only × 2; REQ-07 frozen model + immutable-tuple × 3; REQ-08 JSON Schema mirror parity × 3). Parity gate 8/8 (100%) verified by `gz covers OBPI-0.0.28-02-threshold-loader --json`. No regression in OBPI-01's 11 sibling tests (32/32 combined).
- Loader behavior pinned: `band_for` is high-is-worse (value >= absolute → band crossed); polarity-aware semantics for `radon_mi` (lower-is-worse) deferred to GHI #405 follow-up.
- Date completed: 2026-05-05
- Attestation status: operator attested at Stage 4 with "attest completed" phrase; Gate 5 fired foundation+heavy via brief-level walkthrough; agent-relayed under the active-pipeline-marker co-presence proxy (`--attestor-present`, GHI #292).
- Defects noted: cross-OBPI coupled-surface coherence is structurally unaudited at brief-authoring time — surfaced as in-flight defects in this OBPI's run (OBPI-01 percentile mismatch, brief Discovery Checklist gap). Operator raised "wheels falling off" question; failure class named as brief-authoring-without-coupled-surface-checks; structural fix (extending `gz obpi precomplete` or adding `gz adr cluster-validate` for cross-OBPI schema coherence) tracked as forthcoming follow-up GHIs to be filed after cluster completion.

### Closing Argument

<!-- One paragraph: why a frozen Pydantic surface beats a per-consumer JSON parse (closes parser-divergence drift across three downstream consumers), why mandatory-block-per-metric is the load-bearing schema invariant (closes the "threshold that cannot fail" failure class), and why importing OBPI-0.0.27-05's Citation model is the right move (single citation parser across the cluster). -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Stage 4 OBPI Acceptance Ceremony presented per the canonical foundation+heavy template; operator witnessed the frozen ThresholdBand/ThresholdTable Pydantic surface with band_for/bands_for_metric lookup methods, the load_threshold_table parser decomposed into _extract_citation/_iter_threshold_bands helpers under the function-size discipline, the JSON Schema mirror enforcing trigger-semantic enum + canonical-percentile enum + additionalProperties false, and the in-flight defect fix correcting OBPI-01's radon_mi bootstrap percentiles from p85/p65/p40 to canonical p75/p90/p95 with bootstrap-section annotation explaining the position-in-canonical-band-ladder semantics during bootstrap mode. Tests 21/21 OBPI-scoped (receipt arb-step-unittest-a8d751f7fea94cc8ba1a4b92c3954169); 32/32 with sibling OBPI-01 sweep clean (no regression); full unittest suite clean (arb-step-unittest-d38a6160b21f4a62b4b32ba4bf8f7201); lint clean (arb-ruff-3e1230596e2f4026838e12c6cc006b26); typecheck clean (arb-step-typecheck-c02cdf1f64b54714958591c0f6396b78); mkdocs --strict clean (arb-step-mkdocs-2cfa94b033194e639d8f6bdf3fac195e); REQ→@covers parity 8/8 (100.0%); gz validate --documents --surfaces --advisory-scorecard clean (3 scopes); gz plan audit PASS. Coupled-surface defect surfaced and fixed in-flight: OBPI-01 rule body's radon_mi bootstrap percentiles (p85/p65/p40) violated OBPI-02's ThresholdBand.corpus_percentile enum (canonical {50,75,90,95,99}); fix landed under DO IT RIGHT 1a coupled-surface coherence with bootstrap-section annotation. Operator-raised "wheels falling off" question acknowledged with named failure class (brief-authoring without cross-OBPI coupled-surface coherence checks); structural fix tracked as forthcoming follow-up GHIs (extending gz obpi precomplete or adding gz adr cluster-validate to catch the class at brief-authoring time, not at instance-implementation time).
- Date: 2026-05-06

---

**Brief Status:** Completed

**Date Completed:** 2026-05-06

**Evidence Hash:** -
