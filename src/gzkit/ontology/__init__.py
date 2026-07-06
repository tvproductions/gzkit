"""gzkit ontology — object/link plane (ADR-0.32.0, OBPI-0.32.0-01).

The typed object/link model layer of the gzkit ontology: frozen Pydantic
``OntologyNode``/``OntologyEdge`` models, the closed ``LinkType``/``Ownership``/
``Plane``/``ObjectType`` taxonomies, the total ``OBJECT_TYPE_REGISTRY``
two-axis classification, and the Harness-Purity validator.

This package ships ONLY the model layer + purity fence. The networkx graph
substrate, domain projections, and ``gz ontology`` operator verbs are later
OBPIs in ADR-0.32.0.
"""
