# ADR Closeout Form: ADR-0.35.0-pre-commit-hook-absorption

**Status**: Not Started

---

## Pre-Attestation Checklist

Closeout evidence verified:

- [ ] All checklist items in ADR are complete
- [ ] All OBPIs have passing acceptance criteria
- [ ] Gate 2 (TDD): Tests pass (`uv run gz test`)
- [ ] Gate 3 (Docs): Docs build passes (`uv run mkdocs build --strict`)
- [ ] Code reviewed

## Evidence Paths

| Gate | Evidence | Command/Path |
|------|----------|--------------|
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.35.0-pre-commit-hook-absorption/ADR-0.35.0-pre-commit-hook-absorption.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 5 (Attestation) | Human sign-off | Closeout ceremony |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| OBPI-0.35.0-01 | Evaluate `arb-ruff` | Pending |
| OBPI-0.35.0-02 | Evaluate `ruff-format` | Pending |
| OBPI-0.35.0-03 | Evaluate `ty-check` | Pending |
| OBPI-0.35.0-04 | Evaluate `unittest` | Pending |
| OBPI-0.35.0-05 | Evaluate `arb-validate` | Pending |
| OBPI-0.35.0-06 | Evaluate `xenon-complexity` | Pending |
| OBPI-0.35.0-07 | Evaluate `protect-copilot-instructions` | Pending |
| OBPI-0.35.0-08 | Evaluate `forbid-pytest` | Pending |
| OBPI-0.35.0-09 | Evaluate `normalize-adr-h1` | Pending |
| OBPI-0.35.0-10 | Evaluate `generate-adr-docs` | Pending |
| OBPI-0.35.0-11 | Evaluate `forbid-prod-db-in-tests` | Pending |
| OBPI-0.35.0-12 | Evaluate `cross-platform-sqlite-guard` | Pending |
| OBPI-0.35.0-13 | Evaluate `validate-manpages` | Pending |
| OBPI-0.35.0-14 | Evaluate `sync-manpage-docstrings` | Pending |
| OBPI-0.35.0-15 | Evaluate `interrogate` | Pending |
| OBPI-0.35.0-16 | Evaluate `check-todos-fixmes` | Pending |
| OBPI-0.35.0-17 | Evaluate `md-docs` | Pending |
| OBPI-0.35.0-18 | Evaluate `repo-canonicalization` | Pending |
| OBPI-0.35.0-19 | Evaluate `sync-claude-skills` | Pending |
| OBPI-0.35.0-20 | Evaluate `adr-drift-check` | Pending |

## Attestation

**Human Approver:** ___________________________

**Date:** ___________________________

**Decision:** Accept | Request Changes
