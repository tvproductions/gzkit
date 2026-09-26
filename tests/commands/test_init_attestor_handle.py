"""`gz init` records the project's attestor handle and never scaffolds gzkit's (GHI #1036).

gzkit builds itself: its own `.gzkit.json` carries its handle, and an adopter's
`gz init` must never inherit that value. Operator, verbatim: "gzkit has a
settings and adopters will too. we need to bear in mind that gzkit is building
itself. so, we may beed scaffolding settings and adopter settings".
"""

import json
import unittest
from pathlib import Path

from gzkit.cli.main import main
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

_CONFIG = Path(".gzkit.json")


def setUpModule() -> None:
    """Stub the init subprocess boundaries (uv sync + ruff format)."""
    start_init_subprocess_patches()


def tearDownModule() -> None:
    stop_init_subprocess_patches()


def _authorship() -> dict:
    return json.loads(_CONFIG.read_text(encoding="utf-8")).get("authorship", {})


class InitRecordsTheHandle(unittest.TestCase):
    def test_first_init_records_the_given_handle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--no-skeleton", "--attestor-handle", "h1"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(_authorship().get("attestor_handle"), "h1")

    def test_first_init_without_a_handle_scaffolds_none(self) -> None:
        """Control: no flag and no terminal means no value, never gzkit's own."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--no-skeleton"])

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertIsNone(_authorship().get("attestor_handle"))

    def test_repair_sets_only_the_handle(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            before = json.loads(_CONFIG.read_text(encoding="utf-8"))

            result = runner.invoke(main, ["init", "--no-skeleton", "--attestor-handle", "h2"])

            self.assertEqual(result.exit_code, 0, result.output)
            after = json.loads(_CONFIG.read_text(encoding="utf-8"))
            self.assertEqual(after["authorship"]["attestor_handle"], "h2")
            after["authorship"]["attestor_handle"] = before["authorship"].get("attestor_handle")
            self.assertEqual(after, before, "repair changed more than the handle")
            self.assertIn("authorship.attestor_handle", result.output)

    def test_repair_dry_run_lists_the_change_and_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            before = _CONFIG.read_bytes()

            result = runner.invoke(
                main, ["init", "--no-skeleton", "--dry-run", "--attestor-handle", "h3"]
            )

            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(_CONFIG.read_bytes(), before)
            self.assertIn("authorship.attestor_handle", result.output)


class InitRefusesANameShapedHandle(unittest.TestCase):
    def test_a_value_with_spaces_is_refused_and_nothing_written(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["init", "--no-skeleton", "--attestor-handle", "Jane Doe"])

            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertFalse(_CONFIG.exists())

    def test_update_with_a_handle_is_refused(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            self.assertEqual(runner.invoke(main, ["init", "--no-skeleton"]).exit_code, 0)
            before = _CONFIG.read_bytes()

            result = runner.invoke(main, ["init", "--update", "--attestor-handle", "h4"])

            self.assertNotEqual(result.exit_code, 0, result.output)
            self.assertEqual(_CONFIG.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
