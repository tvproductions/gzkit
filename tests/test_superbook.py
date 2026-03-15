"""Tests for superbook pipeline."""

import unittest

from gzkit.superbook import (
    classify_lane,
    generate_adr_draft,
    map_chunks_to_obpis,
    map_commits_to_chunks,
    next_semver,
    present_draft,
)
from gzkit.superbook_models import (
    ADRDraft,
    ChunkData,
    CommitData,
    OBPIDraft,
    PlanData,
    SpecData,
)


class TestClassifyLane(unittest.TestCase):
    def test_heavy_when_cli_touched(self) -> None:
        """Lane is heavy when CLI file is in scope."""
        plan = PlanData(
            goal="Test",
            chunks=[ChunkData(name="C1", file_paths=["src/gzkit/cli.py"])],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "heavy")
        self.assertIn("src/gzkit/cli.py", result.signals)

    def test_heavy_when_schemas_touched(self) -> None:
        """Lane is heavy when schema files are in scope."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(
                    name="C1",
                    file_paths=[".gzkit/schemas/skill.schema.json"],
                )
            ],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "heavy")

    def test_lite_when_no_heavy_signals(self) -> None:
        """Lane is lite when no heavy signals present."""
        plan = PlanData(
            goal="Test",
            chunks=[ChunkData(name="C1", file_paths=["src/gzkit/foo.py"])],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "lite")
        self.assertEqual(result.signals, [])

    def test_heavy_when_templates_touched(self) -> None:
        """Lane is heavy when template files are in scope."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(
                    name="C1",
                    file_paths=["src/gzkit/templates/claude.md"],
                )
            ],
        )
        spec = SpecData(title="T", goal="G")
        result = classify_lane(spec, plan)
        self.assertEqual(result.lane, "heavy")


class TestNextSemver(unittest.TestCase):
    def test_next_semver_increments_minor(self) -> None:
        """next_semver increments minor version."""
        self.assertEqual(next_semver(["0.15.0", "0.16.0"]), "0.17.0")

    def test_next_semver_defaults_when_empty(self) -> None:
        """next_semver returns 0.1.0 when no existing ADRs."""
        self.assertEqual(next_semver([]), "0.1.0")

    def test_next_semver_handles_semantic_ordering(self) -> None:
        """next_semver orders semantically, not lexicographically."""
        self.assertEqual(next_semver(["0.9.0", "0.10.0"]), "0.11.0")


class TestMapChunksToObpis(unittest.TestCase):
    def test_map_produces_one_obpi_per_chunk(self) -> None:
        """Each chunk maps to exactly one OBPI."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(
                    name="Catalog",
                    file_paths=["src/sync.py"],
                    criteria=["criterion A"],
                ),
                ChunkData(
                    name="Mirroring",
                    file_paths=["src/sync.py"],
                    criteria=["criterion B"],
                ),
            ],
        )
        obpis = map_chunks_to_obpis(plan, "0.17.0", "heavy")
        self.assertEqual(len(obpis), 2)
        self.assertEqual(obpis[0].id, "OBPI-0.17.0-01-catalog")
        self.assertEqual(obpis[1].id, "OBPI-0.17.0-02-mirroring")

    def test_map_generates_req_ids(self) -> None:
        """REQ IDs are generated from chunk criteria."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(
                    name="Catalog",
                    file_paths=["src/sync.py"],
                    criteria=["Category extraction", "Categorized renderer"],
                ),
            ],
        )
        obpis = map_chunks_to_obpis(plan, "0.17.0", "heavy")
        self.assertEqual(len(obpis[0].reqs), 2)
        self.assertEqual(obpis[0].reqs[0].id, "REQ-0.17.0-01-01")
        self.assertEqual(obpis[0].reqs[1].id, "REQ-0.17.0-01-02")

    def test_map_slugifies_chunk_name(self) -> None:
        """OBPI slug is derived from chunk name."""
        plan = PlanData(
            goal="Test",
            chunks=[
                ChunkData(name="Slim CLAUDE.md Template", file_paths=[]),
            ],
        )
        obpis = map_chunks_to_obpis(plan, "0.17.0", "heavy")
        self.assertEqual(obpis[0].id, "OBPI-0.17.0-01-slim-claudemd-template")


class TestGenerateADRDraft(unittest.TestCase):
    def test_generate_adr_draft_from_spec_and_plan(self) -> None:
        """ADR draft is generated from spec and plan data."""
        spec = SpecData(
            title="Test Feature",
            goal="Reduce bloat",
            architecture="Three-layer model",
            decisions=["Use mirroring"],
        )
        plan = PlanData(
            goal="Implement feature",
            chunks=[
                ChunkData(
                    name="Catalog",
                    file_paths=["src/sync.py"],
                    criteria=["Works"],
                ),
                ChunkData(
                    name="Mirror",
                    file_paths=["src/sync.py"],
                    criteria=["Mirrors"],
                ),
            ],
        )
        adr = generate_adr_draft(spec, plan, lane="heavy", semver="0.17.0")
        self.assertEqual(adr.id, "ADR-0.17.0")
        self.assertEqual(adr.title, "Test Feature")
        self.assertEqual(adr.lane, "heavy")
        self.assertEqual(len(adr.checklist), 2)
        self.assertIn("Catalog", adr.checklist[0])
        self.assertEqual(len(adr.obpis), 2)
        self.assertEqual(adr.obpis[0].parent, "ADR-0.17.0")


class TestMapCommitsToChunks(unittest.TestCase):
    def test_map_by_file_overlap(self) -> None:
        """Commits are mapped to chunks by file-path overlap."""
        chunks = [
            ChunkData(name="A", file_paths=["src/a.py", "tests/test_a.py"]),
            ChunkData(name="B", file_paths=["src/b.py"]),
        ]
        commits = [
            CommitData(
                sha="aaa",
                message="feat A",
                files=["src/a.py"],
                date="2026-03-15",
            ),
            CommitData(
                sha="bbb",
                message="feat B",
                files=["src/b.py"],
                date="2026-03-15",
            ),
        ]
        mapping = map_commits_to_chunks(commits, chunks)
        self.assertEqual(mapping[0], [commits[0]])
        self.assertEqual(mapping[1], [commits[1]])

    def test_unmapped_commits_in_last_bucket(self) -> None:
        """Commits matching no chunk go to unmapped list."""
        chunks = [ChunkData(name="A", file_paths=["src/a.py"])]
        commits = [
            CommitData(
                sha="xxx",
                message="unrelated",
                files=["docs/readme.md"],
                date="2026-03-15",
            ),
        ]
        mapping = map_commits_to_chunks(commits, chunks)
        self.assertEqual(mapping[0], [])
        self.assertEqual(mapping[-1], [commits[0]])


class TestPresentDraft(unittest.TestCase):
    def test_present_draft_includes_adr_summary(self) -> None:
        """Presentation includes ADR ID, title, lane."""
        adr = ADRDraft(
            id="ADR-0.17.0",
            title="Test",
            semver="0.17.0",
            lane="heavy",
            intent="G",
            decision="D",
            checklist=["OBPI-0.17.0-01: Catalog"],
            obpis=[
                OBPIDraft(
                    id="OBPI-0.17.0-01-catalog",
                    objective="Catalog",
                    parent="ADR-0.17.0",
                    item=1,
                    lane="heavy",
                )
            ],
        )
        output = present_draft(adr)
        self.assertIn("ADR-0.17.0", output)
        self.assertIn("Heavy", output)
        self.assertIn("Catalog", output)


if __name__ == "__main__":
    unittest.main()
