---
id: OBPI-0.0.27-02-initial-corpus-authoring
parent: ADR-0.0.27
item: 2
lane: Heavy
status: Draft
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

- [ ] OBPI-01 (`.gzkit/rules/complexity-doctrine.md`) — selection criteria + anti-patterns canonized
- [ ] Parent ADR § Decision — ten archetypal cells, locked per-cell candidates, corpus size target
- [ ] Handoff `.gzkit/handoffs/2026-04-25-complexity-doctrine-cluster.md` — locked per-cell projects (Django, Starlette, httpx, click, attrs, CPython subsets, hypothesis, rich, mypy, flit)
- [ ] `.claude/rules/models.md` — Pydantic immutable model patterns
- [ ] Existing pool ADRs under `docs/design/adr/pool/` — file shape and frontmatter convention

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

<!-- Problem before: corpus methodology was rule prose with no pinned authoritative list; nominations could drift session-to-session. Capability now: 12-15 projects pinned at SHA with explicit path filters and craftsmanship justifications, validated by a frozen Pydantic schema, with six forward-reference pool stubs making the citation graph honest from day one. -->

### Key Proof

<!-- Paste a representative entry from data/exemplar_corpus.json and the listing of six pool-stub files. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

<!-- One paragraph: why operator-witnessed nominations beat agent-supplied lists, how the per-project path filter closes the corpus-contamination class, and why pool-stub forward-references are the right shape for the citation graph. -->

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires TTY + ATTEST)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
