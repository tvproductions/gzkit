# Plan: OBPI-0.25.0-31 Validation Receipts Pattern

## Context

OBPI-0.25.0-31 is a **comparison/decision OBPI** under ADR-0.25.0
(Core Infrastructure Pattern Absorption). It evaluates
`airlineops/src/opsdev/lib/validation_receipt.py` (274 lines, validation
anchoring schema) against gzkit's existing receipt surface and produces one
of three outcomes: **Absorb**, **Confirm**, or **Exclude**.

This is the same pattern as the 30 already-completed sibling OBPIs in the
ADR (e.g. OBPI-0.25.0-29 ledger-schema, -30 references). The deliverable is
a brief update — no source code changes — unless the decision is `Absorb`.

The plan below is grounded in the comparison evidence I gathered before
entering plan mode (file reads of both surfaces are documented in the
Comparison Evidence section).

## Decision (recommended): Confirm

gzkit's receipt surface is architecturally a strict superset of airlineops's
`validation_receipt.py`. No absorption is warranted. The brief will record
`Confirm` with concrete capability differences cited.

## Comparison Evidence

### airlineops/src/opsdev/lib/validation_receipt.py (274 lines)

- `ValidationAnchor` Pydantic BaseModel — `commit` (regex `^[0-9a-f]{7,40}$`),
  `tag` (optional), `semver` — frozen, extra=forbid
- `ValidationReceipt` extending `LedgerEntryBase` — `type=Literal["validation"]`,
  `adr_id` (regex-validated via shared `ADR_ID_PATTERN`), `event` Literal in
  {validated, completed, compliance_check}, `anchor`, `evidence: dict[str,Any]`,
  `attestor` (field validator forces `human:<name>` prefix)
- `write_receipt(receipt, ledger_path)` — JSONL append, `mkdir(parents=True)`
- `read_receipts(ledger_path, *, adr_id=None)` — read+parse with malformed-line
  warnings, optional ADR filter
- `get_current_anchor(semver)` — `git rev-parse HEAD` + `git describe
  --exact-match --tags HEAD` (raises `RuntimeError` on git failure)
- `emit_validation_receipt(adr_id, event, evidence, attestor, *, ledger_path=None)`
  — high-level builder, defaults to `{adr-folder}/logs/adr-validation.jsonl`
- 3 fixed event types
- Per-ADR ledger storage (one ledger file per ADR folder)

### gzkit equivalent surface (~1396 lines distributed)

| File | Lines | Role |
|---|---|---|
| `src/gzkit/events.py` | 470 | 17+ typed event models (discriminated union over `event`); `_EventBase`, `AuditReceiptEmittedEvent`, `ObpiReceiptEmittedEvent`, `ObpiReceiptEvidence`, `ScopeAudit`, `GitSyncState`, `ReqProofInput` |
| `src/gzkit/ledger_semantics.py` | 547 | semantic model dispatch and validation orchestration |
| `src/gzkit/validate_pkg/ledger_check.py` | 379 | ledger validation |
| `src/gzkit/utils.py:64-105` | 42 | `capture_validation_anchor_with_warnings` / `capture_validation_anchor` — degraded fallback `{commit:"0000000", semver:"0.0.0"}` instead of raising |
| `src/gzkit/temporal_drift.py` | (whole file) | drift classifier — already absorbed via OBPI-0.25.0-26; consumes anchors from gzkit ledger |
| `src/gzkit/commands/obpi_complete.py:186` | — | atomic OBPI completion that builds anchor + emits `obpi_receipt_emitted` event |

ADR-ID and OBPI-ID patterns are enforced via Pydantic
`Field(pattern=...)` in `core/models.py:37,140`.

### Dimension comparison

| Dimension | airlineops | gzkit | Notes |
|---|---|---|---|
| Anchor schema typing | `ValidationAnchor` Pydantic with regex SHA validation | `dict[str, str] \| None` on event models | airlineops typed; gzkit untyped |
| Anchor capture robustness | Raises `RuntimeError` on git failure | Degraded fallback + warnings | gzkit graceful degradation |
| Receipt event variety | 3 fixed Literals | 17+ lifecycle event types | gzkit strictly larger |
| Evidence model | `dict[str, Any]` | `ObpiReceiptEvidence` with nested `ScopeAudit`, `GitSyncState`, `ReqProofInput` | gzkit strictly richer |
| Attestor enforcement | Model-level `human:` prefix validator | Downstream `requires_human` flow in `obpi_complete.py` | both enforce, different layer |
| ADR ID validation | Field validator | Pattern in `core/models.py:37,140` | tie |
| Storage architecture | Per-ADR `{adr}/logs/adr-validation.jsonl` | Central `.gzkit/ledger.jsonl` | architectural mismatch — gzkit uses single-ledger model |
| Drift consumption | Has `drift_detection.py` | Already absorbed as `temporal_drift.py` (OBPI-0.25.0-26) | tie |
| CLI integration | None | `gz obpi complete`, `gz adr emit-receipt`, `gz obpi reconcile` | gzkit only |
| Atomic transaction | None | `_execute_transaction` in `obpi_complete.py` | gzkit only |

### Conclusion

The single narrow win for airlineops — typed `ValidationAnchor` instead of
`dict[str, str]` — is not worth absorbing because:

1. It would require migrating every existing event in the gzkit ledger schema
   (anchor field is shared across `AuditReceiptEmittedEvent` and
   `ObpiReceiptEmittedEvent`), which is its own OBPI in scope
2. Pattern OBPIs in this ADR have consistently chosen `Confirm` when gzkit's
   surface is architecturally larger (see OBPI-0.25.0-29 ledger-schema receipt
   note in `.claude/plans/.plan-audit-receipt.json`)
3. The architectural mismatch (per-ADR vs central ledger) means a literal
   absorption would create a parallel storage system, not strengthen the
   existing one

Decision: **Confirm**.

## Files to be modified

Only one file:

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-31-validation-receipts-pattern.md`

This is within the brief's `## ALLOWED PATHS`.

## Implementation steps

### 1. Document Comparison and Decision in Brief

Append three sections to the brief:

1. **Comparison** — the dimension table above, with the airlineops file
   reference and the gzkit file references (events.py, utils.py:64-105,
   temporal_drift.py, obpi_complete.py:186, etc.)
2. **Decision: Confirm** — one-paragraph rationale citing the architectural
   superset relationship and naming the three reasons absorption is not warranted
3. **Closing Argument** — fill in the placeholder section with the same
   Confirm rationale framed as the closing argument

### 2. Mark Completion Checklist

Tick the Heavy lane checklist:

- [x] Gate 1 (ADR): Intent recorded — already true
- [x] Gate 2 (TDD): Tests pass — `gz test` will be re-run in Stage 3
- [x] Gate 3 (Docs): Decision rationale completed — done by step 1
- [x] Gate 4 (BDD): N/A — no operator-visible behavior change; record N/A
  rationale in the brief
- [x] Gate 5 (Human): Attestation recorded — happens in pipeline Stage 4

Tick the Acceptance Criteria boxes:

- REQ-0.25.0-31-01: `Confirm` recorded
- REQ-0.25.0-31-02: rationale cites concrete capability differences
- REQ-0.25.0-31-03: N/A (no `Absorb`)
- REQ-0.25.0-31-04: explained
- REQ-0.25.0-31-05: N/A recorded with rationale

Tick the Quality Gates table boxes accordingly.

### 3. Update YAML frontmatter

Change `status: Pending` to `status: Completed` (or whatever
`gz obpi complete` expects — the command rewrites this as part of the
atomic transaction in Stage 5, so step 3 may be unnecessary; verify by
reading `obpi_complete.py:_build_new_content` before touching frontmatter
manually). **Default plan:** leave frontmatter alone and let
`gz obpi complete` rewrite it atomically.

## Verification (Stage 3)

The brief's verification commands:

```bash
test -f ../airlineops/src/opsdev/lib/validation_receipt.py    # source exists
test -f src/gzkit/events.py                                    # target exists
rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-31-validation-receipts-pattern.md
                                                              # decision recorded
uv run gz test                                                 # baseline green
# behave only if operator-visible behavior changed — N/A here
```

Pipeline baseline checks:

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents      # Heavy lane
uv run mkdocs build --strict        # Heavy lane
uv run gz covers OBPI-0.25.0-31-validation-receipts-pattern --json
                                    # REQ→@covers parity (Phase 1b)
```

REQ → @covers parity is the only risk: this is a brief-only OBPI with no
test code, so REQ coverage is satisfied by **prose** in the brief itself
rather than by `@covers` decorators in tests. If `gz covers` reports
uncovered REQs, the workaround is the same one used by the prior 30 sibling
OBPIs in this ADR — which I will inspect during Stage 3 if the gate fails.

## Stage 4 + 5

Standard pipeline ceremony and sync — no special handling.

## Risks

1. **REQ→@covers parity gate may fail.** Brief-only OBPIs have no test code.
   Mitigation: inspect a recently-completed sibling (e.g. OBPI-0.25.0-30) to
   see how it satisfied the gate, then mirror that approach.
2. **Frontmatter rewriting.** `gz obpi complete` may expect specific brief
   structure. Mitigation: leave frontmatter alone; let the command rewrite
   atomically.

## What this plan does NOT do

- Does not write any Python code
- Does not modify `events.py`, `utils.py`, or any other source file
- Does not migrate the anchor field from `dict[str, str]` to a typed model
  (that is a separate OBPI if ever scoped)
- Does not touch any file outside the brief's ALLOWED PATHS
