---
id: OBPI-0.25.0-06-registry-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 6
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-06: Registry Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-06 — "Evaluate and absorb core/registry.py (86 lines) — registry pattern implementation"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/registry.py` (86 lines) against gzkit's `registry.py` (217 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides a registry pattern with lookup facades. gzkit's equivalent is already 2.5x larger, suggesting gzkit may be more sophisticated — but the comparison must verify this.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/registry.py` (86 lines)
- **gzkit equivalent:** `src/gzkit/registry.py` (217 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's larger implementation may already subsume airlineops's capabilities

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Merging registry patterns if they serve fundamentally different purposes

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/registry.py` (86 lines) defines a `StrategyRegistry` that resolves callable strategy functions from airline profile descriptors. The `StrategySpec` dataclass holds a name, function reference, and description. The registry's convenience getters — `get_bank_window_strategy()`, `get_seasonality_strategy()`, `get_seat_trim_strategy()`, `get_export_hook()` — are airline schedule optimization concepts with no governance analogue. The `resolve_strategies()` function maps logical strategy names from a profile dict to registered callables, a pattern specific to airline engine delegation.

gzkit's `registry.py` (217 lines) implements a `ContentTypeRegistry` with Pydantic `ContentType` models providing schema validation, lifecycle states, canonical path patterns, and vendor rendering rules. It registers 8 governance content types (ADR, OBPI, PRD, Constitution, Rule, Skill, Attestation, LedgerEvent) at import time via `_bootstrap_registry()`. gzkit's implementation is already 2.5x larger, uses Pydantic `BaseModel` (not `@dataclass`), and includes frontmatter validation via `validate_artifact()` — capabilities airlineops's registry does not provide.

The two registries share only the generic register/get/list pattern (~15 lines of boilerplate), which is already implemented in gzkit. Everything beyond that boilerplate is domain-specific: airline strategy resolution in airlineops, governance content type cataloging in gzkit.

## COMPARISON ANALYSIS

| Dimension | airlineops (86 lines, 1 file) | gzkit `registry.py` (217 lines) | Assessment |
|-----------|-------------------------------|----------------------------------|------------|
| Purpose | Strategy function registry for airline engine delegation | Content type registry for governance artifact cataloging | **Different concerns** — no functional overlap beyond register/get/list boilerplate |
| Data model | `StrategySpec` (`@dataclass(frozen=True)`) with `name`, `fn` (callable), `description` | `ContentType` (Pydantic `BaseModel`, `frozen=True`, `extra="forbid"`) with `name`, `schema_name`, `frontmatter_model`, `lifecycle_states`, `canonical_path_pattern`, `vendor_rendering_rules` | gzkit is richer — 6 typed fields with validation vs. 3 simple fields |
| Validation | None — registry stores/retrieves callables without validation | `validate_artifact()` — Pydantic frontmatter validation with structured error translation | gzkit has validation; airlineops does not |
| Domain coupling | `get_bank_window_strategy()`, `get_seasonality_strategy()`, `get_seat_trim_strategy()`, `get_export_hook()` — airline schedule optimization | ADR, OBPI, PRD, Constitution, Rule, Skill, Attestation, LedgerEvent — governance artifacts | Both are domain-specific |
| Registration | `register(name, fn, description)` — stores callables | `register(content_type)` — stores Pydantic models | Same pattern, different payloads |
| Lookup | `get(name)` → `StrategyFn` | `get(name)` → `ContentType` | Same pattern |
| Listing | `list_names()` → sorted name strings | `list_all()` → `ContentType` objects in registration order | Same pattern, different return types |
| Profile resolution | `resolve_strategies(profile)` — maps logical names from profile dict to registered callables | N/A — no profile resolution concept | Airline-specific |
| Convenience getters | 4 domain-specific getters with lambda fallbacks | N/A | Airline-specific |
| Singleton | Module-level `REGISTRY = StrategyRegistry()` | Module-level `REGISTRY = ContentTypeRegistry()` with `_bootstrap_registry()` | Same pattern |
| Error handling | `ValueError` for duplicate names, `KeyError` for unknown names | `ValueError` for duplicates, `KeyError` for unknown, `TypeError` for missing model | gzkit has richer error handling |
| Test coverage | N/A (not evaluated in airlineops context) | `tests/test_registry.py` exists | gzkit already tested |

### Subtraction Test

Removing gzkit from airlineops's `registry.py` leaves: airline strategy resolution (`StrategyRegistry` mapping profile descriptors to callable strategies), airline-domain convenience getters (bank window, seasonality, seat trim, export hook), and profile-based strategy lookup (`resolve_strategies()`). These are airline schedule optimization constructs with no governance analogue. The only generic construct — register/get/list boilerplate (~15 lines) — is already implemented in gzkit's `ContentTypeRegistry`. The subtraction test is decisive: this module is airline-domain code.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
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

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-06-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-06-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Twelve-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-06-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-06-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-06-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/registry.py
# Expected: airlineops source under review exists

test -f src/gzkit/registry.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-06-registry-pattern.md
# Expected: completed brief records one final decision

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

Before this OBPI, there was no documented evaluation of whether airlineops's `core/registry.py` contained reusable patterns for gzkit. Both codebases have a module named `registry.py`, creating a surface-level impression of overlap. After reading both implementations completely, they address entirely different concerns: airlineops's `StrategyRegistry` resolves callable strategy functions from airline profile descriptors (bank windows, seasonality, seat trim, export hooks), while gzkit's `ContentTypeRegistry` catalogs governance content types with Pydantic validation, lifecycle states, schema integration, and vendor rendering rules. The only shared construct is the generic register/get/list boilerplate (~15 lines), which gzkit already implements with richer error handling and validation. The four convenience getters (`get_bank_window_strategy`, `get_seasonality_strategy`, `get_seat_trim_strategy`, `get_export_hook`) and the `resolve_strategies()` profile mapper are airline schedule optimization concepts. The subtraction test is decisive: this module is pure airline domain code.

### Key Proof


- Decision: Exclude
- Comparison: twelve-dimension analysis in Comparison Analysis section
- airlineops registry.py: 86 lines, `StrategyRegistry` for airline strategy function resolution
- Domain-specific constructs: `get_bank_window_strategy()`, `get_seasonality_strategy()`, `get_seat_trim_strategy()`, `get_export_hook()`, `resolve_strategies()` — all airline schedule optimization
- gzkit registry.py: 217 lines, `ContentTypeRegistry` with Pydantic validation, 8 content types, lifecycle states — already 2.5x larger and more sophisticated
- Shared boilerplate: register/get/list (~15 lines) — already implemented in gzkit
- Subtraction test: entire module beyond boilerplate is airline domain — fails completely

### Implementation Summary


- Decision: Exclude — airlineops `core/registry.py` (86 lines) is airline-domain-specific
- Module: strategy function registry for airline engine delegation with domain-specific convenience getters
- Subtraction test: removing gzkit leaves airline strategy resolution code (bank windows, seasonality, seat trim, export hooks)
- Shared boilerplate: register/get/list (~15 lines) already implemented in gzkit with richer validation
- Files created: none
- Files modified: this brief only (Exclude decision with twelve-dimension comparison analysis)
- Tests added: none (no code changes)
- Date: 2026-04-09

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-09

## Closing Argument

airlineops's `core/registry.py` (86 lines) defines a `StrategyRegistry` that resolves callable strategy functions from airline profile descriptors using `StrategySpec` (`@dataclass(frozen=True)` with `name`, `fn`, `description`). The convenience getters — `get_bank_window_strategy()`, `get_seasonality_strategy()`, `get_seat_trim_strategy()`, `get_export_hook()` — and the `resolve_strategies()` profile mapper are airline schedule optimization concepts with no governance analogue. gzkit's `ContentTypeRegistry` (217 lines) already implements a more sophisticated registry with Pydantic `ContentType` models, frontmatter validation via `validate_artifact()`, lifecycle states, schema integration, canonical path patterns, and vendor rendering rules across 8 registered governance content types. The two registries share only the generic register/get/list boilerplate (~15 lines), which gzkit already has. The subtraction test is unambiguous: removing gzkit from this module leaves pure airline domain code — strategy resolution for bank windows, seasonality, seat trim, and export hooks. **Decision: Exclude.**
