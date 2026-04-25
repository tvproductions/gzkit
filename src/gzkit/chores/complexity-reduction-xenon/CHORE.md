# CHORE: Complexity Reduction (Xenon C/C/C Enforcement)

**Version:** 2.0.0
**Lane:** Lite
**Slug:** `complexity-reduction-xenon`

> **Version 2.0.0 (2026-04-25):** Strengthened to integrate with the
> complexity-doctrine cluster (ADR-0.0.27 / 0.0.28 / 0.0.29 / 0.0.30).
> Once ADR-0.0.29's `gz complexity-advise` lands, this chore consumes
> `gz complexity-advise --json` for diagnosis; once ADR-0.0.28's
> `ThresholdTable` lands, the xenon thresholds are derived from the
> table's `block` band rather than hard-coded `C/C/C`. Pre-cluster
> behavior remains as the bootstrap mode until the cluster ADRs land.

---

## Overview

Reduce cyclomatic complexity across `src/` to meet the canonical complexity-doctrine block band (per ADR-0.0.28's `ThresholdTable`, mapped to xenon's max-absolute / max-modules / max-average flags). Pre-cluster bootstrap mode runs xenon C/C/C; post-cluster mode reads the threshold table and derives the xenon flags from the `block` band.

## Policy and Guardrails

- **Lane:** Lite — internal refactoring, no external contract changes
- **Threshold (post-cluster):** Derived from ADR-0.0.28's `ThresholdTable` `block` band for `radon_cc` and `lizard_ccn` metrics
- **Threshold (pre-cluster bootstrap):** `uvx xenon --max-absolute C --max-modules C --max-average C src/`
- Tidy-first: extract helpers, remove nesting, keep behavior unchanged
- Tests must stay green
- **Diagnosis-aware (post-cluster):** When xenon fails, run `gz complexity-advise --json <failing-paths>` and use the structured `AdvisorDiagnosis` to inform refactor decisions; do NOT pattern-match refactor archetypes from training memory

## Workflow

### 1. Baseline

**Post-cluster mode (preferred when ADR-0.0.28 + ADR-0.0.29 landed):**

```bash
uv run gz validate --complexity-thresholds  # ensures threshold table is well-formed
uv run gz complexity-advise --json src/ > .gzkit/chores/complexity-reduction-xenon/proofs/advisor-diagnosis-baseline.json
```

**Pre-cluster bootstrap mode (until cluster lands):**

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/ > .gzkit/chores/complexity-reduction-xenon/proofs/xenon-baseline.txt
```

### 2. Plan

- Read the JSON diagnosis (post-cluster) or xenon report (bootstrap) to identify highest-severity crossings
- Tackle `block` band crossings first, then `warn` band, then `advise` band per the threshold-table severity order
- Small batch (3-5 functions) per PR; record operator-witnessed diagnosis acceptance in `.gzkit/chores/complexity-reduction-xenon/proofs/diagnosis-acceptance-{date}.md`
- Closes pre-mortem #6 from the design dialogue: advisor recommendation unbinding is prevented by recording the operator's acceptance of each diagnosis before refactor work begins

### 3. Implement

- Extract helpers per the advisor-recommended refactor archetype (`Long Parameter List → Parameter Object`, `Arrowhead → Guard Clauses`, etc.)
- Pre-attest functions whose complexity is irreducibly algorithmic via the `@intrinsic_complexity` decorator (ADR-0.0.29 OBPI-07) rather than refactoring them artificially
- Run `gz complexity-advise <file>` after each batch to verify the crossing is resolved

### 4. Validate

**Post-cluster mode:**

```bash
uv run gz complexity-advise src/  # exit 0 = no warn or block crossings; exit 3 = block remains
uv run gz validate --complexity-thresholds
uv run -m unittest -q
```

**Pre-cluster bootstrap mode:**

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/
uv run -m unittest -q
```

## Checklist

- [ ] Pre-cluster: F-rank functions eliminated; E-rank count reduced; xenon C/C/C gate passes
- [ ] Post-cluster: `block`-band crossings eliminated; `warn`-band count reduced; `gz complexity-advise` exit 0 or 1 (never 3)
- [ ] Tests pass unchanged
- [ ] Operator-witnessed diagnosis acceptance recorded for each non-trivial crossing under `.gzkit/chores/complexity-reduction-xenon/proofs/`
- [ ] Functions whose complexity is irreducibly algorithmic carry `@intrinsic_complexity(reason=..., attestor=...)` decorator (post-cluster)

## Acceptance Criteria

| Type | Command (post-cluster) | Command (pre-cluster bootstrap) | Expected |
|------|------------------------|----------------------------------|----------|
| exitCodeEquals | `uv run -m unittest -q` | `uv run -m unittest -q` | 0 |
| exitCodeEquals | `uv run gz complexity-advise src/` | `uvx xenon --max-absolute C --max-modules C --max-average C src/` | 0 (no block-band crossings) |
| exitCodeEquals | `uv run gz validate --complexity-thresholds` | _n/a (cluster not landed)_ | 0 |
| fileExists | `.gzkit/chores/complexity-reduction-xenon/proofs/diagnosis-acceptance-{date}.md` | _n/a_ | true (when crossings were addressed) |

## Evidence Commands

**Post-cluster:**

```bash
uv run gz complexity-advise --json src/ > .gzkit/chores/complexity-reduction-xenon/proofs/advisor-diagnosis-final.json
uv run gz validate --complexity-thresholds > .gzkit/chores/complexity-reduction-xenon/proofs/threshold-validation.txt
```

**Pre-cluster bootstrap:**

```bash
uvx xenon --max-absolute C --max-modules C --max-average C src/ > .gzkit/chores/complexity-reduction-xenon/proofs/xenon-report.txt
```

## Cluster Linkage

This chore consumes the four-ADR complexity-doctrine cluster:

- ADR-0.0.27 (corpus + distillation) — provides the empirical basis for threshold values
- ADR-0.0.28 (threshold table) — provides the canonical (metric, percentile-band, absolute-number, trigger-semantic) tuples
- ADR-0.0.29 (advisor) — provides `gz complexity-advise` for trigger-time diagnosis
- ADR-0.0.30 (authoring guidance) — provides `gz complexity-guide` for upstream-prevention preview

Until the cluster lands, the chore runs in pre-cluster bootstrap mode (xenon C/C/C). After the cluster lands, the post-cluster mode is preferred and the bootstrap mode is retained for fallback.

---

**End of CHORE: Complexity Reduction (Xenon)**
