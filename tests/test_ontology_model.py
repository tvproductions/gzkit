"""REQ-derived tests for the ontology model layer (OBPI-0.32.0-01).

Assertions derive from the brief's Acceptance Criteria (semantics), not from a
run of the implementation.
"""

from __future__ import annotations

import enum
import json
import unittest
from pathlib import Path

import pydantic

from gzkit.ontology.model import (
    OBJECT_TYPE_REGISTRY,
    PRODUCT_OBJECT_TYPES,
    LinkType,
    ObjectType,
    OntologyEdge,
    OntologyNode,
    Ownership,
    Plane,
    ontology_node_json_schema,
)
from gzkit.schemas import load_schema
from gzkit.traceability import covers


def _valid_node(**overrides: object) -> OntologyNode:
    kwargs: dict[str, object] = {
        "node_id": "n1",
        "object_type": ObjectType.ADR,
        "ownership": Ownership.HARNESS,
        "plane": Plane.PRODUCT,
    }
    kwargs.update(overrides)
    return OntologyNode(**kwargs)  # type: ignore[arg-type]


class TestOntologyModelImmutability(unittest.TestCase):
    """REQ-0.32.0-01-01: frozen, extra-forbid models + closed LinkType."""

    @covers("REQ-0.32.0-01-01")
    def test_node_rejects_unknown_field(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            OntologyNode(
                node_id="n1",
                object_type=ObjectType.ADR,
                ownership=Ownership.HARNESS,
                plane=Plane.PRODUCT,
                bogus=1,  # type: ignore[call-arg]
            )

    @covers("REQ-0.32.0-01-01")
    def test_edge_rejects_unknown_field(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            OntologyEdge(
                source_id="a",
                target_id="b",
                link_type=LinkType.PARENT,
                bogus=1,  # type: ignore[call-arg]
            )

    @covers("REQ-0.32.0-01-01")
    def test_node_is_frozen(self) -> None:
        node = _valid_node()
        with self.assertRaises(pydantic.ValidationError):
            node.node_id = "mutated"  # type: ignore[misc]

    @covers("REQ-0.32.0-01-01")
    def test_edge_is_frozen(self) -> None:
        edge = OntologyEdge(source_id="a", target_id="b", link_type=LinkType.PARENT)
        with self.assertRaises(pydantic.ValidationError):
            edge.source_id = "mutated"  # type: ignore[misc]

    @covers("REQ-0.32.0-01-01")
    def test_linktype_is_closed_strenum(self) -> None:
        self.assertTrue(issubclass(LinkType, enum.StrEnum))
        with self.assertRaises(ValueError):
            LinkType("not_a_real_link")


_GOVERNANCE_PLANE_SCHEMA = Path(".gzkit") / "governance" / "ontology.schema.json"


def _governance_plane_members() -> set[str]:
    """The canonical `plane` enum seated in the dormant governance schema."""
    schema = json.loads(_GOVERNANCE_PLANE_SCHEMA.read_text(encoding="utf-8"))
    return set(schema["$defs"]["plane"]["enum"])


class TestOntologyTwoAxis(unittest.TestCase):
    """REQ-0.32.0-01-02: required ownership + plane axes; plane verbatim."""

    @covers("REQ-0.32.0-01-02")
    def test_ownership_axis_is_harness_or_product(self) -> None:
        self.assertEqual({o.value for o in Ownership}, {"harness", "product"})

    @covers("REQ-0.32.0-01-02")
    def test_plane_members_match_governance_schema_verbatim(self) -> None:
        # Drift between the Plane StrEnum and the canonical governance-schema
        # `$defs.plane` enum MUST fail this test (continuity-of-naming).
        self.assertEqual({p.value for p in Plane}, _governance_plane_members())
        self.assertEqual({p.value for p in Plane}, {"product", "process"})

    @covers("REQ-0.32.0-01-02")
    def test_node_requires_ownership_axis(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            OntologyNode(node_id="n1", object_type=ObjectType.ADR, plane=Plane.PRODUCT)  # type: ignore[call-arg]

    @covers("REQ-0.32.0-01-02")
    def test_node_requires_plane_axis(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            OntologyNode(node_id="n1", object_type=ObjectType.ADR, ownership=Ownership.HARNESS)  # type: ignore[call-arg]

    @covers("REQ-0.32.0-01-02")
    def test_node_rejects_out_of_enum_axis(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            OntologyNode(
                node_id="n1",
                object_type=ObjectType.ADR,
                ownership="neither",  # type: ignore[arg-type]
                plane=Plane.PRODUCT,
            )


class TestObjectTypeRegistryPartition(unittest.TestCase):
    """REQ-0.32.0-01-04: total OBJECT_TYPE_REGISTRY two-axis partition."""

    @covers("REQ-0.32.0-01-04")
    def test_registry_is_total_over_object_type(self) -> None:
        # Adding an ObjectType member without a registry entry MUST fail here.
        self.assertEqual(set(OBJECT_TYPE_REGISTRY), set(ObjectType))

    @covers("REQ-0.32.0-01-04")
    def test_each_type_maps_to_exactly_one_plane(self) -> None:
        for object_type, (ownership, plane) in OBJECT_TYPE_REGISTRY.items():
            self.assertIsInstance(ownership, Ownership, msg=f"{object_type}")
            self.assertIsInstance(plane, Plane, msg=f"{object_type}")

    @covers("REQ-0.32.0-01-04")
    def test_both_planes_are_non_empty(self) -> None:
        planes = {plane for _own, plane in OBJECT_TYPE_REGISTRY.values()}
        self.assertEqual(planes, {Plane.PRODUCT, Plane.PROCESS})

    @covers("REQ-0.32.0-01-04")
    def test_split_obeys_harness_purity(self) -> None:
        for object_type, (ownership, _plane) in OBJECT_TYPE_REGISTRY.items():
            if object_type in PRODUCT_OBJECT_TYPES:
                self.assertIs(
                    ownership,
                    Ownership.PRODUCT,
                    msg=f"{object_type} is a product type but classified {ownership}",
                )


class TestOntologyNodeSchemaProjection(unittest.TestCase):
    """REQ-0.32.0-01-05: committed schema is the model projection."""

    @covers("REQ-0.32.0-01-05")
    def test_committed_schema_equals_model_projection(self) -> None:
        self.assertEqual(load_schema("ontology_node"), ontology_node_json_schema())


if __name__ == "__main__":
    unittest.main()
