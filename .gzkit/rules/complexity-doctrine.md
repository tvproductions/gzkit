---
id: complexity-doctrine
paths:
  - "docs/governance/complexity/**"
  - "data/exemplar_corpus.json"
  - "src/gzkit/complexity/**"
  - ".gzkit/rules/complexity-doctrine.md"
description: Exemplar-corpus selection methodology, distillation cadence, and citation contract for gzkit complexity calibration
---

<!-- rule-version: 0.2.0 -->

# Complexity Doctrine (gzkit)

> **Rule version:** `0.2.0` — bumped under OBPI-0.0.27-05 to formalize the
> citation tuple `(distilled_characteristics_path, section_anchor,
> corpus_revision)`, codify the percentile + absolute-number pairing rule,
> and name the refresh-portability rule the link-integrity validator
> (OBPI-0.0.27-07) consumes. Prior version `0.1.0` authored under
> OBPI-0.0.27-01 codified the exemplar-corpus selection methodology, seven
> selection criteria, seven corpus anti-patterns, distillation cadence
> triggers, citation contract, and project-doctrine-fitness criterion as
> a Mechanical-class rule consumed by downstream foundation ADRs
> (0.0.28 / 0.0.29 / 0.0.30).

## Invariant

**gzkit calibrates complexity decisions against an empirically-grounded corpus
of well-architected Python projects, distilled into doctrine prose and citable
numeric boundaries.** The corpus is operator-curated against this selection
methodology, not agent-pattern-matched from training corpus. Distilled
characteristics ship as gzkit doctrine; downstream foundation ADRs
(0.0.28 / 0.0.29 / 0.0.30) cite the doctrine, not the corpus directly.

The corpus is a *learning relationship*, not an *adoption relationship* —
gzkit measures click's design metrics to inform CLI doctrine; gzkit does not
depend on click. These are independent relationships and conflating them is
the canonical training-corpus failure mode.

## Selection Criteria (binding — all must hold)

Projects qualify for the exemplar corpus only when **ALL** of the following
criteria hold:

1. **Longevity:** ≥ 5 years active development OR explicitly archived as a
   reference implementation.

2. **Maintenance health:** active releases in last 12 months OR project
   explicitly declares done state (feature-complete, maintenance-only).

3. **Practitioner reputation:** cited in PEPs, in published reference works
   (*Fluent Python*, *Effective Python*, *Architecture Patterns with Python*),
   OR by recurring conference talks (PyCon, EuroPython, PyData). Specifically
   NOT by GitHub-star count — popularity is not a design-quality signal.

4. **Pure-Python predominance:** Python content is the primary artifact
   (≥ 80% of LOC). Excludes thin wrappers around C/Rust where the Python
   part is glue code.

5. **Author craftsmanship signal:** maintainer history shows design discipline
   (PEP authorship, well-known design talks, mentorship reputation). The most
   subjective criterion; mitigated by the agent-drafted-then-operator-audited
   pattern — agent nominates, operator witnesses.

6. **Project doctrine fitness:** the project does not violate gzkit's existing
   doctrinal commitments. A project whose foundational design choices contradict
   Stdlib-First or other gzkit canon is excluded regardless of other strengths.
   The pytest-mention demerit during the ADR-0.0.27 design dialogue was the
   canonical failure this criterion closes: the agent nominated pytest (a
   popular project that violates gzkit's Stdlib-First and `forbid-pytest`
   commitments), demonstrating that training-corpus bias produces
   systemically over-popular nominations regardless of project-canon fit.
   Operator audit is the structural defense.

7. **Pinned to a specific commit SHA at corpus-authoring time** — distributions
   are reproducible from the SHA. No floating-HEAD entries; corpus is
   point-in-time, not rolling.

Corpus authoring is at the project + module-subset level, not whole-project.
Each project enters with explicit per-project path filters declaring which
paths enter the measurement set and which are excluded with rationale.
Strategically-complex modules (Django ORM query compiler, mypy unification
core) are excluded — they encode irreducible algorithmic complexity that
would pull metric distributions toward leniency if measured.

## Corpus Anti-Patterns (binding — any disqualifies)

The following selection behaviors are explicitly prohibited:

1. **Post-hoc fitting:** Selecting projects that confirm a pre-decided
   threshold. The corpus must drive the threshold, not the reverse.

2. **GitHub-star count:** Selecting by GitHub-star count. Popularity ≠ design
   quality; star count is a social-proof proxy with no design-quality signal.

3. **Only modern projects:** Selecting only modern projects loses the
   'test of time' signal — the most reliable quality indicator is code that
   has aged well across multiple Python eras and ecosystem shifts.

4. **Only legacy projects:** Selecting only legacy projects misses current
   best-practice idioms — the corpus must span eras, not anchor to one.

5. **Monoculture:** Selecting projects all from the same domain produces
   monoculture — over-fits to one idiom and misses cross-domain variance that
   makes metric distributions robust.

6. **Agent-supplied list from training memory:** Agent supplying the project
   list from training memory without operator audit. The corpus is doctrine
   and must be operator-witnessed; an agent-only-selected corpus is the
   same failure class as agent-synthesized attestation.

7. **Doctrine-incompatible inclusion:** Including any project that violates
   gzkit's existing doctrinal commitments (project doctrine fitness criterion
   above). This anti-pattern is the mirror image of criterion #6; both name
   the same boundary from opposite directions.

## Distillation Cadence (binding)

Re-distillation fires on **any** of three triggers:

1. **Annual calendar default:** Python ecosystem evolves on roughly annual
   cycles; semi-annual is over-eager, biennial risks doctrine staleness.

2. **Signal trigger:** Advisor verdict-frequency drift > 25% from baseline
   of last distillation. Minimum re-distillation interval of 6 months to
   prevent thrashing — a drift signal within 6 months of the last distillation
   does not fire re-distillation.

3. **Judgment trigger:** Operator ad-hoc trigger when a ground-breaking project
   emerges that warrants corpus amendment (a paradigmatic new design approach,
   a project that settles a long-running idiom debate, etc.).

Distillation is agent-driven, human-reviewed and attested/corrected:

1. Agent drafts metric-aggregate prose per metric (median, p75, p90, p95, p99
   with inter-project variance commentary).
2. Operator adds the practitioner-eye observation.
3. Joint authoring of actionable characteristics per metric: numeric boundary
   (corpus percentile + absolute number at that percentile), qualitative band
   (comfortable craft / investigate / refactor), doctrinal frame.
4. Agent proposes classifier rule-table boundary updates; operator audits.
5. Diff against previous distillation: any boundary that moved > 10% gets
   explicit operator narration.
6. Output: `docs/governance/complexity/distilled-characteristics-{date}.md`.
   Previous documents are preserved (never overwritten) — doctrine evolution
   has a permanent audit trail.

## Citation Contract (binding)

Downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) **MUST** cite the
distilled-characteristics document, **NOT** the raw distributions and **NOT**
the corpus (`data/exemplar_corpus.json`) directly.

### Canonical tuple (binding)

The citation is a three-field tuple
`(distilled_characteristics_path, section_anchor, corpus_revision)`,
codified by the Pydantic `Citation` model at
`src/gzkit/complexity/citation.py` (frozen, `extra="forbid"`) and mirrored
by the JSON Schema at `src/gzkit/schemas/complexity_citation.json`
(`additionalProperties: false`). The tuple is the only valid citation
shape; raw distributions, the corpus registry, and free-form prose
references are explicitly forbidden.

Canonical string form (consumed by `parse_citation`):

```
docs/governance/complexity/distilled-characteristics-2026-05-04.md § radon-cc (corpus revision 1)
```

Field constraints:

- `distilled_characteristics_path` is a relative path under
  `docs/governance/complexity/` ending in `.md`.
- `section_anchor` is a slugified anchor string identifying the metric
  section within the cited document.
- `corpus_revision` is a positive integer matching the
  `corpus_revision` frontmatter of the cited document.

### Percentile + absolute pairing (binding)

Every cited boundary MUST appear as **both** a percentile-of-corpus
**AND** the absolute-number-at-that-percentile, paired together. The
two forms are not alternatives — they are required together, so that
boundaries remain readable across corpus refresh even when absolute
numbers shift.

Worked example (sourced from the landed `radon_cc` boundary at
`distilled-characteristics-2026-05-04.md`):

> at-or-below the corpus p90 = 7 the band is investigate; above it the
> band escalates to refactor

The percentile (`p90`) carries the semantic load — "tail of the
corpus" — and survives refresh; the absolute number (`= 7`) carries
the diagnostic load — "what does that look like at this revision" —
and shifts with refresh. Citing either form alone is a contract
violation.

### Refresh portability (binding)

A citation written against `corpus_revision = N` remains valid at
`current_revision = N` and `current_revision = N + 1` (the default
**supported window** is two revisions, set by
`DEFAULT_SUPPORTED_WINDOW` at `src/gzkit/complexity/citation.py`). At
`current_revision >= N + 2` the citation is out of date.

The link-integrity validator (`gz validate --complexity-doctrine-links`,
**OBPI-0.0.27-07**) **flags** out-of-date citations for amendment but
does **NOT** auto-rewrite them — citations remain stable until the
citing ADR is amended through its own ceremony. The flag-not-rewrite
verdict is the binding contract: silent rewrite would shift downstream
ADR text without a witness, which is the doctrine-drift class the
parent foundation rule (`MAKE LLM STOCHASTIC VIBES INERT`) forbids.

The rationale: the distilled-characteristics document is the reviewed,
attested, operator-witnessed doctrine artifact. The raw distributions are
measurement evidence; the corpus is the source registry. Citing raw
distributions or the corpus directly would bypass the distillation ceremony
and the Gate 5 attestation that made the doctrine trustworthy. The
link-integrity validator (`gz validate --complexity-doctrine-links`, OBPI-0.0.27-07)
fails closed when a downstream ADR cites a document that does not exist or
is out of date.

## Project-Doctrine Fitness Criterion

This criterion deserves extended treatment because it is the most frequently
violated in agent-nomination flows.

**The criterion:** A corpus candidate is excluded if its foundational design
choices contradict gzkit's existing doctrinal commitments — regardless of
how well it scores on the other six criteria.

**The pytest-mention demerit (canonical lesson):** During the ADR-0.0.27
design dialogue, the agent nominated pytest as a corpus candidate. pytest is
a widely-used, well-architected project by conventional metrics. But gzkit
carries a `forbid-pytest` pre-commit hook and a Stdlib-First doctrine that
names `unittest` as the canonical testing framework. pytest's foundational
design (plugin architecture, fixture injection, magic `conftest.py` discovery)
contradicts Stdlib-First directly. The agent's nomination demonstrated that
training-corpus bias produces systemically over-popular nominations regardless
of project-canon fit — the failure class the entire exemplar-corpus doctrine
exists to close. The pytest-mention demerit is now the canonical lesson cited
every time an agent produces a "popular but doctrinally incompatible" nomination.

**Operator audit is the structural defense.** The project-doctrine-fitness
criterion is the most subjective of the seven and the most resistant to
mechanical enforcement. The mitigation is the agent-drafted-then-operator-audited
pattern: the agent nominates with explicit doctrine-fitness justification; the
operator confirms or rejects before any SHA is pinned.

## Anti-Patterns

- Selecting corpus members by GitHub-star count or training-corpus familiarity.
- Nominating candidates without explicit doctrine-fitness justification.
- Citing raw distributions or the corpus registry in downstream ADRs (use the
  distilled-characteristics document instead).
- Re-distilling more frequently than the 6-month minimum guard allows.
- Allowing agent-only corpus selection without operator witness.

## Related

- ADR-0.0.27 — parent ADR codifying the exemplar-corpus doctrine cluster
- `data/exemplar_corpus.json` — pinned project registry (OBPI-0.0.27-02)
- `src/gzkit/complexity/measurement.py` — measurement pipeline (OBPI-0.0.27-03)
- `docs/governance/complexity/` — distilled-characteristics documents
- `src/gzkit/governance/trust_audits.py` — link-integrity validator
  (`gz validate --complexity-doctrine-links`, OBPI-0.0.27-07)
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying
  this rule as **Mechanical** (enforced by `gz validate --complexity-doctrine-links`,
  citations to ADR-0.0.27 and OBPI-0.0.27-07)
