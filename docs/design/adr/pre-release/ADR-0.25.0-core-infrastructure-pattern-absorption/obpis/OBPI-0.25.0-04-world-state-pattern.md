---
id: OBPI-0.25.0-04-world-state-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 4
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-04: World State Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-04 — "Evaluate and absorb core/world_state.py (275 lines) — immutable world-state snapshots"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/world_state.py` (275 lines) and
determine: Absorb (airlineops is better) or Exclude (domain-specific). The
airlineops module provides immutable world-state snapshots, content-addressable
identity, and semantic no-op detection. gzkit currently has no equivalent
module, making this a strong absorption candidate.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/world_state.py` (275 lines)
- **gzkit equivalent:** None

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- No existing gzkit equivalent means either Absorb or Exclude — there is no Confirm path
- World-state snapshots are a governance primitive, not an airline concept

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Building a full event-sourcing system on top of world state

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/world_state.py` (275 lines) defines world-state identity for AIRAC-orchestrated warehouse pipelines. The `WorldState` model's fields (`airac_cycle`, `contract_hash`, `manifest_hash`, `contract_id`, `manifest_root`) are airline-specific. `get_current_world_state()` depends on `airlineops.core.registrar` (get_active_contract, get_active_manifest_root) and `airlineops.warehouse.manifest` (compute_stable_fingerprint) — imports that are entirely airline-domain. `_compute_manifest_fingerprints()` reads `.manifest.json` files with airline dataset fields (dataset_id, contract_hash, periods, package_names, file_locations). The AIRAC cycle invariant ("only ONE AIRAC cycle is active at any time") is an FAA-specific constraint.

The generic primitives are: frozen Pydantic model with hash-based equality (~20 lines), deterministic JSON→SHA-256 hashing (~10 lines), semantic no-op detection via hash comparison (~3 lines), and UTC timestamp helper (~3 lines). Combined, these total ~36 lines of trivial utility code that do not warrant a standalone module. gzkit has no content-addressable snapshot use case today, and the architectural boundaries note that the state doctrine must be locked before building state-tracking infrastructure.

## COMPARISON ANALYSIS

| Dimension | airlineops (275 lines, 1 file) | gzkit (no equivalent) | Assessment |
|-----------|-------------------------------|----------------------|------------|
| Purpose | AIRAC-orchestrated warehouse world-state identity | No world-state use case | Domain-specific |
| Data model | `WorldState` with `airac_cycle`, `contract_hash`, `manifest_hash`, `contract_id`, `manifest_root` | N/A | All fields are airline contract/manifest concepts |
| Dependencies | `airlineops.core.registrar`, `airlineops.warehouse.manifest` | N/A | Imports are airline-domain-specific |
| Domain coupling | AIRAC cycle invariant, contract fingerprinting, manifest directory scanning | N/A | Deeply coupled to airline data pipeline |
| Manifest parsing | `_compute_manifest_fingerprints()` — reads `.manifest.json` with dataset_id, periods, package_names, file_locations | N/A | Airline dataset manifest structure |
| State query | `get_current_world_state()` — queries registrar for active contract/manifest | N/A | Airline registrar pattern |
| Content hashing | `compute_world_state_hash()` — JSON `sort_keys` + SHA-256 (~10 lines) | No `hashlib` usage in `src/gzkit/` | Generic but trivial |
| Immutable model | Frozen Pydantic with `__eq__`/`__hash__` based on content hash (~20 lines) | N/A | Generic pattern but trivial to implement when needed |
| No-op detection | `is_semantic_noop()` — single-line hash comparison | N/A | Generic but trivial (1 line) |
| Timestamp | `_utc_now_iso()` — UTC ISO format (~3 lines) | N/A | Generic but trivial |
| Cross-platform | `pathlib.Path`, UTF-8 encoding | N/A | Standard patterns, nothing to absorb |
| Error handling | Silent `OSError`/`JSONDecodeError` catch in manifest parsing | N/A | Airline-specific resilience pattern |

### Subtraction Test

Removing gzkit from airlineops's `world_state.py` leaves: AIRAC cycle identity, airline contract fingerprinting, airline manifest directory scanning, airline registrar queries, and semantic no-op detection for airline warehouse pipeline transitions. This is pure airline domain — it fails the subtraction test entirely. The only generic constructs (frozen Pydantic + JSON→SHA-256 + hash comparison) are too small and too trivial to justify a standalone module.

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

- [x] REQ-0.25.0-04-01: Given the completed comparison, then the brief records
  one final decision: `Absorb` or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-04-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Twelve-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-04-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-04-04: Given an `Exclude` outcome, then the brief explains why
  the pattern is domain-specific or otherwise not fit for gzkit. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-04-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/world_state.py
# Expected: airlineops source under review exists

rg -n 'Absorb|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-04-world-state-pattern.md
# Expected: completed brief records one final decision

rg -n 'src/gzkit/|tests/' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-04-world-state-pattern.md
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

Before this OBPI, there was no documented evaluation of whether airlineops's `core/world_state.py` contained reusable patterns for gzkit. After reading the full 275-line module, the implementation is deeply coupled to airline domain concepts: AIRAC cycle identity (FAA-specific), airline contract fingerprinting via `airlineops.core.registrar`, manifest directory scanning for `.manifest.json` files with airline dataset fields, and semantic no-op detection for warehouse pipeline transitions. The `WorldState` model's fields (`airac_cycle`, `contract_hash`, `manifest_hash`, `contract_id`, `manifest_root`) are all airline contract/manifest concepts. The generic primitives — frozen Pydantic with hash-based equality, deterministic JSON→SHA-256 hashing, and single-line hash comparison — total ~36 lines of trivial utility code. gzkit has no content-addressable snapshot use case and no `hashlib` usage anywhere in `src/gzkit/`. The subtraction test is decisive: removing gzkit from this module leaves pure airline domain code.

### Key Proof


- Decision: Exclude
- Comparison: twelve-dimension analysis in Comparison Analysis section
- airlineops world_state.py: 275 lines, AIRAC-orchestrated warehouse pipeline state
- Imports: `airlineops.core.registrar` (get_active_contract, get_active_manifest_root), `airlineops.warehouse.manifest` (compute_stable_fingerprint) — all airline-specific
- gzkit: no equivalent module, no hashlib usage, no content-addressable patterns
- Subtraction test: entire module is airline domain — fails completely
- Generic primitives (frozen Pydantic + JSON SHA-256 + hash comparison): ~36 lines, too trivial for a standalone module

### Implementation Summary


- Decision: Exclude — airlineops `core/world_state.py` (275 lines) is airline-domain-specific
- Module: AIRAC-orchestrated warehouse pipeline world-state identity with airline registrar dependencies
- Subtraction test: removing gzkit leaves pure airline domain code (AIRAC cycles, contract fingerprinting, manifest scanning)
- Generic primitives: frozen Pydantic + JSON→SHA-256 + hash comparison (~36 lines) — too trivial for standalone module
- Files created: none
- Files modified: this brief only (Exclude decision with twelve-dimension comparison analysis)
- Tests added: none (no code changes)
- Date: 2026-04-09

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: didn't hurt to try. attest completed
- Date: 2026-04-09

## Closing Argument

airlineops's `core/world_state.py` (275 lines) defines world-state identity for AIRAC-orchestrated warehouse pipelines using `WorldState` with airline-specific fields (`airac_cycle`, `contract_hash`, `manifest_hash`, `contract_id`, `manifest_root`), queries the airline registrar (`get_active_contract`, `get_active_manifest_root`), scans airline manifest directories for `.manifest.json` files with dataset fields (`dataset_id`, `contract_hash`, `periods`, `package_names`), and computes semantic no-op detection for warehouse pipeline transitions. Every significant construct beyond ~36 lines of trivial generic primitives (frozen Pydantic model with hash-based equality, deterministic JSON→SHA-256, single-line hash comparison) is tied to airline domain semantics. gzkit has no content-addressable snapshot use case, no `hashlib` usage, and its architectural boundaries indicate state doctrine must be locked before building state-tracking infrastructure. The subtraction test is unambiguous: this module is pure airline domain code. **Decision: Exclude.**
