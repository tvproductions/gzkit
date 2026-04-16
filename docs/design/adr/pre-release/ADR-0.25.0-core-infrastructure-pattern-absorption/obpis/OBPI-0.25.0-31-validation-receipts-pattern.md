---
id: OBPI-0.25.0-31-validation-receipts-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 31
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-31: Validation Receipts Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-31 — "Evaluate and absorb opsdev/lib/validation_receipt.py (274 lines) — validation anchoring schema"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/validation_receipt.py` (274 lines) against
gzkit's validation receipt surface and determine: Absorb, Confirm, or Exclude.
The airlineops module covers validation anchoring schema. gzkit's equivalent
surface spans `events.py` (470 lines), `ledger_semantics.py` (547 lines), and
`validate_pkg/ledger_check.py` (379 lines) — approximately 1400+ lines across
3 modules providing receipt event models, anchor derivation, and receipt
validation.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/validation_receipt.py` (274 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/events.py`, `src/gzkit/ledger_semantics.py`, `src/gzkit/validate_pkg/ledger_check.py` (~1400+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 5x larger surface suggests more mature receipt handling — comparison will verify

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's receipt architecture around airlineops's validation anchoring model

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
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-31-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [x] REQ-0.25.0-31-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [x] REQ-0.25.0-31-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Confirm)
- [x] REQ-0.25.0-31-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [x] REQ-0.25.0-31-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/validation_receipt.py
# Expected: airlineops source under review exists

test -f src/gzkit/events.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-31-validation-receipts-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Comparison Evidence

Both surfaces were read in full before authoring this decision. The table
records concrete capability differences anchored to file:line citations.
gzkit's receipt surface spans multiple modules (~1396 lines total) versus
airlineops's single 274-line module — the comparison treats the gzkit surface
as the architectural unit of comparison.

| Dimension | airlineops `opsdev/lib/validation_receipt.py` (274 L) | gzkit equivalent surface (~1396 L distributed) |
| --- | --- | --- |
| Anchor schema typing | `ValidationAnchor` Pydantic BaseModel with regex SHA validation `^[0-9a-f]{7,40}$`, `tag`, `semver` — `frozen=True, extra="forbid"` (`validation_receipt.py:42-63`) | `anchor: dict[str, str] \| None` on `AuditReceiptEmittedEvent` and `ObpiReceiptEmittedEvent` (`events.py:362, 373`) |
| Anchor capture robustness | `get_current_anchor()` raises `RuntimeError` when git is unavailable or HEAD cannot be resolved (`validation_receipt.py:175-211`) | `capture_validation_anchor_with_warnings()` returns degraded fallback `{"commit": "0000000", "semver": "0.0.0"}` plus warnings list (`utils.py:64-105`) |
| Receipt event variety | 3 fixed Literals: `validated`, `completed`, `compliance_check` (`validation_receipt.py:84`) | 17+ lifecycle event types as a Pydantic discriminated union (`events.py:_EventBase` and subclasses, including `ProjectInitEvent`, `AdrCreatedEvent`, `ObpiCreatedEvent`, `AttestedEvent`, `GateCheckedEvent`, `CloseoutInitiatedEvent`, `AuditReceiptEmittedEvent`, `ObpiReceiptEmittedEvent`, `ArtifactRenamedEvent`, etc.) |
| Evidence model | `evidence: dict[str, Any]` — untyped (`validation_receipt.py:86`) | `ObpiReceiptEvidence` with nested `ScopeAudit`, `GitSyncState`, `ReqProofInput`, `req_proof_inputs`, `attestation_requirement`, `parent_lane`, `attestation_date`, `recorder_source`, `recorder_warnings` — strict Pydantic with field validators (`events.py:132-205`) |
| Attestor enforcement | Field validator forces `human:<name>` prefix at model layer (`validation_receipt.py:89-105`) | Enforced in `obpi_complete.py` `_enforce_human_attestation_required()` against parent ADR lane (`obpi_complete.py:195-247`); ledger-side attestation gating via `requires_human` flag |
| ADR ID validation | `validate_adr_id` field validator using shared `ADR_ID_PATTERN` (`validation_receipt.py:107-113`) | Pydantic `Field(pattern=...)` enforced in `core/models.py:37,140` for ADR/OBPI ID shape |
| Storage architecture | Per-ADR ledger at `{adr-folder}/logs/adr-validation.jsonl` — one file per ADR (`validation_receipt.py:36, 245-249`) | Central `.gzkit/ledger.jsonl` — single canonical event log with discriminated union over `event` field |
| Drift consumption | Companion module `opsdev/lib/drift_detection.py` consumes anchors from per-ADR ledgers | Already absorbed as `src/gzkit/temporal_drift.py` via OBPI-0.25.0-26; consumes anchors from the central gzkit ledger and shares the `git_cmd` HEAD cache |
| CLI integration | None — module is library-only | `gz obpi complete`, `gz adr emit-receipt`, `gz obpi reconcile`, `gz adr status` — first-class CLI surface that builds + emits + validates receipts |
| Atomic transaction | `write_receipt()` does a plain JSONL append with no rollback semantics (`validation_receipt.py:118-131`) | `_execute_transaction()` in `obpi_complete.py:225-237` performs an atomic three-step write (audit ledger entry + brief content + main ledger receipt event) with rollback on `OSError` |
| Reader surface | `read_receipts()` reads JSONL with optional ADR filter and warns on malformed lines (`validation_receipt.py:134-172`) | Full `Ledger` reader/append API in `gzkit.ledger` plus dispatched semantic validation in `ledger_semantics.py` and `validate_pkg/ledger_check.py` |
| Test surface | Unknown locally; airlineops module is a library outside gzkit's test footprint | gzkit receipt surface is exercised by the `events.py`, `obpi_complete.py`, `temporal_drift.py`, and `ledger_check.py` test modules across the unit + behave suites |

## Decision: Confirm

**Decision:** Confirm — gzkit's receipt surface is architecturally a strict
superset of `airlineops/src/opsdev/lib/validation_receipt.py`. No absorption
is warranted.

**Rationale.**

1. **Strict superset of capability.** Every behavior the airlineops module
   provides — anchor capture, receipt emission, ADR-ID validation, attestor
   enforcement, JSONL persistence, malformed-line tolerance, drift
   consumption — is already present in gzkit, distributed across `events.py`
   (470 L), `ledger_semantics.py` (547 L), `validate_pkg/ledger_check.py`
   (379 L), `utils.capture_validation_anchor()` (`utils.py:64-105`),
   `temporal_drift.py` (already absorbed via OBPI-0.25.0-26), and the
   atomic transaction in `commands/obpi_complete.py:225-237`. gzkit's
   surface is approximately 5x larger because it covers 17+ lifecycle
   events instead of 3, with strict Pydantic evidence models
   (`ObpiReceiptEvidence`, `ScopeAudit`, `GitSyncState`, `ReqProofInput`)
   in place of airlineops's `dict[str, Any]`.
2. **The single narrow win is structurally entangled and not worth a
   migration.** airlineops's only edge over gzkit is the typed
   `ValidationAnchor` Pydantic model (regex-validated SHA, frozen,
   extra=forbid) versus gzkit's `anchor: dict[str, str] | None` on the
   event models (`events.py:362, 373`). Hardening the gzkit anchor would
   require migrating every existing event in the gzkit ledger schema (the
   `anchor` field is shared across `AuditReceiptEmittedEvent` and
   `ObpiReceiptEmittedEvent`) plus updating the receipt writers, the
   `temporal_drift` consumer, and the validation surface in
   `ledger_check.py`. That is a self-contained schema-hardening OBPI in its
   own right, not an absorption — and it does not require copying any
   airlineops code to execute. If gzkit decides to type the anchor field
   later, it can do so directly.
3. **Architectural mismatch — central vs per-ADR ledger.** airlineops's
   storage model is one validation ledger per ADR folder
   (`{adr-folder}/logs/adr-validation.jsonl`, `validation_receipt.py:36`).
   gzkit's storage model is a single canonical `.gzkit/ledger.jsonl` whose
   discriminated union covers every lifecycle event (project init, ADR
   creation, OBPI creation, attestation, gate check, closeout initiation,
   audit/OBPI receipt emission, artifact rename, etc.). Absorbing
   airlineops's per-ADR storage would create a parallel storage system
   that contradicts gzkit's central-ledger doctrine, not strengthen it.
   This is the same tooling-vs-consumer-layer distinction that drove the
   `Exclude` outcomes for OBPI-0.25.0-29 (`ledger_schema`) and
   OBPI-0.25.0-30 (`references`).
4. **Atomic transaction semantics already exist in gzkit.** airlineops's
   `write_receipt()` is a plain JSONL append with no rollback
   (`validation_receipt.py:118-131`). gzkit's `_execute_transaction()` in
   `obpi_complete.py:225-237` performs an atomic three-step write (audit
   ledger entry + brief content + main ledger receipt event) with rollback
   on `OSError`. Any absorption would either downgrade gzkit's atomicity
   or duplicate the transaction surface — both regressions.
5. **CLI integration only exists in gzkit.** airlineops's
   `validation_receipt.py` is a library module with no CLI surface.
   gzkit's receipt surface is reached operationally through `gz obpi
   complete`, `gz adr emit-receipt`, `gz obpi reconcile`, and `gz adr
   status` — first-class operator commands that build, emit, validate, and
   reconcile receipts. Absorbing the airlineops module would not add a
   single operator-visible capability gzkit lacks today.

**Consequence.** No source or test edits in this brief. The Confirm outcome
records that gzkit's receipt surface is the canonical implementation of the
validation anchoring schema pattern. The narrow opportunity to type the
`anchor` field on `events.py:362, 373` is noted as a possible future
schema-hardening OBPI, scoped independently of this absorption decision.
The ADR-0.25.0 decision table will pick up the `Confirm` outcome for
OBPI-0.25.0-31 via `gz obpi reconcile` and `gz adr status` in Stage 5.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.25.0 checklist item #31 captured verbatim in brief l.15.
- [x] **Gate 2 (TDD):** N/A — Confirm outcome introduces no code or tests. `uv run gz test` remains green because no source changed; evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above with concrete capability, robustness, evidence-model, storage-architecture, transaction-semantics, and CLI-integration differences between airlineops and gzkit.
- [x] **Gate 4 (BDD):** N/A — the Confirm outcome introduces no operator-visible behavior change. `features/core_infrastructure.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger event type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

## Evidence

### Gate 1 (ADR)

- Intent captured verbatim from ADR-0.25.0 checklist item #31 at brief l.15
- Scope aligned with ADR Heavy lane and the Absorb / Confirm / Exclude contract

### Gate 2 (TDD)

- Existing gzkit test suite remains green — no new tests needed for a Confirm decision
- Verification: `uv run gz test` → comparison or absorbed implementation remains green (Stage 3 evidence below)

### Code Quality

- No code changes — Confirm decision is documentation-only
- `uv run gz lint` → Stage 3 evidence below
- `uv run gz typecheck` → Stage 3 evidence below
- `uv run gz validate --documents` → Stage 3 evidence below
- `uv run mkdocs build --strict` → Stage 3 evidence below
- `uv run gz covers OBPI-0.25.0-31-validation-receipts-pattern --json` → Stage 3 evidence below

### Value Narrative

Before this OBPI, the comparison between `airlineops/src/opsdev/lib/validation_receipt.py` (274 L validation anchoring schema) and gzkit's distributed receipt surface (~1396 L across `events.py`, `ledger_semantics.py`, `validate_pkg/ledger_check.py`, `utils.capture_validation_anchor`, `temporal_drift.py`, `commands/obpi_complete.py`) was unrecorded. After this OBPI, a five-point rationale is on the record explaining why gzkit's receipt surface is a strict architectural superset: 17+ lifecycle event types vs 3 fixed Literals; strict Pydantic evidence models (`ObpiReceiptEvidence` + `ScopeAudit` + `GitSyncState` + `ReqProofInput`) vs `dict[str, Any]`; central `.gzkit/ledger.jsonl` vs per-ADR `{adr}/logs/adr-validation.jsonl`; atomic three-step transaction with rollback vs plain JSONL append; first-class CLI integration (`gz obpi complete`, `gz adr emit-receipt`, `gz obpi reconcile`, `gz adr status`) vs library-only. The single narrow win for airlineops — typed `ValidationAnchor` instead of `dict[str, str]` on `events.py:362, 373` — is noted as a possible future schema-hardening OBPI scoped independently of absorption, because hardening the field is a direct edit to gzkit and does not require importing any airlineops code. This follows the precedent from OBPI-0.25.0-29 (`ledger_schema` Exclude) and OBPI-0.25.0-30 (`references` Exclude) where the same tooling-vs-consumer-layer distinction governed the outcome.

### Key Proof


- Decision: Confirm recorded in this brief
- Comparison: twelve-dimension table cites validation_receipt.py:42-211, events.py:362,373, utils.py:64-105, obpi_complete.py:225-237, temporal_drift.py
- airlineops validation_receipt.py: 274L library-only validation anchoring schema, 3 fixed event Literals, per-ADR JSONL storage, plain append (no rollback)
- gzkit equivalent: ~1396L across events.py (470L, 17+ event types) + ledger_semantics.py (547L) + validate_pkg/ledger_check.py (379L) + utils.capture_validation_anchor + temporal_drift.py + obpi_complete.py:225-237 atomic transaction
- Precedent: OBPI-0.25.0-29 and OBPI-0.25.0-30 tooling-vs-consumer-layer
- Follow-up: GHI #143 (anchor typing refactor)
- Gates green: lint, typecheck, test (17 features/110 scenarios/584 steps/10.907s), validate --documents (1 scope), mkdocs --strict (1.98s), covers (total_reqs=0)

### Implementation Summary


- Decision: Confirm
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Dependencies added: none
- Follow-up: GHI #143 tracks anchor field typing refactor as defect (refactor of existing capability, not new feature)

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed. — Confirm decision: gzkit receipt surface (events.py 470L + ledger_semantics.py 547L + validate_pkg/ledger_check.py 379L + utils.capture_validation_anchor + temporal_drift.py + commands/obpi_complete.py atomic transaction, ~1396L distributed) is architecturally a strict superset of airlineops/opsdev/lib/validation_receipt.py (274L). 12-dimension comparison anchored in file:line citations: 17+ event types vs 3 fixed Literals; ObpiReceiptEvidence with nested ScopeAudit/GitSyncState/ReqProofInput vs dict[str,Any]; central .gzkit/ledger.jsonl vs per-ADR storage; atomic 3-step transaction with OSError rollback (obpi_complete.py:225-237) vs plain JSONL append; first-class CLI integration vs library-only. Single narrow win for airlineops — typed ValidationAnchor on events.py:362,373 — is a refactor of existing gzkit capability not a new feature, tracked as defect via GHI #143 for independent remediation. No source/test edits. Brief-only OBPI; gates green: lint/typecheck/test (17 features, 110 scenarios, 584 steps, 10.907s)/validate-documents/mkdocs-strict/covers (total_reqs=0). Mirrors OBPI-0.25.0-29 and OBPI-0.25.0-30 tooling-vs-consumer-layer precedent.
- Date: 2026-04-13

## Closing Argument

`airlineops/src/opsdev/lib/validation_receipt.py` is a 274-line library
module that defines a typed `ValidationAnchor`, a `ValidationReceipt`
extending a shared `LedgerEntryBase`, JSONL persistence, and a per-ADR
storage convention (`{adr-folder}/logs/adr-validation.jsonl`). gzkit
already implements every one of those capabilities — and substantially
more — across an ~1396-line distributed surface: `events.py` defines a
17+ entry discriminated union of lifecycle events whose
`ObpiReceiptEmittedEvent` and `AuditReceiptEmittedEvent` carry richly
typed `ObpiReceiptEvidence` payloads with nested `ScopeAudit`,
`GitSyncState`, and `ReqProofInput` models; `commands/obpi_complete.py`
performs an atomic three-step transaction (audit ledger entry + brief
content + main ledger receipt event) with `OSError` rollback;
`utils.capture_validation_anchor()` builds anchor data with graceful
degradation rather than raising; `temporal_drift.py` (already absorbed
via OBPI-0.25.0-26) consumes anchors from the central
`.gzkit/ledger.jsonl` to classify drift; and the surface is reached
operationally through `gz obpi complete`, `gz adr emit-receipt`, `gz obpi
reconcile`, and `gz adr status`. The single narrow place where airlineops
has more typing rigor — `ValidationAnchor` as a frozen Pydantic model
instead of gzkit's `anchor: dict[str, str] | None` — is structurally
entangled with every existing receipt event in the gzkit ledger, and
hardening it is a direct schema edit to gzkit that does not require
importing any airlineops code. The doctrinally-coherent outcome is
Confirm: gzkit's receipt surface is the canonical implementation of the
validation anchoring schema pattern, and absorbing 274 lines of a
parallel per-ADR storage system would contradict gzkit's central-ledger
doctrine instead of strengthening it. The subtraction test
(*if it is not airline-specific, it belongs in gzkit*) does not require a
copy when gzkit already owns the capability at greater fidelity. The
opportunity to type the anchor field on `events.py:362, 373` is a
refactor of an existing capability rather than a new feature, and is
tracked as a defect on the GHI track (gh#143) for future remediation —
scoped independently of this absorption decision.
