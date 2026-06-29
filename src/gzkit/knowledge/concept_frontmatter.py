"""OKF concept-document frontmatter model (ADR-0.30.0, OBPI-0.30.0-01).

The typed contract for a single OKF concept document's YAML frontmatter,
following the Open Knowledge Format v0.1 draft. The downstream bundle generator
(OBPI-02) and the ``--okf-conformance`` validator (OBPI-03) both build on this
one source of truth.

OKF posture (parent ADR Boundary Invariant 3) — load-bearing:
  - ``type`` is the ONLY required field; it is a FREE string, never a closed
    enum. An unrecognized ``type`` value is NOT an error.
  - Producer-defined (unknown) frontmatter keys are accepted, not rejected.

This is why the model uses ``extra="allow"`` — a DELIBERATE, ADR-mandated
departure from the project default ``extra="forbid"`` in
``.gzkit/rules/models.md``. Do NOT "correct" it back to ``forbid``: strict
rejection of unknown fields/types would betray the OKF posture and turn an
external convention back into a bespoke closed taxonomy (the smell Movement I
cut). The model stays ``frozen=True`` for snapshot immutability per the
immutable-domain-model convention (frozen + extra="allow" is supported in
Pydantic v2).

STRUCTURAL-FENCE (parent ADR Boundary Invariant 1): this model is a data
contract only. It MUST NEVER be consumed as enforcement evidence by any
``gz validate`` / gates / closeout surface — OKF orients, it never proves.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

__all__ = ["ConceptFrontmatter"]


class ConceptFrontmatter(BaseModel):
    """Typed OKF concept-document frontmatter (required ``type``; rest optional).

    Posture-tolerant by design: unknown producer-defined fields are retained
    (``extra="allow"``) and ``type`` accepts any non-empty string value.
    """

    # extra="allow": OKF posture (Boundary Invariant 3) — ADR-mandated departure
    # from the models.md extra="forbid" default. See module docstring.
    model_config = ConfigDict(frozen=True, extra="allow")

    type: str = Field(
        ...,
        min_length=1,
        description=(
            "OKF concept type — the ONE required field. Free-form string, never "
            "a closed enum; unknown values are valid (posture tolerance)."
        ),
    )
    title: str | None = Field(None, description="Human-readable document title.")
    description: str | None = Field(None, description="Short summary of the concept document.")
    resource: str | None = Field(
        None, description="Path/URI of the source resource this concept maps to."
    )
    tags: list[str] | None = Field(
        None, description="Optional free-form tags for navigation/orientation."
    )
    timestamp: str | None = Field(
        None, description="Optional authored/generated timestamp (ISO-8601 string)."
    )
