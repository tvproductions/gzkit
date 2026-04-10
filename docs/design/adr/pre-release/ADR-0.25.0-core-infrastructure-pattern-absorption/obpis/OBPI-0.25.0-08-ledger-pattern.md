---
id: OBPI-0.25.0-08-ledger-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 8
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-08: Ledger Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-08 — "Evaluate and absorb core/ledger.py (91 lines) — ledger entry management"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/ledger.py` (91 lines) against gzkit's `ledger.py` (1350 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides ledger entry management and JSONL persistence. gzkit's equivalent is 15x larger and likely far more sophisticated, but the comparison must verify whether airlineops has any patterns or edge-case handling that gzkit lacks.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/ledger.py` (91 lines)
- **gzkit equivalent:** `src/gzkit/ledger.py` (1350 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 15x larger implementation strongly suggests Confirm is the likely outcome

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Modifying gzkit's ledger unless airlineops has genuinely superior patterns

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/ledger.py` (91 lines) is a thin facade that re-exports four functions from `airlineops.warehouse.ingest.ledger`: `resolve_period_path`, `append_event`, `append_load_event`, and `append_error_event`. Every function deals exclusively with airline warehouse ingest concepts — datasets, periods, base months, load results, ETL error events. The facade itself contains no logic; it delegates entirely to the ingest subsystem. The `append_load_event` signature exposes airline-specific parameters: `dataset`, `period`, `base_month`, `status`, `load_result`, `registry_meta`, `calendar_state`, `flags`, `contract_id`, `policy_id`. These are airline data pipeline concepts with no governance equivalent.

gzkit's `ledger.py` (598 lines) plus three sub-modules (`ledger_events.py`, `ledger_proof.py`, `ledger_semantics.py`) implements a fundamentally different system: an append-only JSONL governance event ledger with `LedgerEvent` Pydantic models, schema validation, artifact graph construction, rename chain resolution, attestation tracking, closeout lifecycle, and OBPI receipt management. The two modules share only the name "ledger" — their domains, data models, and operational semantics are entirely disjoint.

The subtraction test is decisive: removing gzkit from airlineops's `core/ledger.py` leaves a pure airline warehouse ingest facade. There are no generic patterns, no reusable abstractions, and no edge-case handling that gzkit lacks. The append-only JSONL pattern that both share is already far more sophisticated in gzkit (schema-validated events, caching, querying, graph building) than the raw `json.dump` + `f.write("\n")` approach in the ingest subsystem.

## COMPARISON ANALYSIS

| Dimension | airlineops `core/ledger.py` (91 lines) | gzkit `ledger.py` (598 lines + 3 sub-modules) | Assessment |
|-----------|----------------------------------------|------------------------------------------------|------------|
| Purpose | Thin facade re-exporting airline warehouse ingest functions | Governance event ledger with lifecycle tracking | **Different domains** — no functional overlap |
| Architecture | Facade pattern — zero logic, pure re-exports from `warehouse.ingest.ledger` | Full implementation — Pydantic models, JSONL I/O, caching, graph builder | gzkit is self-contained; airlineops is a delegation layer |
| Data model | No model — passes through `Mapping[str, Any]` dicts | `LedgerEvent(BaseModel)` with schema validation, `model_validator`, `model_serializer` | gzkit has proper typed models |
| Domain coupling | Airline-specific: `dataset`, `period`, `base_month`, `load_result`, `registry_meta`, `calendar_state` | Governance-specific: `event`, `id`, `ts`, `parent`, artifact graph, attestation | Entirely disjoint domains |
| Append semantics | Raw event dict → JSONL (delegated to ingest module) | Schema-validated `LedgerEvent` → JSONL with cache invalidation | gzkit is more robust |
| Query capability | None — append-only, no read API in facade | `read_all()`, `query()`, `latest_event()`, `get_artifact_graph()`, `canonicalize_id()` | gzkit has full query engine |
| Rename/ID tracking | None | `_build_rename_map()`, `_canonicalize_with_map()` — follows rename chains | gzkit has rename resolution |
| Error handling | `append_error_event` catches `OSError, RuntimeError, ValueError, TypeError` → returns `None` | Schema validation via Pydantic; typed event processing | Different error strategies for different domains |
| Cross-platform | `Path` for `ledger_root`/`ledger_path` parameters | `Path` throughout, `encoding="utf-8"` on reads | Both adequate for their domain |
| Serialization | Passthrough — no serialization logic in facade | `model_dump()` with custom `_serialize()` for schema→schema_ mapping and extra flattening | gzkit has sophisticated serialization |
| Caching | None | `_cached_events`, `_cached_graph` with `_invalidate_cache()` on mutations | gzkit has full caching layer |
| Test coverage | Not evaluated (facade has no testable logic) | Covered by gzkit test suite | N/A comparison |

### Subtraction Test

Removing gzkit from airlineops's `core/ledger.py` leaves: a facade re-exporting four airline warehouse ingest functions (`resolve_period_path` for period-based file paths, `append_event` for generic event dicts, `append_load_event` for airline dataset load tracking with BTS/FAA-specific parameters, `append_error_event` for ETL pipeline error recording). Every function signature, parameter name, and operational concept is tied to airline data warehouse operations. There are no generic patterns worth extracting — the facade contains zero logic, and the underlying ingest functions are airline-domain-specific. The JSONL append pattern is already implemented in gzkit with far greater sophistication (schema validation, caching, querying, graph building).

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

- [x] REQ-0.25.0-08-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-08-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Twelve-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-08-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-08-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-08-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/ledger.py
# Expected: airlineops source under review exists

test -f src/gzkit/ledger.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-08-ledger-pattern.md
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

Before this OBPI, there was no documented evaluation of whether airlineops's `core/ledger.py` contained reusable patterns for gzkit. The brief assumed that airlineops's 91-line module might have patterns or edge-case handling that gzkit's 1350-line (now 598-line) implementation lacked. After reading both implementations completely, they address entirely different concerns: airlineops's `core/ledger.py` is a thin facade that re-exports four functions from the airline warehouse ingest subsystem — `resolve_period_path`, `append_event`, `append_load_event`, and `append_error_event` — all dealing with airline-specific concepts (datasets, periods, base months, load results, ETL errors). The facade contains zero logic; it is pure delegation. gzkit's `ledger.py` implements a governance event ledger with `LedgerEvent` Pydantic models, schema validation, append-only JSONL with caching, artifact graph construction, rename chain resolution, attestation tracking, and lifecycle semantics. The two modules share only the name "ledger." The subtraction test is unambiguous: removing gzkit from the airlineops module leaves a pure airline warehouse ingest facade with no generic patterns worth extracting.

### Key Proof


- Decision: Exclude
- Comparison: twelve-dimension analysis in Comparison Analysis section
- airlineops core/ledger.py: 91 lines, thin facade re-exporting 4 functions from `warehouse.ingest.ledger`
- Functions: `resolve_period_path` (period paths), `append_event` (generic events), `append_load_event` (airline load tracking), `append_error_event` (ETL errors) — all airline-specific
- gzkit ledger.py: 598 lines + 3 sub-modules, governance event ledger with Pydantic models, graph builder, rename chains, attestation — zero functional overlap
- Subtraction test: entire module is airline domain — fails completely
- No generic patterns: facade contains zero logic; underlying ingest functions are domain-specific

### Implementation Summary


- Decision: Exclude — airlineops `core/ledger.py` (91 lines) is airline-domain-specific
- Module: thin facade re-exporting airline warehouse ingest functions (datasets, periods, load events, ETL errors)
- Subtraction test: removing gzkit leaves pure airline warehouse ingest facade with no reusable patterns
- gzkit's ledger (598 lines + 3 sub-modules) is a fundamentally different system — governance event ledger vs. warehouse ingest facade
- Brief premise evaluated: the two modules share only the name "ledger" — entirely disjoint domains
- Files created: none
- Files modified: this brief only (Exclude decision with twelve-dimension comparison analysis)
- Tests added: none (no code changes)
- Date: 2026-04-10

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-09

## Closing Argument

airlineops's `core/ledger.py` (91 lines) is a thin facade that re-exports four functions from `airlineops.warehouse.ingest.ledger`: `resolve_period_path`, `append_event`, `append_load_event`, and `append_error_event`. Every function deals exclusively with airline warehouse ingest concepts — datasets, periods, base months, load results, ETL error events. The facade contains zero logic; it delegates entirely to the ingest subsystem. gzkit's `ledger.py` (598 lines) plus three sub-modules (`ledger_events.py`, `ledger_proof.py`, `ledger_semantics.py`) implements a fundamentally different system: an append-only JSONL governance event ledger with `LedgerEvent` Pydantic models, schema validation, artifact graph construction, rename chain resolution, attestation tracking, closeout lifecycle, and OBPI receipt management. The two modules share only the name "ledger" — their domains, data models, and operational semantics are entirely disjoint. The subtraction test is unambiguous: removing gzkit from the airlineops module leaves a pure airline warehouse ingest facade with no generic patterns worth extracting. **Decision: Exclude.**
