# Release Process (SemVer)

Status: Active
Last reviewed: 2026-10-22

Audience: contributors (developer docs; not published via MkDocs)

Use this checklist to cut a gzkit release with AirlineOps-style release discipline.

## Preconditions

- Target ADR/OBPI scope is complete and attested.
- The version is `X.Y.Z`, set by `uv version X.Y.Z --no-sync` (what `gz patch release`
  and `gz closeout` run), which writes `pyproject.toml` and `uv.lock` together;
  `src/gzkit/__init__.py` `__version__` and the README badge are written from it.
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
uv sync --locked
```

4. Build artifacts

```zsh
uv build --no-sources
ls -1 dist
```

5. Optional smoke check (the same check `release.yml` runs before publishing)

```zsh
uv run --isolated --no-project --with dist/*.whl gz --help
uv run --isolated --no-project --with dist/*.tar.gz gz --help
```

6. Mandatory final git sync (must be immediately before publish/tag commands)

```zsh
uv run gz git-sync --apply --lint --test
```

No intervening command is allowed between this full sync and release/tag commands.
If HEAD or the worktree changes after sync, rerun this step.

7. Tag and publish (manual)

Create the release from the curated notes. `--target main` creates and pushes
the tag, which fires `.github/workflows/release.yml`; that workflow attaches the
built binaries and `py-gzkit.cdx.json`, the CycloneDX SBOM of the runtime
dependency set exported from `uv.lock`, to the release you just created, and
never rewrites a body that already exists.

```zsh
BODY="$(mktemp)"
awk '/^## v/{c++} c==2{exit} c==1' RELEASE_NOTES.md > "$BODY"
gh release create vX.Y.Z --target main --latest --title "vX.Y.Z" --notes-file "$BODY"
```

8. Publish an existing tag to PyPI (only when its tag-push run failed to publish)

A tag push runs `release.yml` as it stands at the tag, so a fix landed on `main`
never reaches a re-run of that push. Dispatch the workflow from `main` against
the tag instead; it runs only the PyPI jobs (`dist` builds the named tag,
`pypi` attests and runs `uv publish`, skipping a version PyPI already holds), and
leaves the binaries and release body alone:

```zsh
gh workflow run release.yml --ref main -f tag=vX.Y.Z
```

## Notes

- Full sync is mandatory immediately before release/tag commands: `uv run gz git-sync --apply --lint --test`.
- Do not create release tags until all gates and human attestation evidence are complete.
- Create the release *before* the tag reaches the remote, not after. A bare
  `git push origin vX.Y.Z` fires the release workflow with no release present,
  so the workflow creates one from generated notes and the curated body never
  lands — the generated-stub outcome GHI #830 closed.
- `RELEASE_NOTES.md` is cumulative, so `--notes-file` against the whole file
  publishes every historical version as the body (GHI #710). The `awk` slice
  above takes only the newest `## v…` block; `gz-patch-release` § Publish runs
  the same slice.
