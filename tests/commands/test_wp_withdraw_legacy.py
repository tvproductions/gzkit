"""`gz wp withdraw-legacy`, the successor to `gz obpi withdraw` (RO-14 act 7).

RO-8 withdraws legacy briefs as superseded through this verb, so `gz obpi` does not
stay open for that one job. Parity is the objective (operator, 2026-11-01: "near-parity
(if not full) for a wp and an obpi"), so a unit withdrawn here must read as withdrawn
to everything that reads a withdrawn OBPI.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

from gzkit.cli import main
from gzkit.governance.trust_audits.closeout_proof import _withdrawn_obpi_ids
from gzkit.ledger import Ledger, obpi_created_event
from gzkit.ledger_events import obpi_superseded_event
from gzkit.ledger_producer_probe import probe_producer
from gzkit.obpi_lifecycle import TERMINAL_EVENTS
from gzkit.ontology.corpus import project_corpus
from gzkit.pipeline_position import _ends_run
from tests.commands.common import CliRunner, _quick_init

_UNIT = "OBPI-0.1.0-01"
_ADR = "ADR-0.1.0"
_VERB = ("wp", "withdraw-legacy", _UNIT)
_WORDS = ("--reason", "carried to REQ-7", "--attestor", "g0")


def _ledger() -> Ledger:
    return Ledger(Path(".gzkit") / "ledger.jsonl")


class TestImport(unittest.TestCase):
    def test_the_rule_imports_as_a_process_first_import(self) -> None:
        # In one process the suite has already loaded `gzkit.ledger`, hiding the cycle.
        run = subprocess.run(
            [sys.executable, "-c", "import gzkit.legacy_units"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(run.returncode, 0, msg=run.stderr)


class TestWithdrawLegacy(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()
        self.enterContext(self.runner.isolated_filesystem())
        _quick_init()
        _ledger().append(obpi_created_event(_UNIT, _ADR))

    def _rows(self) -> list[object]:
        return list(_ledger().query(event_type="legacy_unit_withdrawn"))

    def test_it_books_the_ruled_event_with_the_units_parent(self) -> None:
        result = self.runner.invoke(main, [*_VERB, *_WORDS])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        row = _ledger().query(event_type="legacy_unit_withdrawn")[0]
        self.assertEqual(row.id, _UNIT)
        self.assertEqual(row.parent, _ADR)
        self.assertEqual(row.extra["reason"], "carried to REQ-7")
        self.assertEqual(row.extra["attestor"], "g0")

    def test_a_withdrawn_unit_reads_withdrawn_in_the_artifact_graph(self) -> None:
        self.runner.invoke(main, [*_VERB, *_WORDS])
        node = _ledger().get_artifact_graph()[_UNIT]
        self.assertTrue(node["withdrawn"])
        self.assertEqual(node["withdrawn_reason"], "carried to REQ-7")

    def test_the_corpus_projection_accounts_for_the_withdrawal(self) -> None:
        self.runner.invoke(main, [*_VERB, *_WORDS])
        projection = project_corpus(_ledger())
        self.assertEqual(projection.fidelity.unaccounted_event_types, ())
        self.assertTrue(projection.fidelity.complete)
        self.assertTrue(projection.source_graph[_UNIT]["withdrawn"])

    def test_the_closeout_proof_reads_the_withdrawal(self) -> None:
        self.runner.invoke(main, [*_VERB, *_WORDS])
        self.assertIn(_UNIT, _withdrawn_obpi_ids(Path.cwd()))

    def test_the_withdrawal_ends_a_run(self) -> None:
        self.assertTrue(_ends_run(mock.Mock(event="legacy_unit_withdrawn")))

    def test_the_withdrawal_is_terminal(self) -> None:
        self.assertIn("legacy_unit_withdrawn", TERMINAL_EVENTS)

    def test_the_producer_probe_verifies_the_writer(self) -> None:
        observation = probe_producer("legacy_unit_withdrawn")
        self.assertEqual(observation.status, "verified", msg=observation.error)

    def test_a_superseded_unit_is_refused(self) -> None:
        _ledger().append(obpi_superseded_event(_UNIT, _ADR, "OBPI-0.1.0-02", "r", "g0"))
        result = self.runner.invoke(main, [*_VERB, *_WORDS])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertEqual(self._rows(), [])

    def test_a_dry_run_shows_the_event_without_json(self) -> None:
        result = self.runner.invoke(main, [*_VERB, *_WORDS, "--dry-run"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertIn("legacy_unit_withdrawn", result.output)
        self.assertEqual(self._rows(), [])

    def test_withdrawing_twice_is_refused_through_either_verb(self) -> None:
        self.runner.invoke(main, [*_VERB, *_WORDS])
        again = self.runner.invoke(main, [*_VERB, *_WORDS])
        self.assertEqual(again.exit_code, 3, msg=again.output)
        old = self.runner.invoke(main, ["obpi", "withdraw", _UNIT, *_WORDS])
        self.assertNotEqual(old.exit_code, 0, msg=old.output)
        self.assertEqual(len(self._rows()), 1)

    def test_a_unit_gz_obpi_withdrew_is_refused(self) -> None:
        self.runner.invoke(main, ["obpi", "withdraw", _UNIT, *_WORDS])
        result = self.runner.invoke(main, [*_VERB, *_WORDS])
        self.assertEqual(result.exit_code, 3, msg=result.output)

    def test_an_unknown_unit_exits_1_and_writes_nothing(self) -> None:
        result = self.runner.invoke(main, ["wp", "withdraw-legacy", "OBPI-9.9.9-09", *_WORDS])
        self.assertEqual(result.exit_code, 1, msg=result.output)
        self.assertEqual(self._rows(), [])

    def test_a_blank_attestor_is_refused(self) -> None:
        result = self.runner.invoke(main, [*_VERB, "--reason", "r", "--attestor", "  "])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertEqual(self._rows(), [])

    def test_a_blank_reason_is_refused(self) -> None:
        result = self.runner.invoke(main, [*_VERB, "--reason", "  ", "--attestor", "g0"])
        self.assertEqual(result.exit_code, 3, msg=result.output)
        self.assertEqual(self._rows(), [])

    def test_the_attestor_is_required_and_never_defaulted(self) -> None:
        result = self.runner.invoke(main, [*_VERB, "--reason", "r"])
        self.assertEqual(result.exit_code, 2, msg=result.output)

    def test_a_dry_run_writes_nothing(self) -> None:
        result = self.runner.invoke(main, [*_VERB, *_WORDS, "--dry-run", "--json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(json.loads(result.output)["id"], _UNIT)
        self.assertEqual(self._rows(), [])


if __name__ == "__main__":
    unittest.main()
