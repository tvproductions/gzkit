"""Complexity advisor package — diagnosis schema and downstream surfaces (ADR-0.0.29).

Re-exports all five public symbols from :mod:`gzkit.complexity.advisor.diagnosis`
so downstream consumers (engine OBPI-02, CLI OBPI-03) can import directly from
``gzkit.complexity.advisor``.
"""

from gzkit.complexity.advisor.diagnosis import (
    AdvisorDiagnosis,
    DoctrinalFrame,
    IntrinsicAttestationRef,
    ProofRange,
    RefactorArchetype,
)

__all__ = [
    "AdvisorDiagnosis",
    "DoctrinalFrame",
    "IntrinsicAttestationRef",
    "ProofRange",
    "RefactorArchetype",
]
