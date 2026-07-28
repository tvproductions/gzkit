"""Drift's unlinked-spec set is scoped to the @covers proof channel (GHI #729).

`gz drift` reported every REQ lacking a `@covers` test as drift, including the
two kinds whose proof channel is definitionally NOT a test (SUPPORT,
STRUCTURAL-FENCE per ADR-0.0.59), REQs marked non-testable by the legacy
`ReqKind.DOC` axis, and REQs in sealed briefs. Both kind axes were already
parsed onto `ReqEntity` and then discarded by `_project_source_subgraph`.

These tests pin the scoping rule, not the current numbers: a REQ enters the
unlinked set only when a covering test is the thing that would prove it.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.triangle import (
    EdgeType,
    LinkageRecord,
    ReqEntity,
    ReqId,
    ReqKind,
    ReqStatus,
    VertexRef,
    VertexType,
    covers_channel_reqs,
    detect_drift,
)


def _req(
    criterion: str,
    *,
    taxonomy_kind: str | None = None,
    kind: ReqKind = ReqKind.CODE,
) -> ReqEntity:
    """Build a REQ entity under OBPI-0.1.0-01 with the given kind axes."""
    return ReqEntity(
        id=ReqId(semver="0.1.0", obpi_item="01", criterion_index=criterion),
        parent_obpi="OBPI-0.1.0-01",
        description="a requirement",
        status=ReqStatus.UNCHECKED,
        kind=kind,
        taxonomy_kind=taxonomy_kind,
    )


def _with_status(entity: ReqEntity, *, brief_status: str | None = "Draft") -> ReqEntity:
    """Restamp a REQ with its owning brief's lifecycle status."""
    return entity.model_copy(update={"brief_status": brief_status})


class TestCoversChannelScoping(unittest.TestCase):
    """Only REQs whose proof channel is a `@covers` test are drift-eligible."""

    def _ids(self, reqs: list[ReqEntity]) -> set[str]:
        return {str(r.id) for r in covers_channel_reqs(reqs)}

    def test_support_reqs_are_not_covers_channel(self) -> None:
        """SUPPORT proves via ledger event + structural validator, never a test."""
        rows = [
            _with_status(_req("01", taxonomy_kind="BEHAVIOR")),
            _with_status(_req("02", taxonomy_kind="SUPPORT")),
        ]
        self.assertEqual(self._ids(rows), {"REQ-0.1.0-01-01"})

    def test_structural_fence_reqs_are_not_covers_channel(self) -> None:
        """STRUCTURAL-FENCE proves via the parent ADR's Boundary Invariants."""
        rows = [
            _with_status(_req("01", taxonomy_kind="BEHAVIOR")),
            _with_status(_req("02", taxonomy_kind="STRUCTURAL-FENCE")),
        ]
        self.assertEqual(self._ids(rows), {"REQ-0.1.0-01-01"})

    def test_untagged_reqs_stay_in_scope(self) -> None:
        """A REQ predating ADR-0.0.59 carries no kind; absence is not exemption."""
        rows = [_with_status(_req("01", taxonomy_kind=None))]
        self.assertEqual(self._ids(rows), {"REQ-0.1.0-01-01"})

    def test_taxonomy_kind_match_is_case_insensitive(self) -> None:
        """Briefs author `[support]` and `[SUPPORT]`; both name one kind."""
        rows = [_with_status(_req("01", taxonomy_kind="support"))]
        self.assertEqual(self._ids(rows), set())

    def test_doc_kind_reqs_are_not_covers_channel(self) -> None:
        """`ReqKind.DOC` means non-testable — its own field docstring says so."""
        rows = [
            _with_status(_req("01", kind=ReqKind.CODE)),
            _with_status(_req("02", kind=ReqKind.DOC)),
        ]
        self.assertEqual(self._ids(rows), {"REQ-0.1.0-01-01"})


class TestTerminalBriefScoping(unittest.TestCase):
    """A sealed brief owes no new coverage."""

    def _ids(self, reqs: list[ReqEntity]) -> set[str]:
        return {str(r.id) for r in covers_channel_reqs(reqs)}

    def test_withdrawn_brief_reqs_are_out_of_scope(self) -> None:
        rows = [_with_status(_req("01"), brief_status="Withdrawn")]
        self.assertEqual(self._ids(rows), set())

    def test_abandoned_brief_reqs_are_out_of_scope(self) -> None:
        rows = [_with_status(_req("01"), brief_status="Abandoned")]
        self.assertEqual(self._ids(rows), set())

    def test_terminal_status_match_tolerates_corpus_spelling(self) -> None:
        """The corpus carries both `Withdrawn` and `withdrawn`."""
        rows = [_with_status(_req("01"), brief_status="withdrawn")]
        self.assertEqual(self._ids(rows), set())

    def test_completed_brief_reqs_stay_in_scope(self) -> None:
        """Completed is sealed but NOT retired — it owes its attested coverage.

        Excluding it would blind drift to the regression it most needs to
        catch: a covering test deleted after the brief was attested.
        """
        rows = [
            _with_status(_req("01"), brief_status="Draft"),
            _with_status(_req("02"), brief_status="Completed"),
            _with_status(_req("03"), brief_status="attested_completed"),
            _with_status(_req("04"), brief_status="Validated"),
        ]
        self.assertEqual(
            self._ids(rows),
            {"REQ-0.1.0-01-01", "REQ-0.1.0-01-02", "REQ-0.1.0-01-03", "REQ-0.1.0-01-04"},
        )

    def test_retired_statuses_are_a_subset_of_the_terminal_vocabulary(self) -> None:
        """Pin the local set against its upstream authority.

        `_RETIRED_BRIEF_STATUSES` restates four members of
        `BRIEF_TERMINAL_STATUSES` rather than composing from it, because a new
        terminal status must default to IN scope, not silently exempt itself.
        Restating earns this guard: rename one upstream and this fails.
        """
        from gzkit.governance.brief_structure import BRIEF_TERMINAL_STATUSES
        from gzkit.triangle import _RETIRED_BRIEF_STATUSES

        self.assertTrue(
            _RETIRED_BRIEF_STATUSES <= BRIEF_TERMINAL_STATUSES,
            f"not terminal statuses: {sorted(_RETIRED_BRIEF_STATUSES - BRIEF_TERMINAL_STATUSES)}",
        )

    def test_missing_status_stays_in_scope(self) -> None:
        """An unreadable status is not evidence the brief is sealed."""
        rows = [_with_status(_req("01"), brief_status=None)]
        self.assertEqual(self._ids(rows), {"REQ-0.1.0-01-01"})


class TestReservedFixtureNamespace(unittest.TestCase):
    """`REQ-9.9.9-*` is the corpus's negative-control id, not a real citation."""

    def _covers(self, req_id: str) -> LinkageRecord:
        return LinkageRecord(
            source=VertexRef(
                vertex_type=VertexType.TEST,
                identifier="tests/test_x.py",
                location="tests/test_x.py",
                line=1,
            ),
            target=VertexRef(vertex_type=VertexType.SPEC, identifier=req_id),
            edge_type=EdgeType.COVERS,
            evidence_path="tests/test_x.py",
            evidence_line=1,
        )

    def test_reserved_namespace_is_not_an_orphan(self) -> None:
        """A test asserting @covers rejects unknown REQs must cite an unknown REQ."""
        report = detect_drift([], [self._covers("REQ-9.9.9-99-99")], [], "2026-07-28T00:00:00Z")
        self.assertEqual(report.orphan_tests, [])

    def test_real_unknown_req_is_still_an_orphan(self) -> None:
        """Scoping the sentinel must not blind the detector to genuine drift."""
        report = detect_drift([], [self._covers("REQ-0.1.0-01-09")], [], "2026-07-28T00:00:00Z")
        self.assertEqual(report.orphan_tests, ["REQ-0.1.0-01-09"])


class TestScopingDoesNotManufactureOrphans(unittest.TestCase):
    """The two drift arms read different REQ sets, and must keep doing so.

    Regression pin for a bug introduced while fixing GHI #729: scoping was
    first applied at the CALLER, which shrank `known_req_ids` — the orphan
    baseline — so every test legitimately citing a SUPPORT or doc-kind REQ
    turned into a phantom orphan (10 orphans became 63). `unlinked` reads the
    covers-channel subset; `orphans` must read ALL declared REQs.
    """

    def _covers(self, req_id: str) -> LinkageRecord:
        return LinkageRecord(
            source=VertexRef(
                vertex_type=VertexType.TEST,
                identifier="tests/test_x.py",
                location="tests/test_x.py",
                line=1,
            ),
            target=VertexRef(vertex_type=VertexType.SPEC, identifier=req_id),
            edge_type=EdgeType.COVERS,
            evidence_path="tests/test_x.py",
            evidence_line=1,
        )

    def test_support_req_with_a_test_is_not_an_orphan(self) -> None:
        """A SUPPORT REQ is out of the unlinked arm yet still a declared REQ."""
        support = _req("01", taxonomy_kind="SUPPORT")
        report = detect_drift(
            [support], [self._covers("REQ-0.1.0-01-01")], [], "2026-07-28T00:00:00Z"
        )
        self.assertEqual(report.orphan_tests, [])
        self.assertEqual(report.unlinked_specs, [])

    def test_retired_brief_req_with_a_test_is_not_an_orphan(self) -> None:
        retired = _with_status(_req("01"), brief_status="Withdrawn")
        report = detect_drift(
            [retired], [self._covers("REQ-0.1.0-01-01")], [], "2026-07-28T00:00:00Z"
        )
        self.assertEqual(report.orphan_tests, [])
        self.assertEqual(report.unlinked_specs, [])


class TestFixtureDirectoryExcluded(unittest.TestCase):
    """`tests/fixtures/` holds inputs to tests, not citations by tests."""

    def test_covers_under_fixtures_is_not_scanned(self) -> None:
        from gzkit.commands.drift import scan_covers_references

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fixtures").mkdir()
            (root / "fixtures" / "sample.py").write_text(
                "# @covers REQ-0.99.0-01-01\ndef f():\n    pass\n", encoding="utf-8"
            )
            (root / "test_real.py").write_text(
                "# @covers REQ-0.1.0-01-01\ndef test_f():\n    pass\n", encoding="utf-8"
            )
            targets = {r.target.identifier for r in scan_covers_references(root)}

        self.assertEqual(targets, {"REQ-0.1.0-01-01"})


if __name__ == "__main__":
    unittest.main()
