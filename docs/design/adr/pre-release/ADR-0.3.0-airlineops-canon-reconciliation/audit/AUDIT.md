# Audit: ADR-0.3.0

- ADR: `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`

## Results
- **test**: PASS (`uv run -m unittest discover tests`) -> `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/audit/proofs/test.txt`
- **lint**: PASS (`uvx ruff check src tests`) -> `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/audit/proofs/lint.txt`
- **typecheck**: PASS (`uvx ty check src`) -> `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.3.0-airlineops-canon-reconciliation/audit/proofs/docs.txt`
