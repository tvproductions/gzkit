# CHORE: Complexity Reduction (C/C/C ceiling)

**Lane:** Lite
**Slug:** `complexity-reduction-xenon`

> **Version 3.0.0 (2026-10-22, RO-9 tranche 4, GHI #1183):** Xenon and Radon are
> retired. The C/C/C ceiling is `gz validate --complexity-ceiling`, Lizard's
> native scores held at the `max-complexity` Ruff reads (20), and cognitive
> complexity is complexipy at `[tool.complexipy]`'s ceiling (15) with its own
> shrink-only snapshot. The slug keeps its historical name as a stable
> identifier.
>
> **Version 2.1.0 (2026-09-13, GHI #999):** The chore carries a class declaration
> in `registry.json` and each Workflow step declares its stage.
>
> **Version 2.0.0 (2026-04-25):** Integrated with the complexity-doctrine
> cluster (ADR-0.0.27 / 0.0.28 / 0.0.29 / 0.0.30).

---

## Overview

Reduce complexity in the shipped package. Two gates hold it:

- **Cyclomatic C/C/C** (`gz validate --complexity-ceiling`): the largest function,
  each module's mean and the function-weighted overall mean, each at most the
  `[tool.ruff.lint.mccabe] max-complexity` Ruff enforces as C901.
- **Cognitive** (`uv run complexipy -q`): no new or worsened function over
  `[tool.complexipy] max-complexity-allowed`; the functions over it on
  2026-10-22 are held to their scores in `complexipy-snapshot.json`, which
  tightens itself as they improve.

## Policy and Guardrails

- **Lane:** Lite — internal refactoring, no external contract changes
- Tidy-first: extract helpers, remove nesting, keep behavior unchanged
- Tests must stay green
- **Diagnosis-aware:** run `gz complexity advise --json <paths>` and use the
  structured `AdvisorDiagnosis` to choose the refactor; do NOT pattern-match
  refactor archetypes from training memory
- Never raise a ceiling or re-seed the snapshot to make the chore pass

## Workflow

### 1. Baseline — observe

```bash
uv run gz validate --complexity-ceiling
uv run complexipy --top 20
uv run gz complexity advise --json src/ > .gzkit/chores/complexity-reduction-xenon/proofs/advisor-diagnosis-baseline.json
```

### 2. Plan — propose

- Start with the snapshot's highest cognitive scores and any advisor `block` crossings
- Small batch (3-5 functions) per commit; record operator-witnessed diagnosis
  acceptance in `.gzkit/chores/complexity-reduction-xenon/proofs/diagnosis-acceptance-{date}.md`

### 3. Implement — repair

- Extract helpers per the advisor-recommended refactor archetype (`Long Parameter List → Parameter Object`, `Arrowhead → Guard Clauses`, etc.)
- Pre-attest functions whose complexity is irreducibly algorithmic via the `@intrinsic_complexity` decorator (ADR-0.0.29 OBPI-07) rather than refactoring them artificially
- Run `uv run complexipy -q` after each batch; an improved function lowers its snapshot row, and the lowered snapshot is committed with the refactor

### 4. Validate — observe

```bash
uv run gz validate --complexity-ceiling
uv run complexipy -q
uv run gz test
```

## Checklist

- [ ] `gz validate --complexity-ceiling` passes
- [ ] `complexipy-snapshot.json` has fewer or lower rows than at the baseline
- [ ] Tests pass unchanged
- [ ] Operator-witnessed diagnosis acceptance recorded for each non-trivial crossing under `.gzkit/chores/complexity-reduction-xenon/proofs/`

## Acceptance Criteria

Criteria live in `acceptance.json`, which `gz chores run` executes; render them with `uv run gz chores plan complexity-reduction-xenon`. This section explains them and does not restate them (GHI #1002).

The gate is the C/C/C ceiling, the cognitive ratchet and the unit suite. The
operator-witnessed diagnosis-acceptance record (§ 2 Plan) is a workflow
obligation, not a criterion.

## Evidence Commands

```bash
uv run gz validate --complexity-ceiling > .gzkit/chores/complexity-reduction-xenon/proofs/ceiling-report.txt
uv run complexipy --output-format json --output .gzkit/chores/complexity-reduction-xenon/proofs/cognitive-report.json
```

## Cluster Linkage

This chore consumes the four-ADR complexity-doctrine cluster:

- ADR-0.0.27 (corpus + distillation) — provides the empirical basis for threshold values
- ADR-0.0.28 (threshold table) — provides the canonical (metric, percentile-band, absolute-number, trigger-semantic) tuples
- ADR-0.0.29 (advisor) — provides `gz complexity advise` for trigger-time diagnosis
- ADR-0.0.30 (authoring guidance) — provides `gz complexity guide` for upstream-prevention preview

---

**End of CHORE: Complexity Reduction (C/C/C ceiling)**
