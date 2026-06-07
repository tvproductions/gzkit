"""Tests for gz obpi withdraw command — REQ-0.0.67-02-04.

Verifies that ``obpi_withdraw_cmd`` emits an ``obpi_withdrawn`` event on first
call and that re-withdrawal of the same OBPI is rejected.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import Ledger
from gzkit.ledger_events import obpi_created_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


class TestObpiWithdrawCmd(unittest.TestCase):
    """``gz obpi withdraw`` event emission and double-withdrawal rejection (REQ-0.0.67-02-04)."""

    @covers("REQ-0.0.67-02-04")
    def test_withdraw_emits_obpi_withdrawn_event(self) -> None:
        """obpi_withdraw_cmd emits an obpi_withdrawn event with reason payload.

        Seeds the ledger with an obpi_created event, then invokes withdraw.
        Verifies exit 0 and that a well-formed obpi_withdrawn entry appears
        in the main ledger with the correct id and reason.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            ledger = Ledger(ledger_path)
            ledger.append(obpi_created_event("OBPI-0.0.99-01", "ADR-0.0.99"))

            result = runner.invoke(
                main,
                ["obpi", "withdraw", "OBPI-0.0.99-01", "--reason", "test withdrawal"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

            events = [
                json.loads(line)
                for line in ledger_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            withdrawn = [e for e in events if e.get("event") == "obpi_withdrawn"]
            self.assertEqual(len(withdrawn), 1, msg="Exactly one obpi_withdrawn event expected")
            self.assertEqual(withdrawn[0]["id"], "OBPI-0.0.99-01")
            # LedgerEvent serializes extra dict as top-level fields (flattened).
            self.assertEqual(withdrawn[0]["reason"], "test withdrawal")

    @covers("REQ-0.0.67-02-04")
    def test_double_withdraw_rejected(self) -> None:
        """Re-withdrawal of the same OBPI is rejected with a non-zero exit code.

        After a successful withdrawal, a second withdraw call for the same OBPI
        must fail — the OBPI is already marked withdrawn in the ledger graph
        and the command raises GzCliError (exit 1).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_path = Path(".gzkit/ledger.jsonl")
            ledger = Ledger(ledger_path)
            ledger.append(obpi_created_event("OBPI-0.0.99-01", "ADR-0.0.99"))

            first = runner.invoke(
                main,
                ["obpi", "withdraw", "OBPI-0.0.99-01", "--reason", "first withdrawal"],
            )
            self.assertEqual(first.exit_code, 0, msg=first.output)

            second = runner.invoke(
                main,
                ["obpi", "withdraw", "OBPI-0.0.99-01", "--reason", "second withdrawal"],
            )
            self.assertNotEqual(
                second.exit_code,
                0,
                msg="Re-withdrawal must be rejected with non-zero exit code",
            )
            self.assertIn("already withdrawn", second.output.lower())


if __name__ == "__main__":
    unittest.main()
