# Complexity Thresholds -- Rationale and Pedagogy

Lifted from [`.gzkit/rules/complexity-thresholds.md`](../../../.gzkit/rules/complexity-thresholds.md) under GHI #327 (instructions-files-diet). The threshold data lives in the sibling [`.gzkit/rules/complexity-thresholds.json`](../../../.gzkit/rules/complexity-thresholds.json) (data source-of-truth, GHI #426); the `.md` rule file carries the doctrine narrative and invariant. This document carries the extended rationale, citation contract details, bootstrap carve-out narrative, amendment protocol, refresh portability, and anti-patterns.

## Citation contract details

The rule binds to the corpus-measured boundaries in
[`docs/governance/complexity/distilled-characteristics-2026-05-04.md`](distilled-characteristics-2026-05-04.md)
at `corpus_revision: 1`. Each per-metric table in the rule file carries the canonical
citation tuple `(distilled_characteristics_path, section_anchor, corpus_revision)`
parsed by `gzkit.complexity.citation.parse_citation` (`src/gzkit/complexity/citation.py`).

Canonical-string form (per `parse_citation` contract, sibling rule
`.gzkit/rules/complexity-doctrine.md` section Citation contract):

```
docs/governance/complexity/distilled-characteristics-2026-05-04.md § radon-cc (corpus revision 1)
```

Refresh portability: a citation written against `corpus_revision = 1`
remains valid at `corpus_revision = 1` and `corpus_revision = 2`
(`DEFAULT_SUPPORTED_WINDOW = 2`); the link-integrity validator
(`gz validate --complexity-doctrine-links`, OBPI-0.0.27-07) flags out-of-date
citations for amendment but does not auto-rewrite.

## Bootstrap absolutes (REQ-11 carve-out -- one-shot)

<!-- lifted-from: .claude/rules/complexity-thresholds.md#bootstrap-absolutes-req-11-carve-out----one-shot -->

The bootstrap-absolutes carve-out names exactly three metrics whose
threshold rows do not derive from the cited corpus distillation:

- `radon_mi` -- inverted polarity not modellable by the current
  `band_for(metric, value)` contract (which assumes high-is-worse).
  Bootstrap absolutes chosen conservatively below corpus p50 = 59.53.
  Tracked under **GHI #405** (polarity-aware threshold model).
- `lizard_nesting_depth` -- measurement-pipeline parser defect produces
  all-zero distributions across the corpus. Bootstrap absolutes drawn
  from Martin (Clean Code) -- depth > 3 is the guard-clause signal.
  Tracked under **GHI #404** (measurement-pipeline parser defect).
- `cohesion_lcom4` -- same all-zero parser defect as
  `lizard_nesting_depth`. Bootstrap absolutes drawn from Constantine /
  Page-Jones cohesion canon. Tracked under **GHI #404**.

The carve-out is **one-shot**: the validator (OBPI-0.0.28-03) skips
portability checks for rows under this section. When the upstream
defect is resolved and the affected metric is cited from a fresh
distillation, the metric is removed from this section and the
validator runs the full portability check on its rows.

This is **not** a permanent escape hatch. A bootstrap entry that
persists across two distillation cycles without an upstream-defect
resolution path is itself a defect -- file a follow-up GHI naming the
unresolved lag.

### Per-metric bootstrap narrative

**`radon_mi`** is **inverted polarity** (lower values are worse). The
corpus distillation at `corpus_revision: 1` shows clamping above p90
(p90/p95/p99 all = 100.00) and a long tail below -- the diagnostic signal
lives below the corpus median, which the current `band_for(metric, value)`
contract (high-is-worse) cannot express. Bootstrap absolutes are chosen
conservatively below the corpus p50 (59.53); the percentile column uses
the canonical p75/p90/p95 vocabulary as required by the
`ThresholdBand.corpus_percentile` enum (the percentile names a position
in the canonical band ladder, not a corpus measurement, while the
metric is in bootstrap). The polarity-aware model amendment is tracked
under GHI #405; once the model lands and a fresh distillation is taken,
this metric's rows graduate from bootstrap to cited.

**`lizard_nesting_depth`** corpus distribution is all-zero across 13
projects (p50 through p99 = 0.00) -- a measurement-pipeline parser defect
flagged in OBPI-0.0.27-04's closeout evidence and tracked under GHI
#404. Bootstrap absolutes are drawn from canon: Martin (Clean Code)
names depth > 3 as the guard-clause / extract-method signal; the
bootstrap thresholds embed that signal until the parser is fixed and a
fresh distillation lands.

**`cohesion_lcom4`** corpus distribution is all-zero across 13 projects --
the same measurement-pipeline parser defect tracked under GHI #404.
Bootstrap absolutes encode conservative LCOM4 thresholds against the
Constantine / Page-Jones cohesion canon: values above the bootstrap
block band signal that a class has fractured into independent
responsibilities. Once the parser is fixed and a fresh distillation
lands, these rows graduate from bootstrap to cited.

## Operator-amendable mapping protocol

<!-- lifted-from: .claude/rules/complexity-thresholds.md#operator-amendable-mapping-protocol -->

Amendments to `(metric, band, trigger)` mappings -- for example,
shifting the default `(advise=p75, warn=p90, block=p95)` to
`(advise=p50, warn=p75, block=p90)` for a specific metric, or adjusting
the bootstrap absolutes -- flow through the doctrine-amendment-protocol
pool stub forward-referenced from ADR-0.0.27 OBPI-02. The amendment
record names the metric, the prior mapping, the new mapping, the
operator-attested rationale, and the receipt ID of the Gate 5
walkthrough that witnessed the change.

**Silent edits are forbidden** by the validator
(OBPI-0.0.28-03 -- `gz validate --complexity-thresholds`). An edit to
the rule body without a corresponding doctrine-amendment-protocol
record is a policy breach (exit 3).

The scope of amendment is per-metric mapping only. The trigger-semantic
vocabulary itself (`block` / `warn` / `advise`) is foundation doctrine
and amendable only via ADR-0.0.28 ceremony.

### Amendment record — `radon_raw_nloc`, 2026-08-26

| Field | Value |
|---|---|
| Metric | `radon_raw_nloc` |
| Prior mapping | `advise=p75 (311.75)`, `warn=p90 (733.2)`, `block=p95 (1031.9)` |
| New mapping | `advise=p75 (311.75)`, `warn=p90 (733.2)`, `warn=p95 (1031.9)`, `block=p99 (3143.82)` |
| Authorization | Operator, verbatim: *"do #1"* / *"fix the label and commit it"* (2026-08-26) |
| Consequence | All five `data/module_size_grandfather.json` entries fell under the new band and were surrendered the same day; the ratchet list is now empty. |

**Rationale.** The distilled-characteristics document reports inter-project
variance of **1,093,055** on `radon_raw_nloc` and characterises it in its own
words as *"high variance, the corpus disagrees and per-domain narration
matters"*. The contrast is `radon_cc` at variance **0.0833**, where the same
document says the corpus *"speaks with one voice"*. The thirteen corpus projects
span a web framework, a package manager, a type checker, a TUI toolkit and a
stdlib subset; they have no shared norm for module length and the document does
not claim they do. Blocking at p95 therefore rejected ordinary between-domain
variation rather than naming a defect, and the observed cost was concrete: on
2026-08-26 a 45-line test fixture added under GHI #885 tipped a module over the
band and forced a file split that improved nothing.

p99 is chosen over removing the band because § Invariant requires every metric
to carry a `block` band — *"a metric without a `block` band is prose, not a
threshold"*. p99 keeps the gate real while reserving it for a module larger than
99% of modules across the corpus, which is an outlier claim the corpus can still
support despite its variance.

**Two protocol departures, disclosed rather than worked around.**

1. This record lives here, not in the doctrine-amendment-protocol home the
   protocol names. That home is `ADR-pool.doctrine-amendment-protocol` —
   **Pending, 0/0 OBPIs**. It is designed, not built, so the protocol
   forward-references a surface that cannot yet receive a record.
2. No Gate 5 receipt is cited. The protocol asks for one; `AGENTS.md`
   § Operator Doctrine (2026-08-17) rules that Gate 5 means OBPI/ADR completion
   attestation and nothing else. A threshold amendment is neither, so the
   operator's verbatim authorization above is the record.

**The validator does not enforce this.** The protocol states *"Silent edits are
forbidden by the validator (exit 3)"*. Measured 2026-08-26:
`validate_complexity_thresholds` checks that the data file exists, loads under
Pydantic, and covers the canonical metrics. It has no concept of an amendment
record and cannot detect a silent edit — the claim is doctrine declared without
mechanism, and this record is voluntary compliance, not a gate's output.

## Refresh portability

When a corpus refresh produces a new distilled-characteristics
document (per `.gzkit/rules/complexity-doctrine.md` section Distillation
Cadence), the per-metric tables in the rule file are re-cited:

1. The percentile column remains stable (corpus refresh preserves
   percentile semantics, not absolute numbers).
2. The absolute-number column is updated from the new distillation.
3. The Citation section's `corpus_revision` updates to the new
   revision number.

The link-integrity validator (`gz validate --complexity-doctrine-links`,
OBPI-0.0.27-07) flags out-of-date citations for amendment but does not
auto-rewrite -- silent rewrite would shift downstream ADR text without a
witness.

## Anti-patterns

- **Silent rule-body edits.** Editing `(metric, band, trigger)`
  mappings without flowing through the doctrine-amendment-protocol
  stub. The validator fails closed.
- **Missing `block` band per metric.** A metric without a `block`
  band is prose, not a threshold. The schema enforces a block band
  on every metric.
- **Percentile-only or absolute-only band rows.** Every band row
  carries both. Percentile carries the semantic load; absolute
  carries the diagnostic load. Citing either alone is a contract
  violation.
- **Citation outside the canonical tuple form.** Free-form prose
  references, raw-distribution citations, and corpus-registry
  citations are forbidden. The distilled-characteristics document is
  the operator-witnessed Gate-5-attested doctrine surface; raw
  distributions are measurement evidence; the corpus is the source
  registry.
- **Adding a fourth trigger-semantic value.** The vocabulary is fixed
  at three values mapping to three downstream consumer surfaces. A
  fourth state with no consumer is dead doctrine.
- **Persistent bootstrap entries across two distillation cycles
  without an upstream-defect resolution path.** Bootstrap is one-shot;
  permanent bootstrap is itself a defect.

## Related

- ADR-0.0.28 -- parent ADR codifying the complexity-threshold-doctrine
- ADR-0.0.27 -- sibling ADR codifying the corpus-measurement and
  distillation pipeline this rule consumes
- `.gzkit/rules/complexity-doctrine.md` -- sibling rule codifying the
  citation contract this rule's per-metric tables conform to
- `src/gzkit/complexity/citation.py` -- `Citation` model and
  `parse_citation` parser this rule's citation strings round-trip
  through
- `src/gzkit/complexity/thresholds.py` -- `ThresholdTable` /
  `ThresholdBand` Pydantic models authored under OBPI-0.0.28-02 (the
  loader contract this rule body parses against)
- `src/gzkit/governance/trust_audits.py` --
  `validate_complexity_thresholds` validator authored under
  OBPI-0.0.28-03 (`gz validate --complexity-thresholds`); the gate-time
  defense this rule depends on for fail-closed enforcement
- `docs/governance/complexity/distilled-characteristics-2026-05-04.md`
  -- the cited distilled-characteristics document at corpus revision 1
- `docs/governance/advisory-rules-audit.md` -- scorecard entry
  classifying this rule as **Mechanical** (enforced by
  `gz validate --complexity-thresholds`)
- GHI #404 -- measurement-pipeline parser produces all-zero baselines
  for `lizard_nesting_depth` and `cohesion_lcom4`
- GHI #405 -- polarity-aware threshold model amendment for
  `radon_mi` and other inverted-polarity metrics
