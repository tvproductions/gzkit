# Plan: OBPI-0.0.32-02-skills-scaffolder-refactor

## OBPI
OBPI-0.0.32-02-skills-scaffolder-refactor

## Destination-in-mind disclosure (Step 6a)
Entering this plan: the intended approach is to mirror `_iter_canonical_chore_slugs` exactly, replace the `CORE_SKILLS` loop in `scaffold_core_skills` with a `_iter_canonical_skill_slugs` loop that copies bytes from the package resource, retain `skill.md` with a repurposing comment (since `scaffold_skill` still references it), and file a GHI for that residual dependency.

## Rejected alternatives
1. Delete `skill.md` immediately — rejected because `scaffold_skill` still calls `render_template("skill", ...)` for custom skill creation; deletion would break that path without an explicit code change that is out of scope.
2. Keep copying via `scaffold_skill` (only change the source inside `scaffold_skill`) — rejected because the chores precedent bypasses the per-skill scaffolder entirely; copying directly from the resource is cleaner and removes intermediate logic.
3. Copy only `CORE_SKILLS` subset from the package — rejected because the chore pattern copies ALL canonical slugs; `scaffold_core_skills` should follow the same contract.

## Prerequisite check (confirmed before plan)
- OBPI-01 landed: 70 SKILL.md files at `src/gzkit/skills/<slug>/`; `importlib.resources.files("gzkit.skills")` returns 70 dirs-with-SKILL.md ✓
- `src/gzkit/templates/skill.md` exists ✓
- `src/gzkit/chores/__init__.py` exists (precedent) ✓

## Files this plan modifies
- `src/gzkit/skills/__init__.py`
- `src/gzkit/templates/skill.md` (add repurposing comment — NOT deleted)
- `tests/test_skills.py`
- `docs/user/manpages/init.md`
- `.gzkit/rules/skill-surface-sync.md`

## Steps

### Task 1: TDD Red — write failing tests for REQ-0.0.32-02-01 through -06

In `tests/test_skills.py`, add class `TestSkillsScaffolderRefactor` with:

- `test_iter_canonical_skill_slugs_exists` (`@covers("REQ-0.0.32-02-01")`) — import `_iter_canonical_skill_slugs` from `gzkit.skills`; assert it is callable.
- `test_iter_canonical_skill_slugs_returns_70` (`@covers("REQ-0.0.32-02-01")`) — call `_iter_canonical_skill_slugs()`; assert `sum(1 for _ in it)` equals 70.
- `test_scaffold_core_skills_copies_canonical_content` (`@covers("REQ-0.0.32-02-02")`) — scaffold into a `tempfile.TemporaryDirectory`; read a sample SKILL.md; assert `wc -l` equivalent > 5 lines (refuting one-line stub).
- `test_skill_template_retained_with_comment` (`@covers("REQ-0.0.32-02-03")`) — assert `src/gzkit/templates/skill.md` exists AND its content contains the repurposing comment token `scaffold_skill`.
- `test_skip_existing_preserves_operator_edit` (`@covers("REQ-0.0.32-02-04")`) — scaffold into tempdir; overwrite a SKILL.md with sentinel content; re-scaffold with `skip_existing=True`; assert sentinel is preserved.
- `test_scaffold_core_skills_signature_stable` (`@covers("REQ-0.0.32-02-05")`) — use `inspect.signature` to assert `project_root`, `config`, `skip_existing` all present.
- `test_scaffolded_content_is_multi_line` (`@covers("REQ-0.0.32-02-06")`) — scaffold into tempdir; assert every SKILL.md written has `>` 5 lines.

Also update `TestSkillTemplatePreserved` class: replace
`test_skill_template_still_exists` (which asserts file exists, tagged
REQ-0.0.32-01-07) with a new test tagged `@covers("REQ-0.0.32-02-03")` that
asserts the file still exists (retained, not deleted) AND contains repurposing
comment. Remove the old guard test.

Run `uv run -m unittest tests.test_skills -v` → expect failures for new tests.

### Task 2: Add `_iter_canonical_skill_slugs()` to `src/gzkit/skills/__init__.py`

Add imports at top of file (after existing imports):
```python
import importlib.resources
from collections.abc import Iterator
from importlib.resources.abc import Traversable
```

Add function after the existing `_CANONICAL_RESOURCE = "gzkit.skills"` constant (insert before `CORE_SKILLS`):
```python
_CANONICAL_RESOURCE = "gzkit.skills"


def _iter_canonical_skill_slugs() -> Iterator[Traversable]:
    """Yield each canonical skill-slug directory (one per slug)."""
    root = importlib.resources.files(_CANONICAL_RESOURCE)
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("__"):
            continue
        if not entry.joinpath("SKILL.md").is_file():
            continue
        yield entry
```

Run `uv run ruff check . --fix && uv run ruff format .` after this edit.

### Task 3: Refactor `scaffold_core_skills` body

Replace the body of `scaffold_core_skills` (keep signature and docstring):

OLD body:
```python
    created = []
    for dir_name, kwargs in CORE_SKILLS.items():
        if skip_existing:
            existing = project_root / config.paths.skills / dir_name / "SKILL.md"
            if existing.exists():
                continue
        skill_file = scaffold_skill(
            project_root,
            dir_name,
            config.paths.skills,
            **kwargs,
        )
        created.append(skill_file)
    return created
```

NEW body (mirrors `scaffold_core_chores`):
```python
    skills_dir = project_root / config.paths.skills
    skills_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for slug_resource in _iter_canonical_skill_slugs():
        slug = slug_resource.name
        target_dir = skills_dir / slug
        if skip_existing and (target_dir / "SKILL.md").exists():
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        skill_src = slug_resource.joinpath("SKILL.md")
        skill_dst = target_dir / "SKILL.md"
        skill_dst.write_bytes(skill_src.read_bytes())
        created.append(skill_dst)

    return created
```

Run `uv run ruff check . --fix && uv run ruff format .` after.

### Task 4: Add repurposing comment to `src/gzkit/templates/skill.md`

Insert at the very top of `skill.md` (before the frontmatter `---`):
```
<!-- repurposing-note: This template is retained for scaffold_skill (custom
     non-canonical skill creation). scaffold_core_skills no longer uses this
     template as of OBPI-0.0.32-02 — it copies canonical content directly
     from importlib.resources.files("gzkit.skills"). Residual dependency
     tracked in follow-up GHI. -->
```

File a GHI: "scaffold_skill residual dependency on templates/skill.md after OBPI-0.0.32-02"

### Task 5: Update `docs/user/manpages/init.md`

Add a new section after "## Re-run (Repair Mode)":

```markdown
## Skills Scaffolding

`gz init` copies canonical SKILL.md content from the wheel's package surface
(`importlib.resources.files("gzkit.skills")`) into the project's
`.gzkit/skills/<slug>/SKILL.md`. All ~70 canonical skills are scaffolded;
existing files are preserved (`skip_existing=True` semantics).

Once written, `.gzkit/skills/` becomes the **project canonical source-of-truth**
— the same editing invariant as every gzkit-or-adopter repo. Edit there; run
`gz agent sync control-surfaces` to propagate to vendor mirrors.

Re-running `gz init` (repair mode) adds any new canonical skills from the
installed wheel version without overwriting operator-edited files.
```

### Task 6: Update `.gzkit/rules/skill-surface-sync.md`

Append a new section at the end of the rule file:

```markdown
## Bootstrap semantics (`gz init` and `gz init --update`)

On first init, `gz init` populates the project's `.gzkit/skills/<slug>/SKILL.md`
from the wheel's package surface (`importlib.resources.files("gzkit.skills")`).
This is the *one-time bootstrap source*: after init, the project's `.gzkit/skills/`
is the authored canonical surface for that project, and the "Edit `.gzkit/` first"
rule binds from that point forward.

`gz init --update` (OBPI-0.0.32-05, not yet landed) will provide version-aware
refresh semantics for the adopter's `.gzkit/` from the wheel.
```

Bump rule-version: `0.2.0` → `0.3.0` in both the `<!-- rule-version: X.Y.Z -->` comment and the visible `> **Rule version:** \`X.Y.Z\`` block quote. Add rationale: "added bootstrap-semantics section for gz init wheel-copy behavior (OBPI-0.0.32-02)."

### Task 7: Run QA checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
```

Smoke verification:
```bash
uv run python -c "from gzkit.skills import _iter_canonical_skill_slugs; print(sum(1 for _ in _iter_canonical_skill_slugs()))"  # expect 70
```

## Verification commands (from brief)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

uv run python -c "from gzkit.skills import _iter_canonical_skill_slugs; print(sum(1 for _ in _iter_canonical_skill_slugs()))"  # expect 70
uv run python -c "import importlib.resources; r=importlib.resources.files('gzkit.skills'); print(sum(1 for e in r.iterdir() if e.is_dir() and not e.name.startswith('__')))"  # expect 70
```

## Notes

- `src/gzkit/commands/init_cmd.py` is DENIED — not touched.
- `CORE_SKILLS` dict is retained (backward compat; still exported via `__all__`; used by `scaffold_skill` callers).
- `render_template` import is retained (still used by `scaffold_skill` fallback path).
- `scaffold_skill` is NOT changed — only `scaffold_core_skills` body changes.
- Scope collision advisories (ADR-0.5.0, ADR-0.31.0, etc.) are pool/future ADRs with no active locks — not blocking.
