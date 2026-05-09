"""Authoring-time complexity guidance surface (ADR-0.0.30).

OBPI-0.0.30-03 lands the ``AuthoringHint`` data contract and the
``analyze`` engine that wraps the ADR-0.0.29-02 advisor diagnosis engine
and projects ``advise``-band crossings into authoring-time hints.

The projection direction is fixed: ``AdvisorDiagnosis`` -> ``AuthoringHint``
(full -> light). There is no reverse projection.
"""
