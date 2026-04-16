---
id: OBPI-0.25.0-13-qc-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 13
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-13: QC Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-13 — "Evaluate and absorb core/qc.py (18 lines) — quality control interfaces"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/qc.py` (18 lines) against gzkit's `quality.py` (773 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides quality control interfaces. gzkit's equivalent is 43x larger and addresses an entirely different domain (code quality vs. warehouse data integrity).

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/qc.py` (18 lines)
- **gzkit equivalent:** `src/gzkit/quality.py` (773 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- At 18 lines, airlineops's module is likely a thin facade or interface definition

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's quality module around airlineops's minimal interface

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## DECISION

**Decision: Exclude** — domain-specific, does not belong in gzkit.

**Rationale:** airlineops's `core/qc.py` (18 lines) is a thin facade that re-exports `run_integrity()` from `airlineops.reporter.reports.integrity_check`. It takes airline-domain-specific parameters (`dataset`, `db_path`, `fmt`, `out`) to run warehouse data integrity checks. The module has zero conceptual overlap with gzkit's `quality.py` (773 lines), which provides a comprehensive code quality framework: lint, format, typecheck, test orchestration, AST-based custom lint rules, drift advisory detection, product proof gates, and eval harness. Despite sharing the "quality/QC" name prefix, these modules address entirely different domains — data integrity vs. code quality. The airlineops module's sole function delegates to an airline-specific reporter subsystem (`airlineops.reporter.reports.integrity_check`) that has no analog in gzkit and no reusable pattern worth extracting. The subtraction test is decisive: `airlineops.core.qc - gzkit = pure airline domain`.

## COMPARISON ANALYSIS

| Dimension | airlineops (18 lines, 1 file) | gzkit (773 lines, 1 file) | Winner |
|-----------|-------------------------------|--------------------------|--------|
| Domain scope | Warehouse data integrity checks | Code quality (lint, format, typecheck, test, drift, eval) | N/A — different domains |
| Architecture | Thin facade re-exporting `run_integrity()` from `airlineops.reporter` | Comprehensive module with 10+ functions, 4 Pydantic models, AST-based custom linters | N/A — different domains |
| Interface abstraction | Single function: `run_integrity(dataset, db_path, fmt, out)` | `QualityResult` model, `CheckResult` aggregate, `DriftAdvisoryResult`, `ProductProofResult`, `ObpiProofStatus` | N/A — different domains |
| Error handling | None — delegates entirely to `_impl` | Typed `QualityResult` with returncode, stdout/stderr capture, `OSError`/`SubprocessError` handling | gzkit |
| Cross-platform | No file I/O, no path handling | `pathlib.Path`, UTF-8 encoding throughout, AST-based source scanning | gzkit |
| Test coverage | No tests visible in the facade | Covered by `tests/test_quality.py` and broader quality suite | gzkit |
| Reusable patterns | None — the facade pattern is trivial and the underlying function is airline-specific | `QualityResult` Pydantic model, `run_command()` subprocess wrapper, AST-based lint rules | gzkit |
| Dependencies | `airlineops.reporter.reports.integrity_check` — airline-domain import | `subprocess`, `ast`, `re`, `pydantic` — generic Python | gzkit |

### Key Finding

The name "QC" in airlineops refers to "Quality Control" in the airline operations sense — verifying warehouse data integrity (datasets, database paths). In gzkit, "quality" refers to code quality — linting, formatting, type checking, testing. These are completely different domains with no shared abstractions, interfaces, or patterns. The airlineops module is not a quality framework; it is a single-function facade for a domain-specific integrity check.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Exclude decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Exclude decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [x] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-13-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-13-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Eight-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-13-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-13-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Rationale in Decision section: airline-domain-specific with zero conceptual overlap.
- [x] REQ-0.25.0-13-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/qc.py
# Expected: airlineops source under review exists

test -f src/gzkit/quality.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-13-qc-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Exclude)
- [x] **Gate 3 (Docs):** Decision rationale completed
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Exclude, no behavior change)
- [x] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for an Exclude decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Exclude decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented comparison between airlineops's `core/qc.py` and gzkit's `quality.py`. The names suggested potential overlap ("QC" vs. "quality"), but thorough reading revealed they address entirely different domains: airlineops's module is an 18-line facade for warehouse data integrity checks delegating to `airlineops.reporter`, while gzkit's module is a 773-line code quality framework with Pydantic models, AST-based lint rules, drift detection, and product proof gates. The subtraction test is decisive — the airlineops module is pure airline domain with no reusable patterns.

### Key Proof


- Decision: Exclude
- airlineops `core/qc.py`: 18 lines, thin facade re-exporting `run_integrity()` for warehouse data integrity
- gzkit `quality.py`: 773 lines, comprehensive code quality framework (lint, format, typecheck, test, drift, eval, product proof)
- Zero conceptual overlap — different domains despite similar naming
- No reusable patterns — the facade pattern is trivial, the underlying function is airline-specific
- Subtraction test: `airlineops.core.qc - gzkit = pure airline domain`

### Implementation Summary


- Decision: Exclude
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Date: 2026-04-10

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-10

## Closing Argument

airlineops's `core/qc.py` (18 lines) is a thin facade that re-exports `run_integrity()` from `airlineops.reporter.reports.integrity_check` for warehouse data integrity checks. It takes airline-domain-specific parameters (`dataset`, `db_path`) and has zero conceptual overlap with gzkit's `quality.py` (773 lines), which provides code quality infrastructure: lint, format, typecheck, test orchestration, AST-based custom lint rules, drift advisory, product proof gates, and eval harness. The "QC" label in airlineops refers to operational quality control (data integrity), not code quality. No reusable patterns exist in the 18-line facade — the subtraction test is definitive. **Decision: Exclude.**
