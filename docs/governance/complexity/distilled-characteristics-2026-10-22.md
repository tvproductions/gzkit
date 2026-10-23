---
corpus_revision: 1
baseline_artifact_path: "docs/governance/complexity/baselines/2026-10-22/baseline.json"
distillation_date: "2026-10-22"
prior_distillation_path: "docs/governance/complexity/distilled-characteristics-2026-05-04.md"
---

# Distilled complexity characteristics — 2026-10-22

Doctrine document for the gzkit complexity cluster (ADR-0.0.27 / ADR-0.0.28 / ADR-0.0.29 / ADR-0.0.30).  Per-metric numeric boundaries are sourced from the cross-project corpus aggregate; the qualitative band the boundary represents and the doctrinal frame for a violation at that boundary are the load-bearing per-metric structural surface.  Boundary percentile = p90 (canonical across all metrics).

## Metric: `lizard_file_nloc`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_file_nloc` lands at p50 = 105.00, p75 = 307.25, p90 = 716.50, p95 = 1031.90, p99 = 3130.24.  Inter-project variance of the per-project medians: 1085300.6572 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 716.50 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — module non-comment LOC above corpus p90 names the large-module smell: a file carrying more responsibilities than one reader can hold.

### Practitioner-eye observation

High module NLOC usually signals file-scale drift: too many responsibilities accumulating because no one stopped to redraw boundaries. First move: look for separable services, policies, adapters, or testable units.

*(Operator, 2026-05-04, written for `radon_raw_nloc`, carried forward by selection "Carry forward", 2026-10-22.)*

## Metric: `lizard_nloc`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_nloc` lands at p50 = 6.00, p75 = 13.00, p90 = 25.00, p95 = 37.00, p99 = 77.00.  Inter-project variance of the per-project medians: 2.4242 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 25.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Fowler (Refactoring 2e) — function non-comment LOC above corpus p90 names the long-method smell directly.

### Practitioner-eye observation

Function-scale length is often where agent-generated code gets sloppy: one function keeps accumulating preparation, policy, execution, and formatting. First move: split setup, decision, and output shaping.

*(Operator, 2026-05-04, carried forward by selection "Carry forward", 2026-10-22.)*

## Metric: `lizard_param_count`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_param_count` lands at p50 = 2.00, p75 = 3.00, p90 = 4.00, p95 = 5.00, p99 = 11.00.  Inter-project variance of the per-project medians: 0.0833 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 4.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Martin (Clean Code) — long parameter list above corpus p90 is the canonical decomposition signal Martin names ahead of all other function-shape smells.

### Practitioner-eye observation

Too many parameters usually means the function wants a context object, value object, config object, or clearer boundary. But I’m careful not to hide bad coupling inside a vague bag-of-fields object.

*(Operator, 2026-05-04, carried forward by selection "Carry forward", 2026-10-22.)*

## Metric: `lizard_nesting_depth`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_nesting_depth` lands at p50 = 1.00, p75 = 2.00, p90 = 5.00, p95 = 7.00, p99 = 14.00.  Inter-project variance of the per-project medians: 0.1818 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 5.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Martin (Clean Code) — nested-block depth past corpus p90 is the extract-method / guard-clause signal Martin names; depth is the shape that resists testability.

### Practitioner-eye observation

Deep nesting usually means arrow code: the happy path is buried under conditionals. First move: guard clauses, early returns, extracted predicates, or state-machine style.

*(Operator, 2026-05-04, carried forward by selection "Carry forward", 2026-10-22; the clause "This one is especially operator-judgment-heavy because the corpus parser failed" is cut, the parser having been fixed.)*

## Metric: `lizard_ccn`

Across the corpus (13 project(s) contributing to this aggregate), `lizard_ccn` lands at p50 = 2.00, p75 = 4.00, p90 = 8.00, p95 = 11.00, p99 = 25.00.  Inter-project variance of the per-project medians: 0.0833 — low variance, the corpus speaks with one voice on this metric.

**Numeric boundary:** p90 = 8.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Martin (Clean Code) — cyclomatic complexity above the corpus p90 violates the single-responsibility ceiling Martin names for function decomposition.

### Practitioner-eye observation

When branch count rises, I usually suspect hidden policy logic, mode handling, or too many cases in one function. First move: extract decision policy or split paths by responsibility. But a high CC can be acceptable in explicit parsers/validators when branches are deliberately enumerated and well-tested.

*(Operator, 2026-05-04, written for `radon_cc`; moved here by selection "Move radon_cc words", 2026-10-22, as `lizard_ccn` replaces it.)*

## Metric: `cohesion_lcom4`

Across the corpus (13 project(s) contributing to this aggregate), `cohesion_lcom4` lands at p50 = 25.00, p75 = 55.14, p90 = 100.00, p95 = 100.00, p99 = 100.00.  Inter-project variance of the per-project medians: 242.4462 — high variance, the corpus disagrees and per-domain narration matters.

**Numeric boundary:** p90 = 100.00 (at-or-below this corpus boundary the band is investigate; above it, the band escalates to refactor).

**Qualitative band (at-or-below boundary):** investigate.

**Doctrinal frame:** Constantine (cohesion / coupling foundations) and Page-Jones (connascence) — LCOM4 above corpus p90 is the structural signal that a class has fractured into independent responsibilities.

### Practitioner-eye observation

High LCOM4 usually means a class is acting as a junk drawer: methods don’t share state or purpose. First move: split by concept, lifecycle, or collaborator role.

*(Operator, 2026-05-04, kept by selection "Keep with a note", 2026-10-22; the clause "Also operator-judgment-heavy because the corpus parser failed" is cut.)*

> **Agent note (disclosed, not the operator's observation):** the `cohesion` tool reports a per-class cohesion percentage, where higher is more cohesive, not an LCOM4 count. The corpus figures above are on that scale and that polarity, so this metric's bands stay bootstrap absolutes until GHI #1265 renames it and sets lower-is-worse bands.

## Diff against prior distillation

Boundaries that moved by more than 10% (each line carries an operator narration placeholder; operator authors the rationale at Gate 5):

- `lizard_nesting_depth`: prior boundary was zero; cannot compute percent movement (now 5.00).  The 2026-05-04 pass ran before GHI #398's parser fixes; its zeros were a measurement defect, not a corpus property. *(Operator, by selection "Use the draft", 2026-10-22.)*
- `cohesion_lcom4`: prior boundary was zero; cannot compute percent movement (now 100.00).  The 2026-05-04 pass ran before GHI #398's parser fixes; its zeros were a measurement defect, not a corpus property. *(Operator, by selection "Use the draft", 2026-10-22.)*

## Citation form

Downstream foundation ADRs (per ADR-0.0.27 § Citation contract and `.gzkit/rules/complexity-doctrine.md`) cite this document by the canonical tuple `(file path, section anchor, corpus_revision)`.  Example:

```
docs/governance/complexity/distilled-characteristics-2026-10-22.md § lizard-ccn (corpus revision 1)
```

Citing the raw distributions or the corpus registry directly is a policy breach: the distilled document is the operator-witnessed, Gate-5-attested doctrine surface; the raw distributions are measurement evidence; the corpus is the source registry.  The link-integrity validator (`gz validate --complexity-doctrine-links`, OBPI-0.0.27-07) fails closed when a downstream ADR cites a document that does not exist or is out of date.
