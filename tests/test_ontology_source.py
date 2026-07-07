"""Source-domain sensor tests (ADR-0.32.0, OBPI-0.32.0-07).

Each test derives from a brief acceptance REQ and is decorated with ``@covers``.
Source parsing is a ``SourceParser`` port fulfilled by two real adapters
(``AstSourceParser``, ``TreeSitterSourceParser``); REQ-08 pins that both adapters
satisfy the same contract, and the ``ast`` adapter proves the core runs without
tree-sitter (hexagonal rule 6).
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.ontology import source
from gzkit.ontology.model import LinkType, Provenance
from gzkit.ontology.source import AstSourceParser, TreeSitterSourceParser
from gzkit.traceability import covers
from gzkit.triangle import (
    DriftReport,
    DriftSummary,
    EdgeType,
    LinkageRecord,
    ReqEntity,
    ReqId,
    ReqStatus,
    VertexRef,
    VertexType,
    detect_drift,
)


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class TestCoversSourceAnchors(unittest.TestCase):
    """REQ-0.32.0-07-01 — @covers in product source → first-class source→REQ edges."""

    @covers("REQ-0.32.0-07-01")
    def test_covers_anchor_yields_code_origin_source_req_edge(self) -> None:
        src = (
            "from gzkit.traceability import covers\n\n"
            '@covers("REQ-0.32.0-07-01")\n'
            "def thing():\n"
            "    pass\n"
        )
        anchors = AstSourceParser().scan_anchors("mod.py", src)
        covers_anchors = [a for a in anchors if a.anchor_kind is source.AnchorKind.COVERS]

        self.assertEqual(len(covers_anchors), 1)
        anchor = covers_anchors[0]
        self.assertEqual(anchor.req_id, "REQ-0.32.0-07-01")
        self.assertEqual(anchor.source_path, "mod.py")
        self.assertEqual(anchor.line, 3)

        edge = anchor.to_edge()
        self.assertEqual(edge.source_id, "mod.py")
        self.assertEqual(edge.target_id, "REQ-0.32.0-07-01")
        self.assertEqual(edge.link_type, LinkType.COVERS)
        self.assertEqual(edge.provenance, Provenance.OBSERVED)


class TestSurfaceSourceAnchors(unittest.TestCase):
    """REQ-0.32.0-07-02 — @surface many-to-many, no REQ-existence enforcement."""

    @covers("REQ-0.32.0-07-02")
    def test_surface_is_many_to_many_and_unenforced(self) -> None:
        src = (
            '@surface("REQ-0.32.0-07-02")\n@surface("REQ-9.9.9-99-99")\ndef handler():\n    pass\n'
        )
        anchors = AstSourceParser().scan_anchors("svc.py", src)
        surface = [a for a in anchors if a.anchor_kind is source.AnchorKind.SURFACE]

        req_ids = sorted(a.req_id for a in surface)
        # Two @surface anchors on ONE unit (many-to-many), and the unknown
        # REQ-9.9.9-99-99 is retained (no decoration-time existence check).
        self.assertEqual(req_ids, ["REQ-0.32.0-07-02", "REQ-9.9.9-99-99"])
        self.assertEqual(surface[0].to_edge().link_type, LinkType.SURFACE)


class TestTreeSitterCoupling(unittest.TestCase):
    """REQ-0.32.0-07-03 — tree-sitter builds import + definition coupling edges."""

    @covers("REQ-0.32.0-07-03")
    def test_import_edge_resolves_between_source_units(self) -> None:
        edges = TreeSitterSourceParser().coupling(
            [
                ("a.py", "import b\n"),
                ("b.py", "def helper():\n    return 1\n"),
            ]
        )
        self.assertIn(
            source.CodeCouplingEdge(
                source_path="a.py",
                target="b.py",
                relation=source.CouplingRelation.IMPORTS,
                target_is_unit=True,
            ),
            edges,
        )

    @covers("REQ-0.32.0-07-03")
    def test_definition_relationship_between_units(self) -> None:
        edges = TreeSitterSourceParser().coupling(
            [
                ("b.py", "def helper():\n    return 1\n\n\nclass Widget:\n    pass\n"),
                ("c.py", "from b import helper\n"),
            ]
        )
        self.assertIn(
            source.CodeCouplingEdge(
                source_path="c.py",
                target="b.py",
                relation=source.CouplingRelation.USES_DEFINITION,
                target_is_unit=True,
                symbol="helper",
            ),
            edges,
        )

    @covers("REQ-0.32.0-07-03")
    def test_external_import_is_grammar_invoked_non_unit(self) -> None:
        edges = TreeSitterSourceParser().coupling([("z.py", "import os\n")])
        self.assertEqual(len(edges), 1)
        edge = edges[0]
        self.assertEqual(edge.source_path, "z.py")
        self.assertEqual(edge.target, "os")
        self.assertFalse(edge.target_is_unit)


class TestSourceParserPort(unittest.TestCase):
    """REQ-0.32.0-07-08 — the SourceParser port; two adapters fulfil one contract."""

    _FIXTURE = [
        (
            "b.py",
            '@surface("REQ-0.32.0-07-02")\n'
            "def helper():\n"
            "    return 1\n\n\n"
            "class Widget:\n"
            "    pass\n",
        ),
        (
            "a.py",
            "import os\n"
            "from b import helper\n\n"
            '@covers("REQ-0.32.0-07-01")\n'
            "def run():\n"
            "    return helper()\n",
        ),
    ]

    @covers("REQ-0.32.0-07-08")
    def test_ast_and_tree_sitter_adapters_agree(self) -> None:
        ast_parser = AstSourceParser()
        ts_parser = TreeSitterSourceParser()

        for unit_path, src in self._FIXTURE:
            self.assertEqual(
                ast_parser.scan_anchors(unit_path, src),
                ts_parser.scan_anchors(unit_path, src),
                msg=f"anchor disagreement on {unit_path}",
            )
        self.assertEqual(
            ast_parser.coupling(self._FIXTURE),
            ts_parser.coupling(self._FIXTURE),
        )

    @covers("REQ-0.32.0-07-08")
    def test_core_runs_on_ast_adapter_without_tree_sitter(self) -> None:
        # The core depends on the PORT: injecting the stdlib ast adapter builds a
        # working index with no tree-sitter involvement (hexagonal rule 6).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(root, "b.py", "def helper():\n    return 1\n")
            _write(
                root,
                "a.py",
                'import b\n\n\n@covers("REQ-0.32.0-07-01")\ndef run():\n    return b.helper()\n',
            )
            index_path = root / "idx.json"
            idx = source.build_source_anchor_index(
                root, parser=AstSourceParser(), index_path=index_path, write=True
            )
        self.assertTrue(any(e.target == "b.py" and e.target_is_unit for e in idx.coupling_edges))
        self.assertIn("REQ-0.32.0-07-01", {a.req_id for a in idx.anchors})


class TestSourceAnchorIndex(unittest.TestCase):
    """REQ-0.32.0-07-04 — deterministic source_anchors.json that round-trips."""

    @covers("REQ-0.32.0-07-04")
    def test_index_writes_deterministically_and_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(
                root,
                "pkg/mod.py",
                '@covers("REQ-0.32.0-07-01")\n@surface("REQ-0.32.0-07-02")\ndef go():\n    pass\n',
            )
            index_path = root / "source_anchors.json"
            idx = source.build_source_anchor_index(root, index_path=index_path, write=True)

            self.assertTrue(index_path.exists())
            index_path2 = root / "again.json"
            idx2 = source.build_source_anchor_index(root, index_path=index_path2, write=True)
            self.assertEqual(idx2, idx)
            self.assertEqual(
                index_path.read_text(encoding="utf-8"),
                index_path2.read_text(encoding="utf-8"),
            )

            loaded = source.load_source_anchor_index(index_path)

        self.assertEqual(loaded, idx)
        self.assertEqual(source.SourceAnchorIndex.model_validate_json(idx.model_dump_json()), idx)
        self.assertEqual(
            [a.req_id for a in idx.anchors_for("REQ-0.32.0-07-01")], ["REQ-0.32.0-07-01"]
        )
        self.assertEqual(len(idx.edges), len(idx.anchors))


class TestOrphanGapDetection(unittest.TestCase):
    """REQ-0.32.0-07-05 — orphan gaps: uncovered REQs + unknown anchor REQs."""

    @covers("REQ-0.32.0-07-05")
    def test_orphan_and_unknown_symmetry(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _write(
                root,
                "mod.py",
                '@covers("REQ-0.32.0-07-01")\n@covers("REQ-9.9.9-99-99")\ndef go():\n    pass\n',
            )
            known = {"REQ-0.32.0-07-01", "REQ-0.32.0-07-02"}
            report = source.detect_orphan_gaps(root, known_reqs=known)

        self.assertEqual(report.orphan_reqs, ("REQ-0.32.0-07-02",))
        self.assertEqual(report.unknown_anchor_reqs, ("REQ-9.9.9-99-99",))


class TestDetectDriftSubgraphView(unittest.TestCase):
    """REQ-0.32.0-07-06 — detect_drift re-expressed as a behavior-preserving view."""

    def _fixture(self) -> tuple[list[ReqEntity], list[LinkageRecord], list[VertexRef]]:
        reqs = [
            ReqEntity(
                id=ReqId.parse("REQ-0.32.0-07-01"),
                description="known covered req",
                status=ReqStatus.UNCHECKED,
                parent_obpi="OBPI-0.32.0-07",
            )
        ]
        linkage = [
            LinkageRecord(
                source=VertexRef(vertex_type=VertexType.TEST, identifier="t_cov"),
                target=VertexRef(vertex_type=VertexType.SPEC, identifier="REQ-0.32.0-07-01"),
                edge_type=EdgeType.COVERS,
            ),
            LinkageRecord(
                source=VertexRef(vertex_type=VertexType.TEST, identifier="t_orphan"),
                target=VertexRef(vertex_type=VertexType.SPEC, identifier="REQ-9.9.9-99-99"),
                edge_type=EdgeType.COVERS,
            ),
        ]
        changed = [VertexRef(vertex_type=VertexType.CODE, identifier="foo")]
        return reqs, linkage, changed

    @covers("REQ-0.32.0-07-06")
    def test_detect_drift_matches_golden_report(self) -> None:
        reqs, linkage, changed = self._fixture()
        report = detect_drift(reqs, linkage, changed, scan_timestamp="2026-07-06T00:00:00Z")

        expected = DriftReport(
            unlinked_specs=[],
            orphan_tests=["REQ-9.9.9-99-99"],
            unjustified_code_changes=["foo"],
            summary=DriftSummary(
                unlinked_spec_count=0,
                orphan_test_count=1,
                unjustified_code_change_count=1,
                total_drift_count=2,
            ),
            scan_timestamp="2026-07-06T00:00:00Z",
        )
        self.assertEqual(report, expected)

    @covers("REQ-0.32.0-07-06")
    def test_linkage_absorbed_into_ontology_source_edges(self) -> None:
        _reqs, linkage, _changed = self._fixture()
        edges = source.source_subgraph_edges(linkage)
        covers_edges = [e for e in edges if e.link_type == LinkType.COVERS]
        self.assertEqual(len(covers_edges), 2)
        self.assertTrue(all(e.provenance == Provenance.OBSERVED for e in covers_edges))
        self.assertIn("REQ-0.32.0-07-01", {e.target_id for e in covers_edges})


# REQ-0.32.0-07-07 [SUPPORT] — the tree-sitter dependency declaration — is
# deliberately NOT covered by a @covers test: per .gzkit/rules/tests.md a SUPPORT
# REQ proves via ledger event + structural validator (gz validate --documents +
# the artifact_edited event citing this brief), never a unit test.


if __name__ == "__main__":
    unittest.main()
