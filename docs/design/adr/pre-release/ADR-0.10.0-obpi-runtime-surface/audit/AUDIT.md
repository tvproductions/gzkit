# Audit: ADR-0.10.0-obpi-runtime-surface

- ADR: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`

## Results
- **test**: PASS (`uv run -m unittest discover tests`) -> `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/audit/proofs/test.txt`
- **lint**: PASS (`uvx ruff check src tests`) -> `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/audit/proofs/lint.txt`
- **typecheck**: PASS (`uvx ty check src`) -> `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/audit/proofs/docs.txt`
