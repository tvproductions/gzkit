"""The safe-mode contract is pinned in the ledger at entry and on every amendment.

Operator ruling 2026-10-18, selecting "Hash at entry + amend event (Rec.)" (requirements
model § 11, maxim 14). The 2026-10-17 entry recorded only the contract's path while the
contract was rewritten three hours later and edited nine times since, so the ledger
could not say which suspensions and exit conditions were in force. Entry now records
the contract's hash and its suspended list and exit conditions; a committed edit while
the session is open books ``mx_contract_amended``.
"""

import hashlib
import json
import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from gzkit.events import MxContractAmendedEvent, MxSessionOpenedEvent, parse_typed_event
from tests.commands.common import SilencedConsoleTestCase, _isolated_git_env

_CONTRACT = "docs/governance/pilotage.md"
_TEXT = (
    "# contract\n\n## Authority\n\nthe operator\n\n"
    "## What is suspended, and what is not\n\n- guards advisory\n\n"
    "## Exit — seaworthiness\n\n1. every order closed\n"
)


def _root(tmp: str, text: str = _TEXT) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    path = root / _CONTRACT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return root


def _events(root: Path, event_type: str) -> list[dict]:
    ledger = root / ".gzkit" / "ledger.jsonl"
    if not ledger.exists():
        return []
    rows = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines() if line]
    return [row for row in rows if row.get("event") == event_type]


def _enter(root: Path, mode: str = "safe") -> None:
    from gzkit.commands.mx_cmd import mx_enter_cmd

    mx_enter_cmd(
        reason="harbor pilotage",
        attestor="g0",
        inspection_scope=[],
        project_root=root,
        mode=mode,
        contract=_CONTRACT if mode == "safe" else None,
    )


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class TestEntryPinsTheContract(SilencedConsoleTestCase):
    def test_entry_records_the_contracts_hash(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            (opened,) = _events(root, "mx_session_opened")
            self.assertEqual(opened["contract_sha256"], _digest(_TEXT))

    def test_entry_records_what_is_suspended_and_how_it_exits(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            (opened,) = _events(root, "mx_session_opened")
            self.assertEqual(opened["contract_suspended"], "- guards advisory")
            self.assertEqual(opened["contract_exit"], "1. every order closed")

    def test_the_hangar_pins_no_contract(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root, mode="mx")
            (opened,) = _events(root, "mx_session_opened")
            self.assertNotIn("contract_sha256", opened)

    def test_the_pinned_entry_is_a_typed_event(self) -> None:
        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            (opened,) = _events(root, "mx_session_opened")
            self.assertIsInstance(parse_typed_event(opened), MxSessionOpenedEvent)


class TestAnAmendmentIsBooked(SilencedConsoleTestCase):
    def test_a_changed_contract_books_one_amendment(self) -> None:
        from gzkit.mx.contract import book_contract_amendment

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            amended = _TEXT.replace("- guards advisory", "- guards advisory\n- ceremony")
            self.assertTrue(book_contract_amendment(root, amended, commit="abc123"))
            (event,) = _events(root, "mx_contract_amended")
            self.assertEqual(event["previous_sha256"], _digest(_TEXT))
            self.assertEqual(event["contract_sha256"], _digest(amended))
            self.assertEqual(event["contract_suspended"], "- guards advisory\n- ceremony")
            self.assertEqual(event["commit"], "abc123")
            self.assertIsInstance(parse_typed_event(event), MxContractAmendedEvent)

    def test_an_unchanged_contract_books_nothing(self) -> None:
        from gzkit.mx.contract import book_contract_amendment

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            self.assertFalse(book_contract_amendment(root, _TEXT))
            self.assertEqual(_events(root, "mx_contract_amended"), [])

    def test_the_next_change_is_measured_from_the_last_amendment(self) -> None:
        from gzkit.mx.contract import book_contract_amendment

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            first = _TEXT + "\nfirst\n"
            second = _TEXT + "\nsecond\n"
            book_contract_amendment(root, first)
            self.assertFalse(book_contract_amendment(root, first))
            book_contract_amendment(root, second)
            self.assertEqual(
                _events(root, "mx_contract_amended")[-1]["previous_sha256"], _digest(first)
            )

    def test_no_safe_session_books_nothing(self) -> None:
        from gzkit.mx.contract import book_contract_amendment

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root, mode="mx")
            self.assertFalse(book_contract_amendment(root, _TEXT + "\nedit\n"))
            self.assertEqual(_events(root, "mx_contract_amended"), [])

    def test_the_amendment_replays_in_the_corpus(self) -> None:
        from gzkit.ledger import Ledger
        from gzkit.mx.contract import book_contract_amendment
        from gzkit.ontology.corpus import project_corpus

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            book_contract_amendment(root, _TEXT + "\nedit\n")
            fidelity = project_corpus(Ledger(root / ".gzkit" / "ledger.jsonl")).fidelity
        self.assertTrue(fidelity.complete, fidelity)


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(  # noqa: S603 — git argv this test builds
        ["git", *args],
        cwd=root,
        env=_isolated_git_env(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
    )
    return result.stdout.strip()


class TestTheCommitLocusBooksTheCommittedContract(SilencedConsoleTestCase):
    def _repo(self, tmp: str) -> Path:
        root = _root(tmp)
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "g0@users.noreply.github.com")
        _git(root, "config", "user.name", "g0")
        _git(root, "add", _CONTRACT)
        _git(root, "commit", "-q", "-m", "contract")
        _enter(root)
        return root

    def test_a_committed_edit_is_booked_against_its_commit(self) -> None:
        from gzkit.mx.contract import book_committed_contract_amendment

        with TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / _CONTRACT).write_text(_TEXT + "\namended\n", encoding="utf-8")
            _git(root, "commit", "-q", "-am", "amend")
            self.assertTrue(book_committed_contract_amendment(root))
            (event,) = _events(root, "mx_contract_amended")
            self.assertEqual(event["commit"], _git(root, "rev-parse", "HEAD"))
            self.assertEqual(event["contract_sha256"], _digest(_TEXT + "\namended\n"))

    def test_an_uncommitted_edit_is_not_booked(self) -> None:
        from gzkit.mx.contract import book_committed_contract_amendment

        with TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / _CONTRACT).write_text(_TEXT + "\nworking tree only\n", encoding="utf-8")
            self.assertFalse(book_committed_contract_amendment(root))


class TestThePostCommitRecorderCallsTheBooking(unittest.TestCase):
    def test_a_booking_failure_never_breaks_the_commit(self) -> None:
        from gzkit.hooks import commit_ledger

        with (
            mock.patch.object(commit_ledger, "record_committed_artifact_edits", return_value=[]),
            mock.patch(
                "gzkit.mx.contract.book_committed_contract_amendment",
                side_effect=RuntimeError("boom"),
            ) as booking,
            mock.patch("sys.stderr"),
        ):
            self.assertEqual(commit_ledger.main([]), 0)
        booking.assert_called_once()

    def test_a_booked_amendment_is_announced(self) -> None:
        import io
        from contextlib import redirect_stdout

        from gzkit.hooks import commit_ledger

        out = io.StringIO()
        with (
            mock.patch.object(commit_ledger, "record_committed_artifact_edits", return_value=[]),
            mock.patch("gzkit.mx.contract.book_committed_contract_amendment", return_value=True),
            redirect_stdout(out),
        ):
            commit_ledger.main([])
        self.assertIn("amendment to the open safe-mode contract", out.getvalue())


class TestPinEdges(SilencedConsoleTestCase):
    def test_a_contract_without_an_exit_section_pins_an_empty_exit(self) -> None:
        from gzkit.mx.contract import contract_pin

        self.assertEqual(contract_pin("# c\n\n## Authority\n\nx\n")["contract_exit"], "")

    def test_another_sessions_pin_is_not_this_sessions(self) -> None:
        from gzkit.ledger import Ledger, LedgerEvent
        from gzkit.mx.contract import book_contract_amendment

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            other = _TEXT + "\nother session\n"
            Ledger(root / ".gzkit" / "ledger.jsonl").append(
                LedgerEvent(
                    event="mx_contract_amended",
                    id="other",
                    extra={"session_id": "other", "contract_sha256": _digest(other)},
                )
            )
            self.assertTrue(book_contract_amendment(root, other))

    def test_no_marker_books_nothing_at_the_commit_locus(self) -> None:
        from gzkit.mx.contract import book_committed_contract_amendment

        with TemporaryDirectory() as tmp:
            self.assertFalse(book_committed_contract_amendment(_root(tmp)))

    def test_a_contract_absent_from_the_commit_books_nothing(self) -> None:
        from gzkit.mx.contract import book_committed_contract_amendment

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _git(root, "init", "-q")
            _enter(root)
            self.assertFalse(book_committed_contract_amendment(root))
            self.assertEqual(_events(root, "mx_contract_amended"), [])

    def test_no_git_books_nothing(self) -> None:
        from gzkit.mx import contract

        with TemporaryDirectory() as tmp:
            root = _root(tmp)
            _enter(root)
            with mock.patch.object(contract.subprocess, "run", side_effect=OSError("no git")):
                self.assertFalse(contract.book_committed_contract_amendment(root))


if __name__ == "__main__":
    unittest.main()
