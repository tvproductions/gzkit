"""`gz validate --hexagon-tests`: the hexagon test gates (RP-7, change order of 2026-11-12).

The scope holds every test module covering a hexagon region to `.gzkit/rules/tests.md`
§ Hexagon tests: fakes only inside the walls, given/when/then labels, and `@covers` on
every test. Rulings of 2026-11-13 (operator): regions include the adapters, the kernel is
excluded, an adapter test may patch only targets outside the package, and a fake
adapter's tests declare their `@covers` exemption with a module comment marker.
Today's findings sit in a shrink-only baseline.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from gzkit.governance.trust_audits.hexagon_tests import (
    BASELINE_NAME,
    audit_hexagon_tests,
    check_hexagon_tests,
)
from gzkit.kernel.dependency_checker import load_package_map

if TYPE_CHECKING:
    from collections.abc import Mapping

MAP = """
[tool.py-gzkit.hexagon]
package = "app"
source-root = "src"
kernel = ["app.kernel"]
domain = ["app.core.domain"]
driving-adapters = ["app.cli"]
"""

SOURCE = {
    "app/__init__.py": "",
    "app/kernel/__init__.py": "",
    "app/core/__init__.py": "",
    "app/core/domain/__init__.py": "",
    "app/cli/__init__.py": "",
    "app/cli/main.py": "def run():\n    return 0\n",
}

LABELLED = """
import unittest

from app.cli.main import run
from gzkit.traceability import covers


class TestRun(unittest.TestCase):
    @covers("REQ-1")
    def test_run(self):
        # given
        expected = 0
        # when
        result = run()
        # then
        self.assertEqual(result, expected)
"""


def _project(root: Path, tests: Mapping[str, str], held: list[str] | None = None) -> None:
    (root / "pyproject.toml").write_text(MAP, encoding="utf-8")
    for rel, body in SOURCE.items():
        target = root / "src" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    for rel, body in tests.items():
        target = root / "tests" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    if held is not None:
        (root / "data").mkdir(parents=True, exist_ok=True)
        (root / "data" / BASELINE_NAME).write_text(json.dumps({"findings": held}), encoding="utf-8")


def _keys(tests: Mapping[str, str]) -> set[str]:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _project(root, tests)
        package_map = load_package_map(root / "pyproject.toml")
        return {f.key for f in check_hexagon_tests(package_map, root)}


def _audit(tests: Mapping[str, str], held: list[str] | None = None) -> list[str]:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _project(root, tests, held)
        return [e.message for e in audit_hexagon_tests(root)]


class WhichTestsAreHeld(unittest.TestCase):
    def test_a_conforming_adapter_test_has_no_finding(self) -> None:
        self.assertEqual(_keys({"test_run.py": LABELLED}), set())

    def test_a_test_covering_no_region_is_not_held(self) -> None:
        body = (
            "import unittest\nfrom unittest.mock import MagicMock\n\n\n"
            "class T(unittest.TestCase):\n    def test_x(self):\n        MagicMock()\n"
        )
        self.assertEqual(_keys({"test_plain.py": body}), set())

    def test_a_kernel_only_test_is_not_held(self) -> None:
        body = (
            "import unittest\nfrom app.kernel import bases\n\n\n"
            "class T(unittest.TestCase):\n    def test_x(self):\n        pass\n"
        )
        self.assertEqual(_keys({"test_kernel.py": body}), set())

    def test_a_lazy_import_inside_a_test_still_covers_the_region(self) -> None:
        body = (
            "import unittest\n\n\nclass T(unittest.TestCase):\n    def test_x(self):\n"
            "        from app.cli.main import run\n        run()\n"
        )
        self.assertIn("covers tests/test_lazy.py::T.test_x", _keys({"test_lazy.py": body}))


class FakesOnlyInsideTheWalls(unittest.TestCase):
    def test_an_inner_region_test_may_not_import_mock(self) -> None:
        body = LABELLED.replace(
            "from app.cli.main import run", "from app.core.domain import x as run"
        ).replace("import unittest\n", "import unittest\nfrom unittest import mock\n", 1)
        self.assertIn("mock tests/test_domain.py -> unittest.mock", _keys({"test_domain.py": body}))

    def test_an_adapter_test_may_not_patch_a_package_target(self) -> None:
        body = LABELLED.replace(
            '    @covers("REQ-1")\n', '    @covers("REQ-1")\n    @patch("app.cli.main.run")\n'
        ).replace("def test_run(self):", "def test_run(self, _run):")
        body = "from unittest.mock import patch\n" + body
        self.assertIn("mock tests/test_run.py -> app.cli.main.run", _keys({"test_run.py": body}))

    def test_an_adapter_test_may_patch_an_outer_target(self) -> None:
        body = "from unittest.mock import patch\n" + LABELLED.replace(
            "        result = run()\n",
            '        with patch("subprocess.run"):\n            result = run()\n',
        )
        self.assertEqual(_keys({"test_run.py": body}), set())

    def test_patch_object_on_a_package_module_is_a_finding(self) -> None:
        body = "from unittest import mock\nfrom app.cli import main\n" + LABELLED.replace(
            "        result = run()\n",
            '        with mock.patch.object(main, "run"):\n            result = run()\n',
        )
        self.assertIn("mock tests/test_run.py -> app.cli.main.run", _keys({"test_run.py": body}))

    def test_patch_object_on_an_outer_module_is_allowed(self) -> None:
        body = "import subprocess\nfrom unittest import mock\n" + LABELLED.replace(
            "        result = run()\n",
            '        with mock.patch.object(subprocess, "run"):\n            result = run()\n',
        )
        self.assertEqual(_keys({"test_run.py": body}), set())

    def test_a_bare_mock_in_an_adapter_test_is_a_finding(self) -> None:
        body = "from unittest.mock import MagicMock\n" + LABELLED.replace(
            "        expected = 0\n", "        expected = 0\n        MagicMock()\n"
        )
        self.assertIn("mock tests/test_run.py -> MagicMock()", _keys({"test_run.py": body}))


class LabelsInOrder(unittest.TestCase):
    def test_a_test_missing_a_label_is_a_finding(self) -> None:
        body = LABELLED.replace("        # when\n", "")
        self.assertIn("labels tests/test_run.py::TestRun.test_run", _keys({"test_run.py": body}))

    def test_labels_out_of_order_are_a_finding(self) -> None:
        body = (
            LABELLED.replace("# given", "# swap")
            .replace("# then", "# given")
            .replace("# swap", "# then")
        )
        self.assertIn("labels tests/test_run.py::TestRun.test_run", _keys({"test_run.py": body}))

    def test_a_label_with_words_after_it_counts(self) -> None:
        body = LABELLED.replace("# given", "# Given a run that succeeds")
        self.assertEqual(_keys({"test_run.py": body}), set())


class EveryTestNamesItsReq(unittest.TestCase):
    def test_a_test_without_covers_is_a_finding(self) -> None:
        body = LABELLED.replace('    @covers("REQ-1")\n', "")
        self.assertIn("covers tests/test_run.py::TestRun.test_run", _keys({"test_run.py": body}))

    def test_the_fake_adapter_marker_exempts_covers_only(self) -> None:
        body = "# hexagon-test: fake-adapter\n" + LABELLED.replace(
            '    @covers("REQ-1")\n', ""
        ).replace("        # when\n", "")
        keys = _keys({"test_fake.py": body})
        self.assertNotIn("covers tests/test_fake.py::TestRun.test_run", keys)
        self.assertIn("labels tests/test_fake.py::TestRun.test_run", keys)


UNCOVERED = {"test_run.py": LABELLED.replace('    @covers("REQ-1")\n', "")}

UNCOVERED_KEY = "covers tests/test_run.py::TestRun.test_run"


class TheScopeJudgesAgainstTheBaseline(unittest.TestCase):
    def test_a_new_finding_fails_and_names_the_fix(self) -> None:
        errors = _audit(UNCOVERED, held=[])
        self.assertEqual(len(errors), 1)
        self.assertIn(UNCOVERED_KEY, errors[0])
        self.assertIn("uv run gz validate --hexagon-tests", errors[0])
        self.assertIn(".gzkit/rules/tests.md § Hexagon tests", errors[0])

    def test_a_held_finding_passes(self) -> None:
        self.assertEqual(_audit(UNCOVERED, held=[UNCOVERED_KEY]), [])

    def test_a_repaired_finding_must_leave_the_baseline(self) -> None:
        errors = _audit({"test_run.py": LABELLED}, held=[UNCOVERED_KEY])
        self.assertEqual(len(errors), 1)
        self.assertIn("repaired", errors[0])

    def test_a_malformed_baseline_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _project(root, UNCOVERED)
            (root / "data").mkdir()
            (root / "data" / BASELINE_NAME).write_text("[1, 2]", encoding="utf-8")
            errors = audit_hexagon_tests(root)
        self.assertEqual(len(errors), 1)
        self.assertIn("cannot be read", errors[0].message)

    def test_an_unparseable_test_module_fails(self) -> None:
        errors = _audit({"test_run.py": LABELLED, "test_broken.py": "def (:\n"}, held=[])
        self.assertTrue(any("test_broken.py" in e for e in errors))

    def test_a_project_without_a_package_map_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text("[project]\nname = 'x'\n", encoding="utf-8")
            self.assertEqual(audit_hexagon_tests(root), [])


if __name__ == "__main__":
    unittest.main()
