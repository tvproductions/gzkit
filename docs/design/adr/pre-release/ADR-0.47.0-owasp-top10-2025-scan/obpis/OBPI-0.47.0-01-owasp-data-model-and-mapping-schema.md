---
id: OBPI-0.47.0-01-owasp-data-model-and-mapping-schema
parent: ADR-0.47.0-owasp-top10-2025-scan
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.47.0-01-owasp-data-model-and-mapping-schema: OWASP scanner data model + mapping schema

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/ADR-0.47.0-owasp-top10-2025-scan.md`
- **Checklist Item:** #1 — `OBPI-0.47.0-01-owasp-data-model-and-mapping-schema: mapping.json data + OwaspScanReport Pydantic models + schema tests`

**Status:** Draft

## Objective

Land the `OwaspScanReport` / `OwaspFinding` Pydantic models, the JSON-schema'd `mapping.json` data file that binds OWASP Top 10:2025 categories (A01–A10) to the analyzer source family that scores them, and a schema-invariant test suite that fail-closes on any future drift away from the ADR's hard invariant: **no category may report `coverage == "mechanical"` unless ≥1 named analyzer (ruff `S`, stdlib-AST visitor, or reused chore) ran and produced findings or attested zero findings**.

This brief is the foundational data contract that OBPI-02 (chore runner), OBPI-03 (CLI verb), and OBPI-04 (synthesizer skill) all depend on. No analyzer code, no CLI plumbing, no skill authoring lands here — just the schema surface and its invariant tests.

## Lane

**Heavy** — defines a Pydantic schema contract that is consumed by external tooling (the chore runner, the CLI's `--json` output, and the skill's narrative renderer). Any future contract change is a downstream-breaking mutation.

> Sensitivity: `absent`. This brief authors only data definitions — no
> subprocess invocation, no analyzer logic, no security surface
> overlap per `data/security_surfaces.json`. Heavy lane already forces
> Gate 5 attestation; security-axis escalation would be cosmetic here.

## Allowed Paths

- `src/gzkit/scan/__init__.py` — new package init
- `src/gzkit/scan/models.py` — `OwaspScanReport`, `OwaspFinding`, `OwaspCoverage` Pydantic models
- `src/gzkit/scan/mapping.py` — typed loader for `mapping.json`
- `.gzkit/chores/owasp-top10-2025-scan/mapping.json` — A01–A10 → analyzer-source data
- `.gzkit/chores/owasp-top10-2025-scan/mapping.schema.json` — JSON Schema for `mapping.json`
- `tests/scan/__init__.py` — new test package init
- `tests/scan/test_owasp_models.py` — schema-invariant tests
- `tests/scan/test_owasp_mapping.py` — mapping.json parses against its JSON Schema
- `tests/scan/fixtures/valid_minimal_report.json` — happy-path `OwaspScanReport` payload
- `tests/scan/fixtures/invalid_a06_mechanical.json` — A06=mechanical negative-case fixture
- `tests/scan/fixtures/invalid_a07_other.json` — A07!=not-applicable negative-case fixture
- `tests/scan/fixtures/invalid_mechanical_floor.json` — mechanical-floor invariant negative-case fixture

## Denied Paths

- `src/gzkit/cli/**` — CLI plumbing belongs to OBPI-03; this brief MUST NOT touch argparse
- `.gzkit/chores/owasp-top10-2025-scan/runner.py` (or any runner module) — chore logic belongs to OBPI-02
- `.gzkit/skills/gz-owasp-scan/**` — skill authoring belongs to OBPI-04
- `docs/user/manpages/**` — manpage belongs to OBPI-03
- `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — runbook updates belong to OBPI-03 / OBPI-05
- `pyproject.toml`, `uv.lock` — no new dependencies (Pydantic already in pyproject)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `OwaspScanReport` MUST be a `BaseModel` with `model_config = ConfigDict(frozen=True, extra="forbid")` per `.gzkit/rules/models.md`.
2. REQUIREMENT: `OwaspScanReport.schema_version` MUST be `Literal["1.0"]` and `owasp_year` MUST be `Literal[2025]` — bumping either is a contract change.
3. REQUIREMENT: `OwaspScanReport.coverage` MUST be a `dict[str, Literal["mechanical", "partial-mechanical", "not-mechanical", "not-applicable"]]` keyed by `A01`..`A10`; missing keys fail validation.
4. REQUIREMENT: `OwaspFinding.source` MUST be a `Literal["ruff-S", "stdlib-ast", "chore-reused", "not-mechanical"]` and `category` MUST be `Literal["A01"..."A10"]`.
5. ALWAYS: A model validator on `OwaspScanReport` MUST reject any payload where a category's `coverage` value is `"mechanical"` but no `OwaspFinding` for that category has `source ∈ {"ruff-S", "stdlib-ast", "chore-reused"}` AND no zero-finding attestation is present in the report.
6. ALWAYS: A model validator MUST enforce `coverage["A06"] == "not-mechanical"` and `coverage["A07"] == "not-applicable"` (per ADR Decision § A01–A10 coverage map; A06 honesty is anti-vibing binding claim 4).
7. NEVER: This brief MUST NOT introduce code that imports from `src/gzkit/cli/`, `.gzkit/chores/owasp-top10-2025-scan/runner*`, or `.gzkit/skills/gz-owasp-scan/` — those are downstream consumers.
8. REQUIREMENT: `mapping.json` MUST validate against its companion `mapping.schema.json` and MUST contain entries for all of A01–A10 with `source` ∈ the same Literal set as `OwaspFinding.source` plus `judgment-only` and `not-applicable`.
9. ALWAYS: All Path fields MUST render relative paths via `.as_posix()` per `.gzkit/rules/cross-platform.md` (binding); `tests/scan/test_owasp_models.py` MUST include a Windows-separator regression assertion.

> STOP-on-BLOCKERS: if `pyproject.toml` does not already pin `pydantic >= 2`, halt and report.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote verbatim into Implementation Summary:** "Output schema (Pydantic) … `OwaspScanReport`: `schema_version: Literal[\"1.0\"]` … `coverage: dict[str, Literal[\"mechanical\", \"partial-mechanical\", \"not-mechanical\", \"not-applicable\"]]` — keyed by `A01`..`A10` … **Hard invariant:** No category may report `coverage == \"mechanical\"` unless ≥1 named analyzer (ruff `S` rule, stdlib-ast visitor, or reused chore) produced findings or attested zero findings on the scanned scope."
- [ ] Parent ADR § Intent — stdlib-first analyzer floor + A06 honesty.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.47.0-owasp-top10-2025-scan/ADR-0.47.0-owasp-top10-2025-scan.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `.gzkit/rules/models.md` — Pydantic-only doctrine; no stdlib `dataclasses`.
- [ ] `.gzkit/rules/pythonic.md` — module/function size limits, type-hint forms.
- [ ] `.gzkit/rules/cross-platform.md` — `Path.as_posix()` binding for relative paths.
- [ ] `AGENTS.md` § Stdlib-First doctrine — no third-party JSON Schema lib unless attested.

**Prerequisites (check existence, STOP if missing):**

- [ ] `pyproject.toml` already declares `pydantic >= 2` (verify, do not bump).
- [ ] `src/gzkit/` directory exists (it does).
- [ ] `.gzkit/chores/` directory exists (it does); the `.gzkit/chores/owasp-top10-2025-scan/` directory will be created by this brief.

**Existing Code (understand current state):**

- [ ] `src/gzkit/governance/` — read one model (`adr_doc.py` or similar) for `BaseModel` + `ConfigDict(frozen=True, extra="forbid")` precedent.
- [ ] `.gzkit/chores/dependency-currency/` — sibling chore directory for layout convention (CHORE.md, README.md, acceptance.json).
- [ ] `tests/governance/test_path_separator_portability.py` — pattern for the cross-platform `.as_posix()` regression assertion.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted in Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from REQs above, not from implementation
- [ ] RED→GREEN cycle followed for each invariant validator
- [ ] Tests pass: `uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan`
- [ ] Coverage floor: `uv run gz arb coverage run -m unittest discover -s tests/scan -t .`

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff`
- [ ] Type check clean: `uv run gz arb typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
- [ ] No new manpages or runbook changes in this brief (per Denied Paths)

### Gate 4: BDD (Heavy)

- [ ] N/A — this brief lands schema only; behavioural scenarios live in OBPI-03 (CLI) and OBPI-05 (dogfood).

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded; lane=heavy forces this independent of sensitivity axis.

## Verification

```bash
uv run gz validate --documents
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q tests/scan
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# Specific verification for this OBPI
test -f src/gzkit/scan/models.py
test -f .gzkit/chores/owasp-top10-2025-scan/mapping.json
test -f .gzkit/chores/owasp-top10-2025-scan/mapping.schema.json
uv run python -c "import json, jsonschema; jsonschema.validate(json.load(open('.gzkit/chores/owasp-top10-2025-scan/mapping.json')), json.load(open('.gzkit/chores/owasp-top10-2025-scan/mapping.schema.json')))"
```

## Demo

```bash
# Round-trip: build a fixture report, validate, dump JSON
uv run python -c "
from gzkit.scan.models import OwaspScanReport
report = OwaspScanReport.model_validate_json(open('tests/scan/fixtures/valid_minimal_report.json').read())
print(report.model_dump_json(indent=2)[:300])
"

# Negative path: A06=mechanical without analyzer findings must reject
uv run python -c "
from gzkit.scan.models import OwaspScanReport
import json
try:
    OwaspScanReport.model_validate_json(open('tests/scan/fixtures/invalid_a06_mechanical.json').read())
    raise SystemExit('FAIL: should have rejected A06=mechanical')
except Exception as e:
    print('OK: rejected -', type(e).__name__)
"
```

## Acceptance Criteria

- [ ] REQ-0.47.0-01-01: Given `mapping.json` and `mapping.schema.json`, when `tests/scan/test_owasp_mapping.py::test_mapping_validates_against_schema` runs, then `jsonschema.validate(mapping, schema)` returns without raising.
- [ ] REQ-0.47.0-01-02: Given a payload with `coverage["A06"] == "mechanical"`, when `OwaspScanReport.model_validate(...)` runs, then a `pydantic.ValidationError` is raised; `tests/scan/test_owasp_models.py::test_a06_must_be_not_mechanical` covers.
- [ ] REQ-0.47.0-01-03: Given any category with `coverage[CAT] == "mechanical"` but no `OwaspFinding` whose `category == CAT` has `source ∈ {"ruff-S", "stdlib-ast", "chore-reused"}` AND no zero-finding attestation, when `OwaspScanReport.model_validate(...)` runs, then `ValidationError` is raised; `tests/scan/test_owasp_models.py::test_mechanical_floor_invariant` covers.
- [ ] REQ-0.47.0-01-04: Given `coverage["A07"] != "not-applicable"`, when validate runs, then `ValidationError` is raised; `tests/scan/test_owasp_models.py::test_a07_must_be_not_applicable` covers.
- [ ] REQ-0.47.0-01-05: Given an `OwaspScanReport` instance, when serialized round-trips through `.model_dump_json()` → `.model_validate_json()`, then the resulting instance equals the original; `tests/scan/test_owasp_models.py::test_round_trip_equality` covers.
- [ ] REQ-0.47.0-01-06: Given a Path field on a Windows-style separator, when the model serializes, then the string form is forward-slash; `tests/scan/test_owasp_models.py::test_path_serialization_posix` covers (parallels `tests/governance/test_path_separator_portability.py`).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded; Decision quote in Implementation Summary
- [ ] **Gate 2 (TDD):** RGR cycle followed; six REQ-derived tests pass; coverage receipt captured
- [ ] **Code Quality:** `arb-ruff-*`, `arb-step-typecheck-*` receipts captured
- [ ] **Value Narrative:** Schema as the contract OBPI-02/03/04 build against
- [ ] **Key Proof:** Round-trip + invariant-rejection demos run cleanly
- [ ] **OBPI Acceptance:** Human attestation recorded (heavy lane)

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` § OBPI Acceptance Protocol.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded; Decision-quote present in Implementation Summary

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Receipts expected:
# arb-step-unittest-<sha>  (uv run -m unittest -q tests/scan)
# arb-step-coverage-<sha>  (uv run gz arb coverage run -m unittest discover -s tests/scan -t .)
```

### Code Quality

```text
# Receipts expected:
# arb-ruff-<sha>           (uv run gz arb ruff)
# arb-step-typecheck-<sha> (uv run gz arb typecheck)
```

### Gate 3 (Docs)

```text
# arb-step-mkdocs-<sha>    (uv run gz arb step --name mkdocs -- uv run mkdocs build --strict)
```

### Gate 4 (BDD)

```text
# N/A — schema-only brief; behavioural scenarios deferred to OBPI-03 / OBPI-05
```

### Gate 5 (Human)

```text
# Attestation text recorded at completion. Receipt via `gz adr emit-receipt`.
```

### Value Narrative

Before this OBPI: ADR-0.47.0 has a Pydantic schema in prose only. Anyone authoring the chore, CLI, or skill would re-derive the model shape from natural language, drifting against the hard invariant. After this OBPI: the schema is code; the hard invariant is a Pydantic validator; six REQ-derived tests fail-close on drift. The chore (OBPI-02), CLI (OBPI-03), and skill (OBPI-04) all import a single source of truth.

### Key Proof


`uv run python -c "from gzkit.scan.models import OwaspScanReport; OwaspScanReport.model_validate_json(open('tests/scan/fixtures/invalid_a06_mechanical.json').read())"` raises `ValidationError` — proving the A06-honesty invariant is mechanical, not narrative.

### Implementation Summary


`OwaspScanReport` and `OwaspFinding` Pydantic models landed at `src/gzkit/scan/models.py` with `ConfigDict(frozen=True, extra="forbid")` and four `@model_validator(mode="after")` invariants: `_coverage_keys_complete` (A01..A10 keyset exact), `_check_a06_not_mechanical` (REQ-02 — Insecure Design must report not-mechanical), `_check_a07_not_applicable` (REQ-04 — Authentication Failures not-applicable to Python library/CLI scope), `_check_mechanical_floor` (REQ-03 — `coverage[CAT]=="mechanical"` requires ≥1 finding with mechanical source OR `coverage_attestations[CAT]=True`). The typed mapping loader at `src/gzkit/scan/mapping.py` uses `jsonschema.Draft202012Validator` per the `archetype_rules.py:130-136` precedent. The A01-A10 → analyzer-source binding lives at `.gzkit/chores/owasp-top10-2025-scan/mapping.json` validated against `mapping.schema.json` (Draft 2020-12 with `source` accepting string-or-array union via `oneOf`); category names use OWASP **2025** nomenclature verbatim.

- Files created/modified: `src/gzkit/scan/__init__.py` (new package); `src/gzkit/scan/models.py` (Pydantic schema + 4 model validators + 2 field validators for posix-only path); `src/gzkit/scan/mapping.py` (typed loader); `.gzkit/chores/owasp-top10-2025-scan/mapping.json` (A01-A10 analyzer-source data); `.gzkit/chores/owasp-top10-2025-scan/mapping.schema.json` (Draft 2020-12 schema); `tests/scan/__init__.py`, `tests/scan/test_owasp_models.py` (5 REQ-covered methods), `tests/scan/test_owasp_mapping.py` (1 REQ-covered method + 1 loader sanity test); `tests/scan/fixtures/{valid_minimal_report,invalid_a06_mechanical,invalid_a07_other,invalid_mechanical_floor}.json`. Brief Allowed Paths refined to list explicit fixture files alongside `tests/scan/fixtures/`. Defect [GHI #433](https://github.com/tvproductions/gzkit/issues/433) (audit `lstrip` over-broad strip dropping dotfile-rooted creates) fixed in commit `fea540d7` before pipeline launch — added `_normalize_for_creates` helper preserving `.gzkit/`/`.claude/`/`.agents/`/`.github/` leading dots, with two regression tests.
- Tests added: 7 (6 REQ-covered via `@covers("REQ-0.47.0-01-NN")` + 1 loader sanity); `Ran 7 tests in 0.002s OK`.
- Date completed: 2026-05-10
- Attestation status: Heavy lane attestation by Jeffry Babb (operator-driven; agent-relayed via `--attestor-present`); behave-coverage waived under rationale `adr-0.47.0-bdd-deferred-to-obpi-03-and-obpi-05` per brief Gate-4 N/A line (BDD scenarios live in OBPI-03 CLI and OBPI-05 dogfood).
- Defects noted: None at OBPI-01 scope. Out-of-scope defect GHI #433 fixed in flight (≤10 SLOC, single module, defect-fix routing thresholds met).

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: OBPI-0.47.0-01 attested: 7 REQ-covered tests passing (arb-step-unittest-9ef8409116914ddb9f5bcce257681ee9); lint clean (arb-ruff-0f0d7620b10142ea82b2e575608631a8); typecheck clean (arb-step-typecheck-a7625eb6775849998b0f24425ea86d1b); coverage captured (arb-step-coverage-ad49b73a309f460d8b347cd3fdef1f3e); docs build clean (arb-step-mkdocs-2fbb3a764f6f4cf6ab246c8c43532378); OWASP 2025 names verbatim; ready for OBPI-02 chore runner.
- Date: 2026-05-10

---

**Brief Status:** Completed

**Date Completed:** 2026-05-10

**Evidence Hash:** -
