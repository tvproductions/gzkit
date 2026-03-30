"""Flag diagnostics — stale detection, health reporting, and explain.

Implements ADR-0.0.8 checklist items #6 (stale flag detection and health
reporting) and #7 (time-bomb CI test support).  All functions are read-only;
they never modify flag values or registry entries.
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from gzkit.flags.models import FlagSpec
from gzkit.flags.service import FlagService

# Days threshold for "approaching deadline" warnings.
_APPROACHING_DAYS = 14


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


class FlagHealthSummary(BaseModel):
    """Aggregate health report for the flag registry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total: int = Field(..., description="Total number of registered flags")
    stale_count: int = Field(..., description="Flags past remove_by or review_by")
    approaching_count: int = Field(..., description="Flags within 14 days of a deadline")
    category_counts: dict[str, int] = Field(..., description="Flag count per category")
    stale_keys: list[str] = Field(..., description="Keys of stale flags")
    approaching_keys: list[str] = Field(..., description="Keys of flags approaching deadline")


class FlagExplanation(BaseModel):
    """Detailed explanation of a single flag's state."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str = Field(..., description="Flag key")
    category: str = Field(..., description="Flag category")
    default: bool = Field(..., description="Registry default value")
    current_value: bool = Field(..., description="Resolved value")
    source: str = Field(..., description="Precedence layer providing current value")
    description: str = Field(..., description="Human-readable purpose")
    owner: str = Field(..., description="Responsible party")
    review_by: date | None = Field(None, description="Review deadline")
    remove_by: date | None = Field(None, description="Removal deadline")
    days_until_review: int | None = Field(
        None, description="Days until review_by (negative = overdue)"
    )
    days_until_removal: int | None = Field(
        None, description="Days until remove_by (negative = overdue)"
    )
    is_stale: bool = Field(..., description="Whether the flag is past a deadline")


# ---------------------------------------------------------------------------
# Stale detection
# ---------------------------------------------------------------------------


def get_stale_flags(
    registry: dict[str, FlagSpec],
    *,
    as_of: date | None = None,
) -> list[FlagSpec]:
    """Return flags past their ``remove_by`` or ``review_by`` dates.

    Args:
        registry: Mapping of flag keys to FlagSpec instances.
        as_of: Reference date for staleness check.  Defaults to today.

    Returns:
        List of stale FlagSpec instances, sorted by key.
    """
    ref = as_of or date.today()
    stale: list[FlagSpec] = []
    for spec in sorted(registry.values(), key=lambda s: s.key):
        if (
            spec.remove_by is not None
            and spec.remove_by < ref
            or spec.review_by is not None
            and spec.review_by < ref
        ):
            stale.append(spec)
    return stale


# ---------------------------------------------------------------------------
# Health summary
# ---------------------------------------------------------------------------


def get_flag_health(
    registry: dict[str, FlagSpec],
    *,
    as_of: date | None = None,
) -> FlagHealthSummary:
    """Return an aggregate health summary for the flag registry.

    Args:
        registry: Mapping of flag keys to FlagSpec instances.
        as_of: Reference date.  Defaults to today.

    Returns:
        FlagHealthSummary with counts and key lists.
    """
    ref = as_of or date.today()

    category_counts: dict[str, int] = {}
    stale_keys: list[str] = []
    approaching_keys: list[str] = []

    for spec in sorted(registry.values(), key=lambda s: s.key):
        cat = spec.category.value
        category_counts[cat] = category_counts.get(cat, 0) + 1

        is_stale = False
        if (
            spec.remove_by is not None
            and spec.remove_by < ref
            or spec.review_by is not None
            and spec.review_by < ref
        ):
            is_stale = True

        if is_stale:
            stale_keys.append(spec.key)
            continue

        # Check approaching deadline (within _APPROACHING_DAYS)
        approaching = False
        if spec.remove_by is not None:
            days_left = (spec.remove_by - ref).days
            if 0 <= days_left <= _APPROACHING_DAYS:
                approaching = True
        if not approaching and spec.review_by is not None:
            days_left = (spec.review_by - ref).days
            if 0 <= days_left <= _APPROACHING_DAYS:
                approaching = True

        if approaching:
            approaching_keys.append(spec.key)

    return FlagHealthSummary(
        total=len(registry),
        stale_count=len(stale_keys),
        approaching_count=len(approaching_keys),
        category_counts=category_counts,
        stale_keys=stale_keys,
        approaching_keys=approaching_keys,
    )


# ---------------------------------------------------------------------------
# Explain
# ---------------------------------------------------------------------------


def explain_flag(key: str, service: FlagService) -> FlagExplanation:
    """Return a detailed explanation of a flag's current state.

    Args:
        key: The dotted flag key to explain.
        service: A FlagService instance for value resolution.

    Returns:
        FlagExplanation with metadata, resolved value, and staleness.

    Raises:
        UnknownFlagError: If *key* is not in the registry.
    """
    evaluation = service.evaluate(key)
    spec = service._registry[key]
    today = date.today()

    days_review: int | None = None
    if spec.review_by is not None:
        days_review = (spec.review_by - today).days

    days_removal: int | None = None
    if spec.remove_by is not None:
        days_removal = (spec.remove_by - today).days

    is_stale = False
    if (
        spec.remove_by is not None
        and spec.remove_by < today
        or spec.review_by is not None
        and spec.review_by < today
    ):
        is_stale = True

    return FlagExplanation(
        key=spec.key,
        category=spec.category.value,
        default=spec.default,
        current_value=evaluation.value,
        source=evaluation.source,
        description=spec.description,
        owner=spec.owner,
        review_by=spec.review_by,
        remove_by=spec.remove_by,
        days_until_review=days_review,
        days_until_removal=days_removal,
        is_stale=is_stale,
    )
