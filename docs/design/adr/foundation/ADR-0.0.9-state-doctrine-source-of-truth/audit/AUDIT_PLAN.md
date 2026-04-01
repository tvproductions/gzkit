# AUDIT PLAN (Gate-5) — ADR-0.0.9

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.9 |
| ADR Title | State Doctrine and Source-of-Truth Hierarchy |
| SemVer | 0.0.9 |
| ADR Dir | docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth |
| Audit Date | 2026-03-31 |
| Auditor(s) | jeff |

## Purpose

Confirm ADR-0.0.9 implementation is complete by validating its claims with reproducible CLI evidence.

**Audit Trigger:** Post-attestation Gate-5 validation to advance lifecycle from Completed to Validated.

## Scope & Inputs

**Primary contract surfaces:**

- `uv run gz state` — state query and display
- `uv run gz state --repair` — force-reconciliation of frontmatter from ledger
- `src/gzkit/ledger_semantics.py` — ledger-first status derivation
- `src/gzkit/sync.py` — frontmatter reconciliation
- `src/gzkit/pipeline_markers.py` — Layer 3 runtime state

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| Ledger-first status reads | `uv run gz state --json` | Status derived from ledger, not frontmatter | Pending |
| State repair command | `uv run gz state --repair` | Frontmatter reconciled from ledger | Pending |
| Layer 3 gate independence | `uv run gz gates --adr ADR-0.0.9` | Gates pass without L3 artifacts | Pending |
| Lifecycle auto-fix | Inspect closeout/attest code paths | Frontmatter updated at lifecycle moments | Pending |
| Three-layer model docs | `uv run mkdocs build -q` | Docs build clean, state doctrine documented | Pending |
| Unit tests | `uv run -m unittest -q -k test_state_doctrine` | All state doctrine tests pass | Pending |
| Ledger completeness | `uv run gz adr audit-check ADR-0.0.9` | All 6 OBPIs completed with evidence | Pending |

## Risk Focus

- Commands that read frontmatter as authoritative instead of ledger
- Layer 3 artifacts that could block gate checks
- `--repair` flag not being discoverable via `--help`

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under ADR dir `audit/proofs/` and referenced in `audit/AUDIT.md`.
- No edits to accepted ADR prose.

## Attestation Placeholder

Human will complete in `AUDIT.md` with final ✓ summary.
