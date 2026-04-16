---
id: OBPI-0.25.0-01-attestation-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 1
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-01: Attestation Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-01 — "Evaluate and absorb core/attestation.py (511 lines) — evidence attestation and proof recording"`

## OBJECTIVE

Compare `airlineops/src/airlineops/core/attestation.py` (511 lines) against gzkit's attestation surface and determine: Absorb (airlineops has reusable patterns gzkit lacks), Confirm (gzkit already covers this domain), or Exclude (domain-specific, does not belong in gzkit). The airlineops module covers AIRAC-cycle-based attestation and ceremony ledgers. gzkit's attestation surface is distributed across 10+ modules (~2000+ lines) covering ADR attestation, OBPI completion, structured evidence, and closeout ceremonies.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/attestation.py` (511 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/commands/attest.py`, `obpi_complete.py`, `closeout.py`, `ledger_semantics.py`, `ledger_proof.py`, `ledger_events.py`, and others (~2000+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Line count differences between a standalone module and a distributed surface are not meaningful without feature-level comparison

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Modifying the existing `gz attest` CLI command contract without Heavy lane approval

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## DECISION

**Decision: Confirm** — gzkit's attestation implementation is sufficient. No upstream absorption warranted.

**Rationale:** gzkit's attestation surface spans 10+ modules (~2000+ lines) with multi-level attestation (ADR + OBPI), structured REQ-proof evidence inputs, a composite state machine with 7 runtime states and drift detection, transactional OBPI completion with rollback, and an 11-step closeout ceremony pipeline. airlineops's `core/attestation.py` (511 lines) is a standalone module organized around AIRAC cycles (airline-domain-specific) with simpler hash-based evidence and summary queries. The only generic patterns in airlineops (JSONL append-only ledger, `CommandExecution` tracking, hash-based evidence) are already subsumed by gzkit's `Ledger` class, ARB receipts, and structured proof system respectively.

## COMPARISON ANALYSIS

| Dimension | airlineops (511 lines, 1 file) | gzkit (~2000+ lines, 10+ modules) | Winner |
|-----------|-------------------------------|----------------------------------|--------|
| Architecture | Standalone module, cycle-based JSONL files | Distributed multi-module with unified ledger and artifact graph | gzkit |
| Attestation model | 3 responses (approved/rejected/deferred) | Multi-level: ADR attestation (completed/partial/dropped) + OBPI attestation (human/self-close), fail-closed gate prerequisites, force bypass with 20-char reason validation | gzkit |
| Evidence model | SHA256 hashes (world_state, contract, transcript, output) | Structured REQ-proof inputs (kind/source/status), value narrative, key proof, scope audit with allowlist enforcement | gzkit |
| Ceremony | `CeremonyRecord` model with transcript hash and UUID | 11-step `CeremonyState` pipeline with pause/resume, attempt tracking, step history | gzkit |
| State derivation | `get_attestation_summary()`, `get_ceremony_summary()` returning latest record and counts | Composite state machine: 7 runtime states, 4 proof states, 3 attestation states, anchor-based drift detection | gzkit |
| Error handling | Single `AttestationError(RuntimeError)`, silently skips malformed JSONL records | `GzCliError`, `PolicyBreachError`, transactional rollback via `_execute_transaction`, placeholder detection, input validation | gzkit |
| Cross-platform | `pathlib.Path`, UTF-8 encoding, cycle-name sanitization | `pathlib.Path`, UTF-8 encoding, `PurePosixPath` for scope matching, forward-slash normalization | Tie |
| Test coverage | ~1,249 lines across 4 test files | ~2,276 lines across 4+ attestation-related test files | gzkit |
| Domain specificity | AIRAC cycle organization, world_state hash, contract hash — airline-specific | ADR/OBPI organization — governance-generic | N/A |

### Patterns Worth Noting (But Not Absorbing)

- airlineops has clean cycle-name sanitization (`safe_cycle = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(cycle))`). gzkit does not need this because it uses a unified ledger rather than per-cycle files.
- airlineops's `compute_transcript_hash()` is a clean SHA256 utility, but gzkit handles hashing at the anchor/evidence level rather than ceremony transcript level.
- airlineops's `CommandExecution` model (command, exit_code, output_hash) is generic but is already subsumed by gzkit's `gate_checked_event` and ARB receipt infrastructure.

## GATE 4 BDD: N/A Rationale

A Confirm decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Confirm decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [x] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-01-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Confirm** recorded in Decision section.
- [x] REQ-0.25.0-01-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Six-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-01-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Confirm decision).
- [x] REQ-0.25.0-01-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Rationale in Decision section.
- [x] REQ-0.25.0-01-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/attestation.py
# Expected: airlineops source under review exists

test -f src/gzkit/commands/attest.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-01-attestation-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Confirm)
- [x] **Gate 3 (Docs):** Decision rationale completed
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Confirm, no behavior change)
- [x] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for a Confirm decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Confirm decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented comparison of the two attestation implementations. After thorough comparison across six dimensions (architecture, attestation model, evidence model, ceremony, state derivation, error handling), gzkit's distributed attestation surface (~2000+ lines across 10+ modules) is more capable in every category. The airlineops module's remaining value is airline-domain-specific (AIRAC cycle organization, operational attestation responses) and correctly excluded from gzkit.

### Key Proof


- Decision: Confirm
- Comparison: six-dimension analysis in Comparison Analysis section
- airlineops attestation.py: 511 lines, standalone, AIRAC-cycle-specific
- gzkit attestation surface: ~2000+ lines, 10+ modules, governance-generic
- Generic patterns (JSONL ledger, CommandExecution, hash evidence) already subsumed
- Domain-specific patterns (AIRAC cycles, world_state, contract_hash) correctly excluded

### Implementation Summary


- Decision: Confirm
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Date: 2026-04-09

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: Confirmed: gzkit attestation surface is more capable across all dimensions. Comparison is honest and neutral — retains best from both codebases. No absorption warranted.
- Date: 2026-04-10

## Closing Argument

airlineops's `core/attestation.py` (511 lines) implements AIRAC-cycle-based attestation and ceremony ledgers using Pydantic models and JSONL append-only storage. gzkit's attestation surface (~2000+ lines across 10+ modules) provides multi-level attestation (ADR + OBPI), structured REQ-proof evidence, a composite state machine with drift detection, transactional OBPI completion with rollback, and an 11-step ceremony pipeline. Every generic pattern in airlineops is already subsumed by gzkit. The remaining airlineops-specific constructs (AIRAC cycle organization, operational attestation responses, world-state and contract hashing) are airline-domain-specific and correctly excluded from absorption. **Decision: Confirm.**
