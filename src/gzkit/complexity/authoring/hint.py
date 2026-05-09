"""AuthoringHint model + projection from AdvisorDiagnosis (OBPI-0.0.30-03).

The ``AuthoringHint`` is the light-weight, authoring-time projection of
:class:`gzkit.complexity.advisor.diagnosis.AdvisorDiagnosis`. It drops fields
that are meaningful only at trigger-time (``proof`` — the developer has the
file open, location is implicit; ``intrinsic_attestation`` — authoring-time
hints precede attestation) and truncates ``doctrinal_frame.excerpt`` to a
one-line headline. The first ``ProofRange`` location is promoted to top-level
fields so a downstream IDE/CLI surface can place the hint at the correct line.

Projection direction is fixed (full -> light) per ADR-0.0.30 § Decision
rationale #1; there is no reverse projection.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gzkit.complexity.advisor.diagnosis import AdvisorDiagnosis, RefactorArchetype

__all__ = [
    "AuthoringHint",
    "project_diagnosis_to_hint",
]


class AuthoringHint(BaseModel):
    """Frozen authoring-time hint projected from an :class:`AdvisorDiagnosis`.

    Carries the smallest subset of advisor evidence the authoring surface
    needs: which metric, where it crossed in the advise band, what archetype
    matched, the one-line doctrinal headline, the recommended refactor move,
    and the file location the editor can navigate to.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric: str = Field(..., description="Complexity metric key (e.g. 'radon_cc').")
    precedence_band: Literal["approaching", "approaching_warn"] = Field(
        ...,
        description=(
            "Position within the advise band: 'approaching' for the lower "
            "portion, 'approaching_warn' for the upper (closer to the warn "
            "boundary)."
        ),
    )
    crossing_value: float = Field(
        ...,
        description="Observed metric value that triggered the hint.",
    )
    archetype: RefactorArchetype = Field(
        ...,
        description="Canonical refactor archetype most applicable to this hint.",
    )
    doctrinal_frame_headline: str = Field(
        ...,
        description="Truncated one-line excerpt of the cited doctrinal frame.",
    )
    recommended_move: str = Field(
        ...,
        description="Human-readable refactor recommendation.",
    )
    file_path: str = Field(
        ...,
        description="Source file path for the editor to navigate to.",
    )
    start_line: int = Field(..., ge=1, description="First line (1-indexed, inclusive).")
    end_line: int = Field(..., ge=1, description="Last line (1-indexed, inclusive).")

    @model_validator(mode="after")
    def _check_line_range(self) -> AuthoringHint:
        if self.end_line < self.start_line:
            msg = "end_line must be >= start_line"
            raise ValueError(msg)
        return self


def project_diagnosis_to_hint(
    diagnosis: AdvisorDiagnosis,
    *,
    precedence_band: Literal["approaching", "approaching_warn"],
) -> AuthoringHint | None:
    """Project an :class:`AdvisorDiagnosis` into an :class:`AuthoringHint`.

    Returns ``None`` when ``diagnosis.crossing_band`` is ``"warn"`` or
    ``"block"`` -- those crossings are the trigger-time advisor's
    responsibility, not the authoring-guidance surface. Returns an
    ``AuthoringHint`` only for ``"advise"``-band crossings.

    The projection drops ``proof`` (location is promoted to top-level
    fields from the first :class:`ProofRange`) and ``intrinsic_attestation``
    (not relevant authoring-time), and truncates ``doctrinal_frame.excerpt``
    to its first line as ``doctrinal_frame_headline``.
    """
    if diagnosis.crossing_band != "advise":
        return None
    first_proof = diagnosis.proof[0]
    headline = diagnosis.doctrinal_frame.excerpt.splitlines()[0]
    return AuthoringHint(
        metric=diagnosis.metric,
        precedence_band=precedence_band,
        crossing_value=diagnosis.crossing_value,
        archetype=diagnosis.archetype,
        doctrinal_frame_headline=headline,
        recommended_move=diagnosis.recommended_move,
        file_path=first_proof.file_path,
        start_line=first_proof.start_line,
        end_line=first_proof.end_line,
    )
