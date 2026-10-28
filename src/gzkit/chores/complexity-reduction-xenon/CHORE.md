# CHORE: Complexity Reduction (C/C/C ceiling)

**Lane:** Lite
**Slug:** `complexity-reduction-xenon`

> **Version 3.1.1 (2026-10-28, GHI #1183):** the remediation and non-authority
> text stop naming xenon as the current ceiling; the procedure is unchanged.
>
> **Version 3.1.0 (2026-10-22, RO-9 tranche 4):** complexipy is retired (operator,
> verbatim: *"so, this is a poor replacement: \"complexipy\""*). Cognitive
> complexity is scored by gzkit over CPython's `ast` and held by the same
> `gz validate --complexity-ceiling`, at `.gzkit.json`'s `complexity.cognitive_ceiling`
> (15), with the functions over it held in `data/cognitive_complexity_baseline.json`.
>
> **Version 3.0.0 (2026-10-22, RO-9 tranche 4, GHI #1183):** Xenon and Radon are
> retired. The C/C/C ceiling is `gz validate --complexity-ceiling`, Lizard's
> native scores held at the `max-complexity` Ruff reads (20). The slug keeps its
> historical name as a stable identifier.
>
> **Version 2.1.0 (2026-09-13, GHI #999):** The chore carries a class declaration
> in `registry.json` and each Workflow step declares its stage.
>
> **Version 2.0.0 (2026-04-25):** Integrated with the complexity-doctrine
> cluster (ADR-0.0.27 / 0.0.28 / 0.0.29 / 0.0.30).

---

## Overview

Reduce complexity in the shipped package. One gate, `gz validate --complexity-ceiling`,
holds it in two legs:

- **Cyclomatic C/C/C:** the largest function, each module's mean and the
  function-weighted overall mean, each at most the `[tool.ruff.lint.mccabe]
  max-complexity` Ruff enforces as C901.
- **Cognitive:** no function over `.gzkit.json`'s `complexity.cognitive_ceiling`
  unless `data/cognitive_complexity_baseline.json` holds it at no less than its
  score. The baseline is exact and shrinks only by hand: an improved function's row
  is lowered, or deleted at the ceiling, in the commit that improves it.

## Policy and Guardrails

- **Lane:** Lite — internal refactoring, no external contract changes
- Tidy-first: extract helpers, remove nesting, keep behavior unchanged
- Tests must stay green
- **Diagnosis-aware:** run `gz complexity advise --json <paths>` and use the
  structured `AdvisorDiagnosis` to choose the refactor; do NOT pattern-match
  refactor archetypes from training memory
- Never raise a ceiling, or raise or add a baseline row, to make the chore pass

## Workflow

### 1. Baseline — observe

```bash
uv run gz validate --complexity-ceiling
uv run python -m gzkit.complexity.cognitive src/gzkit --top 20
uv run gz complexity advise --json src/ > .gzkit/chores/complexity-reduction-xenon/proofs/advisor-diagnosis-baseline.json
```

### 2. Plan — propose

- Start with the baseline's highest cognitive scores and any advisor `block` crossings
- Small batch (3-5 functions) per commit; record operator-witnessed diagnosis
  acceptance in `.gzkit/chores/complexity-reduction-xenon/proofs/diagnosis-acceptance-{date}.md`

### 3. Implement — repair

- Extract helpers per the advisor-recommended refactor archetype (`Long Parameter List → Parameter Object`, `Arrowhead → Guard Clauses`, etc.)
- Pre-attest functions whose complexity is irreducibly algorithmic via the `@intrinsic_complexity` decorator (ADR-0.0.29 OBPI-07) rather than refactoring them artificially
- Run `uv run gz validate --complexity-ceiling` after each batch; it names each baseline row an improved function leaves inexact, and the lowered or deleted row, with `baseline_count` in `data/waiver_ratchet_registry.json`, is committed with the refactor

### 4. Validate — observe

```bash
uv run gz validate --complexity-ceiling
uv run gz test
```

## Checklist

- [ ] `gz validate --complexity-ceiling` passes
- [ ] `data/cognitive_complexity_baseline.json` has fewer or lower rows than at the baseline
- [ ] Tests pass unchanged
- [ ] Operator-witnessed diagnosis acceptance recorded for each non-trivial crossing under `.gzkit/chores/complexity-reduction-xenon/proofs/`

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan complexity-reduction-xenon`. This section explains them and does not restate them (GHI #1002).

The gate is the complexity ceiling (both legs) and the unit suite. The
operator-witnessed diagnosis-acceptance record (§ 2 Plan) is a workflow
obligation, not a criterion.

## Evidence Commands

```bash
uv run gz validate --complexity-ceiling > .gzkit/chores/complexity-reduction-xenon/proofs/ceiling-report.txt
uv run python -m gzkit.complexity.cognitive src/gzkit --json > .gzkit/chores/complexity-reduction-xenon/proofs/cognitive-report.json
```

## Cluster Linkage

This chore consumes the four-ADR complexity-doctrine cluster:

- ADR-0.0.27 (corpus + distillation) — provides the empirical basis for threshold values
- ADR-0.0.28 (threshold table) — provides the canonical (metric, percentile-band, absolute-number, trigger-semantic) tuples
- ADR-0.0.29 (advisor) — provides `gz complexity advise` for trigger-time diagnosis
- ADR-0.0.30 (authoring guidance) — provides `gz complexity guide` for upstream-prevention preview

---

**End of CHORE: Complexity Reduction (C/C/C ceiling)**
