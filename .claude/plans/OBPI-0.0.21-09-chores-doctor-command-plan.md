# Plan: OBPI-0.0.21-09-chores-doctor-command

**Anchor:** `OBPI-0.0.21-09-chores-doctor-command`
**Parent ADR:** `ADR-0.0.21-chores-as-gzkit-surface` (foundation, Heavy)
**Lane:** Heavy (new CLI subcommand)
**Brief:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/obpis/OBPI-0.0.21-09-chores-doctor-command.md`

## Context

Add `gz chores doctor` — a 2am-operator recovery path for a corrupted or partial
`.gzkit/chores/` tree. The command enumerates canonical slugs (shipped in the
wheel via `gzkit.chores`), compares with project state, classifies each slug
(`MISSING` / `DAMAGED` / `HEALTHY` / `PROJECT-LOCAL`), and repairs only the
shipped slugs that need it — never touching `proofs/` content and never
modifying project-local slugs absent from canonical.

Prerequisites confirmed completed:

- OBPI-0.0.21-04 (resolver) — `_resolve_chore_dir` / `_resolve_registry` exist
  in `src/gzkit/commands/chores.py:166-215`.
- OBPI-0.0.21-05 (scaffolder) — `scaffold_core_chores(project_root, config,
  skip_existing=True)` lives at `src/gzkit/chores/__init__.py:46-96`. Its
  `skip_existing=True` branch skips slugs whose **directory** already exists,
  so `MISSING` repair routes through it directly; `DAMAGED` per-file repair
  must use the same canonical resource walker the scaffolder uses
  (`_iter_canonical_chore_slugs` + `_PER_SLUG_FILES`) without re-implementing
  the directory-level orchestration.
- OBPI-0.0.21-06 — manpage at `docs/user/manpages/gz-chores.md:80-93` already
  documents the `doctor` subcommand contract; this OBPI's CLI surface must
  match (no new flags beyond `--dry-run` and `--json`).

Real parser registration site is `src/gzkit/cli/parser_maintenance.py`
(`_register_chores_parsers` at line 681) — the brief's Allowed Paths line
mentions `parser_artifacts.py` as a placeholder; the actual registration site
takes precedence per the brief's "confirm via grep during implementation"
instruction.

## Files

### Will edit

- `src/gzkit/commands/chores.py` — add `chores_doctor(*, dry_run: bool,
  json_output: bool)` handler; small private helpers
  (`_classify_slugs`, `_repair_damaged_slug`, `_render_doctor_table`,
  `_render_doctor_json`).
- `src/gzkit/cli/parser_maintenance.py` — add the `doctor` subparser, register
  `chores_doctor` in the lazy-import map.
- `tests/commands/test_chores.py` — add 6 REQ-derived TDD tests inside a new
  `TestChoresDoctor` class plus an output-form fixture for table rendering.

### Will read (context only)

- `src/gzkit/chores/__init__.py` (scaffolder + canonical-resource walker)
- `tests/commands/common.py` (`_quick_init`, `CliRunner`)
- `docs/user/manpages/gz-chores.md` (column names from OBPI-06)

### Out of scope

- `src/gzkit/chores/__init__.py` — denied (scaffolder belongs to OBPI-05).
- `src/gzkit/commands/init_cmd.py` — denied (init wiring is OBPI-05).
- `pyproject.toml`, `features/**`, `docs/**`, `.gzkit/rules/**`.

## Steps

### Step 1 — RED: write the 6 REQ-derived tests in `TestChoresDoctor`

Create `TestChoresDoctor(unittest.TestCase)` in
`tests/commands/test_chores.py`. Helper: `_seed_canonical_slug_clone(slug)` —
copies one real canonical slug's three files (`CHORE.md`, `acceptance.json`,
`README.md`) into the project tree from `importlib.resources.files("gzkit.chores")`.
Tests (one per REQ where mechanical):

1. `test_doctor_repairs_missing_slug` (REQ-09-03) — seed only one canonical
   slug into the project; run `gz chores doctor`; assert another canonical
   slug's three files appear; assert `Before=MISSING` / `After=HEALTHY` row.
2. `test_doctor_repairs_damaged_slug` (REQ-09-04) — seed slug, delete its
   `acceptance.json`; run `doctor`; assert file restored byte-identical to
   canonical.
3. `test_doctor_preserves_proofs` (REQ-09-05) — seed slug, write
   `.gzkit/chores/<slug>/proofs/evidence.txt` with known bytes, delete its
   `CHORE.md`; run `doctor`; assert proofs file unchanged.
4. `test_doctor_untouches_project_local` (REQ-09-06) — create
   `.gzkit/chores/my-custom/CHORE.md`; run `doctor`; assert file present and
   row labelled `PROJECT-LOCAL`; no canonical fields invented for it.
5. `test_doctor_dry_run_makes_no_changes` (REQ-09-07) — `os.walk` the chores
   dir before/after a `--dry-run` invocation against a tree with one MISSING
   slug; assert directory listing identical.
6. `test_doctor_json_output_parses` (REQ-09-08) — run `--json`; parse stdout;
   assert it is a list of `{slug, before_status, after_status}` records and
   one entry has the expected status pair.
7. `test_doctor_healthy_tree_is_noop` (REQ-09-02) — seed every canonical slug
   into project; run `doctor`; assert exit 0 and every row HEALTHY/HEALTHY.
8. `test_doctor_subcommand_registered` (REQ-09-01) — invoke
   `gz chores doctor --help`; assert exit 0.

Plus an output-form fixture per `.gzkit/rules/tests.md` (Invariant 3):

- `TestChoresDoctorOutputForm` with `test_doctor_renders_rich_table` —
  invoke `doctor` against a non-empty tree; assert output contains
  Rich-table box-drawing characters (`╭`, `┬`, `│`, `╰`).

Run: `uv run -m unittest tests.commands.test_chores -v 2>&1 | tail -30`.
Expect each new test to RED (NameError on `chores_doctor` symbol or
parser-not-found exit code).

### Step 2 — GREEN: implement `chores_doctor` and register the subcommand

In `src/gzkit/commands/chores.py`:

```python
class _SlugStatus(str, Enum):  # actually Literal alias since stdlib pref
    HEALTHY = "HEALTHY"
    MISSING = "MISSING"
    DAMAGED = "DAMAGED"
    PROJECT_LOCAL = "PROJECT-LOCAL"
```

Add the following functions, each <=50 lines:

- `_canonical_slug_names() -> set[str]` — wraps `_iter_canonical_chore_slugs`.
- `_classify_slug(slug, *, in_canonical, in_project, project_dir) -> str` —
  returns one of the four status strings. DAMAGED iff any of the three
  per-slug files is missing or any `acceptance.json` is unparseable. HEALTHY
  iff all three present and acceptance.json parses.
- `_repair_damaged_slug(slug, project_dir)` — for each missing/malformed file
  among `_PER_SLUG_FILES`, copy bytes from
  `importlib.resources.files("gzkit.chores").joinpath(slug, filename)`. Never
  touches `proofs/`.
- `chores_doctor(*, dry_run: bool, json_output: bool) -> None` —
  1. Enumerate canonical and project slug sets.
  2. Classify each, recording `before_status`.
  3. If not `dry_run`: for `MISSING`, call
     `scaffold_core_chores(project_root, config, skip_existing=True)` once
     (it scaffolds every missing slug at once); for `DAMAGED`, call
     `_repair_damaged_slug` per slug.
  4. Re-classify after repair to derive `after_status`. (For `dry_run`,
     `after_status` is the simulated status: MISSING → HEALTHY, DAMAGED →
     HEALTHY, HEALTHY/PROJECT-LOCAL unchanged.)
  5. Render Rich table (default) or JSON (`--json`). Footer: counts of
     `repaired`, `healthy`, `project-local`, `damaged-remaining`.

In `src/gzkit/cli/parser_maintenance.py`:

- Add `"chores_doctor": "gzkit.commands.chores"` to the `_LAZY_TARGETS` map.
- Inside `_register_chores_parsers`, after `audit`, register `doctor`:
  - `--dry-run` (action="store_true")
  - `--json` (action="store_true", dest="json_output" to avoid clobbering
    Python's `json` module name)
  - `set_defaults(func=lambda a: _lazy("chores_doctor")(dry_run=a.dry_run,
    json_output=a.json_output))`
- Update the `_chores_help_examples` to include
  `"gz chores doctor"` for parity with manpage examples (only if the
  existing epilog list is referenced in tests; otherwise skip cosmetic
  updates).

Run tests after each substantive edit; expect each RED → GREEN.

### Step 3 — Sanity / quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_chores -v
uv run gz arb step --name unittest -- uv run -m unittest -q   # full sweep
uv run gz covers OBPI-0.0.21-09-chores-doctor-command --json
```

Add `@covers("REQ-0.0.21-09-NN")` decorators to each new test; verify the
coverage parity gate (`uncovered_reqs == 0`) before Stage 4.

### Step 4 — Verification (per brief)

Re-run the brief's verification commands:

```bash
uv run gz chores doctor --help 2>&1 | head -10
uv run gz chores doctor 2>&1 | tail -10
rm -rf .gzkit/chores/coverage-40pct
uv run gz chores doctor 2>&1 | tail -10
test -f .gzkit/chores/coverage-40pct/CHORE.md && echo "repaired"

rm -rf .gzkit/chores/coverage-40pct
uv run gz chores doctor --dry-run 2>&1 | tail -5
test ! -e .gzkit/chores/coverage-40pct && echo "dry-run made no changes"

uv run gz chores doctor --json | uv run python -c \
  "import sys, json; json.load(sys.stdin); print('valid JSON')"
```

After verification finishes successfully, the project tree must end the run
with `coverage-40pct` restored (since the live tree was modified); the final
verification step should leave the project in a clean state for Stage 5.

## Verification

| Check | Command |
|---|---|
| Lint | `uv run gz arb ruff` |
| Typecheck | `uv run gz arb typecheck` |
| OBPI tests | `uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_chores -v` |
| Full unittest | `uv run gz arb step --name unittest -- uv run -m unittest -q` |
| Coverage parity | `uv run gz covers OBPI-0.0.21-09-chores-doctor-command --json` (uncovered_reqs == 0) |
| MkDocs | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` |

## Notes

### Destination-in-mind disclosure

The chosen approach: per-file repair function for DAMAGED slugs walking
`importlib.resources.files("gzkit.chores")` directly, with `MISSING` repair
routed through `scaffold_core_chores(skip_existing=True)`. This was the
approach formed during exploration of `src/gzkit/chores/__init__.py:46-96`
when I observed that `skip_existing=True` skips entire directories, so
DAMAGED repair (sub-directory file restore) cannot route through it without
either (a) deleting the slug dir first, which risks `proofs/` content, or
(b) extending the scaffolder, which is denied by the brief.

### Rejected alternatives

1. **Delete-and-rescaffold for DAMAGED:** Move slug dir aside (preserve
   `proofs/`), call scaffold_core_chores, restore `proofs/`. Rejected:
   destructive, fragile under interrupt, and re-scaffolds the file even when
   only one of three files is missing.
2. **Extend `scaffold_core_chores` to support file-level repair:** Cleanest
   architecturally but edits a denied path (`src/gzkit/chores/__init__.py`).
   Brief explicitly assigns scaffolder ownership to OBPI-05.
3. **Add a new helper in `gzkit.chores` package:** Same denied-path issue.
4. **Make `doctor` a thin wrapper that always calls scaffold + over-writes:**
   Violates REQ-09-06 (untouched project-local) and risks proofs/ content
   if the scaffolder were ever to grow a `force=True` mode.

The chosen approach is minimal, stays inside Allowed Paths, and treats the
3-line per-file `target.write_bytes(source.read_bytes())` as mechanical file
restoration (not "scaffolder logic"), which is the narrow interpretation
the brief's "MUST NOT reimplement scaffolder logic" admits.

### Risk register

- **Rich table column names:** Must match OBPI-06 manpage. Manpage shows a
  three-column table (`Slug`, `Before`, `After`). Plan adopts those names
  verbatim.
- **`--json` flag name collision:** `argparse` dest is `json_output` to avoid
  shadowing the `json` stdlib import inside the handler.
- **Test isolation:** Tests must use `runner.isolated_filesystem()` and
  `_quick_init()` so `.gzkit/chores/` is project-scaffolded before doctor
  runs; otherwise the canonical-from-package side could leak into assertions.
