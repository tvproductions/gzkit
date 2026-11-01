"""A handler's returned exit code reaches the shell (GHI #1198).

Every test here runs through the CLI entry point, because the defect sat between
the handler and the process: the handler refused and returned 1, and ``cli.main``
returned 0.
"""

import argparse
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.ledger import Ledger
from tests.commands.common import CliRunner, _quick_init

_OBPI = "OBPI-0.12.0-04"
_ROLE = ("--role", "Implementer", "--model", "sonnet")


class TestMainHonoursAReturnedExitCode(unittest.TestCase):
    """``cli.main`` carries a handler's int to the shell, and nothing else."""

    def _exit_for(self, result: object) -> int:
        parser = argparse.ArgumentParser()
        parser.set_defaults(func=lambda _args: result)
        with patch("gzkit.cli.main._get_parser", return_value=parser):
            return main([])

    def test_a_returned_refusal_is_the_exit_code(self) -> None:
        for code in (1, 2, 3):
            with self.subTest(code=code):
                self.assertEqual(self._exit_for(code), code)

    def test_a_handler_that_returns_zero_or_nothing_exits_zero(self) -> None:
        for result in (0, None):
            with self.subTest(result=result):
                self.assertEqual(self._exit_for(result), 0)

    def test_a_returned_value_that_is_not_a_code_exits_zero(self) -> None:
        self.assertEqual(self._exit_for("rendered text"), 0)


class _ProjectCase(unittest.TestCase):
    """A real project in a temporary directory, driven through the CLI."""

    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        self.ledger_path = Path(".gzkit/ledger.jsonl")
        self.before = len(Ledger(self.ledger_path).read_all())

    def _dispatch(self, *args: str) -> int:
        return self.runner.invoke(main, ["obpi", "dispatch", _OBPI, *args]).exit_code

    def _marker(self, **payload: object) -> None:
        marker = Path(f".claude/plans/.pipeline-active-{_OBPI}.json")
        marker.parent.mkdir(parents=True, exist_ok=True)
        body = {"obpi_id": _OBPI, "parent_adr": "ADR-0.12.0", **payload}
        marker.write_text(json.dumps(body), encoding="utf-8")

    def _new_rows(self) -> list[str]:
        return [row.event for row in Ledger(self.ledger_path).read_all()[self.before :]]


class TestObpiDispatchRefusalsExitOne(_ProjectCase):
    """Each refusal ``obpi-dispatch.md`` documents exits 1 with nothing recorded."""

    def test_no_marker_on_disk(self) -> None:
        self.assertEqual(self._dispatch(*_ROLE), 1)
        self.assertEqual(self._new_rows(), [])

    def test_single_driver_without_a_reason(self) -> None:
        self._marker()
        self.assertEqual(self._dispatch("--single-driver"), 1)
        self.assertEqual(self._new_rows(), [])

    def test_an_unknown_role(self) -> None:
        self._marker()
        self.assertEqual(self._dispatch("--role", "Stranger", "--model", "sonnet"), 1)
        self.assertEqual(self._new_rows(), [])

    def test_a_role_without_a_model(self) -> None:
        self._marker()
        self.assertEqual(self._dispatch("--role", "Implementer"), 1)
        self.assertEqual(self._new_rows(), [])

    def test_single_driver_on_a_marker_naming_another_obpi(self) -> None:
        self._marker(obpi_id="OBPI-0.99.0-01")
        self.assertEqual(self._dispatch("--single-driver", "--reason", "no Agent tool"), 1)
        self.assertEqual(self._new_rows(), [])

    def test_a_recorded_dispatch_exits_zero(self) -> None:
        self._marker()
        self.assertEqual(self._dispatch(*_ROLE), 0)
        self.assertEqual(self._new_rows(), ["stage2_dispatch_recorded"])


class TestAdversaryWorkspaceRefusalExitsTwo(unittest.TestCase):
    """The population's other member: its manpage says exit 2, and now the process does."""

    def test_an_unreproducible_checkout_exits_two(self) -> None:
        runner = CliRunner()
        self.enterContext(runner.isolated_filesystem())
        _quick_init()
        with patch(
            "gzkit.commands.obpi_adversary_workspace.materialize_adversary_workspace",
            side_effect=RuntimeError("checkout cannot be reproduced"),
        ):
            result = runner.invoke(main, ["obpi", "adversary-workspace", _OBPI])
        self.assertEqual(result.exit_code, 2)


if __name__ == "__main__":
    unittest.main()
