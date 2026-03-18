# AUDIT (Gate-5) — ADR-0.15.0

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.15.0-pydantic-schema-enforcement |
| ADR Title | Pydantic Schema Enforcement |
| ADR Dir | docs/design/adr/pre-release/ADR-0.15.0-pydantic-schema-enforcement |
| Audit Date | 2026-03-18 |
| Auditor(s) | Agent (Claude Code) + Human |

## Feature Demonstration (Step 3 — MANDATORY)

**What does this ADR deliver?**

- All 14+ dataclass models migrated to Pydantic BaseModel v2+
- Declarative validation via Pydantic field validators, pattern constraints, and Literal types
- 12 typed ledger event models with discriminated union dispatch (eliminates manual event parsing)
- JSON Schema cross-validation: hand-authored schemas and Pydantic-generated schemas verified equivalent by 17 tests
- Zero behavioral regression — 588 tests pass, all existing `gz` commands work identically

### Capability 1: Core Model Migration

```
=== Capability 1: Core Model Migration ===
LedgerEvent base: (<class 'pydantic.main.BaseModel'>,)
model_dump: {'schema': 'gzkit.ledger.v1', 'event': 'test', 'id': 'test-id', 'ts': '2026-03-18T10:59:24.777989+00:00'}
Roundtrip: test

PathConfig base: (<class 'pydantic.main.BaseModel'>,)
  ledger: .gzkit/ledger.jsonl, manifest: .gzkit/manifest.json
  Total fields: 23

ValidationError base: (<class 'pydantic.main.BaseModel'>,)
  frozen: {'type': 'schema', 'artifact': 'test.md', 'message': 'test error', 'field': None}
  ValidationResult valid=False, errors=1
```

**Why it matters:** LedgerEvent, PathConfig, ValidationError, and ValidationResult are the foundational data types in gzkit. Migrating them to Pydantic means every governance record is now validated at construction time with structured error messages. `model_dump()`/`model_validate()` replace hand-written `to_dict()`/`from_dict()` across the codebase.

### Capability 2: Content-Type Frontmatter Models

```
=== Capability 2: Content-Type Frontmatter Models ===
Valid ADR: id=ADR-0.15.0, status=Proposed, lane=lite
Invalid ADR ID rejected: 1 error(s) — pattern validator
Valid OBPI: OBPI-0.15.0-01, parent=ADR-0.15.0, status=Completed
Invalid status rejected: 1 error(s) — Literal type
Invalid OBPI status rejected: 1 error(s) — enum constraint
Declarative Pydantic validators replace hand-written regex and enum checks
```

**Why it matters:** ADR, OBPI, and PRD frontmatter is now enforced by Pydantic pattern validators and Literal enums. Invalid IDs (e.g., `bad-id`) and invalid statuses (e.g., `Pending` for OBPI) are rejected at construction time with actionable error messages. Previously, these were hand-written regex checks in `validate.py`.

### Capability 3: Discriminated Union Event Dispatch

```
=== Capability 3: Discriminated Union Event Dispatch ===
AdrCreatedEvent: event=adr_created, lane=heavy
ObpiCreatedEvent: event=obpi_created
Discriminated dispatch: AdrCreatedEvent from raw dict
Typed event models: 12 total
Manual event-type dispatch eliminated — Pydantic discriminator resolves automatically
```

**Why it matters:** The ledger contains 12+ event types. Previously, parsing a raw ledger line required manual `if event == "adr_created"` dispatch. Now, `TypeAdapter(TypedLedgerEvent).validate_python(raw_dict)` automatically resolves to the correct typed model using Pydantic's discriminated union on the `event` field. Each event model validates its own fields.

### Capability 4: Schema Generation & Cross-Validation

```
=== Capability 4: Schema Generation & Cross-Validation ===
Hand-authored adr.json frontmatter fields: ['date', 'id', 'lane', 'parent', 'semver', 'status']
AdrFrontmatter Pydantic fields: ['date', 'id', 'lane', 'parent', 'semver', 'status']
Schema required: ['date', 'id', 'lane', 'parent', 'semver', 'status']
Pydantic required: ['id', 'status', 'semver', 'lane', 'parent', 'date']
Cross-validation tests: 17 tests enforce parity
Decision: Option B — hand-authored schemas and Pydantic models cross-validated by test invariant
```

**Why it matters:** The ADR decided on Option B (cross-validate) rather than replacing hand-authored schemas. Both sources are maintained. 17 cross-validation tests in `tests/test_schemas.py` enforce that the hand-authored JSON schemas and Pydantic-generated schemas agree on field names, required fields, and types. If either drifts, tests fail immediately.

### Value Summary

Before ADR-0.15.0, gzkit used Python dataclasses with 20+ hand-written validation functions scattered across `validate.py`. The lodestar document (AI-000) declared "Pydantic enforces at runtime" but the code didn't match. After this ADR, every structured data type is a Pydantic BaseModel with declarative validation, every ledger event resolves through discriminated unions, and schema parity is enforced by test — closing the largest gap between gzkit's stated architecture and its implementation.

---

## Execution Log

| Check | Command / Method | Result | Notes |
|-------|------------------|--------|-------|
| Unit tests | `uv run -m unittest -q` | ✓ 588 tests OK | `audit/proofs/unittest.txt` |
| Lint | `uv run gz lint` | ✓ All checks passed | Clean |
| Type check | `uv run gz typecheck` | ✓ All checks passed | Clean |
| Docs build | `uv run mkdocs build --strict` | ✓ Build clean | `audit/proofs/mkdocs.txt` |
| Gates | `uv run gz gates --adr ADR-0.15.0` | ✓ Gate 1 + Gate 2 PASS | `audit/proofs/gates.txt` |
| Config paths | `uv run gz check-config-paths` | ✓ Passed | Clean |
| CLI audit | `uv run gz cli audit` | ⚠ 1 issue | Missing link to `readiness-eval.md` — pre-existing, not ADR-0.15.0 scope |
| Ledger check | `uv run gz adr audit-check` | ⚠ Anchor drift + dirty worktree | All 4 OBPIs: metadata issues only, evidence intact |
| Capability 1: Core models | Python import + construction | ✓ All BaseModel | LedgerEvent, PathConfig, ValidationError, ValidationResult |
| Capability 2: Frontmatter | Construct valid/invalid | ✓ Rejects bad input | Pattern, Literal, required field validation working |
| Capability 3: Discriminated unions | TypeAdapter dispatch | ✓ 12 typed models | Correct type resolution from raw dict |
| Capability 4: Schema cross-validation | Compare fields | ✓ 17 tests enforce parity | Hand-authored and Pydantic schemas agree |

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ All 4 OBPIs completed, all features shipped |
| Code Quality | ✓ Lint, typecheck, 588 tests pass |
| Documentation Alignment | ✓ Lodestar AI-000 matches implementation |
| Schema Integrity | ✓ 17 cross-validation tests enforce parity |
| Risk Items Resolved | ⚠ Anchor drift + dirty worktree (non-blocking metadata) |

## Evidence Index

- `audit/proofs/unittest.txt` — 588 tests OK
- `audit/proofs/mkdocs.txt` — docs build clean
- `audit/proofs/gates.txt` — Gate 1 + Gate 2 PASS
- `audit/proofs/cli-audit.txt` — 1 pre-existing issue (readiness-eval.md link)
- `logs/obpi-audit.jsonl` — 8 ledger entries covering all 4 OBPI audits + attestations

## Shortfalls Identified

### Non-blocking (⚠)

1. **Completion anchor drift** — All 4 OBPIs report "completion anchor drifted in recorded OBPI scope." This is a metadata tracking issue in the receipt system, not a functional regression. The actual code, tests, and coverage are all verified.
   - **Severity:** Non-blocking
   - **Remedy:** Re-emit receipts after clean commit, or accept as historical artifact

2. **Dirty worktree receipts** — All 4 completion receipts were captured from a dirty worktree.
   - **Severity:** Non-blocking
   - **Remedy:** Same as above — re-emit or accept

3. **Brief metadata gaps** — OBPI-02 missing implementation summary and key proof in brief; all 4 briefs missing human attestation section.
   - **Severity:** Non-blocking (evidence exists in `obpi-audit.jsonl` ledger)
   - **Remedy:** Backfill brief metadata sections

4. **CLI audit: readiness-eval.md link** — Pre-existing issue, not in ADR-0.15.0 scope.
   - **Severity:** Non-blocking
   - **Remedy:** Address in separate maintenance task

### Blocking (✗)

None.

## Attestation

I/we attest that ADR-0.15.0 (Pydantic Schema Enforcement) is implemented as intended, evidence is reproducible, and no blocking discrepancies remain.

Signed: ___________________________  Date: ___________
