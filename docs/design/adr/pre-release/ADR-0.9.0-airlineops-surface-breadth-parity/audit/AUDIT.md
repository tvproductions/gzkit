# Audit: ADR-0.9.0-airlineops-surface-breadth-parity

- ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`

## Results
- **test**: PASS (`uv run -m unittest discover tests`) -> `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/audit/proofs/test.txt`
- **lint**: PASS (`uvx ruff check src tests`) -> `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/audit/proofs/lint.txt`
- **typecheck**: PASS (`uvx ty check src`) -> `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/audit/proofs/docs.txt`
