"""Tests for infer_req_kind and compute_three_channel_coverage (OBPI-0.0.59-03).

The ReqCoverageRecord/ReqCoverageSummary contract tests were retired with the
models (GHI #545): CoverageEntry/CoverageReport are the surviving three-channel
coverage record — a complete superset already wired into `gz covers --json`.

All tests derive semantics from brief REQs, not from implementation output.
"""

import json
import unittest
import unittest.mock
from pathlib import Path

from gzkit.traceability import covers
from tests.commands.common import SilencedConsoleTestCase


class TestReqEntityTaxonomyKind(unittest.TestCase):
    """REQ-0.0.59-03-01 (BEHAVIOR): gz covers JSON includes per-REQ kind fields.

    Prerequisite: ReqEntity must store taxonomy_kind from [kind] inline tags.
    """

    @covers("REQ-0.0.59-03-01")
    def test_behavior_tag_stored_on_req_entity(self) -> None:
        """extract_reqs_from_brief populates taxonomy_kind from [BEHAVIOR] tag."""
        from gzkit.triangle import extract_reqs_from_brief

        content = "## Acceptance Criteria\n- [ ] REQ-0.0.59-03-01 [BEHAVIOR]: Code behavior REQ\n"
        reqs = extract_reqs_from_brief(content, "OBPI-0.0.59-03")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].taxonomy_kind, "BEHAVIOR")

    @covers("REQ-0.0.59-03-01")
    def test_support_tag_stored_on_req_entity(self) -> None:
        """extract_reqs_from_brief populates taxonomy_kind from [SUPPORT] tag."""
        from gzkit.triangle import extract_reqs_from_brief

        content = (
            "## Acceptance Criteria\n"
            "- [ ] REQ-0.0.59-03-02 [SUPPORT]: Support REQ "
            "gz validate --documents ledger artifact_edited\n"
        )
        reqs = extract_reqs_from_brief(content, "OBPI-0.0.59-03")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].taxonomy_kind, "SUPPORT")

    @covers("REQ-0.0.59-03-01")
    def test_structural_fence_tag_stored_on_req_entity(self) -> None:
        """extract_reqs_from_brief populates taxonomy_kind from [STRUCTURAL-FENCE] tag."""
        from gzkit.triangle import extract_reqs_from_brief

        content = (
            "## Acceptance Criteria\n"
            "- [ ] REQ-0.0.59-03-03 [STRUCTURAL-FENCE]: Boundary invariants REQ\n"
        )
        reqs = extract_reqs_from_brief(content, "OBPI-0.0.59-03")
        self.assertEqual(len(reqs), 1)
        self.assertEqual(reqs[0].taxonomy_kind, "STRUCTURAL-FENCE")

    @covers("REQ-0.0.59-03-01")
    def test_untagged_req_has_none_taxonomy_kind(self) -> None:
        """extract_reqs_from_brief sets taxonomy_kind=None for untagged legacy REQs."""
        from gzkit.triangle import extract_reqs_from_brief

        content = "## Acceptance Criteria\n- [ ] REQ-0.0.59-03-04: Legacy untagged REQ\n"
        reqs = extract_reqs_from_brief(content, "OBPI-0.0.59-03")
        self.assertEqual(len(reqs), 1)
        self.assertIsNone(reqs[0].taxonomy_kind)


class TestCoverageEntryExtendedFields(unittest.TestCase):
    """REQ-0.0.59-03-01 and REQ-0.0.59-03-05 (BEHAVIOR): CoverageEntry has kind fields."""

    @covers("REQ-0.0.59-03-01")
    def test_coverage_entry_has_taxonomy_kind_field(self) -> None:
        """CoverageEntry has optional taxonomy_kind defaulting to None."""
        from gzkit.traceability import CoverageEntry

        entry = CoverageEntry(req_id="REQ-0.0.59-03-01", covered=True, covering_tests=[])
        self.assertIsNone(entry.taxonomy_kind)

    @covers("REQ-0.0.59-03-01")
    def test_coverage_entry_has_proof_channel_field(self) -> None:
        """CoverageEntry has optional proof_channel defaulting to None."""
        from gzkit.traceability import CoverageEntry

        entry = CoverageEntry(req_id="REQ-0.0.59-03-01", covered=True, covering_tests=[])
        self.assertIsNone(entry.proof_channel)

    @covers("REQ-0.0.59-03-01")
    def test_coverage_entry_has_proof_status_field(self) -> None:
        """CoverageEntry has proof_status defaulting to 'unknown'."""
        from gzkit.traceability import CoverageEntry

        entry = CoverageEntry(req_id="REQ-0.0.59-03-01", covered=True, covering_tests=[])
        self.assertEqual(entry.proof_status, "unknown")

    @covers("REQ-0.0.59-03-01")
    def test_coverage_entry_has_ledger_event_ids_field(self) -> None:
        """CoverageEntry has ledger_event_ids defaulting to empty list."""
        from gzkit.traceability import CoverageEntry

        entry = CoverageEntry(req_id="REQ-0.0.59-03-01", covered=True, covering_tests=[])
        self.assertEqual(entry.ledger_event_ids, [])

    @covers("REQ-0.0.59-03-01")
    def test_coverage_entry_has_parent_adr_anchor_field(self) -> None:
        """CoverageEntry has optional parent_adr_anchor defaulting to None."""
        from gzkit.traceability import CoverageEntry

        entry = CoverageEntry(req_id="REQ-0.0.59-03-01", covered=True, covering_tests=[])
        self.assertIsNone(entry.parent_adr_anchor)

    @covers("REQ-0.0.59-03-05")
    def test_coverage_rollup_has_behavior_uncovered_reqs(self) -> None:
        """CoverageRollup has behavior_uncovered_reqs defaulting to 0."""
        from gzkit.traceability import CoverageRollup

        rollup = CoverageRollup(
            identifier="all",
            total_reqs=3,
            covered_reqs=2,
            uncovered_reqs=1,
            coverage_percent=66.7,
        )
        self.assertEqual(rollup.behavior_uncovered_reqs, 0)

    @covers("REQ-0.0.59-03-05")
    def test_coverage_rollup_has_grandfathered_reqs(self) -> None:
        """CoverageRollup has grandfathered_reqs defaulting to 0."""
        from gzkit.traceability import CoverageRollup

        rollup = CoverageRollup(
            identifier="all",
            total_reqs=3,
            covered_reqs=2,
            uncovered_reqs=1,
            coverage_percent=66.7,
        )
        self.assertEqual(rollup.grandfathered_reqs, 0)


class TestInferReqKind(unittest.TestCase):
    """REQ-0.0.59-03-02 (BEHAVIOR): One-shot inference heuristic for legacy REQs."""

    def _infer(self, text: str) -> tuple:
        from gzkit.req_kind import infer_req_kind

        return infer_req_kind(text)

    @covers("REQ-0.0.59-03-02")
    def test_default_inference_is_behavior(self) -> None:
        """Generic REQ text defaults to BEHAVIOR classification."""
        from gzkit.req_kind import ReqKind

        kind, status = self._infer("Given the module, when invoked, then it returns the result.")
        self.assertEqual(kind, ReqKind.BEHAVIOR)
        self.assertEqual(status, "inferred-behavior")

    @covers("REQ-0.0.59-03-02")
    def test_denied_paths_text_infers_structural_fence(self) -> None:
        """REQ text mentioning 'Denied Paths' infers STRUCTURAL-FENCE."""
        from gzkit.req_kind import ReqKind

        kind, status = self._infer(
            "Given the brief's Denied Paths, when changes run, then denied paths remain untouched."
        )
        self.assertEqual(kind, ReqKind.STRUCTURAL_FENCE)
        self.assertEqual(status, "inferred-structural-fence")

    @covers("REQ-0.0.59-03-02")
    def test_boundary_invariants_text_infers_structural_fence(self) -> None:
        """REQ text mentioning 'boundary invariants' infers STRUCTURAL-FENCE."""
        from gzkit.req_kind import ReqKind

        kind, status = self._infer("boundary invariants entry in the parent ADR is required.")
        self.assertEqual(kind, ReqKind.STRUCTURAL_FENCE)
        self.assertEqual(status, "inferred-structural-fence")

    @covers("REQ-0.0.59-03-02")
    def test_remains_inside_scope_infers_structural_fence(self) -> None:
        """REQ text mentioning 'remains inside scope' infers STRUCTURAL-FENCE."""
        from gzkit.req_kind import ReqKind

        kind, status = self._infer("changes remains inside scope contract.")
        self.assertEqual(kind, ReqKind.STRUCTURAL_FENCE)
        self.assertEqual(status, "inferred-structural-fence")

    @covers("REQ-0.0.59-03-02")
    def test_artifact_edited_text_infers_support(self) -> None:
        """REQ text mentioning 'artifact_edited' infers SUPPORT."""
        from gzkit.req_kind import ReqKind

        kind, status = self._infer(
            "Given the file exists, when it is modified, artifact_edited event emitted."
        )
        self.assertEqual(kind, ReqKind.SUPPORT)
        self.assertEqual(status, "inferred-support")

    @covers("REQ-0.0.59-03-02")
    def test_gz_validate_text_infers_support(self) -> None:
        """REQ text mentioning 'gz validate --' infers SUPPORT."""
        from gzkit.req_kind import ReqKind

        kind, status = self._infer("gz validate --documents confirms valid JSON.")
        self.assertEqual(kind, ReqKind.SUPPORT)
        self.assertEqual(status, "inferred-support")

    @covers("REQ-0.0.59-03-02")
    def test_structural_fence_beats_support_on_denied_paths(self) -> None:
        """STRUCTURAL-FENCE takes priority over SUPPORT when both patterns match."""
        from gzkit.req_kind import ReqKind

        # "Denied Paths" is STRUCTURAL_FENCE trigger, even if "artifact_edited" also present
        kind, status = self._infer("Denied Paths remain untouched; artifact_edited event confirms.")
        self.assertEqual(kind, ReqKind.STRUCTURAL_FENCE)


class TestComputeThreeChannelCoverage(unittest.TestCase):
    """REQ-0.0.59-03-01, REQ-0.0.59-03-02, REQ-0.0.59-03-05 (BEHAVIOR):
    compute_three_channel_coverage enriches coverage report with kind fields.
    """

    def _make_minimal_report(self, req_id: str, covered: bool, covering_tests: list[str]):
        from gzkit.traceability import CoverageEntry, CoverageReport, CoverageRollup

        entry = CoverageEntry(
            req_id=req_id,
            covered=covered,
            covering_tests=covering_tests,
        )
        rollup = CoverageRollup(
            identifier="all",
            total_reqs=1,
            covered_reqs=1 if covered else 0,
            uncovered_reqs=0 if covered else 1,
            coverage_percent=100.0 if covered else 0.0,
        )
        return CoverageReport(by_adr=[], by_obpi=[], entries=[entry], summary=rollup)

    def _make_discovered_req(self, req_id: str, taxonomy_kind: str | None):
        from gzkit.triangle import DiscoveredReq, ReqEntity, ReqId, ReqKind, ReqStatus

        rid = ReqId.parse(req_id)
        entity = ReqEntity(
            id=rid,
            description="test",
            status=ReqStatus.UNCHECKED,
            parent_obpi="OBPI-0.0.59-03",
            kind=ReqKind.CODE,
            taxonomy_kind=taxonomy_kind,
        )
        return DiscoveredReq(entity=entity, source_path="test_brief.md")

    @covers("REQ-0.0.59-03-01")
    @covers("REQ-0.0.59-03-05")
    def test_behavior_covered_req_has_pass_status(self) -> None:
        """BEHAVIOR REQ with @covers test gets proof_status='pass'."""
        from gzkit.req_kind import compute_three_channel_coverage

        report = self._make_minimal_report(
            "REQ-0.0.59-03-01", covered=True, covering_tests=["tests/foo.py"]
        )
        dreq = self._make_discovered_req("REQ-0.0.59-03-01", "BEHAVIOR")
        enriched = compute_three_channel_coverage(report, [dreq])
        entry = enriched.entries[0]
        self.assertEqual(entry.taxonomy_kind, "BEHAVIOR")
        self.assertEqual(entry.proof_status, "pass")
        self.assertFalse(enriched.summary.behavior_uncovered_reqs > 0)

    @covers("REQ-0.0.59-03-05")
    def test_behavior_uncovered_req_has_fail_status(self) -> None:
        """BEHAVIOR REQ without @covers test gets proof_status='fail'."""
        from gzkit.req_kind import compute_three_channel_coverage

        report = self._make_minimal_report("REQ-0.0.59-03-01", covered=False, covering_tests=[])
        dreq = self._make_discovered_req("REQ-0.0.59-03-01", "BEHAVIOR")
        enriched = compute_three_channel_coverage(report, [dreq])
        entry = enriched.entries[0]
        self.assertEqual(entry.proof_status, "fail")
        self.assertEqual(enriched.summary.behavior_uncovered_reqs, 1)

    @covers("REQ-0.0.59-03-01")
    @covers("REQ-0.0.59-03-05")
    def test_support_req_is_advisory_not_fail_closed(self) -> None:
        """SUPPORT REQ gets proof_status='advisory-support' regardless of test coverage."""
        from gzkit.req_kind import compute_three_channel_coverage

        report = self._make_minimal_report("REQ-0.0.59-03-01", covered=False, covering_tests=[])
        dreq = self._make_discovered_req("REQ-0.0.59-03-01", "SUPPORT")
        enriched = compute_three_channel_coverage(report, [dreq])
        entry = enriched.entries[0]
        self.assertEqual(entry.proof_status, "advisory-support")
        self.assertEqual(enriched.summary.behavior_uncovered_reqs, 0)
        self.assertGreater(enriched.summary.grandfathered_reqs, 0)

    @covers("REQ-0.0.59-03-01")
    @covers("REQ-0.0.59-03-05")
    def test_structural_fence_req_no_project_root_is_unproven_fence(self) -> None:
        """STRUCTURAL-FENCE REQ with no project_root gets proof_status='unproven-fence'.

        The arm is fail-close: unproven-fence is NOT advisory, so grandfathered_reqs == 0.
        """
        from gzkit.req_kind import compute_three_channel_coverage

        report = self._make_minimal_report("REQ-0.0.59-03-01", covered=False, covering_tests=[])
        dreq = self._make_discovered_req("REQ-0.0.59-03-01", "STRUCTURAL-FENCE")
        enriched = compute_three_channel_coverage(report, [dreq])
        entry = enriched.entries[0]
        self.assertEqual(entry.proof_status, "unproven-fence")
        self.assertEqual(enriched.summary.behavior_uncovered_reqs, 0)
        self.assertEqual(enriched.summary.grandfathered_reqs, 0)

    @covers("REQ-0.0.59-03-02")
    def test_legacy_untagged_req_inferred_as_grandfathered(self) -> None:
        """Legacy untagged REQ is inferred and marked grandfathered=True."""
        from gzkit.req_kind import compute_three_channel_coverage

        report = self._make_minimal_report("REQ-0.0.59-03-01", covered=False, covering_tests=[])
        dreq = self._make_discovered_req("REQ-0.0.59-03-01", None)
        enriched = compute_three_channel_coverage(report, [dreq])
        entry = enriched.entries[0]
        # Inferred as BEHAVIOR by default for generic description
        self.assertIn("inferred", entry.proof_status)
        # Legacy (untagged) reqs are advisory — not fail-closed
        self.assertEqual(enriched.summary.behavior_uncovered_reqs, 0)

    @covers("REQ-0.0.59-03-02")
    def test_grandfathering_cache_overrides_inference(self) -> None:
        """Operator-supplied kind in grandfathering cache overrides inferred kind."""
        from gzkit.req_kind import compute_three_channel_coverage

        report = self._make_minimal_report("REQ-0.0.59-03-01", covered=False, covering_tests=[])
        dreq = self._make_discovered_req("REQ-0.0.59-03-01", None)
        # Operator overrides the default BEHAVIOR inference to STRUCTURAL-FENCE.
        # Without project_root, proof_status is unproven-fence (fail-close, not advisory).
        cache = {"REQ-0.0.59-03-01": "STRUCTURAL-FENCE"}
        enriched = compute_three_channel_coverage(report, [dreq], grandfathering_cache=cache)
        entry = enriched.entries[0]
        self.assertEqual(entry.taxonomy_kind, "STRUCTURAL-FENCE")
        self.assertEqual(entry.proof_status, "unproven-fence")


class TestBypassFlagLedgerEvent(SilencedConsoleTestCase):
    """REQ-0.0.59-03-04 (BEHAVIOR): --bypass-req-kind-discipline-once emits bypass_used event."""

    @covers("REQ-0.0.59-03-04")
    def test_bypass_emits_bypass_used_ledger_event(self) -> None:
        """_emit_bypass_ledger_event writes a bypass_used event to the ledger."""
        import tempfile
        import types

        from gzkit.commands.covers import _emit_bypass_ledger_event

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            ledger_path = tmp_path / "ledger.jsonl"
            cfg = types.SimpleNamespace(paths=types.SimpleNamespace(ledger=ledger_path))
            with unittest.mock.patch("gzkit.config.load_config", return_value=cfg):
                _emit_bypass_ledger_event(tmp_path, "unit test bypass reason")

            lines = ledger_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            event = json.loads(lines[0])
            self.assertEqual(event["event"], "bypass_used")
            self.assertEqual(event["reason"], "unit test bypass reason")
            self.assertEqual(event["scope"], "gz-covers-req-kind-discipline")

    @covers("REQ-0.0.59-03-04")
    def test_bypass_flag_requires_bypass_reason(self) -> None:
        """covers_cmd exits 1 when bypass flag is set without --bypass-reason."""
        from gzkit.commands.covers import covers_cmd

        with self.assertRaises(SystemExit) as ctx:
            covers_cmd(bypass_req_kind_discipline_once=True, bypass_reason=None)
        self.assertEqual(ctx.exception.code, 1)


class TestGrandfatheringCacheFile(unittest.TestCase):
    """REQ-0.0.59-03-06 (SUPPORT): data/req_kind_grandfathering.json exists as valid JSON."""

    def test_grandfathering_json_exists(self) -> None:
        """data/req_kind_grandfathering.json exists in the repository."""
        project_root = Path(__file__).parent.parent.parent
        cache_path = project_root / "data" / "req_kind_grandfathering.json"
        self.assertTrue(cache_path.exists(), f"Missing: {cache_path}")

    def test_grandfathering_json_is_valid_json(self) -> None:
        """data/req_kind_grandfathering.json contains valid JSON."""
        project_root = Path(__file__).parent.parent.parent
        cache_path = project_root / "data" / "req_kind_grandfathering.json"
        data = json.loads(cache_path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main()
