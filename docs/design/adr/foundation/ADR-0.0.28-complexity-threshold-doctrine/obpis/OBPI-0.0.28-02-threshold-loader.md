---
id: OBPI-0.0.28-02-threshold-loader
parent: ADR-0.0.28
item: 2
lane: Heavy
status: Draft
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

- [ ] OBPI-0.0.28-01 rule body shape — what the loader parses
- [ ] OBPI-0.0.27-05 `Citation` model at `src/gzkit/complexity/citation.py` — imported, not duplicated
- [ ] `.claude/rules/models.md` — Pydantic immutable model patterns
- [ ] `.claude/rules/pythonic.md` — function-size and import discipline
- [ ] AGENTS.md § STDLIB-FIRST DOCTRINE — no new dependencies; pydantic is the named departure already canonized

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

<!-- Paste the band_for lookup against a CC fixture demonstrating warn-band selection at value=13 with bands (p75=8/advise, p90=12/warn, p95=18/block). -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why a frozen Pydantic surface beats a per-consumer JSON parse (closes parser-divergence drift across three downstream consumers), why mandatory-block-per-metric is the load-bearing schema invariant (closes the "threshold that cannot fail" failure class), and why importing OBPI-0.0.27-05's Citation model is the right move (single citation parser across the cluster). -->

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
