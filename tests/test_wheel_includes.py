"""Tests for wheel build configuration (OBPI-0.0.32-06 REQ-0.0.32-06-02)."""

import tomllib
import unittest
from pathlib import Path


class TestWheelIncludes(unittest.TestCase):
    """Verify wheel includes cover all canonical surfaces."""

    def test_wheel_includes_skills_rules_personas_templates(self) -> None:
        """REQ-0.0.32-06-02: include list covers skills, rules, personas, templates, hooks."""
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)

        wheel_config = config["tool"]["hatch"]["build"]["targets"]["wheel"]
        include_list = wheel_config["include"]

        required_patterns = [
            "src/gzkit/skills/**/*.md",
            "src/gzkit/rules/**/*.md",
            "src/gzkit/personas/**/*.md",
            "src/gzkit/templates/**/*.md",
            "src/gzkit/hooks/scripts/**",
        ]

        for pattern in required_patterns:
            self.assertIn(
                pattern,
                include_list,
                f"Required pattern '{pattern}' not found in wheel include list",
            )
