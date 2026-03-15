# ADR Closeout Form: ADR-0.17.0

**Status**: Phase 2 — Completed

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass
- [ ] Gate 3 (Docs): Docs build passes
- [ ] Gate 4 (BDD): Behave suite passes
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir/ADR-0.17.0-agentsmd-tidy-control-surface-schema-and-rules-mir.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Quality (Lint) | Lint passes | `uv run gz lint` |
| Quality (Typecheck) | Typecheck passes | `uv run gz typecheck` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 4 (BDD) | BDD passes | `uv run -m behave features/` |
| Gate 5 | Human attests | `uv run gz attest ADR-0.17.0 --status completed` |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| [OBPI-0.17.0-01-categorized-skill-catalog](OBPI-0.17.0-01-categorized-skill-catalog.md) | Categorized Skill Catalog | Pending |
| [OBPI-0.17.0-02-rules-mirroring](OBPI-0.17.0-02-rules-mirroring.md) | Rules Mirroring | Pending |
| [OBPI-0.17.0-03-slim-claudemd-template](OBPI-0.17.0-03-slim-claudemd-template.md) | Slim CLAUDE.md Template | Pending |
| [OBPI-0.17.0-04-json-schemas-and-validation](OBPI-0.17.0-04-json-schemas-and-validation.md) | JSON Schemas and Validation | Pending |
| [OBPI-0.17.0-05-manifest-update-and-final-sync](OBPI-0.17.0-05-manifest-update-and-final-sync.md) | Manifest Update and Final Sync | Pending |

## Human Attestation

### Verbatim Attestation

- `completed: Retroactive attestation: work completed via superpowers plan execution with all quality gates passing (lint, typecheck, test, 447 tests OK). Booked retroactively via gz superbook.`

**Attested by**: Test User
**Timestamp (UTC)**: 2026-03-15T18:44:42Z
