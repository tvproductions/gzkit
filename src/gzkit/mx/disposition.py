"""MX disposition handler — the single level→route matrix (ADR-0.0.74 item 12).

Pure matrix: no marker awareness, no guard-name state. The shared checkpoint
(checkpoint.resolve) applies under-marker demotion and gate5_invariants pinning
before calling route().

The grounding line splits the matrix into two bands:

- **Grounding band** (``>= ERROR``): CRITICAL and ERROR route to a *defect*
  airlock — the hangar and the GHI-fix path — and block.
- **V.I.B.E.S.-management band** (``< ERROR``): WARNING, NOTICE, INFO, and
  DEBUG are visible-but-non-grounding, because you cannot fail-close on
  stochastic drift the way you fail-close on a broken build. The sub-grounding
  routes are the vibing ladder in descending urgency:

  * ``NOTICE`` → drift / Chores drain — a vibe requiring **escalation**;
    surfaced via the arb receipts and the insights log, then drained to Chores.
  * ``INFO`` → track — a vibe requiring **tracking** for long-term improvement
    or refactoring; also the channel for *inherent model behavior that can't be
    changed, only influenced* — you don't block on a model trait you can't fix,
    you track it to influence the governance around it.
  * ``DEBUG`` → steering — a **verbose mode** that pre-emptively **steers**
    agents away from V.I.B.E.S. before the vibe occurs; not a defect.

This band is gzkit's purpose — *make stochastic LLM vibing structurally inert*
— expressed as a severity ladder rather than a single block/allow flag.
"""

from __future__ import annotations

from enum import StrEnum

from gzkit.mx import levels


class Route(StrEnum):
    # Grounding band (>= ERROR): routes to a defect airlock, blocks.
    AOG_MX_HANGAR = "aog-mx-hangar"  # CRITICAL — ground the session into the hangar
    BLOCK_GHI_FIX = "block-ghi-fix"  # ERROR — block/ground, repair via a GHI direct fix
    # V.I.B.E.S.-management band (< ERROR): visible-but-non-grounding (see docstring).
    REFACTOR_CHORES = "refactor-chores"  # WARNING — design vibed: refactor to Chores
    DRIFT_DRAIN = "drift-drain"  # NOTICE — vibe requiring escalation (arb / insights)
    TRACK = "track"  # INFO — vibe requiring tracking (incl. inherent model behavior)
    STEERING = "steering"  # DEBUG — verbose mode steering agents away from V.I.B.E.S.
    ADVISORY = "advisory"  # under-marker demotion sentinel (non-floor demotes here)


_MATRIX: dict[int, Route] = {
    levels.CRITICAL: Route.AOG_MX_HANGAR,
    levels.ERROR: Route.BLOCK_GHI_FIX,
    levels.WARNING: Route.REFACTOR_CHORES,
    levels.NOTICE: Route.DRIFT_DRAIN,
    levels.INFO: Route.TRACK,
    levels.DEBUG: Route.STEERING,
}


def route(level: int) -> Route:
    """Map *level* to its ADR § Decision item 12 matrix route."""
    return _MATRIX.get(level, Route.TRACK)


# Grounding routes derived from the single matrix + levels.grounds — not a second
# hand-maintained list (parent ADR Boundary Invariant #2: one severity authority).
# ADVISORY is absent from the matrix, so the under-marker demotion sentinel never
# grounds — exactly the warn-only semantics demotion is meant to produce.
_GROUNDING_ROUTES: frozenset[Route] = frozenset(
    route_ for level, route_ in _MATRIX.items() if levels.grounds(level)
)


def grounds(route: Route) -> bool:
    """Return True iff *route* blocks (grounds) — the grounding band (>= ERROR).

    The consumer-facing counterpart to :func:`levels.grounds`: a guard holding a
    Route resolved by :func:`checkpoint.resolve` asks this whether to fail-closed,
    rather than re-deriving the level→route matrix at the call-site.
    """
    return route in _GROUNDING_ROUTES
