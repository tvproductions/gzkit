"""REQ scope discipline taxonomy models (ADR-0.0.59 Decision item 2).

Defines the three-kind taxonomy (BEHAVIOR / SUPPORT / STRUCTURAL_FENCE) and
the proof-channel mapping used by gz validate --req-kind-discipline.

Separate from triangle.py's ReqKind(CODE, DOC) which owns the pre-ADR-0.0.59
binary testable/doc classification used by the traceability layer.
"""

from __future__ import annotations

import enum

from pydantic import BaseModel, ConfigDict, Field


class ReqKind(enum.StrEnum):
    """Three-kind taxonomy for OBPI brief acceptance-criteria REQs."""

    BEHAVIOR = "BEHAVIOR"
    SUPPORT = "SUPPORT"
    STRUCTURAL_FENCE = "STRUCTURAL-FENCE"


class ProofChannel(enum.StrEnum):
    """Proof channel paired 1:1 with each ReqKind."""

    TEST_COVERS = "TEST_COVERS"
    LEDGER_PLUS_VALIDATOR = "LEDGER_PLUS_VALIDATOR"
    PARENT_ADR_INVARIANT = "PARENT_ADR_INVARIANT"


_KIND_TO_CHANNEL: dict[ReqKind, ProofChannel] = {
    ReqKind.BEHAVIOR: ProofChannel.TEST_COVERS,
    ReqKind.SUPPORT: ProofChannel.LEDGER_PLUS_VALIDATOR,
    ReqKind.STRUCTURAL_FENCE: ProofChannel.PARENT_ADR_INVARIANT,
}


class ReqClassification(BaseModel):
    """Classification record for a single REQ within an OBPI brief."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str = Field(..., description="REQ identifier (e.g. REQ-0.0.59-02-01)")
    kind: ReqKind = Field(..., description="One of BEHAVIOR / SUPPORT / STRUCTURAL-FENCE")
    proof_channel: ProofChannel = Field(..., description="Proof channel paired with kind")
    proof_status: str = Field(..., description="pass / fail / missing-citation")

    @classmethod
    def kind_to_channel(cls, kind: ReqKind) -> ProofChannel:
        """Return the canonical proof channel for a given REQ kind."""
        return _KIND_TO_CHANNEL[kind]
