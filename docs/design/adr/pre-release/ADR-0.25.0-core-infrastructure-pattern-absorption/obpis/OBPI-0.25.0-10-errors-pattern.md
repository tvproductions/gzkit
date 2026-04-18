---
id: OBPI-0.25.0-10-errors-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 10
status: in_progress
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-10: Errors Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-10 — "Evaluate and absorb core/errors.py (53 lines) — exception hierarchy"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/errors.py` (53 lines) and determine:
Absorb (airlineops is better) or Exclude (domain-specific). The airlineops
module provides an exception hierarchy with error classification. gzkit
currently has no dedicated errors module, relying on ad-hoc exception
handling. The comparison must determine whether airlineops's error hierarchy
is generic enough to standardize gzkit's exception patterns.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/errors.py` (53 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- A structured exception hierarchy aligns with gzkit's Pythonic standards (explicit exceptions, typed errors)

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Migrating all existing gzkit exception handling in this OBPI

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/errors.py` (53 lines) is misnamed — it is not an exception hierarchy. It is a thin UI error rendering facade that wraps `render_error_panel` from `airlineops.warehouse.bootstrap.common`. The function takes airline-specific parameters (`dataset`, `period`, `phase`, `exc`) and renders Rich error panels for warehouse dataset processing failures. The module contains zero exception classes, zero error classification, and zero reusable error-handling patterns. Its `__all__` exports only `render_error_panel`.

gzkit already has `src/gzkit/core/exceptions.py` (96 lines) — a well-structured typed exception hierarchy with exit-code classification aligned to the CLI Standard 4-Code Map: `GzkitError` (base), `ValidationError`, `ResourceNotFoundError`, `PermanentError`, `OperatorError` (exit code 1), `TransientError` (exit code 2), `PolicyBreachError` (exit code 3). Additionally, `commands/common.py` defines `GzCliError(GzkitError)` for user-facing CLI errors, and `eval/datasets.py` defines `DatasetValidationError(ValueError)` for domain-specific validation. gzkit's exception hierarchy is substantially more sophisticated than anything in the airlineops module.

## COMPARISON ANALYSIS

| Dimension | airlineops `core/errors.py` (53 lines) | gzkit `core/exceptions.py` (96 lines) | Assessment |
|-----------|----------------------------------------|----------------------------------------|------------|
| Purpose | UI error rendering facade for warehouse dataset failures | Typed exception hierarchy with exit-code classification | **Different concerns** — rendering vs. classification |
| Exception classes | None — zero exception classes defined | 6 exception classes (`GzkitError`, `ValidationError`, `ResourceNotFoundError`, `PermanentError`, `OperatorError`, `TransientError`, `PolicyBreachError`) + `GzCliError` | gzkit is categorically ahead |
| Error classification | None | Standard 4-Code Map: exit 1 (user/config), exit 2 (system/IO), exit 3 (policy breach) | gzkit has structured classification; airlineops has none |
| Exit codes | None | `exit_code` property on every exception class | gzkit only |
| Domain coupling | `dataset`, `period`, `phase` parameters — airline warehouse pipeline concepts | Content-type agnostic governance exceptions | airlineops is airline-domain-specific |
| Error rendering | `render_error_panel()` — Rich error panel via `airlineops.warehouse.bootstrap.common` | N/A (rendering handled by CLI boundary in `__main__.py`) | Airline-specific UI rendering |
| Fallback handling | Plain-text stderr fallback when Rich unavailable | N/A (separate concern) | Airline-specific fallback |
| Import surface | Delegates to `airlineops.warehouse.bootstrap.common` | Standalone, no external dependencies | gzkit is self-contained |
| Reusable patterns | None — the entire module is a delegation facade | Exception hierarchy pattern, exit-code property pattern, backward-compatibility aliases | gzkit has all the reusable patterns |
| Cross-platform | N/A | N/A (exceptions are platform-agnostic) | No difference |

### Subtraction Test

Removing gzkit from airlineops's `core/errors.py` leaves: a `render_error_panel()` function that takes `dataset` (BTS/FAA dataset name), `period` (data period), `phase` (processing phase), and `exc` (exception), delegates to `airlineops.warehouse.bootstrap.common.render_error_panel`, and falls back to stderr output. Every parameter and every delegation target is airline-domain-specific. There are zero generic error-handling patterns — the module is a UI rendering wrapper, not an exception hierarchy. The subtraction test fails entirely: this module is pure airline domain code.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, new gzkit module/tests are added or updated — N/A (Exclude decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Exclude` decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the absorbed pattern changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Exclude decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-10-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-10-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Ten-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-10-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-10-04: [doc] Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-10-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/errors.py
# Expected: airlineops source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-10-errors-pattern.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-10-errors-pattern.md
# Expected: absorb path names concrete target paths, or exclude rationale is documented

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Exclude)
- [x] **Gate 3 (Docs):** Decision rationale completed with comparison table
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Exclude, no behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

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

Before this OBPI, there was no documented evaluation of whether airlineops's `core/errors.py` contained reusable exception patterns for gzkit. The ADR description listed this as an "exception hierarchy" — but after reading the actual source completely, the module is not an exception hierarchy at all. It is a thin UI error rendering facade (53 lines) that wraps `render_error_panel` from `airlineops.warehouse.bootstrap.common`, taking airline-specific parameters (`dataset`, `period`, `phase`) to render Rich error panels for warehouse dataset processing failures. It contains zero exception classes. Meanwhile, gzkit already has `core/exceptions.py` (96 lines) — a well-structured typed exception hierarchy with six exception classes, exit-code classification aligned to the CLI Standard 4-Code Map, and backward-compatibility aliases. The subtraction test is decisive: the entire airlineops module is airline-domain UI code with no reusable error-handling patterns.

### Key Proof


- Decision: Exclude
- Comparison: ten-dimension analysis in Comparison Analysis section
- airlineops core/errors.py: 53 lines, UI error rendering facade (NOT an exception hierarchy)
- Module exports: only render_error_panel() with airline-specific params (dataset, period, phase)
- Exception classes defined: zero
- gzkit core/exceptions.py: 96 lines, typed exception hierarchy with 6 classes and exit-code classification
- Subtraction test: entire module is airline domain — fails completely

### Implementation Summary


- Decision: Exclude — airlineops core/errors.py (53 lines) is airline-domain-specific
- Module: UI error rendering facade wrapping render_error_panel for warehouse dataset failures
- Subtraction test: removing gzkit leaves pure airline domain code (dataset/period/phase error rendering)
- ADR description corrected: module is a UI facade, not an exception hierarchy
- gzkit already ahead: core/exceptions.py (96 lines) has typed hierarchy with 6 exception classes
- Files created: none
- Files modified: this brief only (Exclude decision with ten-dimension comparison analysis)
- Tests added: none (no code changes)
- Date: 2026-04-10

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-10

## Closing Argument

airlineops's `core/errors.py` (53 lines) is a thin UI error rendering facade — not an exception hierarchy as described in the ADR. The module wraps `render_error_panel` from `airlineops.warehouse.bootstrap.common`, taking airline-specific parameters (`dataset` for BTS/FAA dataset names, `period` for data periods, `phase` for processing phases, `exc` for the caught exception) and rendering Rich error panels for warehouse dataset processing failures. It exports only `render_error_panel` and defines zero exception classes, zero error classification, and zero reusable error-handling patterns. gzkit already has `src/gzkit/core/exceptions.py` (96 lines) — a well-structured typed exception hierarchy with six exception classes (`GzkitError`, `ValidationError`, `ResourceNotFoundError`, `PermanentError`, `OperatorError`, `TransientError`, `PolicyBreachError`), exit-code classification aligned to the CLI Standard 4-Code Map, and additional domain exceptions (`GzCliError`, `DatasetValidationError`) in other modules. The subtraction test is unambiguous: every parameter, every delegation target, and every fallback path in the airlineops module is airline-domain-specific. There are no reusable exception patterns to absorb. **Decision: Exclude.**
