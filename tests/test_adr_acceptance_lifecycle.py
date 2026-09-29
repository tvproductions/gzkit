"""ADR lifecycle transitions are validated and Accepted is reachable (GHI #1014).

Closeout wrote `Proposed -> Completed` 62 times with a hardcoded `from_state`
straight to the ledger, a pair `ADR_TRANSITIONS` forbids, and no writer ever
recorded `Accepted`. Operator rulings 2026-09-28, verbatim: "Fix forward only
(Recommended)", "Record at OBPI work start (Recommended)", "Map to Deprecated
(Recommended)", "Walk Draft→Proposed→Accepted at launch (Recommended)",
"Catch up with cited evidence (Recommended)", "Write it; fix the vocab
(Recommended)". The 62 historical rows stay as dated records.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from gzkit.cli import main
from gzkit.commands.obpi_cmd import _accept_adr_on_work_start
from gzkit.core.lifecycle import InvalidTransitionError, is_valid_transition
from gzkit.governance.status_vocab import canonicalize_status
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    lifecycle_transition_event,
    obpi_created_event,
    pipeline_launched_event,
)
from gzkit.lifecycle import closeout_transitions, current_adr_state, work_start_transitions
from gzkit.quality import QualityResult
from tests.commands.common import CliRunner, _init_git_repo, _quick_init

_ADR = "ADR-0.1.0-demo"
_OK = QualityResult(success=True, command="test", stdout="OK", stderr="", returncode=0)


class TestWorkStartTransitions(unittest.TestCase):
    """Starting OBPI work accepts the ADR, walking Draft through Proposed."""

    def test_proposed_is_accepted(self) -> None:
        self.assertEqual(work_start_transitions("Proposed"), [("Proposed", "Accepted")])

    def test_draft_walks_through_proposed(self) -> None:
        self.assertEqual(
            work_start_transitions("Draft"), [("Draft", "Proposed"), ("Proposed", "Accepted")]
        )

    def test_already_accepted_or_later_is_untouched(self) -> None:
        for state in ("Accepted", "Completed", "Validated", "Superseded", None):
            with self.subTest(state=state):
                self.assertEqual(work_start_transitions(state), [])

    def test_every_emitted_pair_is_legal(self) -> None:
        for state in ("Draft", "Proposed"):
            for pair in work_start_transitions(state):
                with self.subTest(pair=pair):
                    self.assertTrue(is_valid_transition("ADR", *pair))


class TestCloseoutTransitions(unittest.TestCase):
    """Closeout starts from the ADR's actual state and refuses illegal pairs."""

    def test_accepted_completes(self) -> None:
        self.assertEqual(
            closeout_transitions("Accepted", dropped=False, work_started=True),
            [("Accepted", "Completed")],
        )

    def test_mid_flight_proposed_catches_up_through_accepted(self) -> None:
        self.assertEqual(
            closeout_transitions("Proposed", dropped=False, work_started=True),
            [("Proposed", "Accepted"), ("Accepted", "Completed")],
        )

    def test_proposed_without_work_evidence_fails_closed(self) -> None:
        with self.assertRaises(InvalidTransitionError):
            closeout_transitions("Proposed", dropped=False, work_started=False)

    def test_draft_completion_fails_closed(self) -> None:
        with self.assertRaises(InvalidTransitionError):
            closeout_transitions("Draft", dropped=False, work_started=True)

    def test_dropped_maps_to_deprecated(self) -> None:
        for state in ("Proposed", "Accepted"):
            with self.subTest(state=state):
                self.assertEqual(
                    closeout_transitions(state, dropped=True, work_started=True),
                    [(state, "Deprecated")],
                )


class TestCurrentAdrStateAndSemantics(unittest.TestCase):
    """The ledger's latest transition is the state; frontmatter is the fallback."""

    def _graph_info(self, transitions: list[tuple[str, str, str]]) -> dict:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            ledger.append(adr_created_event(_ADR, "", "lite"))
            for content_type, from_state, to_state in transitions:
                ledger.append(lifecycle_transition_event(_ADR, content_type, from_state, to_state))
            return ledger.get_artifact_graph()[_ADR]

    def test_frontmatter_is_the_fallback(self) -> None:
        self.assertEqual(current_adr_state(self._graph_info([]), "Draft"), "Draft")

    def test_latest_transition_wins_whatever_its_casing(self) -> None:
        info = self._graph_info([("ADR", "Proposed", "Accepted")])
        self.assertEqual(current_adr_state(info, "Proposed"), "Accepted")
        info = self._graph_info([("adr", "Proposed", "Completed")])
        self.assertEqual(current_adr_state(info, "Proposed"), "Completed")

    def test_accepted_derives_as_accepted_not_pending(self) -> None:
        info = self._graph_info([("ADR", "Proposed", "Accepted")])
        self.assertEqual(Ledger.derive_adr_semantics(info)["lifecycle_status"], "Accepted")

    def test_unaccepted_adr_still_derives_pending(self) -> None:
        self.assertEqual(
            Ledger.derive_adr_semantics(self._graph_info([]))["lifecycle_status"], "Pending"
        )


class TestAcceptedVocabulary(unittest.TestCase):
    """Accepted is in-progress work, never validated."""

    def test_accepted_canonicalizes_to_in_progress(self) -> None:
        self.assertEqual(canonicalize_status("Accepted"), "in_progress")


def _lifecycle_rows(adr_id: str) -> list[tuple[str, str]]:
    rows = []
    for line in Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if event.get("event") == "lifecycle_transition" and event.get("id") == adr_id:
            rows.append((event["from_state"], event["to_state"]))
    return rows


class TestCloseoutWiring(unittest.TestCase):
    """`gz closeout` writes validated transitions from the ADR's actual state."""

    @patch("gzkit.cli.main.run_command", return_value=_OK)
    @patch("builtins.input", return_value="1")
    def test_draft_adr_is_refused_before_any_write(self, _input, _run) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _init_git_repo(Path.cwd())
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(main, ["closeout", "ADR-0.1.0-f"])
            self.assertEqual(result.exit_code, 1, result.output)
            self.assertEqual(_lifecycle_rows("ADR-0.1.0-f"), [])
            ledger = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertNotIn('"event":"attested"', ledger.replace(" ", ""))

    def _plan(self, *, launched: bool) -> tuple[list[tuple[str, str]], str | None]:
        from gzkit.commands.closeout import _plan_closeout_lifecycle

        with tempfile.TemporaryDirectory() as tmp:
            ledger = Ledger(Path(tmp) / "ledger.jsonl")
            ledger.append(adr_created_event(_ADR, "", "lite"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-x", _ADR))
            if launched:
                ledger.append(
                    pipeline_launched_event(
                        obpi_id="OBPI-0.1.0-01-x",
                        parent_adr=_ADR,
                        lane="lite",
                        nonce="n",
                        marker_path=".claude/plans/m.json",
                        entry="full",
                    )
                )
            adr_file = Path(tmp) / "ADR.md"
            adr_file.write_text("---\nstatus: Proposed\n---\n", encoding="utf-8")
            return _plan_closeout_lifecycle(ledger, _ADR, adr_file, dropped=False)

    def test_mid_flight_proposed_adr_catches_up_citing_the_launch(self) -> None:
        steps, evidence = self._plan(launched=True)
        self.assertEqual(steps, [("Proposed", "Accepted"), ("Accepted", "Completed")])
        self.assertEqual(evidence, "OBPI-0.1.0-01-x")

    def test_proposed_adr_without_work_evidence_is_refused(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            self._plan(launched=False)
        self.assertEqual(ctx.exception.code, 1)


class TestWorkStartWiring(unittest.TestCase):
    """Pipeline launch records Accepted and mirrors it into ADR frontmatter."""

    def _setup(self, tmp: str, status: str) -> tuple[Ledger, Path]:
        root = Path(tmp)
        ledger = Ledger(root / "ledger.jsonl")
        ledger.append(adr_created_event(_ADR, "", "lite"))
        adr_file = root / "ADR.md"
        adr_file.write_text(f"---\nid: {_ADR}\nstatus: {status}\n---\n# ADR\n", encoding="utf-8")
        return ledger, adr_file

    def test_proposed_adr_is_accepted_in_ledger_and_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger, adr_file = self._setup(tmp, "Proposed")
            graph = ledger.get_artifact_graph()
            _accept_adr_on_work_start(Path(tmp), ledger, graph, "OBPI-0.1.0-01", _ADR, adr_file)
            self.assertEqual(ledger.get_artifact_graph()[_ADR]["lifecycle_state"], "Accepted")
            self.assertIn("status: Accepted", adr_file.read_text(encoding="utf-8"))

    def test_gate_refusal_writes_nothing_and_blocks_launch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger, adr_file = self._setup(tmp, "Draft")
            graph = ledger.get_artifact_graph()
            refusal = [SimpleNamespace(message="walkthrough required")]
            with (
                patch(
                    "gzkit.governance.trust_audits.evaluation_justify_binding."
                    "validate_evaluation_justify_binding",
                    return_value=refusal,
                ),
                self.assertRaises(SystemExit) as ctx,
            ):
                _accept_adr_on_work_start(Path(tmp), ledger, graph, "OBPI-0.1.0-01", _ADR, adr_file)
            self.assertEqual(ctx.exception.code, 3)
            self.assertIsNone(ledger.get_artifact_graph()[_ADR]["lifecycle_state"])
            self.assertIn("status: Draft", adr_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
