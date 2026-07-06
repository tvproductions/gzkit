"""OKF open-absorption into the ontology corpus subgraph (ADR-0.32.0, OBPI-05).

Reads the generated OKF orientation bundle (``.gzkit/governance/knowledge/``,
ADR-0.30.0) READ-ONLY and absorbs each ``type``-bearing concept document into a
``Doc`` node whose ``subtype`` echoes the source OKF ``type`` frontmatter value
VERBATIM, plus a ``links_to`` ``OntologyEdge`` per markdown link in the body.

Open-absorption posture (parent ADR § Boundary Invariants #5; OKF ADR-0.30.0
BI-1/BI-3), load-bearing:

  - ``subtype`` is the OKF ``type`` byte-for-byte — no normalization, no mapping.
  - NO closed ``type`` set / subset-validator exists here — an unknown ``type``
    is not an error (BI-3), and no OKF frontmatter/link is consumed as
    enforcement evidence (BI-1). The absorption only populates the derived
    Tier-B ontology.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict

from gzkit.ontology.model import (
    OBJECT_TYPE_REGISTRY,
    LinkType,
    ObjectType,
    OntologyEdge,
    OntologyNode,
    Provenance,
)

__all__ = ["Doc", "absorb_okf_bundle", "doc_from_concept"]

# Inline markdown link: ``[text](target)`` — the human-navigable edge the OKF
# generator writes (``Canonical source: [name](ref)``) and index/authored nodes
# carry. Captures the target ref verbatim; no resolution/normalization (the
# open-absorption posture keeps the ref as authored).
_MD_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

_FRONTMATTER_FENCE = "---\n"


class Doc(BaseModel):
    """An OKF-absorbed documentation node.

    Subsumption over a parallel model (hexagonal rule #8): a ``Doc`` REUSES the
    typed ``OntologyNode`` (``object_type=Doc``) for identity/typing and adds only
    the OKF-specific enrichment — ``subtype`` (OKF ``type`` verbatim) and the
    source ``path``. It does not re-type the node's axes.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    node: OntologyNode
    subtype: str
    path: str

    @property
    def id(self) -> str:
        """The Doc's node identity — its OKF source path."""
        return self.node.node_id


def doc_from_concept(frontmatter: dict[str, Any], path: str) -> Doc:
    """Build a ``Doc`` from one concept doc's frontmatter + source path.

    ``subtype`` is the OKF ``type`` value VERBATIM (REQ-01); any non-empty
    ``type`` is accepted with no closed-set membership check (REQ-02).
    """
    ownership, plane = OBJECT_TYPE_REGISTRY[ObjectType.DOC]
    node = OntologyNode(node_id=path, object_type=ObjectType.DOC, ownership=ownership, plane=plane)
    return Doc(node=node, subtype=frontmatter["type"], path=path)


def _split_frontmatter(text: str) -> tuple[dict[str, Any], str] | None:
    """Return ``(frontmatter, body)`` for a ``---``-fenced doc, else ``None``."""
    if not text.startswith(_FRONTMATTER_FENCE):
        return None
    _, fm_text, body = text.split(_FRONTMATTER_FENCE, 2)
    frontmatter = yaml.safe_load(fm_text) or {}
    return frontmatter, body


def _links_to_edges(doc: Doc, body: str) -> list[OntologyEdge]:
    """One ``links_to`` edge per markdown link in ``body`` (REQ-03).

    ``provenance`` is ``INTENT`` — the links are authored in the concept doc.
    Advisory-vs-binding is derived downstream from the ``Doc`` source endpoint
    type, so the edge auto-honors OKF BI-1 (no OKF link read as authority).
    """
    return [
        OntologyEdge(
            source_id=doc.id,
            target_id=match.group(1),
            link_type=LinkType.LINKS_TO,
            provenance=Provenance.INTENT,
        )
        for match in _MD_LINK.finditer(body)
    ]


def absorb_okf_bundle(bundle_dir: str | Path) -> tuple[list[Doc], list[OntologyEdge]]:
    """Absorb every ``type``-bearing concept doc in ``bundle_dir`` (READ-ONLY).

    Walks ``*.md`` in sorted (deterministic) order; each doc carrying a non-empty
    ``type`` frontmatter becomes a ``Doc`` (subtype verbatim) with a ``links_to``
    edge per body markdown link. Files are only read — never written.
    """
    root = Path(bundle_dir)
    docs: list[Doc] = []
    edges: list[OntologyEdge] = []
    for md_path in sorted(root.glob("*.md")):
        split = _split_frontmatter(md_path.read_text(encoding="utf-8"))
        if split is None:
            continue
        frontmatter, body = split
        if not frontmatter.get("type"):  # non-concept doc — nothing to absorb
            continue
        doc = doc_from_concept(frontmatter, md_path.as_posix())
        docs.append(doc)
        edges.extend(_links_to_edges(doc, body))
    return docs, edges
