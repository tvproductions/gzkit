"""Wall-clock currency gate for chores whose staleness is externally driven.

``check_proof_freshness.py`` judges a proof stale when an audited surface has a
newer last-commit date. That technique cannot express
``frontier-model-card-currency``: no repo file's commit date moves when
Anthropic or OpenAI publishes a system card, so the registry stays internally
valid — and the chore reports ``All criteria pass`` — for as long as nobody
looks. Measured 2026-09-02 under GHI #935: both criteria passed while the
Mythos-class ``current`` entry had been superseded since 2026-09-01 (GHI #934).

The variable such a chore depends on is elapsed time, so the gate reads a
clock. What it reads the clock *against* is the load-bearing choice, and the
first answer was wrong. Reading the PASS blocks ``gz chores run`` appends was
circular: the gate is a criterion of that run and a PASS block is written only
when every criterion passes, so once a chore went overdue no run could ever
clear it (GHI #935, reopened 2026-09-14). It was also bypassable: a bare run
inside the period wrote a fresh PASS block and extended the clock with no scan.

The witness is the chore's declared ``staleness.artifacts`` — the record its
procedure writes — never ``CHORE-LOG.md``, whose narrative headings are
authorship and whose run blocks are written by the gated run itself. Operator
ruling 2026-09-14, verbatim *"Declare it (Recommended)"*.

The interval is the chore's declared ``staleness.periodDays`` (GHI #999), so
the gate tests inject a registry with a fixture period rather than transcribing
the live one. Only the *semantics* are pinned.
"""

from __future__ import annotations

import importlib.util
import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
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

        A chore declaring elapsed-time takes the interval arm, so surfaces on it
        would describe a gate that never runs — the arm reads them only for
        content-delta, whatever the registry carries.
        """
        staleness = {"signal": "elapsed-time", "periodDays": 30, "surfaces": ["src"]}
        with patch.object(_GATE, "_declared_staleness", return_value=staleness):
            self.assertIsNone(_GATE._declared_surfaces(_SLUG))
            self.assertEqual(_GATE._declared_period(_SLUG), 30)


_PERIOD = 10
_ARTIFACT = f".gzkit/chores/{_SLUG}/proofs/scan-record.md"


class _GateFixture(unittest.TestCase):
    """Runs the gate against a fixture chore whose scan-artifact history is injected."""

    def _run_against(
        self,
        artifact_days_ago: int | None,
        *,
        log: str = "",
        period: int = _PERIOD,
        signal: str = "elapsed-time",
        artifacts: list[str] | None = None,
    ) -> int:
        """Return the gate's exit code.

        *artifact_days_ago* is when the declared scan artifact last changed (None:
        never). *log* is the ``CHORE-LOG.md`` body — the record the gate must never
        read, so every case that sets it asserts the verdict ignores it.
        """
        declared = [_ARTIFACT] if artifacts is None else artifacts
        changed = None
        if artifact_days_ago is not None:
            changed = datetime.now(UTC) - timedelta(days=artifact_days_ago)
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            proofs = root / ".gzkit" / "chores" / _SLUG / "proofs"
            proofs.mkdir(parents=True)
            staleness: dict[str, object] = {"signal": signal, "periodDays": period, "graceDays": 7}
            if declared:
                staleness["artifacts"] = declared
            registry = {"chores": [{"slug": _SLUG, "staleness": staleness}]}
            (root / ".gzkit" / "chores" / "registry.json").write_text(
                json.dumps(registry), encoding="utf-8"
            )
            if log:
                (proofs / "CHORE-LOG.md").write_text(log, encoding="utf-8")

            def reader(project_root: Path, _now: datetime) -> Any:
                self.assertEqual(project_root, root)
                return lambda paths: changed if list(paths) == declared else None

            with (
                patch.object(_GATE, "_PROJECT_ROOT", root),
                patch.object(_GATE, "git_artifact_changed", side_effect=reader),
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                return _GATE.main([_SLUG])


def _block(days_ago: int, status: str) -> str:
    when = datetime.now(UTC) - timedelta(days=days_ago)
    return f"## {when.isoformat()}\n- Status: {status}\n\n"


class ScanIntervalGateTests(_GateFixture):
    """Exit-code contract: 0 fresh, 3 policy breach, 1 no gate for the slug."""

    def test_scan_within_interval_passes(self) -> None:
        self.assertEqual(self._run_against(1), 0)

    def test_scan_older_than_interval_is_a_policy_breach(self) -> None:
        self.assertEqual(self._run_against(_PERIOD + 1), 3)

    def test_the_declared_period_is_the_limit(self) -> None:
        """The same scan is overdue under one declaration and current under a longer one."""
        self.assertEqual(self._run_against(_PERIOD + 1, period=_PERIOD), 3)
        self.assertEqual(self._run_against(_PERIOD + 1, period=_PERIOD * 2), 0)

    def test_a_chore_declaring_no_elapsed_time_has_no_interval_gate(self) -> None:
        """Without the declaration the slug is neither interval- nor surface-gated."""
        self.assertEqual(self._run_against(1, signal="content-delta"), 1)

    def test_no_scan_artifact_on_record_fails_closed(self) -> None:
        """A declared artifact that never changed is not evidence of a recent scan."""
        self.assertEqual(self._run_against(None), 3)

    def test_an_elapsed_time_chore_declaring_no_artifact_is_refused(self) -> None:
        """With no declared artifact the only record left is the run's own PASS block.

        That record is circular — reading it is the deadlock this gate had — so the
        slug is refused as a declaration error rather than read.
        """
        self.assertEqual(self._run_against(1, artifacts=[]), 1)


class OverdueChoreRecoveryTests(_GateFixture):
    """GHI #935 reopened: an overdue chore returns to passing only by doing its scan.

    Each case puts the run log in a state that used to decide the verdict and
    shows the verdict now follows the scan artifact alone.
    """

    def test_a_performed_scan_clears_a_chore_whose_last_pass_is_overdue(self) -> None:
        """The deadlock: the newest PASS block is past its period, yet the scan is done."""
        self.assertEqual(self._run_against(0, log=_block(_PERIOD + 26, "PASS")), 0)

    def test_a_bare_rerun_after_a_failed_run_stays_blocked(self) -> None:
        """A FAIL block records that the verb ran, never that the scan was done."""
        log = _block(_PERIOD + 26, "PASS") + _block(0, "FAIL")
        self.assertEqual(self._run_against(_PERIOD + 26, log=log), 3)

    def test_a_fresh_pass_block_without_a_scan_cannot_extend_the_clock(self) -> None:
        """The in-period bypass: a bare run's PASS block is not a scan."""
        self.assertEqual(self._run_against(_PERIOD + 1, log=_block(0, "PASS")), 3)

    def test_a_hand_written_heading_resets_nothing(self) -> None:
        """A narrative heading dated today is authorship, not a scan."""
        today = datetime.now(UTC).date().isoformat()
        log = f"## {today} — findings appended by hand\n\n"
        self.assertEqual(self._run_against(_PERIOD + 1, log=log), 3)


class DeclaredSurfaceArmTests(unittest.TestCase):
    """The proof arm reads the chore's declared surfaces, never a map of its own (GHI #936).

    ``gz chores status`` and this gate must judge a content-delta chore against the
    same inputs; two surface authorities is how one reports a chore fresh while the
    other reports it stale.
    """

    _PROOF = ".gzkit/chores/demo-coherence/proofs/report.md"

    def _run(self, surfaces: list[str] | None, epochs: dict[str, int]) -> int:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            proofs = root / ".gzkit" / "chores" / "demo-coherence" / "proofs"
            proofs.mkdir(parents=True)
            (proofs / "report.md").write_text("findings\n", encoding="utf-8")
            staleness: dict[str, object] = {"signal": "content-delta", "graceDays": 7}
            if surfaces is not None:
                staleness["surfaces"] = surfaces
            registry = {"chores": [{"slug": "demo-coherence", "staleness": staleness}]}
            (root / ".gzkit" / "chores" / "registry.json").write_text(
                json.dumps(registry), encoding="utf-8"
            )
            with (
                patch.object(_GATE, "_PROJECT_ROOT", root),
                patch.object(_GATE, "_last_commit_epoch", side_effect=epochs.get),
            ):
                return _GATE.main(["demo-coherence"])

    def test_proof_older_than_a_declared_surface_is_a_breach(self) -> None:
        self.assertEqual(self._run(["watched"], {"watched": 200, self._PROOF: 100}), 3)

    def test_proof_newer_than_every_declared_surface_passes(self) -> None:
        self.assertEqual(self._run(["watched"], {"watched": 100, self._PROOF: 200}), 0)

    def test_an_undeclared_surface_never_makes_the_proof_stale(self) -> None:
        """Only declared inputs count: movement elsewhere is not this chore's staleness."""
        self.assertEqual(
            self._run(["watched"], {"watched": 100, "elsewhere": 900, self._PROOF: 200}), 0
        )

    def test_content_delta_chore_declaring_no_surfaces_has_no_gate(self) -> None:
        self.assertEqual(self._run(None, {self._PROOF: 200}), 1)


if __name__ == "__main__":
    unittest.main()
