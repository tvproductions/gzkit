# Audit: ADR-0.22.0-task-level-governance

- ADR: `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/ADR-0.22.0-task-level-governance.md`
- Generated: 2026-03-28

## Attestation Record
- Attestor: Jeff
- Status: completed
- Timestamp: 2026-03-28T11:31:21.059099+00:00

## Gate Results (from ledger)
| Gate | Status | Command | Return Code |
|------|--------|---------|-------------|
| 1 | pass | `ADR exists` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `eval-delta` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |

## OBPI Completion Summary
| OBPI | Receipt Event | Completed |
|------|---------------|-----------|
| OBPI-0.22.0-01-define-task-entity-format-and-identifier-scheme-e-g-task-semver-obpi-req-seq | — | No |
| OBPI-0.22.0-01-task-entity-model | completed | Yes |
| OBPI-0.22.0-02-define-task-level-ledger-events-task-started-task-completed-task-blocked-task-escalated | — | No |
| OBPI-0.22.0-02-task-ledger-events | completed | Yes |
| OBPI-0.22.0-03-define-git-commit-linkage-contract-task-id-in-commit-message-traceable-to-req-obpi-adr | — | No |
| OBPI-0.22.0-03-git-commit-linkage | completed | Yes |
| OBPI-0.22.0-04-define-the-intermeshing-contract-with-superpowers-how-superpowers-behavioral-methodology-anti-rationalization-red-green-refactor-circuit-breakers-maps-to-task-level-governance-events | — | No |
| OBPI-0.22.0-04-gz-task-cli | completed | Yes |
| OBPI-0.22.0-05-add-cli-surfaces-for-task-lifecycle-management-within-obpi-pipeline-execution | — | No |
| OBPI-0.22.0-05-status-and-state-integration | completed | Yes |
| OBPI-0.22.0-06-integrate-task-status-with-existing-gz-status-and-gz-state-reporting | — | No |

## Verification Results
- **test**: PASS (`uv run gz test`) -> `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/audit/proofs/test.txt`
- **lint**: PASS (`uv run gz lint`) -> `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/audit/proofs/lint.txt`
- **typecheck**: PASS (`uv run gz typecheck`) -> `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/audit/proofs/docs.txt`

## Evidence Links
- `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/obpis/OBPI-0.22.0-01-task-entity-model.md`
- `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/obpis/OBPI-0.22.0-02-task-ledger-events.md`
- `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/obpis/OBPI-0.22.0-03-git-commit-linkage.md`
- `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/obpis/OBPI-0.22.0-04-gz-task-cli.md`
- `docs/design/adr/pre-release/ADR-0.22.0-task-level-governance/obpis/OBPI-0.22.0-05-status-and-state-integration.md`
