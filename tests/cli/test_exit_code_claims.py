"""Negative control for `.gzkit/rules/cli.md` § Exit Codes code 2 (GHI #1001).

Rule `0.7.0` relabelled code 2 "Usage or System/IO", because every parse error
exits 2 (attested REQ-0.0.4-02-03) while the map and the help epilog called 2
System/IO alone. The scorecard's Mechanical row for that clause cites this
control, so the control must fail when either half of the property breaks — the
parser's exit or the help text's label — and must not pass for an always-exit
parser.
"""

import unittest
from unittest import mock

from gzkit.enforcement import (
    EXEMPTS_NONE,
    _ensure_production_claims_registered,
    _run_single_claim,
    get_enforcement_registry,
)

CLAIM_ID = "cli-usage-error-exit-two"


def _record():
    _ensure_production_claims_registered()
    return next(r for r in get_enforcement_registry() if r.claim_id == CLAIM_ID)


class TestUsageErrorExitTwoControl(unittest.TestCase):
    def test_claim_is_registered_through_the_production_seam(self) -> None:
        record = _record()
        self.assertEqual(record.exempts, EXEMPTS_NONE)

    def test_control_passes_on_the_live_parser_and_epilog(self) -> None:
        result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "PASS", result.message)

    def test_control_fails_when_a_parse_error_stops_exiting_two(self) -> None:
        def exit_one(self, message: str) -> None:  # noqa: ARG001
            raise SystemExit(1)

        with mock.patch("gzkit.cli.parser.StableArgumentParser.error", exit_one):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)

    def test_control_fails_when_the_epilog_calls_two_system_io_alone(self) -> None:
        stale = "Exit codes\n    0   Success\n    1   User/config error\n    2   System/IO error\n"
        with mock.patch("gzkit.cli.helpers.exit_codes.STANDARD_EXIT_CODES_EPILOG", stale):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)

    def test_control_fails_for_a_parser_that_rejects_everything(self) -> None:
        def always_exit_two(self, args=None, namespace=None):  # noqa: ARG001
            raise SystemExit(2)

        with mock.patch("gzkit.cli.parser.StableArgumentParser.parse_args", always_exit_two):
            result = _run_single_claim(_record())
        self.assertEqual(result.outcome, "FACADE", result.message)


if __name__ == "__main__":
    unittest.main()
