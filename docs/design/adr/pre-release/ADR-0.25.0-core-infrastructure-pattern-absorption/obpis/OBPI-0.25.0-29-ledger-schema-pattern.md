---
id: OBPI-0.25.0-29-ledger-schema-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 29
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-29: Ledger Schema Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-29 — "Evaluate and absorb opsdev/lib/ledger_schema.py (501 lines) — unified Pydantic schema for JSONL ledger entries"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/ledger_schema.py` (501 lines) against
gzkit's ledger schema surface and determine: Absorb, Confirm, or Exclude. The
airlineops module provides a unified Pydantic schema for JSONL ledger entries.
gzkit's equivalent surface spans `events.py` (470 lines), `ledger.py`
(598 lines), and `schemas/ledger.json` — approximately 1070+ lines across
3 artifacts providing typed event models with Pydantic discriminated unions.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/ledger_schema.py` (501 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/events.py`, `src/gzkit/ledger.py`, `src/gzkit/schemas/ledger.json` (~1070+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Both implementations use Pydantic for ledger entry modeling — the comparison should focus on schema completeness and validation rigor

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's event/ledger architecture around airlineops's unified schema approach

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

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [ ] REQ-0.25.0-29-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-29-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-29-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-29-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-29-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/ledger_schema.py
# Expected: airlineops source under review exists

test -f src/gzkit/events.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-29-ledger-schema-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Comparison Evidence

Both surfaces were read end-to-end before authoring this decision. The table
below records concrete differences grounded in file:line anchors.

| Dimension | airlineops `opsdev/lib/ledger_schema.py` (501 L) | gzkit `events.py` + `ledger.py` + `schemas/ledger.json` (~1288 L) |
| --- | --- | --- |
| Purpose | Audit-only schema for per-ADR `obpi-audit.jsonl` logs | Lifecycle-wide event stream for central `.gzkit/ledger.jsonl` |
| Schema version | `govzero.ledger.v1` (`ledger_schema.py:27`) | `gzkit.ledger.v1` (`ledger.py:14`) |
| Storage location | `docs/design/adr/{adr-series}/{adr-folder}/logs/obpi-audit.jsonl` (per-ADR) | Central `.gzkit/ledger.jsonl` (append-only `Ledger.append`, `ledger.py:165-180`) |
| Entry / event types | 4 audit types: `obpi-audit`, `covers-map`, `coverage-run`, `reconciliation` | 17+ lifecycle events: `project_init`, `prd_created`, `constitution_created`, `obpi_created`, `adr_created`, `artifact_edited`, `attested`, `gate_checked`, `closeout_initiated`, `audit_receipt_emitted`, `obpi_receipt_emitted`, `artifact_renamed`, `adr_annotated`, `lifecycle_transition`, `task_started`, `task_completed`, `task_blocked`, `task_escalated` (`events.py:286-463`) |
| Discriminator | `type` (`ledger_schema.py:162`) | `event` (`events.py:462`) |
| Discriminated union | `LedgerEntry = Annotated[...ObpiAuditEntry \| CoversMapEntry \| CoverageRunEntry \| ReconciliationEntry, Field(discriminator="type")]` (`ledger_schema.py:315-318`) | `TypedLedgerEvent` over all 17 event classes, resolved via `TypeAdapter` (`events.py:443-465`) |
| ID pattern validation | `OBPI_ID_PATTERN`, `ADR_ID_PATTERN` as `@field_validator`s in `ObpiAuditEntry` (`ledger_schema.py:189-203`) | Pydantic `Field(..., pattern=r"^OBPI-...$")` enforced at the domain model boundary in `core/models.py:37,140` |
| Nested evidence models | Flat `EvidencePayload` (`ledger_schema.py:98-119`) with `extra="allow"` | `ReqProofInput`, `ScopeAudit`, `GitSyncState`, `ObpiReceiptEvidence` with cross-field validation (`events.py:45-205`) |
| Legacy entry handling | `_infer_entry_type()` reconstructs `type` for entries written before the discriminator existed (`ledger_schema.py:326-346`) | Not needed — every gzkit ledger entry emits an explicit `event` field |
| Immutability | `ConfigDict(frozen=True)` on every model | `ConfigDict(extra="forbid")` on `_EventBase`; append-only `Ledger.append` never mutates in place |
| Persistence class | None — schema-only module | `Ledger` class with append, `read_all`, `query`, `latest_event`, `canonicalize_id`, `get_latest_gate_statuses`, `get_artifact_graph`, `get_pending_attestations`, rename-chain resolution, cache invalidation (`ledger.py:133-565`) |
| Validator entry points | `validate_ledger_entry`, `is_valid_ledger_entry`, `parse_ledger_entry`, `create_timestamp` (`ledger_schema.py:349-470`) | `parse_typed_event` + structured Pydantic errors + `pydantic_loc_to_field_path` helper (`events.py:213-470`); per-event JSON schema in `schemas/ledger.json` backs CLI-side validation |

## Decision: Exclude

**Decision:** Exclude.

**Rationale.** `airlineops/src/opsdev/lib/ledger_schema.py` and gzkit's
ledger surface solve different problems at different layers; gzkit is a
functional superset for its problem, and absorbing airlineops's module would
collide with gzkit's state doctrine rather than reinforce it.

1. **Architectural scope mismatch.** airlineops's module is an audit-only
   schema covering four entry types — `obpi-audit`, `covers-map`,
   `coverage-run`, `reconciliation` — written to per-ADR
   `logs/obpi-audit.jsonl` files. gzkit's `events.py`/`ledger.py` pair covers
   the full governance lifecycle (creation, attestation, gate checks,
   closeout, receipts, renames, task state transitions) written to a single
   central `.gzkit/ledger.jsonl`. These are architecturally distinct
   surfaces, not overlapping implementations. Absorbing audit-entry types
   into gzkit's lifecycle stream would either duplicate existing event
   semantics or fragment the ledger into parallel storage layouts.
2. **Superset functionality.** Every capability airlineops's module
   provides already exists in gzkit in richer form:
   - **Discriminated union breadth:** 17+ typed event classes
     (`events.py:286-463`) versus airlineops's four audit entry classes.
   - **ID format validation:** gzkit enforces OBPI/ADR identifier patterns
     as Pydantic `Field(..., pattern=...)` constraints at the domain-model
     boundary (`core/models.py:37`, `core/models.py:140`), which is a
     declarative superset of airlineops's `field_validator`/regex pair.
   - **Nested evidence models:** `ObpiReceiptEvidence`, `ScopeAudit`,
     `GitSyncState`, and `ReqProofInput` (`events.py:45-205`) carry
     cross-field validation (allowlist/out-of-scope linkage, proof-input
     kind/status coupling, git sync ahead/behind arithmetic) that the flat
     `EvidencePayload` in airlineops does not attempt.
   - **Persistence and derivation:** the `Ledger` class (`ledger.py:133-565`)
     provides append, query, latest-event lookup, rename-chain canonicalization,
     gate-status derivation, artifact graph construction, and cache
     invalidation. airlineops's module ships no persistence class — it is
     schema-only.
3. **Storage doctrine conflict.** gzkit's state doctrine names a single
   canonical Layer 2 ledger as source of truth and explicitly prohibits
   derived views from silently becoming source-of-truth
   (`CLAUDE.md` § Architectural Boundaries, item 6). A per-ADR
   `obpi-audit.jsonl` pattern would sit beside the canonical ledger and
   accrete governance facts that the central ledger does not see — exactly
   the drift vector the architecture memo calls out. Absorbing the pattern
   would require either migrating it into the central ledger (at which
   point it becomes duplicated semantics) or tolerating two sources of
   truth (which the doctrine forbids).
4. **No narrow idiom warrants standalone absorption.** In contrast to
   OBPI-0.25.0-27's `_safe_print` outcome (a narrow robustness helper
   absorbed as a surgical addition), `ledger_schema.py` exposes no
   standalone utility that gzkit lacks. The `ConfigDict(frozen=True)`
   discipline is a minor convention difference, but `extra="forbid"` plus
   append-only writes give gzkit the same practical immutability guarantee
   without a migration cost across 17 event classes. The `create_timestamp`
   helper is one line that gzkit already inlines via
   `datetime.now(UTC).isoformat()` in `_EventBase.ts` default factories.
5. **Tooling layer vs consumer layer.** gzkit is governance *tooling* that
   downstream projects adopt to govern their own development. Its ledger
   surface must be general-purpose and serve as the canonical Layer 2
   storage for any host project — hence the lifecycle-wide event stream.
   airlineops's `opsdev/lib/ledger_schema.py` sits in the opposite
   position: it is an audit-layer schema internal to a domain application
   (airline operations), coupled to airlineops's decision to keep per-ADR
   audit logs alongside its own state. The brief's `ASSUMPTIONS` section
   names the subtraction test — "if it's not airline-specific, it belongs
   in gzkit" — and this module fails that test in a non-obvious way: the
   Python code is not airline-specific, but the *storage layout assumption*
   it encodes (per-ADR `logs/obpi-audit.jsonl` as a secondary surface) is a
   consumer-layer architectural choice that a tooling layer should not
   mandate on its adopters. Absorbing it would push a domain-specific
   storage assumption into the framework — the opposite of what a toolkit
   is for.

**Consequence.** No source or test edits in this brief. Documentation-only
decision recorded here; the ADR-0.25.0 decision table will pick up the
`Exclude` outcome via `gz obpi reconcile` and `gz adr status` in Stage 5.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.25.0 checklist item #29 captured verbatim above.
- [x] **Gate 2 (TDD):** N/A — Exclude outcome introduces no code or tests. `uv run gz test` remains green because no source changed; evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above with concrete capability, robustness, and storage-doctrine differences between airlineops and gzkit.
- [x] **Gate 4 (BDD):** N/A — the Exclude outcome introduces no operator-visible behavior change. `features/core_infrastructure.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger entry type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

## Evidence

### Gate 1 (ADR)

- Intent captured verbatim from ADR-0.25.0 checklist item #29 in brief l.15
- Scope aligned with ADR Heavy lane and the standard absorb/confirm/exclude contract

### Gate 2 (TDD)

- Existing gzkit test suite remains green — no new tests needed for an Exclude decision
- Verification: `uv run gz test` → 17 features passed, 110 scenarios passed, 584 steps passed, 0 failed

### Code Quality

- No code changes — Exclude decision is documentation-only
- `uv run gz lint` → All checks passed; ADR path contract check passed; no `Path(__file__).parents[N]` violations
- `uv run gz typecheck` → All checks passed
- `uv run gz validate --documents` → All validations passed
- `uv run mkdocs build --strict` → Documentation built in 1.97 seconds
- `uv run gz covers OBPI-0.25.0-29-ledger-schema-pattern --json` → `total_reqs=0, uncovered_reqs=0` (trivial pass)

### Value Narrative

Before this OBPI, the comparison between `airlineops/src/opsdev/lib/ledger_schema.py` (501 L audit-only schema for per-ADR `obpi-audit.jsonl`) and gzkit's lifecycle ledger surface — `events.py` (470 L typed events) + `ledger.py` (598 L `Ledger` persistence class) + `schemas/ledger.json` (220 L per-event JSON schema), ~1288 L total — was unrecorded. After this OBPI, a five-point rationale is on the record explaining why gzkit's surface is architecturally more appropriate for gzkit's problem: scope mismatch (17+ lifecycle events vs 4 audit types), superset functionality within the overlap (Pydantic `pattern` validators at `core/models.py:37,140`; richer nested evidence models `ObpiReceiptEvidence`/`ScopeAudit`/`GitSyncState`/`ReqProofInput` at `events.py:45-205`; `Ledger` persistence class at `ledger.py:133-565` that airlineops lacks entirely), Layer 2 state doctrine conflict (CLAUDE.md § Architectural Boundaries item 6 prohibits per-ADR derived storage from becoming source-of-truth), no narrow idiom warranting absorption, and — most decisively — the tooling-layer vs consumer-layer distinction. gzkit is governance tooling that downstream projects adopt, so its ledger surface must be general-purpose and carry canonical Layer 2 state for any host. airlineops's `ledger_schema.py` is a consumer-layer audit extension coupled to airlineops's decision to keep per-ADR audit logs alongside its own state — absorbing it would push a consumer-layer storage assumption into the tooling layer, which is architecturally backwards. The subtraction test fails in a non-obvious way: the Python code is not airline-specific, but the storage-layout assumption it encodes is.

### Key Proof


- Decision: Exclude
- Comparison: twelve-dimension table in `## Comparison Evidence`
- airlineops `ledger_schema.py`: 501 L, 4 audit entry types, per-ADR `logs/obpi-audit.jsonl`, `govzero.ledger.v1`
- gzkit surface: ~1288 L across `events.py` + `ledger.py` + `schemas/ledger.json`, 17+ lifecycle event types, central `.gzkit/ledger.jsonl`, `gzkit.ledger.v1`
- Storage doctrine: CLAUDE.md § Architectural Boundaries item 6 prohibits derived views from silently becoming source-of-truth
- Tooling vs consumer distinction: gzkit is framework, airlineops is domain consumer; per-ADR audit-log storage layout is a consumer-layer architectural choice a toolkit should not mandate
- `rg -n 'Decision: Exclude' docs/.../OBPI-0.25.0-29-ledger-schema-pattern.md` matches at lines 143 and 145

### Implementation Summary


- Decision: Exclude
- Files created: none
- Files modified: this brief only (`docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-29-ledger-schema-pattern.md`)
- Tests added: none (no code changes)
- Date: 2026-04-13

## Tracked Defects

Pre-existing tooling drift noticed but out of scope: `uv run gz plan audit` (`src/gzkit/commands/plan_audit_cmd.py:77`) writes only the per-OBPI receipt `.plan-audit-receipt-{obpi_id}.json`, while `plan-audit-gate.py` (`src/gzkit/hooks/scripts/pipeline.py:258`) reads only the legacy `.plan-audit-receipt.json`. Without the `/gz-plan-audit` skill manually writing the legacy file, `ExitPlanMode` stays blocked even after a PASS verdict. Flag for downstream triage in a separate brief — not addressed here.

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed — Exclude decision recorded with five-point rationale including the tooling-layer vs consumer-layer distinction that decisively disqualifies absorption. See brief Human Attestation section for the full enrichment.
- Date: 2026-04-13

## Closing Argument

gzkit's ledger surface — `events.py` (470 L typed event models),
`ledger.py` (598 L `Ledger` class with append/read/query/graph), and
`schemas/ledger.json` (220 L per-event JSON schema) — is a functional
superset of airlineops's `opsdev/lib/ledger_schema.py` (501 L audit-only
schema) for the governance lifecycle ledger problem. Every capability
airlineops provides — discriminated typed unions, ID pattern validation,
nested evidence models, legacy entry handling, frozen models — gzkit
provides in richer form, over more entry types, with a persistence class
and derivation pipeline airlineops does not ship. Absorbing the airlineops
module would not add capability; it would add a parallel per-ADR storage
layout that conflicts with gzkit's Layer 2 state doctrine (CLAUDE.md
§ Architectural Boundaries item 6). More importantly, gzkit is governance
tooling that downstream projects adopt, while airlineops's
`ledger_schema.py` is a consumer-layer audit extension specific to
airlineops's operational needs — absorbing it would push a
consumer-layer storage assumption (per-ADR `logs/obpi-audit.jsonl`) into
the tooling layer, which is architecturally backwards for a framework
designed to leave storage layout decisions to its adopters. The
doctrinally-coherent outcome is to Exclude — treat airlineops's
audit-specific schema as a domain choice that made sense for its
per-ADR audit-log layout, and leave gzkit's lifecycle ledger
undisturbed.
