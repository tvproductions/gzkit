"""Tests for gz upgrade resource resolution plumbing.

These tests verify that ``importlib.resources.files("gzkit.<surface>")``
resolves correctly for every surface the upgrade command will process, and
that the CORE_* registries in each surface package are non-empty.

These tests use real package data (not mocked) and are expected to PASS even
at the red phase (before upgrade.py exists), because they test resource
plumbing that already exists in gzkit.

REQ covered: REQ-0.0.32-14-01 (resource resolution variant).
"""

import importlib.resources
import unittest

from gzkit.traceability import covers


class TestResourceResolution(unittest.TestCase):
    """importlib.resources.files resolves each canonical surface package."""

    @covers("REQ-0.0.32-14-01")
    def test_skills_resource_traversable(self) -> None:
        """gzkit.skills resolves to a Traversable via importlib.resources.files."""
        traversable = importlib.resources.files("gzkit.skills")
        self.assertIsNotNone(traversable, "gzkit.skills must resolve to a Traversable")
        # Traversable has an is_dir() method
        self.assertTrue(
            hasattr(traversable, "is_dir"),
            "gzkit.skills Traversable must have is_dir()",
        )

    @covers("REQ-0.0.32-14-01")
    def test_rules_resource_traversable(self) -> None:
        """gzkit.rules resolves to a Traversable via importlib.resources.files."""
        traversable = importlib.resources.files("gzkit.rules")
        self.assertIsNotNone(traversable)
        self.assertTrue(hasattr(traversable, "is_dir"))

    @covers("REQ-0.0.32-14-01")
    def test_templates_resource_traversable(self) -> None:
        """gzkit.templates resolves to a Traversable via importlib.resources.files."""
        traversable = importlib.resources.files("gzkit.templates")
        self.assertIsNotNone(traversable)
        self.assertTrue(hasattr(traversable, "is_dir"))

    @covers("REQ-0.0.32-14-01")
    def test_personas_resource_traversable(self) -> None:
        """gzkit.personas resolves to a Traversable via importlib.resources.files."""
        traversable = importlib.resources.files("gzkit.personas")
        self.assertIsNotNone(traversable)
        self.assertTrue(hasattr(traversable, "is_dir"))

    @covers("REQ-0.0.32-14-01")
    def test_chores_resource_traversable(self) -> None:
        """gzkit.chores resolves to a Traversable via importlib.resources.files."""
        traversable = importlib.resources.files("gzkit.chores")
        self.assertIsNotNone(traversable)
        self.assertTrue(hasattr(traversable, "is_dir"))

    @covers("REQ-0.0.32-14-01")
    def test_skills_resource_is_directory(self) -> None:
        """gzkit.skills Traversable must be a directory (has file children)."""
        traversable = importlib.resources.files("gzkit.skills")
        self.assertTrue(
            traversable.is_dir(),
            "gzkit.skills resource must be a directory",
        )

    @covers("REQ-0.0.32-14-01")
    def test_rules_resource_is_directory(self) -> None:
        """gzkit.rules Traversable must be a directory."""
        traversable = importlib.resources.files("gzkit.rules")
        self.assertTrue(traversable.is_dir(), "gzkit.rules resource must be a directory")


class TestCoreRegistries(unittest.TestCase):
    """CORE_* registries in each surface package must be non-empty."""

    @covers("REQ-0.0.32-14-01")
    def test_core_skills_non_empty(self) -> None:
        """CORE_SKILLS registry must contain at least one entry."""
        from gzkit.skills import CORE_SKILLS

        self.assertIsInstance(CORE_SKILLS, (dict, list, set))
        self.assertGreater(
            len(CORE_SKILLS),
            0,
            "CORE_SKILLS must be non-empty",
        )

    @covers("REQ-0.0.32-14-01")
    def test_core_rules_non_empty(self) -> None:
        """CORE_RULES registry must contain at least one entry."""
        from gzkit.rules import CORE_RULES

        self.assertIsInstance(CORE_RULES, (dict, list, set, frozenset))
        self.assertGreater(
            len(CORE_RULES),
            0,
            "CORE_RULES must be non-empty",
        )

    @covers("REQ-0.0.32-14-01")
    def test_core_personas_non_empty(self) -> None:
        """CORE_PERSONAS registry must contain at least one entry."""
        from gzkit.personas import CORE_PERSONAS

        self.assertIsInstance(CORE_PERSONAS, (dict, list, set, frozenset))
        self.assertGreater(
            len(CORE_PERSONAS),
            0,
            "CORE_PERSONAS must be non-empty",
        )

    @covers("REQ-0.0.32-14-01")
    def test_core_templates_non_empty(self) -> None:
        """CORE_TEMPLATES registry must contain at least one entry."""
        from gzkit.templates import CORE_TEMPLATES

        self.assertIsInstance(CORE_TEMPLATES, (dict, list, set, frozenset))
        self.assertGreater(
            len(CORE_TEMPLATES),
            0,
            "CORE_TEMPLATES must be non-empty",
        )


class TestIiterCanonicalSurfaceFilesPlumbing(unittest.TestCase):
    """_iter_canonical_surface_files from init_cmd yields real files for each surface."""

    @covers("REQ-0.0.32-14-01")
    def test_iter_skills_yields_files(self) -> None:
        """_iter_canonical_surface_files('gzkit.skills') must yield at least one file."""
        from pathlib import Path

        from gzkit.commands.init_cmd import _iter_canonical_surface_files

        results = list(_iter_canonical_surface_files("gzkit.skills"))
        self.assertGreater(
            len(results),
            0,
            "_iter_canonical_surface_files('gzkit.skills') must yield files",
        )
        # Each item must be a (Traversable, Path) pair
        traversable, rel_path = results[0]
        self.assertTrue(hasattr(traversable, "read_bytes"), "First element must be Traversable")
        self.assertIsInstance(rel_path, Path, "Second element must be Path")

    @covers("REQ-0.0.32-14-01")
    def test_iter_rules_yields_files(self) -> None:
        """_iter_canonical_surface_files('gzkit.rules') must yield at least one file."""
        from gzkit.commands.init_cmd import _iter_canonical_surface_files

        results = list(_iter_canonical_surface_files("gzkit.rules"))
        self.assertGreater(
            len(results),
            0,
            "_iter_canonical_surface_files('gzkit.rules') must yield files",
        )

    @covers("REQ-0.0.32-14-01")
    def test_iter_personas_yields_files(self) -> None:
        """_iter_canonical_surface_files('gzkit.personas') must yield at least one file."""
        from gzkit.commands.init_cmd import _iter_canonical_surface_files

        results = list(_iter_canonical_surface_files("gzkit.personas"))
        self.assertGreater(
            len(results),
            0,
            "_iter_canonical_surface_files('gzkit.personas') must yield files",
        )

    @covers("REQ-0.0.32-14-01")
    def test_iter_templates_yields_files(self) -> None:
        """_iter_canonical_surface_files('gzkit.templates') must yield at least one file."""
        from gzkit.commands.init_cmd import _iter_canonical_surface_files

        results = list(_iter_canonical_surface_files("gzkit.templates"))
        self.assertGreater(
            len(results),
            0,
            "_iter_canonical_surface_files('gzkit.templates') must yield files",
        )


if __name__ == "__main__":
    unittest.main()
