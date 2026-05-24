# Audit: ADR-0.27.0-namespace-router-product-surface

- ADR: `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/ADR-0.27.0-namespace-router-product-surface.md`
- Generated: 2026-05-24

## Attestation Record
- Attestor: Jeffry
- Status: completed
- Timestamp: 2026-05-24T15:06:00.166032+00:00

## Gate Results (from ledger)
| Gate | Status | Command | Return Code |
|------|--------|---------|-------------|
| 1 | pass | `ADR exists` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |

## OBPI Completion Summary
| OBPI | Receipt Event | Completed |
|------|---------------|-----------|
| OBPI-0.27.0-01-router-skill-files | completed | Yes |
| OBPI-0.27.0-02-router-surface-sync | completed | Yes |
| OBPI-0.27.0-03-router-tables-validator | completed | Yes |
| OBPI-0.27.0-04-router-coverage-completion | completed | Yes |

## Verification Results
- **test**: PASS (`uv run gz test`) -> `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/audit/proofs/test.txt`
- **lint**: PASS (`uv run gz lint`) -> `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/audit/proofs/lint.txt`
- **typecheck**: PASS (`uv run gz typecheck`) -> `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/audit/proofs/docs.txt`

## Evidence Links
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-01-router-skill-files.md`
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-02-router-surface-sync.md`
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-03-router-tables-validator.md`
- `docs/design/adr/pre-release/ADR-0.27.0-namespace-router-product-surface/obpis/OBPI-0.27.0-04-router-coverage-completion.md`
