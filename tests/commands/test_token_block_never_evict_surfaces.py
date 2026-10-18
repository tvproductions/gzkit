"""The operator-facing surfaces of "an expired token block is booked, never evicted".

Follow-up to f29a96a4f (operator ruling 2026-10-18), whose ``gz arb red --commit``
witness found these branches undriven by that commit's own tests: the claim refusal's
recovery prose, the check and list renderings of an expired lock, preflight's handling
of an unreadable lock file, an orphan session lock and an apply over held leases, the
reaper's once-per-claim booking against a real ledger, and the corpus projection.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from gzkit.ledger import Ledger
from gzkit.lock_manager import LockData, reap_expired_locks, write_lock
from gzkit.mx.marker import SESSION_LOCK_KEY
from gzkit.ontology.corpus import project_corpus


def _root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir()
    (root / ".gzkit" / "ledger.jsonl").write_text("", encoding="utf-8")
    (root / ".gzkit.json").write_text(
        json.dumps(
            {"project_name": "t", "mode": "lite", "paths": {"ledger": ".gzkit/ledger.jsonl"}}
        ),
        encoding="utf-8",
    )
    return root


def _expired(root: Path, obpi_id: str = "OBPI-0.1.0-01", agent: str = "agent-a") -> None:
    write_lock(
        root,
        LockData(
            obpi_id=obpi_id,
            agent=agent,
            pid=1,
            session_id="s",
            claimed_at=(datetime.now(UTC) - timedelta(days=3)).isoformat(),
            branch="main",
            ttl_minutes=60,
        ),
    )


def _config() -> MagicMock:
    config = MagicMock()
    config.paths.ledger = ".gzkit/ledger.jsonl"
    config.paths.adrs = "docs/design/adr"
    return config


def _run(module: str, func, root: Path, **kwargs) -> tuple[str, int]:
    out = io.StringIO()
    code = 0
    with (
        patch(f"gzkit.commands.{module}.ensure_initialized", return_value=_config()),
        patch(f"gzkit.commands.{module}.get_project_root", return_value=root),
        patch(f"gzkit.commands.{module}.console", Console(file=out, width=300)),
        redirect_stdout(out),
    ):
        try:
            func(**kwargs)
        except SystemExit as exc:
            code = int(exc.code or 0)
    return out.getvalue(), code


def _events(root: Path, event_type: str) -> list[dict]:
    text = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
    rows = [json.loads(line) for line in text.splitlines() if line.strip()]
    return [row for row in rows if row.get("event") == event_type]


class TestTheLockVerbsSayTheLeaseExpired(unittest.TestCase):
    def test_a_refused_claim_names_the_release_on_the_operators_word(self) -> None:
        from gzkit.commands.obpi_lock import obpi_lock_claim_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root)
            text, code = _run(
                "obpi_lock",
                obpi_lock_claim_cmd,
                root,
                obpi_id="OBPI-0.1.0-01",
                ttl_minutes=60,
                as_json=False,
                agent="agent-b",
            )
        self.assertEqual(code, 1)
        self.assertIn("--force --abandon", text)
        self.assertIn("on the operator's word", text)

    def test_check_marks_an_expired_lock(self) -> None:
        from gzkit.commands.obpi_lock import obpi_lock_check_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root)
            text, code = _run(
                "obpi_lock", obpi_lock_check_cmd, root, obpi_id="OBPI-0.1.0-01", as_json=False
            )
        self.assertEqual(code, 0)
        self.assertIn("lease expired", text)

    def test_list_marks_an_expired_lock(self) -> None:
        from gzkit.commands.obpi_lock import obpi_lock_list_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root)
            text, _ = _run("obpi_lock", obpi_lock_list_cmd, root, adr_id=None, as_json=False)
        self.assertIn("OBPI-0.1.0-01  LEASE EXPIRED", text)
        self.assertIn("ttl=60m", text)


class TestPreflightOverHeldAndCleanableLocks(unittest.TestCase):
    def test_an_unreadable_lock_file_is_an_issue(self) -> None:
        from gzkit.commands.preflight import preflight_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            locks = root / ".gzkit" / "locks" / "obpi"
            locks.mkdir(parents=True)
            (locks / "broken.lock.json").write_text("{not json", encoding="utf-8")
            text, code = _run("preflight", preflight_cmd, root)
        self.assertEqual(code, 1)
        self.assertIn("Expired lock:    broken.lock.json (unreadable", text)

    def test_the_orphan_session_lock_is_listed_as_an_issue(self) -> None:
        from gzkit.commands.preflight import preflight_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root, SESSION_LOCK_KEY)
            text, _ = _run("preflight", preflight_cmd, root)
        self.assertIn(f"Expired lock:    {SESSION_LOCK_KEY}.lock.json", text)

    def test_stale_markers_and_orphan_receipts_are_listed(self) -> None:
        from gzkit.commands.preflight import preflight_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            plans = root / ".claude" / "plans"
            plans.mkdir(parents=True)
            (plans / ".pipeline-active-OBPI-0.1.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.1.0-01"}), encoding="utf-8"
            )
            (plans / ".plan-audit-receipt-OBPI-0.2.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.2.0-01"}), encoding="utf-8"
            )
            text, _ = _run("preflight", preflight_cmd, root)
        self.assertIn("Stale marker:   .pipeline-active-OBPI-0.1.0-01.json (OBPI-0.1.0-01)", text)
        self.assertIn(
            "Orphan receipt:  .plan-audit-receipt-OBPI-0.2.0-01.json (OBPI-0.2.0-01)", text
        )

    def test_apply_over_held_leases_alone_books_their_expiry(self) -> None:
        from gzkit.commands.preflight import preflight_cmd

        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root)
            _run("preflight", preflight_cmd, root, apply=True)
            self.assertEqual(len(_events(root, "obpi_lock_lease_expired")), 1)


class TestTheReaperBooksOncePerClaim(unittest.TestCase):
    def test_a_second_pass_books_nothing_new(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root)
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            reap_expired_locks(root, ledger=ledger)
            reap_expired_locks(root, ledger=ledger)
            self.assertEqual(len(_events(root, "obpi_lock_lease_expired")), 1)

    def test_the_booked_expiry_replays_in_the_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _root(tmp)
            _expired(root)
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            reap_expired_locks(root, ledger=ledger)
            fidelity = project_corpus(ledger).fidelity
        self.assertTrue(fidelity.complete, fidelity)


if __name__ == "__main__":
    unittest.main()
