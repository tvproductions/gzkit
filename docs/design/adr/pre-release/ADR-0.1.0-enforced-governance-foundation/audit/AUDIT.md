# Audit: ADR-0.1.0

- ADR: `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/ADR-0.1.0-enforced-governance-foundation.md`
- Generated: 2026-03-27

## Attestation Record
- Attestor: Jeffry Babb
- Status: completed
- Timestamp: 2026-01-29T22:00:59.219856+00:00

## Gate Results (from ledger)
| Gate | Status | Command | Return Code |
|------|--------|---------|-------------|
| 2 | pass | `uv run -m unittest discover tests` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |
| 1 | pass | `ADR exists` | 0 |
| 2 | pass | `uv run gz test` | 0 |
| 2 | pass | `eval-delta` | 0 |
| 3 | pass | `uv run mkdocs build --strict` | 0 |
| 4 | pass | `uv run -m behave features/` | 0 |

## OBPI Completion Summary
| OBPI | Receipt Event | Completed |
|------|---------------|-----------|
| OBPI-0.1.0-01 | completed | Yes |
| OBPI-0.1.0-02 | completed | Yes |
| OBPI-0.1.0-03 | completed | Yes |
| OBPI-0.1.0-04 | completed | Yes |
| OBPI-0.1.0-05 | completed | Yes |
| OBPI-0.1.0-06 | completed | Yes |
| OBPI-0.1.0-07 | completed | Yes |
| OBPI-0.1.0-08 | completed | Yes |
| OBPI-0.1.0-09 | completed | Yes |
| OBPI-0.1.0-10 | completed | Yes |

## Verification Results
- **test**: PASS (`uv run gz test`) -> `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/audit/proofs/test.txt`
- **lint**: PASS (`uv run gz lint`) -> `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/audit/proofs/lint.txt`
- **typecheck**: PASS (`uv run gz typecheck`) -> `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/audit/proofs/docs.txt`

## Evidence Links
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-01-gz-init.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-02-gz-prd.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-03-gz-constitute.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-04-gz-specify.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-05-gz-plan.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-06-gz-state.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-07-gz-status.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-08-gz-attest.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-09-ledger-writer-hook.md`
- `docs/design/adr/pre-release/ADR-0.1.0-enforced-governance-foundation/obpis/OBPI-0.1.0-10-templates.md`
