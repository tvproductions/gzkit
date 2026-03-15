# AGENTS.md Tidy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce context window bloat ~80% by mirroring `.github/instructions/` to `.claude/rules/`, slimming CLAUDE.md, and compacting the skill catalog with categories.

**Architecture:** `gz agent sync control-surfaces` gains a rules mirror step that converts Copilot instruction frontmatter (`applyTo`) to Claude rules frontmatter (`paths`). CLAUDE.md becomes a thin pointer (~40 lines). The skill catalog switches from flat alphabetical to categorized name-only groups (~20 lines). JSON Schema files validate canonical frontmatter.

**Tech Stack:** Python 3.13, stdlib `unittest`, `json`, `pathlib`, YAML frontmatter parsing (existing `_extract_skill_description` pattern), JSON Schema files.

**Spec:** `docs/superpowers/specs/2026-03-15-agents-md-tidy-design.md`

---

## Chunk 1: Categorized Skill Catalog

### Task 1: Add `category` field to `collect_skills_catalog()`

**Files:**
- Modify: `src/gzkit/sync.py:425-456` (`collect_skills_catalog`)
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test**

In `tests/test_sync.py`, add:

```python
def test_collect_skills_catalog_reads_category_from_frontmatter(self) -> None:
    """Skill catalog collection extracts the category field from frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        config = GzkitConfig(project_name="gzkit-test")

        skill_dir = project_root / config.paths.skills / "gz-plan"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: gz-plan\ndescription: Create ADR artifacts.\n"
            "category: adr-lifecycle\nlifecycle_state: active\n"
            "owner: gzkit-governance\nlast_reviewed: 2026-03-15\n---\n"
        )

        skills = collect_skills_catalog(project_root, config.paths.skills)
        self.assertEqual(len(skills), 1)
        self.assertEqual(skills[0]["category"], "adr-lifecycle")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run -m unittest tests.test_sync.TestSync.test_collect_skills_catalog_reads_category_from_frontmatter -v`
Expected: FAIL with `KeyError: 'category'`

- [ ] **Step 3: Implement category extraction in `collect_skills_catalog()`**

Modify `src/gzkit/sync.py:425-456`. Add a helper `_extract_skill_frontmatter_field()` and update `collect_skills_catalog()` to include `category`:

```python
def _extract_skill_frontmatter_field(skill_file: Path, field: str) -> str:
    """Extract a named field from SKILL.md frontmatter.

    Args:
        skill_file: Path to SKILL.md.
        field: Frontmatter key to extract.

    Returns:
        Field value or empty string if not found.
    """
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return ""

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    for raw in lines[1:]:
        stripped = raw.strip()
        if stripped == "---":
            break
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key.strip() == field:
            return value.strip().strip("\"'")
    return ""
```

Update `collect_skills_catalog()` to add category to each skill dict:

```python
skills.append(
    {
        "name": skill_dir.name,
        "description": _extract_skill_description(skill_file),
        "category": _extract_skill_frontmatter_field(skill_file, "category"),
        "path": skill_file.relative_to(project_root).as_posix(),
    }
)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run -m unittest tests.test_sync.TestSync.test_collect_skills_catalog_reads_category_from_frontmatter -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/sync.py tests/test_sync.py
git commit -m "feat(sync): extract category field from SKILL.md frontmatter"
```

### Task 2: Add categorized rendering to `render_skills_catalog()`

**Files:**
- Modify: `src/gzkit/sync.py:459-474` (`render_skills_catalog`)
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test for categorized output**

```python
def test_render_skills_catalog_categorized_groups_by_category(self) -> None:
    """Categorized renderer groups skills under category headers."""
    skills = [
        {"name": "gz-plan", "description": "Create ADR.", "category": "adr-lifecycle", "path": ".gzkit/skills/gz-plan/SKILL.md"},
        {"name": "lint", "description": "Run linting.", "category": "code-quality", "path": ".gzkit/skills/lint/SKILL.md"},
        {"name": "gz-attest", "description": "Record attestation.", "category": "adr-lifecycle", "path": ".gzkit/skills/gz-attest/SKILL.md"},
    ]
    result = render_skills_catalog(skills, categorized=True)
    self.assertIn("#### ADR Lifecycle", result)
    self.assertIn("#### Code Quality", result)
    self.assertIn("`gz-plan`", result)
    self.assertIn("`gz-attest`", result)
    self.assertIn("`lint`", result)
    # Should NOT contain full descriptions or paths
    self.assertNotIn("Create ADR.", result)
    self.assertNotIn(".gzkit/skills/", result)
```

- [ ] **Step 2: Write the failing test for uncategorized fallback**

```python
def test_render_skills_catalog_categorized_shows_uncategorized_for_missing_category(self) -> None:
    """Skills without a category field appear under Uncategorized."""
    skills = [
        {"name": "gz-plan", "description": "Create ADR.", "category": "adr-lifecycle", "path": ".gzkit/skills/gz-plan/SKILL.md"},
        {"name": "orphan-skill", "description": "No category.", "category": "", "path": ".gzkit/skills/orphan-skill/SKILL.md"},
    ]
    result = render_skills_catalog(skills, categorized=True)
    self.assertIn("#### ADR Lifecycle", result)
    self.assertIn("#### Uncategorized", result)
    self.assertIn("`orphan-skill`", result)
```

- [ ] **Step 3: Write the failing test that flat mode still works**

```python
def test_render_skills_catalog_flat_mode_preserves_existing_format(self) -> None:
    """Non-categorized rendering preserves the existing flat bullet format."""
    skills = [
        {"name": "lint", "description": "Run linting.", "category": "code-quality", "path": ".gzkit/skills/lint/SKILL.md"},
    ]
    result = render_skills_catalog(skills, categorized=False)
    self.assertIn("- `lint`: Run linting. (`.gzkit/skills/lint/SKILL.md`)", result)
```

- [ ] **Step 4: Run tests to verify they fail**

Run: `uv run -m unittest tests.test_sync -v -k categorized`
Expected: FAIL — `render_skills_catalog()` does not accept `categorized` parameter

- [ ] **Step 5: Implement categorized rendering**

Replace `render_skills_catalog()` in `src/gzkit/sync.py:459-474`:

```python
# Display names for category slugs, in desired render order.
SKILL_CATEGORY_ORDER: list[tuple[str, str]] = [
    ("adr-lifecycle", "ADR Lifecycle"),
    ("adr-operations", "ADR Operations"),
    ("adr-audit", "ADR Audit & Closeout"),
    ("obpi-pipeline", "OBPI Pipeline"),
    ("governance-infrastructure", "Governance Infrastructure"),
    ("agent-operations", "Agent & Repository Operations"),
    ("code-quality", "Code Quality"),
    ("cross-repository", "Cross-Repository"),
]

_CATEGORY_DISPLAY: dict[str, str] = dict(SKILL_CATEGORY_ORDER)
_CATEGORY_SORT: dict[str, int] = {slug: i for i, (slug, _) in enumerate(SKILL_CATEGORY_ORDER)}


def render_skills_catalog(skills: list[dict[str, str]], *, categorized: bool = True) -> str:
    """Render a markdown skill catalog.

    Args:
        skills: Skill metadata records (must include 'name', 'description', 'category', 'path').
        categorized: If True, group by category with compact name-only format.
            If False, emit flat bullet list with full descriptions (legacy).

    Returns:
        Markdown catalog text.
    """
    if not skills:
        return "- No local skills found. Create one with `gz skill new <name>`."

    if not categorized:
        lines = []
        for skill in skills:
            lines.append(f"- `{skill['name']}`: {skill['description']} (`{skill['path']}`)")
        return "\n".join(lines)

    # Group by category.
    groups: dict[str, list[str]] = {}
    for skill in skills:
        cat = skill.get("category", "").strip() or "uncategorized"
        groups.setdefault(cat, []).append(f"`{skill['name']}`")

    lines = []
    # Render known categories in order.
    for slug, display in SKILL_CATEGORY_ORDER:
        if slug in groups:
            lines.append(f"#### {display}")
            lines.append(", ".join(sorted(groups.pop(slug))))
            lines.append("")

    # Render uncategorized last.
    for slug in sorted(groups):
        display = _CATEGORY_DISPLAY.get(slug, "Uncategorized")
        lines.append(f"#### {display}")
        lines.append(", ".join(sorted(groups[slug])))
        lines.append("")

    lines.append("For details on any skill, read its `SKILL.md` in `.gzkit/skills/<skill-name>/`.")
    return "\n".join(lines)
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run -m unittest tests.test_sync -v -k categorized`
Expected: all 3 new tests PASS

- [ ] **Step 7: Run full test suite to check no regressions**

Run: `uv run -m unittest tests.test_sync -v`
Expected: all existing tests still PASS (flat format is default=True now, so existing tests that check `{skills_catalog}` content will see categorized output — update `test_sync_includes_skills_in_generated_surfaces` and `test_sync_skills_catalog_uses_frontmatter_description` assertions if needed)

- [ ] **Step 8: Commit**

```bash
git add src/gzkit/sync.py tests/test_sync.py
git commit -m "feat(sync): categorized skill catalog renderer with uncategorized fallback"
```

### Task 3: Add `category` frontmatter to all 49 SKILL.md files

**Files:**
- Modify: 49x `.gzkit/skills/*/SKILL.md`

- [ ] **Step 1: Write a script to batch-add category field**

Use the category mapping from the spec. For each skill, insert `category: <slug>` after the `description:` line in frontmatter. This is a one-time batch operation.

Category mapping (from spec):

```
adr-lifecycle: gz-plan, gz-adr-create, gz-adr-promote, gz-adr-status, gz-adr-eval, gz-closeout, gz-attest
adr-operations: gz-adr-check, gz-adr-sync, gz-adr-recon, gz-adr-map, gz-adr-autolink, gz-adr-verification, gz-adr-emit-receipt, gz-adr-manager
adr-audit: gz-adr-audit, gz-adr-closeout-ceremony, gz-audit
obpi-pipeline: gz-specify, gz-obpi-brief, gz-obpi-pipeline, gz-obpi-sync, gz-obpi-reconcile, gz-obpi-audit, gz-plan-audit
governance-infrastructure: gz-init, gz-constitute, gz-prd, gz-interview, gz-gates, gz-validate, gz-implement, gz-state, gz-status
agent-operations: gz-agent-sync, gz-session-handoff, gz-register-adrs, gz-migrate-semver, gz-check-config-paths, gz-tidy, git-sync
code-quality: lint, format, test, gz-typecheck, gz-check, gz-arb, gz-cli-audit
cross-repository: airlineops-parity-scan
```

For each skill directory in `.gzkit/skills/`, read its `SKILL.md`, find the frontmatter, insert `category: <slug>` after the `description:` line. If the skill is not in the mapping, insert `category: uncategorized` (should not happen if mapping is complete).

- [ ] **Step 2: Verify all 49 skills have category field**

Run: `grep -c "^category:" .gzkit/skills/*/SKILL.md | grep -v ":1$"` — should return nothing (all files have exactly 1 category line).

- [ ] **Step 3: Run `uv run gz agent sync control-surfaces` to regenerate**

Verify AGENTS.md now shows categorized output.

- [ ] **Step 4: Commit**

```bash
git add .gzkit/skills/
git commit -m "feat(skills): add category frontmatter to all 49 SKILL.md files"
```

---

## Chunk 2: Rules Mirroring

### Task 4: Implement `sync_claude_rules()`

**Files:**
- Modify: `src/gzkit/sync.py` (add new function after `sync_claude_md` ~line 1100)
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test for basic mirroring**

```python
def test_sync_claude_rules_mirrors_instructions_to_claude_rules(self) -> None:
    """Instructions from .github/instructions/ are mirrored to .claude/rules/."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "tests.instructions.md").write_text(
            '---\napplyTo: "tests/**"\n---\n\n# Test Policy\n\nUse unittest.\n'
        )

        sync_claude_rules(project_root)

        rules_file = project_root / ".claude" / "rules" / "tests.md"
        self.assertTrue(rules_file.exists())
        content = rules_file.read_text(encoding="utf-8")
        self.assertIn("paths:", content)
        self.assertIn('  - "tests/**"', content)
        self.assertIn("# Test Policy", content)
        self.assertIn("Use unittest.", content)
```

- [ ] **Step 2: Write the failing test for unconditional conversion**

```python
def test_sync_claude_rules_strips_frontmatter_for_universal_rules(self) -> None:
    """Instructions with applyTo: '**/*' become unconditional rules (no frontmatter)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "governance_core.instructions.md").write_text(
            '---\napplyTo: "**/*"\n---\n\n# Governance Core\n\nRead AGENTS.md.\n'
        )

        sync_claude_rules(project_root)

        rules_file = project_root / ".claude" / "rules" / "governance_core.md"
        content = rules_file.read_text(encoding="utf-8")
        # Should NOT have paths frontmatter — unconditional
        self.assertNotIn("paths:", content)
        self.assertNotIn("---", content)
        self.assertIn("# Governance Core", content)
```

- [ ] **Step 3: Write the failing test for comma-separated applyTo**

```python
def test_sync_claude_rules_splits_comma_separated_apply_to(self) -> None:
    """Comma-separated applyTo patterns become a YAML list in paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "gate5.instructions.md").write_text(
            '---\napplyTo: "docs/**,src/gzkit/**"\n---\n\n# Gate 5\n'
        )

        sync_claude_rules(project_root)

        rules_file = project_root / ".claude" / "rules" / "gate5.md"
        content = rules_file.read_text(encoding="utf-8")
        self.assertIn('  - "docs/**"', content)
        self.assertIn('  - "src/gzkit/**"', content)
```

- [ ] **Step 4: Write the failing test for excludeAgent filter**

```python
def test_sync_claude_rules_skips_excluded_coding_agent_rules(self) -> None:
    """Instructions with excludeAgent: coding-agent are not mirrored."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "review_only.instructions.md").write_text(
            '---\napplyTo: "**/*"\nexcludeAgent: coding-agent\n---\n\n# Review Only\n'
        )

        sync_claude_rules(project_root)

        rules_file = project_root / ".claude" / "rules" / "review_only.md"
        self.assertFalse(rules_file.exists())
```

- [ ] **Step 5: Write the failing test for file filter (skip non-instruction files)**

```python
def test_sync_claude_rules_skips_readme_and_non_instruction_files(self) -> None:
    """Only *.instructions.md files are mirrored."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "README.md").write_text("# Instructions\n")
        (instructions_dir / "tests.instructions.md").write_text(
            '---\napplyTo: "tests/**"\n---\n\n# Tests\n'
        )

        sync_claude_rules(project_root)

        rules_dir = project_root / ".claude" / "rules"
        mirrored = [f.name for f in rules_dir.iterdir()] if rules_dir.exists() else []
        self.assertIn("tests.md", mirrored)
        self.assertNotIn("README.md", mirrored)
```

- [ ] **Step 6: Write the failing test for stale file cleanup**

```python
def test_sync_claude_rules_deletes_stale_mirrored_rules(self) -> None:
    """Rules that no longer have a source instruction file are deleted."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "tests.instructions.md").write_text(
            '---\napplyTo: "tests/**"\n---\n\n# Tests\n'
        )

        # Create a stale rule that has no source
        rules_dir = project_root / ".claude" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        (rules_dir / "old_rule.md").write_text("# Stale\n")

        sync_claude_rules(project_root)

        self.assertTrue((rules_dir / "tests.md").exists())
        self.assertFalse((rules_dir / "old_rule.md").exists())
```

- [ ] **Step 7: Run tests to verify they all fail**

Run: `uv run -m unittest tests.test_sync -v -k claude_rules`
Expected: FAIL — `sync_claude_rules` not defined

- [ ] **Step 8: Implement `sync_claude_rules()`**

Add to `src/gzkit/sync.py` after `sync_claude_md()`:

```python
def _parse_instruction_frontmatter(content: str) -> dict[str, str]:
    """Parse frontmatter from an instruction file.

    Args:
        content: Full file content.

    Returns:
        Dictionary of frontmatter key-value pairs.
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fm: dict[str, str] = {}
    for raw in lines[1:]:
        stripped = raw.strip()
        if stripped == "---":
            break
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        fm[key.strip()] = value.strip().strip("\"'")
    return fm


def _extract_body_after_frontmatter(content: str) -> str:
    """Return the body content after YAML frontmatter.

    Args:
        content: Full file content.

    Returns:
        Body text after the closing --- delimiter.
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content

    for idx, raw in enumerate(lines[1:], start=1):
        if raw.strip() == "---":
            return "\n".join(lines[idx + 1 :])
    return content


def _convert_apply_to_paths(apply_to: str) -> list[str]:
    """Convert Copilot applyTo string to Claude paths list.

    Args:
        apply_to: Comma-separated glob patterns.

    Returns:
        List of trimmed glob patterns.
    """
    patterns = [p.strip() for p in apply_to.split(",") if p.strip()]

    for pattern in patterns:
        if any(c in pattern for c in "{}!"):
            logger.warning(
                "Glob pattern %r contains brace expansion or negation "
                "which may not be supported by Claude Code paths matcher.",
                pattern,
            )

    return patterns


def sync_claude_rules(project_root: Path) -> list[str]:
    """Mirror .github/instructions/*.instructions.md to .claude/rules/*.md.

    Converts Copilot applyTo frontmatter to Claude paths frontmatter.
    Deletes stale mirrored files. Creates directory if missing.

    Args:
        project_root: Project root directory.

    Returns:
        List of mirrored file paths (relative to project_root).
    """
    instructions_dir = project_root / ".github" / "instructions"
    rules_dir = project_root / ".claude" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)

    updated: list[str] = []
    expected_names: set[str] = set()

    if instructions_dir.exists():
        for src_file in sorted(instructions_dir.iterdir()):
            if not src_file.name.endswith(".instructions.md"):
                continue

            content = src_file.read_text(encoding="utf-8")
            fm = _parse_instruction_frontmatter(content)

            # Skip rules excluded from coding agents.
            exclude = fm.get("excludeAgent", "")
            if exclude in ("coding-agent", "all"):
                continue

            apply_to = fm.get("applyTo", "")
            if not apply_to:
                logger.warning("Skipping %s: no applyTo frontmatter.", src_file.name)
                continue

            body = _extract_body_after_frontmatter(content)
            target_name = src_file.name.replace(".instructions.md", ".md")
            expected_names.add(target_name)

            # Build Claude rules content.
            if apply_to.strip() == "**/*":
                # Unconditional — no frontmatter needed.
                output = body.lstrip("\n")
            else:
                paths = _convert_apply_to_paths(apply_to)
                paths_yaml = "\n".join(f'  - "{p}"' for p in paths)
                output = f"---\npaths:\n{paths_yaml}\n---\n{body}"

            target = rules_dir / target_name
            target.write_text(output, encoding="utf-8")
            updated.append(str(target.relative_to(project_root)))

    # Delete stale mirrored rules.
    if rules_dir.exists():
        for existing in rules_dir.iterdir():
            if existing.is_file() and existing.name not in expected_names:
                existing.unlink()

    return updated
```

- [ ] **Step 9: Add import for `sync_claude_rules` to test file**

Update `tests/test_sync.py` imports to include `sync_claude_rules`.

- [ ] **Step 10: Run tests to verify they pass**

Run: `uv run -m unittest tests.test_sync -v -k claude_rules`
Expected: all 6 tests PASS

- [ ] **Step 11: Commit**

```bash
git add src/gzkit/sync.py tests/test_sync.py
git commit -m "feat(sync): add sync_claude_rules() to mirror instructions to .claude/rules/"
```

### Task 5: Wire `sync_claude_rules()` into `sync_all()`

**Files:**
- Modify: `src/gzkit/sync.py:1197-1222` (`sync_all`)
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test**

```python
def test_sync_all_creates_claude_rules_from_instructions(self) -> None:
    """sync_all() mirrors .github/instructions/ to .claude/rules/."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        config = GzkitConfig(project_name="gzkit-test")

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "tests.instructions.md").write_text(
            '---\napplyTo: "tests/**"\n---\n\n# Test Policy\n'
        )

        sync_all(project_root, config)

        rules_file = project_root / ".claude" / "rules" / "tests.md"
        self.assertTrue(rules_file.exists())
        content = rules_file.read_text(encoding="utf-8")
        self.assertIn("paths:", content)
        self.assertIn("# Test Policy", content)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run -m unittest tests.test_sync.TestSync.test_sync_all_creates_claude_rules_from_instructions -v`
Expected: FAIL — `.claude/rules/tests.md` does not exist

- [ ] **Step 3: Add `sync_claude_rules()` call to `sync_all()`**

In `src/gzkit/sync.py`, in `sync_all()`, add after `sync_claude_md()` call (after line 1201):

```python
    updated.extend(sync_claude_rules(project_root))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run -m unittest tests.test_sync.TestSync.test_sync_all_creates_claude_rules_from_instructions -v`
Expected: PASS

- [ ] **Step 5: Run full test suite**

Run: `uv run -m unittest tests.test_sync -v`
Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add src/gzkit/sync.py tests/test_sync.py
git commit -m "feat(sync): wire sync_claude_rules() into sync_all() orchestration"
```

---

## Chunk 3: Slim CLAUDE.md Template

### Task 6: Replace CLAUDE.md template

**Files:**
- Modify: `src/gzkit/templates/claude.md`
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test — slim content assertions**

```python
def test_sync_claude_md_is_slim_without_duplicated_governance(self) -> None:
    """Slim CLAUDE.md does not contain Gate Covenant, Governance Workflow, or skill catalog."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        config = GzkitConfig(project_name="gzkit-test")

        skill_dir = project_root / config.paths.skills / "demo-skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: Demo.\ncategory: code-quality\n"
            "lifecycle_state: active\nowner: test\nlast_reviewed: 2026-03-15\n---\n"
        )

        sync_all(project_root, config)

        claude = (project_root / config.paths.claude_md).read_text(encoding="utf-8")
        # Should NOT contain duplicated governance
        self.assertNotIn("Gate Covenant", claude)
        self.assertNotIn("Governance Workflow", claude)
        self.assertNotIn("OBPI Acceptance", claude)
        self.assertNotIn("demo-skill", claude)  # No skill catalog
        # Should contain slim pointers
        self.assertIn("AGENTS.md", claude)
        self.assertIn(".claude/rules/", claude)
        self.assertIn(".claude/skills/", claude)
        self.assertIn("Build Commands", claude)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run -m unittest tests.test_sync.TestSync.test_sync_claude_md_is_slim_without_duplicated_governance -v`
Expected: FAIL — current CLAUDE.md still has Gate Covenant etc.

- [ ] **Step 3: Replace `src/gzkit/templates/claude.md`**

Replace the entire template with the slim version from the spec:

```markdown
# CLAUDE.md

This file provides guidance to Claude Code when working with {project_name}.

## Project Overview

{project_purpose}

## Canonical Contract

`AGENTS.md` is the authoritative governance contract.

If this file and `AGENTS.md` diverge, follow `AGENTS.md` and run `gz agent sync control-surfaces`.

## Tech Stack

{tech_stack}

## Build Commands

```bash
{build_commands}
```

## Coding Conventions

{coding_conventions}

## Governance Rules

Loaded contextually from `.claude/rules/` (mirrored from `.github/instructions/`).

Run `gz agent sync control-surfaces` to regenerate.

## Skills

Discovered automatically from `.claude/skills/`. See `AGENTS.md` for the full catalog.

## Control Surfaces

This file is generated by `gz agent sync control-surfaces` from governance canon.

Project-specific additions come from `agents.local.md`.

---

<!-- BEGIN agents.local.md -->
{local_content}
<!-- END agents.local.md -->
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run -m unittest tests.test_sync.TestSync.test_sync_claude_md_is_slim_without_duplicated_governance -v`
Expected: PASS

- [ ] **Step 5: Fix existing tests that assert old CLAUDE.md content**

Three existing tests will break after the template change. Fix each:

**Fix `test_sync_includes_skills_in_generated_surfaces` (~line 445):**
- Remove: `self.assertIn("`demo-skill`", claude)` — CLAUDE.md no longer has skills
- Keep: `self.assertIn("`demo-skill`", agents)` — still in AGENTS.md (now under "Uncategorized" since test skill has no category)
- Keep: `self.assertIn("`demo-skill`", copilot)` — copilot template still has skills
- Remove: `self.assertIn(".gzkit/skills/demo-skill/SKILL.md", agents)` — categorized format no longer includes paths

**Fix `test_sync_skills_catalog_uses_frontmatter_description` (~line 468):**
- Change: `self.assertIn("`demo-skill`: Demo skill", agents)` to `self.assertIn("`demo-skill`", agents)` — categorized format shows names only, no descriptions

**Note on `{skills_catalog}` in `get_project_context()`**: The slim CLAUDE.md template no longer references `{skills_catalog}`, but `get_project_context()` still produces it. This is safe — the template engine (`SafeDict`) silently ignores unused keys. The variable remains because AGENTS.md and copilot templates still use it.

- [ ] **Step 6: Run full test suite**

Run: `uv run -m unittest tests.test_sync -v`
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/gzkit/templates/claude.md tests/test_sync.py
git commit -m "feat(templates): slim CLAUDE.md to ~40 lines, remove duplicated governance"
```

---

## Chunk 4: JSON Schemas and Validation

### Task 7: Create skill and rule JSON Schemas

**Files:**
- Create: `.gzkit/schemas/skill.schema.json`
- Create: `.gzkit/schemas/rule.schema.json`

- [ ] **Step 1: Create `.gzkit/schemas/` directory**

```bash
mkdir -p .gzkit/schemas
```

- [ ] **Step 2: Write `skill.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "gzkit Skill Frontmatter",
  "description": "Schema for .gzkit/skills/*/SKILL.md frontmatter fields.",
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9-]+$",
      "maxLength": 64,
      "description": "Skill identifier. Lowercase, hyphens only."
    },
    "description": {
      "type": "string",
      "maxLength": 1024,
      "description": "What the skill does and when to use it."
    },
    "category": {
      "type": "string",
      "enum": [
        "adr-lifecycle",
        "adr-operations",
        "adr-audit",
        "obpi-pipeline",
        "governance-infrastructure",
        "agent-operations",
        "code-quality",
        "cross-repository"
      ],
      "description": "Skill category for catalog grouping."
    },
    "lifecycle_state": {
      "type": "string",
      "enum": ["active", "deprecated", "draft", "retired"],
      "description": "Current lifecycle state."
    },
    "owner": { "type": "string" },
    "last_reviewed": {
      "type": "string",
      "pattern": "^\\d{4}-\\d{2}-\\d{2}$",
      "description": "ISO date of last review."
    },
    "user-invocable": { "type": "boolean" },
    "disable-model-invocation": { "type": "boolean" },
    "argument-hint": { "type": "string" },
    "allowed-tools": { "type": "string" },
    "model": { "type": "string" },
    "context": { "type": "string", "enum": ["fork"] },
    "agent": { "type": "string" }
  },
  "required": ["description"]
}
```

- [ ] **Step 3: Write `rule.schema.json`**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "gzkit Rule/Instruction Frontmatter",
  "description": "Schema for .github/instructions/*.instructions.md frontmatter fields.",
  "type": "object",
  "properties": {
    "name": { "type": "string", "description": "Display name for the rule." },
    "description": { "type": "string", "description": "What the rule enforces." },
    "category": { "type": "string", "description": "Grouping for catalog use." },
    "applyTo": {
      "type": "string",
      "description": "Copilot glob patterns (comma-separated)."
    },
    "excludeAgent": {
      "type": "string",
      "enum": ["code-review", "coding-agent", "all"],
      "description": "Copilot agent exclusion."
    }
  },
  "required": ["applyTo"]
}
```

- [ ] **Step 4: Commit**

```bash
git add .gzkit/schemas/
git commit -m "feat(schemas): add JSON Schema for skill and rule frontmatter"
```

### Task 8: Wire schema validation into `gz validate --surfaces`

**Files:**
- Modify: `src/gzkit/validate.py:1050+` (`validate_surfaces`)
- Modify: `src/gzkit/sync.py` (reuse `_parse_instruction_frontmatter` or `_extract_skill_frontmatter_field`)
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test for invalid category**

```python
def test_validate_surfaces_catches_invalid_skill_category(self) -> None:
    """validate_surfaces reports an error for skills with invalid category values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)

        # Create AGENTS.md so existing validation does not short-circuit.
        (project_root / "AGENTS.md").write_text("# AGENTS.md\n## Skills\n## Gate Covenant\n")

        skill_dir = project_root / ".gzkit" / "skills" / "bad-skill"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: bad-skill\ndescription: Bad.\ncategory: invalid-category\n"
            "lifecycle_state: active\nowner: test\nlast_reviewed: 2026-03-15\n---\n"
        )

        errors = validate_surfaces(project_root)
        category_errors = [e for e in errors if "category" in e.message.lower()]
        self.assertGreater(len(category_errors), 0)
```

- [ ] **Step 2: Write the failing test for missing applyTo in instruction**

```python
def test_validate_surfaces_catches_instruction_without_apply_to(self) -> None:
    """validate_surfaces reports an error for instruction files missing applyTo."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        (project_root / "AGENTS.md").write_text("# AGENTS.md\n## Skills\n## Gate Covenant\n")

        instructions_dir = project_root / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
        (instructions_dir / "bad.instructions.md").write_text(
            "---\nname: bad\n---\n\n# Missing applyTo\n"
        )

        errors = validate_surfaces(project_root)
        apply_errors = [e for e in errors if "applyTo" in e.message]
        self.assertGreater(len(apply_errors), 0)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `uv run -m unittest tests.test_sync -v -k validate_surfaces`
Expected: FAIL — `validate_surfaces` does not check skill/rule frontmatter.

- [ ] **Step 4: Implement frontmatter validation in `validate_surfaces()`**

Add to `src/gzkit/validate.py`, appending to the `validate_surfaces()` function body (after the existing AGENTS.md checks):

```python
    # Validate skill frontmatter against schema constraints.
    VALID_CATEGORIES = {
        "adr-lifecycle", "adr-operations", "adr-audit", "obpi-pipeline",
        "governance-infrastructure", "agent-operations", "code-quality",
        "cross-repository",
    }
    VALID_LIFECYCLE_STATES = {"active", "deprecated", "draft", "retired"}

    skills_dir = project_root / ".gzkit" / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(skills_dir.iterdir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_dir.is_dir() or not skill_file.exists():
                continue

            try:
                content = skill_file.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(content)
            except Exception as e:
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(skill_file),
                        message=f"Failed to parse frontmatter: {e}",
                    )
                )
                continue

            # Check category is from allowed enum (if present).
            category = fm.get("category", "")
            if category and category not in VALID_CATEGORIES:
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(skill_file),
                        message=f"Invalid category '{category}'. "
                        f"Allowed: {', '.join(sorted(VALID_CATEGORIES))}",
                        field="category",
                    )
                )

            # Check lifecycle_state is from allowed enum (if present).
            state = fm.get("lifecycle_state", "")
            if state and state not in VALID_LIFECYCLE_STATES:
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(skill_file),
                        message=f"Invalid lifecycle_state '{state}'. "
                        f"Allowed: {', '.join(sorted(VALID_LIFECYCLE_STATES))}",
                        field="lifecycle_state",
                    )
                )

    # Validate instruction file frontmatter.
    instructions_dir = project_root / ".github" / "instructions"
    if instructions_dir.exists():
        for inst_file in sorted(instructions_dir.iterdir()):
            if not inst_file.name.endswith(".instructions.md"):
                continue

            try:
                content = inst_file.read_text(encoding="utf-8")
                fm, _ = parse_frontmatter(content)
            except Exception as e:
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(inst_file),
                        message=f"Failed to parse frontmatter: {e}",
                    )
                )
                continue

            if not fm.get("applyTo"):
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(inst_file),
                        message="Missing required field: applyTo",
                        field="applyTo",
                    )
                )
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `uv run -m unittest tests.test_sync -v -k validate_surfaces`
Expected: PASS

- [ ] **Step 6: Run full test suite**

Run: `uv run gz test`
Expected: all tests PASS

- [ ] **Step 7: Commit**

```bash
git add src/gzkit/validate.py tests/test_sync.py
git commit -m "feat(validate): validate skill category and rule applyTo against schema constraints"
```

Note: `src/gzkit/cli.py` already wires `validate_surfaces()` to `gz validate --surfaces` (line 5030 and line 4063). No CLI changes needed — the extended `validate_surfaces()` function is called automatically.

---

## Chunk 5: Manifest Update and Final Sync

### Task 9: Update manifest generation to include rules paths

**Files:**
- Modify: `src/gzkit/sync.py` (in `generate_manifest()`)
- Test: `tests/test_sync.py`

- [ ] **Step 1: Write the failing test**

```python
def test_sync_manifest_includes_claude_rules_and_instructions_paths(self) -> None:
    """Generated manifest includes claude_rules and instructions control surfaces."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        config = GzkitConfig(project_name="gzkit-test")

        sync_all(project_root, config)

        manifest_path = project_root / ".gzkit" / "manifest.json"
        manifest = manifest_path.read_text(encoding="utf-8")
        self.assertIn('"claude_rules"', manifest)
        self.assertIn('".claude/rules"', manifest)
        self.assertIn('"instructions"', manifest)
        self.assertIn('".github/instructions"', manifest)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run -m unittest tests.test_sync.TestSync.test_sync_manifest_includes_claude_rules_and_instructions_paths -v`
Expected: FAIL — manifest does not contain these entries.

- [ ] **Step 3: Find `generate_manifest()` and add entries**

Add to the `control_surfaces` dict in `generate_manifest()`:

```python
"instructions": ".github/instructions",
"claude_rules": ".claude/rules",
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run -m unittest tests.test_sync.TestSync.test_sync_manifest_includes_claude_rules_and_instructions_paths -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/gzkit/sync.py tests/test_sync.py
git commit -m "feat(manifest): add claude_rules and instructions to control_surfaces"
```

### Task 10: Full integration test — regenerate and verify

**Files:**
- No new files — this is a verification step

- [ ] **Step 1: Run full sync**

```bash
uv run gz agent sync control-surfaces
```

- [ ] **Step 2: Verify CLAUDE.md is slim (~40 lines)**

```bash
wc -l CLAUDE.md
```

Expected: ~40-50 lines (no Gate Covenant, no skill catalog, no OBPI protocol).

- [ ] **Step 3: Verify AGENTS.md has categorized skill catalog**

Check that AGENTS.md contains `#### ADR Lifecycle`, `#### Code Quality`, etc. instead of the flat list.

- [ ] **Step 4: Verify `.claude/rules/` was created with mirrored files**

```bash
ls -la .claude/rules/
```

Expected: 14 `.md` files (one per instruction file, minus any excluded). `governance_core.md` should have no `paths:` frontmatter. `tests.md` should have `paths: ["tests/**"]`.

- [ ] **Step 5: Verify `.claude/rules/governance_core.md` is unconditional**

```bash
head -5 .claude/rules/governance_core.md
```

Expected: No `---` / `paths:` frontmatter — body content starts immediately.

- [ ] **Step 6: Run full quality gates**

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --surfaces
```

Expected: all pass.

- [ ] **Step 7: Final commit**

```bash
git add AGENTS.md CLAUDE.md .claude/rules/ .gzkit/manifest.json
git commit -m "chore: regenerate control surfaces after tidy implementation"
```
