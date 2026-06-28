"""Pydantic model for static theater-signature findings (ADR-0.0.73 channel 1).

The static analyzer (``gzkit.governance.trust_audits.theater_signature_scan``)
emits one ``TheaterSignatureFinding`` per detected theater signature in QC-step
validator source. Channel 1 of the qc-binding antibody renders these into
``QCStep.theater_flags`` at audit time, replacing the inert self-declaration
model with a derived one (GHI #657).

All models use ConfigDict(frozen=True, extra="forbid") per .gzkit/rules/models.md.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TheaterSignatureFinding(BaseModel):
    """One statically-detected theater signature in a QC-step's validator source."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    signature: str = Field(
        ..., description="The detected theater signature (a member of THEATER_SIGNATURES)"
    )
    file_path: str = Field(..., description="Relative path from project root (posix)")
    line_number: int = Field(..., description="Line number of the matched node")
    function_name: str = Field(..., description="Name of the enclosing function")
    evidence: str = Field(..., description="The concrete node text / why it matched")
