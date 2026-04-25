# OBPI-0.0.21-05: Scaffolder for `.gzkit/chores/` — Implementation Plan

## Context

ADR-0.0.21 (`chores-as-gzkit-surface`) is migrating the chore registry from
`ops/chores/` to a wheel-distributed canonical tree at `src/gzkit/chores/`
that downstream projects scaffold into `.gzkit/chores/` via `gz init`.

OBPIs 01–04 have landed:
- **OBPI-01** — `src/gzkit/chores/__init__.py` exists; 33 chore directories
  ship under it, each with `CHORE.md`, `acceptance.json`, `README.md`, and
  a `proofs/` subdir; canonical `registry.json` ships at the package root
  (verified: `ls src/gzkit/chores/` returns 33 slugs + `__init__.py` +
  `registry.json` + `README.md`).
- **OBPI-02** — `GzkitConfig.paths.chores = ".gzkit/chores"`
  (`src/gzkit/config.py:101`).
- **OBPI-03** — chores ship inside the wheel; `importlib.resources.files
  ("gzkit.chores")` resolves.
- **OBPI-04** — resolver in `src/gzkit/commands/chores.py`.

OBPI-05 closes the loop: when an operator runs `gz init` (first-run or
`--repair`), the canonical chore tree must land in
`<project>/.gzkit/chores/` with the same discipline that `scaffold_core_skills`
applies to `.gzkit/skills/`. Without OBPI-05, downstream projects still
have no chores surface even though the wheel ships one — and
OBPI-07 (BDD distribution proof) and OBPI-09 (`gz chores doctor`) both
explicitly block on it.

The scaffolder pattern differs from skills in one critical way: skills
are **rendered from templates** (`src/gzkit/skills.py:CORE_SKILLS` dict +
`render_template`), but chores are **copied byte-for-byte from package
resources**. The shape (signature, return type, callsites, repair
discipline) matches `scaffold_core_skills`; the body is a tree-copy from
`importlib.resources.files("gzkit.chores")` rather than a render loop.

## Design

### New module: `src/gzkit/chores.py`

Three public functions (mirroring the `skills.py` shape — module-level
functions, no class, library-not-CLI):

1. **`scaffold_core_chores(project_root, config=None, *, skip_existing=False) -> list[Path]`**
   - Signature is locked by REQ-06 — must match `scaffold_core_skills` at
     `src/gzkit/skills.py:302-307` exactly.
   - Iterates canonical chore slugs from
     `importlib.resources.files("gzkit.chores")` filtered to directories
     containing `CHORE.md` (skips `__pycache__`, top-level files like
     `registry.json` / `README.md`).
   - For each slug: ensures `<destination>/<slug>/` exists, copies
     `CHORE.md`, `acceptance.json`, `README.md` from canonical resource
     to destination. Never copies `proofs/` (REQ-03a).
   - When `skip_existing=True`: skips any `<slug>/` whose target directory
     already exists on disk (REQ-02).
   - When `skip_existing=False`: still preserves any existing
     `<slug>/proofs/` byte-identically (REQ-03b, REQ-07) — copy operates
     per-file, never deletes the destination directory first.
   - On first-run only (no project-local `registry.json`), copy the
     canonical `registry.json` so `gz chores list` has something to read.
   - Emits one `console.print` per scaffolded slug using the same shape
     as `scaffold_core_skills`'s caller emits — REQ-08 says "log event
     per scaffolded slug" but the existing skills pattern does the
     printing in `init_cmd.py`, not inside the scaffolder. To match REQ-08
     while staying consistent with the existing pattern, the scaffolder
     returns one `Path` per scaffolded slug and the caller in
     `init_cmd.py` iterates them with one `console.print` per entry.
   - Returns `list[Path]` of created `CHORE.md` files (parallel to
     `scaffold_core_skills` returning `list[Path]` of `SKILL.md`).

2. **`merge_chores_registry(project_root, config, *, auto_yes=False, dry_run=False) -> RegistryMergeReport`**
   - Implements REQ-04 (Decision #6 contract).
   - Reads canonical `registry.json` from
     `importlib.resources.files("gzkit.chores").joinpath("registry.json")`.
   - Reads project-local `registry.json` from
     `<destination>/registry.json` (if missing, no merge needed —
     return early with `wrote=False`).
   - Computes the union: canonical-wins on shipped slugs (slug present in
     canonical), local-wins on unknown slugs (slug not in canonical).
   - Returns a `RegistryMergeReport` with `added`, `removed`, `changed`,
     `unchanged_local` lists and a `wrote: bool` flag.
   - Prints diff to stdout via the existing `console`.
   - Unless `auto_yes=True` or `dry_run=True`: calls `_confirm(...)` from
     `commands/common.py` before writing the merged registry.
   - On `dry_run`: never writes, returns the report only.

3. **`RegistryMergeReport`** — Pydantic `BaseModel` with `frozen=True,
   extra="forbid"` per `.claude/rules/models.md`. Fields: `added: list[str]`,
   `removed: list[str]`, `changed: list[str]`, `unchanged_local: list[str]`,
   `wrote: bool`, `local_registry_path: Path`.

**Helper:** `_iter_canonical_chore_slugs() -> Iterator[Traversable]` — single
private function that yields each subdirectory under `gzkit.chores` package
resource that contains a `CHORE.md` file. Centralizes the "which slugs
are canonical" question so OBPI-09's doctor command (which depends on
OBPI-05) and OBPI-08's layout validator have a single source of truth
they could reuse later.

### Wire into `src/gzkit/commands/init_cmd.py`

**Imports** (line 26 area, after `from gzkit.skills import scaffold_core_skills`):

```python
from gzkit.chores import merge_chores_registry, scaffold_core_chores
```

**Main init path** (current line 472 area, immediately after the skills
scaffolding block):

```python
chores = scaffold_core_chores(project_root, config)
console.print(f"  Scaffolded {len(chores)} core chores")
```

**Repair path** (current line 281 area, paralleling the
`new_skills = scaffold_core_skills(...)` block):

```python
new_chores = scaffold_core_chores(project_root, config, skip_existing=not dry_run)
if dry_run:
    from gzkit.chores import _iter_canonical_chore_slugs  # noqa: PLC0415
    chores_dir = project_root / config.paths.chores
    for slug_resource in _iter_canonical_chore_slugs():
        slug = slug_resource.name
        if not (chores_dir / slug / "CHORE.md").exists():
            repaired.append(f"Would scaffold chore: {slug}")
elif new_chores:
    for chore_path in new_chores:
        repaired.append(f"Scaffolded new chore: {chore_path.parent.name}")

# Registry merge (REQ-04)
merge_report = merge_chores_registry(
    project_root, config, auto_yes=yes_flag, dry_run=dry_run
)
if merge_report.added or merge_report.removed or merge_report.changed:
    if dry_run:
        repaired.append(
            f"Would merge chores registry: "
            f"+{len(merge_report.added)}/-{len(merge_report.removed)}/"
            f"~{len(merge_report.changed)}"
        )
    elif merge_report.wrote:
        repaired.append("Merged chores registry")
```

**`--yes` flag** (REQ-04(e)): Add `yes: bool = False` to the `init` Click
command and the underlying `init()` and `_repair_missing_artifacts()`
function signatures. `--yes` is the canonical "accept registry-merge
diff without prompting" flag. Threading it through is small (3 changes:
Click decorator, `init()` signature, `_repair_missing_artifacts()`
signature + call).

### Tests: append to `tests/commands/test_init.py`

`tests/commands/test_init.py` is currently 293 lines. Adding ~180 lines
keeps it under the 600-line module cap, so the brief's optional
`tests/test_chores_scaffold.py` is **not needed** — keeping the tests
beside the existing skills/persona scaffolding tests preserves
discoverability.

New test class `TestInitChoresScaffolding(unittest.TestCase)`. Each
test follows the existing `CliRunner.isolated_filesystem()` pattern.

| Test | REQ | Notes |
|------|-----|-------|
| `test_scaffold_core_chores_creates_canonical_slugs` | REQ-05-01 | Empty project; call function directly; assert ≥3 representative slug dirs (e.g., `coverage-40pct`, `quality-check`, `dependency-currency`) exist with `CHORE.md` + `acceptance.json` + `README.md`. |
| `test_scaffold_core_chores_skip_existing_preserves_operator_edits` | REQ-05-02 | Pre-write `.gzkit/chores/coverage-40pct/CHORE.md` with `OPERATOR EDIT`; call `skip_existing=True`; assert content unchanged. |
| `test_scaffold_core_chores_does_not_copy_proofs` | REQ-05-03a | Call function on empty dir; assert no `<slug>/proofs/` directory exists in destination (canonical has them; we strip). |
| `test_scaffold_core_chores_preserves_existing_proofs` | REQ-05-03b, REQ-07 | Pre-write `.gzkit/chores/coverage-40pct/proofs/evidence.txt`; call function with `skip_existing=False`; assert proofs file byte-identical after run. |
| `test_scaffold_core_chores_signature_matches_brief` | REQ-05-06 | Use `inspect.signature` to assert exact parameter names + kinds + defaults. |
| `test_scaffold_core_chores_emits_one_path_per_slug` | REQ-05-07 | Call function on empty dir; assert returned list has one entry per canonical slug, each pointing at `<slug>/CHORE.md`. |
| `test_merge_chores_registry_reports_diff_on_canonical_addition` | REQ-05-04 | Seed local `registry.json` missing one canonical slug; call merge with `auto_yes=True`; assert report.added contains that slug; assert local registry now contains it. |
| `test_merge_chores_registry_yes_skips_prompt` | REQ-05-04(e) | Patch `_confirm` to raise; call merge with `auto_yes=True`; assert `_confirm` was NOT called. |
| `test_merge_chores_registry_dry_run_never_writes` | REQ-05-04 | Seed divergent registries; call with `dry_run=True`; assert local registry file unchanged on disk. |
| `test_gz_init_invokes_scaffold_core_chores_main_path` | REQ-05-05 | Patch `gzkit.commands.init_cmd.scaffold_core_chores` to a `MagicMock`; run `gz init`; assert called once with `(project_root, config)`. |
| `test_gz_init_repair_invokes_scaffold_core_chores_with_skip_existing` | REQ-05-05 | Patch the same mock; run `gz init` twice; on the second invocation assert called with `skip_existing=True`. |

**TDD discipline:** Per `.claude/rules/tests.md` § Red-Green-Refactor,
each test goes RED first (function does not exist or raises ImportError),
then minimum-code GREEN, increment by increment. The plan groups them
into 5 RED→GREEN cycles per the brief's Gate 2 checklist (which lists
5 cycles, one per requirement family). I will follow the brief's
cycle count exactly.

### Verification (matches brief § Verification block)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.21-05-scaffold-core-chores
uv run -m unittest tests.commands.test_init -v

# Smoke: dry-run init in a scratch tempdir
mkdir -p /tmp/gz-scaffold-test && cd /tmp/gz-scaffold-test \
  && uv run gz init --dry-run 2>&1 | grep -i chore

# Real init in a throwaway dir
cd $(mktemp -d) && uv run gz init 2>&1 | tail -10 && ls .gzkit/chores/ | head

# Repair preserves operator edits
echo "OPERATOR EDIT" > .gzkit/chores/coverage-40pct/CHORE.md
uv run gz init --repair
grep "OPERATOR EDIT" .gzkit/chores/coverage-40pct/CHORE.md && echo "preserved"

uv run gz validate --documents
uv run mkdocs build --strict
```

### Files Touched

| Path | Action | Why |
|------|--------|-----|
| `src/gzkit/chores.py` | **create** | New module, mirrors `skills.py:302-338` shape (REQ-01); houses `scaffold_core_chores` + `merge_chores_registry` + `RegistryMergeReport`. |
| `src/gzkit/commands/init_cmd.py` | **edit** | Import + 2 callsites (main + repair) + `--yes` flag plumbing (REQ-05, REQ-04(e)). |
| `tests/commands/test_init.py` | **edit** | Add `TestInitChoresScaffolding` class (~180 lines, 11 tests covering 7 REQs). |

No other files touched. Brief Denied Paths respected:
`commands/chores.py`, `config.py`, `pyproject.toml`, `chores/**`,
`features/**`, `governance/trust_audits.py` are all outside the working
set.

### Acceptance Mapping (REQ → mechanism)

| REQ | Mechanism |
|-----|-----------|
| 05-01 | `scaffold_core_chores` body: per-slug copy from package resource. |
| 05-02 | `skip_existing` branch: `if skip_existing and target_dir.exists(): continue`. |
| 05-03 | Per-file copy of only `{CHORE.md, acceptance.json, README.md}`; `proofs/` never enumerated for source, never deleted at destination. |
| 05-04 | `merge_chores_registry` reads canonical + local, computes union, prints diff, prompts via `_confirm` unless `auto_yes=True`. |
| 05-05 | Two callsites in `init_cmd.py`: line ~472 (main) and line ~281 (repair). |
| 05-06 | Signature locked by `test_scaffold_core_chores_signature_matches_brief` using `inspect.signature`. |
| 05-07 | Returns `list[Path]` (one per scaffolded slug); caller iterates and prints. |

## Risk Notes

- **Slug enumeration:** `importlib.resources.files()` returns a
  `Traversable`; iterating its children gives both files and
  directories. The helper filters to entries that have a `CHORE.md`
  child to identify "this is a chore slug" — robust against future
  package additions like `__pycache__` or top-level files.
- **`importlib.resources` editable-install gotcha:** REQ-06 forbids
  taking a filesystem-path source argument because in editable mode
  the resource path resolves to the working tree, which is correct by
  accident. The function exclusively goes through `importlib.resources`,
  so the same code path runs in both editable mode and a real wheel.
- **`--yes` flag plumbing:** Adding the Click option is the only CLI
  surface change. The brief allows modifying `init_cmd.py`, and `--yes`
  is named explicitly in REQ-04(e), so this is in scope.
- **Existing tests:** The new `scaffold_core_chores` runs inside
  every existing `gz init` test. Tests that didn't expect a
  `.gzkit/chores/` directory may need to tolerate it. The pattern is the
  same as when skills/personas were added — existing tests assert
  positive things (`.gzkit` exists, ledger exists) and don't assert
  absence of new directories, so risk is low. Will verify by running
  the full `tests/commands/test_init.py` after wiring.
