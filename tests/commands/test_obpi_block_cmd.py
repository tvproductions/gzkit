"""`gz obpi block` / `gz obpi unblock` end-to-end (GHI #887).

The projection and the launch guard are pinned in `tests/governance/`. These
tests pin the operator-facing surface: that the pair actually writes Layer-2
events, that both refuse an empty payload, and that `--dry-run` writes nothing.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import Ledger, adr_created_event, obpi_created_event
from tests.commands.common import CliRunner, _quick_init

OBPI = "OBPI-0.1.0-01"


def _seed() -> Ledger:
    ledger = Ledger(Path.cwd() / ".gzkit" / "ledger.jsonl")
    ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "heavy"))
    ledger.append(obpi_created_event(OBPI, "ADR-0.1.0"))
    return ledger


def _events_of(kind: str) -> list[dict]:
    text = (Path.cwd() / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [r for r in rows if r.get("event") == kind]


class TestObpiBlockCommand(unittest.TestCase):
    """Blocking writes a Layer-2 record carrying both the reason and the awaited act."""

    def test_block_writes_the_event_with_both_payload_fields(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed()
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "block",
                    OBPI,
                    "--reason",
                    "REQ-04 contradicts its counterexample test",
                    "--next-action",
                    "amend REQ-04 under attestation",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            rows = _events_of("obpi_blocked_on_operator")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["reason"], "REQ-04 contradicts its counterexample test")
            self.assertEqual(rows[0]["next_operator_action"], "amend REQ-04 under attestation")

    def test_block_requires_a_named_next_action(self) -> None:
        """A block naming no awaited act is a complaint a second reader cannot discharge."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed()
            result = runner.invoke(
                main, ["obpi", "block", OBPI, "--reason", "stuck", "--next-action", "   "]
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertEqual(_events_of("obpi_blocked_on_operator"), [])

    def test_block_dry_run_writes_nothing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed()
            result = runner.invoke(
                main,
                ["obpi", "block", OBPI, "--reason", "r", "--next-action", "a", "--dry-run"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertEqual(_events_of("obpi_blocked_on_operator"), [])

    def test_block_refuses_an_obpi_absent_from_the_ledger(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main, ["obpi", "block", "OBPI-9.9.9-99", "--reason", "r", "--next-action", "a"]
            )
            self.assertNotEqual(result.exit_code, 0)


class TestObpiUnblockCommand(unittest.TestCase):
    """Unblocking records the operator's own words, not the agent's summary of them."""

    def test_unblock_writes_the_ruling_verbatim(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed()
            runner.invoke(main, ["obpi", "block", OBPI, "--reason", "r", "--next-action", "a"])
            result = runner.invoke(
                main,
                [
                    "obpi",
                    "unblock",
                    OBPI,
                    "--ruling",
                    "amend REQ-04; the append path is a separate defect",
                    "--operator",
                    "g0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            rows = _events_of("obpi_unblocked")
            self.assertEqual(len(rows), 1)
            self.assertEqual(
                rows[0]["ruling"], "amend REQ-04; the append path is a separate defect"
            )
            self.assertEqual(rows[0]["operator"], "g0")

    def test_unblock_requires_a_non_empty_ruling(self) -> None:
        """An empty ruling would clear the block while recording no decision."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed()
            runner.invoke(main, ["obpi", "block", OBPI, "--reason", "r", "--next-action", "a"])
            result = runner.invoke(
                main, ["obpi", "unblock", OBPI, "--ruling", "  ", "--operator", "g0"]
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertEqual(_events_of("obpi_unblocked"), [])

    def test_block_and_unblock_round_trip_leaves_the_obpi_runnable(self) -> None:
        """The pair composes: after a ruling the projection reports nothing blocked."""
        from gzkit.obpi_lifecycle import operator_block_state

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed()
            runner.invoke(main, ["obpi", "block", OBPI, "--reason", "r", "--next-action", "a"])
            runner.invoke(main, ["obpi", "unblock", OBPI, "--ruling", "ruled", "--operator", "g0"])
            text = (Path.cwd() / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
            rows = [json.loads(line) for line in text.splitlines() if line.strip()]
            self.assertEqual(operator_block_state(rows), {})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
