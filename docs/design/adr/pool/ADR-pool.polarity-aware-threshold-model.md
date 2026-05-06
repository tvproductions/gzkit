---
id: ADR-pool.polarity-aware-threshold-model
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.polarity-aware-threshold-model: Polarity-aware threshold model for inverted-polarity metrics

## Status

Pool

## Intent

The complexity-threshold-doctrine cluster (ADR-0.0.28) ships a
`ThresholdTable.band_for(metric, value) -> ThresholdBand | None` lookup
that hard-codes high-is-worse semantics — a value at-or-above a band's
`absolute_number` triggers the band. The contract cannot express
inverted-polarity metrics, where lower values signal worse health.

The canonical instance is `radon_mi` (Maintainability Index): values
below the corpus boundary signal poor maintainability; values above are
good. The corpus distillation at
`docs/governance/complexity/distilled-characteristics-2026-05-04.md`
shows `radon_mi` clamping at 100 from p90 upward (p90/p95/p99 = 100.00)
with a long tail below — the diagnostic signal lives **below** corpus
p50 = 59.53, not above. Applying high-is-worse semantics to `radon_mi`
produces the wrong verdict in every case: high MI values incorrectly
trigger refactor bands; low values are silently ignored.

ADR-0.0.28 OBPI-01 ships the bootstrap-absolutes carve-out (REQ-11) for
`radon_mi` because the threshold-table model has no way to express
inverted polarity. Bootstrap absolutes are picked conservatively below
corpus p50 (`block=50, warn=70, advise=85`) but the model still treats
them as high-is-worse, so the verdict logic is wrong even with bootstrap
numbers. The validator (`gz validate --complexity-thresholds`) skips
portability checks for the affected rows but cannot rescue the verdict.

Downstream consumers ADR-0.0.29 (advisor) and ADR-0.0.30 (authoring-
guidance) will inherit this polarity defect on every `radon_mi` verdict
until the model is amended. The bootstrap carve-out is one-shot by
doctrine — `.gzkit/rules/complexity-thresholds.md` § Anti-patterns
explicitly forbids "Persistent bootstrap entries across two
distillation cycles without an upstream-defect resolution path."
Promotion of this pool ADR is the resolution path.

## Decision

Pool — design conversation pending. Promotion through `gz adr promote`
will land the chosen alternative as a foundation-kind ADR (the change
amends an app-system invariant: the threshold-table contract). The
promoted ADR's OBPI cluster covers the model amendment + rule body
amendment + JSON schema mirror + validator update + tests + BDD
scenarios + downstream consumer wiring (ADR-0.0.29, ADR-0.0.30) as a
coupled-surface coherence patch (per `AGENTS.md` § DO IT RIGHT 1a).

Recommendation seat at promotion time: **Alternative 1 (per-band
polarity field)** — polarity travels with the band, the comparison
inversion happens in `band_for()` next to the field that drives it,
schema migration is additive, and the eleven standard high-is-worse
metrics keep current behavior via the field default.

## Alternatives Considered

### 1. Per-band `polarity` field on `ThresholdBand` (recommended)

Add `polarity: Literal["high_is_worse", "low_is_worse"]` to the frozen
Pydantic model at `src/gzkit/complexity/thresholds.py:49` with default
`high_is_worse`. `band_for()` checks polarity per band and inverts the
comparison for `low_is_worse`:

```python
crossed = [
    band for band in self.bands
    if band.metric == metric and (
        (band.polarity == "high_is_worse" and value >= band.absolute_number)
        or
        (band.polarity == "low_is_worse" and value <= band.absolute_number)
    )
]
```

Schema migration is additive — existing rule-body rows render `polarity:
high_is_worse` by default, preserving behavior for the eleven standard
metrics. The rule body's `radon_mi` section declares `polarity:
low_is_worse` per-row and graduates from bootstrap to cited under a
fresh distillation.

**Pros:** polarity travels with the band; `band_for()` semantics stay
local (no parse-time fan-out); schema migration is additive; auditable
per-row.

**Cons:** every standard band carries an explicit `polarity` field even
though all eleven default to the same value (small storage / display
cost; mitigated by Pydantic default rendering).

### 2. Per-metric polarity declaration in the rule body

Same band schema; polarity is a metric-level attribute declared in a
separate section of `.gzkit/rules/complexity-thresholds.md` and parsed
at load time into a `dict[str, Polarity]` consumed by `band_for()`.

**Pros:** one declaration per metric instead of per band; tighter rule
body.

**Cons:** decouples polarity from the band where the comparison
happens — the parse step is a coherence surface that can drift from the
band rows; the `band_for()` lookup acquires a second indirection
(metric → polarity) the validator must keep consistent.

### 3. Keep the bootstrap carve-out indefinitely

Rejected. `.gzkit/rules/complexity-thresholds.md` § Anti-patterns
explicitly forbids "Persistent bootstrap entries across two
distillation cycles without an upstream-defect resolution path."
Bootstrap is one-shot. The doctrine names this rejection as the
mechanical defense against the carve-out becoming a permanent escape
hatch.

### 4. Invert sign at measurement time so all metrics emit high-is-worse values

Rejected. Corrupts the cited absolute number's correspondence to corpus
reality. The distilled-characteristics document at `corpus_revision: 1`
reports `radon_mi` p50 = 59.53, not -59.53; rewriting the measurement
output to fit the model would shift every cited absolute number on
inverted-polarity metrics without an operator witness — the doctrine-
drift class the parent foundation rule (`MAKE LLM STOCHASTIC VIBES
INERT`) forbids. The citation contract
(`.gzkit/rules/complexity-doctrine.md` § Citation contract — Percentile
+ absolute pairing) requires the absolute number to remain the
diagnostic signal at the cited revision. Sign inversion at measurement
time breaks the citation tuple.

## Notes

### Relationship matrix

- **ADR-0.0.28** (parent doctrine, foundation-kind, Validated). The
  threshold-table model authored under OBPI-0.0.28-02 is what this
  pool ADR amends. Promotion lands as a sibling foundation ADR with
  ADR-0.0.28 as the upstream invariant relationship.
- **ADR-0.0.29** (advisor, future) — consumer of `band_for()`. Inherits
  the polarity defect on every `radon_mi` verdict until this pool ADR
  is promoted and shipped. Promotion ceremony must update the advisor
  prompt-engineering surface to consume the polarity-aware verdict.
- **ADR-0.0.30** (authoring-guidance, future) — same consumer
  relationship as ADR-0.0.29.
- **`.gzkit/rules/complexity-thresholds.md`** — the current bootstrap
  carve-out for `radon_mi` (lines 96-117 + § Bootstrap absolutes) is the
  in-place workaround. Promotion of this pool ADR removes the carve-out
  for `radon_mi` and re-cites the rows from a fresh distillation under
  the polarity-aware contract. The `block`-band-per-metric invariant
  remains.
- **`src/gzkit/complexity/thresholds.py`** (OBPI-0.0.28-02 deliverable).
  The frozen Pydantic models that gain the new field. Module docstring
  lines 7-10 already forward-reference GHI #405 / this pool ADR.
- **`src/gzkit/schemas/complexity_thresholds.json`** — JSON Schema
  mirror gains the `polarity` field as an additive enum.
- **`src/gzkit/governance/trust_audits/complexity_thresholds.py`** —
  validator gains polarity-coherence checks (every metric's bands carry
  a consistent polarity; bootstrap rows graduate cleanly).
- **`features/complexity_thresholds.feature`** — BDD scenarios cover
  the inverted-polarity verdict path.
- **GHI #405** — origin (filed during ADR-0.0.28 closeout). Closes
  `superseded` against this pool ADR.

### Promotion guidance

This is foundation-kind work — the threshold-table contract is an
app-system invariant cited by every downstream complexity-doctrine
consumer. Promotion via `gz adr promote --kind foundation` lands at
`ADR-0.0.31` (or the next available foundation slot at promotion
time).

The OBPI cluster at promotion time should preserve the coupled-surface
coherence pattern from ADR-0.0.28's three-OBPI cluster:

1. **OBPI-01 — rule body amendment.** Adds `polarity` declaration to
   each per-metric table in `.gzkit/rules/complexity-thresholds.md`;
   removes the `radon_mi` bootstrap carve-out; re-cites `radon_mi` rows
   under a fresh distillation. Doctrine-amendment-protocol record
   names the metric-level mapping change per `.gzkit/rules/complexity-
   thresholds.md` § Operator-amendable mapping protocol.
2. **OBPI-02 — model + parser + JSON schema.** Adds `polarity` field
   to `ThresholdBand`; updates `band_for()` comparison; updates the
   rule-body parser to read polarity; mirrors the field in
   `src/gzkit/schemas/complexity_thresholds.json`.
3. **OBPI-03 — validator + BDD + advisor wiring.** Updates the
   `gz validate --complexity-thresholds` validator to check
   polarity-coherence; adds BDD scenarios for the inverted-polarity
   verdict path; updates the ADR-0.0.29 advisor prompt surface (if
   advisor has shipped by promotion time) to consume the polarity-
   aware verdict; same for ADR-0.0.30 authoring-guidance.

The single-loader structural defense (one parser, no parser-divergence
drift across consumers) is preserved — the polarity field is read once
by `load_threshold_table()` and consumed by every downstream surface
through the loader.

### Doctrine boundaries this pool ADR honors

- **Trigger-semantic vocabulary stays fixed at three values**
  (`block` / `warn` / `advise`). Polarity is a per-band orientation
  attribute; it is not a fourth trigger value (which would violate the
  ADR-0.0.28 § Alternative #5 fixed-vocabulary invariant).
- **Citation contract is preserved.** Polarity declares the band's
  comparison direction; it does not alter the percentile-or-absolute
  pairing rule or the canonical citation tuple form.
- **Refresh portability is preserved.** A polarity-aware citation
  written against `corpus_revision = 1` remains valid across the
  default supported window; polarity is a band-level attribute, not a
  corpus-level one, so it survives refresh.

### Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.

Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen
taxonomy.
