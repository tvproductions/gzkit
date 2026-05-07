# Complexity Doctrine — Rationale and Extended Treatment

This document extracts the pedagogical and extended-rationale material that
used to live alongside the per-turn binding criteria in
`.gzkit/rules/complexity-doctrine.md`. The binding invariants, compressed
selection criteria, anti-pattern names, cadence triggers, and citation
contract remain in the rule file; this file preserves the *why* — extended
criterion explanations, worked examples, and the project-doctrine-fitness
canonical lesson — without forcing that material to load into every context
window.

Lineage: `.gzkit/rules/complexity-doctrine.md` 0.2.0 (OBPI-0.0.27-05) ->
0.3.0 (GHI #327 diet pass) + this file.

## Selection criteria extended explanations

The seven selection criteria are binding in compressed form in the rule file.
This section preserves the extended explanations that were lifted during the
GHI #327 diet pass.

### 1. Longevity

Projects must have >= 5 years of active development OR be explicitly archived
as a reference implementation. The longevity threshold ensures the corpus
captures projects that have survived multiple Python-era transitions and
ecosystem shifts, not projects that are popular in a single moment.

### 2. Maintenance health

Active releases in the last 12 months OR a project that explicitly declares
done state (feature-complete, maintenance-only). The distinction between
"actively maintained" and "abandoned" is not binary — a project that declares
itself feature-complete and enters maintenance-only mode is a stronger signal
than one that simply stops releasing.

### 3. Practitioner reputation

Cited in PEPs, in published reference works (*Fluent Python*, *Effective
Python*, *Architecture Patterns with Python*), OR by recurring conference
talks (PyCon, EuroPython, PyData). Specifically NOT by GitHub-star count —
popularity is not a design-quality signal. The reference-work and conference
signals measure practitioner respect, not social-media virality.

### 4. Pure-Python predominance

Python content is the primary artifact (>= 80% of LOC). Excludes thin
wrappers around C/Rust where the Python part is glue code. The 80%
threshold ensures the corpus measures Python design decisions, not FFI
binding patterns.

### 5. Author craftsmanship signal

Maintainer history shows design discipline (PEP authorship, well-known
design talks, mentorship reputation). The most subjective criterion;
mitigated by the agent-drafted-then-operator-audited pattern — agent
nominates, operator witnesses. The subjectivity is intentional: design
discipline is not mechanically measurable, but the agent-then-operator
pattern makes the judgment auditable.

### 6. Project doctrine fitness

The project does not violate gzkit's existing doctrinal commitments. A
project whose foundational design choices contradict Stdlib-First or other
gzkit canon is excluded regardless of other strengths. See the
[project-doctrine fitness extended treatment](#project-doctrine-fitness-criterion-extended-treatment)
below for the pytest-mention demerit canonical lesson.

### 7. Pinned commit SHA

Pinned to a specific commit SHA at corpus-authoring time — distributions are
reproducible from the SHA. No floating-HEAD entries; corpus is point-in-time,
not rolling. The pinning ensures measurement reproducibility: running the
same measurement pipeline against the same SHA must produce the same
distributions.

### Corpus authoring scope

Corpus authoring is at the project + module-subset level, not whole-project.
Each project enters with explicit per-project path filters declaring which
paths enter the measurement set and which are excluded with rationale.
Strategically-complex modules (Django ORM query compiler, mypy unification
core) are excluded — they encode irreducible algorithmic complexity that
would pull metric distributions toward leniency if measured.

## Project-Doctrine Fitness Criterion (extended treatment)

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

## Percentile + absolute pairing (worked example)

Every cited boundary MUST appear as **both** a percentile-of-corpus **AND**
the absolute-number-at-that-percentile, paired together. The two forms are
not alternatives — they are required together.

Worked example (sourced from the landed `radon_cc` boundary at
`distilled-characteristics-2026-05-04.md`):

> at-or-below the corpus p90 = 7 the band is investigate; above it the
> band escalates to refactor

The percentile (`p90`) carries the semantic load — "tail of the corpus" —
and survives refresh; the absolute number (`= 7`) carries the diagnostic
load — "what does that look like at this revision" — and shifts with
refresh. Citing either form alone is a contract violation.

## Refresh portability (extended rationale)

A citation written against `corpus_revision = N` remains valid at
`current_revision = N` and `current_revision = N + 1` (the default
**supported window** is two revisions, set by `DEFAULT_SUPPORTED_WINDOW`
at `src/gzkit/complexity/citation.py`). At `current_revision >= N + 2`
the citation is out of date.

The link-integrity validator (`gz validate --complexity-doctrine-links`,
**OBPI-0.0.27-07**) **flags** out-of-date citations for amendment but does
**NOT** auto-rewrite them — citations remain stable until the citing ADR is
amended through its own ceremony. The flag-not-rewrite verdict is the binding
contract: silent rewrite would shift downstream ADR text without a witness,
which is the doctrine-drift class the parent foundation rule
(`MAKE LLM STOCHASTIC VIBES INERT`) forbids.

The rationale: the distilled-characteristics document is the reviewed,
attested, operator-witnessed doctrine artifact. The raw distributions are
measurement evidence; the corpus is the source registry. Citing raw
distributions or the corpus directly would bypass the distillation ceremony
and the Gate 5 attestation that made the doctrine trustworthy. The
link-integrity validator (`gz validate --complexity-doctrine-links`,
OBPI-0.0.27-07) fails closed when a downstream ADR cites a document that
does not exist or is out of date.

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
