---
id: OBPI-0.26.0-08-validation-receipt
parent: ADR-0.26.0-governance-library-module-absorption
item: 8
status: Completed
lane: heavy
date: 2026-03-21
decision: Confirm
---

# OBPI-0.26.0-08: Validation Receipt

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-08 — "Evaluate and absorb lib/validation_receipt.py (274 lines) — structured validation receipt generation"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/validation_receipt.py` (274 lines)
against gzkit's validation-receipt surface and determine: Absorb (opsdev is
better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The
opsdev module provides a typed `ValidationAnchor` plus `ValidationReceipt`
extending a shared `LedgerEntryBase`, JSONL persistence, and a per-ADR
storage convention. The comparison must determine whether gzkit's
distributed receipt surface produces evidence with the same — or greater —
structural rigor and auditability.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/validation_receipt.py` (274 lines)
- **gzkit equivalent:** Body-level observation in `## Comparison`: parent-ADR
  Tidy First Plan table names "Partial in `src/gzkit/validate.py`," but
  `validate.py` is now a 121-line re-export shim that delegates to
  `validate_pkg/` submodules. The actual gzkit receipt-validation surface is
  ~1830 L distributed across `src/gzkit/events.py` (556 L, including the
  typed `EventAnchor` Pydantic model at line 355), `src/gzkit/ledger_semantics.py`
  (547 L), `src/gzkit/validate_pkg/ledger_check.py` (379 L),
  `src/gzkit/temporal_drift.py` (348 L; absorbed via OBPI-0.25.0-26),
  `src/gzkit/utils.capture_validation_anchor_with_warnings` (`utils.py:64-105`),
  and `src/gzkit/commands/obpi_complete.py` atomic `_execute_transaction`
  (`obpi_complete.py:225-237`). This source artifact was already evaluated
  and decided **Confirm** under OBPI-0.25.0-31-validation-receipts-pattern
  (attested 2026-04-13). Parent-ADR header is intentionally not amended
  (mirror of OBPI-0.26.0-04 / -05 / -06 / -07 pattern).

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any decision binds future
governance-library absorption work. The brief frontmatter records a doctrine
choice (Confirm-by-reference to OBPI-0.25.0-31) that future agents will
treat as canonical, so Heavy scrutiny applies even though no code changes
under this brief.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Structured validation receipts are a governance primitive that aligns
  with gzkit's ARB (Agent Self-Reporting) middleware
- ~~gzkit's validate.py may perform validation but may lack receipt
  generation depth~~ — **brief-scaffold defect**: gzkit ships a much
  larger and more capable receipt surface than the brief Source Material
  acknowledges (~1830 L distributed across six modules). The canonical
  OBPI-0.25.0-31 evaluated this exact source artifact and decided
  **Confirm** with a five-point rationale anchored on capability superset,
  central-ledger doctrine, atomic transaction semantics, and CLI
  integration. The defect class is the fourth instance across ADR-0.26.0
  briefs (also present in OBPI-04 / -05 / -06 / -07 wording); tracked under
  GHI #376 as part of the duplicate-OBPI surface.
- Validation receipts are fundamental to governance auditing and integrate
  with the central `.gzkit/ledger.jsonl` discriminated event union
- The actual gzkit comparison surface is ~1830 L across six modules
  (`events.py` + `ledger_semantics.py` + `validate_pkg/ledger_check.py` +
  `temporal_drift.py` + `utils.capture_validation_anchor_with_warnings` +
  `commands/obpi_complete.py`), already evaluated and confirmed superior
  under OBPI-0.25.0-31 — recorded in `## Comparison` body section
  (parent-ADR-authored Source Material header not amended).

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing validation infrastructure — the goal is
  enriching receipt capabilities only if a real capability gap exists
- Re-running the comparison work already attested under
  OBPI-0.25.0-31-validation-receipts-pattern (2026-04-13) on identical
  source material — divergent rationale on identical material is itself a
  doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Confirm / Exclude (Confirm permitted by precedent despite stale brief Source Material wording — see above).
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Confirm: document why gzkit's existing surface is superior.
6. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/`
  for a Confirm-by-reference outcome (the existing surface was already
  evaluated as superior under OBPI-0.25.0-31; this brief introduces no new
  code or tests)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a
  governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — re-confirmed the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-04-adr-governance brief (Completed) — Confirm-by-reference structural precedent
- [x] Sibling OBPI-0.26.0-05-ledger-schema brief (Completed) — Exclude-by-reference NON-GOAL anchor for "no divergent rationale on identical source"
- [x] Sibling OBPI-0.26.0-06-drift-detection brief (Completed) — Absorb-by-reference scaffold-drift correction recipe
- [x] Sibling OBPI-0.26.0-07-adr-traceability brief (Completed 2026-05-01) — same-day Confirm-by-reference precedent for stale brief Source Material wording as scaffold-defect
- [x] OBPI-0.25.0-31-validation-receipts-pattern brief (attested 2026-04-13) — canonical precedent for the same source-module evaluation; recorded **Decision: Confirm** with five-point rationale and twelve-dimension capability table anchored on capability superset, single-narrow-win entanglement, central-vs-per-ADR storage architecture, atomic transaction semantics, and CLI integration
- [x] `src/gzkit/schemas/obpi.json` — required headers contract (validator caught ALL-CAPS heading drift; corrected to title case)
- [x] GHI #376 (open) — duplicate-OBPI tracking surface; this brief is the fifth structural instance of the same defect

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/validation_receipt.py` (274 lines) — opsdev source under review
- [x] Required path exists: `src/gzkit/events.py` (556 L, includes typed `EventAnchor` at line 355)
- [x] Required path exists: `src/gzkit/ledger_semantics.py` (547 L)
- [x] Required path exists: `src/gzkit/validate_pkg/ledger_check.py` (379 L)
- [x] Required path exists: `src/gzkit/temporal_drift.py` (348 L; absorbed via OBPI-0.25.0-26)
- [x] Required path exists: `src/gzkit/utils.py` (`capture_validation_anchor_with_warnings` at lines 64-105)
- [x] Required path exists: `src/gzkit/commands/obpi_complete.py` (atomic `_execute_transaction` at lines 225-237)
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Parent ADR Cross-Reference Matrix row for `validation_receipt.py` reviewed: anticipates "Decide whether current validation output already satisfies receipt-level audit requirements"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/validation_receipt.py` structure confirmed at lines 42-63 (`ValidationAnchor` Pydantic BaseModel — frozen, extra=forbid, regex SHA validation `^[0-9a-f]{7,40}$`), 84 (3 fixed event Literals: `validated`, `completed`, `compliance_check`), 86 (`evidence: dict[str, Any]` — untyped), 89-105 (attestor field validator forces `human:<name>` prefix), 107-113 (ADR-ID field validator using shared `ADR_ID_PATTERN`), 118-131 (`write_receipt()` plain JSONL append, no rollback), 134-172 (`read_receipts()` JSONL reader with malformed-line tolerance), 175-211 (`get_current_anchor()` raises `RuntimeError` on git unavailable), 245-249 (per-ADR ledger path resolution `{adr-folder}/logs/adr-validation.jsonl`)
- [x] `src/gzkit/events.py` confirmed: `EventAnchor` Pydantic BaseModel at line 355 (frozen, extra=forbid) replacing the prior `dict[str, str] | None` shape; `events.py:378, 389` reference `EventAnchor | None`; 17+ lifecycle event types in discriminated union; `ObpiReceiptEvidence` with nested `ScopeAudit`, `GitSyncState`, `ReqProofInput` payloads (strict Pydantic with field validators)
- [x] `src/gzkit/commands/obpi_complete.py` confirmed: `_execute_transaction` performs atomic three-step write (audit ledger entry + brief content + main ledger receipt event) with `OSError` rollback
- [x] `src/gzkit/temporal_drift.py` confirmed: consumes anchors from the central `.gzkit/ledger.jsonl` (already absorbed via OBPI-0.25.0-26)
- [x] `src/gzkit/utils.py` confirmed: `capture_validation_anchor_with_warnings` returns degraded fallback `{"commit": "0000000", "semver": "0.0.0"}` plus warnings list (graceful degradation vs opsdev's `RuntimeError`)
- [x] Duplicate-OBPI surface check: same source module `lib/validation_receipt.py` evaluated under both ADR-0.25.0/OBPI-31 (Confirm, attested 2026-04-13) and ADR-0.26.0/OBPI-08 (this brief) — defect tracked under **GHI #376** (will be extended via fifth-instance comment in Stage 5 if operator authorizes)

## Quality Gates

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test --obpi OBPI-0.26.0-08-validation-receipt` (vacuous parity-gate pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`; covered by `gz covers` parity gate)
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — **N/A**, Confirm outcome; existing receipt surface (`events.py` + `ledger_semantics.py` + `validate_pkg/ledger_check.py` + `temporal_drift.py` + `utils.capture_validation_anchor_with_warnings` + `commands/obpi_complete.py`) already constitutes the superior surface (per OBPI-0.25.0-31 precedent)

### Gate 3: Docs

- [x] Completed brief records a final `Confirm` decision (frontmatter `decision: Confirm` + `## Decision` body)
- [x] Comparison rationale names concrete capability differences and the chosen outcome (twelve-dimension table from OBPI-0.25.0-31 precedent + six-point Decision rationale + duplicate-OBPI tracking)

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior, the brief names `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [x] Otherwise the brief records `N/A` rationale for no external-surface change — see `### Gate 4 (BDD): N/A` in `## Decision`

### Gate 5: Human

- [ ] Human attestation required (Heavy lane) — recorded during Stage 4 ceremony of `gz-obpi-pipeline`

## Acceptance Criteria

- [x] REQ-0.26.0-08-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb`, `Confirm`, or `Exclude`. **Decision:
  Confirm** — see frontmatter and `## Decision` below.
- [x] REQ-0.26.0-08-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (twelve-dimension capability table) and
  `## Decision` (six-point rationale anchored on OBPI-0.25.0-31 plus the
  EventAnchor hardening update).
- [x] REQ-0.26.0-08-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests needed to carry the pattern safely.
  **N/A — Confirm outcome.** This REQ is vacuously satisfied.
- [x] REQ-0.26.0-08-04: [doc] Given a `Confirm` or `Exclude` outcome, then
  the brief explains why no upstream absorption is warranted. See
  `## Decision` — gzkit's distributed receipt surface is materially superior
  to opsdev's heuristic per-ADR storage on twelve dimensions, and opsdev's
  per-ADR ledger model contradicts gzkit's central-ledger doctrine.
- [x] REQ-0.26.0-08-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Confirm outcome with zero code changes
  under `src/gzkit/`, zero new CLI verbs, zero generated-surface change —
  nothing operator-visible changes under this brief.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/validation_receipt.py
# Expected: opsdev source under review exists

test -f src/gzkit/events.py && test -f src/gzkit/validate_pkg/ledger_check.py
# Expected: gzkit existing receipt surface exists (confirmed superior under OBPI-0.25.0-31)

rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: brief frontmatter and Decision body record the Confirm verdict
# (OBPI-0.26.0-08-specific verification command)

rg -n 'OBPI-0.25.0-31' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: brief cites the canonical precedent in body and Closing Argument
# (OBPI-0.26.0-08-specific verification command)

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-08-validation-receipt
# Expected: OBPI-scoped tests remain green (vacuous pass on [doc] REQ pattern via _synthesize_doc_proof_linkage)

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes (Confirm: not required)

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: completed brief captures Gate 4 N/A rationale
```

## Comparison

### Source-material observation

The brief Source Material header at parent-ADR Tidy First Plan row 8 names
"gzkit equivalent: Partial in `src/gzkit/validate.py`." That assertion is
stale at this brief's authoring time:

1. `src/gzkit/validate.py` is now a 121 L re-export shim that delegates to
   `validate_pkg/` submodules.
2. The actual gzkit receipt-validation surface is ~1830 L distributed
   across six modules.
3. The same source artifact was already evaluated as **architecturally
   superior** to opsdev's `lib/validation_receipt.py` under
   **OBPI-0.25.0-31-validation-receipts-pattern** (attested 2026-04-13).

| Surface | Lines | Role |
|---------|-------|------|
| `../airlineops/src/opsdev/lib/validation_receipt.py` | 274 | opsdev module: typed `ValidationAnchor`, `ValidationReceipt` extending `LedgerEntryBase`, JSONL persistence, per-ADR storage |
| `src/gzkit/events.py` | 556 | discriminated event union (17+ lifecycle types), typed `EventAnchor` (line 355), `ObpiReceiptEvidence` with nested `ScopeAudit` / `GitSyncState` / `ReqProofInput` |
| `src/gzkit/ledger_semantics.py` | 547 | semantic validation surface for ledger event payloads |
| `src/gzkit/validate_pkg/ledger_check.py` | 379 | append-only ledger JSONL validation |
| `src/gzkit/temporal_drift.py` | 348 | absorbed via OBPI-0.25.0-26; consumes anchors from central ledger |
| `src/gzkit/utils.py:64-105` | 42 | `capture_validation_anchor_with_warnings` graceful-degradation anchor capture |
| `src/gzkit/commands/obpi_complete.py:225-237` | 13 | atomic three-step `_execute_transaction` with `OSError` rollback |

This observation is body-level (Comparison section); the parent-ADR-authored
Source Material header is intentionally not amended (mirror of the
OBPI-0.26.0-04 / -05 / -06 / -07 pattern).

### Per-dimension comparison (re-anchored from OBPI-0.25.0-31 precedent)

The twelve-dimension capability table established by
OBPI-0.25.0-31-validation-receipts-pattern (2026-04-13, attested) holds for
the gzkit/opsdev capability shape because the source artifact is identical
(`lib/validation_receipt.py`, 274 lines) and the gzkit surface preserves
its distributed central-ledger architecture. Line anchors are refreshed to
the current files; the anchor-typing dimension is updated to record that
the prior narrow win has been closed.

| Dimension | opsdev `lib/validation_receipt.py` (274 L) | gzkit equivalent surface (~1830 L distributed) | Winner |
|-----------|---------------------------------------------|-------------------------------------------------|--------|
| Anchor schema typing | `ValidationAnchor` Pydantic BaseModel with regex SHA validation `^[0-9a-f]{7,40}$`, `tag`, `semver` — `frozen=True, extra="forbid"` (`validation_receipt.py:42-63`) | `EventAnchor` Pydantic BaseModel — `frozen=True, extra="forbid"` at `events.py:355`; `events.py:378, 389` reference `EventAnchor \| None`. **Closes the prior narrow win** (was `dict[str, str] \| None` at OBPI-0.25.0-31 authoring; hardened since) | gzkit (parity, then superior via integration) |
| Anchor capture robustness | `get_current_anchor()` raises `RuntimeError` when git unavailable or HEAD unresolvable (`validation_receipt.py:175-211`) | `capture_validation_anchor_with_warnings()` returns degraded fallback `{"commit": "0000000", "semver": "0.0.0"}` plus warnings list (`utils.py:64-105`) | gzkit (graceful degradation > raise) |
| Receipt event variety | 3 fixed Literals: `validated`, `completed`, `compliance_check` (`validation_receipt.py:84`) | 17+ lifecycle event types as a Pydantic discriminated union (`events.py` `_EventBase` and subclasses, including `ProjectInitEvent`, `AdrCreatedEvent`, `ObpiCreatedEvent`, `AttestedEvent`, `GateCheckedEvent`, `CloseoutInitiatedEvent`, `AuditReceiptEmittedEvent`, `ObpiReceiptEmittedEvent`, `ArtifactRenamedEvent`, etc.) | gzkit |
| Evidence model | `evidence: dict[str, Any]` — untyped (`validation_receipt.py:86`) | `ObpiReceiptEvidence` with nested `ScopeAudit`, `GitSyncState`, `ReqProofInput`, `req_proof_inputs`, `attestation_requirement`, `parent_lane`, `attestation_date`, `recorder_source`, `recorder_warnings` — strict Pydantic with field validators (`events.py`) | gzkit |
| Attestor enforcement | Field validator forces `human:<name>` prefix at model layer (`validation_receipt.py:89-105`) | Enforced in `obpi_complete.py` `_enforce_human_attestation_required()` against parent ADR lane + foundation kind + sensitivity axis; ledger-side attestation gating via `requires_human` flag | gzkit (three-axis predicate vs single check) |
| ADR ID validation | `validate_adr_id` field validator using shared `ADR_ID_PATTERN` (`validation_receipt.py:107-113`) | Pydantic `Field(pattern=...)` enforced in `core/models.py` for ADR/OBPI ID shape | parity |
| Storage architecture | Per-ADR ledger at `{adr-folder}/logs/adr-validation.jsonl` — one file per ADR (`validation_receipt.py:36, 245-249`) | Central `.gzkit/ledger.jsonl` — single canonical event log with discriminated union over `event` field | gzkit (central-ledger doctrine) |
| Drift consumption | Companion module `opsdev/lib/drift_detection.py` consumes anchors from per-ADR ledgers | Already absorbed as `src/gzkit/temporal_drift.py` via OBPI-0.25.0-26; consumes anchors from the central gzkit ledger | gzkit |
| CLI integration | None — module is library-only | `gz obpi complete`, `gz adr emit-receipt`, `gz obpi reconcile`, `gz adr status` — first-class CLI surface that builds + emits + validates receipts | gzkit |
| Atomic transaction | `write_receipt()` does a plain JSONL append with no rollback semantics (`validation_receipt.py:118-131`) | `_execute_transaction()` in `obpi_complete.py:225-237` performs an atomic three-step write (audit ledger entry + brief content + main ledger receipt event) with rollback on `OSError` | gzkit |
| Reader surface | `read_receipts()` reads JSONL with optional ADR filter and warns on malformed lines (`validation_receipt.py:134-172`) | Full `Ledger` reader/append API in `gzkit.ledger` plus dispatched semantic validation in `ledger_semantics.py` and `validate_pkg/ledger_check.py` | gzkit |
| Test surface | Library-only module outside gzkit's test footprint | gzkit receipt surface is exercised by `events.py`, `obpi_complete.py`, `temporal_drift.py`, `ledger_check.py` test modules across the unit + behave suites | gzkit |

### Cross-platform / convention-compliance observations

opsdev `lib/validation_receipt.py` carries two structural conflicts with
gzkit doctrine that absorb-by-copy could not eliminate:

1. **Per-ADR storage doctrine.** `validation_receipt.py:36, 245-249` writes
   one ledger per ADR folder. gzkit's central `.gzkit/ledger.jsonl` is the
   canonical event log; a parallel storage surface would double the audit
   footprint, not strengthen it.
2. **No CLI integration.** opsdev's module is library-only. Absorbing it
   would require building CLI surface around it that gzkit already provides
   via `gz obpi complete`, `gz adr emit-receipt`, `gz obpi reconcile`,
   `gz adr status` — net-negative effort.

Per OBPI-0.25.0-31's analysis, these are not adapt-and-clean fixes — they
are structural mismatches with gzkit's central-ledger-first doctrine that
make the absorbed module strictly worse than the existing distributed
surface.

## Decision

**Confirm** (by reference to OBPI-0.25.0-31-validation-receipts-pattern,
attested 2026-04-13). gzkit's existing receipt surface (~1830 L distributed
across `events.py` + `ledger_semantics.py` + `validate_pkg/ledger_check.py`
+ `temporal_drift.py` + `utils.capture_validation_anchor_with_warnings` +
`commands/obpi_complete.py`) is architecturally a strict superset of
opsdev's `lib/validation_receipt.py` (274 L) on twelve named dimensions;
absorbing the opsdev module would degrade governance compliance (per-ADR
storage contradicts central-ledger doctrine; plain-append loses atomic
transaction semantics) and add a parallel storage system with no
operator-visible capability gain. No absorption is warranted.

### Brief-scaffold defect (surfaced)

The brief Source Material at parent-ADR Tidy First Plan row 8 reads
"Partial in `src/gzkit/validate.py`." That wording is **stale and
misleading**:

- `src/gzkit/validate.py` is now a 121 L re-export shim, not the actual
  receipt-validation surface.
- gzkit DOES have a substantial existing surface (~1830 L distributed
  across six modules).
- OBPI-0.25.0-31 already evaluated this exact source artifact and decided
  **Confirm** with full five-point rationale and a twelve-dimension
  capability table — the precedent attests the Confirm verdict on
  identical source.
- OBPI-0.26.0-04 / -07 (sibling briefs on `lib/adr_governance.py` and
  `lib/adr_traceability.py`) carried analogous Source Material drift
  yet successfully landed `decision: Confirm` with the validator
  accepting the verdict.

The Source Material wording is itself a brief-scaffold defect — the fourth
instance of this defect class across ADR-0.26.0 briefs (also present in
OBPI-04 / -05 / -06 / -07 wording, surfaced and noted in each of those
briefs' Source-material observations). The defect is tracked structurally
under the broader GHI #376 duplicate-OBPI surface; the doctrine here is
that authoritative precedent (OBPI-0.25.0-31) overrides stale brief Source
Material.

### Rationale

1. **Strict superset of capability (canonical precedent).** OBPI-0.25.0-31
   evaluated the same opsdev source file (`lib/validation_receipt.py`,
   274 lines) against gzkit's distributed receipt surface three weeks
   earlier (attested 2026-04-13) and recorded **Decision: Confirm** with a
   five-point rationale. The gzkit surface covers every behavior the
   opsdev module provides — anchor capture, receipt emission, ADR-ID
   validation, attestor enforcement, JSONL persistence, malformed-line
   tolerance, drift consumption — with strictly greater capability and
   structure (17+ event types vs 3, strict Pydantic evidence models vs
   `dict[str, Any]`, ~1830 L vs 274 L). The source artifact is
   byte-for-byte identical at this brief's authoring time.

2. **Architectural mismatch — central vs per-ADR ledger.** opsdev's
   storage model is one validation ledger per ADR folder
   (`{adr-folder}/logs/adr-validation.jsonl`, `validation_receipt.py:36`).
   gzkit's storage model is a single canonical `.gzkit/ledger.jsonl` whose
   discriminated union covers every lifecycle event. Absorbing opsdev's
   per-ADR storage would create a parallel storage system that
   contradicts gzkit's central-ledger doctrine, not strengthen it. This
   is the same tooling-vs-consumer-layer distinction that drove the
   `Exclude` outcomes for OBPI-0.25.0-29 (`ledger_schema`) and
   OBPI-0.25.0-30 (`references`).

3. **Atomic transaction semantics already exist in gzkit.** opsdev's
   `write_receipt()` is a plain JSONL append with no rollback
   (`validation_receipt.py:118-131`). gzkit's `_execute_transaction()` in
   `obpi_complete.py:225-237` performs an atomic three-step write (audit
   ledger entry + brief content + main ledger receipt event) with
   rollback on `OSError`. Any absorption would either downgrade gzkit's
   atomicity or duplicate the transaction surface — both regressions.

4. **CLI integration only exists in gzkit.** opsdev's
   `validation_receipt.py` is a library module with no CLI surface.
   gzkit's receipt surface is reached operationally through `gz obpi
   complete`, `gz adr emit-receipt`, `gz obpi reconcile`, and `gz adr
   status` — first-class operator commands that build, emit, validate,
   and reconcile receipts. Absorbing the opsdev module would not add a
   single operator-visible capability gzkit lacks today.

5. **Graceful-degradation anchor capture.** opsdev's `get_current_anchor()`
   raises `RuntimeError` when git is unavailable
   (`validation_receipt.py:175-211`). gzkit's
   `capture_validation_anchor_with_warnings` (`utils.py:64-105`) returns
   a degraded fallback `{"commit": "0000000", "semver": "0.0.0"}` plus
   warnings list. The graceful path is doctrinally aligned with
   layered-trust T2 (escalate-not-escape): receipts are still
   emittable in unhealthy environments, with explicit recorder warnings
   surfacing the degradation.

6. **EventAnchor hardening — closes the prior narrow win.** OBPI-0.25.0-31
   identified one narrow place opsdev had more typing rigor: typed
   `ValidationAnchor` Pydantic model versus gzkit's
   `anchor: dict[str, str] | None` on the event models (`events.py:362, 373`
   at the time). That gap has since been closed — `src/gzkit/events.py:355`
   now defines `EventAnchor` as a frozen Pydantic model with
   `extra="forbid"`, replacing the prior dict shape on `events.py:378, 389`.
   The Confirm verdict is therefore structurally stronger today than at
   2026-04-13: gzkit now has parity on anchor typing AND retains every
   architectural advantage the original twelve-dimension comparison
   surfaced.

### Tracking the duplicate-evaluation signal

This brief is the fifth OBPI evaluating an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered:

| OBPI | Parent ADR | Source | Decision | Status |
|------|------------|--------|----------|--------|
| OBPI-0.25.0-20 | ADR-0.25.0 | `lib/adr_governance.py` | Confirm | attested 2026-04-11 |
| OBPI-0.26.0-04 | ADR-0.26.0 | (same) | Confirm-by-reference | attested |
| OBPI-0.25.0-29 | ADR-0.25.0 | `lib/ledger_schema.py` | Exclude | attested 2026-04-13 |
| OBPI-0.26.0-05 | ADR-0.26.0 | (same) | Exclude-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-26 | ADR-0.25.0 | `lib/drift_detection.py` | Absorb | attested 2026-04-09 |
| OBPI-0.26.0-06 | ADR-0.26.0 | (same) | Absorb-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-22 | ADR-0.25.0 | `lib/adr_traceability.py` | Confirm | attested 2026-04-09 |
| OBPI-0.26.0-07 | ADR-0.26.0 | (same) | Confirm-by-reference | attested 2026-05-01 |
| OBPI-0.25.0-31 | ADR-0.25.0 | `lib/validation_receipt.py` | Confirm | attested 2026-04-13 |
| **OBPI-0.26.0-08** | **ADR-0.26.0** | **(same)** | **Confirm-by-reference** (this brief) | **in-flight** |

The duplicate-OBPI surface is structurally identical to GHI #376's canonical
defect. Same root cause: the ADR-0.26.0 authoring did not check whether
ADR-0.25.0's earlier absorption sweep had already covered each module in
scope. Same proposed mitigation: `gz validate --absorption-duplicates`
would catch this fifth instance alongside the prior four.

Resolution: extend GHI #376 with this `lib/validation_receipt.py` fifth
instance via `gh issue comment` rather than file a parallel GHI — pending
operator authorization (per OBPI-07 ceremony observation that
`attest completed` does not authorize external GitHub comment posts; the
GHI extension requires explicit authorization). Root cause and mitigation
are identical; tracking unification keeps the ADR-0.26.0 closeout-audit
footprint single. The Confirm-by-reference verdict here closes the in-flight
duplicate; GHI #376 carries the long-term tracking surface.

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing receipt surface continues to function identically; no new
commands, flags, output formats, or behavioral changes are introduced.
`features/heavy_lane_gate4.feature` is not touched.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #8 captured verbatim above (`OBPI Entry (Level 1 WBS)` line).
- [x] **Gate 2 (TDD):** `uv run gz test --obpi OBPI-0.26.0-08-validation-receipt` remains green; vacuous pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`. Existing test coverage on the gzkit receipt surface (`events.py`, `obpi_complete.py`, `temporal_drift.py`, `ledger_check.py`) exists from prior OBPIs (Confirm decided gzkit's surface is superior). Evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above (`## Decision`, six-point rationale + brief-scaffold-defect surfacing + duplicate-evaluation tracking + Gate 4 N/A) with concrete capability deltas across twelve dimensions and the architectural-superiority observation.
- [x] **Gate 4 (BDD):** N/A — the Confirm-by-reference outcome introduces no operator-visible behavior change. `features/heavy_lane_gate4.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger entry type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

### Implementation Summary


- Decision: Confirm — by reference to OBPI-0.25.0-31-validation-receipts-pattern (attested 2026-04-13). gzkit's distributed receipt surface (`events.py` 556 L + `ledger_semantics.py` 547 L + `validate_pkg/ledger_check.py` 379 L + `temporal_drift.py` 348 L + `utils.capture_validation_anchor_with_warnings` 42 L + `commands/obpi_complete.py:225-237` atomic transaction; ~1830 L total) already constitutes an architecturally superior receipt surface to opsdev's `lib/validation_receipt.py` (274 L) on twelve named dimensions.
- Modules compared: opsdev `validation_receipt.py` (274 L; typed `ValidationAnchor`, 3 fixed event Literals, `evidence: dict[str, Any]`, per-ADR JSONL storage at `{adr-folder}/logs/adr-validation.jsonl`, plain append no rollback, library-only) vs gzkit distributed surface (typed `EventAnchor` Pydantic at `events.py:355`, 17+ lifecycle event discriminated union, strict Pydantic `ObpiReceiptEvidence` with nested `ScopeAudit`/`GitSyncState`/`ReqProofInput`, central `.gzkit/ledger.jsonl`, atomic three-step `_execute_transaction` with `OSError` rollback, first-class CLI via `gz obpi complete` / `gz adr emit-receipt` / `gz obpi reconcile` / `gz adr status`).
- Architectural superiority across twelve dimensions: anchor schema typing (now parity via EventAnchor + integration win), anchor capture robustness (graceful fallback vs raise), receipt event variety (17+ vs 3), evidence model (typed Pydantic vs dict[str,Any]), attestor enforcement (three-axis predicate vs single check), ADR-ID validation (parity), storage architecture (central vs per-ADR), drift consumption (gzkit-native via temporal_drift.py absorbed under OBPI-0.25.0-26), CLI integration (first-class vs library-only), atomic transaction (OSError rollback vs plain append), reader surface (full Ledger API vs basic JSONL), test surface (gzkit-exercised vs library-only).
- New observation since 2026-04-13: `EventAnchor` Pydantic model at `events.py:355` (`frozen=True, extra="forbid"`) closes the single narrow-win gap identified in the OBPI-0.25.0-31 precedent (was `dict[str, str] | None` at OBPI-0.25.0-31 authoring; hardened since under GHI #143). Confirm verdict structurally stronger today than at 2026-04-13.
- Brief-scaffold-defect surfaced: brief Source Material at parent-ADR Tidy First Plan row 8 reads "Partial in `src/gzkit/validate.py`" but `validate.py` is now a 121 L re-export shim and gzkit HAS a ~1830 L distributed receipt surface; the precedent OBPI-0.25.0-31 attests Confirm; OBPI-0.26.0-04/07 already established `decision: Confirm` is validator-accepted despite the assumption. Fourth instance of the same scaffold-defect class across ADR-0.26.0 briefs.
- Duplicate-OBPI surface tracked under **GHI #376** — fifth structural instance after OBPI-0.26.0-04 (`lib/adr_governance.py`), OBPI-0.26.0-05 (`lib/ledger_schema.py`), OBPI-0.26.0-06 (`lib/drift_detection.py`), OBPI-0.26.0-07 (`lib/adr_traceability.py`). Resolution: extend GHI #376 with a fifth-instance comment in Stage 5 if operator authorizes; do not file parallel GHI.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings (`OBJECTIVE`, `SOURCE MATERIAL`, `ASSUMPTIONS`, `NON-GOALS`, `REQUIREMENTS (FAIL-CLOSED)`, `ALLOWED PATHS`, `QUALITY GATES (Heavy)`, `ADR ITEM`) renamed to title case; added missing `Lane`, `Denied Paths`, `Discovery Checklist` sections; `Verification Commands (Concrete)` → `Verification` with two OBPI-specific verification commands.
- No code absorbed under this brief; no `src/gzkit/` or `tests/` edits — Confirm decided existing surface is superior; modifying it would invalidate the OBPI-0.25.0-31 attestation.

### Key Proof


```bash
rg -n '^decision: Confirm|^\*\*Confirm\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Confirms brief frontmatter and ## Decision body record the Confirm verdict.

rg -c 'OBPI-0.25.0-31' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: ≥10 — brief cites the canonical precedent across body, Decision rationale, Implementation Summary, Closing Argument.

test -f src/gzkit/events.py && test -f src/gzkit/validate_pkg/ledger_check.py
# Expected: gzkit modules exist (Confirm precedent under OBPI-0.25.0-31 attests they are superior).

grep -n 'class EventAnchor' src/gzkit/events.py
# Expected: 355:class EventAnchor(BaseModel):  — confirms the prior narrow win is closed.

uv run gz covers OBPI-0.26.0-08-validation-receipt --json
# Expected: {"summary": {"total_reqs": ..., "uncovered_reqs": 0, ...}} — parity-gate pass for [doc] REQs via _synthesize_doc_proof_linkage.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-08-validation-receipt.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): ruff `arb-ruff-f8c5232c699e437c9335015b90696ab8`, typecheck `arb-step-typecheck-4a0048e7bce44e09afb086533c724671`, unittest (OBPI-scoped, canonical) `arb-step-unittest-999c5e1fe9fc4dd2988f060d26f7114c`, mkdocs `arb-step-mkdocs-e002b267fe7d441ab88bf1cc98cc05de`. REQ→@covers parity: `gz covers OBPI-0.26.0-08-validation-receipt --json` → `uncovered_reqs: 0` (vacuous parity-gate pass on `[doc]` REQs via `_synthesize_doc_proof_linkage`; `total_reqs: 0` reflects the doc-proof synthesis path). Mirroring the OBPI-04/05/06/07 sibling precedent: pre-existing failures (GHI #377 insight schema regression, GHI #378 expired `release.drift_command` flag) remain disclosed in the broader ADR-0.26.0 evidence trail; not introduced by this brief.

## Human Attestation

- Attestor: `Jeffry Babb`
- Date: 2026-05-01
- Attestation: attest completed — OBPI-0.26.0-08 Confirm-by-reference verdict on opsdev lib/validation_receipt.py (274 L). Anchored on OBPI-0.25.0-31-validation-receipts-pattern (attested 2026-04-13, identical 274-line source) and OBPI-0.26.0-04/07 sibling precedents for `decision: Confirm` despite stale brief Source Material. Twelve-dimension capability comparison authored in brief ## Comparison; six-point rationale in ## Decision (rationale 6 records EventAnchor hardening at events.py:355 closing the prior narrow win since 2026-04-13); brief-scaffold-defect surfaced (fourth instance across ADR-0.26.0); Gate 4 N/A (zero operator-visible change). Heavy-lane Stage 3 ARB receipts cited inline in Key Proof: lint arb-ruff-f8c5232c699e437c9335015b90696ab8, typecheck arb-step-typecheck-4a0048e7bce44e09afb086533c724671, OBPI-scoped unittest arb-step-unittest-999c5e1fe9fc4dd2988f060d26f7114c, mkdocs arb-step-mkdocs-e002b267fe7d441ab88bf1cc98cc05de. REQ→@covers parity: 5×[doc] REQs, uncovered_reqs:0 via _synthesize_doc_proof_linkage. No `src/` or `tests/` edits (Confirm preserves OBPI-0.25.0-31 attestation). GHI #376 fifth-instance comment deferred to explicit operator authorization (out of scope for `attest completed`).

### Closing Argument

**Confirm-by-reference.** opsdev's `lib/validation_receipt.py` (274 lines)
provides validation-receipt generation via a typed `ValidationAnchor`
Pydantic model, a `ValidationReceipt` extending a shared `LedgerEntryBase`,
JSONL persistence, and a per-ADR storage convention
(`{adr-folder}/logs/adr-validation.jsonl`). gzkit's existing receipt
surface — ~1830 L distributed across `src/gzkit/events.py` (556 L,
including the typed `EventAnchor` Pydantic model at line 355 and the 17+
lifecycle event discriminated union with strict `ObpiReceiptEvidence`
payloads), `src/gzkit/ledger_semantics.py` (547 L semantic validation),
`src/gzkit/validate_pkg/ledger_check.py` (379 L append-only ledger
validation), `src/gzkit/temporal_drift.py` (348 L absorbed under
OBPI-0.25.0-26), `src/gzkit/utils.capture_validation_anchor_with_warnings`
(graceful-degradation anchor capture), and
`src/gzkit/commands/obpi_complete.py:225-237` (atomic three-step
`_execute_transaction` with `OSError` rollback) — is architecturally a
strict superset on twelve dimensions: anchor schema typing (parity via
EventAnchor + central-ledger integration), anchor capture robustness
(graceful vs raise), receipt event variety (17+ vs 3), evidence model
(strict Pydantic vs dict[str, Any]), attestor enforcement (three-axis
predicate vs single check), ADR-ID validation (parity), storage
architecture (central vs per-ADR), drift consumption (native vs reliant
on companion module), CLI integration (first-class vs library-only),
atomic transaction (rollback vs plain append), reader surface (full
Ledger API vs basic JSONL), and test surface (exercised vs unknown).

The opsdev module's per-ADR storage model contradicts gzkit's
central-ledger doctrine: `.gzkit/ledger.jsonl` is the single canonical
event log, and adding a parallel per-ADR storage system would double the
audit footprint, not strengthen it. Absorbing the opsdev pattern would
also downgrade gzkit's atomic three-step transaction (`obpi_complete.py`)
to a plain JSONL append. The single narrow place where opsdev had more
typing rigor at OBPI-0.25.0-31's authoring (`ValidationAnchor` vs
`dict[str, str] | None`) has since been closed — `EventAnchor` at
`events.py:355` is now a frozen Pydantic model with `extra="forbid"`,
making the Confirm verdict structurally stronger today than at
2026-04-13. Not absorbed.

This brief is the fifth evaluation of an opsdev `lib/` module across two
parent ADRs that the canonical OBPI-0.25.0-* sweep had already covered.
The brief Source Material's "Partial in `src/gzkit/validate.py`" wording
is itself a brief-scaffold defect — `validate.py` is now a 121 L re-export
shim and gzkit HAS a ~1830 L distributed receipt surface — and the
precedent (OBPI-0.25.0-31 with Decision: Confirm, attested 2026-04-13)
attests the Confirm verdict on identical source. OBPI-0.26.0-04 / -07
already established the precedent that `decision: Confirm` is
validator-accepted despite the brief assumption; this brief follows that
precedent. GHI #376 to be extended (under operator authorization) with a
fifth-occurrence comment so the absorption sweep does not silently
recur. No code under `src/gzkit/` or `tests/` is modified by this brief;
modifying the existing surface would invalidate the 2026-04-13
OBPI-0.25.0-31 attestation. Gate 4 N/A: zero operator-visible behavior
change.
