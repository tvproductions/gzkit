"""Pydantic models for the historical attestation waiver list (OBPI-0.0.36-04).

This module defines the schema for data/historical_self_close_waivers.json,
which enumerates pre-doctrine receipts that would otherwise fail
gz validate --receipt-shape (ADR-0.0.36 cutoff: 2026-04-26).
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HistoricalAttestationWaiver(BaseModel):
    """One row in the historical attestation waiver list."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    receipt_id: str = Field(..., description="Ledger event ID of the waivered receipt")
    obpi_id: str = Field(..., description="OBPI that generated the receipt")
    deprecated_shape: str = Field(
        ...,
        description=(
            "Comma-separated deprecated shape labels (e.g. 'attestation_requirement: optional')"
        ),
    )
    rationale: str = Field(..., description="Why this receipt is waivered")
    added_under: str = Field(
        ...,
        description=(
            "OBPI that added this waiver entry; must be "
            "OBPI-0.0.36-04-historical-self-close-waivers"
        ),
    )


class HistoricalAttestationWaiverFile(BaseModel):
    """Container for the complete list of historical attestation waivers."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    waivers: list[HistoricalAttestationWaiver] = Field(
        ..., description="List of historical receipt waivers"
    )


__all__ = [
    "HistoricalAttestationWaiver",
    "HistoricalAttestationWaiverFile",
]
