---
id: OBPI-0.0.27-02-initial-corpus-authoring
parent: ADR-0.0.27
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.27-02-initial-corpus-authoring: Initial Corpus Authoring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/ADR-0.0.27-exemplar-corpus-doctrine.md`
- **Checklist Item:** #2 — "Initial corpus authoring with pinned SHAs and per-project path filters; books the six pool stubs as forward-references (`data/exemplar_corpus.json`)"

**Status:** Draft

## Objective

Pin the initial 12-15-project exemplar corpus across the ten archetypal cells with per-project path filters, commit SHAs, and craftsmanship justifications recorded in `data/exemplar_corpus.json`; introduce the `ExemplarProject` Pydantic model with `ConfigDict(frozen=True, extra="forbid")`; book the six cluster pool stubs as forward-references.

## Lane

**Heavy** — Introduces a new data-contract artifact (`data/exemplar_corpus.json`) consumed by OBPI-03's measurement pipeline. Operator-witnessed nominations per the OBPI-01 methodology; foundation-kind brief-level Gate 5 attestation per ADR-0.0.18.

## Allowed Paths

- `data/exemplar_corpus.json` — registry of pinned project metadata
- `src/gzkit/models/exemplar.py` — `ExemplarProject` Pydantic model + corpus loader
- `src/gzkit/schemas/exemplar_corpus.json` — JSON Schema mirror for validation tooling
- `tests/models/test_exemplar.py`, `tests/governance/test_exemplar_corpus.py` — REQ-derived assertions
- `docs/design/adr/pool/ADR-pool.attestation-quality-measurement.md`
- `docs/design/adr/pool/ADR-pool.doctrine-amendment-protocol.md`
- `docs/design/adr/pool/ADR-pool.complexity-doctrine-validate-suite.md`
- `docs/design/adr/pool/ADR-pool.canon-pillar-codification.md`
- `docs/design/adr/pool/ADR-pool.complexity-doctrine-meets-chore-system.md`
- `docs/design/adr/pool/ADR-pool.complexity-guide-obpi-authoring-integration.md`
- `docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/**` — brief evidence updates only

## Denied Paths

- `.gzkit/rules/complexity-doctrine.md` — rule file lands in OBPI-01
- `src/gzkit/complexity/measurement.py` — measurement pipeline is OBPI-03
- `pyproject.toml` — runtime dep declarations are OBPI-03
- `docs/governance/complexity/**` — distillation outputs are OBPI-04
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `data/exemplar_corpus.json` lists 12-15 projects (inclusive) covering at least eight of the ten archetypal cells from ADR-0.0.27 § Decision; vacant cells are explicit and rationaled, not silent.
2. REQUIREMENT: Each entry carries: project name, canonical URL, pinned commit SHA (40-char hex), included paths (glob list), excluded paths with rationale (glob → reason map), archetypal cell, longevity evidence, maintenance-health evidence, practitioner-reputation citation, pure-Python LOC ratio, craftsmanship-signal narrative, and project-doctrine-fitness narrative.
3. REQUIREMENT: The `ExemplarProject` Pydantic model uses `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`. No `dataclass`, no `Optional`/`List`, no implicit defaults.
4. REQUIREMENT: Every entry passes the seven selection criteria from `.gzkit/rules/complexity-doctrine.md` (OBPI-01 dependency); a project failing any criterion is rejected with the failure recorded in the brief evidence, not silently filtered.
5. REQUIREMENT: pytest is NOT in the corpus (project-doctrine-fitness; demerit-lesson canon). Pydantic is NOT in the corpus (Rust-core; pure-Python predominance fails). Both exclusions are explicit in the brief evidence.
6. REQUIREMENT: All six cluster pool stubs land as files under `docs/design/adr/pool/` with the canonical pool-ADR shape (`ADR-pool.<slug>.md`), each carrying a one-paragraph rationale citing this OBPI as the booking event. The six cluster pool stubs are: `attestation-quality-measurement`, `doctrine-amendment-protocol`, `complexity-doctrine-validate-suite`, `canon-pillar-codification`, `complexity-doctrine-meets-chore-system`, `complexity-guide-obpi-authoring-integration`.
7. REQUIREMENT: A JSON Schema at `src/gzkit/schemas/exemplar_corpus.json` mirrors the Pydantic model and is used by `gz validate --documents` to fail closed on schema drift.
8. REQUIREMENT: Tests cover: schema validates known-good corpus; schema rejects entries with non-SHA commit fields, missing path filters, or absent rationale; loader returns frozen models; mutation attempts raise; pool-stub files exist with expected shape. Each test decorated with `@covers(REQ-0.0.27-02-NN)`.
9. REQUIREMENT: Path filters are explicit at the project + module-subset level (e.g. Django excludes ORM query compiler, mypy excludes unification core); whole-project measurement is rejected.
10. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures; tests do not network out to clone repos (SHAs are recorded; clone-and-measure is OBPI-03's surface).
11. REQUIREMENT: NEVER include the operator's personal email in corpus entries, pool stubs, or test fixtures.

> STOP-on-BLOCKERS: if OBPI-01's `.gzkit/rules/complexity-doctrine.md` has not landed, STOP — selection criteria must be canonized before nominations are pinned.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.27-01 `Completed` — `.gzkit/rules/complexity-doctrine.md` (rule v0.1.0) is canon; selection criteria, corpus anti-patterns, distillation cadence, citation contract, and project-doctrine-fitness criterion all in place.
- [x] Parent ADR-0.0.27 § Decision — ten archetypal cells, locked per-cell candidates, corpus-size target 12-15.
- [x] Handoff `.gzkit/handoffs/2026-04-25-complexity-doctrine-cluster.md` — locked per-cell projects (Django, Starlette, httpx, click, attrs, CPython subsets, hypothesis, rich, mypy, flit).
- [x] `.gzkit/rules/models.md` — Pydantic immutable-model contract (`frozen=True, extra="forbid"`, no `Optional`/`List`, no implicit defaults).
- [x] `.claude/rules/cross-platform.md` — UTF-8 encoding + `pathlib.Path` discipline for file IO.

**Existing Code**

- [x] `src/gzkit/models/security_surfaces.py` — pattern reference for `frozen=True, extra="forbid"` model + `TypeAdapter` loader (OBPI-0.0.22-02 precedent).
- [x] `tests/models/test_security_surface_entry.py` — pattern reference for `@covers`-decorated REQ-derived model tests.
- [x] `src/gzkit/schemas/security_surfaces.json` — JSON Schema (Draft 2020-12) structural template with `additionalProperties: false`.
- [x] `src/gzkit/commands/validate_cmd.py:840` `_validate_manifest_documents` — extension point for fold-in corpus validation under the `--documents` scope.
- [x] `docs/design/adr/pool/ADR-pool.adr-amendment-tracking.md` — canonical pool-ADR shape + frontmatter convention for the six new pool stubs.

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle per assertion; `uv run gz test` passes

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] `mkdocs build --strict` clean (pool stubs render)

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: data-contract-only OBPI; CLI exposure is OBPI-03

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` confirmation; operator witnesses each nomination's craftsmanship signal

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz arb step --name unittest -- uv run -m unittest tests/models/test_exemplar.py tests/governance/test_exemplar_corpus.py -v
ls docs/design/adr/pool/ADR-pool.{attestation-quality-measurement,doctrine-amendment-protocol,complexity-doctrine-validate-suite,canon-pillar-codification,complexity-doctrine-meets-chore-system,complexity-guide-obpi-authoring-integration}.md
```

## Acceptance Criteria

- [ ] REQ-0.0.27-02-01: Given the corpus file, when the loader parses it, then 12-15 entries instantiate as frozen `ExemplarProject` models without validation error.
- [ ] REQ-0.0.27-02-02: Given an entry with a non-SHA commit field (e.g. branch name, tag), when the schema validates, then validation fails with a named error.
- [ ] REQ-0.0.27-02-03: Given an entry without per-project path filters or without rationale on excluded paths, when the schema validates, then validation fails.
- [ ] REQ-0.0.27-02-04: Given the corpus, when archetypal-cell coverage is checked, then at least eight of the ten cells are populated; vacant cells appear in the file as explicit `null` entries with rationale.
- [ ] REQ-0.0.27-02-05: Given pytest, Pydantic, or any project violating Stdlib-First, when corpus inclusion is checked, then the project is absent and the brief records the rejection.
- [ ] REQ-0.0.27-02-06: Given the six cluster pool-stub files, when listed under `docs/design/adr/pool/`, then each exists with the canonical pool-ADR shape and cites OBPI-0.0.27-02 as the booking event.
- [ ] REQ-0.0.27-02-07: Given a frozen `ExemplarProject` instance, when mutation is attempted, then a `ValidationError` is raised.
- [ ] REQ-0.0.27-02-08: Given the corpus file, when `uv run gz validate --documents` runs, then exit 0 and the JSON Schema mirror validates the file.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict clean
- [ ] Gate 4: BDD waiver registered
- [ ] Gate 5: TTY + `ATTEST` confirmation captured

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict output
```

### Gate 4 (BDD)
```text
# Waiver entry: data/behave_coverage_waivers.json — OBPI-0.0.27-02
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs at completion
```

### Value Narrative

Before this OBPI, the corpus methodology lived only in rule prose (`.gzkit/rules/complexity-doctrine.md` from OBPI-01) with no pinned authoritative list — nominations could drift session-to-session and downstream foundation ADRs (0.0.28 / 0.0.29 / 0.0.30) had no empirical anchor to cite. After this OBPI, 13 projects are pinned at 40-char-hex commit SHAs across all 10 archetypal cells, validated by a frozen `ExemplarProject` Pydantic model + JSON Schema mirror that fail-closes drift through `gz validate --documents`, with six forward-reference pool stubs making the citation graph honest from day one.

### Key Proof


```bash
$ uv run gz validate --documents
Validated: documents
✓ All validations passed (1 scopes).

$ uv run python -c "import sys; sys.stdout.reconfigure(encoding='utf-8'); from pathlib import Path; from gzkit.models.exemplar import load_corpus; c = load_corpus(Path('data/exemplar_corpus.json')); print(f'projects={len(c.projects)}, vacant={len(c.vacant_cells)}, cells={sorted({p.archetypal_cell for p in c.projects})}')"
projects=13, vacant=0, cells=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

$ ls docs/design/adr/pool/ADR-pool.{attestation-quality-measurement,doctrine-amendment-protocol,complexity-doctrine-validate-suite,canon-pillar-codification,complexity-doctrine-meets-chore-system,complexity-guide-obpi-authoring-integration}.md
docs/design/adr/pool/ADR-pool.attestation-quality-measurement.md
docs/design/adr/pool/ADR-pool.canon-pillar-codification.md
docs/design/adr/pool/ADR-pool.complexity-doctrine-meets-chore-system.md
docs/design/adr/pool/ADR-pool.complexity-doctrine-validate-suite.md
docs/design/adr/pool/ADR-pool.complexity-guide-obpi-authoring-integration.md
docs/design/adr/pool/ADR-pool.doctrine-amendment-protocol.md
```

Representative entry — Django (cell 1):

```json
{
  "name": "django",
  "canonical_url": "https://github.com/django/django",
  "commit_sha": "50bbf71bbd51616e2ce48785336ca3746fbe5f24",
  "archetypal_cell": 1,
  "included_paths": ["django/forms/**/*.py", "django/template/**/*.py", "..."],
  "excluded_paths_with_rationale": [
    {"glob": "django/db/models/sql/compiler.py",
     "exclusion_rationale": "ORM query compiler — irreducible algorithmic complexity per ADR-0.0.27 anti-pattern"}
  ],
  "pure_python_loc_ratio": 0.96,
  "...": "..."
}
```

### Implementation Summary


- Files created:
  - `src/gzkit/models/exemplar.py` — `ExemplarProject`, `ExcludedPath`, `VacantCell`, `ExemplarCorpus` Pydantic models (`frozen=True, extra="forbid"`); `load_corpus(Path)` loader
  - `src/gzkit/schemas/exemplar_corpus.json` — JSON Schema (Draft 2020-12) mirror with `additionalProperties: false` on every object schema
  - `data/exemplar_corpus.json` — 13 pinned projects covering all 10 archetypal cells; `corpus_revision: 1`
  - `tests/models/test_exemplar.py` — 48 tests (model frozen-contract, SHA validation, path-filter requiredness, vacant-cell shape, JSON-Schema parity, loader, validate-cmd integration)
  - `tests/governance/test_exemplar_corpus.py` — 14 tests asserting REQ-derived semantics on the on-disk corpus
  - `docs/design/adr/pool/ADR-pool.attestation-quality-measurement.md`
  - `docs/design/adr/pool/ADR-pool.doctrine-amendment-protocol.md`
  - `docs/design/adr/pool/ADR-pool.complexity-doctrine-validate-suite.md`
  - `docs/design/adr/pool/ADR-pool.canon-pillar-codification.md`
  - `docs/design/adr/pool/ADR-pool.complexity-doctrine-meets-chore-system.md`
  - `docs/design/adr/pool/ADR-pool.complexity-guide-obpi-authoring-integration.md`
- Files modified:
  - `src/gzkit/commands/validate_cmd.py` — `_validate_exemplar_corpus()` wired into `_validate_manifest_documents` so `gz validate --documents` fail-closes on corpus drift (REQ-08)
  - `data/behave_coverage_waivers.json` — Gate 4 BDD waiver entry under `adr-0.0.27-foundation-bdd-deferred` rationale (data-contract-only OBPI; CLI exposure deferred to OBPI-0.0.27-07)
  - `.gzkit/insights/agent-insights.jsonl:29` — in-flight shape fix (route-A side fix per operator direction; pre-existing record had `timestamp`/`evidence`-as-string drift)

- Tests added: 62 total — 48 in `tests/models/test_exemplar.py`, 14 in `tests/governance/test_exemplar_corpus.py`. All `@covers`-decorated against acceptance-criteria REQs (`gz covers OBPI-0.0.27-02 --json` reports 8/8 covered, `uncovered_reqs == 0`).

- Rejection records (REQ-04, REQ-05): two doctrine-incompatible candidates were considered and rejected during slate authoring; rejections are recorded here per the brief's "rejection recorded in brief evidence, not silently filtered" wording.

  **pytest** — rejected on project-doctrine-fitness criterion (`.gzkit/rules/complexity-doctrine.md` § criterion 6). pytest is widely-used and well-architected by conventional metrics, but its plugin architecture, fixture injection, and magic `conftest.py` discovery contradict gzkit's Stdlib-First doctrine and `forbid-pytest` pre-commit hook. The pytest-mention demerit during the ADR-0.0.27 design dialogue is the canonical lesson this rejection records.

  **Pydantic** — rejected on pure-Python predominance criterion (`.gzkit/rules/complexity-doctrine.md` § criterion 4). Pydantic v2 moved its validation core to Rust (`pydantic-core`); the Python part is glue, well below the ≥80% pure-Python LOC threshold. gzkit *uses* Pydantic at runtime (Stdlib-First named departure with rationale per `.gzkit/rules/models.md`), but Pydantic is not a *learning* relationship for Python design metrics — its design now lives in Rust.

  **httpx** — initially nominated for cell 3 (HTTP) but rejected on maintenance-health criterion (criterion 2): latest stable release 0.28.1 from 2024-12-06 is 17 months from the corpus-authoring date and the project does not declare a done state. Substituted with `urllib3` (latest 2.6.3 on 2026-01-07; passes all seven criteria).

- Date completed: 2026-05-04
- Attestation status: pending Gate 5 (Heavy + Foundation — TTY + `ATTEST` confirmation)
- Defects noted: none in scope. In-flight side fix to `.gzkit/insights/agent-insights.jsonl:29` brought the pre-existing `gz validate --insights-shape` failure to green; recorded above.

### Closing Argument

The operator-witnessed-nomination doctrine is the load-bearing structural defense of the entire complexity-doctrine cluster. An agent-only-authored corpus is `.gzkit/rules/complexity-doctrine.md` Anti-Pattern #6 by name — the same failure class as agent-synthesized attestation, because the corpus is doctrine and doctrine drift is invariant drift. This OBPI's slate was drafted by the agent against the seven criteria, but every nomination's craftsmanship narrative, every excluded path's rationale, and every pinned SHA passed through Stage 4 walkthrough before the brief was attested — Gate 5's TTY + `ATTEST` is the structural witness, not narrative recall. The per-project path-filter discipline closes the corpus-contamination class flagged in pre-mortem #1 of ADR-0.0.27: strategically-complex modules (Django ORM compiler, mypy expression-checker unification core) are excluded with named rationale rather than silently averaged into metric distributions that would drift toward leniency. The six pool-stub forward-references make the citation graph honest from day one — every anticipated amendment path has a named home, so future foundation drift surfaces as an activation event rather than a surprise.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.27-02 lands the empirical anchor of the complexity-doctrine cluster: 13 projects pinned at 40-char-hex SHAs across all 10 archetypal cells, immutable ExemplarProject Pydantic model with ConfigDict(frozen=True, extra="forbid"), JSON Schema mirror folded into gz validate --documents, and six pool-stub forward-references. 62/62 OBPI-scoped tests pass; gz covers OBPI-0.0.27-02 reports 8/8 REQs covered (uncovered_reqs=0). Lint: arb-ruff-dd688c2b9f6e4e6a9084d79368c12259. Typecheck: arb-step-typecheck-622545e590b744359adb0519dbcdd50c. OBPI tests: arb-step-unittest-caeba048a48d4e53a71bb462962868a3. Full unittest: arb-step-unittest-b50a7c08c7704d3dafb3a795d9b9c979. Mkdocs strict: arb-step-mkdocs-60f32dbdfc414082bd07733cf5595657. pytest + Pydantic + httpx rejection records present in brief Implementation Summary per .gzkit/rules/complexity-doctrine.md criteria 4 and 6.
- Date: 2026-05-04

---

**Brief Status:** Completed

**Date Completed:** 2026-05-04

**Evidence Hash:** -
