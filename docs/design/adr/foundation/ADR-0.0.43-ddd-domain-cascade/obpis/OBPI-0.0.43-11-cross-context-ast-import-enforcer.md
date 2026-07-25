---
id: OBPI-0.0.43-11-cross-context-ast-import-enforcer
parent: ADR-0.0.43-ddd-domain-cascade
item: 11
lane: Heavy
status: Draft
---

# OBPI-0.0.43-11-cross-context-ast-import-enforcer: AST cross-context import enforcer

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #11 — "OBPI pipeline verify-stage AST cross-context import enforcer — Static AST analysis of Python source against DM Implementation Surface declarations; cross-context imports without context-map entry fail-closed during gz obpi pipeline verify stage; `# cascade-allowed: <reason>` inline marker honored with `cascade_import_bypass` ledger event; false-positive rate measured on existing corpus, reported in evidence (must be <5%)."

**Status:** Draft

## Objective

Land the strongest mechanical enforcement layer of the cascade: static AST analysis of Python source against DM Implementation Surface declarations. Cross-context imports without a context-map entry fail-closed at OBPI verify stage. The `# cascade-allowed: <reason>` inline marker provides an operator-attested bypass with a ledger event. False-positive rate on the existing gzkit corpus MUST be measured and reported as <5% (the shakiest condition from Tier-2 WWHTBT analysis).

## Lane

**Heavy** — adds a runtime-enforced gate to `gz obpi pipeline` verify stage. New static-analysis surface.

## Allowed Paths

- `src/gzkit/governance/cascade_import_check.py` — NEW; AST analyzer + enforcement logic
- `src/gzkit/pipeline/verify.py` — EXTEND verify stage to call cascade import check
- `tests/governance/test_cascade_import_check.py` — NEW
- `tests/pipeline/test_verify_cascade_import.py` — NEW
- `docs/governance/cascade-import-enforcer.md` — NEW (or extend `docs/governance/domain-cascade.md` from OBPI-12; this OBPI may author the dedicated technical doc or the OBPI-12 author folds it in)

## Denied Paths

- `src/gzkit/governance/domain_models.py` — OBPI-01 / 02 (consume only)
- Other schemas — other OBPI scopes
- `src/gzkit/governance/trust_audits/domain_cascade.py` — OBPI-06 (separate validator scope; this OBPI is a pipeline verify-stage hook, not a `gz validate` scope)
- `src/gzkit/cli/domain.py` — OBPI-03
- `src/gzkit/ledger/**` — OBPI-05 (this OBPI calls `emit_cascade_import_bypass` from cascade emitter)
- `.gzkit/skills/**` — OBPI-08 / 09 / 10
<!-- gz-validate-skip: brief-cross-references -->
- Runtime enforcement at import time (e.g., import hooks, `sys.meta_path` manipulation) — deferred to ADR-0.0.46 per parent ADR § Extension Points
- Runtime dependencies

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (AST analyzer).** Module parses each Python source file via `ast.parse`, walks `ast.Import` and `ast.ImportFrom` nodes, resolves each imported module to a file path, and maps each file path to a BC via DM `## Implementation Surface` declarations. Files outside any declared Implementation Surface are categorized as `bc: unassigned` (no enforcement target).
2. **REQUIREMENT (cross-context detection).** When source file in BC `X` imports a module in BC `Y` (X ≠ Y, both declared in their respective DMs), the enforcer checks PRD § 2.3 for a `(X, Y)` or `(Y, X)` context-map entry. Missing entry = enforcement violation.
3. **REQUIREMENT (inline-marker bypass).** `# cascade-allowed: <reason>` comment on the import line (or the line above) suppresses enforcement for that import. Reason MUST be non-empty (≥3 words). Bypass emits `cascade_import_bypass` event with `source_file`, `source_line`, `imported_module`, `reason`, `accepted_by` (parsed from `OBPI_ACTOR` env var or operator context).
4. **REQUIREMENT (false-positive rate measurement).** OBPI completion evidence MUST include a corpus-wide enforcer run with the false-positive rate measured: operator-classified false positives / total flagged imports. Run reports the ratio. <5% = OBPI passes. ≥5% = STOP-on-BLOCKERS escape; refine the analyzer or restrict scope per below.
5. **REQUIREMENT (analyzer scope restriction option).** If false-positive rate is ≥5% on first measurement, the analyzer MAY restrict to `src/gzkit/governance/` and `src/gzkit/domain/` (the cleanest cross-BC surface) and defer broader corpus coverage to a follow-on OBPI. Restriction is operator-attested in evidence.
6. **REQUIREMENT (pipeline integration).** `gz obpi pipeline <OBPI-ID> verify` invokes the cascade import check after standard verify checks. Failures exit 3 with `Resolve:` line naming (a) the offending import (b) the relevant context-map gap (c) the inline-marker bypass option.
7. **REQUIREMENT (`# cascade-allowed:` marker discipline).** Each bypass marker MUST be reviewable in code review (no programmatic insertion). Lint scope (separate; not implemented here) MAY warn on `cascade-allowed:` accumulation > N markers per file.
<!-- gz-validate-skip: brief-cross-references -->
8. **REQUIREMENT (no runtime enforcement).** This OBPI does NOT install Python import hooks or modify `sys.meta_path`. Static-only. Runtime enforcement is ADR-0.0.46 scope.
9. **REQUIREMENT (lazy/conditional import handling).** `importlib.import_module(...)` and conditional imports under `if TYPE_CHECKING:` are recognized but NOT flagged as violations (false-positive control). The analyzer emits a warning when these patterns appear in cross-context contexts so operators can review.
10. **REQUIREMENT (evidence document).** `docs/governance/cascade-import-enforcer.md` (or section in OBPI-12's `domain-cascade.md`) MUST document the analyzer's scope, limitations, false-positive policy, and `# cascade-allowed:` marker contract.

> STOP-on-BLOCKERS: if false-positive rate on the corpus is ≥5% AND scope restriction does not bring it under, halt and surface — the foundation can land without the runtime enforcer; this OBPI may be deferred or split.

## Discovery Checklist

**Parent ADR:**

- [ ] Parent ADR § Decision item #11 quoted
- [ ] Parent ADR § Intent — Tier-2 WWHTBT shakiest condition (false-positive rate)
- [ ] Parent ADR file

**Governance:**

- [ ] `AGENTS.md` § OBPI Pipeline mandate
- [ ] `.gzkit/rules/governance-core.md`
- [ ] `docs/governance/state-doctrine.md`

**Context:**

- [ ] OBPI-02 (DM with `ImplementationSurface`) landed
- [ ] OBPI-04 (frontmatter cascade keys) landed
- [ ] OBPI-05 (`cascade_import_bypass` emitter) landed
- [ ] OBPI-06 (`gz validate --domain-cascade`) landed
- [ ] Existing pipeline verify stage in `src/gzkit/pipeline/verify.py`

**Prerequisites:**

- [ ] OBPI-02 / OBPI-04 / OBPI-05 / OBPI-06 landed
- [ ] Existing OBPI pipeline runtime exists
- [ ] Python `ast` module behavior understood for the gzkit corpus' import patterns

**Existing Code:**

- [ ] `src/gzkit/pipeline/verify.py` for verify-stage hook insertion
- [ ] Sample analysis of import patterns in `src/gzkit/governance/` to estimate false-positive sources

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #11 quoted
- [ ] Intent recorded with Tier-2 WWHTBT reference

### Gate 2: TDD

- [ ] AST parsing test: simple import / from-import / aliased import recognized
- [ ] Cross-context detection: BC-X file importing BC-Y file → violation flagged; BC-X file importing BC-X file → no violation
- [ ] Context-map presence: BC-X importing BC-Y with PRD § 2.3 entry → no violation; without entry → violation
- [ ] Inline-marker bypass: `# cascade-allowed: testing only` on import line → no violation; ledger event emitted
- [ ] Inline-marker bypass: empty reason / single-word reason → violation (reason rejected)
- [ ] Lazy import (`importlib.import_module(...)`) → warning, not violation
- [ ] `if TYPE_CHECKING:` conditional import → no violation
- [ ] False-positive rate measurement test: run enforcer against test fixture corpus, assert <5% false positives on a fixture with known ground-truth labels
- [ ] Pipeline integration: `gz obpi pipeline ... verify` invokes the check; failure exits 3 with `Resolve:` line
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint / typecheck clean

### Gate 3: Docs (Heavy only)

- [ ] mkdocs build --strict clean
- [ ] `docs/governance/cascade-import-enforcer.md` (or OBPI-12 section) documents scope + limitations

### Gate 4: BDD (Heavy only)

- [ ] Scenario: developer introduces a cross-BC import without a context-map entry → `gz obpi pipeline ... verify` fails → developer adds `# cascade-allowed: refactor in flight` → next run passes with bypass event in ledger

### Gate 5: Human (Heavy + Foundation)

- [ ] Attestation recorded — MUST include false-positive rate measurement from corpus-wide run
- [ ] Attestor: operator name only

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Run enforcer against existing corpus and measure FP rate
uv run python -c "
from gzkit.governance.cascade_import_check import scan_corpus, false_positive_rate
results = scan_corpus(root='src/gzkit/')
print(f'Total flagged: {len(results.flagged)}')
print(f'False positives (operator-classified): see evidence')
"

# Run within a pipeline verify stage
uv run gz obpi pipeline OBPI-0.0.43-01 --from verify --dry-run
```

## Demo

```bash
# Introduce a deliberate cross-context import in a test fixture
echo "from gzkit.domain.experimentation_module import something" >> tests/fixtures/cascade_violator.py

# Run enforcer
uv run python -c "
from gzkit.governance.cascade_import_check import scan_file
result = scan_file('tests/fixtures/cascade_violator.py')
print(result.violations)
"

# Add bypass and re-run
sed -i.bak 's|from gzkit.domain.experimentation_module import something|from gzkit.domain.experimentation_module import something  # cascade-allowed: demo test fixture for OBPI-11|' tests/fixtures/cascade_violator.py
uv run python -c "
from gzkit.governance.cascade_import_check import scan_file
result = scan_file('tests/fixtures/cascade_violator.py')
print(f'Violations: {result.violations}; Bypasses: {result.bypasses}')
"

# Cleanup
rm tests/fixtures/cascade_violator.py tests/fixtures/cascade_violator.py.bak
```

## Acceptance Criteria

- [ ] REQ-0.0.43-11-01: Given a Python source file with a simple `import X` statement, when AST analyzer parses it, then `X`'s module path is resolved
- [ ] REQ-0.0.43-11-02: Given a BC-X file importing a BC-Y file with no PRD § 2.3 entry covering (X, Y), when scanner runs, then violation flagged
- [ ] REQ-0.0.43-11-03: Given a BC-X file importing a BC-Y file with a PRD § 2.3 entry covering (X, Y), when scanner runs, then no violation
- [ ] REQ-0.0.43-11-04: Given an import line with `# cascade-allowed: refactor in flight, full review`, when scanner runs, then no violation; `cascade_import_bypass` event emitted with the reason
- [ ] REQ-0.0.43-11-05: Given a `# cascade-allowed:` marker with single-word reason, when scanner runs, then violation flagged (reason rejected)
- [ ] REQ-0.0.43-11-06: Given an `importlib.import_module(...)` in cross-context source, when scanner runs, then warning emitted, not violation
- [ ] REQ-0.0.43-11-07: Given an import under `if TYPE_CHECKING:`, when scanner runs, then no violation
- [ ] REQ-0.0.43-11-08: Given a corpus-wide run with operator-classified ground truth, when false-positive rate is measured, then ratio reported in evidence; OBPI passes iff <5% OR scope-restriction taken with operator attestation
- [ ] REQ-0.0.43-11-09: Given a violation in `gz obpi pipeline ... verify`, when pipeline runs, then exit 3 with `Resolve:` line naming offending import + context-map gap + bypass option
- [ ] REQ-0.0.43-11-10: Given `docs/governance/cascade-import-enforcer.md` (or OBPI-12 section), when inspected, then scope, limitations, and bypass-marker contract documented

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR followed
- [ ] **Code Quality:** Clean
- [ ] **Gate 3 (Docs):** mkdocs + cascade enforcer doc clean
- [ ] **Gate 4 (BDD):** Scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded with measured false-positive rate
- [ ] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [ ] Intent recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/typecheck output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here; MUST include corpus-wide false-positive rate
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:
- Corpus-wide false-positive rate: TBD (must be <5% or scope-restriction attested)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`; MUST include false-positive rate measurement
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
