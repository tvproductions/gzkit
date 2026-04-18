---
id: OBPI-0.25.0-05-dataset-version-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 5
status: in_progress
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-05: Dataset Version Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-05 — "Evaluate and absorb core/dataset_version.py (246 lines) — version management utilities"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/dataset_version.py` (246 lines) against gzkit's partial version management in `lifecycle.py` and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides version management utilities and semantic versioning patterns. gzkit has partial coverage in `lifecycle.py`, so the comparison must determine whether the airlineops patterns fill genuine gaps.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/dataset_version.py` (246 lines)
- **gzkit equivalent:** Partial in `src/gzkit/lifecycle.py`

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- "Dataset version" may contain airline-specific semantics that do not generalize — careful evaluation needed

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Replacing gzkit's existing lifecycle management if it is already sufficient

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/dataset_version.py` (246 lines) defines content-addressable dataset version identity for airline data pipelines. The `DatasetVersion` model's fields (`dataset_id`, `source_version`, `schema_version`, `etl_version`, `content_hash`, `version_hash`) are built around airline dataset semantics: `dataset_id` identifies BTS/FAA datasets (e.g., "bts_db28dm_market"), `source_version` tracks BTS/FAA archive releases, `schema_version` and `etl_version` track airline ETL pipeline components. The factory function `create_dataset_version()` composes these airline-specific fields into a composite identity hash. The serialization helpers `version_to_dict()` and `version_from_dict()` are thin wrappers around Pydantic's `.model_dump()` and `(**data)` — patterns gzkit already uses by convention.

The brief's premise that gzkit's `lifecycle.py` provides "partial coverage" is incorrect. `lifecycle.py` (128 lines) implements a state machine for governance artifact transitions (Draft → Proposed → Accepted, etc.) — a completely different concern from dataset version identity and content hashing. There is zero functional overlap between these modules.

The generic primitives are: `compute_content_hash()` — SHA-256 of raw bytes in `sha256:hexdigest` format (~3 lines), `compute_version_hash()` — deterministic JSON serialization with `sort_keys` → SHA-256 (~10 lines), frozen Pydantic model with custom `__eq__`/`__hash__` (~8 lines), and semver/hash format validators (~12 lines). Combined, these total ~33 lines of trivial utility code. gzkit has no `hashlib` usage anywhere in `src/gzkit/` and no content-addressable versioning use case today.

## COMPARISON ANALYSIS

| Dimension | airlineops (246 lines, 1 file) | gzkit `lifecycle.py` (128 lines) | Assessment |
|-----------|-------------------------------|----------------------------------|------------|
| Purpose | Content-addressable dataset version identity for airline data pipelines | Governance artifact lifecycle state machine (Draft → Proposed → Accepted, etc.) | **Different concerns** — no functional overlap |
| Data model | `DatasetVersion` with `dataset_id`, `source_version`, `schema_version`, `etl_version`, `content_hash`, `version_hash` | `LifecycleStateMachine` with transition tables for ADR, OBPI, PRD, etc. | No overlap — airline dataset fields vs. governance state transitions |
| Domain coupling | `dataset_id` = BTS/FAA dataset identifiers, `source_version` = archive releases | Content-type agnostic governance transitions | airlineops is airline-domain-specific |
| Version semantics | Composite identity from schema_version + etl_version + content_hash → version_hash | No versioning — tracks state transitions, not version identity | Different paradigm entirely |
| Content hashing | `compute_content_hash()` — SHA-256 of raw bytes (~3 lines) | No hashing in module or anywhere in `src/gzkit/` | Generic but trivial |
| Composite hashing | `compute_version_hash()` — JSON `sort_keys` + SHA-256 (~10 lines) | N/A | Generic technique but trivial |
| Immutable model | Frozen Pydantic with custom `__eq__`/`__hash__` based on `version_hash` (~8 lines) | N/A | Generic pattern, trivial to implement when needed |
| Validation | Semver format validator (`X.Y.Z`), content hash format validator (`sha256:64_hex_chars`) (~12 lines) | N/A | Airline-specific field validation |
| Factory | `create_dataset_version()` — auto-computes version_hash from airline dataset fields | N/A | Airline-specific factory |
| Serialization | `version_to_dict()` / `version_from_dict()` — thin Pydantic wrappers | N/A | gzkit already uses `.model_dump()` by convention |
| Cross-platform | UTF-8 encoding, deterministic `ensure_ascii=True` | N/A | Standard patterns, nothing to absorb |
| Error handling | `ValueError` for invalid semver/hash formats | `InvalidTransitionError`, `KeyError` for unknown content types | Different error domains |

### Subtraction Test

Removing gzkit from airlineops's `dataset_version.py` leaves: airline dataset identity (`dataset_id` for BTS/FAA datasets), archive version tracking (`source_version` for BTS/FAA releases), ETL pipeline versioning (`schema_version` + `etl_version`), composite version hashing from these airline-specific components, and format validation for airline data fields. This is pure airline domain — it fails the subtraction test entirely. The only generic constructs (SHA-256 content hashing, deterministic JSON serialization, frozen Pydantic model) are too small (~33 lines) and too trivial to justify a standalone module. The premise that `lifecycle.py` provides partial coverage is incorrect — the two modules address entirely different concerns.

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

- [x] REQ-0.25.0-05-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-05-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Twelve-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-05-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-05-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-05-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/dataset_version.py
# Expected: airlineops source under review exists

test -f src/gzkit/lifecycle.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-05-dataset-version-pattern.md
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

Before this OBPI, there was no documented evaluation of whether airlineops's `core/dataset_version.py` contained reusable patterns for gzkit. The brief assumed `lifecycle.py` provided "partial coverage" — but after reading both implementations completely, they address entirely different concerns: `dataset_version.py` defines content-addressable version identity for airline data pipelines (BTS/FAA datasets, ETL versioning, composite hashing), while `lifecycle.py` implements governance artifact state transitions (Draft → Proposed → Accepted). There is zero functional overlap. The `DatasetVersion` model's fields (`dataset_id`, `source_version`, `schema_version`, `etl_version`) are all airline data pipeline concepts. The generic primitives — SHA-256 content hashing (~3 lines), deterministic JSON serialization (~10 lines), frozen Pydantic with hash-based equality (~8 lines), and format validators (~12 lines) — total ~33 lines of trivial utility code. gzkit has no `hashlib` usage anywhere in `src/gzkit/` and no content-addressable versioning use case. The subtraction test is decisive: removing gzkit from this module leaves pure airline domain code.

### Key Proof


- Decision: Exclude
- Comparison: twelve-dimension analysis in Comparison Analysis section
- airlineops dataset_version.py: 246 lines, content-addressable dataset version identity for airline data pipelines
- Model fields: `dataset_id` (BTS/FAA datasets), `source_version` (archive releases), `schema_version`/`etl_version` (ETL pipeline) — all airline-specific
- gzkit lifecycle.py: 128 lines, governance artifact state machine — zero functional overlap
- Subtraction test: entire module is airline domain — fails completely
- Generic primitives (SHA-256 hashing + JSON serialization + frozen Pydantic): ~33 lines, too trivial for a standalone module

### Implementation Summary


- Decision: Exclude — airlineops `core/dataset_version.py` (246 lines) is airline-domain-specific
- Module: content-addressable dataset version identity with airline ETL pipeline versioning
- Subtraction test: removing gzkit leaves pure airline domain code (BTS/FAA dataset identity, ETL versioning, archive tracking)
- Generic primitives: SHA-256 hashing + deterministic JSON + frozen Pydantic (~33 lines) — too trivial for standalone module
- Brief premise corrected: `lifecycle.py` has zero overlap with dataset versioning (different concerns entirely)
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

airlineops's `core/dataset_version.py` (246 lines) defines content-addressable dataset version identity for airline data pipelines using `DatasetVersion` with airline-specific fields (`dataset_id` for BTS/FAA datasets, `source_version` for archive releases, `schema_version` and `etl_version` for ETL pipeline components, `content_hash` for processed output, `version_hash` as composite identity). The factory function `create_dataset_version()` composes these airline-specific components into a deterministic identity hash. The serialization helpers are thin Pydantic wrappers that gzkit already uses by convention. Every significant construct beyond ~33 lines of trivial generic primitives (SHA-256 content hashing, deterministic JSON serialization, frozen Pydantic with hash-based equality, semver/hash format validators) is tied to airline data pipeline semantics. The brief's premise that `lifecycle.py` provides "partial coverage" is incorrect — `lifecycle.py` implements governance artifact state transitions, a completely different concern with zero functional overlap. gzkit has no `hashlib` usage, no content-addressable versioning use case, and no dataset identity requirement. The subtraction test is unambiguous: this module is pure airline domain code. **Decision: Exclude.**
