"""Tests for wheel build configuration (OBPI-0.0.32-06 REQ-0.0.32-06-02)."""

import unittest
from pathlib import Path

from gzkit.governance.trust_audits.distribution import wheel_shipped_files

REPO_ROOT = Path(__file__).parent.parent


class TestWheelIncludes(unittest.TestCase):
    """Verify the wheel ships every canonical surface.

    The hatchling include list this read was retired for uv_build on 2026-10-22
    (RO-9 tranche 3), which ships the module tree whole; the assertion reads the
    predicted wheel, the one `gz validate --distribution` reads.
    """

    def test_wheel_ships_skills_rules_personas_templates_hooks(self) -> None:
        """REQ-0.0.32-06-02: the wheel ships skills, rules, personas, templates, hooks."""
        shipped = wheel_shipped_files(REPO_ROOT)
        for surface in ("skills", "rules", "personas", "templates", "hooks/scripts"):
            with self.subTest(surface=surface):
                on_disk = {
                    path.relative_to(REPO_ROOT).as_posix()
                    for path in (REPO_ROOT / "src" / "gzkit" / surface).rglob("*.md")
                }
                if surface == "hooks/scripts":
                    on_disk = {
                        path.relative_to(REPO_ROOT).as_posix()
                        for path in (REPO_ROOT / "src" / "gzkit" / surface).rglob("*")
                        if path.is_file() and "__pycache__" not in path.parts
                    }
                self.assertTrue(on_disk, msg=f"no {surface} files on disk to ship")
                self.assertLessEqual(on_disk, shipped)


if __name__ == "__main__":
    unittest.main()
