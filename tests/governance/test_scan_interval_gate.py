"""Wall-clock currency gate for chores whose staleness is externally driven.

``check_proof_freshness.py`` judges a proof stale when an audited surface has a
newer last-commit date. That technique cannot express
``frontier-model-card-currency``: no repo file's commit date moves when
Anthropic or OpenAI publishes a system card, so the registry stays internally
valid — and the chore reports ``All criteria pass`` — for as long as nobody
looks. Measured 2026-09-02 under GHI #935: both criteria passed while the
Mythos-class ``current`` entry had been superseded since 2026-09-01 (GHI #934).

The variable such a chore depends on is elapsed time, so the gate reads a
clock. What it reads the clock *against* is the load-bearing choice:
``CHORE-LOG.md`` carries both hand-authored narrative headings (``## 2026-09-02
— findings``) and the timestamped blocks ``gz chores run`` appends
(``## 2026-09-02T02:11:01-04:00``). Only the latter witnesses that the governed
procedure actually ran. Keying on narrative headings would rebuild exactly the
gate ``AGENTS.md`` forbids — one whose witness is that somebody wrote
something, not that anything ran.

The interval is the chore's declared ``staleness.periodDays`` (GHI #999), so
the gate tests inject a registry with a fixture period rather than transcribing
the live one. Only the *semantics* are pinned.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any
from unittest.mock import patch


def _load_freshness_gate() -> Any:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "check_proof_freshness.py"
    spec = importlib.util.spec_from_file_location("check_proof_freshness", script)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_proof_freshness"] = module
    spec.loader.exec_module(module)
    return module


_GATE = _load_freshness_gate()
_SLUG = "frontier-model-card-currency"


class ScanIntervalRegistrationTests(unittest.TestCase):
    """The externally-driven chore must declare an interval."""

    def test_frontier_chore_declares_a_scan_interval(self) -> None:
        """The declaration is the whole gate — a chore declaring no period is ungated."""
        period = _GATE._declared_period(_SLUG)
        self.assertIsNotNone(period)

    def test_interval_chores_are_not_also_surface_gated(self) -> None:
        """The two arms answer different questions; a slug picks one.

        A chore declaring elapsed-time takes the interval arm, so a surface entry
        for it would be dead code describing a gate that never runs.
        """
        overlap = {s for s in _GATE._AUDITED_SURFACES if _GATE._declared_period(s) is not None}
        self.assertEqual(overlap, set())


class NewestScanTimestampTests(unittest.TestCase):
    """Which heading counts as evidence the procedure ran."""

    def test_narrative_heading_never_resets_the_clock(self) -> None:
        """A hand-written date is authorship, not a run receipt.

        This is the defect the gate exists to avoid re-introducing: if prose
        headings counted, appending a findings section would mark the chore
        fresh without any scan having happened.
        """
        log = (
            "## 2026-09-02 — findings written by hand\n\n"
            "## 2026-08-02T10:59:02-06:00\n- Status: PASS\n"
        )
        newest = _GATE._newest_scan_timestamp(log)
        assert newest is not None
        self.assertEqual(newest.date().isoformat(), "2026-08-02")

    def test_newest_mechanical_stamp_wins_regardless_of_file_order(self) -> None:
        """Blocks are appended, but order in the file is not the authority."""
        log = (
            "## 2026-09-01T00:00:00+00:00\n- Status: PASS\n\n"
            "## 2026-06-01T00:00:00+00:00\n- Status: PASS\n"
        )
        newest = _GATE._newest_scan_timestamp(log)
        assert newest is not None
        self.assertEqual(newest.date().isoformat(), "2026-09-01")

    def test_log_with_no_mechanical_stamp_reads_as_never_run(self) -> None:
        """Narrative-only log means no governed run is on record."""
        self.assertIsNone(_GATE._newest_scan_timestamp("## 2026-09-02 — prose only\n"))

    def test_a_failed_run_never_resets_the_clock(self) -> None:
        """A FAIL block records that the verb ran, not that the audit was done.

        ``gz chores run`` stamps FAIL runs exactly like PASS runs. Counting them let
        an overdue chore clear its own staleness by running twice: the first run
        fails the gate and writes a stamp, the second passes on that stamp.
        """
        log = (
            "## 2026-08-01T00:00:00+00:00\n- Status: PASS\n\n"
            "## 2026-09-01T00:00:00+00:00\n- Status: FAIL\n"
        )
        newest = _GATE._newest_scan_timestamp(log)
        assert newest is not None
        self.assertEqual(newest.date().isoformat(), "2026-08-01")


_PERIOD = 10


class ScanIntervalGateTests(unittest.TestCase):
    """Exit-code contract: 0 fresh, 3 policy breach, 1 no gate for the slug."""

    def _run_against(
        self, log_body: str | None, *, period: int = _PERIOD, signal: str = "elapsed-time"
    ) -> int:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            proofs = root / ".gzkit" / "chores" / _SLUG / "proofs"
            proofs.mkdir(parents=True)
            staleness = {"signal": signal, "periodDays": period, "graceDays": 7}
            registry = {"chores": [{"slug": _SLUG, "staleness": staleness}]}
            (root / ".gzkit" / "chores" / "registry.json").write_text(
                json.dumps(registry), encoding="utf-8"
            )
            if log_body is not None:
                (proofs / "CHORE-LOG.md").write_text(log_body, encoding="utf-8")
            with patch.object(_GATE, "_PROJECT_ROOT", root):
                return _GATE.main([_SLUG])

    def _stamp(self, days_ago: int) -> str:
        when = datetime.now(UTC) - timedelta(days=days_ago)
        return f"## {when.isoformat()}\n- Status: PASS\n"

    def test_scan_within_interval_passes(self) -> None:
        self.assertEqual(self._run_against(self._stamp(1)), 0)

    def test_scan_older_than_interval_is_a_policy_breach(self) -> None:
        self.assertEqual(self._run_against(self._stamp(_PERIOD + 1)), 3)

    def test_the_declared_period_is_the_limit(self) -> None:
        """The same run is overdue under one declaration and current under a longer one."""
        stamp = self._stamp(_PERIOD + 1)
        self.assertEqual(self._run_against(stamp, period=_PERIOD), 3)
        self.assertEqual(self._run_against(stamp, period=_PERIOD * 2), 0)

    def test_a_chore_declaring_no_elapsed_time_has_no_interval_gate(self) -> None:
        """Without the declaration the slug is neither interval- nor surface-gated."""
        self.assertEqual(self._run_against(self._stamp(1), signal="content-delta"), 1)

    def test_narrative_heading_cannot_rescue_an_overdue_scan(self) -> None:
        """The semantic in NewestScanTimestampTests, enforced at the exit code."""
        today = datetime.now(UTC).date().isoformat()
        log = f"## {today} — findings appended by hand\n\n{self._stamp(_PERIOD + 1)}"
        self.assertEqual(self._run_against(log), 3)

    def test_a_newer_failed_run_cannot_rescue_an_overdue_scan(self) -> None:
        """The run-twice bypass, enforced at the exit code."""
        failed = (datetime.now(UTC) - timedelta(days=1)).isoformat()
        log = f"{self._stamp(_PERIOD + 1)}\n## {failed}\n- Status: FAIL\n"
        self.assertEqual(self._run_against(log), 3)

    def test_missing_log_fails_closed(self) -> None:
        """No record of a run is not evidence of a recent run."""
        self.assertEqual(self._run_against(None), 3)


if __name__ == "__main__":
    unittest.main()
