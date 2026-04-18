---
id: OBPI-0.25.0-03-signature-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 3
status: in_progress
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-03: Signature Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-03 — "Evaluate and absorb core/signature.py (365 lines) — cryptographic content hashing and artifact fingerprinting"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/signature.py` (365 lines) and
determine: Absorb (airlineops is better) or Exclude (domain-specific). The
airlineops module provides cryptographic content hashing, artifact
fingerprinting, and deterministic JSON serialization. gzkit currently has no
equivalent module, making this a strong absorption candidate unless the logic
is airline-specific.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/signature.py` (365 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Implementing a full PKI or key management system

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Exclude: document why the module is domain-specific

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/signature.py` (365 lines) computes "dataset signatures" for airline-specific dataset families (BTS DB1B, BTS DB28DM, BTS ASQP, BTS DB10, BTS DB20, FAA, exogenous). The `DatasetFamily` type, all 6 character extractors, catalog loading from `data/datasets/`, and dataset-family detection are entirely tied to airline dataset semantics. gzkit has no equivalent module because it has no dataset signature use case — gzkit is a governance toolkit, not a dataset processing pipeline. The only generic primitives (`_compute_fingerprint()` — JSON sort_keys + SHA256, `_timestamp_utc()` — UTC ISO format) are trivial utility functions (~13 lines combined) that don't warrant a standalone module. gzkit can add a `hashlib.sha256` call inline wherever needed in the future.

## COMPARISON ANALYSIS

| Dimension | airlineops (365 lines, 1 file) | gzkit (no equivalent) | Assessment |
|-----------|-------------------------------|----------------------|------------|
| Purpose | Dataset signature computation for operational attestation | No dataset signature use case | Domain-specific |
| Data model | `SignaturePayload` with `dataset_id`, `dataset_family`, `row_count`, `period_count`, `period_range`, `character` | N/A | All fields are airline dataset concepts |
| Type system | `DatasetFamily` = `Literal["bts_db1b", "bts_db28dm", "bts_asqp", "bts_db10", "bts_db20", "faa", "exog"]` | N/A | Airline-specific literal type |
| Character extractors | 6 extractors: DB1B (ticket counts, quarters), DB28 (passenger totals, months), ASQP (flight counts), FAA (AIRAC cycles), exogenous, generic | N/A | All airline-specific metrics |
| Catalog loading | `_load_catalog()`, `_find_dataset_root()` from `data/datasets/` | N/A | Airline dataset directory structure |
| Family detection | `_detect_dataset_family()` — prefix-based matching on airline dataset IDs | N/A | Airline-specific prefixes |
| Fingerprinting | `_compute_fingerprint()` — JSON `sort_keys` + SHA256 (~10 lines) | No hashlib usage in `src/gzkit/` | Generic but trivial — not worth a module |
| Timestamp | `_timestamp_utc()` — UTC ISO format (~3 lines) | N/A | Generic but trivial |
| Error handling | `SignatureError(RuntimeError)` | N/A | Single exception, airline-specific context |
| Cross-platform | `pathlib.Path`, UTF-8 encoding | N/A | Standard patterns, nothing to absorb |

### Subtraction Test

Removing gzkit from airlineops leaves: dataset signature computation for airline dataset families. This is pure airline domain — it fails the subtraction test entirely. No construct in this module belongs in a governance toolkit.

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

- [x] REQ-0.25.0-03-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-03-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Ten-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-03-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-03-04: [doc] Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-03-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/signature.py
# Expected: airlineops source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-03-signature-pattern.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-03-signature-pattern.md
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

Before this OBPI, there was no documented evaluation of whether airlineops's `core/signature.py` contained reusable patterns for gzkit. After reading the full 365-line module, every significant construct is airline-domain-specific: `DatasetFamily` type literals, 6 character extractors for airline dataset families, catalog loading from airline dataset directories, and prefix-based dataset family detection. The only generic primitives (JSON-to-SHA256 fingerprinting and UTC timestamp formatting) are trivial utilities (~13 lines) that don't justify a standalone module. The subtraction test is decisive: removing gzkit from airlineops leaves pure airline domain code. No absorption warranted.

### Key Proof


- Decision: Exclude
- Comparison: ten-dimension analysis in Comparison Analysis section
- airlineops signature.py: 365 lines, single module, airline-dataset-specific
- gzkit: no equivalent module, no hashlib usage — no use case for dataset signatures
- Subtraction test: entire module is airline domain — fails completely
- Generic primitives (JSON+SHA256, UTC timestamp): too trivial for a standalone module

### Implementation Summary


- Decision: Exclude
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Date: 2026-04-09

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: agree, not everything from airlineops will transfer
- Date: 2026-04-09

## Closing Argument

airlineops's `core/signature.py` (365 lines) computes dataset signatures for airline-specific dataset families using `DatasetFamily` literal types (bts_db1b, bts_db28dm, bts_asqp, bts_db10, bts_db20, faa, exog), 6 family-specific character extractors, catalog loading from `data/datasets/`, and prefix-based family detection. Every construct beyond two trivial utility functions (`_compute_fingerprint` — JSON sort_keys + SHA256, `_timestamp_utc` — UTC ISO format) is tied to airline dataset semantics. gzkit has no dataset signature use case and no existing hashlib usage. The subtraction test is unambiguous: this module is pure airline domain code. **Decision: Exclude.**
