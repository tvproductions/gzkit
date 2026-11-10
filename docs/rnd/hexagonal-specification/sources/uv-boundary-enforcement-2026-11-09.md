# uv and boundary enforcement — research report, 2026-11-09

> A research subagent's report for the hexagonal-specification R&D run, landed verbatim. It is a
> primary source for the run; it rules nothing. Commissioned to answer the operator's question
> *"Can the uv-build system help with boundary/package/module enforcement?"*

Sources: uv docs as published for uv 0.13.7 (the local version: `uv 0.13.7 (316c827e0 2026-11-03)`), read in full from the docs source in `astral-sh/uv` `main/docs/` (the same text docs.astral.sh renders), plus the published settings reference and local `uv help sync` / `uv help run`. Where the docs were silent I ran a throwaway three-member workspace in the session scratchpad (nothing written to any repository); those results are marked OBSERVED.

## 1. Does `uv_build` restrict imports, or only control distribution contents?

Only distribution contents. No `uv_build` setting restricts what a module may import.

- https://docs.astral.sh/uv/concepts/build-backend/ — "A build backend transforms a source tree (i.e., a directory) into a source distribution or a wheel."
- Same page, § File inclusion and exclusion — "The build backend is responsible for determining which files in a source tree should be packaged into the distributions."

The complete `[tool.uv.build-backend]` setting list (https://docs.astral.sh/uv/reference/settings/#build-backend) is `data`, `default-excludes`, `module-name`, `module-root`, `namespace`, `source-exclude`, `source-include`, `wheel-exclude`. Those bearing on layout:

| Setting | What the docs say |
|---|---|
| `module-name` | "The name of the module directory inside `module-root`." May be dotted (`foo.bar`) or a list. |
| `module-root` | "The directory that contains the module directory." Default `src`. |
| `namespace` | "Build a PEP 420 implicit namespace package, allowing more than one root `__init__.py`." |
| `source-include` / `source-exclude` | Globs adding to / removing from the sdist; excludes also apply to wheels. |
| `wheel-exclude` | "Glob expressions which files and directories to exclude from the wheel." |

Related structural facts from the build-backend page:

- One top-level module per wheel: "There must only be one top level module, and all data files must either be under the module root or in the appropriate data directory."
- Multi-module packages are supported but discouraged: "While we do not recommend this structure (i.e., you should use a workspace with multiple packages instead), it is supported".
- `namespace = true` weakens checks: "Using `namespace = true` disables safety checks."
- The backend does validate, but only metadata and structure: "It validates project metadata and structures, preventing common mistakes."
- Pure Python only: "The uv build backend currently **only supports pure Python code**."

## 2. Is a workspace one shared environment? What do `--package`, `--exact`, `--isolated` install?

One lockfile and one `.venv` for the workspace; which members are installed depends on the command.

- https://docs.astral.sh/uv/concepts/projects/workspaces/ — "each package defines its own `pyproject.toml`, but the workspace shares a single lockfile".
- Same page — "`uv run` and `uv sync` operate on the workspace root by default, though both accept a `--package` argument".
- Same page, § When (not) to use workspaces — "Workspaces are _not_ suited for cases in which members have conflicting requirements, or desire a separate virtual environment for each member."

What each form installs:

| Command | Docs / help text | OBSERVED in scratch workspace (members `core`, `adapter` → `core`, `other`) |
|---|---|---|
| `uv sync` (root is a package depending on `core`) | operates on the workspace root | root + `core` only; `adapter`, `other` absent |
| `uv sync` (virtual root, no `[project]`) | not stated for this case | all three members installed |
| `uv sync --all-packages` | `uv help sync`: "The workspace's environment (`.venv`) is updated to include all workspace members." | all members |
| `uv sync --package core` | `uv help sync`: "updated to reflect the subset of dependencies declared by the specified workspace member packages." | `core` only |
| `uv sync --package adapter` | same | `adapter` + `core`; `other` absent |
| `uv run --package core` after an all-packages sync | inexact by default (below) | all three still importable |
| `uv run --exact --package core` | exact sync | `core` only (and the shared `.venv` is stripped) |
| `uv run --isolated --package core` | fresh environment | `core` only; shared `.venv` untouched |

- `--exact`: https://docs.astral.sh/uv/concepts/projects/sync/ § Handling of extraneous packages — "`uv sync` performs "exact" syncing by default, which means it will remove any packages that are not selected for installation."
- Same section — "`uv run` uses "inexact" syncing by default, ensuring that all required packages are installed but not removing extraneous packages."
- `--isolated` (`uv help run`; also https://docs.astral.sh/uv/reference/cli/#uv-run) — "This option forces a fresh environment to be used for the project, enforcing strict isolation between dependencies and declaration of requirements."
- `--no-project` is not a member-isolation tool (`uv help run`): "Avoid discovering the project or workspace."

So `--package X` alone does not guarantee siblings are absent under `uv run`; `--exact` or `--isolated` does.

## 3. Can a member's tests run with only its declared dependencies, so an undeclared sibling import fails?

Yes in practice, but uv documents this as environment selection, not as an enforcement guarantee.

Command shapes the docs support:

- `uv run --isolated --package <member> <test command>` — temporary environment, shared `.venv` left alone.
- `uv run --exact --package <member> <test command>` — same content, but mutates the shared `.venv`.
- `uv sync --package <member>` then run in `.venv` — exact by default.

OBSERVED: with `other` undeclared by `adapter`, `uv run --isolated --package adapter` gave an environment where `other` was not importable. I checked importability with `importlib.util.find_spec`, not a full test run.

Caveats the docs give:

- The explicit disclaimer (workspaces page, closing note): "uv can't ensure that a package uses its declared dependencies and nothing else."
- Same note: "uv can't ensure that packages don't import dependencies declared by another workspace member."
- Editable installs remain, even with `--isolated` (`uv help run`): "An editable installation is still used for the project." And workspaces page: "Dependencies between workspace members are editable." `--no-editable` exists to opt out.
- Shared Python range: "uv's workspaces enforce a single `requires-python` for the entire workspace, taking the intersection of all members' `requires-python` values."
- Single resolution: `uv lock` "operates on the entire workspace at once", so members cannot hold conflicting versions.
- The `dev` group is included by default: "The `dev` group is special-cased and synced by default." (sync page). A sibling listed in a member's `dev` group would therefore be importable in its tests.
- The docs' own alternative for per-member environments is path dependencies, "with the downside that `uv run --package` is no longer available".

INFERRED (not in the docs):

- Isolation is at distribution granularity and is transitive. `adapter` declaring `core` gets everything `core` depends on, so an import of a transitive dependency it never declared still succeeds.
- It cannot constrain imports between modules inside one distribution, nor direction (only presence/absence).
- Tests launched from the workspace root may still pick up sibling source through the working directory on `sys.path` if a flat layout is used; the docs' `src`-layout note ("isolated from any `python` invocations in the project root") addresses this only in general terms.

## 4. Does uv document any import-boundary or architecture-enforcement feature?

No. I found none in the build backend, workspaces, sync, run, dependencies, layout, init, config or packaging pages, nor in the settings reference or `uv help sync` / `uv help run`. The only statement on the subject is the negative one quoted in answer 3, which begins: "As Python does not provide dependency isolation". The nearest positive wording is aspirational, not a mechanism: "Workspaces help enforce isolation and separation of concerns." (workspaces page). I did not read every page of the uv docs site (e.g. the full CLI reference, `uv pip` pages, preview features), so "none anywhere" is limited to the pages listed.

## 5. Workspace limits relevant to publishing one PyPI distribution

- Members are separate packages, each with its own `pyproject.toml`: workspaces page — "a series of libraries that are versioned and maintained as separate Python packages, all in the same Git repository."
- Builds are per package: https://docs.astral.sh/uv/guides/package/ — "`uv build --package <PACKAGE>` will build the specified package within the current workspace."
- `tool.uv.sources` (including `workspace = true`) is a uv-only development mechanism; the packaging guide recommends "running `uv build --no-sources` to ensure that the package builds correctly when `tool.uv.sources`" is absent.
- The docs describe no option for a root package to bundle member code into its wheel. A wheel holds the module under `module-root` only ("There are no specific wheel includes.").
- OBSERVED: building a root that depends on member `core` produced a wheel containing only `rootpkg/` with `Requires-Dist: core` in its metadata. So the member would have to be published as its own distribution for the root to install from an index.
- INFERRED: the documented way to ship several import roots in one distribution is a single package using list-valued `module-name` or `namespace = true`, which the docs discourage and which forgoes per-member environments.

## Summary

- Certain: `uv_build` settings govern only which files enter the sdist/wheel and how the module is located; none governs imports.
- Certain: a workspace has one lockfile, one `requires-python` intersection, and one shared `.venv`; `--package`, `--exact` and `--isolated` select which members are installed, and uv's docs explicitly disclaim enforcing declared-dependencies-only.
- Certain (observed on 0.13.7, consistent with the help text): `uv run --isolated --package X` and `uv sync --package X` yield an environment without undeclared sibling members.
- Not documented: any import-boundary, layering or architecture-enforcement feature; any way for a root distribution to bundle workspace members; the behaviour of plain `uv sync` on a virtual root (observed: installs all members).
- Not documented and only inferred: transitive-dependency leakage, lack of intra-distribution or directional control, and `sys.path` leakage from the working directory.

The report's closing line named two session-scratchpad directories as safe to delete (the fetched doc sources and the test workspace); they are outside the repository and are not reproduced here.
