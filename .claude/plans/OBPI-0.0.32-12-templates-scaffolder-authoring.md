# Plan: OBPI-0.0.32-12 — Templates Scaffolder Authoring

**OBPI:** `OBPI-0.0.32-12-templates-scaffolder-authoring`
**Parent ADR:** `ADR-0.0.32-canonical-surface-packaging`
**Lane:** Heavy | **Kind:** Foundation
**Date:** 2026-05-12

## Context

OBPI-11 has landed: 11 canonical template `.md` files now exist at both
`src/gzkit/templates/<name>.md` (wheel-shipping) and `.gzkit/templates/<name>.md`
(authored canonical). `src/gzkit/templates/__init__.py` exists with `load_template`,
`render_template`, `SafeDict`, `get_template_path`, `list_templates`.

This OBPI authors the scaffolding surface that brings the templates surface into
the same canonical-routing model as skills/rules/personas/chores:
- `CORE_TEMPLATES` registry
- `_iter_canonical_template_slugs()` enumerator
- `scaffold_core_templates()` scaffolder
- `render_template()` updated to project-first → package-fallback resolution
- Fresh init wires templates scaffolding
- Repair mode wires templates scaffolding with skip_existing=True

## Files

### Modified
- `src/gzkit/templates/__init__.py` — add registry, enumerator, scaffolder; update `render_template()` resolution
- `src/gzkit/commands/init_cmd.py` — wire scaffold_core_templates into fresh init and repair
- `docs/user/manpages/init.md` — add Templates Scaffolding section
- `docs/user/runbook.md` — add templates commands section

### Created
- `tests/test_templates.py` — unit tests for all new surfaces and resolution semantics

## Steps

### Step 1: RED — Write failing tests in tests/test_templates.py

Write tests first (TDD discipline, `.gzkit/rules/tests.md` RGR):

**Test classes to author:**

```python
class TestCoreTemplatesRegistry(unittest.TestCase):
    # test_core_templates_is_list — CORE_TEMPLATES is a list of str
    # test_core_templates_enumerates_all_canonical_slugs — count >= 11
    # test_iter_canonical_template_slugs_count_matches — same count as CORE_TEMPLATES

class TestScaffoldCoreTemplates(unittest.TestCase):
    # Uses tempfile.TemporaryDirectory
    # test_scaffold_writes_all_templates — fresh dir gets all canonical templates
    # test_scaffold_content_byte_identical — written bytes match package resource
    # test_skip_existing_preserves_edits — operator edits not overwritten when skip_existing=True
    # test_skip_existing_false_overwrites — default (skip_existing=False) does overwrite
    # test_returns_list_of_created_paths — return type is list[Path]
    # test_creates_templates_dir — .gzkit/templates/ created if absent

class TestRenderTemplateProjectFirst(unittest.TestCase):
    # Uses tempfile.TemporaryDirectory, os.chdir within the temp dir
    # test_project_first_uses_project_copy — when .gzkit/templates/adr.md exists in CWD tree, render uses it
    # test_package_fallback_used_when_no_project_copy — no project copy → package surface used
    # test_operator_edits_respected — project copy with custom content → rendered output includes edit

class TestInitCmdTemplatesIntegration(unittest.TestCase):
    # test_fresh_init_produces_template_files — gz init in tempdir produces .gzkit/templates/
    # test_repair_adds_missing_templates — repair scaffolds new templates (skip_existing=True)
```

All tests MUST fail at this point (RED gate).

### Step 2: GREEN — Author implementation in src/gzkit/templates/__init__.py

Add after existing imports and before `load_template`:

```python
import importlib.resources
from collections.abc import Iterator
from importlib.resources.abc import Traversable

def _iter_canonical_template_slugs() -> Iterator[Traversable]:
    """Yield each canonical template .md entry shipped with the wheel."""
    root = importlib.resources.files("gzkit.templates")
    for entry in root.iterdir():
        if not entry.is_file():
            continue
        if not entry.name.endswith(".md"):
            continue
        yield entry

CORE_TEMPLATES: list[str] = sorted(entry.name[:-3] for entry in _iter_canonical_template_slugs())
"""Canonical template slugs shipped with the gzkit wheel."""

def scaffold_core_templates(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    skip_existing: bool = False,
) -> list[Path]:
    """Scaffold canonical templates into <project_root>/.gzkit/templates/.
    ...
    """
    templates_dir = project_root / ".gzkit" / "templates"
    templates_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    for slug_resource in _iter_canonical_template_slugs():
        target = templates_dir / slug_resource.name
        if skip_existing and target.exists():
            continue
        target.write_bytes(slug_resource.read_bytes())
        created.append(target)
    return created
```

Update `load_template()` to project-first → package-fallback:

```python
def _find_project_template(name: str) -> Path | None:
    """Walk CWD upward for .gzkit/templates/<name>.md."""
    current = Path.cwd()
    while True:
        candidate = current / ".gzkit" / "templates" / f"{name}.md"
        if candidate.exists():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None

def load_template(name: str) -> str:
    """Load a template — project-first, package-fallback."""
    project_copy = _find_project_template(name)
    if project_copy is not None:
        return project_copy.read_text(encoding="utf-8")
    # Package fallback
    template_dir = files("gzkit.templates")
    template_file = template_dir.joinpath(f"{name}.md")
    return template_file.read_text(encoding="utf-8")
```

Update `__all__` to include `CORE_TEMPLATES`, `scaffold_core_templates`,
`_iter_canonical_template_slugs`.

After implementation: all tests in TestCoreTemplatesRegistry, TestScaffoldCoreTemplates,
TestRenderTemplateProjectFirst should pass (GREEN).

### Step 3: Wire into init_cmd.py

In `init_cmd.py`:

Add import:
```python
from gzkit.templates import scaffold_core_templates
```

In `init()` fresh-init path, after `scaffold_core_personas`:
```python
# Scaffold canonical templates
templates = scaffold_core_templates(project_root, config)
console.print(f"  Scaffolded {len(templates)} core templates")
```

Add `_repair_templates` function (mirrors `_repair_personas`):
```python
def _repair_templates(
    project_root: Path,
    config: GzkitConfig,
    *,
    dry_run: bool,
) -> list[str]:
    """Scaffold new canonical templates, returning per-slug status messages."""
    from gzkit.templates import _iter_canonical_template_slugs  # noqa: PLC0415
    if dry_run:
        templates_dir = project_root / ".gzkit" / "templates"
        return [
            f"Would scaffold template: {entry.name[:-3]}"
            for entry in _iter_canonical_template_slugs()
            if not (templates_dir / entry.name).exists()
        ]
    new_templates = scaffold_core_templates(project_root, config, skip_existing=True)
    return [f"Scaffolded new template: {path.name[:-3]}" for path in new_templates]
```

In `_repair_missing_artifacts`, after `_repair_personas` call:
```python
# Repair templates — scaffold any core templates added in newer gzkit versions
repaired.extend(_repair_templates(project_root, config, dry_run=dry_run))
```

After wiring: TestInitCmdTemplatesIntegration tests should pass (GREEN).

### Step 4: Update docs/user/manpages/init.md

Add section after existing "Personas Scaffolding" section:

```markdown
## Templates Scaffolding

As of OBPI-0.0.32-12, `gz init` copies canonical template `.md` content from the
wheel's package surface (`importlib.resources.files("gzkit.templates")`) into the
project's `.gzkit/templates/<name>.md`. The 11 canonical template slugs are:
`adr`, `adr_pool`, `agents`, `audit`, `audit_plan`, `claude`, `closeout`,
`constitution`, `copilot`, `obpi`, `prd`.

Once written, `.gzkit/templates/` is the **project canonical source-of-truth** for
that project — `render_template()` consults the project copy first when present
(project-first → package-fallback resolution). Operators customize templates there.

Re-running `gz init` (repair mode) adds any new canonical templates delivered by
the installed gzkit version without overwriting existing ones (`skip_existing=True`
semantics). Operator edits to `.gzkit/templates/<name>.md` are preserved.
```

### Step 5: Update docs/user/runbook.md

Add a "Templates" subsection under the `gz init` / surface commands area,
mirroring the existing chores/rules/personas entries.

### Step 6: Run quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

All must exit 0.

## Verification

```bash
python -c "from gzkit.templates import CORE_TEMPLATES, scaffold_core_templates, _iter_canonical_template_slugs; print('imports OK', len(CORE_TEMPLATES), sum(1 for _ in _iter_canonical_template_slugs()))"
# Expect: imports OK 11 11 (or higher if more templates land)

uv run gz covers OBPI-0.0.32-12-templates-scaffolder-authoring --json
# Expect: uncovered_reqs == 0
```

## Notes

- The brief had a defect: Allowed Paths listed `docs/user/manpages/gz-init.md`; the
  actual file is `docs/user/manpages/init.md`. Fixed in the brief before this plan was created.
- Template count is 11 (post-OBPI-11); brief says "13+" — actual count governs.
- `render_template()` call signature stays `render_template(name, **kwargs)` — project-first
  resolution applies to template loading, not the rendering context API.
- `GzkitConfig` param in `scaffold_core_templates` accepted for API symmetry (mirrors personas);
  templates dir is hardcoded as `.gzkit/templates/` (no config-managed path yet).
