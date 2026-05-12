# Plan: OBPI-0.0.32-04-rules-scaffolder-authoring

**OBPI:** OBPI-0.0.32-04-rules-scaffolder-authoring
**Parent ADR:** ADR-0.0.32-canonical-surface-packaging
**Lane:** Heavy
**Date:** 2026-05-12

## Context

OBPI-03 has landed: `src/gzkit/rules/__init__.py` exists; both `.gzkit/rules/`
and `src/gzkit/rules/` carry 20 `.md` files (byte-parity). `CORE_RULES`,
`_iter_canonical_rule_slugs`, and `scaffold_core_rules` do not yet exist.

The direct sibling pattern is `src/gzkit/skills/__init__.py` (post-OBPI-02)
for `CORE_SKILLS`/`scaffold_core_skills` and `src/gzkit/chores/__init__.py`
for `scaffold_core_chores`. Rules differ structurally: rules are flat `.md`
files (not slug directories with SKILL.md), so `_iter_canonical_rule_slugs`
enumerates `.md` entries rather than subdirectories.

**Advisory (plan-audit):** `.gzkit/rules/` has 20 .md files, not 14 as the
brief states. Tests MUST use `len(CORE_RULES)` / `sum(1 for _ in
_iter_canonical_rule_slugs())` for count assertions. Whether `AGENTS.md` is
a canonical rule slug or a package-internal file is a decision at step 1.

**Destination-in-mind:** `CORE_RULES` = list of slugs (like `list[str]`),
`_iter_canonical_rule_slugs` enumerates `.md` entries skipping `AGENTS.md` and
non-.md, `scaffold_core_rules` writes each slug's `.md` bytes to
`.gzkit/rules/<slug>.md`, wired after `scaffold_core_skills` in both
`_scaffold_project_skeleton` and `_repair_missing_artifacts`.

**Rejected alternatives:**
- Dict-of-slug-to-metadata (like CORE_SKILLS): more overhead than needed for
  flat files with no harness/trigger metadata; list-of-slugs is sufficient.
- Including `AGENTS.md` in canonical rule slugs: it is a package-internal
  agent contract for the `gzkit.rules` module, not an operator-facing rule;
  excluding it keeps the scaffolded `.gzkit/rules/` set clean.

## Files

### Created
- None (all changes are additions to existing files)

### Modified
- `src/gzkit/rules/__init__.py` — add CORE_RULES, _iter_canonical_rule_slugs, scaffold_core_rules
- `src/gzkit/commands/init_cmd.py` — import and invoke scaffold_core_rules
- `tests/test_rules.py` — new test file for CORE_RULES, scaffold_core_rules
- `tests/commands/test_init.py` — integration tests for init_cmd wiring
- `docs/user/manpages/init.md` — mention rule scaffolding
- `docs/user/runbook.md` — rules surface section
- `.gzkit/rules/skill-surface-sync.md` — re-affirm "Edit .gzkit/ first" + gz init bootstrap note

## Steps

### Step 1: TDD RED — Write failing tests

In `tests/test_rules.py` (new file), author tests that FAIL before implementation:

```python
# test CORE_RULES is a list with at least 1 slug (not 0, not None)
# test all slugs in CORE_RULES are strings and exist as .md in src/gzkit/rules/
# test _iter_canonical_rule_slugs returns entries matching CORE_RULES (same count)
# test scaffold_core_rules writes files to a fresh tempdir
# test scaffold_core_rules with skip_existing=True preserves operator-edited file
```

In `tests/commands/test_init.py`, add tests that FAIL:

```python
# test _scaffold_project_skeleton produces .gzkit/rules/ content in a tempdir
# test _repair_missing_artifacts(skip_existing=True) adds missing rule files
```

Verify all new tests fail (RED): `uv run -m unittest tests.test_rules tests.commands.test_init -v`

### Step 2: Author CORE_RULES and _iter_canonical_rule_slugs

In `src/gzkit/rules/__init__.py`, add after existing imports:

```python
_CANONICAL_RULES_RESOURCE = "gzkit.rules"

def _iter_canonical_rule_slugs() -> Iterator[Traversable]:
    """Yield each canonical rule .md entry shipped with the wheel.

    Mirrors _iter_canonical_skill_slugs. Enumerates entries under
    importlib.resources.files("gzkit.rules"), yielding .md files that are
    not AGENTS.md (package-internal agent contract, not an operator rule).
    """
    root = importlib.resources.files(_CANONICAL_RULES_RESOURCE)
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        if not entry.name.endswith(".md"):
            continue
        if entry.name == "AGENTS.md":
            continue
        yield entry

CORE_RULES: list[str] = [
    e.name[:-3]  # strip .md suffix
    for e in sorted(_iter_canonical_rule_slugs(), key=lambda e: e.name)
]
```

Note: `_iter_canonical_rule_slugs` must be defined before `CORE_RULES` at module level;
add required imports (`importlib.resources`, `Iterator`, `Traversable`) at top of file.

### Step 3: Author scaffold_core_rules

In `src/gzkit/rules/__init__.py`, add:

```python
def scaffold_core_rules(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    skip_existing: bool = False,
) -> list[Path]:
    """Scaffold all canonical rules into <project_root>/<config.paths.rules>.

    Mirrors scaffold_core_skills / scaffold_core_chores semantics.
    Each canonical rule .md is copied from importlib.resources into the
    adopter's .gzkit/rules/<slug>.md. skip_existing=True preserves
    operator-edited files; used by repair mode.

    Returns list of Path objects for newly-created files.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    rules_dir = project_root / config.paths.rules
    rules_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for slug_resource in _iter_canonical_rule_slugs():
        target = rules_dir / slug_resource.name
        if skip_existing and target.exists():
            continue
        target.write_bytes(slug_resource.read_bytes())
        created.append(target)
    return created
```

Check `config.paths.rules` is the correct attribute name (should be `.gzkit/rules`).

### Step 4: Wire scaffold_core_rules into init_cmd

In `src/gzkit/commands/init_cmd.py`:

**Import:** Add `from gzkit.rules import scaffold_core_rules` alongside other scaffold imports.

**In `_scaffold_project_skeleton`** (the fresh init path), after the `scaffold_core_skills` call block:

```python
    # Scaffold canonical rules
    rules = scaffold_core_rules(project_root, config)
    console.print(f"  Scaffolded {len(rules)} core rules")
```

**In `_repair_missing_artifacts`**, after the `new_skills` block, mirroring
the skills repair pattern with `skip_existing=True`:

```python
    # Repair rules — scaffold any core rules added in newer gzkit versions
    new_rules = scaffold_core_rules(project_root, config, skip_existing=not dry_run)
    if dry_run:
        repaired.extend([f"Would scaffold rule: {r.name}" for r in
                         _missing_canonical_rules(project_root, config)])
    elif new_rules:
        for rule_path in new_rules:
            repaired.append(f"Scaffolded new rule: {rule_path.name}")
```

Note: `_missing_canonical_rules` helper for dry-run reporting may be optional;
check if the skills repair uses an equivalent and mirror if so.

### Step 5: Update docs

**`docs/user/manpages/init.md`** — Add a "Rule files" bullet under the scaffolded
artifacts section, mirroring the skills/chores/personas bullets.

**`docs/user/runbook.md`** — Add a brief Rules surface section (2-4 lines) in
the appropriate "Scaffolded surfaces" area, noting that `.gzkit/rules/` is
populated by `gz init`.

**`.gzkit/rules/skill-surface-sync.md`** — At the end, add a section:

```
## gz init bootstrap

`gz init` populates the adopter's `.gzkit/rules/` from the wheel's package
surface (`importlib.resources.files("gzkit.rules")`). Once written, the
adopter's `.gzkit/rules/` is their project canonical source-of-truth. Always
edit `.gzkit/rules/<slug>.md` first; vendor mirrors (`.claude/rules/`) are
regenerated by `gz agent sync control-surfaces`.
```

### Step 6: TDD GREEN + quality gates

```bash
uv run -m unittest tests.test_rules tests.commands.test_init -v   # must go green
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
```

Fix any ruff/ty issues. All checks must exit 0.

### Step 7: Present OBPI Acceptance Ceremony

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

python -c "from gzkit.rules import CORE_RULES, scaffold_core_rules, _iter_canonical_rule_slugs; print('imports OK', len(CORE_RULES), sum(1 for _ in _iter_canonical_rule_slugs()))"
```

## Notes

- Rules are flat .md files (not directories); `_iter_canonical_rule_slugs` uses
  `entry.is_file()` + `.endswith(".md")` unlike skill slugs which use `entry.is_dir()`.
- `AGENTS.md` in `src/gzkit/rules/` is package-internal; exclude from enumeration.
- `complexity-thresholds.json` is already excluded (non-.md).
- `GzkitConfig.paths.rules` — verify this attribute exists before wiring; it should
  be `.gzkit/rules` per the manifest.
- Do NOT edit `pyproject.toml` (wheel includes = OBPI-06).
- Do NOT edit `features/` (BDD = OBPI-06).
