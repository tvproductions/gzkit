# OBPI-0.25.0-29 — Ledger Schema Pattern (Absorb/Confirm/Exclude)

## Context

OBPI-0.25.0-29 is a Heavy-lane evaluation brief in the ADR-0.25.0 series
"core-infrastructure-pattern-absorption". Each brief in this series walks one
airlineops module and records one of {Absorb, Confirm, Exclude} against the
gzkit equivalent. This one evaluates `airlineops/src/opsdev/lib/ledger_schema.py`
(501 lines) against gzkit's ledger-schema surface distributed across
`src/gzkit/events.py` (470 lines), `src/gzkit/ledger.py` (598 lines), and
`src/gzkit/schemas/ledger.json` (220 lines).

The brief is documentation-only if the outcome is Confirm or Exclude, and
becomes code + tests only if the outcome is Absorb. Based on the pre-plan
comparison summarised below, the evidence points to **Exclude** (architectural
scope mismatch), which means no src/ or tests/ edits — only the brief file
itself.

## Comparison Summary (established in exploration)

| Dimension | airlineops ledger_schema.py | gzkit events.py + ledger.py + schemas/ledger.json |
| --- | --- | --- |
| Purpose | Audit-only schema for per-ADR `obpi-audit.jsonl` logs | Lifecycle-wide event stream for central `.gzkit/ledger.jsonl` |
| Schema version | `govzero.ledger.v1` | `gzkit.ledger.v1` |
| Storage location | `docs/design/adr/{series}/{adr}/logs/obpi-audit.jsonl` (per-ADR) | `.gzkit/ledger.jsonl` (single central ledger) |
| Entry/event types | 4: `obpi-audit`, `covers-map`, `coverage-run`, `reconciliation` | 17+: `project_init`, `prd_created`, `constitution_created`, `obpi_created`, `adr_created`, `artifact_edited`, `attested`, `gate_checked`, `closeout_initiated`, `audit_receipt_emitted`, `obpi_receipt_emitted`, `artifact_renamed`, `adr_annotated`, `lifecycle_transition`, `task_started`, `task_completed`, `task_blocked`, `task_escalated` |
| Discriminator field | `type` | `event` |
| Discriminated union | `LedgerEntry = ObpiAuditEntry \| CoversMapEntry \| CoverageRunEntry \| ReconciliationEntry` | `TypedLedgerEvent` over 17 event classes via `TypeAdapter` (`events.py:443-465`) |
| ID pattern validation | `OBPI_ID_PATTERN`, `ADR_ID_PATTERN` as `field_validator`s | Pydantic `Field(pattern=...)` on OBPI models in `core/models.py:37,140` |
| Nested evidence models | `EvidencePayload` (tests_found, coverage_*, docs_found, ...) | `ReqProofInput`, `ScopeAudit`, `GitSyncState`, `ObpiReceiptEvidence` with cross-field validation (`events.py:45-205`) |
| Legacy entry handling | `_infer_entry_type()` for entries missing `type` | Not needed — all gzkit events emit `event` discriminator |
| `frozen=True` | Applied to every model | Applied to `_EventBase` only via `extra="forbid"`; not `frozen=True` — but events are never mutated post-append (append-only `Ledger.append()`) |
| Persistence class | None — schema module only | `Ledger` class (`ledger.py:133-565`) with append/read/query/graph derivation + cache invalidation |
| Validator functions | `validate_ledger_entry`, `is_valid_ledger_entry`, `parse_ledger_entry`, `create_timestamp` | `parse_typed_event` + structured Pydantic errors + `pydantic_loc_to_field_path` helper |

## Preliminary Decision — Exclude (rationale)

The airlineops `ledger_schema.py` and gzkit's ledger surface solve different
problems at different layers:

1. **Scope mismatch.** airlineops's schema covers audit-only entry types
   (`obpi-audit`, `covers-map`, `coverage-run`, `reconciliation`) written to
   per-ADR `logs/obpi-audit.jsonl` files. gzkit's `events.py` covers the full
   governance lifecycle — creation, attestation, gate checks, closeout,
   receipts, renames, task state transitions — written to a central
   `.gzkit/ledger.jsonl`. These are architecturally distinct surfaces, not
   overlapping implementations.
2. **Superset functionality.** Every capability airlineops's module provides
   (typed event models, discriminated union, validation, timestamp helper,
   pattern validation) already exists in gzkit in richer form:
   - Typed union over **17+** event types vs airlineops's **4** entry types
   - Pydantic `pattern` field constraints in `core/models.py:37,140` already
     enforce OBPI/ADR ID format at the model boundary
   - Nested evidence models (`ObpiReceiptEvidence`, `ScopeAudit`, `GitSyncState`,
     `ReqProofInput`) with cross-field validation surpass airlineops's flat
     `EvidencePayload`
   - `Ledger` class provides append, query, graph derivation, rename
     canonicalisation, and cache invalidation that airlineops lacks
3. **Storage doctrine conflict.** Absorbing airlineops's per-ADR audit-log
   pattern would collide with gzkit's state doctrine (Layer 2 ledger as single
   source of truth). gzkit's architecture memo prohibits derived views from
   silently becoming source-of-truth — a per-ADR audit log would be exactly
   that drift vector.
4. **No narrow absorption warranted.** In contrast to OBPI-27's
   `_safe_print` case (a narrow robustness idiom that was absorbed), this
   module exposes no standalone utility that gzkit lacks. The `frozen=True`
   discipline is a minor convention difference, but `extra="forbid"` plus
   append-only writes already give gzkit the same practical immutability
   guarantee without a migration cost across 17 event classes.

Decision: **Exclude**. Rationale: architectural scope mismatch and storage
doctrine divergence, not capability gaps. gzkit's ledger surface is a
functional superset for the lifecycle-ledger problem, and airlineops's
audit-only schema targets a storage layout gzkit deliberately does not adopt.

## Critical Files

- **Edit:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-29-ledger-schema-pattern.md`
  - Status frontmatter: `Pending` → (remain `Pending`; `gz obpi complete` flips to `Completed` atomically in Stage 5)
  - Add `## Comparison Evidence` table
  - Add `## Decision: Exclude` section with rationale (cites the 4 points above and concrete file:line anchors)
  - Check Gate 1, 2 (N/A — no code change), 3 (decision recorded), 4 (N/A rationale — no operator-visible behavior change), 5 (deferred to Stage 4 attestation)
  - Fill in Completion Checklist
  - Write `## Closing Argument` grounded in the comparison evidence
- **Read (evidence):** `../airlineops/src/opsdev/lib/ledger_schema.py`,
  `src/gzkit/events.py`, `src/gzkit/ledger.py`, `src/gzkit/schemas/ledger.json`,
  `src/gzkit/core/models.py`

## Plan Steps

1. **Edit the brief** — add the `## Comparison Evidence` table and `## Decision: Exclude` narrative to `OBPI-0.25.0-29-ledger-schema-pattern.md`. Record Gate 2 as N/A (no code change), Gate 3 decision, Gate 4 N/A with rationale, Gate 5 deferred. Fill the Completion Checklist and Closing Argument.
2. **Verify brief regex** — `rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-29-ledger-schema-pattern.md` must find the decision line.
3. **Run baseline quality gates** — `uv run gz lint`, `uv run gz typecheck`, `uv run gz test`, `uv run gz validate --documents`, `uv run mkdocs build --strict`. All must pass. No source was modified so regressions are not expected, but Heavy lane requires the full check surface.
4. **REQ parity gate** — `uv run gz covers OBPI-0.25.0-29-ledger-schema-pattern --json`. Expected: the brief is comparison/decision, not code — verify whether the covers gate considers this brief parity-applicable. If parity is required for all 5 REQs and no test coverage exists, investigate whether REQ-0.25.0-29-0* decisions are supposed to be covered by a generic absorption-ceremony test or by `N/A` brief metadata (this is the one open question and may need a narrow `@covers` addition in an existing test — defer decision until parity output is read).
5. **Stage 4 ceremony** — present the comparison table, the Exclude decision, Gate 4 N/A rationale, and acceptance criteria mapping. Wait for human attestation (Heavy lane, non-Exception mode).
6. **Stage 5 sync** — `uv run gz obpi complete OBPI-0.25.0-29-ledger-schema-pattern --attestor "<operator>" --attestation-text "<user words + enrichment>"`, release lock, git-sync #1, `uv run gz obpi reconcile`, `uv run gz adr status ADR-0.25.0 --json`, git-sync #2.

## Verification

- `rg -n 'Decision.*Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-29-ledger-schema-pattern.md` → matches the decision line
- `uv run gz test` → all tests pass (no code changed)
- `uv run gz lint` / `uv run gz typecheck` → clean (no code changed)
- `uv run gz validate --documents` → brief validates against doc schema
- `uv run mkdocs build --strict` → doc site builds clean
- `uv run gz covers OBPI-0.25.0-29-ledger-schema-pattern --json` → REQ parity satisfied (see Plan Step 4 — may need narrow test annotation)
- `uv run gz obpi reconcile OBPI-0.25.0-29-ledger-schema-pattern` → brief state agrees with receipt after completion

## Open Question (to flag during Stage 3)

The REQ→`@covers` parity gate (#113) applies to every REQ in every brief. For a documentation-only comparison brief with no code change, REQs 01-05 are satisfied by the brief content itself, not by runnable tests. If `gz covers` fails parity, the remediation is one of:
- Add a thin test under `tests/test_adr_0_25_0_absorption_decisions.py` (or similar) that asserts the brief contains `Decision: Exclude` and carries `@covers REQ-0.25.0-29-01..05` decorators — this is the airlineops precedent for documentation briefs
- Or check whether the covers command has a `--brief-only` mode that exempts doc-only REQs

Will determine which during Stage 3 Phase 1b when `gz covers` output is observed. This is the only execution-time unknown.

## Risk Assessment

- **Low technical risk:** no src/ or tests/ edits if Exclude holds
- **Low reversibility risk:** brief-only edit; a second comparison pass could Absorb instead, but the architectural mismatch is structural, not stylistic
- **Ceremony risk:** Heavy lane requires human attestation — Stage 4 will wait for operator response
- **Parity gate unknown** (see open question above) — may add one test annotation
