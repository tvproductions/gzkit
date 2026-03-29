# Audit: ADR-0.23.0-agent-burden-of-proof

- ADR: `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/ADR-0.23.0-agent-burden-of-proof.md`
- Generated: 2026-03-29

## Attestation Record
- Attestor: Jeff
- Status: completed
- Timestamp: 2026-03-28T21:55:07.237482+00:00

## Gate Results (from ledger)
| Gate | Status | Command | Return Code |
|------|--------|---------|-------------|
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `uv run gz lint` | 0 |
| 2 | pass | `uv run gz typecheck` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 1 | pass | `ADR exists` | 0 |
| 1 | pass | `ADR exists` | 0 |
| 2 | fail | `uv run gz test` | 1 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 1 | pass | `ADR exists` | 0 |
| 2 | fail | `uv run gz test` | 1 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 1 | pass | `ADR exists` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 1 | pass | `ADR exists` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `eval-delta` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |

## OBPI Completion Summary
| OBPI | Receipt Event | Completed |
|------|---------------|-----------|
| OBPI-0.23.0-01-closing-argument | completed | Yes |
| OBPI-0.23.0-02-product-proof-gate | completed | Yes |
| OBPI-0.23.0-03-reviewer-agent | completed | Yes |
| OBPI-0.23.0-04-ceremony-enforcement | completed | Yes |

## Verification Results
- **test**: PASS (`uv run gz test`) -> `docs\design\adr\pre-release\ADR-0.23.0-agent-burden-of-proof\audit\proofs\test.txt`
- **lint**: PASS (`uv run gz lint`) -> `docs\design\adr\pre-release\ADR-0.23.0-agent-burden-of-proof\audit\proofs\lint.txt`
- **typecheck**: PASS (`uv run gz typecheck`) -> `docs\design\adr\pre-release\ADR-0.23.0-agent-burden-of-proof\audit\proofs\typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs\design\adr\pre-release\ADR-0.23.0-agent-burden-of-proof\audit\proofs\docs.txt`

## Evidence Links
- `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/obpis/OBPI-0.23.0-01-closing-argument.md`
- `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/obpis/OBPI-0.23.0-02-product-proof-gate.md`
- `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/obpis/OBPI-0.23.0-03-reviewer-agent.md`
- `docs/design/adr/pre-release/ADR-0.23.0-agent-burden-of-proof/obpis/OBPI-0.23.0-04-ceremony-enforcement.md`
