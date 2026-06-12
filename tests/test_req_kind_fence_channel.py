"""Fail-close regression tests for the STRUCTURAL-FENCE proof channel (OBPI-0.0.69-02).

These tests derive semantics from brief REQs, not from implementation output.
REQ-0.0.69-02-01: FENCE REQ + NO Boundary Invariants anchor → unproven (fail-close)
REQ-0.0.69-02-02: FENCE REQ + Boundary Invariants anchor present → proven
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers


def _make_adr_package(project_root: Path, semver: str, *, with_boundary_invariants: bool) -> None:
    """Create a minimal fake ADR package under project_root/docs/design/adr/foundation/."""
    adr_dir = project_root / "docs" / "design" / "adr" / "foundation" / f"ADR-{semver}-fake"
    adr_dir.mkdir(parents=True)
    content = f"# ADR-{semver}-fake\n\n## Intent\n\nTest fixture only.\n"
    if with_boundary_invariants:
        content += "\n## Boundary Invariants\n\n1. Test structural invariant.\n"
    (adr_dir / f"ADR-{semver}-fake.md").write_text(content, encoding="utf-8")


def _make_fence_report(req_id: str):
    """Minimal CoverageReport + DiscoveredReq pair for a STRUCTURAL-FENCE REQ."""
    from gzkit.traceability import CoverageEntry, CoverageReport, CoverageRollup
    from gzkit.triangle import DiscoveredReq, ReqEntity, ReqId, ReqKind, ReqStatus

    entry = CoverageEntry(req_id=req_id, covered=False, covering_tests=[])
    rollup = CoverageRollup(
        identifier="all",
        total_reqs=1,
        covered_reqs=0,
        uncovered_reqs=1,
        coverage_percent=0.0,
    )
    report = CoverageReport(by_adr=[], by_obpi=[], entries=[entry], summary=rollup)

    rid = ReqId.parse(req_id)
    entity = ReqEntity(
        id=rid,
        description="STRUCTURAL-FENCE test REQ",
        status=ReqStatus.UNCHECKED,
        parent_obpi="OBPI-0.0.69-02",
        kind=ReqKind.CODE,
        taxonomy_kind="STRUCTURAL-FENCE",
    )
    dreq = DiscoveredReq(entity=entity, source_path="brief.md")
    return report, [dreq]


class TestFenceChannelNoAnchor(unittest.TestCase):
    """REQ-0.0.69-02-01 [behavior]: Fence REQ without Boundary Invariants anchor → unproven."""

    @covers("REQ-0.0.69-02-01")
    def test_fence_no_anchor_is_unproven(self) -> None:
        """FENCE REQ whose parent ADR has NO ## Boundary Invariants → proof_status unproven.

        The proof_status MUST NOT be 'grandfathered' or any advisory string.
        Fail-close: absent anchor = unproven.
        """
        from gzkit.req_kind import compute_three_channel_coverage

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _make_adr_package(project_root, "0.0.69", with_boundary_invariants=False)

            report, known_reqs = _make_fence_report("REQ-0.0.69-02-01")
            enriched = compute_three_channel_coverage(report, known_reqs, project_root=project_root)
            entry = enriched.entries[0]

        self.assertNotEqual(
            entry.proof_status,
            "grandfathered",
            "FENCE arm MUST NOT report 'grandfathered' — #538",
        )
        self.assertNotIn(
            "advisory",
            entry.proof_status,
            "FENCE arm MUST NOT report advisory status when anchor is absent",
        )
        self.assertIn(
            "unproven",
            entry.proof_status,
            "FENCE arm MUST report unproven when anchor is absent (fail-close)",
        )


class TestFenceChannelWithAnchor(unittest.TestCase):
    """REQ-0.0.69-02-02 [behavior]: Fence REQ with Boundary Invariants anchor → proven."""

    @covers("REQ-0.0.69-02-02")
    def test_fence_with_anchor_is_proven(self) -> None:
        """FENCE REQ whose parent ADR has ## Boundary Invariants → proof_status 'pass'."""
        from gzkit.req_kind import compute_three_channel_coverage

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            _make_adr_package(project_root, "0.0.69", with_boundary_invariants=True)

            report, known_reqs = _make_fence_report("REQ-0.0.69-02-02")
            enriched = compute_three_channel_coverage(report, known_reqs, project_root=project_root)
            entry = enriched.entries[0]

        self.assertEqual(
            entry.proof_status,
            "pass",
            "FENCE arm MUST report 'pass' when parent ADR has ## Boundary Invariants",
        )


class TestFenceChannelNoProjectRoot(unittest.TestCase):
    """REQ-0.0.69-02-01 [behavior]: Fence REQ without project_root → unproven (fail-close)."""

    @covers("REQ-0.0.69-02-01")
    def test_fence_no_project_root_is_unproven(self) -> None:
        """FENCE REQ with project_root=None → unproven, never grandfathered/advisory.

        When no project_root is provided, the anchor cannot be verified;
        the FENCE arm must fail-close (unproven), not degrade to advisory.
        """
        from gzkit.req_kind import compute_three_channel_coverage

        report, known_reqs = _make_fence_report("REQ-0.0.69-02-01")
        enriched = compute_three_channel_coverage(report, known_reqs, project_root=None)
        entry = enriched.entries[0]

        self.assertNotEqual(
            entry.proof_status,
            "grandfathered",
            "FENCE arm MUST NOT report 'grandfathered' even when project_root is absent",
        )
        self.assertNotIn(
            "advisory",
            entry.proof_status,
            "FENCE arm MUST NOT degrade to advisory when project_root is absent",
        )
        self.assertIn(
            "unproven",
            entry.proof_status,
            "FENCE arm MUST report unproven when project_root is absent (fail-close)",
        )
        self.assertEqual(
            enriched.summary.grandfathered_reqs,
            0,
            "unproven-fence is fail-closed, not advisory; grandfathered_reqs MUST be 0",
        )


class TestCoversCmdPassesProjectRoot(unittest.TestCase):
    """Regression: the `gz covers` CLI MUST pass project_root to the three-channel
    enricher, or STRUCTURAL-FENCE REQs resolve to unproven-fence at the CLI layer
    even when the parent ADR carries a ## Boundary Invariants anchor.

    The function-level fence tests above always pass project_root directly, so the
    CLI-wiring omission slipped past them; this test pins the wiring. (Direct fix
    surfaced during OBPI-0.0.70-01 Stage 3 parity gate, 2026-06-12.)
    """

    def test_covers_cmd_forwards_project_root_to_enricher(self) -> None:
        from unittest.mock import patch

        from gzkit.commands import covers as covers_mod

        captured: dict[str, object] = {}

        def _spy(report, known_reqs, grandfathering_cache=None, project_root=None):
            captured["project_root"] = project_root
            return report

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "docs" / "design" / "adr").mkdir(parents=True)
            (project_root / "tests").mkdir()
            (project_root / "features").mkdir()
            (project_root / "data").mkdir()

            # compute_three_channel_coverage is imported lazily inside covers_cmd,
            # so it must be patched at its source module (gzkit.req_kind).
            with (
                patch.object(covers_mod, "get_project_root", return_value=project_root),
                patch.object(covers_mod, "scan_briefs", return_value=[]),
                patch.object(covers_mod, "scan_test_tree", return_value=[]),
                patch.object(covers_mod, "scan_feature_tree", return_value=[]),
                patch("gzkit.req_kind.compute_three_channel_coverage", _spy),
            ):
                covers_mod.covers_cmd(
                    target="OBPI-0.0.70-01-stop-hook-turn-end-feedback", as_json=True
                )

        self.assertIn("project_root", captured)
        self.assertEqual(
            captured["project_root"],
            project_root,
            "covers_cmd MUST forward project_root so STRUCTURAL-FENCE REQs resolve at the CLI",
        )


if __name__ == "__main__":
    unittest.main()
