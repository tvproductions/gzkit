"""Tests for the advisory test-shape inventory (GHI #571).

Assertions derive from the requirement — the screen reports test shape and never gates
— not from a run of the scanner.

The advisory contract is the load-bearing property here. 824 of 832 output assertions
in this repo are undeclared, and most are legitimate render-contract tests permitted by
`.gzkit/rules/tests.md` § Output-form fixture carve-out. A gate would redden a green
trunk. `test_command_always_exits_zero` is what stops a later change from making it one.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.test_shape import scan_output_assertions


class _TreeFixture(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        (self.root / "tests").mkdir()

    def write(self, name: str, body: str) -> None:
        (self.root / "tests" / name).write_text(body, encoding="utf-8")

    def scan(self) -> list:
        return scan_output_assertions(self.root / "tests", self.root)


class TestOutputAssertionDetection(_TreeFixture):
    def test_assertion_on_result_output_is_flagged(self) -> None:
        self.write(
            "test_a.py",
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_x(self):\n        self.assertIn('a', result.output)\n",
        )
        found = self.scan()
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0].source_kind, "output")
        self.assertFalse(found[0].declared)

    def test_getvalue_is_flagged(self) -> None:
        self.write(
            "test_a.py",
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_x(self):\n        self.assertEqual(buf.getvalue(), 'a')\n",
        )
        self.assertEqual(self.scan()[0].source_kind, "getvalue")

    def test_assert_regex_is_flagged(self) -> None:
        self.write(
            "test_a.py",
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_x(self):\n        self.assertRegex(value, 'a')\n",
        )
        self.assertEqual(self.scan()[0].source_kind, "assertRegex")

    def test_function_without_an_assertion_is_not_flagged(self) -> None:
        """Touching output is not a finding; asserting on it is."""
        self.write(
            "test_a.py",
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_x(self):\n        print(result.output)\n",
        )
        self.assertEqual(self.scan(), [])

    def test_assertion_without_output_source_is_not_flagged(self) -> None:
        self.write(
            "test_a.py",
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_x(self):\n        self.assertEqual(model.field, 1)\n",
        )
        self.assertEqual(self.scan(), [])

    def test_fixture_methods_are_skipped(self) -> None:
        self.write(
            "test_a.py",
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def setUp(self):\n        self.assertIn('a', result.output)\n",
        )
        self.assertEqual(self.scan(), [])

    def test_non_test_files_are_not_scanned(self) -> None:
        (self.root / "tests" / "helper.py").write_text(
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_x(self):\n        self.assertIn('a', result.output)\n",
            encoding="utf-8",
        )
        self.assertEqual(self.scan(), [])


class TestCarveOutDeclaration(_TreeFixture):
    """The carve-out is declared by marker or by class name — the doctrine's two forms."""

    def test_output_contract_marker_declares_the_carve_out(self) -> None:
        self.write(
            "test_a.py",
            "import unittest\n\nclass T(unittest.TestCase):\n"
            "    def test_x(self):\n"
            "        # output-contract: the table header IS the operator contract\n"
            "        self.assertIn('a', result.output)\n",
        )
        found = self.scan()[0]
        self.assertTrue(found.declared)
        self.assertEqual(found.marker_reason, "the table header IS the operator contract")

    def test_class_name_suffix_declares_the_carve_out(self) -> None:
        for suffix in ("OutputForm", "OutputContract", "Rendering"):
            with self.subTest(suffix=suffix):
                self.write(
                    "test_a.py",
                    f"import unittest\n\nclass Test{suffix}(unittest.TestCase):\n"
                    "    def test_x(self):\n        self.assertIn('a', result.output)\n",
                )
                self.assertTrue(self.scan()[0].declared)

    def test_an_unrelated_class_name_does_not_declare(self) -> None:
        self.write(
            "test_a.py",
            "import unittest\n\nclass TestOutputThings(unittest.TestCase):\n"
            "    def test_x(self):\n        self.assertIn('a', result.output)\n",
        )
        self.assertFalse(self.scan()[0].declared)

    def test_marker_outside_the_function_span_does_not_declare(self) -> None:
        """A module-level marker must not silently declare every test in the file."""
        self.write(
            "test_a.py",
            "# output-contract: module level\nimport unittest\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_x(self):\n        self.assertIn('a', result.output)\n",
        )
        self.assertFalse(self.scan()[0].declared)


class TestAdvisoryContract(unittest.TestCase):
    """`gz test-shape` reports; it never gates. This is the safety property."""

    def test_command_always_exits_zero(self) -> None:
        """Even with findings present, the advisory command returns 0.

        A later change that made this a gate would fail here. 824 of this repo's 832
        output assertions are undeclared; a fail-closed screen would block every commit.
        """
        from gzkit.commands import test_shape as mod

        inventory = mock.MagicMock()
        inventory.tautological = [mock.MagicMock(disposition="convert")]
        inventory.by_disposition = {"convert": 1}
        inventory.output_assertions = [mock.MagicMock(file_path="tests/x.py")]
        inventory.undeclared_output_assertions = inventory.output_assertions

        with (
            mock.patch.object(mod, "get_project_root", return_value=Path(".")),
            mock.patch.object(mod, "build_inventory", return_value=inventory),
            mock.patch.object(mod, "console"),
        ):
            self.assertEqual(mod.test_shape_cmd(), 0)

    def test_by_disposition_rolls_up_the_dispositions(self) -> None:
        """The roll-up GHI #571's predecessor cited but that never existed."""
        from gzkit.test_shape import TautologicalOp, TestShapeInventory

        ops = [
            TautologicalOp(
                file_path="tests/a.py",
                line_number=i,
                function_name=f"t{i}",
                operation_kind="exists",
                disposition=d,
            )
            for i, d in enumerate(["convert", "convert", "fold-to-validator"], start=1)
        ]
        inventory = TestShapeInventory(tautological=ops, output_assertions=[])
        self.assertEqual(inventory.by_disposition, {"convert": 2, "fold-to-validator": 1})


if __name__ == "__main__":
    unittest.main()
