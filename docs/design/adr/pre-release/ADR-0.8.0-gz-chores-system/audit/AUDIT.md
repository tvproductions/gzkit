# Audit: ADR-0.8.0-gz-chores-system

- ADR: `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/ADR-0.8.0-gz-chores-system.md`

## Results
- **test**: PASS (`uv run -m unittest discover tests`) -> `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/audit/proofs/test.txt`
- **lint**: PASS (`uvx ruff check src tests`) -> `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/audit/proofs/lint.txt`
- **typecheck**: PASS (`uvx ty check src`) -> `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/audit/proofs/typecheck.txt`
- **docs**: PASS (`uv run mkdocs build --strict`) -> `docs/design/adr/pre-release/ADR-0.8.0-gz-chores-system/audit/proofs/docs.txt`
