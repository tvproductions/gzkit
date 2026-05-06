"""Advisor diagnosis schema for the gzkit complexity advisor (OBPI-0.0.29-01).

Exports five symbols consumed by downstream OBPIs in ADR-0.0.29:
- :class:`RefactorArchetype` — StrEnum with ten canonical refactor archetypes.
- :class:`DoctrinalFrame` — frozen model carrying authority, citation, and excerpt.
- :class:`ProofRange` — frozen model carrying file path and line range.
- :class:`IntrinsicAttestationRef` — forward stub for OBPI-07 attestation binding.
- :class:`AdvisorDiagnosis` — top-level frozen diagnosis container.

All models use ``ConfigDict(frozen=True, extra="forbid")`` per
``.claude/rules/models.md``. Amendments to ``RefactorArchetype`` values
require ADR-0.0.29 ceremony per § Decision rationale #2.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "AdvisorDiagnosis",
    "DoctrinalFrame",
    "IntrinsicAttestationRef",
    "ProofRange",
    "RefactorArchetype",
]


class RefactorArchetype(StrEnum):
    """Canonical ten-value refactor archetype enumeration (ADR-0.0.29 § Decision rationale #2).

    Values are snake_case to round-trip cleanly through JSON serialization
    without a ``.value`` accessor call (StrEnum emits the string value directly).
    Amendments require ADR-0.0.29 ceremony.
    """

    LONG_PARAMETER_LIST = "long_parameter_list"
    ARROWHEAD = "arrowhead"
    SWITCH_ON_TYPE = "switch_on_type"
    FEATURE_ENVY = "feature_envy"
    LARGE_CLASS = "large_class"
    DIVERGENT_CHANGE = "divergent_change"
    SHOTGUN_SURGERY = "shotgun_surgery"
    PRIMITIVE_OBSESSION = "primitive_obsession"
    DATA_CLUMPS = "data_clumps"
    MESSAGE_CHAIN = "message_chain"


class DoctrinalFrame(BaseModel):
    """Doctrinal authority, citation, and excerpt backing a refactor recommendation.

    Carries the four-authority canon (Fowler / Martin / Page-Jones / Constantine)
    as a ``Literal`` constraint so engine-layer code cannot accidentally emit
    an unrecognized authority name.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    authority: Literal["fowler", "martin", "page_jones", "constantine"] = Field(
        ...,
        description="One of the four canonical doctrinal authorities.",
    )
    citation: str = Field(
        ...,
        description="Free-form citation string (book title, chapter, page).",
    )
    excerpt: str = Field(
        ...,
        description="Brief excerpt from the cited authority supporting the diagnosis.",
    )


class ProofRange(BaseModel):
    """File-path and line-range identifying the code evidence for a diagnosis.

    ``start_line`` must be ≥ 1. ``end_line`` must be ≥ ``start_line``.
    The cross-field constraint is enforced by the ``_check_line_range``
    model validator; JSON Schema carries only per-field ``minimum: 1``
    (Draft 2020-12 has no portable cross-field comparator).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(
        ...,
        description="Relative path to the source file (from repo root).",
    )
    start_line: int = Field(
        ...,
        ge=1,
        description="First line of the proof range (1-indexed, inclusive).",
    )
    end_line: int = Field(
        ...,
        ge=1,
        description="Last line of the proof range (1-indexed, inclusive).",
    )
    ast_node_kind: str = Field(
        ...,
        description="AST node kind at this range (e.g. 'FunctionDef', 'ClassDef').",
    )

    @model_validator(mode="after")
    def _check_line_range(self) -> ProofRange:
        if self.end_line < self.start_line:
            msg = "end_line must be >= start_line"
            raise ValueError(msg)
        return self


class IntrinsicAttestationRef(BaseModel):
    """Forward stub for the intrinsic attestation reference (OBPI-07).

    OBPI-07 will extend this stub with ``reason``, ``attestor``, ``attested_at``,
    and ledger-event linkage. The single-field stub keeps ``AdvisorDiagnosis``'s
    optional field type-checkable from day one without blocking OBPI-07.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    attestation_id: str = Field(
        ...,
        description="Opaque attestation identifier; resolved by OBPI-07.",
    )


class AdvisorDiagnosis(BaseModel):
    """Top-level frozen diagnosis container (ADR-0.0.29 data contract).

    This is the data contract every downstream OBPI in ADR-0.0.29 binds
    against: engine (OBPI-02), CLI (OBPI-03), proof binding (OBPI-08),
    and intrinsic attestation (OBPI-07).

    ``proof`` is non-empty by belt-and-braces design: ``Field(min_length=1)``
    gives Pydantic 2 the declarative constraint; ``_check_proof_nonempty``
    catches edge-case looseness observed in pydantic-core 2.10–2.18 where
    ``min_length`` on tuple fields was intermittently lax.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric: str = Field(
        ...,
        description="Complexity metric key (e.g. 'radon_cc', 'radon_mi').",
    )
    crossing_band: Literal["block", "warn", "advise"] = Field(
        ...,
        description="Threshold band the metric crossed: block/warn/advise.",
    )
    crossing_value: float = Field(
        ...,
        description="Observed metric value that triggered the diagnosis.",
    )
    archetype: RefactorArchetype = Field(
        ...,
        description="Canonical refactor archetype most applicable to this diagnosis.",
    )
    doctrinal_frame: DoctrinalFrame = Field(
        ...,
        description="Doctrinal authority, citation, and excerpt backing the recommendation.",
    )
    proof: tuple[ProofRange, ...] = Field(
        ...,
        min_length=1,
        description="Non-empty tuple of file-range proof items for this diagnosis.",
    )
    recommended_move: str = Field(
        ...,
        description="Human-readable refactor recommendation (e.g. 'Introduce Parameter Object').",
    )
    intrinsic_attestation: IntrinsicAttestationRef | None = Field(
        None,
        description="Optional intrinsic attestation reference; populated by OBPI-07.",
    )

    @model_validator(mode="after")
    def _check_proof_nonempty(self) -> AdvisorDiagnosis:
        if len(self.proof) == 0:
            msg = "proof must be non-empty"
            raise ValueError(msg)
        return self
