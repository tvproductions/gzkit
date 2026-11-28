"""The coverage-floor gate applies the manifest's ``coverage_floor`` (GHI #1415).

``thresholds.coverage_floor`` in the project manifest is the floor's one
authority. These tests drive the gate's ``main`` with the manifest and the
measured total substituted, so a floor hardcoded in ``main`` fails them, which
the gate's own ``--self-test`` (pure decision functions only) cannot detect.
"""

import contextlib
import importlib.util
import io
import unittest
from typing import TYPE_CHECKING
from unittest import mock

from gzkit.commands.common import get_project_root

if TYPE_CHECKING:
    from types import ModuleType

# The canonical authored copy; `gz validate --distribution` holds the package
# mirror to it byte for byte.
_SCRIPT = get_project_root() / ".gzkit" / "chores" / "coverage-40pct" / "check_coverage_floor.py"


def _load_gate() -> ModuleType:
    """Import the chore script by path; its directory name is not an identifier."""
    spec = importlib.util.spec_from_file_location("_coverage_floor_gate", _SCRIPT)
    if spec is None or spec.loader is None:
        msg = f"cannot load {_SCRIPT}"
        raise unittest.SkipTest(msg)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestTheGateAppliesTheManifestFloor(unittest.TestCase):
    """``main`` compares the measured total against the manifest's floor."""

    def _run(self, manifest: dict, total: float) -> int:
        gate = _load_gate()
        with (
            mock.patch.object(gate, "load_manifest", return_value=manifest),
            mock.patch.object(gate, "_measured_total", return_value=total),
            contextlib.redirect_stdout(io.StringIO()),
            contextlib.redirect_stderr(io.StringIO()),
        ):
            return gate.main([])

    def test_a_raised_manifest_floor_is_a_policy_breach(self) -> None:
        self.assertEqual(self._run({"thresholds": {"coverage_floor": 75.0}}, 50.0), 3)

    def test_coverage_at_the_declared_floor_passes(self) -> None:
        self.assertEqual(self._run({"thresholds": {"coverage_floor": 50.0}}, 50.0), 0)

    def test_an_undeclared_floor_is_an_error_not_a_default(self) -> None:
        self.assertEqual(self._run({"thresholds": {}}, 50.0), 1)


if __name__ == "__main__":
    unittest.main()
