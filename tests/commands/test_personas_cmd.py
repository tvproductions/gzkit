"""Tests for gz personas list command."""

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init

_VALID_PERSONA = """\
---
name: tester
traits:
  - methodical
  - thorough
anti-traits:
  - shallow-compliance
grounding: Evidence-first.
---

# Tester Persona
"""


class TestPersonasListCmd(unittest.TestCase):
    """Tests for ``gz personas list``."""

    def setUp(self) -> None:
        self.runner = CliRunner()

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_no_dir(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No personas directory", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_empty_dir(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            Path(".gzkit/personas").mkdir(parents=True)
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("No persona files", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_with_file(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            pdir.mkdir(parents=True)
            (pdir / "tester.md").write_text(_VALID_PERSONA, encoding="utf-8")
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("tester", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_json_mode(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            pdir.mkdir(parents=True)
            (pdir / "tester.md").write_text(_VALID_PERSONA, encoding="utf-8")
            result = self.runner.invoke(main, ["personas", "list", "--json"])
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.output)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["name"], "tester")
            self.assertEqual(data[0]["traits"], ["methodical", "thorough"])

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_malformed_warns(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            pdir = Path(".gzkit/personas")
            pdir.mkdir(parents=True)
            (pdir / "bad.md").write_text("no frontmatter here", encoding="utf-8")
            result = self.runner.invoke(main, ["personas", "list"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("WARNING", result.output)

    @covers("REQ-0.0.11-02-02")
    def test_personas_list_json_empty_dir(self) -> None:
        with self.runner.isolated_filesystem():
            _quick_init()
            Path(".gzkit/personas").mkdir(parents=True)
            result = self.runner.invoke(main, ["personas", "list", "--json"])
            self.assertEqual(result.exit_code, 0)
            data = json.loads(result.output)
            self.assertEqual(data, [])
