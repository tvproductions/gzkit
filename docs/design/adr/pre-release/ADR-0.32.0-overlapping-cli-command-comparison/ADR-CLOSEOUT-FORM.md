# ADR Closeout Form: ADR-0.32.0-overlapping-cli-command-comparison

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
| Gate 1 | ADR exists | `docs/design/adr/pre-release/ADR-0.32.0-overlapping-cli-command-comparison/ADR-0.32.0-overlapping-cli-command-comparison.md` |
| Gate 2 (TDD) | Tests pass | `uv run gz test` |
| Gate 3 (Docs) | Docs build | `uv run mkdocs build --strict` |
| Gate 5 (Attestation) | Human sign-off | Closeout ceremony |

## OBPI Status

| OBPI | Description | Status |
|------|-------------|--------|
| OBPI-0.32.0-01 | Compare `git-sync` (opsdev 682 vs gzkit 199 lines) | Pending |
| OBPI-0.32.0-02 | Compare `lint` | Pending |
| OBPI-0.32.0-03 | Compare `format` | Pending |
| OBPI-0.32.0-04 | Compare `test` | Pending |
| OBPI-0.32.0-05 | Compare `typecheck` | Pending |
| OBPI-0.32.0-06 | Compare `check-config-paths` | Pending |
| OBPI-0.32.0-07 | Compare `cli-audit` | Pending |
| OBPI-0.32.0-08 | Compare `tidy/clean` | Pending |
| OBPI-0.32.0-09 | Compare `gates` | Pending |
| OBPI-0.32.0-10 | Compare `implement` | Pending |
| OBPI-0.32.0-11 | Compare `closeout` | Pending |
| OBPI-0.32.0-12 | Compare `audit` | Pending |
| OBPI-0.32.0-13 | Compare `attest` | Pending |
| OBPI-0.32.0-14 | Compare `status/state` | Pending |
| OBPI-0.32.0-15 | Compare `adr status/docs/map/check` | Pending |
| OBPI-0.32.0-16 | Compare `adr recon/audit-check/emit-receipt` | Pending |
| OBPI-0.32.0-17 | Compare `adr evidence/autolink/sync/promote` | Pending |
| OBPI-0.32.0-18 | Compare `adr eval/report` | Pending |
| OBPI-0.32.0-19 | Compare `docs/docs-lint/md-lint/md-fix/md-tidy` | Pending |
| OBPI-0.32.0-20 | Compare `sync-repo` | Pending |
| OBPI-0.32.0-21 | Compare `sync-agents-skills/sync-claude-skills` | Pending |
| OBPI-0.32.0-22 | Compare `layout-verify` | Pending |
| OBPI-0.32.0-23 | Evaluate `cwd-guard` (opsdev only) | Pending |
| OBPI-0.32.0-24 | Evaluate `yaml-guard` (opsdev only) | Pending |
| OBPI-0.32.0-25 | Compare `hooks subcommands` | Pending |

## Attestation

**Human Approver:** ___________________________

**Date:** ___________________________

**Decision:** Accept | Request Changes
