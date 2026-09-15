"""Negative control for `.gzkit/rules/cli.md` § Flag Conventions verbosity rows.

`docs/design/cli-standards-v3.md` § Verbosity Levels: default WARNING, `--quiet`
ERROR, `--verbose` INFO, `--debug` DEBUG, all on stderr. The scorecard's
Mechanical row for that clause cites this control, so the control must fail
when the level map drifts, when the entrypoint ignores a flag, when logging goes
silent, and when a record reaches stdout.
"""

import logging
import sys
import unittest
from unittest import mock

import structlog

from gzkit.cli import logging as cli_logging
from gzkit.enforcement import (
    EXEMPTS_NONE,
    POPULATION_NONE,
    _ensure_production_claims_registered,
    _run_single_claim,
    get_enforcement_registry,
)

CLAIM_ID = "cli-log-levels-follow-spec"


def _record():
    _ensure_production_claims_registered()
    return next(r for r in get_enforcement_registry() if r.claim_id == CLAIM_ID)


class TestLogLevelsFollowSpecControl(unittest.TestCase):
    def setUp(self) -> None:
        root = logging.getLogger()
        self._handlers, self._level = list(root.handlers), root.level

    def tearDown(self) -> None:
        structlog.reset_defaults()
        root = logging.getLogger()
        root.handlers[:] = self._handlers
        root.setLevel(self._level)

    def test_claim_is_registered_through_the_production_seam(self) -> None:
        record = _record()
        self.assertEqual((record.exempts, record.population), (EXEMPTS_NONE, POPULATION_NONE))

    def test_control_passes_on_the_live_entrypoint(self) -> None:
        result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "PASS", result.message)

    def test_control_restores_process_logging_state(self) -> None:
        before = (list(logging.getLogger().handlers), logging.getLogger().level)
        _run_single_claim(_record())
        self.assertEqual((list(logging.getLogger().handlers), logging.getLogger().level), before)

    def test_control_fails_when_the_default_shows_info(self) -> None:
        with mock.patch.dict(cli_logging.VERBOSITY_TO_LEVEL, {"normal": logging.INFO}):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)

    def test_control_fails_when_verbose_shows_debug(self) -> None:
        with mock.patch.dict(cli_logging.VERBOSITY_TO_LEVEL, {"verbose": logging.DEBUG}):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)

    def test_control_fails_when_the_entrypoint_ignores_the_flags(self) -> None:
        real = cli_logging.configure_logging

        def always_normal(verbosity="normal", log_file=None, *, console_stream=None):  # noqa: ARG001
            real("normal", log_file, console_stream=console_stream)

        with mock.patch.object(cli_logging, "configure_logging", always_normal):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)

    def test_control_fails_when_logs_reach_stdout(self) -> None:
        real = cli_logging.configure_logging

        def to_stdout(verbosity="normal", log_file=None, *, console_stream=None):  # noqa: ARG001
            real(verbosity, log_file, console_stream=sys.stdout)

        with mock.patch.object(cli_logging, "configure_logging", to_stdout):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)


if __name__ == "__main__":
    unittest.main()
