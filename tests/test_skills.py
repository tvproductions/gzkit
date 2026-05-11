"""Regression tests for public-symbol re-exports from gzkit.skills.

OBPI-0.0.32-01-skills-physical-migration: verifies that every symbol in
``gzkit.skills.__all__`` (plus ``_parse_frontmatter``) continues to resolve
after the module-package conversion, and that the dual-surface layout
(.gzkit/skills/ authored source plus src/gzkit/skills/ package copy)
holds byte-parity.
"""

from __future__ import annotations

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


class TestPyprojectTomlUnchanged(unittest.TestCase):
    """pyproject.toml must not include src/gzkit/skills in wheel includes (OBPI-06's work)."""

    @covers("REQ-0.0.32-01-06")
    def test_pyproject_does_not_include_skills_package_data(self) -> None:
        pyproject = (_PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertNotIn(
            "src/gzkit/skills/**",
            pyproject,
            "pyproject.toml must not include src/gzkit/skills/** until OBPI-06",
        )


class TestSkillTemplatePreserved(unittest.TestCase):
    """src/gzkit/templates/skill.md must still exist (deletion is OBPI-02's work)."""

    @covers("REQ-0.0.32-01-07")
    def test_skill_template_still_exists(self) -> None:
        skill_template = _PROJECT_ROOT / "src" / "gzkit" / "templates" / "skill.md"
        self.assertTrue(
            skill_template.exists(),
            f"skill.md template must still exist at {skill_template}",
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
