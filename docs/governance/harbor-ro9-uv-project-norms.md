<!-- markdownlint-configure-file { "MD013": { "line_length": 9999 } } -->

# uv's project model — the normative checklist RO-9 holds gzkit to

**A record, read 2026-10-18 from uv's documentation source** (`astral-sh/uv` `docs/`, end to end; the
settings reference from the live site), describing **uv 0.13.x**. It is the reference for
[the RO-9 specification](harbor-ro9-astral-toolchain.md). Strength is uv's own wording; where uv uses no
modal word it reads "default" or "descriptive". Re-read it when uv moves a minor (operator ruling
2026-10-19: *"keep all astral tools up to date"*).

Pages read in full: [projects](https://docs.astral.sh/uv/concepts/projects/) and its sub-pages
([layout](https://docs.astral.sh/uv/concepts/projects/layout/), [init](https://docs.astral.sh/uv/concepts/projects/init/),
[dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/), [run](https://docs.astral.sh/uv/concepts/projects/run/),
[sync](https://docs.astral.sh/uv/concepts/projects/sync/), [config](https://docs.astral.sh/uv/concepts/projects/config/),
[build](https://docs.astral.sh/uv/concepts/projects/build/), [export](https://docs.astral.sh/uv/concepts/projects/export/),
[workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/)), the [projects guide](https://docs.astral.sh/uv/guides/projects/),
[package guide](https://docs.astral.sh/uv/guides/package/), [Python versions](https://docs.astral.sh/uv/concepts/python-versions/),
[build backend](https://docs.astral.sh/uv/concepts/build-backend/), [resolution](https://docs.astral.sh/uv/concepts/resolution/),
[configuration files](https://docs.astral.sh/uv/concepts/configuration-files/), [GitHub](https://docs.astral.sh/uv/guides/integration/github/),
[pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/), [`uv pip` compatibility](https://docs.astral.sh/uv/pip/compatibility/)
and [settings](https://docs.astral.sh/uv/reference/settings/).

## 1. `pyproject.toml` and `requires-python`

| Rule | Strength | uv's words |
|---|---|---|
| `pyproject.toml` identifies the project root | requires | "uv requires this file to identify the root directory of a project." |
| A minimal project has `name` and `version` | descriptive | "A minimal project definition includes a name and version" |
| Set `requires-python` | recommended | "It is recommended to set a `requires-python` value" |
| `requires-python` sets the allowed syntax and dependency selection | descriptive | "determines the Python syntax that is allowed in the project and affects selection of dependency versions" |
| Every dependency must support the whole range | must | "all required packages must be compatible with the _entire_ range of `requires-python`" |
| Upper bounds are ignored for dependencies | descriptive | "uv only considers lower bounds and ignores upper bounds entirely." |
| `.python-version` or `--python` chooses the interpreter within the range | descriptive | "The first Python version that is compatible with the requirement will be used, unless a version is otherwise requested, e.g., via a `.python-version` file" |
| Entry points need a build system | requires | "Using the entry point tables requires a build system to be defined." |
| Namespace plugin entry-point groups by package name | recommended | "it is recommended to namespace the key by the package name" |

## 2. `.python-version`

| Rule | Strength | uv's words |
|---|---|---|
| `uv init` writes it (not with `--bare`); it sets the venv's Python | default | "This file tells uv which Python version to use when creating the project's virtual environment." |
| Write a version number | recommended | "use of a version number is recommended for interoperability with other tools." |
| Create it with `uv python pin` | descriptive | "A `.python-version` file can be created in the current directory with the `uv python pin` command." |
| `uv python install` with no argument reads it | descriptive | (Python versions page; CI guide: "This will respect the Python version pinned in the project.") |
| Not searched beyond the project or workspace | descriptive | "uv will not search for `.python-version` files beyond project or workspace boundaries" |

## 3. Build system, packaging and `uv_build`

| Rule | Strength | uv's words |
|---|---|---|
| Configure a build system | strongly recommend | "We strongly recommend configuring a build system." |
| `uv init` defines one and uses `src/<project>/` | default | "uv prefers to define a build system and place source files in a dedicated `src/<project_name>/` directory." |
| Libraries are packaged | always require | "Libraries always require a packaged project." |
| `uv_build` is `uv init`'s backend | default | "By default, `uv init` creates a packaged project using the uv build backend." |
| Upper-bound the `uv_build` requirement | rationale | "Including an upper bound on the `uv_build` version ensures that your package continues to build correctly" (`uv_build>=0.13.1,<0.14`) |
| `uv_build` is pure Python only | limitation | "The uv build backend currently **only supports pure Python code**." |
| One root module at `src/<name>/__init__.py` by default | default | "By default, a single root module is expected at `src/<package_name>/__init__.py`." |
| Data files under the module root or a data directory | must | "all data files must either be under the module root or in the appropriate data directory." |
| Anchor include globs | avoid | "avoid patterns without an anchor such as `**/sample.csv`." |
| Augment build dependencies rather than disable isolation | recommend | "we recommend augmenting the build dependencies rather than disabling build isolation entirely" |
| `tool.uv.package = false` skips building and installing | optional | "Setting `tool.uv.package = false` will force a project package _not_ to be built and installed" |

## 4. `uv.lock` and `.venv`

| Rule | Strength | uv's words |
|---|---|---|
| Commit the lockfile | should | "This file should be checked into version control" |
| Never edit it by hand | should not | "managed by uv and should not be edited manually." |
| It is universal | descriptive | "a _universal_ or _cross-platform_ lockfile" |
| New releases do not stale it; upgrades are explicit | important | "uv will not consider lockfiles outdated when new versions of packages are released" (`uv lock --upgrade`, `--upgrade-package`) |
| Schema compatibility holds within a uv minor only | descriptive | "lockfiles may only be rejected across minor releases." |
| `exclude-newer` gives reproducible resolution and cooldowns | optional | "This is a good way to improve security posture by delaying package updates" |
| Do not commit `.venv` | not recommended | "It is not recommended to include the `.venv` directory in version control" |
| Do not change the environment by hand | not recommended | "It is _not_ recommended to modify the project environment manually, e.g., with `uv pip install`." |

## 5. Dependencies

| Rule | Strength | uv's words |
|---|---|---|
| Development dependencies go in `[dependency-groups]`, never `[project]` | descriptive | "development dependencies are local-only and will _not_ be included in the project requirements when published" |
| Extras are not synced by default | default | "uv does not sync extras by default." |
| The `dev` group is synced by default | default | "The `dev` group is special-cased and synced by default." |
| Groups resolve together and must be compatible | requires | "uv requires that all dependency groups are compatible with each other" |
| Only uv reads `tool.uv.sources` | important | "Sources are only respected by uv." |
| Build with `--no-sources` before publishing | recommend | "we recommend running `uv build --no-sources`" |
| Direct dependencies carry lower bounds | default + warning | "uv will warn if direct dependencies don't have lower bounds." |
| `tool.uv.dev-dependencies` is on its way out | will be deprecated and removed | "Eventually, the `dev-dependencies` field will be deprecated and removed." |
| `uv add` / `uv remove` maintain pyproject, lock and environment; hand edits are allowed | permissive | "dependency metadata can also be updated by editing the `pyproject.toml` directly." |

## 6. Running, locking and syncing

| Rule | Strength | uv's words |
|---|---|---|
| `uv run` locks and syncs first | default | "`uv run` guarantees that your command is run in an environment with all required dependencies at their locked versions." |
| `--locked` refuses a stale lock | option | "If the lockfile is not up-to-date, uv will raise an error instead of updating the lockfile." |
| `--frozen` does not check the lock | option | "use the lockfile without checking if it is up-to-date" |
| `uv lock --check` equals `--locked` | descriptive | "This is equivalent to the `--locked` flag for other commands." |
| `uv sync` is exact; `uv run` is inexact | default | "`uv sync` performs "exact" syncing by default" |
| A tool the project needs runs with `uv run`; one-off tools with `uvx` or `uv run --with` | not recommended otherwise | "For one-off requirements, use `uvx` or `uv run --with`." |
| PREVIEW: malware check during sync | preview | `audit.malware-check = true` / `UV_MALWARE_CHECK=1` |

## 7. Build, publish and export

| Rule | Strength | uv's words |
|---|---|---|
| `uv build` is a frontend; the backend decides contents | important | "uv acts as a build frontend and only determines the Python version to use and invokes the build backend." |
| Publish with `uv publish`; trusted publishing needs no credentials | descriptive | (package guide) |
| `uv publish` makes no attestations | descriptive | "attestations must be created separately before publishing." |
| Separate build and publish jobs | important | "so that the publishing step … does not share its permissions with the building step." |
| Do not keep both `uv.lock` and `requirements.txt` | recommend against | "we recommend against using both a `uv.lock` and a `requirements.txt` file." |
| PREVIEW: CycloneDX export | preview | "Support for exporting to CycloneDX is in preview" |

## 8. Configuration and CI

| Rule | Strength | uv's words |
|---|---|---|
| `required-version` pins uv | optional | "If the version of uv does not meet the requirement at runtime, uv will exit with an error." |
| Install uv with `astral-sh/setup-uv` | recommend | "we recommend the official `astral-sh/setup-uv` action" |
| Pin uv in CI | best practice | "It is considered best practice to pin to a specific uv version" |
| The CI install step is `uv sync --locked` | example | the guide's canonical step: `uv sync --locked --all-extras --dev` |
| Python in CI from uv or `python-version-file` | option | "This will respect the Python version pinned in the project." |
| `uv-pre-commit`'s `uv-lock` keeps the lock current | optional | "To make sure your `uv.lock` file is up to date even if your `pyproject.toml` file was changed" |

## Where uv is silent, and RO-9 decides

Hand edits vs `uv add`; `--locked` vs `--frozen` in CI (RO-9: `--locked`); committing `.python-version`
and its precision (RO-9: committed, exact patch); tying `.python-version` to `requires-python` (RO-9:
the pin satisfies the floor, nothing else restates either); pinning uv (RO-9: `required-version`,
setup-uv reads it); upper bounds on runtime dependencies; which groups exist; `uv_build` over other
backends (RO-9: `uv_build`, operator ruling 3); upgrade cadence and `exclude-newer` (RO-9 tranche 5: no cooldown, ruled 2026-10-28);
committed exports (RO-9: none); SHA-pinned actions (RO-9: yes, as the guide's examples do); sources in
published packages; which `uv init` files a project keeps (RO-9 tranche 7); lockfile schema across uv
minors (RO-9: uv moves first, lock regenerated); lowest-resolution testing.
