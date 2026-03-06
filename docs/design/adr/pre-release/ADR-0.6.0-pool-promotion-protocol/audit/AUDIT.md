# Audit: ADR-0.6.0-pool-promotion-protocol

- ADR: `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/ADR-0.6.0-pool-promotion-protocol.md`

## Results
- **test**: PASS (`uv run -m unittest discover tests`) -> `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/audit/proofs/test.txt`
- **lint**: PASS (`uvx ruff check src tests`) -> `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/audit/proofs/lint.txt`
- **typecheck**: PASS (`uvx ty check src`) -> `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.6.0-pool-promotion-protocol/audit/proofs/docs.txt`
