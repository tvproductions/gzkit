"""Tests for tracked-defect state resolution in the OBPI status view (GHI #966).

A ``## Tracked Defects`` bullet is a dated record: the ``(open)``/``(closed)``
token an author wrote is true on the day it was written and nothing in the
brief re-resolves it. The status view is a Layer-3 derived view
(``docs/governance/state-doctrine.md``) and must never read that authored
token as the defect's truth. It resolves live state through the
``ReferenceChecker`` port, and where it cannot resolve, it says so —
``unresolved`` is never rendered as live, and never rendered bare.
"""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.status_obpi import _adr_obpi_status_rows
from gzkit.commands.status_obpi_inspect import (
    _extract_tracked_defects,
    _issue_details,
    _resolve_tracked_defects,
    _tracked_defect_refs,
    prefetch_tracked_defects,
)
from gzkit.config import GzkitConfig
from gzkit.handoff_api import ReferenceKind, ReferenceState, StepReference
from gzkit.ledger import Ledger
from tests.commands.common import CliRunner, _quick_init, _write_obpi


def _brief(*bullets: str) -> str:
    return "## Tracked Defects\n\n" + "\n".join(f"- {b}" for b in bullets) + "\n\n## Next\n"


def _checker(states: dict[str, ReferenceState]):
    """A port-shaped stub answering from a number→state table, UNKNOWN elsewhere."""

    def check(reference: StepReference) -> ReferenceState:
        return states.get(reference.identifier, ReferenceState.UNKNOWN)

    return check


class TestTrackedDefectExtraction(unittest.TestCase):
    """Parsing keeps the authored token as *authored*, never as the verdict."""

    def test_authored_token_is_recorded_separately_from_state(self) -> None:
        defects = _extract_tracked_defects(_brief("GHI-11 (closed): stale by now"))
        self.assertEqual(defects[0]["authored_state"], "closed")
        self.assertEqual(defects[0]["state"], "unresolved")

    def test_missing_token_authors_nothing(self) -> None:
        defects = _extract_tracked_defects(_brief("GHI #737 — folded into this ADR"))
        self.assertEqual(defects[0]["id"], "GHI-737")
        self.assertIsNone(defects[0]["authored_state"])
        self.assertEqual(defects[0]["state"], "unresolved")


class TestTrackedDefectResolution(unittest.TestCase):
    """Live state comes from the port; the authored token is compared, not trusted."""

    def test_closed_issue_with_no_token_resolves_closed(self) -> None:
        # The GHI #737 reproduction: authored 2026-08-02, closed 2026-08-03,
        # and the brief line carries no token at all.
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI #737 — folded into this ADR")),
            _checker({"737": ReferenceState.SETTLED}),
        )
        self.assertEqual(defects[0]["state"], "closed")
        self.assertEqual(_tracked_defect_refs(defects), "GHI-737 (closed)")

    def test_stale_open_token_on_a_closed_issue_renders_live_state_and_names_drift(
        self,
    ) -> None:
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI-11 (open): moved on since")),
            _checker({"11": ReferenceState.SETTLED}),
        )
        self.assertEqual(defects[0]["state"], "closed")
        self.assertEqual(defects[0]["authored_state"], "open")
        self.assertEqual(_tracked_defect_refs(defects), "GHI-11 (closed; brief says open)")

    def test_stale_closed_token_on_an_open_issue_renders_live_state_and_names_drift(
        self,
    ) -> None:
        # The other direction: a reopened GHI whose brief line still says closed.
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI-12 (closed): reopened after the fact")),
            _checker({"12": ReferenceState.LIVE}),
        )
        self.assertEqual(defects[0]["state"], "open")
        self.assertEqual(_tracked_defect_refs(defects), "GHI-12 (open; brief says closed)")

    def test_agreeing_token_renders_the_live_state_plainly(self) -> None:
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI-11 (open): still live")),
            _checker({"11": ReferenceState.LIVE}),
        )
        self.assertEqual(_tracked_defect_refs(defects), "GHI-11 (open)")

    def test_unresolvable_reference_renders_unresolved_never_bare(self) -> None:
        # The port's contract: UNKNOWN is first-class and never a synonym for
        # LIVE. A bare ref inside a blockers list reads as live, so the view
        # must say it did not check.
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI #737 — folded into this ADR")),
            _checker({}),
        )
        self.assertEqual(defects[0]["state"], "unresolved")
        self.assertEqual(_tracked_defect_refs(defects), "GHI-737 (unresolved)")

    def test_unresolvable_reference_never_promotes_the_authored_token(self) -> None:
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI-12 (closed): authored, unverified")),
            _checker({}),
        )
        self.assertEqual(defects[0]["state"], "unresolved")
        self.assertEqual(_tracked_defect_refs(defects), "GHI-12 (unresolved; brief says closed)")

    def test_no_checker_leaves_every_reference_unresolved(self) -> None:
        # Hexagonal § Operative rule 6: the core runs without an adapter, and
        # running without one is not the same as having checked.
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI-11 (open): a", "GHI-12 (closed): b")),
            None,
        )
        self.assertEqual([d["state"] for d in defects], ["unresolved", "unresolved"])
        self.assertEqual(
            _tracked_defect_refs(defects),
            "GHI-11 (unresolved; brief says open), GHI-12 (unresolved; brief says closed)",
        )

    def test_checker_is_asked_for_the_ghi_by_number(self) -> None:
        checker = mock.Mock(return_value=ReferenceState.LIVE)
        _resolve_tracked_defects(_extract_tracked_defects(_brief("GHI-966: subject")), checker)
        checker.assert_called_once_with(StepReference(kind=ReferenceKind.GHI, identifier="966"))

    def test_issue_details_carry_the_resolved_annotation(self) -> None:
        defects = _resolve_tracked_defects(
            _extract_tracked_defects(_brief("GHI #737 — folded")),
            _checker({"737": ReferenceState.SETTLED}),
        )
        self.assertEqual(
            _issue_details(["ledger proof of completion is missing"], defects),
            ["ledger proof of completion is missing [tracked defects: GHI-737 (closed)]"],
        )


class _Prefetcher:
    """A batching port fake: records each prefetch and each check, in order."""

    def __init__(self) -> None:
        self.events: list[tuple[str, tuple[str, ...]]] = []

    def prefetch(self, references) -> None:
        self.events.append(("prefetch", tuple(r.identifier for r in references)))

    def __call__(self, reference: StepReference) -> ReferenceState:
        self.events.append(("check", (reference.identifier,)))
        return ReferenceState.SETTLED


class TestTrackedDefectsAreBatchedBeforeTheyAreChecked(unittest.TestCase):
    """GHI #1334: a brief's tracked GHIs reach a batching adapter as one set, first."""

    def test_one_brief_prefetches_its_defects_ahead_of_checking_them(self) -> None:
        # given a brief tracking two GHIs and a checker that batches
        checker = _Prefetcher()
        defects = _extract_tracked_defects(_brief("GHI #11 (open): a", "GHI #12 (open): b"))
        # when they are resolved
        resolved = _resolve_tracked_defects(defects, checker)
        # then one prefetch carried both before either was checked
        self.assertEqual(
            checker.events,
            [("prefetch", ("11", "12")), ("check", ("11",)), ("check", ("12",))],
        )
        self.assertEqual([d["state"] for d in resolved], ["closed", "closed"])

    def test_many_briefs_prefetch_all_their_defects_in_one_set(self) -> None:
        # given two brief files tracking three GHIs between them
        checker = _Prefetcher()
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "a.md"
            first.write_text(_brief("GHI #11 (open): a", "GHI #12 (open): b"), encoding="utf-8")
            second = Path(tmp) / "b.md"
            second.write_text(_brief("GHI #13 (open): c"), encoding="utf-8")
            # when the view prefetches across them
            prefetch_tracked_defects(checker, [first, second])
        # then one prefetch carried all three
        self.assertEqual(checker.events, [("prefetch", ("11", "12", "13"))])


class TestAnAdrsBriefsAreBatchedAsOneSet(unittest.TestCase):
    """GHI #1334: an ADR's status rows hand every brief's tracked GHIs over in one set.

    `gz adr status ADR-0.35.0` read its 20 briefs' 31 tracked GHIs one round trip
    at a time (~21 s); one prefetch across the briefs makes that one batch.
    """

    def test_every_briefs_defects_are_prefetched_before_any_is_checked(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            # given an ADR whose two briefs track three GHIs between them
            _quick_init()
            root = Path.cwd()
            first = root / "OBPI-0.1.0-01-demo.md"
            _write_obpi(
                path=first,
                status="Active",
                brief_status="In Progress",
                implementation_line="src/module.py",
                tracked_defects=["GHI #11 (open): one", "GHI #12 (open): two"],
            )
            second = root / "OBPI-0.1.0-02-other.md"
            _write_obpi(
                path=second,
                status="Active",
                brief_status="In Progress",
                implementation_line="src/other.py",
                tracked_defects=["GHI #13 (open): three"],
            )
            index = [
                ("OBPI-0.1.0-01-demo", "ADR-0.1.0-f", first),
                ("OBPI-0.1.0-02-other", "ADR-0.1.0-f", second),
            ]
            checker = _Prefetcher()
            # when the ADR's status rows are built
            rows = _adr_obpi_status_rows(
                root,
                GzkitConfig.load(root / ".gzkit.json"),
                Ledger(root / ".gzkit" / "ledger.jsonl"),
                "ADR-0.1.0-f",
                obpi_index=index,
                reference_checker=checker,
            )
        # then the first event is one prefetch carrying all three
        self.assertEqual(checker.events[0][0], "prefetch")
        self.assertEqual(sorted(checker.events[0][1]), ["11", "12", "13"])
        self.assertEqual(sum(1 for d in rows for _ in d["tracked_defects"]), 3)


if __name__ == "__main__":
    unittest.main()
