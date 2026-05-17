"""CLI smoke tests for gz content import — OBPI-0.0.34-03.

Covers REQ-0.0.34-03-01, REQ-0.0.34-03-04, REQ-0.0.34-03-05.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.cli.main import main
from gzkit.content.models import Rule, Skill
from gzkit.content.render import render
from gzkit.traceability import covers
from tests.commands.common import CliRunner


class TestContentImportCmd(unittest.TestCase):
    """CLI smoke tests for gz content import."""

    def setUp(self) -> None:
        self._runner = CliRunner()
        self._tempdir = tempfile.TemporaryDirectory()
        self._tmp = Path(self._tempdir.name)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    def _canonical_rule_path(self) -> Path:
        rule = Rule(title="Test Rule", version="1.0.0", paths=[], body=[])
        p = self._tmp / "rule.md"
        p.write_bytes(render(rule, "claude"))
        return p

    def _canonical_skill_path(self) -> Path:
        skill = Skill(slug="test-skill", title="Test Skill", purpose="Does things", steps=[])
        p = self._tmp / "skill.md"
        p.write_bytes(render(skill, "claude"))
        return p

    # REQ-0.0.34-03-01 --------------------------------------------------------

    @covers("REQ-0.0.34-03-01")
    def test_import_canonical_rule_emits_json_exits_0(self) -> None:
        """gz content import <canonical-rule> --as Rule emits JSON, exits 0."""
        rule_path = self._canonical_rule_path()
        result = self._runner.invoke(main, ["content", "import", str(rule_path), "--as", "Rule"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        data = json.loads(result.output)
        self.assertEqual(data["title"], "Test Rule")
        self.assertEqual(data["version"], "1.0.0")

    @covers("REQ-0.0.34-03-01")
    def test_import_unknown_type_exits_1(self) -> None:
        """gz content import --as UnknownType exits 1 (type not in CONTENT_MODELS)."""
        dummy = self._tmp / "dummy.md"
        dummy.write_text("# dummy\n", encoding="utf-8")
        result = self._runner.invoke(main, ["content", "import", str(dummy), "--as", "UnknownType"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("unknown content type", result.output.lower())

    # REQ-0.0.34-03-04 --------------------------------------------------------

    @covers("REQ-0.0.34-03-04")
    def test_import_missing_file_exits_1(self) -> None:
        """gz content import <nonexistent> exits 1 with file-not-found message."""
        result = self._runner.invoke(
            main,
            ["content", "import", str(self._tmp / "no-such.md"), "--as", "Rule"],
        )
        self.assertEqual(result.exit_code, 1)
        self.assertIn("not found", result.output.lower())

    @covers("REQ-0.0.34-03-04")
    def test_import_malformed_input_exits_nonzero(self) -> None:
        """gz content import <malformed.md> exits non-zero with error diagnostic."""
        bad = self._tmp / "bad.md"
        bad.write_text("not valid markdown for any content type\n", encoding="utf-8")
        result = self._runner.invoke(main, ["content", "import", str(bad), "--as", "Rule"])
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("error", result.output.lower())

    # REQ-0.0.34-03-05 --------------------------------------------------------

    @covers("REQ-0.0.34-03-03")
    def test_import_write_is_idempotent(self) -> None:
        """gz content import --write is idempotent: second pass output equals first pass output."""
        rule = Rule(title="Migration Test", version="2.0.0", paths=[], body=[])
        canonical = self._tmp / "canonical.md"
        canonical.write_bytes(render(rule, "claude"))

        out1 = self._tmp / "out1.md"
        out2 = self._tmp / "out2.md"

        r1 = self._runner.invoke(
            main,
            ["content", "import", str(canonical), "--as", "Rule", "--write", str(out1)],
        )
        self.assertEqual(r1.exit_code, 0, msg=r1.output)

        r2 = self._runner.invoke(
            main,
            ["content", "import", str(out1), "--as", "Rule", "--write", str(out2)],
        )
        self.assertEqual(r2.exit_code, 0, msg=r2.output)

        self.assertEqual(
            out1.read_bytes(),
            out2.read_bytes(),
            "Second import+write must produce identical bytes to first (idempotency)",
        )

    @covers("REQ-0.0.34-03-05")
    def test_import_type_mismatch_exits_1(self) -> None:
        """Type mismatch (Rule file imported --as Skill) exits 1 before returning model."""
        rule_path = self._canonical_rule_path()
        result = self._runner.invoke(main, ["content", "import", str(rule_path), "--as", "Skill"])
        self.assertEqual(result.exit_code, 1)
        self.assertIn("error", result.output.lower())
