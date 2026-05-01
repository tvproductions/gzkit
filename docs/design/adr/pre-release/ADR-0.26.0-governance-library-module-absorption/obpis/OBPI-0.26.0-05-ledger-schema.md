---
id: OBPI-0.26.0-05-ledger-schema
parent: ADR-0.26.0-governance-library-module-absorption
item: 5
status: Completed
lane: heavy
date: 2026-03-21
decision: Exclude
---

# OBPI-0.26.0-05: Ledger Schema

## ADR Item

- Source ADR: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.26.0-05 — "Evaluate and absorb lib/ledger_schema.py (501 lines) — ledger schema definitions and validation"`

## Objective

Evaluate `../airlineops/src/opsdev/lib/ledger_schema.py` (501 lines)
against gzkit's partial ledger schema in `src/gzkit/ledger.py` and determine:
Absorb (opsdev is better), Confirm (gzkit is sufficient), or Exclude
(domain-specific). The opsdev module provides dedicated ledger schema
definitions and validation, including schema versioning, entry type
definitions, migration logic, and structural validation. gzkit has partial
coverage in `src/gzkit/ledger.py`, but the comparison must determine whether
its inline schema handling adequately covers the same capability.

## Source Material

- **opsdev:** `../airlineops/src/opsdev/lib/ledger_schema.py` (501 lines)
- **gzkit equivalent:** Partial in `src/gzkit/ledger.py`

## Lane

**Heavy** — parent ADR-0.26.0 is Heavy-lane, and any absorption outcome
would add or change a runtime module / CLI surface. Confirm and Exclude
outcomes inherit Heavy because the decision is binding on future
governance-library absorption work and because the brief frontmatter
records a doctrine choice (Exclude-by-reference to OBPI-0.25.0-29) that
future agents will treat as canonical.

## Assumptions

- The subtraction test governs: if it's not ops-specific, it belongs in gzkit
- opsdev wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Ledger schema management (versioning, migration, validation) is a governance primitive that belongs in gzkit
- gzkit's ledger.py likely handles schema inline without the versioning and migration depth that a dedicated 501-line module provides
- The actual gzkit comparison surface for opsdev `lib/ledger_schema.py` is the `events.py` + `ledger.py` + `schemas/ledger.json` triad (1,602 L), not `ledger.py` alone — recorded in `## Comparison` body section (parent-ADR-authored Source Material header not amended)

## Non-Goals

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing opsdev — this is upstream absorption only
- Replacing gzkit's existing ledger module — the goal is enriching schema capabilities
- Re-running the comparison work already attested under OBPI-0.25.0-29-ledger-schema-pattern (2026-04-13) on identical source material — divergent rationale on identical material is itself a doctrine-drift signal

## Requirements (FAIL-CLOSED)

1. Read both implementations completely.
2. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage.
3. Record decision with rationale: Absorb / Confirm / Exclude.
4. If Absorb: adapt to gzkit conventions and write tests.
5. If Confirm: document why gzkit's implementation is sufficient despite lacking dedicated schema management.
6. If Exclude: document why the module is domain-specific.

## Allowed Paths

- `src/gzkit/` — target for absorbed modules (Absorb path only)
- `tests/` — tests for absorbed modules (Absorb path only)
- `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` — this ADR and briefs

## Denied Paths

- Any path outside `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/` for Confirm/Exclude outcomes (no code, no tests, no CLI change)
- `../airlineops/` — opsdev is upstream; absorption is one-way into gzkit
- `pyproject.toml` — no new dependencies added as a side-effect of a governance-library comparison brief
- CI files, lockfiles, or unrelated runtime surfaces

## Discovery Checklist

**Governance (read once, cache):**

- [x] Parent ADR `ADR-0.26.0-governance-library-module-absorption.md` — understand the 12-module absorption program and the subtraction test
- [x] Sibling OBPI-0.26.0-04-adr-governance brief — confirm Confirm-by-reference structural pattern, source-material observation pattern, and `[doc]` REQ tag convention
- [x] OBPI-0.25.0-29-ledger-schema-pattern brief (Completed 2026-04-13) — canonical precedent for the same source-module evaluation, recorded **Decision: Exclude** with five-point rationale
- [x] `src/gzkit/schemas/obpi.json` — required headers contract (validator caught ALL-CAPS heading drift; corrected to title case)
- [x] GHI #376 (open) — duplicate-OBPI tracking surface for `lib/adr_governance.py`; this brief is structurally a second instance of the same defect for `lib/ledger_schema.py`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists: `../airlineops/src/opsdev/lib/ledger_schema.py` (501 lines) — opsdev source under review
- [x] Required path exists: `docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/ADR-0.26.0-governance-library-module-absorption.md` — parent ADR
- [x] Parent ADR Cross-Reference Matrix row for `ledger_schema.py` reviewed: anticipates "Decide whether schema/versioning should remain inline or become a first-class module"

**Existing Code (understand current state):**

- [x] `../airlineops/src/opsdev/lib/ledger_schema.py` structure confirmed at lines 27, 98, 154, 162, 235, 264, 286, 315-318, 326-346, 349-470 (entry classes, EvidencePayload, discriminator, legacy `_infer_entry_type`, validator entry points)
- [x] gzkit comparison surface read with refreshed line anchors: `src/gzkit/events.py` (556 L; `_EventBase:232`, event classes 286-514, `TypedLedgerEvent:522`, `_typed_event_adapter:551`, `parse_typed_event:554`, nested evidence models 45/96/106/132), `src/gzkit/ledger.py` (728 L; `Ledger:170`, `append:202`, `read_all:254`, `query:279`, `latest_event:304`, `canonicalize_id:339`, `get_latest_gate_statuses:365`, `get_artifact_graph:614`, `get_pending_attestations:644`), `src/gzkit/schemas/ledger.json` (318 L), `src/gzkit/core/models.py:25,41,147,168` (ID pattern validators)
- [x] Duplicate-OBPI surface check: same source module `lib/ledger_schema.py` evaluated under both ADR-0.25.0/OBPI-29 (Completed Exclude) and ADR-0.26.0/OBPI-05 (this brief) — defect tracked under **GHI #376** (will be extended via second-instance comment in Stage 5)

## Quality Gates

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

- [ ] If the chosen path changes operator-visible behavior, the brief names
  `features/heavy_lane_gate4.feature` as the Gate 4 behavioral proof artifact
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.26.0-05-01: [doc] Given the completed comparison, then the brief
  records one final decision: `Absorb`, `Confirm`, or `Exclude`.
  **Decision: Exclude** — see `## Decision` below.
- [x] REQ-0.26.0-05-02: [doc] Given the decision rationale, then it cites
  concrete capability, robustness, or ergonomics differences between opsdev
  and gzkit. See `## Comparison` (twelve-dimension table re-anchored to
  current line ranges) and `## Decision` (six-point rationale anchored on
  OBPI-0.25.0-29-ledger-schema-pattern).
- [x] REQ-0.26.0-05-03: [doc] Given an `Absorb` outcome, then gzkit contains
  the adapted module/tests needed to carry the pattern safely. **N/A —
  Exclude outcome.** No code absorbed; this REQ is vacuously satisfied.
- [x] REQ-0.26.0-05-04: [doc] Given a `Confirm` or `Exclude` outcome, then
  the brief explains why no upstream absorption is warranted. See
  `## Decision` — the six-point rationale (architectural-scope mismatch,
  superset functionality, storage-doctrine conflict, no-narrow-idiom,
  tooling-vs-consumer distinction, duplicate-OBPI surface) documents why
  no upstream absorption is warranted.
- [x] REQ-0.26.0-05-05: [doc] Given any operator-visible behavior change,
  then Gate 4 behavioral proof is present; otherwise the brief records
  `N/A` with rationale. **N/A.** Exclude outcome with zero code changes
  under `src/gzkit/`, zero new CLI verbs, zero generated-surface change —
  nothing operator-visible changes, so Gate 4 behavioral proof is not
  required.

## Verification

```bash
test -f ../airlineops/src/opsdev/lib/ledger_schema.py
# Expected: opsdev source under review exists

test -f src/gzkit/ledger.py
# Expected: gzkit comparison target exists before or after the decision

rg -n '^decision: Exclude|^\*\*Exclude\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md
# Expected: brief frontmatter and Decision body record the Exclude verdict
# (OBPI-0.26.0-05-specific verification command)

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md
# Expected: completed brief records one final decision

uv run gz test --obpi OBPI-0.26.0-05-ledger-schema
# Expected: OBPI-scoped tests remain green (vacuous pass when no @covers
# tests target this OBPI — the [doc] REQ pattern routes to brief-content
# proof via _synthesize_doc_proof_linkage; covered by gz covers parity gate)

uv run -m behave features/heavy_lane_gate4.feature
# Expected: only required when operator-visible behavior changes

rg -n 'Gate 4|N/A|behavioral proof' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md
# Expected: completed brief captures operator-visible proof requirement or N/A rationale
```

## Comparison

### Source-material observation

The brief Source Material header at line 31 names `src/gzkit/ledger.py` as
the gzkit equivalent — mirroring the parent ADR's Tidy First Plan table at
`ADR-0.26.0-...md:30`. ledger.py (728 lines, current) is the persistence-class
surface only. The actual gzkit ledger-schema surface that mirrors opsdev's
`lib/ledger_schema.py` (501 lines) is a triad:

| gzkit module | Lines | Role |
|--------------|-------|------|
| `src/gzkit/events.py` | 556 | Typed ledger event models, ~25 lifecycle event classes via Pydantic discriminated union, nested evidence models with cross-field validation |
| `src/gzkit/ledger.py` | 728 | `Ledger` persistence class (`append`, `read_all`, `query`, `latest_event`, `canonicalize_id`, gate-status derivation, artifact graph, rename-chain resolution, cache invalidation) |
| `src/gzkit/schemas/ledger.json` | 318 | Per-event JSON Schema consumed by CLI-side validation |

Total gzkit surface: 1,602 lines vs opsdev's 501 lines. This observation is
body-level (Comparison section); the parent-ADR-authored Source Material
header is intentionally not amended (mirror of the OBPI-0.26.0-04 pattern).

### Per-dimension comparison (re-anchored from OBPI-0.25.0-29 precedent)

The dimension table established by OBPI-0.25.0-29-ledger-schema-pattern
(2026-04-13, attested) holds verbatim because the source artifact is
identical (`lib/ledger_schema.py`, 501 lines, `govzero.ledger.v1`) and the
gzkit comparison surface is unchanged in capability between attestations
(events.py grew 470 → 556 lines via new lifecycle events, ledger.py grew
598 → 728 lines via additional persistence helpers, but the architectural
shape is unchanged). Line anchors are refreshed to the current files; capability
deltas are noted inline.

| Dimension | opsdev `lib/ledger_schema.py` (501 L) | gzkit `events.py` + `ledger.py` + `schemas/ledger.json` (1,602 L) |
| --- | --- | --- |
| Purpose | Audit-only schema for per-ADR `obpi-audit.jsonl` logs | Lifecycle-wide event stream for central `.gzkit/ledger.jsonl` |
| Schema version | `govzero.ledger.v1` (`ledger_schema.py:27`) | `gzkit.ledger.v1` (recorded in events.py header docstring) |
| Storage location | `docs/design/adr/{adr-series}/{adr-folder}/logs/obpi-audit.jsonl` (per-ADR) | Central `.gzkit/ledger.jsonl` (append-only `Ledger.append`, `ledger.py:202`) |
| Entry / event types | 4 audit types: `obpi-audit`, `covers-map`, `coverage-run`, `reconciliation` (`ledger_schema.py:154,235,264,286`) | ~25 lifecycle event classes: `project_init`, `prd_created`, `constitution_created`, `obpi_created`, `adr_created`, `artifact_edited`, `attested`, `gate_checked`, `closeout_initiated`, `event_anchor`, `audit_receipt_emitted`, `obpi_receipt_emitted`, `artifact_renamed`, `adr_annotated`, `lifecycle_transition`, `agent_sync_completed`, `adr_eval_completed`, `audit_generated`, `obpi_lock_claimed`, `obpi_lock_released`, `obpi_withdrawn`, `patch_release`, `task_started`, `task_completed`, `task_blocked`, `task_escalated` (`events.py:286-514`). Capability delta vs precedent: precedent cited 17+ events; current count ~25 (8 new lifecycle events added since 2026-04-13). |
| Discriminator | `type` (`ledger_schema.py:162`) | `event` (`events.py` `_EventBase:232` + per-event `event: ClassVar[str]`) |
| Discriminated union | `LedgerEntry = Annotated[...ObpiAuditEntry \| CoversMapEntry \| CoverageRunEntry \| ReconciliationEntry, Field(discriminator="type")]` (`ledger_schema.py:315-318`) | `TypedLedgerEvent = Annotated[...]` over all ~25 event classes, resolved via `_typed_event_adapter: TypeAdapter[TypedLedgerEvent]` (`events.py:522,551`) |
| ID pattern validation | `OBPI_ID_PATTERN`, `ADR_ID_PATTERN` as `@field_validator`s in `ObpiAuditEntry` (`ledger_schema.py:189-203`) | Pydantic `Field(..., pattern=...)` enforced at the domain-model boundary in `core/models.py:25` (AdrFrontmatter), `core/models.py:41` (ObpiFrontmatter), `core/models.py:147` (AdrId), `core/models.py:168` (ObpiId). Capability delta vs precedent: precedent cited `core/models.py:37,140`; current anchors are 25/41/147/168 — same declarative-validator capability, anchors shifted only. |
| Nested evidence models | Flat `EvidencePayload` (`ledger_schema.py:98-119`) with `extra="allow"` | `ReqProofInput`, `ScopeAudit`, `GitSyncState`, `ObpiReceiptEvidence` with cross-field validation (`events.py:45,96,106,132` — unchanged from precedent's 45-205 range) |
| Legacy entry handling | `_infer_entry_type()` reconstructs `type` for entries written before the discriminator existed (`ledger_schema.py:326-346`) | Not needed — every gzkit ledger entry emits an explicit `event` field |
| Immutability | `ConfigDict(frozen=True)` on every model | `ConfigDict(extra="forbid")` on `_EventBase`; append-only `Ledger.append` never mutates in place (`ledger.py:202`) |
| Persistence class | None — schema-only module | `Ledger` class with `append`, `read_all`, `query`, `latest_event`, `canonicalize_id`, `get_latest_gate_statuses`, `get_artifact_graph`, `get_pending_attestations`, rename-chain resolution, cache invalidation (`ledger.py:170,202,254,279,304,339,365,614,644`) |
| Validator entry points | `validate_ledger_entry`, `is_valid_ledger_entry`, `parse_ledger_entry`, `create_timestamp` (`ledger_schema.py:349-470`) | `parse_typed_event` (`events.py:554`) + structured Pydantic errors + per-event JSON schema in `schemas/ledger.json` backs CLI-side validation |

### Cross-platform / convention-compliance observations

opsdev `lib/ledger_schema.py` is stdlib + Pydantic only (no ops-internal
imports unlike `lib/adr_governance.py`), so the imports themselves do not
fail the subtraction test. The doctrinal failure is the *storage-layout
assumption* the schema encodes: per-ADR `logs/obpi-audit.jsonl` files as
secondary surfaces beside the canonical ledger. gzkit's surface uses a
single central `.gzkit/ledger.jsonl` as Layer 2 source-of-truth and forbids
derived per-ADR storage from accreting governance facts the central ledger
does not see (`CLAUDE.md` § Architectural Boundaries item 6).

## Decision

**Exclude** (by reference to OBPI-0.25.0-29-ledger-schema-pattern, attested
2026-04-13). gzkit's ledger surface (`events.py` + `ledger.py` +
`schemas/ledger.json`, ~1,602 lines) is a functional superset of opsdev's
`lib/ledger_schema.py` (501 lines) for the gzkit problem. Absorbing the
opsdev module would not add capability; it would push a consumer-layer
storage-layout assumption (per-ADR `obpi-audit.jsonl`) into the tooling
layer, which collides with gzkit's Architectural Boundary 6 and the
tooling-vs-consumer distinction.

### Rationale

1. **Canonical precedent.** OBPI-0.25.0-29-ledger-schema-pattern evaluated
   the same opsdev source file (`lib/ledger_schema.py`, 501 lines) against
   the same gzkit surface three weeks earlier (attested 2026-04-13) and
   recorded **Decision: Exclude** with five-point rationale anchored on
   architectural-scope mismatch, superset functionality, storage-doctrine
   conflict, no-narrow-idiom, and tooling-vs-consumer distinction. The
   source artifact is byte-for-byte identical; the gzkit surface has grown
   by ~310 lines (events.py 470→556, ledger.py 598→728) but the
   architectural shape and capability guarantees are unchanged.
   Re-running the comparison with divergent rationale on identical source
   material would itself be a doctrine-drift signal — Exclude-by-reference
   is the structurally correct landing.
2. **Architectural scope mismatch.** opsdev's module is an audit-only
   schema covering four entry types — `obpi-audit`, `covers-map`,
   `coverage-run`, `reconciliation` — written to per-ADR
   `logs/obpi-audit.jsonl` files. gzkit's `events.py`/`ledger.py` pair
   covers the full governance lifecycle (~25 event classes spanning
   creation, attestation, gate checks, closeout, receipts, locks, renames,
   task state transitions) written to a single central
   `.gzkit/ledger.jsonl`. These are architecturally distinct surfaces, not
   overlapping implementations.
3. **Superset functionality.** Every capability opsdev's module provides
   already exists in gzkit in richer form: ~25-class discriminated union
   (`events.py:286-514`) vs opsdev's four audit classes; declarative
   `Field(..., pattern=...)` ID validators at the domain-model boundary
   (`core/models.py:25,41,147,168`) vs opsdev's `field_validator`/regex
   pair; nested evidence models with cross-field validation
   (`events.py:45,96,106,132`) vs opsdev's flat `EvidencePayload`
   (`extra="allow"`); `Ledger` class providing persistence, query,
   rename-chain resolution, gate-status derivation, artifact graph, and
   cache invalidation (`ledger.py:170-728`) — opsdev ships no
   persistence class.
4. **Storage doctrine conflict.** gzkit's state doctrine names a single
   canonical Layer 2 ledger as source of truth and explicitly prohibits
   derived views from silently becoming source-of-truth (`CLAUDE.md`
   § Architectural Boundaries item 6). A per-ADR `obpi-audit.jsonl`
   pattern would sit beside the canonical ledger and accrete governance
   facts that the central ledger does not see — exactly the drift vector
   the architecture memo calls out. Absorbing the pattern would require
   either migrating it into the central ledger (at which point it
   becomes duplicated semantics) or tolerating two sources of truth
   (which the doctrine forbids).
5. **No narrow idiom warrants standalone absorption.** In contrast to
   OBPI-0.25.0-27's `_safe_print` outcome (a narrow robustness helper
   absorbed as a surgical addition), `ledger_schema.py` exposes no
   standalone utility that gzkit lacks. The `ConfigDict(frozen=True)`
   discipline is a minor convention difference, but `extra="forbid"` plus
   append-only writes give gzkit the same practical immutability
   guarantee without a migration cost across ~25 event classes. The
   `create_timestamp` helper is one line that gzkit already inlines via
   `datetime.now(UTC).isoformat()` in `_EventBase.ts` default factories.
6. **Tooling layer vs consumer layer.** gzkit is governance *tooling*
   that downstream projects adopt to govern their own development. Its
   ledger surface must be general-purpose and serve as the canonical
   Layer 2 storage for any host project — hence the lifecycle-wide event
   stream. opsdev's `lib/ledger_schema.py` sits in the opposite position:
   it is an audit-layer schema internal to a domain application
   (airlineops operations), coupled to airlineops's decision to keep
   per-ADR audit logs alongside its own state. The brief's `ASSUMPTIONS`
   section names the subtraction test — "if it's not airline-specific,
   it belongs in gzkit" — and this module fails that test in a
   non-obvious way: the Python code is not airline-specific, but the
   *storage layout assumption* it encodes (per-ADR `logs/obpi-audit.jsonl`
   as a secondary surface) is a consumer-layer architectural choice that
   a tooling layer should not mandate on its adopters.

### Tracking the duplicate-evaluation signal

This brief is the second OBPI evaluating `lib/ledger_schema.py` across two
parent ADRs (OBPI-0.25.0-29 attested 2026-04-13, OBPI-0.26.0-05 in-flight).
The duplicate-OBPI surface is structurally identical to the
`lib/adr_governance.py` defect already tracked under **GHI #376** ("OBPI
absorption sweep authored two parallel OBPIs for the same source artifact
across two ADRs"). Same root cause: the ADR-0.26.0 authoring did not check
whether ADR-0.25.0's Phase-2 absorption sweep had already covered each
module in scope. Same proposed mitigation: the mechanical guard
`gz validate --absorption-duplicates` enumerated in GHI #376's "Tracking
impact" section would catch both instances.

Resolution: extend GHI #376 with this `lib/ledger_schema.py` second
instance via `gh issue comment` rather than file a parallel GHI. Root
cause and mitigation are identical; tracking unification keeps the
ADR-0.26.0 closeout-audit footprint single. The Exclude-by-reference
verdict here closes the in-flight duplicate; GHI #376 carries the
long-term tracking surface.

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Exclude decision validates that
gzkit's existing ledger surface is a functional superset and that opsdev's
storage-layout assumption would collide with gzkit doctrine — no new
commands, flags, output formats, or behavioral changes are introduced.

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded — ADR-0.26.0 checklist item #5 captured verbatim above (`OBPI Entry (Level 1 WBS)` line).
- [x] **Gate 2 (TDD):** N/A — Exclude outcome introduces no code or tests. `uv run gz test --obpi OBPI-0.26.0-05-ledger-schema` remains green because no source changed; vacuous pass on `[doc]` REQ pattern via `_synthesize_doc_proof_linkage`. Evidence captured in Stage 3 of the pipeline run.
- [x] **Gate 3 (Docs):** Decision rationale completed above (`## Decision`, six points + duplicate-evaluation tracking + Gate 4 N/A) with concrete capability, robustness, and storage-doctrine differences between opsdev and gzkit, anchored to current line ranges.
- [x] **Gate 4 (BDD):** N/A — the Exclude outcome introduces no operator-visible behavior change. `features/heavy_lane_gate4.feature` is not touched. Rationale: no CLI surface, no user-facing command, no ledger entry type, and no doc output is added, removed, or modified by this decision.
- [ ] **Gate 5 (Human):** Attestation recorded during Stage 4 ceremony of `gz-obpi-pipeline`.

### Implementation Summary



- Decision: Exclude — by reference to OBPI-0.25.0-29-ledger-schema-pattern (attested 2026-04-13). gzkit's ledger surface (`events.py` 556 L + `ledger.py` 728 L + `schemas/ledger.json` 318 L = 1,602 L total) is a functional superset of opsdev's `lib/ledger_schema.py` (501 L) for the gzkit problem (lifecycle event stream, central `.gzkit/ledger.jsonl`).
- Modules compared: opsdev `ledger_schema.py` (4 audit entry types: ObpiAuditEntry, CoversMapEntry, CoverageRunEntry, ReconciliationEntry; flat EvidencePayload; legacy `_infer_entry_type` shim) vs gzkit triad (~25 lifecycle event classes via TypedLedgerEvent discriminated union; nested evidence models with cross-field validation; Ledger persistence class with append/query/graph/rename-chain).
- Canonical precedent: OBPI-0.25.0-29-ledger-schema-pattern (Completed 2026-04-13) recorded **Exclude** with five-point rationale (architectural-scope mismatch, superset functionality, storage-doctrine conflict, no-narrow-idiom, tooling-vs-consumer distinction). This brief reproduces the rationale verbatim with refreshed line anchors (events.py 470→556 L, ledger.py 598→728 L; capability shape unchanged) plus a sixth point on the duplicate-OBPI surface.
- Source-material observation: brief Source Material header names `src/gzkit/ledger.py` (persistence-class surface only); actual comparison surface is the events.py + ledger.py + schemas/ledger.json triad. Recorded in body, parent-ADR-authored header not amended (mirror of OBPI-0.26.0-04 pattern).
- Duplicate-OBPI surface tracked under **GHI #376** — same source module evaluated twice across ADR-0.25.0/OBPI-29 (Exclude) and ADR-0.26.0/OBPI-05 (this brief, Exclude-by-reference). Resolution: extend GHI #376 with a second-instance comment, do not file parallel GHI.
- Brief-scaffold drift corrected in flight: ALL-CAPS section headings (`OBJECTIVE`, `ASSUMPTIONS`, `NON-GOALS`, `REQUIREMENTS (FAIL-CLOSED)`, `ALLOWED PATHS`, `QUALITY GATES (Heavy)`) renamed to title case; added missing `Lane`, `Denied Paths`, `Discovery Checklist` sections; corrected `status: Pending` (capital P) to allowed lowercase `pending`; renamed `Verification Commands (Concrete)` → `Verification` and added OBPI-specific `rg -n '^decision: Exclude' ...` command.
- Pre-existing tracked failure: `gz validate --documents --surfaces --brief-headings` fails on rule-placement (GHI #375); out of brief boundary; not blocking.
- No code absorbed; no `src/gzkit/` or `tests/` edits required.

### Key Proof



```bash
rg -n '^decision: Exclude|^\*\*Exclude\*\*' docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md
# Confirms brief frontmatter and ## Decision body record the Exclude verdict.

uv run gz covers OBPI-0.26.0-05-ledger-schema --json
# Expected: {"summary": {"total_reqs": 0, "uncovered_reqs": 0, ...}} — vacuous parity-gate pass for [doc] REQs via _synthesize_doc_proof_linkage.

uv run gz obpi validate --authored docs/design/adr/pre-release/ADR-0.26.0-governance-library-module-absorption/obpis/OBPI-0.26.0-05-ledger-schema.md
# Expected: OBPI Validation Passed.
```

ARB receipts (Stage 3): arb-ruff-6db021c78698482e8f022dd0c3a9029e, arb-step-typecheck-f4eabbe920564e73a62aff613c5e7d09, arb-step-unittest-5e8c640507c54a1dbeca6b7c99522039, arb-step-mkdocs-721706b840914e9f9398cc89b9ea988b. REQ→@covers parity: `gz covers OBPI-0.26.0-05-ledger-schema --json` → `uncovered_reqs: 0`. Pre-existing failure: `gz validate --documents --surfaces --brief-headings` fails on rule-placement (GHI #375 — not introduced here).

## Human Attestation

- Attestor: `Jeffry Babb`
- Date: 2026-05-01
- Attestation: attest completed — Exclude-by-reference to OBPI-0.25.0-29-ledger-schema-pattern (Completed/attested 2026-04-13) on identical opsdev source `lib/ledger_schema.py` (501 lines, govzero.ledger.v1, 4 audit entry types). Six-point rationale anchored on architectural-scope mismatch (per-ADR audit-only schema vs lifecycle-wide event stream), superset functionality (~25 typed event classes vs 4; declarative Field(..., pattern=...) ID validators at core/models.py:25,41,147,168 vs field_validator/regex pair; nested evidence models with cross-field validation at events.py:45,96,106,132 vs flat EvidencePayload; Ledger persistence class at ledger.py:170-728 that opsdev lacks entirely), storage-doctrine conflict (CLAUDE.md § Architectural Boundaries item 6 prohibits per-ADR derived storage from becoming source-of-truth), no-narrow-idiom warranting standalone absorption, tooling-vs-consumer distinction (consumer-layer storage-layout assumption a tooling layer should not mandate), and duplicate-OBPI surface (second instance of the GHI #376 root-cause defect). Refreshed gzkit anchors: events.py 470→556 L, ledger.py 598→728 L; capability shape unchanged. ARB receipts: ruff arb-ruff-6db021c78698482e8f022dd0c3a9029e, typecheck arb-step-typecheck-f4eabbe920564e73a62aff613c5e7d09, unittest arb-step-unittest-5e8c640507c54a1dbeca6b7c99522039, mkdocs arb-step-mkdocs-721706b840914e9f9398cc89b9ea988b. REQ→@covers parity gate green (uncovered_reqs=0; [doc] route via _synthesize_doc_proof_linkage). Pre-existing GHI #375 (validate --rule-placement) cited in evidence; not introduced by this brief. Heavy-lane Gate 5; no code under src/gzkit/ or tests/ modified — Gate 4 N/A documented inline. Brief-scaffold heading drift (ALL CAPS → title case, missing Lane/Denied Paths/Discovery Checklist) corrected in flight to satisfy `gz obpi validate --authored`.

### Closing Argument

**Exclude.** opsdev's `lib/ledger_schema.py` (501 lines) is an audit-only
Pydantic schema covering four entry types written to per-ADR
`logs/obpi-audit.jsonl` files — a consumer-layer audit extension specific
to airlineops's operational needs. gzkit's ledger surface — `events.py`
(556 L typed event models with ~25 lifecycle event classes), `ledger.py`
(728 L `Ledger` persistence class with append/read/query/graph/rename-chain
resolution/cache invalidation), and `schemas/ledger.json` (318 L
per-event JSON schema), 1,602 L total — is a functional superset for the
gzkit problem (lifecycle event stream, central `.gzkit/ledger.jsonl`).
Every capability opsdev provides — discriminated typed unions, ID
pattern validation, nested evidence models, legacy entry handling, frozen
models — gzkit provides in richer form, over more entry types, with a
persistence class and derivation pipeline opsdev does not ship.

Absorbing the opsdev module would not add capability; it would push a
consumer-layer storage-layout assumption (per-ADR `obpi-audit.jsonl`)
into the tooling layer, which collides with gzkit's Architectural
Boundary 6 ("derived views never silently become source-of-truth") and
the tooling-vs-consumer distinction. The subtraction test fails in a
non-obvious way: the Python code is not airline-specific, but the
storage-layout assumption it encodes is.

This brief is the second evaluation of `lib/ledger_schema.py` across two
parent ADRs; the canonical precedent is OBPI-0.25.0-29-ledger-schema-pattern
(attested 2026-04-13). Re-running the comparison with divergent rationale
on identical source material would itself be a doctrine-drift signal —
Exclude-by-reference is the structurally correct landing, with GHI #376
extended to track this second occurrence of the duplicate-OBPI defect so
the absorption sweep does not silently recur.
