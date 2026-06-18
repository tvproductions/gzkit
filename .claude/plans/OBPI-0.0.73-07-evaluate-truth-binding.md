# Plan: OBPI-0.0.73-07-evaluate-truth-binding

**Parent ADR:** ADR-0.0.73-verification-layer-binding-audit (foundation, heavy)
**Homes:** GHI #624 — `gz adr evaluate` dim-1/dim-2 grade prose SHAPE & KEYWORDS, not decision SUBSTANCE.

## Destination-in-mind (plan-before-exploration disclosure)

Before exploring I expected to: replace `_has_keywords`/numbered-list regex checks in
`_score_problem_clarity` and `_score_decision_justification` with structural substance
checks, add a self-registration channel to `qc_binding.py`, and add a 7th theater
signature. Exploration confirmed this shape and surfaced two coupled surfaces the brief
under-declared (now amended).

## Rejected alternatives

- **Rewrite the whole 8-dimension scorer.** Rejected — surgical (Rule 11): only dim-1/dim-2
  grade on keyword/format heuristics (the GHI #624 defect). Dims 3-8 use structural checks
  (path refs, section presence, counts) that already grade substance; touching them is
  taste-driven cleanup, out of scope.
- **Self-register via `_build_check_steps()` in quality.py.** Rejected — `gz adr evaluate` is
  not a `gz check` step; forcing it into that derived list would corrupt the bound-step
  registry. Instead add a separate advisory self-registration channel in qc_binding.py.
- **Make dim-1/dim-2 keyword-blind entirely.** Rejected — keywords are weak positive signal;
  the defect is keyword presence *alone* lifting the score and keyword *absence* flooring a
  rigorous ADR. Fix: grade structural substance (word depth, path/command refs, explicit
  rejected-alternatives, honest consequences) so neither keyword presence nor absence is
  decisive.

## Context

- `_score_problem_clarity` (`src/gzkit/adr_eval_scoring.py:23`): checks 3 & 4 use
  `_has_keywords(intent, ["before",...])` / `_has_keywords(intent, ["after",...])`.
- `_score_decision_justification` (`src/gzkit/adr_eval_scoring.py:42`): check 2 is a
  `^\d+\.` numbered-list regex; check 3 is `_has_keywords(decision, ["because",...])`.
- `build_qc_registry()` (`src/gzkit/qc_binding.py:114`) derives bound steps from
  `_build_check_steps()`; no advisory self-registration channel exists yet.
- `THEATER_SIGNATURES` (`src/gzkit/governance/trust_audits/qc_binding.py:26`): six-tuple;
  `_check_theater_signatures` (line 146) fires on any flag in the tuple.
- Facade corpus: 6 `.json` fixtures in `tests/governance/fixtures/facade_corpus/`;
  `test_facade_regression_corpus.py:94` asserts fixture count == `len(THEATER_SIGNATURES)`.

## Files

- `src/gzkit/adr_eval_scoring.py` — substance checks for dim-1/dim-2; module-level self-register call
- `src/gzkit/qc_binding.py` — `register_advisory_qc_step()` + `_SELF_REGISTERED_ADVISORY_STEPS`; extend `build_qc_registry()`
- `src/gzkit/governance/trust_audits/qc_binding.py` — add `shape-graded-not-substance` to `THEATER_SIGNATURES` + description
- `tests/governance/fixtures/facade_corpus/shape_graded_not_substance.json` **CREATE**
- `tests/governance/test_adr_eval_truth_binding.py` **CREATE**
- `tests/governance/test_facade_regression_corpus.py` — 7th-signature test + count assertion update
- `docs/user/manpages/adr-evaluate.md` — substance-grading + QC-step registration sections

## Steps

1. **Substance checks (RED→GREEN):** Rewrite dim-1 checks 3/4 and dim-2 checks 2/3 in
   `adr_eval_scoring.py`. Dim-1: (3) intent depth `_word_count > 150`, (4) concrete reference
   `re.search(r'`[^`]+`|src/|tests/|GHI #|OBPI-|ADR-', intent)`. Dim-2: (2) decision depth
   `_word_count(decision) > 100`, (3) explicit rejected-alternative language in Alternatives
   section (`REJECTED`/`rejected`/`instead of`/`over`) OR honest `### Negative` consequences.
   Keep `_has_keywords` import if still used elsewhere; else drop with its usage.
2. **Self-registration channel (qc_binding.py):** add `_SELF_REGISTERED_ADVISORY_STEPS:
   list[QCStep] = []`, `register_advisory_qc_step(...)` (constructs an advisory QCStep,
   appends, dedups by id), and append the list in `build_qc_registry()`.
3. **Self-register the evaluator:** at module bottom of `adr_eval_scoring.py`, call
   `register_advisory_qc_step` for "ADR Evaluate" (kind=audit, subject=docs/,
   wired_into=["gz adr evaluate"], binding=advisory, locus=python_function).
4. **7th theater signature:** add `"shape-graded-not-substance"` to `THEATER_SIGNATURES` and
   a `_THEATER_SIGNATURE_DESCRIPTIONS` entry.
5. **Fixture:** create `shape_graded_not_substance.json` (advisory step, flag
   `shape-graded-not-substance`, wired_into `["gz adr evaluate"]`).
6. **Tests (`test_adr_eval_truth_binding.py`):** REQ-01 (rigorous keyword-free ADR not
   floored), REQ-02 (keyword-stuffed hollow ADR not lifted by keywords alone), REQ-03
   (registry includes advisory "ADR Evaluate"), REQ-04 (fixture detected). `@covers` each.
7. **Corpus test:** add `test_shape_graded_not_substance_detected`; the count assertion
   stays correct (auto-counts `len(THEATER_SIGNATURES)`) but add the 7th case + rename
   docstring/method if "six" is hardcoded in prose.
8. **Manpage:** add Substance-Grading + QC-Step Registration sections to `adr-evaluate.md`.

## Verification

- `uv run gz arb ruff`
- `uv run gz arb typecheck`
- `uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_adr_eval_truth_binding tests.governance.test_facade_regression_corpus -v`
- `uv run gz covers OBPI-0.0.73-07-evaluate-truth-binding --json`
- `uv run gz validate --qc-binding`
- `uv run gz validate --cli-alignment`
- `uv run gz validate --documents`
- `uv run gz adr evaluate ADR-0.0.73-verification-layer-binding-audit`

## Notes

- Surgical: only dim-1/dim-2 touched in the scorer; dims 3-8 untouched.
- Pre-existing defect (out of scope): sibling OBPI-05 brief fails `gz validate --sensitivity`
  (exit 3) — confirmed pre-existing on clean HEAD, not introduced here. Recorded in insights.
