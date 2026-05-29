---
id: ADR-pool.obpi-authoring-mechanical-floor
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: GHI #517
---

# ADR-pool.obpi-authoring-mechanical-floor: OBPI Authoring Mechanical Floor

## Status

Pool

## Intent

OBPI authoring has T2 emission paths that don't consult T1 validation. The default `gz specify` (no `--author`) path emits `obpi_created_event` at `src/gzkit/commands/specify_cmd.py:749` unconditionally — `_authored_validation_errors` is computed at line 817 but only acted on inside the `if author and authored_errors:` branch at line 835. The schema files (`src/gzkit/schemas/obpi.json` and `src/gzkit/schemas/obpi_brief_structure.json`) lack the `req_evidence` field that downstream closeout proof-binding (per `ADR-pool.closeout-ceremony-runtime-engine-parity` Decision item 4) will need to consume.

Surfaced by cross-analyst diagnosis in GHI #517. Lead Architect originally framed F5 as "`gz specify` emits regardless of validation"; Codex disputed the claim as overbroad; primary-source verification confirmed Codex right — the `--author` path DOES fail-close at line 840, but the default path emits without validation. See `artifacts/reports/ghi-517-cross-analyst-reconciliation.md` § Dispute D2.

### Absorbed findings

| ID | Surface | Defect |
|---|---|---|
| F5-revised | `specify_cmd.py:749` vs `:817-840` | Default `gz specify` emits `obpi_created` without consulting `_authored_validation_errors`. Only `--author` flag gates the ledger emission. |
| F6 | OBPI authoring SKILL prose | `gz validate --briefs --ground-truth` is SKILL-promised but not implemented as a mechanical validator on brief structure |
| F10 | `src/gzkit/schemas/obpi.json` + `src/gzkit/schemas/obpi_brief_structure.json` (Lead's `obpi_brief.json` path was wrong per Codex) | Neither schema has a `req_evidence` field; closeout proof-binding has no schema home for REQ↔receipt-ID payloads |

## Decision

1. **Make `--author` default behavior of `gz specify`.** The flag flips: `gz specify` runs authored validation by default and fail-closes on errors before ledger emission; a new `--unvalidated` flag preserves the current default-path behavior for genuine "scaffold-only" use cases (rare; warning emitted).
2. **~~Add `req_evidence` field to `obpi_brief_structure.json`.~~ RELOCATED to ADR-0.0.63 OBPI-0.0.63-03 (2026-05-29).** Canonical field key is **`ln`** (model `ReqEvidence`), shape `{req_id: str, receipt_ids: list[str], file_lines: list[str]}`. Optional at authoring time, required by `gz validate --closeout-proof-binding` at closeout time. Single-owner: the field exists only to serve closeout proof-binding (Decision item 5 of `ADR-pool.closeout-ceremony-runtime-engine-parity`, now promoted as ADR-0.0.63), so it is homed with its first consumer rather than here. This pool ADR retains items 1, 3, 4 (the `gz specify` authoring-gate work).
3. **Implement `gz validate --briefs --ground-truth`.** Mechanical validator over `BriefStructure` Pydantic model: REQ kinds present, Allowed Paths resolvable on disk, declared receipt-IDs match ledger events, parent ADR is non-Superseded. Fail-close at exit 3.
4. **Emit distinct events for validated vs unvalidated creation.** `obpi_created_validated` and `obpi_created_unvalidated` rather than overloading `obpi_created` — downstream gates can mechanically distinguish.

## Alternatives Considered

1. **Keep `gz specify` flag shape; run validation as a parallel CLI `gz obpi validate --authored` operator step.** Smaller diff; preserves backward compatibility. **Rejected:** identical class of failure to the `evaluate_adr` creation-time gap addressed by `ADR-pool.evaluation-gate-creation-time-extension` — relying on operator memory to run a separate gate is exactly the prose-vs-mechanics pattern this pool ADR exists to close.
2. **Add `req_evidence` to `obpi.json` only (not `obpi_brief_structure.json`).** Smaller schema surface. **Rejected:** `obpi_brief_structure.json` is the structural brief Pydantic schema; that's where REQ-kind-discipline (ADR-0.0.59) lives and is the natural home for REQ-bound evidence.

## Patterns surfaced

- **Prose-vs-mechanics.** Authoring validation exists as a code path but is gated by an opt-in flag — the SKILL prose tells the operator to run it; nothing mechanically requires it. Default-on flips the prose-mechanics relationship.
- **Tautological-test-surface (GHI #531).** Tests on `gz specify` currently assert that a file was created and contains certain strings; none assert that an *invalid* brief is rejected at the default path. REQ-derived assertions for the default-path validation gate are required as part of the implementation.

## Origin

`artifacts/reports/ghi-517-cross-analyst-reconciliation.md` §§ Dispute D2 (verified), F5-revised, F6, F10.
