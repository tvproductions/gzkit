"""Tests for the airlock-OUT primitive (OBPI-0.33.0-03).

Assertions derive from the brief's Acceptance Criteria
(REQ-0.33.0-03-01 through REQ-0.33.0-03-05), NOT from a run of the
implementation. The primitive is exercised with an injected fake ``reach_fn``
so the core runs with NO ontology projection built (hexagonal rule 6).

airlock-OUT is co-equal with airlock-IN ("same shape both ways"): where IN
gates entry, OUT accounts for what a completed transit disturbed — a drift-diff
push-minus-pull over the two-graph (FACT/OBSERVED reach edges vs INTENT/LAW
invariant edges), findings + recommendations behind the CLOSED ExitDecision
menu, fresh-transit routing (never smuggled), one airlock_out L2 event, and
never a write to L1 canon.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.airlock.exit import (
    EXIT_DECISION_MENU,
    Door,
    ExitDecision,
    FindingKind,
    airlock_exit,
    build_findings,
    compute_drift_diff,
)
from gzkit.airlock.model import Provenance, SeamKind, Verdict
from gzkit.ledger import Ledger
from gzkit.traceability import covers

_BRIEF = """# Brief

## Allowed Paths

- `src/gzkit/airlock/exit.py`
- `tests/test_airlock_exit.py`

The exit accounts for the declared footprint on the way out.
"""


class _AirlockExitCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self._brief_seq = 0

    def _brief(self, text: str = _BRIEF) -> Path:
        self._brief_seq += 1
        path = self.tmp / f"brief-{self._brief_seq}.md"
        path.write_text(text, encoding="utf-8")
        return path

    def _ledger(self) -> Ledger:
        return Ledger(self.tmp / "ledger.jsonl")


class TestDriftDiff(_AirlockExitCase):
    @covers("REQ-0.33.0-03-01")
    def test_push_minus_pull_classifies_wrecked_and_broken(self) -> None:
        # One un-matched FACT edge (OBSERVED, no matching intent) and one
        # un-matched INTENT edge (LAW, no matching fact); "MATCH" is in both.
        drift = compute_drift_diff(
            fact_targets=("FACT-A", "MATCH"), intent_targets=("INT-B", "MATCH")
        )

        wrecked = [e for e in drift.drift if e.kind is SeamKind.PUSH]
        broken = [e for e in drift.drift if e.kind is SeamKind.PULL]
        self.assertEqual(
            [e.target for e in wrecked],
            ["FACT-A"],
            "a FACT edge (OBSERVED) with no matching INTENT edge is a wrecked-something drift",
        )
        self.assertIs(wrecked[0].provenance, Provenance.OBSERVED)
        self.assertEqual(
            [e.target for e in broken],
            ["INT-B"],
            "an INTENT edge (LAW) with no matching FACT edge is a broken-contract drift",
        )
        self.assertIs(broken[0].provenance, Provenance.LAW)
        self.assertIs(
            drift.verdict, Verdict.SURFACE, "drift present -> SURFACE, never silently clean"
        )

        findings = build_findings(drift)
        by_target = {f.edge.target: f.kind for f in findings}
        self.assertEqual(by_target["FACT-A"], FindingKind.WRECKED_SOMETHING)
        self.assertEqual(by_target["INT-B"], FindingKind.BROKEN_CONTRACT)

    @covers("REQ-0.33.0-03-01")
    def test_fully_matched_two_graph_yields_empty_drift(self) -> None:
        drift = compute_drift_diff(fact_targets=("MATCH",), intent_targets=("MATCH",))
        self.assertEqual(drift.drift, (), "a fully-matched two-graph has no drift")
        self.assertIs(drift.verdict, Verdict.CLEAN)
        self.assertEqual(build_findings(drift), ())


class TestClosedMenu(_AirlockExitCase):
    @covers("REQ-0.33.0-03-02")
    def test_decision_menu_is_closed_set_of_exactly_four(self) -> None:
        self.assertEqual(
            {m.value for m in ExitDecision},
            {"leave_it_be", "modify", "repair", "adjust_maps"},
            "the ExitDecision menu is a CLOSED enum of exactly four members "
            "(a fifth or renamed member is a fail-closed drift)",
        )
        self.assertEqual(
            tuple(EXIT_DECISION_MENU),
            (
                ExitDecision.LEAVE_IT_BE,
                ExitDecision.MODIFY,
                ExitDecision.REPAIR,
                ExitDecision.ADJUST_MAPS,
            ),
        )

    @covers("REQ-0.33.0-03-02")
    def test_every_finding_carries_non_empty_recommendation(self) -> None:
        drift = compute_drift_diff(fact_targets=("FACT-A",), intent_targets=("INT-B",))
        findings = build_findings(drift)
        self.assertTrue(findings, "drift must surface findings")
        for finding in findings:
            self.assertTrue(
                finding.recommendation.strip(),
                "every emitted finding carries a non-empty recommendation",
            )


class TestFreshTransitRouting(_AirlockExitCase):
    @covers("REQ-0.33.0-03-03")
    def test_discovered_correction_routes_fresh_never_smuggled(self) -> None:
        brief = self._brief()
        sentinel = self.tmp / "discovered_surface.txt"
        sentinel.write_text("ORIGINAL", encoding="utf-8")
        before = sentinel.read_text(encoding="utf-8")

        report = airlock_exit(
            "OBPI-X",
            brief,
            parent_invariants=("INV-DELIVERED",),
            reach_fn=lambda _n: ["DEP-WRECKED"],
        )

        self.assertTrue(report.routing, "a discovered correction yields a fresh-transit directive")
        directive = report.routing[0]
        self.assertIn(directive.door, set(Door), "the directive names a real door")
        self.assertFalse(
            directive.smuggled,
            "the correction routes as a FRESH transit, never smuggled into the current sortie",
        )
        self.assertEqual(
            sentinel.read_text(encoding="utf-8"),
            before,
            "airlock-OUT performs ZERO in-sortie mutation of the discovered surface",
        )


class TestAlwaysLogsL2(_AirlockExitCase):
    @covers("REQ-0.33.0-03-04")
    def test_airlock_exit_books_exactly_one_airlock_out_event(self) -> None:
        brief = self._brief()
        ledger = self._ledger()
        airlock_exit("OBPI-X", brief, reach_fn=lambda _n: ["DEP-WRECKED"], ledger=ledger)
        out_events = [e for e in ledger.read_all() if e.event == "airlock_out"]
        self.assertEqual(
            len(out_events),
            1,
            "every airlock-OUT transit emits exactly one airlock_out event "
            "(a computed drift-diff with no event is a fail-closed silent exit)",
        )

    @covers("REQ-0.33.0-03-04")
    def test_stage5_gate_reaches_primitive_and_books_l2(self) -> None:
        from gzkit.pipeline_runtime import check_airlock_out_gate

        project_root = self.tmp
        (project_root / ".gzkit").mkdir(exist_ok=True)
        brief = self._brief()
        check_airlock_out_gate("OBPI-X", brief, project_root, reach_fn=lambda _n: ["DEP-WRECKED"])
        ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
        out_events = [e for e in ledger.read_all() if e.event == "airlock_out"]
        self.assertEqual(
            len(out_events),
            1,
            "the Stage-5 exit seam reaches airlock_exit and books airlock_out to L2",
        )

    @covers("REQ-0.33.0-03-04")
    def test_stage5_executor_exit_membrane_books_airlock_out(self) -> None:
        # Drive the ACTUAL Stage-5 executor seam (_run_airlock_out_diagnostic,
        # called by _run_pipeline_sync_stage) — not a hasattr import blessing — and
        # prove it REACHES airlock_exit and books exactly one airlock_out event. If
        # the call block were deleted from the executor this test fails, closing the
        # orphan-blessing surface (Step-4b adversary Weakest Point, 2026-07-11).
        from gzkit.commands.obpi_stages import _run_airlock_out_diagnostic

        project_root = self.tmp
        (project_root / ".gzkit").mkdir(exist_ok=True)
        brief_dir = project_root / "docs" / "design" / "adr" / "obpis"
        brief_dir.mkdir(parents=True)
        (brief_dir / "OBPI-X-airlock.md").write_text(_BRIEF, encoding="utf-8")

        _run_airlock_out_diagnostic(project_root, "OBPI-X", reach_fn=lambda _n: ["DEP-WRECKED"])

        ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
        out_events = [e for e in ledger.read_all() if e.event == "airlock_out"]
        self.assertEqual(
            len(out_events),
            1,
            "the Stage-5 executor exit membrane reaches check_airlock_out_gate -> "
            "airlock_exit and books exactly one airlock_out event via the stage path",
        )


class TestNeverWritesL1(_AirlockExitCase):
    @covers("REQ-0.33.0-03-05")
    def test_canon_amendment_is_proposed_never_written(self) -> None:
        brief = self._brief()
        canon = self.tmp / "ADR-canon.md"
        canon.write_text("# Canon\n\nInvariant text.\n", encoding="utf-8")
        before = canon.read_text(encoding="utf-8")

        # An INTENT edge with no backing FACT surfaces a broken-contract finding,
        # for which the primitive PROPOSES a map/canon amendment.
        report = airlock_exit(
            "OBPI-X",
            brief,
            parent_invariants=("INV-UNDELIVERED",),
            reach_fn=lambda _n: [],
        )

        self.assertTrue(
            report.proposals,
            "a surfaced canon-relevant drift yields a LawProposal (a proposal object, not a write)",
        )
        self.assertEqual(
            canon.read_text(encoding="utf-8"),
            before,
            "airlock-OUT NEVER writes L1 canon — it returns proposals, never mutating a canon file",
        )


if __name__ == "__main__":
    unittest.main()
