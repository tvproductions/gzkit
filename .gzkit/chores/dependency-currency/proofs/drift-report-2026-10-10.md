# Drift report — 2026-10-10 (maintenance visit A)

Scan and recommend only; nothing was bumped. Installed versions read from the environment
and `uv.lock`; latest from the GitHub releases API (`gh api repos/<owner>/<repo>/releases/latest`),
read 2026-10-10. The operator applies bumps through the `gz-deps-upgrade` skill, one per commit.

## Toolchain

| Surface | Current | Latest | Delta | Recommendation |
|---|---|---|---|---|
| uv | 0.12.23 | 0.13.0 | minor | read the changelog first (0.x minor; lockfile and `uv self version` semantics can move) |
| ruff | 0.16.10 (lock; pyproject `>=0.16.2`) | 0.17.0 | minor | read the changelog first — 0.17 is a rule-set boundary; run `uv run ruff check` before committing the bump |
| ty | 0.0.84 (lock; pyproject `>=0.0.84`) | 0.0.86 | patch ×2 | **bump now** — operator ruling 2026-08-09 (GHI #789): track ty forward, tighten the code if it gets stricter |
| Python (CI) | 3.13.16 | — | — | hold; `requires-python >=3.13` unchanged (out of this chore's scope) |

## Runtime and dev dependencies

| Surface | Current | Latest | Delta | Recommendation |
|---|---|---|---|---|
| pydantic | 2.13.5 (pyproject `>=2.13.3`) | 2.14.0 | minor | read the changelog first (validation is the one named stdlib departure; run `gz test` after) |
| rich | 15.0.0 | 15.0.0 | none | — |
| jsonschema | 4.26.0 | 4.26.0 | none | — |
| behave | 1.3.3 | 1.3.3 | none | — |
| mkdocs | 1.6.1 (pinned `==`) | 1.6.1 | none | — |
| mkdocs-material | 9.7.7 (pinned `==`) | 9.7.7 | none | — |

## Pre-commit

| Surface | Current | Latest | Delta | Recommendation |
|---|---|---|---|---|
| pre-commit-hooks | v5.0.0 | v6.0.0 | **major** | read the changelog first (end-of-file-fixer, trailing-whitespace, check-merge-conflict are in use) |
| gitleaks (local binary) | 8.30.1 | v8.30.1 | none | — |
| all other hooks | `repo: local` (uv-run tools) | tracked above | — | — |

## GitHub Actions

| Surface | Current | Latest | Delta | Recommendation |
|---|---|---|---|---|
| actions/checkout | v6 (6 uses) | v7.0.1 | **major** | read the changelog first |
| actions/setup-python | v6 (3 uses) | v7.0.0 | **major** | read the changelog first |
| astral-sh/setup-uv | v10.2.0 (5 uses) | v10.3.0 | patch | **bump now** |
| actions/upload-artifact | v7 | v7.0.2 | none (major tag) | — |
| actions/download-artifact | v8 | v8.0.2 | none (major tag) | — |
| actions/deploy-pages | v5 | v5.0.1 | none (major tag) | — |
| actions/upload-pages-artifact | v5 | v5.0.0 | none (major tag) | — |
| pypa/gh-action-pypi-publish | release/v1 | tracking tag | — | — |
| runners | `ubuntu-latest` + matrix | — | — | — |

## Summary

Nine surfaces current, two patch bumps recommended now (ty, setup-uv), three minor bumps behind
a changelog read (uv, ruff, pydantic), three majors behind a changelog read (pre-commit-hooks,
checkout, setup-python). No security advisory was observed on any surface during the scan;
this chore does not query advisory databases, so that absence is a non-observation, not a
finding. Previous run: 2026-07-31 (criteria only; no drift report was written).
