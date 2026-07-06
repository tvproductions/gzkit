"""Ontology object/link model layer (ADR-0.32.0, OBPI-0.32.0-01).

SKELETON — behavior deliberately absent so REQ tests red on their own
assertions (RGR negative control), filled per-behavior below.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class Ownership(enum.StrEnum):
    """Whether an object type is GovZero-universal (harness) or gzkit-specific."""

    HARNESS = "harness"
    PRODUCT = "product"


class Plane(enum.StrEnum):
    """Product plane (constrains code) or process plane (constrains governance).

    Members reproduced verbatim from the dormant governance schema
    ``.gzkit/governance/ontology.schema.json`` ``$defs.plane`` for
    continuity-of-naming (parent ADR § Decision).
    """

    PRODUCT = "product"
    PROCESS = "process"


class Provenance(enum.StrEnum):
    """The vein an edge belongs to: authored INTENT or extracted/observed fact.

    Non-erasable per the airlock two-graph doctrine (``docs/governance/
    work-phases-and-airlock.md`` § 2): a seam is the diff between the INTENT vein
    ("what ought to be touched") and the OBSERVED vein ("what is touched"), so
    every edge MUST record which vein it belongs to or the diff is uncomputable.
    Binding-vs-advisory is NOT stored here — it is derived from the intent
    endpoint's node type (REQ/ADR => binding; Doc => advisory), which auto-honors
    OKF Boundary Invariant #1 (ADR-0.30.0).
    """

    INTENT = "intent"
    OBSERVED = "observed"


class LinkType(enum.StrEnum):
    """Closed taxonomy of ontology edge relations."""

    PARENT = "parent"
    CHILD = "child"
    LINKS_TO = "links_to"
    COVERS = "covers"
    SURFACE = "surface"
    BLOCKS = "blocks"
    BLOCKED_BY = "blocked_by"
    DISCOVERED_FROM = "discovered_from"
    VALIDATES = "validates"
    ATTESTS = "attests"
    SUPERSEDES = "supersedes"


class ObjectType(enum.StrEnum):
    """Closed catalog of seated ontology object types."""

    PRD = "PRD"
    CONSTITUTION = "Constitution"
    ADR = "ADR"
    OBPI = "OBPI"
    REQ = "REQ"
    GHI = "GHI"
    RECEIPT = "Receipt"
    DOC = "Doc"
    TASK = "TASK"
    CLI_VERB = "CliVerb"
    VALIDATOR = "Validator"
    SKILL = "Skill"
    CHORE = "Chore"


class OntologyNode(BaseModel):
    """A typed ontology object: a node in the object/link plane."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    node_id: str
    object_type: ObjectType
    ownership: Ownership
    plane: Plane


class OntologyEdge(BaseModel):
    """A typed ontology relation: a directed link between two nodes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_id: str
    target_id: str
    link_type: LinkType
    provenance: Provenance


# gzkit's own product object types — never admitted to `ownership:harness`
# (parent ADR § Boundary Invariants #4, Harness purity). The single seating
# list read by both the OBJECT_TYPE_REGISTRY partition and the purity fence.
PRODUCT_OBJECT_TYPES: frozenset[ObjectType] = frozenset(
    {ObjectType.CLI_VERB, ObjectType.VALIDATOR, ObjectType.SKILL, ObjectType.CHORE}
)


# The single, total two-axis seating of every ObjectType. GovZero-universal
# corpus objects are `harness` ownership on the `process` plane (they constrain
# governance); gzkit's own product objects are `product` ownership — CliVerb and
# Validator constrain code (`product` plane), Skill and Chore constrain the
# governance workflow (`process` plane). Harness purity holds: no PRODUCT_OBJECT_TYPE
# is `harness`. Adding an ObjectType member without an entry here fails REQ-04.
OBJECT_TYPE_REGISTRY: dict[ObjectType, tuple[Ownership, Plane]] = {
    ObjectType.PRD: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.CONSTITUTION: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.ADR: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.OBPI: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.REQ: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.GHI: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.RECEIPT: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.DOC: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.TASK: (Ownership.HARNESS, Plane.PROCESS),
    ObjectType.CLI_VERB: (Ownership.PRODUCT, Plane.PRODUCT),
    ObjectType.VALIDATOR: (Ownership.PRODUCT, Plane.PRODUCT),
    ObjectType.SKILL: (Ownership.PRODUCT, Plane.PROCESS),
    ObjectType.CHORE: (Ownership.PRODUCT, Plane.PROCESS),
}


def ontology_node_json_schema() -> dict[str, Any]:
    """Return the JSON-schema projection of ``OntologyNode``."""
    return OntologyNode.model_json_schema()
