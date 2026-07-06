"""Harness-Purity validator (ADR-0.32.0 Boundary Invariant #4, OBPI-0.32.0-01).

``ownership:harness`` admits only GovZero-universal object types; gzkit's own
product objects (CliVerb/Validator/Skill/Chore) are ``ownership:product`` and
must never appear in the harness subgraph. Dispatched by
``gz validate --ontology-purity``.

SKELETON — fence deliberately absent so the REQ-0.32.0-01-03 refusal test reds
on its assertion; filled below.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.ontology.model import (
    OBJECT_TYPE_REGISTRY,
    PRODUCT_OBJECT_TYPES,
    OntologyNode,
    Ownership,
)


def harness_purity_violations(nodes: Iterable[OntologyNode]) -> list[ValidationError]:
    """Refuse any gzkit product object type placed in ``ownership:harness``."""
    return [
        ValidationError(
            type="ontology_purity",
            artifact=node.node_id,
            message=(
                f"Harness-Purity breach: product object type '{node.object_type.value}' "
                f"placed in ownership:harness; gzkit product objects are ownership:product "
                f"(ADR-0.32.0 Boundary Invariant #4)."
            ),
            field="ownership",
        )
        for node in nodes
        if node.object_type in PRODUCT_OBJECT_TYPES and node.ownership is Ownership.HARNESS
    ]


def audit_ontology_purity(project_root: Path) -> list[ValidationError]:
    """Audit the seated OBJECT_TYPE_REGISTRY for Harness-Purity violations."""
    _ = project_root
    nodes = [
        OntologyNode(
            node_id=f"seed:{object_type.value}",
            object_type=object_type,
            ownership=ownership,
            plane=plane,
        )
        for object_type, (ownership, plane) in OBJECT_TYPE_REGISTRY.items()
    ]
    return harness_purity_violations(nodes)
