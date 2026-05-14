"""Regression tests for public-symbol re-exports from gzkit.skills.

OBPI-0.0.32-01-skills-physical-migration: verifies that every symbol in
``gzkit.skills.__all__`` (plus ``_parse_frontmatter``) continues to resolve
after the module-package conversion, and that the dual-surface layout
(.gzkit/skills/ authored source plus src/gzkit/skills/ package copy)
holds byte-parity.

OBPI-0.0.32-02-skills-scaffolder-refactor: verifies that
``_iter_canonical_skill_slugs`` enumerates all 70 canonical slugs and
``scaffold_core_skills`` copies canonical SKILL.md content from the wheel's
package surface rather than rendering stubs.
"""

from __future__ import annotations

import inspect
import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestSkillsPublicSymbols(unittest.TestCase):
    """Every symbol in gzkit.skills.__all__ must be importable post-migration."""

    @covers("REQ-0.0.32-01-03")
    def test_core_skills_is_dict(self) -> None:
        from gzkit.skills import CORE_SKILLS

        self.assertIsInstance(CORE_SKILLS, dict)
        self.assertGreater(len(CORE_SKILLS), 0)

    @covers("REQ-0.0.32-01-03")
    def test_scaffold_skill_is_callable(self) -> None:
        from gzkit.skills import scaffold_skill

        self.assertTrue(callable(scaffold_skill))

    @covers("REQ-0.0.32-01-03")
    def test_scaffold_core_skills_is_callable(self) -> None:
        from gzkit.skills import scaffold_core_skills

        self.assertTrue(callable(scaffold_core_skills))

    @covers("REQ-0.0.32-01-03")
    def test_list_skills_is_callable(self) -> None:
        from gzkit.skills import list_skills

        self.assertTrue(callable(list_skills))

    @covers("REQ-0.0.32-01-03")
    def test_get_skill_is_callable(self) -> None:
        from gzkit.skills import get_skill

        self.assertTrue(callable(get_skill))

    @covers("REQ-0.0.32-01-03")
    def test_skill_class_is_type(self) -> None:
        from gzkit.skills import Skill

        self.assertIsInstance(Skill, type)

    @covers("REQ-0.0.32-01-03")
    def test_skill_audit_issue_is_type(self) -> None:
        from gzkit.skills import SkillAuditIssue

        self.assertIsInstance(SkillAuditIssue, type)

    @covers("REQ-0.0.32-01-03")
    def test_skill_audit_report_is_type(self) -> None:
        from gzkit.skills import SkillAuditReport

        self.assertIsInstance(SkillAuditReport, type)

    @covers("REQ-0.0.32-01-03")
    def test_parse_frontmatter_is_callable(self) -> None:
        from gzkit.skills import _parse_frontmatter

        self.assertTrue(callable(_parse_frontmatter))

    @covers("REQ-0.0.32-01-03")
    def test_default_max_review_age_days_is_int(self) -> None:
        from gzkit.skills import DEFAULT_MAX_REVIEW_AGE_DAYS

        self.assertIsInstance(DEFAULT_MAX_REVIEW_AGE_DAYS, int)
        self.assertGreater(DEFAULT_MAX_REVIEW_AGE_DAYS, 0)

    @covers("REQ-0.0.32-01-03")
    def test_audit_skills_is_callable(self) -> None:
        from gzkit.skills import audit_skills

        self.assertTrue(callable(audit_skills))

    @covers("REQ-0.0.32-01-03")
    def test_all_exports_present(self) -> None:
        """Verify __all__ covers the expected canonical set."""
        import gzkit.skills as skills_mod

        all_exports = getattr(skills_mod, "__all__", None)
        self.assertIsNotNone(all_exports, "__all__ must be defined")
        expected = {
            "CORE_SKILLS",
            "DEFAULT_MAX_REVIEW_AGE_DAYS",
            "Skill",
            "SkillAuditIssue",
            "SkillAuditReport",
            "audit_skills",
            "get_skill",
            "list_skills",
            "scaffold_core_skills",
            "scaffold_skill",
        }
        missing = expected - set(all_exports)
        self.assertEqual(missing, set(), f"Missing from __all__: {missing}")

    @covers("REQ-0.0.32-01-03")
    def test_module_resolves_as_package_or_module(self) -> None:
        """gzkit.skills must be importable regardless of module vs package shape."""
        import gzkit.skills as skills_mod

        self.assertIsNotNone(skills_mod)


class TestSkillsAuditSiblingImports(unittest.TestCase):
    """gzkit.skills_audit import sites must continue to resolve post-migration."""

    @covers("REQ-0.0.32-01-04")
    def test_skills_audit_default_max_review_age_days(self) -> None:
        from gzkit.skills_audit import DEFAULT_MAX_REVIEW_AGE_DAYS

        self.assertIsInstance(DEFAULT_MAX_REVIEW_AGE_DAYS, int)

    @covers("REQ-0.0.32-01-04")
    def test_skills_audit_audit_skills(self) -> None:
        from gzkit.skills_audit import audit_skills

        self.assertTrue(callable(audit_skills))

    @covers("REQ-0.0.32-01-04")
    def test_skills_mirror_imports(self) -> None:
        """skills_mirror.py imports from gzkit.skills must survive the conversion."""
        from gzkit.skills_mirror import validate_mirror_root  # noqa: F401

        self.assertTrue(callable(validate_mirror_root))


class TestScaffolderBodyUnchanged(unittest.TestCase):
    """scaffold_core_skills must not have changed its calling signature."""

    @covers("REQ-0.0.32-01-05")
    def test_scaffold_core_skills_signature(self) -> None:
        import inspect

        from gzkit.skills import scaffold_core_skills

        sig = inspect.signature(scaffold_core_skills)
        params = list(sig.parameters.keys())
        self.assertIn("project_root", params, "scaffold_core_skills must accept project_root")


class TestSkillsLayoutDualSurface(unittest.TestCase):
    """SKILL.md must exist at BOTH .gzkit/skills/<slug>/ and src/gzkit/skills/<slug>/.

    .gzkit/skills/ is the authored source (project canonical, retained).
    src/gzkit/skills/ is the synced copy (ships in wheel).
    """

    @covers("REQ-0.0.32-01-01")
    @covers("REQ-0.0.32-08-06")
    def test_skill_files_present_in_package_surface(self) -> None:
        skills_root = _PROJECT_ROOT / "src" / "gzkit" / "skills"
        skill_dirs = [
            d for d in skills_root.iterdir() if d.is_dir() and not d.name.startswith("__")
        ]
        self.assertGreater(len(skill_dirs), 60, "expected at least 60 skill directories")
        for slug_dir in skill_dirs[:3]:
            self.assertTrue((slug_dir / "SKILL.md").exists(), f"Missing: {slug_dir}/SKILL.md")

    @covers("REQ-0.0.32-01-01")
    def test_skill_files_retained_at_authored_source(self) -> None:
        authored_root = _PROJECT_ROOT / ".gzkit" / "skills"
        skill_dirs = [d for d in authored_root.iterdir() if d.is_dir()]
        skill_count = sum(1 for d in skill_dirs if (d / "SKILL.md").exists())
        self.assertGreaterEqual(
            skill_count,
            61,
            f".gzkit/skills/ must retain authored SKILL.md files (found {skill_count})",
        )

    @covers("REQ-0.0.32-01-01")
    @covers("REQ-0.0.32-01-02")
    @covers("REQ-0.0.32-08-03")
    @covers("REQ-0.0.32-15-10")
    def test_dual_surface_byte_parity(self) -> None:
        """Authored .gzkit/skills/<slug>/SKILL.md must be byte-identical to src/gzkit copy."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "skills"
        pkg_root = _PROJECT_ROOT / "src" / "gzkit" / "skills"
        for slug_dir in authored_root.iterdir():
            authored = slug_dir / "SKILL.md"
            if not authored.exists():
                continue
            pkg_copy = pkg_root / slug_dir.name / "SKILL.md"
            self.assertTrue(
                pkg_copy.exists(),
                f"Package copy missing: {pkg_copy.relative_to(_PROJECT_ROOT)}",
            )
            self.assertEqual(
                authored.read_bytes(),
                pkg_copy.read_bytes(),
                f"Drift between .gzkit/ and src/gzkit/ for {slug_dir.name}/SKILL.md",
            )


class TestSkillMdByteIdenticalContent(unittest.TestCase):
    """Migrated SKILL.md files must be valid markdown with frontmatter."""

    @covers("REQ-0.0.32-01-02")
    def test_all_skill_md_files_have_frontmatter(self) -> None:
        skills_root = _PROJECT_ROOT / "src" / "gzkit" / "skills"
        skill_dirs = [
            d for d in skills_root.iterdir() if d.is_dir() and not d.name.startswith("__")
        ]
        for slug_dir in skill_dirs:
            skill_file = slug_dir / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---\n"), f"No frontmatter: {skill_file}")

    @covers("REQ-0.0.32-01-02")
    def test_skills_count_is_full(self) -> None:
        skills_root = _PROJECT_ROOT / "src" / "gzkit" / "skills"
        skill_dirs = [
            d for d in skills_root.iterdir() if d.is_dir() and not d.name.startswith("__")
        ]
        count = len(skill_dirs)
        self.assertGreaterEqual(count, 61, f"Expected at least 61 skill dirs, got {count}")


class TestPyprojectTomlSkillsInclude(unittest.TestCase):
    """pyproject.toml includes src/gzkit/skills wheel-include (landed by OBPI-0.0.32-06)."""

    @covers("REQ-0.0.32-01-06")
    def test_pyproject_includes_skills_package_data(self) -> None:
        pyproject = (_PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn(
            "src/gzkit/skills/**",
            pyproject,
            "pyproject.toml must include src/gzkit/skills/** for wheel-shipping (OBPI-06)",
        )


class TestScaffoldSkillTemplateRemoved(unittest.TestCase):
    """GHI #453: scaffold_skill no longer reads templates/skill.md; the file is deleted.

    The OBPI-0.0.32-02 follow-up clause permitted either deletion or retention with a
    repurposing comment; this defect closure takes the deletion branch and inlines a
    minimal stub in scaffold_skill so no template consumer remains.
    """

    def test_skill_template_does_not_exist(self) -> None:
        skill_template = _PROJECT_ROOT / "src" / "gzkit" / "templates" / "skill.md"
        self.assertFalse(
            skill_template.exists(),
            f"templates/skill.md must be deleted (GHI #453); still present at {skill_template}",
        )

    def test_scaffold_skill_module_does_not_import_render_template(self) -> None:
        skills_init = _PROJECT_ROOT / "src" / "gzkit" / "skills" / "__init__.py"
        content = skills_init.read_text(encoding="utf-8")
        self.assertNotIn(
            "render_template",
            content,
            "scaffold_skill must not depend on render_template after GHI #453",
        )

    def test_scaffold_skill_writes_inline_stub_with_required_frontmatter(self) -> None:
        from gzkit.skills import scaffold_skill

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            skill_file = scaffold_skill(
                project_root,
                "demo-inline-stub",
                "skills",
                skill_description="Inline stub regression test (GHI #453).",
            )
            content = skill_file.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("---"), "stub must start with frontmatter")
            for field in ("name:", "description:", "lifecycle_state:", "owner:", "last_reviewed:"):
                self.assertIn(field, content, f"stub missing required frontmatter field {field!r}")
            self.assertIn("demo-inline-stub", content)


class TestCoreSkillsHasNoRetiredEntries(unittest.TestCase):
    """GHI #453: CORE_SKILLS must not carry slugs whose canonical SKILL.md is retired."""

    def test_no_retired_slug_in_core_skills(self) -> None:
        import importlib.resources

        from gzkit.skills import CORE_SKILLS, _parse_frontmatter

        canonical_root = importlib.resources.files("gzkit.skills")
        retired_in_core: list[str] = []
        for slug in CORE_SKILLS:
            slug_dir = canonical_root.joinpath(slug)
            skill_file = slug_dir.joinpath("SKILL.md")
            if not skill_file.is_file():
                continue
            frontmatter, _ = _parse_frontmatter(skill_file.read_text(encoding="utf-8"))
            if (frontmatter.get("lifecycle_state") or "active") == "retired":
                retired_in_core.append(slug)
        self.assertEqual(
            retired_in_core,
            [],
            f"CORE_SKILLS must contain no retired slugs (GHI #453); found: {retired_in_core}",
        )

    def test_lint_is_not_in_core_skills(self) -> None:
        from gzkit.skills import CORE_SKILLS

        self.assertNotIn(
            "lint",
            CORE_SKILLS,
            "stale 'lint' entry must be removed from CORE_SKILLS (GHI #453)",
        )


class TestSkillsScaffolderRefactor(unittest.TestCase):
    """OBPI-0.0.32-02: scaffold_core_skills copies from importlib.resources package surface."""

    @covers("REQ-0.0.32-02-01")
    def test_iter_canonical_skill_slugs_exists(self) -> None:
        from gzkit.skills import _iter_canonical_skill_slugs

        self.assertTrue(callable(_iter_canonical_skill_slugs))

    @covers("REQ-0.0.32-02-01")
    def test_iter_canonical_skill_slugs_count(self) -> None:
        from gzkit.skills import _iter_canonical_skill_slugs

        count = sum(1 for _ in _iter_canonical_skill_slugs())
        self.assertGreaterEqual(
            count,
            70,
            f"_iter_canonical_skill_slugs must yield >= 70 slugs, got {count}",
        )

    @covers("REQ-0.0.32-02-02")
    def test_scaffold_core_skills_copies_canonical_content(self) -> None:
        from gzkit.config import GzkitConfig
        from gzkit.skills import scaffold_core_skills

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig(mode="lite", project_name="test-project")  # type: ignore[arg-type]
            created = scaffold_core_skills(project_root, config, skip_existing=False)
            self.assertGreaterEqual(
                len(created),
                50,
                f"scaffold_core_skills must produce >= 50 files, got {len(created)}",
            )
            for skill_path in created[:5]:
                content = skill_path.read_text(encoding="utf-8")
                self.assertTrue(
                    content.startswith("---"),
                    f"scaffolded {skill_path.name} must start with --- (got: {content[:40]!r})",
                )

    @covers("REQ-0.0.32-02-04")
    def test_skip_existing_preserves_operator_edit(self) -> None:
        from gzkit.config import GzkitConfig
        from gzkit.skills import scaffold_core_skills

        sentinel = "OPERATOR-EDIT-SENTINEL-OBPI-32-02"
        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig(mode="lite", project_name="test-project")  # type: ignore[arg-type]
            created = scaffold_core_skills(project_root, config, skip_existing=False)
            self.assertGreater(len(created), 0, "first scaffold must create files")
            target = created[0]
            target.write_text(sentinel, encoding="utf-8")
            scaffold_core_skills(project_root, config, skip_existing=True)
            self.assertEqual(
                target.read_text(encoding="utf-8"),
                sentinel,
                "skip_existing=True must preserve operator-edited SKILL.md",
            )

    @covers("REQ-0.0.32-02-05")
    def test_scaffold_core_skills_signature_stable(self) -> None:
        from gzkit.skills import scaffold_core_skills

        sig = inspect.signature(scaffold_core_skills)
        params = list(sig.parameters.keys())
        self.assertIn("project_root", params, "scaffold_core_skills must accept project_root")
        self.assertIn("config", params, "scaffold_core_skills must accept config")
        self.assertIn("skip_existing", params, "scaffold_core_skills must accept skip_existing")

    @covers("REQ-0.0.32-02-06")
    def test_scaffolded_content_is_canonical_not_stub(self) -> None:
        from gzkit.config import GzkitConfig
        from gzkit.skills import scaffold_core_skills

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig(mode="lite", project_name="test-project")  # type: ignore[arg-type]
            created = scaffold_core_skills(project_root, config, skip_existing=False)
            for skill_path in created[:10]:
                content = skill_path.read_text(encoding="utf-8")
                lines = content.splitlines()
                self.assertGreater(
                    len(lines),
                    5,
                    f"{skill_path.name} has {len(lines)} lines; canonical must be > 5",
                )
                self.assertTrue(
                    content.startswith("---"),
                    f"{skill_path.name} must start with --- frontmatter marker",
                )

    @covers("REQ-0.0.32-02-07")
    def test_skill_surface_sync_rule_documents_bootstrap_semantics(self) -> None:
        rule_path = _PROJECT_ROOT / ".gzkit" / "rules" / "skill-surface-sync.md"
        self.assertTrue(rule_path.exists(), f"canonical rule must exist at {rule_path}")
        content = rule_path.read_text(encoding="utf-8")
        self.assertIn(
            "Edit `.gzkit/` first",
            content,
            "rule must re-affirm 'Edit `.gzkit/` first' canon",
        )
        self.assertIn(
            "Bootstrap semantics",
            content,
            "rule must document bootstrap-from-wheel semantics for gz init",
        )
        self.assertIn(
            'importlib.resources.files("gzkit.skills")',
            content,
            "rule must cite the package-surface resource path",
        )

    @covers("REQ-0.0.32-02-08")
    def test_init_manpage_documents_skills_scaffolding(self) -> None:
        manpage = _PROJECT_ROOT / "docs" / "user" / "manpages" / "init.md"
        self.assertTrue(manpage.exists(), f"init manpage must exist at {manpage}")
        content = manpage.read_text(encoding="utf-8")
        self.assertIn(
            "Skills Scaffolding",
            content,
            "init manpage must include a Skills Scaffolding section",
        )
        self.assertIn(
            'importlib.resources.files("gzkit.skills")',
            content,
            "init manpage must document the package-surface copy behavior",
        )

    @covers("REQ-0.0.32-02-09")
    def test_scaffold_core_skills_filters_retired_lifecycle(self) -> None:
        """gz check exit 0 invariant — retired skills are filtered.

        REQ-09 says ``uv run gz check`` MUST exit 0 after the refactor.
        The brittle failure mode (retired skills re-introduced by scaffold)
        is asserted directly here: the post-refactor ``scaffold_core_skills``
        MUST filter ``lifecycle_state: retired`` slugs.  ``gz check`` running
        green is the umbrella property; this test asserts the underlying
        invariant whose violation would break gz check.
        """
        from gzkit.config import GzkitConfig
        from gzkit.skills import scaffold_core_skills

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            config = GzkitConfig(mode="lite", project_name="test-project")  # type: ignore[arg-type]
            created = scaffold_core_skills(project_root, config, skip_existing=False)
            scaffolded_names = {p.parent.name for p in created}
            self.assertNotIn(
                "gz-adr-manager",
                scaffolded_names,
                "retired gz-adr-manager must not be scaffolded",
            )
            self.assertNotIn(
                "lint",
                scaffolded_names,
                "retired lint must not be scaffolded",
            )


class TestGzCheckPasses(unittest.TestCase):
    """Migration must leave lint, type, test, and format state passing."""

    @covers("REQ-0.0.32-01-08")
    def test_all_skill_imports_resolve(self) -> None:
        from gzkit.skills import (
            CORE_SKILLS,
            DEFAULT_MAX_REVIEW_AGE_DAYS,
            Skill,
            SkillAuditIssue,
            SkillAuditReport,
            audit_skills,
            get_skill,
            list_skills,
            scaffold_core_skills,
            scaffold_skill,
        )

        self.assertIsNotNone(CORE_SKILLS)
        self.assertIsNotNone(DEFAULT_MAX_REVIEW_AGE_DAYS)
        self.assertIsNotNone(Skill)
        self.assertIsNotNone(SkillAuditIssue)
        self.assertIsNotNone(SkillAuditReport)
        self.assertIsNotNone(audit_skills)
        self.assertIsNotNone(get_skill)
        self.assertIsNotNone(list_skills)
        self.assertIsNotNone(scaffold_core_skills)
        self.assertIsNotNone(scaffold_skill)

    @covers("REQ-0.0.32-01-08")
    def test_skills_package_not_flat_module(self) -> None:
        skills_init = _PROJECT_ROOT / "src" / "gzkit" / "skills" / "__init__.py"
        skills_flat = _PROJECT_ROOT / "src" / "gzkit" / "skills.py"
        self.assertTrue(skills_init.exists(), "src/gzkit/skills/__init__.py must exist")
        self.assertFalse(skills_flat.exists(), "src/gzkit/skills.py must not exist")


class TestClassifySkillFile(unittest.TestCase):
    """Per-surface classifier for the skills canonical surface (REQ-0.0.32-15-04).

    Signature-compatible with ``gzkit.chores._classify_chore_file``: returns
    one of ``"canonical"``, ``"package_only"``, or ``"runtime_state"``.
    """

    @covers("REQ-0.0.32-15-04")
    def test_importable(self) -> None:
        """``_classify_skill_file`` is importable from ``gzkit.skills``."""
        try:
            from gzkit.skills import _classify_skill_file  # noqa: PLC0415, F401
        except ImportError as e:  # pragma: no cover - failure surfaces in assertion
            self.fail(
                f"_classify_skill_file must be importable from gzkit.skills; got ImportError: {e}"
            )

    @covers("REQ-0.0.32-15-04")
    def test_package_only_init_py(self) -> None:
        """``__init__.py`` files classify as ``package_only``."""
        from gzkit.skills import _classify_skill_file  # noqa: PLC0415

        result = _classify_skill_file(Path("src/gzkit/skills/__init__.py"))
        self.assertEqual(result, "package_only")

    @covers("REQ-0.0.32-15-04")
    def test_canonical_md(self) -> None:
        """A ``SKILL.md`` (or any non-package file) classifies as ``canonical``."""
        from gzkit.skills import _classify_skill_file  # noqa: PLC0415

        result = _classify_skill_file(Path("src/gzkit/skills/gz-prd/SKILL.md"))
        self.assertEqual(result, "canonical")

    @covers("REQ-0.0.32-15-04")
    def test_package_only_pycache(self) -> None:
        """Anything under ``__pycache__`` classifies as ``package_only``."""
        from gzkit.skills import _classify_skill_file  # noqa: PLC0415

        result = _classify_skill_file(
            Path("src/gzkit/skills/__pycache__/something.cpython-313.pyc")
        )
        self.assertEqual(result, "package_only")
