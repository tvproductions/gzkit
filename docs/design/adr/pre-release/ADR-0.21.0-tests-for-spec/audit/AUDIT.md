# Audit: ADR-0.21.0-tests-for-spec

- ADR: `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- Generated: 2026-03-27

## Attestation Record
- Attestor: Jeff
- Status: completed
- Timestamp: 2026-03-27T21:19:20.508369+00:00

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
| OBPI-0.21.0-01-covers-decorator-and-registration | completed | Yes |
| OBPI-0.21.0-01-define-traceability-contract-from-spec-artifacts-to-tests | — | No |
| OBPI-0.21.0-02-coverage-anchor-scanner | completed | Yes |
| OBPI-0.21.0-02-enforce-requirement-level-coverage-anchors-across-three-levels | — | No |
| OBPI-0.21.0-03-add-command-surfaces-to-report-missing-and-present-covers-mappings | — | No |
| OBPI-0.21.0-03-gz-covers-cli | completed | Yes |
| OBPI-0.21.0-04-adr-audit-integration | completed | Yes |
| OBPI-0.21.0-04-integrate-traceability-output-with-adr-audit-and-status-reporting | — | No |
| OBPI-0.21.0-05-operator-docs-and-migration | completed | Yes |
| OBPI-0.21.0-05-produce-operator-facing-docs-with-examples-of-compliant-annotations | — | No |
| OBPI-0.21.0-06-define-language-agnostic-proof-metadata-patterns-for-non-python-test-stacks | — | No |

## Verification Results
- **test**: PASS (`uv run gz test`) -> `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/audit/proofs/test.txt`
- **lint**: PASS (`uv run gz lint`) -> `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/audit/proofs/lint.txt`
- **typecheck**: PASS (`uv run gz typecheck`) -> `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/audit/proofs/docs.txt`

## Evidence Links
- `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/obpis/OBPI-0.21.0-01-covers-decorator-and-registration.md`
- `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/obpis/OBPI-0.21.0-02-coverage-anchor-scanner.md`
- `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/obpis/OBPI-0.21.0-03-gz-covers-cli.md`
- `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/obpis/OBPI-0.21.0-04-adr-audit-integration.md`
- `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/obpis/OBPI-0.21.0-05-operator-docs-and-migration.md`
