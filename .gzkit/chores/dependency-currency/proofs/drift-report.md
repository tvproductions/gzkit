# Dependency drift report — 2026-11-26

Scan at 2026-11-26T02:11:20Z (`dependency-currency` 2.1.1, first run under the
currency criterion, GHI #1369). Before: `check_currency.py --currency` exit 3,
27 pins behind. After the upgrade: exit 0.

| Surface | Current | Latest | Delta | Notes |
|---------|---------|--------|-------|-------|
| uv binary | 0.13.10 | 0.13.10 | none | |
| `.python-version` | 3.14.10 | 3.14.10 | none | newest stable 3.14 download |
| ty (dev) | 0.0.109 | 0.0.111 | patch | floor raised to 0.0.111; no new default-off rules (the three unconfigured ones are #1332's) |
| babel (transitive) | 2.18.0 | 2.19.0 | minor | via `uv lock --upgrade` |
| markdown (transitive) | 3.11.3 | 3.11.4 | patch | via `uv lock --upgrade` |
| mkdocs / mkdocs-material (`==`) | 1.6.1 / 9.8.2 | 1.6.1 / 9.8.2 | none | |
| setuptools (build constraint) | 84.2.1 | 84.2.1 | none | |
| uv_build (`[build-system]` floor) | >=0.13.1 | 0.13.10 | patch | floor raised to >=0.13.10, bound `<0.14` kept |
| hook astral-sh/uv-pre-commit | 0.13.9 | 0.13.10 | patch | |
| hook pre-commit/pre-commit-hooks | v5.0.0 | v6.0.0 | **major** | [6.0.0 changelog](https://github.com/pre-commit/pre-commit-hooks/blob/main/CHANGELOG.md): removes `check-byte-order-marker` and `fix-encoding-pragma`, neither used here |
| hook gitleaks/gitleaks | v8.30.1 | v8.30.1 | none | `pre-commit autoupdate` proposed v8.30.0, a downgrade; kept v8.30.1 |
| action actions/checkout | v6 | v7.0.1 | **major** | [v7.0.0 notes](https://github.com/actions/checkout/releases/tag/v7.0.0): blocks fork checkout on `pull_request_target` / `workflow_run`, which no workflow here uses; 11 pins |
| action astral-sh/setup-uv | v10.3.0 | v10.4.0 | minor | SHA pin moved to the v10.4.0 commit; 11 pins |
| action astral-sh/attest-action | v0.0.6 | v0.0.7 | patch | SHA pin moved to the v0.0.7 commit |
| lizard | 1.26.1 (2026-11-16) | 1.26.1 | none | current; parser support: `gz validate --complexity-ceiling` refuses nothing as unmeasured |
| cohesion | 1.2.0 (2024-12-09) | 1.2.0 | none | **stale**: newest release older than a year. Not abandoned: the repository is not archived and no maintainer notice was found (`gh api repos/mschwager/cohesion`: archived=false) |

Holds: none.
