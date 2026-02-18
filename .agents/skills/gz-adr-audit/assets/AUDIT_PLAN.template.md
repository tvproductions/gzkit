# AUDIT PLAN TEMPLATE (Gate-5) — Replace Placeholders

| Field | Value |
| ----- | ----- |
| ADR ID | {{ADR_ID}} |
| ADR Title | {{ADR_TITLE}} |
| SemVer | {{SEMVER}} |
| ADR Dir | {{ADR_DIR}} |
| Audit Date | {{AUDIT_DATE}} |
| Auditor(s) | {{AUDITORS}} |

## Purpose

Confirm {{ADR_ID}} implementation is complete by validating its claims with reproducible CLI evidence.

**Audit Trigger:** (e.g., post-implementation stability check, pre-release confirmation, Gate-5 validation)

## Scope & Inputs

**Primary contract surfaces:**

List the specific CLI commands, reporter surfaces, or behaviors that this ADR introduces or modifies.

Example (adapt to ADR):

- `uv run -m airlineops reporter <feature> ...`
- Config sources: `config/settings.json`, `config/calendars.json`
- Registry/manifest: `data/data_sources.json`

**System health surfaces (use when relevant):**

- `uv run -m airlineops reporter status`
- `uv run -m airlineops reporter contract horizon`
- `uv run -m airlineops reporter manifest status`
- `uv run -m airlineops reporter registrar --format console`

## Planned Checks

| Check | Command / Method | Expected Signal | Status (Planned) |
|-------|------------------|-----------------|------------------|
| (ADR-specific check 1) | (command) | (expected outcome) | Pending |
| (ADR-specific check 2) | (command) | (expected outcome) | Pending |
| Docs build (if docs changed) | `uv run mkdocs build -q -f mkdocs.yml` | Build clean | Pending |
| Markdown lint (if docs changed) | `uv run -m opsdev md-docs` | Zero violations | Pending |
| (Add more checks as needed) | | | Pending |

## Risk Focus

Highlight higher-risk seams (e.g., new flags, calendar normalization, receipt immutability).

## Findings Placeholder

Will be captured in `AUDIT.md` — do not populate here beyond structural notes.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `{{ADR_DIR}}/audit/proofs/` and referenced in `audit/AUDIT.md` (co-located, committed).
- ADR present in index/status with correct state; backlinks maintained when applicable.
- No edits to accepted ADR prose; hygiene via follow-up ADR if required.

## Attestation Placeholder

Human will complete in `AUDIT.md` with final ✓ summary.
