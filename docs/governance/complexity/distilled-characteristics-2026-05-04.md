---
corpus_revision: 1
baseline_artifact_path: "docs/governance/complexity/baselines/2026-05-04/baseline.json"
distillation_date: "2026-05-04"
prior_distillation_path: null
---

# Distilled complexity characteristics — 2026-05-04

Doctrine document for the gzkit complexity cluster (ADR-0.0.27 / ADR-0.0.28 / ADR-0.0.29 / ADR-0.0.30).  Per-metric numeric boundaries are sourced from the cross-project corpus aggregate; the qualitative band the boundary represents and the doctrinal frame for a violation at that boundary are the load-bearing per-metric structural surface.  Boundary percentile = p90 (canonical across all metrics).

## Metric: `radon_cc`

Across the corpus (13 project(s) contributing to this aggregate), `radon_cc` lands at p50 = 2.00, p75 = 4.00, p90 = 7.00, p95 = 11.00, p99 = 24.00.  Inter-project variance of the per-project medians: 0.0833 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 7.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Martin (Clean Code) — cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.

### Practitioner-eye observation

When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.

## Metric: `radon_mi`

Across the corpus (13 project(s) contributing to this aggregate), `radon_mi` lands at p50 = 59.53, p75 = 79.58, p90 = 100.00, p95 = 100.00, p99 = 100.00.  Inter-project variance of the per-project medians: 613.7122 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 100.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — maintainability index is the aggregate smell signal across long-method, large-class, and divergent-change smells; corpus p90 demarcates the smell-attention threshold.

### Practitioner-eye observation

Because high MI is good, low MI is the smell. A low score usually means several smells are stacking: long code, branching, dense tokens. I treat it as a triage signal, not a diagnosis.

## Metric: `radon_hal_volume`

Across the corpus (13 project(s) contributing to this aggregate), `radon_hal_volume` lands at p50 = 233.19, p75 = 946.89, p90 = 2740.93, p95 = 5549.80, p99 = 14981.93.  Inter-project variance of the per-project medians: 29896244.3886 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 2740.93 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — Halstead volume past the corpus p90 presents the long-method smell from a token-count vantage.

### Practitioner-eye observation

High volume often means the function is carrying too much vocabulary: too many names, operations, or concepts. First move: identify the dominant concept and extract secondary concepts. But volume can over-penalize straightforward data-shaping code.

## Metric: `radon_hal_difficulty`

Across the corpus (13 project(s) contributing to this aggregate), `radon_hal_difficulty` lands at p50 = 4.35, p75 = 8.13, p90 = 11.54, p95 = 12.46, p99 = 17.80.  Inter-project variance of the per-project medians: 14.8147 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 11.54 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — Halstead difficulty above the corpus p90 indicates comprehensibility loss; the operand/operator ratio exceeds the audience the function can carry.

### Practitioner-eye observation

Difficulty rises when the reader must juggle too many operators/operands or domain terms at once. I look for places where naming, helper extraction, or intermediate variables can reduce mental stack load.

## Metric: `radon_hal_effort`

Across the corpus (13 project(s) contributing to this aggregate), `radon_hal_effort` lands at p50 = 1030.14, p75 = 7975.79, p90 = 30805.01, p95 = 74805.40, p99 = 216567.24.  Inter-project variance of the per-project medians: 7778930824.0282 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 30805.01 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — Halstead effort = volume * difficulty composite; corpus p90 names the practitioner-readable ceiling.

### Practitioner-eye observation

Effort is useful when volume and difficulty combine. I read it as ‘how much attention this code will consume during review.’ First move: reduce either size or conceptual density, not necessarily both.

## Metric: `radon_raw_nloc`

Across the corpus (13 project(s) contributing to this aggregate), `radon_raw_nloc` lands at p50 = 105.00, p75 = 311.75, p90 = 733.20, p95 = 1031.90, p99 = 3143.82.  Inter-project variance of the per-project medians: 1093055.2784 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 733.20 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — non-comment LOC above corpus p90 names the long-method / large-class smell directly.

### Practitioner-eye observation

High module NLOC usually signals file-scale drift: too many responsibilities accumulating because no one stopped to redraw boundaries. First move: look for separable services, policies, adapters, or testable units.

## Metric: `radon_raw_lloc`

Across the corpus (13 project(s) contributing to this aggregate), `radon_raw_lloc` lands at p50 = 90.50, p75 = 238.25, p90 = 518.00, p95 = 811.70, p99 = 2502.73.  Inter-project variance of the per-project medians: 830299.7027 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 518.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — logical LOC above corpus p90 strips comment-padding from the long-method smell.

### Practitioner-eye observation

High logical LOC is more concerning than physical length because it points to actual executable density. I use it to find modules that look short enough visually but are doing too much real work.

## Metric: `lizard_nloc`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_nloc` lands at p50 = 6.00, p75 = 13.00, p90 = 25.00, p95 = 37.00, p99 = 77.00.  Inter-project variance of the per-project medians: 2.4242 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 25.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — lizard non-comment LOC corroborates radon's long-method signal across the corpus.

### Practitioner-eye observation

Function-scale length is often where agent-generated code gets sloppy: one function keeps accumulating preparation, policy, execution, and formatting. First move: split setup, decision, and output shaping.

## Metric: `lizard_param_count`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_param_count` lands at p50 = 2.00, p75 = 3.00, p90 = 4.00, p95 = 5.00, p99 = 11.00.  Inter-project variance of the per-project medians: 0.0833 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 4.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Martin (Clean Code) — long parameter list above corpus p90 is the canonical decomposition signal Martin names ahead of all other function-shape smells.

### Practitioner-eye observation

Too many parameters usually means the function wants a context object, value object, config object, or clearer boundary. But I’m careful not to hide bad coupling inside a vague bag-of-fields object.

## Metric: `lizard_nesting_depth`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_nesting_depth` lands at p50 = 0.00, p75 = 0.00, p90 = 0.00, p95 = 0.00, p99 = 0.00.  Inter-project variance of the per-project medians: 0.0000 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 0.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Martin (Clean Code) — nested-block depth past corpus p90 is the extract-method / guard-clause signal Martin names; depth is the shape that resists testability.

### Practitioner-eye observation

This one is especially operator-judgment-heavy because the corpus parser failed. Deep nesting usually means arrow code: the happy path is buried under conditionals. First move: guard clauses, early returns, extracted predicates, or state-machine style.

## Metric: `lizard_ccn`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_ccn` lands at p50 = 2.00, p75 = 4.00, p90 = 8.00, p95 = 11.00, p99 = 25.00.  Inter-project variance of the per-project medians: 0.0833 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 8.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Martin (Clean Code) — lizard cyclomatic complexity number corroborates radon_cc's single-responsibility-ceiling signal.

### Practitioner-eye observation

I compare this with `radon_cc`. Agreement means real branch complexity; disagreement means I inspect parser behavior or language constructs. Either way, it is a review prompt, not an automatic condemnation.

## Metric: `cohesion_lcom4`

Across the corpus (13 project(s) contributing to this aggregate), `cohesion_lcom4` lands at p50 = 0.00, p75 = 0.00, p90 = 0.00, p95 = 0.00, p99 = 0.00.  Inter-project variance of the per-project medians: 0.0000 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 0.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Constantine (cohesion / coupling foundations) and Page-Jones (connascence) — LCOM4 above corpus p90 is the structural signal that a class has fractured into independent responsibilities.

### Practitioner-eye observation

Also operator-judgment-heavy because the corpus parser failed. High LCOM4 usually means a class is acting as a junk drawer: methods don’t share state or purpose. First move: split by concept, lifecycle, or collaborator role.

## Diff against prior distillation

Cold start — no prior distillation; this document establishes the baseline.  Subsequent runs will narrate every boundary that moved by more than 10%.

## Citation form

Downstream foundation ADRs (per ADR-0.0.27 § Citation contract and `.gzkit/rules/complexity-doctrine.md`) cite this document by the canonical tuple `(file path, section anchor, corpus_revision)`.  Example:

```
docs/governance/complexity/distilled-characteristics-2026-05-04.md § Cyclomatic Complexity (corpus_revision 1)
```

Citing the raw distributions or the corpus registry directly is a policy breach: the distilled document is the operator-witnessed, Gate-5-attested doctrine surface; the raw distributions are measurement evidence; the corpus is the source registry.  The link-integrity validator (`gz validate --complexity-doctrine-links`, OBPI-0.0.27-07) fails closed when a downstream ADR cites a document that does not exist or is out of date.
