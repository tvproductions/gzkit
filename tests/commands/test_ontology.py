"""@covers tests for the gz ontology read-only sonar (ADR-0.32.0, OBPI-03).

Fixtures build ``OntologyGraph`` directly so the pure helpers are exercised
without a ledger; the side-effecting command handlers are driven with
``project_corpus`` / ``get_project_root`` patched to a fixture + temp root so no
test mutates the real repository (the read-only fence, REQ-08).
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import gzkit.commands.ontology as ontology
from gzkit.commands.ontology import (
    compute_reach,
    compute_seams,
    compute_trace,
    diff_snapshots,
    render_dot,
    render_sense_json,
    snapshot_of,
)
from gzkit.ontology.corpus import CorpusProjection, RebuildFidelity
from gzkit.ontology.graph import OntologyGraph
from gzkit.ontology.model import (
    LinkType,
    ObjectType,
    OntologyEdge,
    OntologyNode,
    Ownership,
    Plane,
)
from gzkit.traceability import covers


def _node(node_id: str, object_type: ObjectType = ObjectType.OBPI) -> OntologyNode:
    return OntologyNode(
        node_id=node_id,
        object_type=object_type,
        ownership=Ownership.HARNESS,
        plane=Plane.PROCESS,
    )


def _healthy_graph() -> OntologyGraph:
    """ADR with two OBPI children; every edge resolves -> zero structural seams."""
    g = OntologyGraph()
    g.add_node(_node("ADR-1", ObjectType.ADR))
    g.add_node(_node("OBPI-1"))
    g.add_node(_node("OBPI-2"))
    g.add_edge(OntologyEdge(source_id="ADR-1", target_id="OBPI-1", link_type=LinkType.CHILD))
    g.add_edge(OntologyEdge(source_id="ADR-1", target_id="OBPI-2", link_type=LinkType.CHILD))
    return g


def _dangling_graph() -> OntologyGraph:
    """A CHILD edge points at a node never materialized -> exactly one seam."""
    g = OntologyGraph()
    g.add_node(_node("ADR-1", ObjectType.ADR))
    g.add_edge(OntologyEdge(source_id="ADR-1", target_id="OBPI-GHOST", link_type=LinkType.CHILD))
    return g


def _fidelity() -> RebuildFidelity:
    return RebuildFidelity.build(
        accounted=frozenset(),
        registry=frozenset(),
        replayed=frozenset(),
        latest_ts=None,
        build_ts="2026-01-01T00:00:00+00:00",
    )


def _projection(graph: OntologyGraph) -> CorpusProjection:
    return CorpusProjection(graph, {}, _fidelity())


class TestSenseSeamFloor(unittest.TestCase):
    @covers("REQ-0.32.0-03-01")
    def test_healthy_tree_has_zero_spurious_seams(self) -> None:
        # The false-positive floor: a clean tree surfaces NO structural seam,
        # so operators are never trained to mute the sonar (§ Negative #7).
        self.assertEqual(compute_seams(_healthy_graph()), [])

    @covers("REQ-0.32.0-03-01")
    def test_a_real_structural_gap_is_still_detected(self) -> None:
        # Non-vacuity: the floor is not "always []" — a genuine gap surfaces.
        seams = compute_seams(_dangling_graph())
        self.assertEqual(len(seams), 1)

    @covers("REQ-0.32.0-03-01")
    def test_sense_exits_zero_on_a_healthy_tree(self) -> None:
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(
                ontology, "project_corpus", return_value=_projection(_healthy_graph())
            ),
            mock.patch.object(ontology, "get_project_root", return_value=Path(tmp)),
            redirect_stdout(io.StringIO()),
        ):
            ontology.ontology_sense_cmd()  # exits 0 (no SystemExit): the sonar never gates


class TestTrace(unittest.TestCase):
    @covers("REQ-0.32.0-03-02")
    def test_trace_returns_vertical_lineage_and_lateral_provenance(self) -> None:
        g = _healthy_graph()
        g.add_edge(
            OntologyEdge(source_id="OBPI-1", target_id="OBPI-1", link_type=LinkType.VALIDATES)
        )
        trace = compute_trace(g, "OBPI-1")
        assert trace is not None
        self.assertEqual(trace.ancestors, ["ADR-1"])  # vertical lineage upward
        lateral_types = {p.link_type for p in trace.lateral}
        self.assertIn("validates", lateral_types)  # lateral anchor/proof
        # edge provenance: every edge touching the node carries a reason
        self.assertTrue(trace.provenance)
        self.assertTrue(all(p.reason for p in trace.provenance))

    @covers("REQ-0.32.0-03-02")
    def test_trace_unknown_node_returns_none(self) -> None:
        self.assertIsNone(compute_trace(_healthy_graph(), "NO-SUCH-NODE"))


class TestResense(unittest.TestCase):
    @covers("REQ-0.32.0-03-03")
    def test_diff_reports_added_and_removed(self) -> None:
        before = snapshot_of(_healthy_graph())
        mutated = _healthy_graph()
        mutated.add_node(_node("OBPI-3"))  # add a node
        mutated.add_edge(
            OntologyEdge(source_id="ADR-1", target_id="OBPI-3", link_type=LinkType.CHILD)
        )
        after = snapshot_of(mutated)
        diff = diff_snapshots(before, after)
        self.assertIn("OBPI-3", diff.added_nodes)
        self.assertIn("ADR-1|OBPI-3|child", diff.added_edges)
        self.assertEqual(diff.removed_nodes, [])

    @covers("REQ-0.32.0-03-03")
    def test_resense_diffs_against_the_persisted_baseline(self) -> None:
        # End-to-end airlock gate: sense seeds a baseline; the shape mutates;
        # resense reports the delta against the prior point in time.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (
                mock.patch.object(ontology, "get_project_root", return_value=root),
                mock.patch.object(
                    ontology, "project_corpus", return_value=_projection(_healthy_graph())
                ),
                redirect_stdout(io.StringIO()),
            ):
                ontology.ontology_sense_cmd()  # persists last_sweep.json baseline
            mutated = _healthy_graph()
            mutated.add_node(_node("OBPI-NEW"))
            buf = io.StringIO()
            with (
                mock.patch.object(ontology, "get_project_root", return_value=root),
                mock.patch.object(ontology, "project_corpus", return_value=_projection(mutated)),
                redirect_stdout(buf),
            ):
                ontology.ontology_resense_cmd(as_json=True)
            diff = json.loads(buf.getvalue())
            self.assertIn("OBPI-NEW", diff["added_nodes"])

    @covers("REQ-0.32.0-03-03")
    def test_resense_with_no_baseline_exits_zero(self) -> None:
        with (
            tempfile.TemporaryDirectory() as tmp,
            mock.patch.object(ontology, "get_project_root", return_value=Path(tmp)),
            mock.patch.object(
                ontology, "project_corpus", return_value=_projection(_healthy_graph())
            ),
            redirect_stdout(io.StringIO()),
        ):
            ontology.ontology_resense_cmd()  # no baseline -> clean message, exit 0


class TestSeams(unittest.TestCase):
    @covers("REQ-0.32.0-03-04")
    def test_seams_lists_the_dangling_edge(self) -> None:
        seams = compute_seams(_dangling_graph())
        self.assertEqual(len(seams), 1)
        self.assertEqual(seams[0].target_id, "OBPI-GHOST")
        self.assertEqual(seams[0].missing_endpoint, "target")


class TestReach(unittest.TestCase):
    @covers("REQ-0.32.0-03-05")
    def test_reach_returns_transitive_dependents(self) -> None:
        g = OntologyGraph()
        for nid in ("A", "B", "C"):
            g.add_node(_node(nid))
        g.add_edge(OntologyEdge(source_id="A", target_id="B", link_type=LinkType.CHILD))
        g.add_edge(OntologyEdge(source_id="B", target_id="C", link_type=LinkType.CHILD))
        self.assertEqual(compute_reach(g, "A"), ["B", "C"])

    @covers("REQ-0.32.0-03-05")
    def test_reach_unknown_node_returns_none(self) -> None:
        self.assertIsNone(compute_reach(_healthy_graph(), "NO-SUCH-NODE"))


class TestJsonAndDotOutput(unittest.TestCase):
    @covers("REQ-0.32.0-03-06")
    def test_sense_json_includes_rebuild_fidelity_selfreport(self) -> None:
        result = render_sense_json(_projection(_healthy_graph()))
        self.assertEqual(result["coverage"], "structural")
        self.assertIn("fidelity", result)
        self.assertIn("complete", result["fidelity"])
        self.assertIn("fresh", result["fidelity"])
        self.assertIn("unaccounted_event_types", result["fidelity"])

    @covers("REQ-0.32.0-03-06")
    def test_dot_emits_a_graphviz_digraph(self) -> None:
        dot = render_dot(_healthy_graph())
        self.assertTrue(dot.lstrip().startswith("digraph"))
        self.assertIn('"ADR-1" -> "OBPI-1"', dot)


class TestReadOnlyFence(unittest.TestCase):
    """Defense-in-depth for the read-only fence (REQ-08 / Boundary Invariant #2).

    REQ-08 is a STRUCTURAL-FENCE proven by the parent-ADR invariant (no ``@covers``),
    so this undecorated regression guard is not its formal proof channel — it exists
    so a *future* edit that adds a ledger/graph-state write to a handler is caught
    mechanically rather than only at ADR closeout. The sole legitimate write is the
    Tier-B ``last_sweep.json`` derived cache.
    """

    def test_sense_writes_only_the_last_sweep_cache(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (
                mock.patch.object(ontology, "get_project_root", return_value=root),
                mock.patch.object(
                    ontology, "project_corpus", return_value=_projection(_healthy_graph())
                ),
                redirect_stdout(io.StringIO()),
            ):
                ontology.ontology_sense_cmd()
            written = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
            self.assertEqual(written, [".gzkit/ontology/last_sweep.json"])


if __name__ == "__main__":
    unittest.main()
