"""``gz arb red`` reports the witness's own reason when its run could not tell (GHI #1154).

A not-applicable witness has more than one cause (nothing withheld, a runner that
crashed before running a test, a run that executed nothing). The command must say
which, because the remedy differs: the old canned text named only the first.
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.arb import arb_red_cmd
from gzkit.red_witness import RedWitness


def _void_witness(reason: str) -> RedWitness:
    return RedWitness(
        req_id="REQ-1.2.3-01-01",
        base_commit="a" * 40,
        test_names=["tests.test_x"],
        exit_status=2,
        failure_class="not-applicable",
        output_tail=f"RED witness did not run: {reason}. This is NOT a finding about the test.",
    )


class TestArbRedReportsTheWitnessReason(unittest.TestCase):
    def _run(self, witness: RedWitness) -> tuple[int, str]:
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as td, contextlib.ExitStack() as stack:
            root = Path(td)
            stack.enter_context(
                mock.patch("gzkit.commands.common.get_project_root", return_value=root)
            )
            stack.enter_context(
                mock.patch(
                    "gzkit.red_witness.resolve_covering_test_names",
                    return_value=["tests.test_x"],
                )
            )
            stack.enter_context(
                mock.patch(
                    "gzkit.arb.red_reporter.run_red_via_arb",
                    return_value=(witness, root / "receipt.json"),
                )
            )
            stack.enter_context(mock.patch("gzkit.ledger.Ledger"))
            stack.enter_context(contextlib.redirect_stderr(err))
            stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
            code = arb_red_cmd(req="REQ-1.2.3-01-01")
        return code, err.getvalue()

    def test_a_crashed_runner_is_reported_as_such(self) -> None:
        code, stderr = self._run(_void_witness("the run printed no summary"))
        self.assertEqual(code, 0)
        self.assertIn("the run printed no summary", stderr)
        self.assertNotIn("no production hunks were withheld", stderr)


if __name__ == "__main__":
    unittest.main()
