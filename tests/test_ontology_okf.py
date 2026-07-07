"""REQ tests for OKF open-absorption (ADR-0.32.0, OBPI-0.32.0-05).

Each test derives its assertion from an OBPI brief acceptance criterion, not from
a run of the implementation.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.ontology.model import LinkType, ObjectType
from gzkit.ontology.okf import Doc, absorb_okf_bundle, doc_from_concept
from gzkit.traceability import covers

_CONCEPT = """---
type: {type}
title: {title}
---

# {title}

Canonical source: [{name}]({link})
"""


def _write_concept(
    out: Path, slug: str, *, doc_type: str = "doctrine", link: str = "../src/x.md"
) -> None:
    out.joinpath(f"{slug}.md").write_text(
        _CONCEPT.format(type=doc_type, title=slug, name=f"{slug}.md", link=link),
        encoding="utf-8",
    )


class TestDocFromConcept(unittest.TestCase):
    @covers("REQ-0.32.0-05-01")
    def test_subtype_is_okf_type_verbatim(self) -> None:
        """REQ-01: Doc.subtype == source OKF `type`, byte-for-byte, no mapping."""
        doc = doc_from_concept({"type": "doctrine"}, "docs/a.md")
        self.assertEqual(doc.subtype, "doctrine")

    @covers("REQ-0.32.0-05-01")
    def test_subtype_not_normalized(self) -> None:
        """REQ-01: mixed-case / spaced `type` carried verbatim (no lowercasing)."""
        doc = doc_from_concept({"type": "Runbook Concept"}, "docs/b.md")
        self.assertEqual(doc.subtype, "Runbook Concept")

    @covers("REQ-0.32.0-05-02")
    def test_unknown_type_tolerated(self) -> None:
        """REQ-02: an arbitrary never-registered `type` yields a Doc, raises nothing."""
        doc = doc_from_concept({"type": "never-registered-type"}, "docs/c.md")
        self.assertIsInstance(doc, Doc)
        self.assertEqual(doc.subtype, "never-registered-type")
        self.assertEqual(doc.node.object_type, ObjectType.DOC)


class TestAbsorbBundle(unittest.TestCase):
    @covers("REQ-0.32.0-05-03")
    def test_links_to_edge_per_markdown_link(self) -> None:
        """REQ-03: each body markdown link emits a links_to edge Doc->target."""
        with TemporaryDirectory() as tmp:
            out = Path(tmp)
            _write_concept(out, "alpha", link="../src/alpha_source.md")
            docs, edges = absorb_okf_bundle(out)
            self.assertEqual([d.subtype for d in docs], ["doctrine"])
            links_to = [e for e in edges if e.link_type == LinkType.LINKS_TO]
            self.assertEqual(len(links_to), 1)
            self.assertEqual(links_to[0].source_id, docs[0].id)
            self.assertEqual(links_to[0].target_id, "../src/alpha_source.md")

    @covers("REQ-0.32.0-05-02")
    def test_bundle_unknown_type_not_rejected(self) -> None:
        """REQ-02: a concept doc with an unregistered `type` is absorbed, not dropped."""
        with TemporaryDirectory() as tmp:
            out = Path(tmp)
            _write_concept(out, "weird", doc_type="galactic-charter")
            docs, _edges = absorb_okf_bundle(out)
            self.assertEqual([d.subtype for d in docs], ["galactic-charter"])


class TestOkfCompositionLinkResolution(unittest.TestCase):
    """GHI #674: intra-bundle Doc->Doc links_to edges resolve into the composed graph."""

    @covers("REQ-0.32.0-05-03")
    def test_intra_bundle_doc_link_imaged_in_graph(self) -> None:
        """A concept doc linking a sibling concept doc yields a links_to edge
        between their Doc nodes in the composed graph. The raw markdown ref
        (./beta.md) resolves to the sibling's absolute node_id (GHI #674)."""
        from gzkit.ontology.graph import OntologyGraph
        from gzkit.ontology.unified import _compose_okf

        with TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            _write_concept(bundle, "alpha", link="./beta.md")
            _write_concept(bundle, "beta", link="./alpha.md")
            graph = OntologyGraph()
            _compose_okf(graph, bundle)
            alpha_id = bundle.joinpath("alpha.md").as_posix()
            beta_id = bundle.joinpath("beta.md").as_posix()
            links = {
                (e.source_id, e.target_id)
                for e in graph.edges()
                if e.link_type == LinkType.LINKS_TO
            }
            self.assertIn((alpha_id, beta_id), links)
            self.assertIn((beta_id, alpha_id), links)

    @covers("REQ-0.32.0-05-03")
    def test_cross_bundle_link_not_minted(self) -> None:
        """A ref pointing outside the bundle resolves to no Doc node and is
        dropped — never minted into a fake node (BI#1)."""
        from gzkit.ontology.graph import OntologyGraph
        from gzkit.ontology.unified import _compose_okf

        with TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            _write_concept(bundle, "alpha", link="../../docs/outside.md")
            graph = OntologyGraph()
            _compose_okf(graph, bundle)
            alpha_id = bundle.joinpath("alpha.md").as_posix()
            self.assertEqual(graph.node_ids(), [alpha_id])
            links = [e for e in graph.edges() if e.link_type == LinkType.LINKS_TO]
            self.assertEqual(links, [])


if __name__ == "__main__":
    unittest.main()
