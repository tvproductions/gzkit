# OBPI-0.0.21-04-resolver-with-fallback — Resolver with Package-Resource Fallback

**Canonical OBPI slug:** OBPI-0.0.21-04-resolver-with-fallback
**Parent ADR:** ADR-0.0.21-chores-as-gzkit-surface
**Lane:** Heavy
**Brief:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/obpis/OBPI-0.0.21-04-resolver-with-fallback.md`

## Context

The chores command surface (`gz chores {list,show,plan,advise,run}`) is currently broken on this codebase: `src/gzkit/commands/chores.py:18` hard-codes `Path("config/gzkit.chores.json")` as the registry location, but that file does not exist (and never will under the new layout). OBPI-01 physically migrated chores to `src/gzkit/chores/<slug>/`, OBPI-02 added `GzkitConfig.paths.chores`, and OBPI-03 packaged the data into the wheel. OBPI-04 closes the loop: rewrite the resolver to consult `<project_root>/<paths.chores>/` first, fall back to `importlib.resources.files("gzkit.chores")`, surface which path won via a new `--explain` flag, and produce diagnostic errors that name *both* attempted paths so operators can distinguish "scaffolder never ran" from "wrong slug" from "broken install" at a glance.

Verified pre-plan:
- Sibling OBPIs 01/02/03 are `Completed` in their frontmatter.
- `src/gzkit/chores/{__init__.py, registry.json, <slug>/}` exists.
- `GzkitConfig.paths.chores = ".gzkit/chores"` (`src/gzkit/config.py:101`).
- `uv run gz chores list` currently exits 1 with `BLOCKERS: Missing chores registry: config/gzkit.chores.json` — confirming the regression this OBPI must close.

Note (defer to GHI): `src/gzkit/chores/registry.json` `chores[*].path` entries still read `"ops/chores/<slug>"`, a stale OBPI-01 location. The resolver below intentionally uses **slug** (not the `path` field) for filesystem probes, so this drift does not block OBPI-04. File a `defect`-labelled GHI during Stage 5 to fix the registry's `path` fields under OBPI-01's allowlist (or in OBPI-08's layout validator).

## Design

### Resolver core (`src/gzkit/commands/chores.py`)

Add a small `ResolvedPath` Pydantic model and three helpers. All three follow the same project→package→error shape so operators see one consistent diagnostic.

```python
class ResolvedPath(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    path: Path                          # Traversable concrete path (works for both)
    source: Literal["project", "package"]

def _project_chores_root(project_root: Path) -> Path:
    cfg = load_gzkit_config(project_root)         # OBPI-02 surface
    return project_root / cfg.paths.chores

def _package_chores_root() -> Path:
    return Path(str(importlib.resources.files("gzkit.chores")))

def _resolve_registry() -> ResolvedPath: ...
def _resolve_chore_dir(slug: str) -> ResolvedPath: ...
```

Resolution rules:
- **Project wins** when `<project_root>/<paths.chores>/<slug>/acceptance.json` is a file (or for the registry: `<project_root>/<paths.chores>/registry.json` is a file).
- **Package wins** when project-local missing AND `importlib.resources.files("gzkit.chores").joinpath(slug)/acceptance.json` is a file.
- **Both miss** → raise `GzCliError` whose message contains *both* literal substrings: `.gzkit/chores/<slug>` (or whatever `paths.chores` resolves to) AND `importlib.resources` + `gzkit.chores`. Include a one-line operator hint ("run `gz init` to scaffold, or verify the slug").

Convert the `Traversable` returned by `importlib.resources.files(...)` to a concrete `Path` via `str(...)` — package data ships in the wheel as real files (per OBPI-03), so this is safe and lets all downstream code keep using `Path` semantics unchanged.

### Structured log on fallback

Add `logger = structlog.get_logger(__name__)` at module top of `chores.py`. Inside both `_resolve_registry` and `_resolve_chore_dir`, the package-fallback branch emits exactly one event:

```python
logger.info(
    "chore.resolver.fallback",
    slug=slug,                     # "registry" for the registry resolver
    project_path=str(project_candidate),
    package_path=str(package_candidate),
)
```

Mirror gzkit's existing structlog pattern (setup at `src/gzkit/cli/logging.py:114-122`; this would be the first command-layer caller — that's fine, it's the documented contract).

### Wire-up

1. **`_load_chores_registry`** (`chores.py:122`): replace `registry_path = project_root / CHORES_REGISTRY_PATH` with `resolved = _resolve_registry(); registry_path = resolved.path`. Preserve all existing JSON parsing, blocker accumulation, and return shape. Drop the `CHORES_REGISTRY_PATH` constant entirely (no other in-repo references after grep).
2. **`_parse_chore_pointer`** (`chores_exec.py:169` / probe at line 214): replace `chore_dir = project_root / chore_path` with `resolved = _resolve_chore_dir(slug); chore_dir = resolved.path`. The registry's `path` field becomes a *display-only* attribute (kept on `ChoreDefinition` for `chores show` output); resolution uses **slug** so the package and project trees can diverge in literal layout without breaking the resolver.
3. **`_load_acceptance`** (`chores_exec.py:138`): take `chore_dir: Path` (or the `resolved.path` value) instead of `(project_root, chore_path)`, since chore_dir already encodes both.
4. **Threading the source label**: extend `ChoreDefinition` with an optional `resolution_source: Literal["project", "package"] | None = None` field so `--explain` can render it without a second resolution pass. Set during `_parse_chore_pointer`.

### `--explain` flag (`src/gzkit/cli/parser_maintenance.py:673-678` + `chores_list`)

Add the flag at the parser:

```python
p_chores_list = chores_commands.add_parser("list", ...)
p_chores_list.add_argument(
    "--explain",
    action="store_true",
    help="Show which resolution path (project|package) won per chore.",
)
p_chores_list.set_defaults(
    func=lambda a: _lazy("chores_list")(explain=a.explain),
)
```

`chores_list(explain: bool = False)` adds a `Source` column to the existing Rich table when `explain=True`. Cell values: `project` (no annotation), `package (fallback; scaffolder may need re-run)`, or `missing` (if a registry entry resolved to neither root). Default `explain=False` keeps the existing table shape — protects REQ-07 (no regression on the default surface).

### Error semantics on miss

`GzCliError` raised by `_resolve_chore_dir(slug)` for both-paths-miss must read like this (Acceptance REQ-03 dictates substrings; the wording is operator-facing):

```
Chore 'foo-bar' not found in either resolution path:
  - project: /abs/path/.gzkit/chores/foo-bar (path: .gzkit/chores/foo-bar)
  - package: importlib.resources('gzkit.chores')/foo-bar
Hint: run `gz init` to scaffold .gzkit/chores/, or verify the slug spelling.
```

Same shape for `_resolve_registry()` miss with `registry.json` instead of `<slug>`.

## Files Touched

| File | Change | Notes |
|------|--------|-------|
| `src/gzkit/commands/chores.py` | Drop `CHORES_REGISTRY_PATH`. Add `ResolvedPath`, `_project_chores_root`, `_package_chores_root`, `_resolve_registry`, `_resolve_chore_dir`. Add structlog logger. Rewrite `_load_chores_registry` to use resolver. Add `explain` parameter to `chores_list` and a `Source` column. Extend `ChoreDefinition` with `resolution_source`. | Brief allowlist primary site. |
| `src/gzkit/commands/chores_exec.py` | Rewrite `_parse_chore_pointer` to call `_resolve_chore_dir(slug)` and stop joining `project_root + path`. Adjust `_load_acceptance` to accept a resolved `Path`. Set `resolution_source` on the returned `ChoreDefinition`. | Two existing call sites at lines 138, 214. |
| `src/gzkit/cli/parser_maintenance.py` | Add `--explain` to the `chores list` subparser, thread the flag through to `chores_list(explain=...)`. | Lines 673-678 (subparser definition only — no other surface changes). |
| `tests/commands/test_chores.py` | Replace `Path("config/gzkit.chores.json")` scaffolding (~lines 13-32, 99, 106, 209) with the new project-root scaffolder. Add four REQ-derived TDD tests below. Existing tests rewritten to match the new resolver shape but assert the same operator-visible behavior. | Brief allowlist; existing tests are part of the regression baseline (REQ-07). |
| `tests/commands/test_frontmatter_reconcile.py` | Single docstring reference to `config/gzkit.chores.json` at line 43 — update to the new resolver's path. | Cosmetic; not in allowlist but the docstring is a stale literal that will mislead future readers. **Decision: leave alone unless test fails; flag in Stage 5 if needed.** |

`src/gzkit/commands/common.py` — **not touched**. The new resolver lives in `chores.py` per the brief's preference. No new shared helper warranted.

## TDD plan (RED → GREEN per increment)

Use `CliRunner.isolated_filesystem()` like the existing tests. For the package-fallback path, monkeypatch `importlib.resources.files` (no in-codebase precedent for this mock — use the standard `unittest.mock.patch("gzkit.commands.chores.importlib.resources.files", return_value=fake_traversable)` shape). Use a `tmp_path`-style real directory wrapped in a `pathlib.Path` as the fake "package root" — `Path` is `Traversable`-compatible for `.joinpath()`, `.is_file()`, and `str(...)`.

1. **REQ-04-01 — `test_chore_resolver_project_wins`**
   - Setup: scaffold `.gzkit/chores/demo-chore/{acceptance.json,CHORE.md}` + project-local `.gzkit/chores/registry.json` listing `demo-chore`.
   - Act: call `_resolve_chore_dir("demo-chore")`.
   - RED expectation: current code raises `Missing chores registry: config/gzkit.chores.json`.
   - Assert: `result.source == "project"` and `result.path` equals the `.gzkit/chores/demo-chore` directory.

2. **REQ-04-02 — `test_chore_resolver_falls_back_to_package`**
   - Setup: NO `.gzkit/chores/`; mock `importlib.resources.files("gzkit.chores")` to return a tempdir containing `pkg-chore/acceptance.json` + `registry.json`.
   - Act: call `_resolve_chore_dir("pkg-chore")` with `caplog`/structlog capture active.
   - Assert: `result.source == "package"`; capture contains a `chore.resolver.fallback` event with `slug="pkg-chore"`.

3. **REQ-04-03 — `test_chore_resolver_raises_with_both_paths_named`**
   - Setup: NO `.gzkit/chores/`; mock package root to a tempdir that does NOT contain the slug.
   - Act + Assert: `GzCliError` raised; message contains both `".gzkit/chores/missing"` AND (`"importlib.resources"` OR `"gzkit.chores"`).

4. **REQ-04-04 — `test_gz_chores_list_explain_distinguishes_source`**
   - Setup: mixed scaffolding — one chore in `.gzkit/chores/`, one only in mocked package root, both listed in a project-side registry.
   - Act: `runner.invoke(main, ["chores", "list", "--explain"])`.
   - Assert: exit 0, output contains `project` and `package` labels on the matching rows.

5. **REQ-04-05 — `test_registry_resolver_uses_same_order`**
   - Setup: NO project registry; mocked package contains `registry.json`.
   - Assert: `_resolve_registry().source == "package"`; fallback log event fired with `slug="registry"`.

6. **REQ-04-07 (regression) — `test_chores_list_default_no_source_column`**
   - Assert: `runner.invoke(main, ["chores", "list"])` (no `--explain`) produces output **without** a `Source` column header — proves the default surface is byte-equivalent to pre-OBPI behavior.

Existing test file's `_write_v2_registry()` helper rewrites cleanly: change the literal target path to `_project_chores_root(Path.cwd()) / "registry.json"`, ensure the directory exists. Existing tests then exercise the new resolver via the project-first branch.

## Verification

```bash
# Phase 1 — TDD cycles
uv run -m unittest tests.commands.test_chores -v 2>&1 | tail -30

# Phase 2 — gates
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.21-04

# Phase 3 — operator-facing smoke
uv run gz chores list --explain 2>&1 | head -10
uv run gz chores show coverage-40pct 2>&1 | head -5      # project resolution
mv .gzkit/chores .gzkit/chores.away 2>/dev/null || true
uv run gz chores list --explain 2>&1 | head -5            # expect "package" labels + log event
mv .gzkit/chores.away .gzkit/chores 2>/dev/null || true
uv run gz chores show nonexistent-slug 2>&1 | grep -E "\.gzkit/chores|gzkit\.chores|importlib"

# Phase 4 — Heavy-lane gates
uv run gz validate --documents
uv run mkdocs build --strict
```

Heavy-lane BDD is explicitly deferred to OBPI-07 per the brief's Gate 4 section.

## Out of scope (do NOT do in this OBPI)

- Fixing `src/gzkit/chores/registry.json` `path` fields (OBPI-01 surface) — file a GHI in Stage 5.
- `gz init` scaffolder wiring of `.gzkit/chores/` — OBPI-05.
- Manpage updates for `--explain` — OBPI-06.
- BDD `gz chores` end-to-end scenarios — OBPI-07.
- Layout validator for `paths.chores` — OBPI-08.
