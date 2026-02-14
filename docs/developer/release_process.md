# Release Process (SemVer)

Status: Active
Last reviewed: 2026-02-14

Audience: contributors (developer docs; not published via MkDocs)

Use this checklist to cut a gzkit release with AirlineOps-style release discipline.

## Preconditions

- Target ADR/OBPI scope is complete and attested.
- `pyproject.toml` `[project].version` is set to `X.Y.Z`.
- `src/gzkit/__init__.py` `__version__` matches `X.Y.Z`.
- `uv.lock` is refreshed after the version bump.
- `RELEASE_NOTES.md` has a `vX.Y.Z - ... (YYYY-MM-DD)` section.

## Quick checklist

1. Validate release readiness

```zsh
uv run -m unittest discover tests
uv run gz lint
uv run gz typecheck
uv run gz validate --ledger
uv run mkdocs build --strict
```

2. Finalize release notes

- Move release items into a top section in `RELEASE_NOTES.md`.
- Keep `## Unreleased` as the next placeholder section.

3. Refresh lock + sync

```zsh
uv lock
uv sync --frozen --all-extras
```

4. Build artifacts

```zsh
uv build
ls -1 dist
```

5. Optional smoke check

```zsh
uv venv .venv-smoke
uv pip install --python .venv-smoke dist/gzkit-*.whl
uv run --python .venv-smoke -m gzkit --version
rm -rf .venv-smoke
```

6. Tag and publish (manual)

```zsh
git tag -a vX.Y.Z -m "gzkit vX.Y.Z"
git push origin vX.Y.Z
gh release create vX.Y.Z --notes-file RELEASE_NOTES.md --title "gzkit vX.Y.Z"
```

## Notes

- Use `uv run gz git-sync --apply` before tagging/pushing if branch state needs normalization.
- Do not create release tags until all gates and human attestation evidence are complete.
