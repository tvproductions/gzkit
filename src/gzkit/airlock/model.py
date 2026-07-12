"""Airlock seam/preflight/drift data layer (ADR-0.33.0, OBPI-0.33.0-01).

Ships the closed ``SeamKind``/``Provenance``/``Authority``/``Decision``/``Verdict``
StrEnums and the frozen ``SeamEdge``/``SeamMap``/``Preflight``/``DriftDiff``
Pydantic models. Pure shapes: no behavior, no compute, no CLI.
"""

from __future__ import annotations

import enum
from typing import Any

from pydantic import BaseModel, ConfigDict


class SeamKind(enum.StrEnum):
    """Direction a seam edge crosses the airlock: pushed out or pulled in."""

    PUSH = "push"
    PULL = "pull"


class Provenance(enum.StrEnum):
    """The vein a seam edge belongs to: declared LAW or extracted/OBSERVED fact.

    Non-erasable by construction (state-doctrine section-2 guard): L2 records what
    was encountered, so provenance is never rewritable. The closed membership below
    plus ``frozen=True`` on ``SeamEdge`` means provenance can be neither reassigned
    nor blanked after construction — the guard is enforced, not merely documented.
    """

    LAW = "LAW"
    OBSERVED = "OBSERVED"


class Authority(enum.StrEnum):
    """Who authorized the crossing: the captain directly or a delegate."""

    CAPTAIN = "captain"
    DELEGATED = "delegated"


class Decision(enum.StrEnum):
    """The captain's preflight verdict on whether the crossing may go ahead."""

    PROCEED = "proceed"
    PAUSE = "pause"
    HOLD = "hold"
    REVERT = "revert"


class Verdict(enum.StrEnum):
    """The drift adjudication for a crossing measured against its declared seam.

    ``ABORTED`` is the terminal verdict for an exit whose fallible work raised
    before the drift-diff could be measured: the transit is still paired on both
    edges (an ``airlock_out`` is booked so it matches its ``airlock_in``), but the
    adjudication never ran (GHI #679 failure-atomic accounting).
    """

    CLEAN = "clean"
    BLOCK = "block"
    SURFACE = "surface"
    RESOLVE = "resolve"
    ABORTED = "aborted"


class SeamEdge(BaseModel):
    """A single directed join between a source and target, tagged by vein and kind."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: SeamKind
    provenance: Provenance
    source: str
    target: str
    accounted: bool


class SeamMap(BaseModel):
    """Two-layer seam view carrying both senses of "seam" (parent ADR § Decision).

    ``bodies`` is seam-as-BODY: contiguous regions of similarity — the FOOTPRINT.
    ``push_edges``/``pull_edges`` are seam-as-BOUNDARY: the join. ``unaccounted``
    holds edges present but undeclared, and is never folded into the joins.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    bodies: tuple[str, ...]
    push_edges: tuple[SeamEdge, ...]
    pull_edges: tuple[SeamEdge, ...]
    unaccounted: tuple[SeamEdge, ...]


class Preflight(BaseModel):
    """A preflight snapshot: the seam map, its blast radius, authority, and decision.

    ``blast_radius`` is the DELEGATION dial, never a responsibility dial — a small,
    fully-accounted radius may auto-proceed (logged), but the captain owns every
    outcome regardless (parent ADR § Decision).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    seam_map: SeamMap
    blast_radius: int
    authority: Authority
    decision: Decision | None


class DriftDiff(BaseModel):
    """Observed drift edges, their adjudicated verdict, and any resolutions applied."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    drift: tuple[SeamEdge, ...]
    verdict: Verdict
    resolutions: tuple[str, ...]


def seam_map_json_schema() -> dict[str, Any]:
    """Return the JSON-schema projection of ``SeamMap``."""
    return SeamMap.model_json_schema()
