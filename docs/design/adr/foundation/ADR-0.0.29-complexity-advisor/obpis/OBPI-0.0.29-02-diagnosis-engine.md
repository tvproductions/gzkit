---
id: OBPI-0.0.29-02-diagnosis-engine
parent: ADR-0.0.29
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.29-02-diagnosis-engine: Diagnosis Engine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #2 — "Diagnosis engine (binds ThresholdTable + distilled-characteristics; refactor-archetype rules data-driven at data/advisor_archetype_rules.json)"

**Status:** Draft

## Objective

Implement the diagnosis engine at `src/gzkit/complexity/advisor/engine.py` that, given an AST context plus a metric crossing, returns an `AdvisorDiagnosis`. Bind to `ThresholdTable` (ADR-0.0.28-02) for band classification and to OBPI-0.0.27-04's distilled-characteristics document for doctrinal-frame attribution. Refactor-archetype detection rules are data-driven at `data/advisor_archetype_rules.json` (rules are doctrine; amendments flow through the doctrine-amendment-protocol pool stub).

## Lane

**Heavy** — New runtime engine consumed by OBPI-03 CLI and OBPI-05 auto-chain hook. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/advisor/engine.py`
- `src/gzkit/complexity/advisor/archetype_rules.py` — rule loader for `data/advisor_archetype_rules.json`
- `data/advisor_archetype_rules.json`
- `src/gzkit/schemas/advisor_archetype_rules.json` — JSON Schema for the rule file
- `tests/complexity/advisor/test_engine.py`, `tests/complexity/advisor/test_archetype_rules.py`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-02-diagnosis-engine.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is OBPI-01 (consumed, not edited)
- `src/gzkit/complexity/thresholds.py` — ThresholdTable is ADR-0.0.28-02 (consumed, not edited)
- `src/gzkit/complexity/citation.py` — citation parser is OBPI-0.0.27-05 (consumed, not edited)
- `src/gzkit/commands/complexity_advise.py` — CLI is OBPI-03
- `src/gzkit/complexity/advisor/intrinsic.py` — attestation is OBPI-07
- `src/gzkit/complexity/advisor/timeout.py` — timeout is OBPI-09
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `engine.diagnose(ast_context: AstContext, metric: str, value: float, table: ThresholdTable) -> AdvisorDiagnosis | None` returns a diagnosis when the value crosses any band, `None` when below all bands. Imports `ThresholdTable` from ADR-0.0.28-02; never reimplements band classification.
2. REQUIREMENT: `AstContext` is a frozen Pydantic model with `file_path: str`, `source: str`, `tree: ast.Module`, `target_node: ast.AST`. The engine accepts the context as input; AST construction is the caller's responsibility (the CLI, the auto-chain hook).
3. REQUIREMENT: The refactor-archetype detection rule table at `data/advisor_archetype_rules.json` is loaded once per engine instantiation. The rule shape: each rule names an `archetype: RefactorArchetype`, a `metric_predicate` (which metrics + bands the rule applies to), an `ast_predicate` (the AST shape the rule looks for; e.g. "FunctionDef with > N parameters" → `long_parameter_list`), and a `doctrinal_frame` (authority + citation + excerpt).
4. REQUIREMENT: For each metric crossing, the engine evaluates archetype rules in declared order; the first matching rule's `archetype` and `doctrinal_frame` are bound to the resulting diagnosis. If no rule matches, the engine emits a diagnosis with `archetype=long_parameter_list` (the lowest-specificity default) and a `doctrinal_frame` citing the metric's distilled-characteristics doctrinal-frame entry — never a fabricated frame.
5. REQUIREMENT: The engine populates `proof: tuple[ProofRange, ...]` from the matched AST nodes; an empty `proof` causes the engine to fail closed (raise `EngineError`) rather than emit a malformed diagnosis. This codifies ADR § Decision rationale #5 at the engine layer (model-layer enforcement is OBPI-01; engine-layer enforcement is here — defense-in-depth).
6. REQUIREMENT: The engine reads OBPI-0.0.27-04's distilled-characteristics document (path resolved from the active citation tuple in the threshold table) to populate `recommended_move` from the per-metric "Practitioner-eye observation" section. If the cited document is missing or the citation is unparseable, the engine fails closed with a named error referencing OBPI-0.0.27-07's link-integrity validator as the resolution path.
7. REQUIREMENT: The JSON Schema at `src/gzkit/schemas/advisor_archetype_rules.json` is `extra="forbid"`-equivalent and validates: rule file is a non-empty array; each rule has `archetype` ∈ ten-value enum; `metric_predicate` and `ast_predicate` are non-empty; `doctrinal_frame.authority` ∈ four-value enum.
8. REQUIREMENT: Tests cover: engine returns `None` below all bands; engine returns diagnosis at warn band crossing with matching archetype rule; engine returns diagnosis at block band; engine fails closed on empty proof; engine fails closed on missing distilled-characteristics document; rule-table load rejects malformed rules; default-archetype fallback returns `long_parameter_list` when no rule matches; `recommended_move` is populated from distilled-characteristics, never from agent training memory. Each test decorated with `@covers(REQ-0.0.29-02-NN)`. Tests use synthetic AST fixtures and synthetic distilled-characteristics fixtures; no live corpus.
9. REQUIREMENT: Function-size discipline per `.claude/rules/pythonic.md` — engine decomposes into named helpers (rule evaluation, archetype matching, proof extraction, doctrinal-frame attribution).
10. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures.
11. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, rule data, or docstrings.

> STOP-on-BLOCKERS: if OBPI-01's `AdvisorDiagnosis`/`DoctrinalFrame`/`ProofRange` are not present, OR if ADR-0.0.28-02's `ThresholdTable` is not importable, OR if ADR-0.0.27-04's distilled-characteristics document does not yet exist, STOP. Engine cannot operate without all three.

## Discovery Checklist

- [ ] OBPI-01 schema (`src/gzkit/complexity/advisor/diagnosis.py`)
- [ ] ADR-0.0.28-02 `ThresholdTable` (`src/gzkit/complexity/thresholds.py`)
- [ ] OBPI-0.0.27-04 distilled-characteristics document — concrete artifact engine reads
- [ ] OBPI-0.0.27-05 `parse_citation` (`src/gzkit/complexity/citation.py`)
- [ ] Parent ADR § Decision — engine binding, archetype rules data-driven
- [ ] `.claude/rules/pythonic.md` — function-size discipline

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: engine-internal OBPI; user-facing scenarios at OBPI-03 CLI

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_engine.py tests/complexity/advisor/test_archetype_rules.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.29-02-01: Given a metric value below all bands, when `engine.diagnose` runs, then `None` is returned.
- [ ] REQ-0.0.29-02-02: Given a value crossing the warn band + an AST whose shape matches a rule, when the engine runs, then a diagnosis is returned with the matching `archetype` and `doctrinal_frame`.
- [ ] REQ-0.0.29-02-03: Given the engine produces a diagnosis with empty proof, when the diagnosis is constructed, then `EngineError` is raised before model instantiation.
- [ ] REQ-0.0.29-02-04: Given the cited distilled-characteristics document does not exist, when the engine runs, then `EngineError` referencing OBPI-0.0.27-07 is raised.
- [ ] REQ-0.0.29-02-05: Given the rule table at `data/advisor_archetype_rules.json`, when loaded, then each rule passes the JSON Schema; a malformed rule causes load to fail closed.
- [ ] REQ-0.0.29-02-06: Given no archetype rule matches a metric crossing, when the engine runs, then `archetype=long_parameter_list` (default) is bound and `recommended_move` is populated from the distilled-characteristics document, never from a fabricated string.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: docs clean
- [ ] Gate 4: BDD waiver registered
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
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
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.29-02
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
