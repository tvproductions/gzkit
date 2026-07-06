"""REQ-derived tests for the Harness-Purity fence (OBPI-0.32.0-01).

Assertions derive from the brief's Acceptance Criteria REQ-0.32.0-01-03, not
from a run of the implementation.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.ontology.model import ObjectType, OntologyNode, Ownership, Plane
from gzkit.ontology.purity import audit_ontology_purity, harness_purity_violations
from gzkit.traceability import covers


class TestHarnessPurityFence(unittest.TestCase):
    """REQ-0.32.0-01-03: refuse a product object placed in ownership:harness."""

    @covers("REQ-0.32.0-01-03")
    def test_product_type_in_harness_is_refused(self) -> None:
        # A gzkit product object (CliVerb) illegally tagged ownership:harness.
        node = OntologyNode(
            node_id="illegal",
            object_type=ObjectType.CLI_VERB,
            ownership=Ownership.HARNESS,
            plane=Plane.PRODUCT,
        )
        violations = harness_purity_violations([node])
        self.assertTrue(violations, "product-in-harness node must be refused")
        self.assertEqual(violations[0].type, "ontology_purity")

    @covers("REQ-0.32.0-01-03")
    def test_harness_legal_universal_object_passes(self) -> None:
        # An ADR is a GovZero-universal type — legal at ownership:harness.
        node = OntologyNode(
            node_id="adr-1",
            object_type=ObjectType.ADR,
            ownership=Ownership.HARNESS,
            plane=Plane.PROCESS,
        )
        self.assertEqual(harness_purity_violations([node]), [])

    @covers("REQ-0.32.0-01-03")
    def test_seated_registry_is_pure(self) -> None:
        # The committed OBJECT_TYPE_REGISTRY must itself be Harness-Purity clean.
        self.assertEqual(audit_ontology_purity(Path(".")), [])


if __name__ == "__main__":
    unittest.main()
