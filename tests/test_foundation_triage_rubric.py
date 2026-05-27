"""Tests for gzkit.foundation.rubric — derived from OBPI-0.0.57-04 REQs."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.traceability import covers


class TestFoundationTriageRankEntry(unittest.TestCase):
    """REQ-0.0.57-04-01 and REQ-0.0.57-04-03: model constraints."""

    @classmethod
    def setUpClass(cls) -> None:
        from gzkit.foundation.rubric import EvidenceRef, FoundationTriageRankEntry

        cls.EvidenceRef = EvidenceRef
        cls.FoundationTriageRankEntry = FoundationTriageRankEntry

    @covers("REQ-0.0.57-04-01")
    def test_valid_construction(self) -> None:
        # @covers REQ-0.0.57-04-01
        ref = self.EvidenceRef(
            source="insights.jsonl",
            dimension="insights_signal",
            weight=3,
            weighted=6,
            count=2,
        )
        entry = self.FoundationTriageRankEntry(
            id="ADR-0.0.90",
            priority_score=10,
            evidence=(ref,),
        )
        self.assertEqual(entry.id, "ADR-0.0.90")
        self.assertEqual(entry.priority_score, 10)
        self.assertEqual(len(entry.evidence), 1)

    @covers("REQ-0.0.57-04-01")
    def test_empty_evidence_raises(self) -> None:
        # @covers REQ-0.0.57-04-01
        with self.assertRaises(ValidationError):
            self.FoundationTriageRankEntry(
                id="ADR-0.0.90",
                priority_score=0,
                evidence=(),
            )

    @covers("REQ-0.0.57-04-03")
    def test_extra_field_raises(self) -> None:
        # @covers REQ-0.0.57-04-03
        ref = self.EvidenceRef(
            source="x", dimension="insights_signal", weight=3, weighted=3, count=1
        )
        with self.assertRaises(ValidationError):
            self.FoundationTriageRankEntry(
                id="ADR-0.0.90",
                priority_score=1,
                evidence=(ref,),
                rationale="this should be rejected",
            )

    @covers("REQ-0.0.57-04-03")
    def test_evidence_ref_extra_field_raises(self) -> None:
        # @covers REQ-0.0.57-04-03
        with self.assertRaises(ValidationError):
            self.EvidenceRef(
                source="x", dimension="insights_signal", weight=3, weighted=3, count=1, why="bad"
            )

    @covers("REQ-0.0.57-04-03")
    def test_evidence_ref_dimension_is_literal(self) -> None:
        # @covers REQ-0.0.57-04-03 — dimension is a Literal enum, not free-form
        with self.assertRaises(ValidationError):
            self.EvidenceRef(source="x", dimension="freeform_string", weight=3, weighted=0, count=0)

    @covers("REQ-0.0.57-04-02")
    def test_evidence_ref_weighted_consistency(self) -> None:
        # @covers REQ-0.0.57-04-02 — weighted must equal weight × count
        with self.assertRaises(ValidationError):
            self.EvidenceRef(
                source="x", dimension="insights_signal", weight=3, weighted=99, count=2
            )

    @covers("REQ-0.0.57-04-01")
    def test_evidence_ref_count_must_be_non_negative(self) -> None:
        # @covers REQ-0.0.57-04-01 — count is bounded; negative counts are nonsensical
        with self.assertRaises(ValidationError):
            self.EvidenceRef(
                source="x", dimension="insights_signal", weight=3, weighted=3, count=-1
            )

    @covers("REQ-0.0.57-04-01")
    def test_entry_is_frozen(self) -> None:
        # @covers REQ-0.0.57-04-01
        ref = self.EvidenceRef(
            source="x", dimension="insights_signal", weight=3, weighted=3, count=1
        )
        entry = self.FoundationTriageRankEntry(id="ADR-0.0.90", priority_score=1, evidence=(ref,))
        with self.assertRaises((ValidationError, TypeError)):
            entry.id = "ADR-0.0.91"  # type: ignore


class TestGatherFoundationIdsHandlesCanonicalSlug(unittest.TestCase):
    """Regression: _gather_foundation_ids must recover ADR-X.Y.Z from canonical-slug ids (GHI #548).

    The defective code split raw frontmatter `id` on the literal `-foundation-`
    substring; real ids are shaped `ADR-X.Y.Z-<slug>` with no `-foundation-`
    substring, so the split returned the input unchanged and the
    `^ADR-\\d+\\.\\d+\\.\\d+$` filter rejected every real entry. Sibling
    class-of-failure to GHI #518 (composer + bundled triage script).
    """

    def test_gather_returns_canonical_slug_id(self) -> None:
        from gzkit.foundation.rubric import _gather_foundation_ids

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            adr_dir = (
                project_root
                / "docs"
                / "design"
                / "adr"
                / "foundation"
                / "ADR-0.0.77-canonical-slug-no-foundation-substring"
            )
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-0.0.77-canonical-slug-no-foundation-substring.md").write_text(
                "---\n"
                "id: ADR-0.0.77-canonical-slug-no-foundation-substring\n"
                "status: Draft\n"
                "---\n"
                "# ADR-0.0.77\n",
                encoding="utf-8",
            )
            ids = _gather_foundation_ids(project_root)
            self.assertEqual(ids, ["ADR-0.0.77"])


class TestStructuralOnly(unittest.TestCase):
    """REQ-0.0.57-04-03: output is structural-only, no prose fields."""

    @covers("REQ-0.0.57-04-03")
    def test_rank_entry_keys_are_structural_only(self) -> None:
        # @covers REQ-0.0.57-04-03
        from gzkit.foundation.rubric import EvidenceRef, FoundationTriageRankEntry

        ref = EvidenceRef(source="x", dimension="insights_signal", weight=3, weighted=3, count=1)
        entry = FoundationTriageRankEntry(id="ADR-0.0.90", priority_score=5, evidence=(ref,))
        keys = set(entry.model_dump().keys())
        self.assertEqual(keys, {"id", "priority_score", "evidence"})


class TestRubricSignals(unittest.TestCase):
    """REQ-0.0.57-04-02 and REQ-0.0.57-04-06: signal dimension counting."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = Path(__file__).parent / "fixtures" / "foundation_triage_rubric"

    @covers("REQ-0.0.57-04-02")
    def test_three_dimensions_computed_and_in_evidence(self) -> None:
        # @covers REQ-0.0.57-04-02
        from gzkit.foundation.rubric import score_foundation

        with tempfile.TemporaryDirectory() as tmp:
            project_root = _build_minimal_project(tmp, self.fixtures)
            entry = score_foundation(
                project_root,
                "ADR-0.0.90",
                insights_path=self.fixtures / "insights.jsonl",
                pool_adrs_root=self.fixtures / "pool_adrs",
            )
        signal_types = {ref.dimension for ref in entry.evidence}
        self.assertIn("insights_signal", signal_types)
        self.assertIn("ghi_occurrence", signal_types)
        self.assertIn("feature_unblocking", signal_types)

    @covers("REQ-0.0.57-04-02")
    def test_insights_signal_count_correct(self) -> None:
        # @covers REQ-0.0.57-04-02
        from gzkit.foundation.rubric import score_foundation

        with tempfile.TemporaryDirectory() as tmp:
            project_root = _build_minimal_project(tmp, self.fixtures)
            entry = score_foundation(
                project_root,
                "ADR-0.0.90",
                insights_path=self.fixtures / "insights.jsonl",
                pool_adrs_root=self.fixtures / "pool_adrs",
            )
        insight_ref = next(r for r in entry.evidence if r.dimension == "insights_signal")
        # fixtures/insights.jsonl has 3 rows mentioning ADR-0.0.90
        self.assertEqual(insight_ref.count, 3)

    @covers("REQ-0.0.57-04-06")
    def test_feature_unblocking_count_correct(self) -> None:
        # @covers REQ-0.0.57-04-06
        from gzkit.foundation.rubric import score_foundation

        with tempfile.TemporaryDirectory() as tmp:
            project_root = _build_minimal_project(tmp, self.fixtures)
            entry = score_foundation(
                project_root,
                "ADR-0.0.90",
                insights_path=self.fixtures / "insights.jsonl",
                pool_adrs_root=self.fixtures / "pool_adrs",
            )
        unblocking_ref = next(r for r in entry.evidence if r.dimension == "feature_unblocking")
        # feature-x and feature-y both depend on ADR-0.0.90; feature-z does not
        self.assertEqual(unblocking_ref.count, 2)

    @covers("REQ-0.0.57-04-06")
    def test_feature_unblocking_increments_per_dependent(self) -> None:
        # @covers REQ-0.0.57-04-06
        from gzkit.foundation.rubric import score_foundation

        with tempfile.TemporaryDirectory() as tmp:
            project_root = _build_minimal_project(tmp, self.fixtures)
            # ADR-0.0.91 has no pool ADR dependents
            entry = score_foundation(
                project_root,
                "ADR-0.0.91",
                insights_path=self.fixtures / "insights.jsonl",
                pool_adrs_root=self.fixtures / "pool_adrs",
            )
        unblocking_ref = next(r for r in entry.evidence if r.dimension == "feature_unblocking")
        self.assertEqual(unblocking_ref.count, 0)

    @covers("REQ-0.0.57-04-02")
    def test_priority_score_reflects_all_dimensions(self) -> None:
        # @covers REQ-0.0.57-04-02
        from gzkit.foundation.rubric import score_foundation

        with tempfile.TemporaryDirectory() as tmp:
            project_root = _build_minimal_project(tmp, self.fixtures)
            entry = score_foundation(
                project_root,
                "ADR-0.0.90",
                insights_path=self.fixtures / "insights.jsonl",
                pool_adrs_root=self.fixtures / "pool_adrs",
            )
        # priority_score must be > 0 reflecting at least one dimension contributing
        self.assertGreater(entry.priority_score, 0)

    @covers("REQ-0.0.57-04-02")
    def test_ghi_occurrence_count_from_insights(self) -> None:
        # @covers REQ-0.0.57-04-02
        from gzkit.foundation.rubric import score_foundation

        with tempfile.TemporaryDirectory() as tmp:
            project_root = _build_minimal_project(tmp, self.fixtures)
            entry = score_foundation(
                project_root,
                "ADR-0.0.90",
                insights_path=self.fixtures / "insights.jsonl",
                pool_adrs_root=self.fixtures / "pool_adrs",
            )
        ghi_ref = next(r for r in entry.evidence if r.dimension == "ghi_occurrence")
        # Row 1: GHI #101 (1), Row 2: GHI #202, GHI #303 (2), Row 3: none (0)
        # Unique GHI count = 3
        self.assertEqual(ghi_ref.count, 3)


class TestPrdRegistration(unittest.TestCase):
    """REQ-0.0.57-04-04: PRD vocabulary registration."""

    @covers("REQ-0.0.57-04-04")
    def test_governance_triage_vocabulary_exists(self) -> None:
        # @covers REQ-0.0.57-04-04
        prd = Path(__file__).parents[1] / "docs" / "design" / "prd" / "PRD-GZKIT-1.0.0.md"
        content = prd.read_text(encoding="utf-8")
        self.assertIn("governance-triage", content)
        self.assertIn("ADR-0.0.57-foundation-adr-nominal-id-triage", content)

    @covers("REQ-0.0.57-04-04")
    def test_feature_unblocking_count_term_registered(self) -> None:
        # @covers REQ-0.0.57-04-04
        prd = Path(__file__).parents[1] / "docs" / "design" / "prd" / "PRD-GZKIT-1.0.0.md"
        content = prd.read_text(encoding="utf-8")
        self.assertIn("feature-unblocking-count", content)


class TestJsonSchema(unittest.TestCase):
    """REQ-0.0.57-04-05: JSON schema validates Pydantic-emitted entries."""

    @covers("REQ-0.0.57-04-05")
    def test_schema_file_exists(self) -> None:
        # @covers REQ-0.0.57-04-05
        schema_path = (
            Path(__file__).parents[1]
            / "src"
            / "gzkit"
            / "schemas"
            / "foundation_triage_rank_input.json"
        )
        self.assertTrue(schema_path.exists())

    @covers("REQ-0.0.57-04-05")
    def test_schema_validates_pydantic_output(self) -> None:
        # @covers REQ-0.0.57-04-05
        import jsonschema

        from gzkit.foundation.rubric import EvidenceRef, FoundationTriageRankEntry

        schema_path = (
            Path(__file__).parents[1]
            / "src"
            / "gzkit"
            / "schemas"
            / "foundation_triage_rank_input.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        ref = EvidenceRef(source="test", dimension="insights_signal", weight=3, weighted=3, count=1)
        entry = FoundationTriageRankEntry(id="ADR-0.0.90", priority_score=3, evidence=(ref,))
        instance = entry.model_dump()
        # evidence is a tuple — convert to list for JSON schema validation
        instance["evidence"] = list(instance["evidence"])
        jsonschema.validate(instance, schema)

    @covers("REQ-0.0.57-04-05")
    def test_schema_rejects_extra_fields(self) -> None:
        # @covers REQ-0.0.57-04-05
        import jsonschema

        schema_path = (
            Path(__file__).parents[1]
            / "src"
            / "gzkit"
            / "schemas"
            / "foundation_triage_rank_input.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        invalid = {"id": "ADR-0.0.90", "priority_score": 1, "evidence": [], "rationale": "bad"}
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(invalid, schema)


def _build_minimal_project(tmp: str, fixtures: Path) -> Path:
    """Build a minimal project tree in tmp for signal counting tests."""
    project_root = Path(tmp)
    (project_root / ".gzkit" / "insights").mkdir(parents=True)
    (project_root / ".gzkit" / "rules").mkdir(parents=True)
    (project_root / "docs" / "design" / "adr" / "foundation").mkdir(parents=True)
    # Copy fixture foundation ADRs into project tree
    foundation_dir = project_root / "docs" / "design" / "adr" / "foundation"
    for src in (fixtures / "backlog").iterdir():
        import shutil

        shutil.copy(src, foundation_dir / src.name)
    # Copy insights
    import shutil

    shutil.copy(
        fixtures / "insights.jsonl", project_root / ".gzkit" / "insights" / "agent-insights.jsonl"
    )
    # Write minimal AGENTS.md
    (project_root / "AGENTS.md").write_text(
        "# AGENTS\n\nADR-0.0.90 and ADR-0.0.91 are test fixtures.\n", encoding="utf-8"
    )
    return project_root


if __name__ == "__main__":
    unittest.main()
