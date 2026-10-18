"""The maxim-13 recurrence check: when a recorded failure may become a rule.

Operator rulings 2026-10-18 (drydock RO-1), verbatim selections: '3 occurrences
(Rec.)', 'Cited records (Rec.)' and 'One lease apart (Rec.)'. A single failure is
an insight. A proposal to write it into a rule cites insight or GHI records of the
same class of failure; it qualifies when it cites at least the threshold, and every
pair of cited records is at least one session lease apart by full timestamp, so
records written inside one session count once. The proposer judges the class; this
module checks only the count and the separation.

The core takes resolved timestamps as a parameter and never reads the store or
``gh`` itself (`.gzkit/rules/hexagonal-architecture.md` rules 1 and 4); the
``gz insights recurrence`` handler is the adapter.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from itertools import combinations
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.registries import load_registry_field, registry_path

#: The registry holding the threshold (`data/recurrence_threshold.json`).
THRESHOLD_REGISTRY = "recurrence_threshold.json"

#: Used only when a project carries no registry; a present, broken one raises.
DEFAULT_MIN_OCCURRENCES = 3


class RecurrenceVerdict(BaseModel):
    """Whether a set of cited records qualifies a failure as recurring."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    met: bool = Field(..., description="Enough citations and every pair a lease apart")
    cited: int = Field(..., description="Number of cited records")
    required: int = Field(..., description="The threshold the citations must reach")
    separation_hours: float = Field(..., description="Minimum hours between any two records")
    too_close: list[tuple[str, str]] = Field(
        default_factory=list, description="Citation pairs closer than the separation"
    )


def load_min_occurrences(project_root: Path) -> int:
    """Return the recurrence threshold from the registry, or the default without one."""
    if not registry_path(project_root, THRESHOLD_REGISTRY).is_file():
        return DEFAULT_MIN_OCCURRENCES
    return int(
        load_registry_field(
            project_root, THRESHOLD_REGISTRY, "min_occurrences", DEFAULT_MIN_OCCURRENCES
        )
    )


def check_recurrence(
    cited: Mapping[str, datetime], *, min_occurrences: int, separation_hours: float
) -> RecurrenceVerdict:
    """Judge whether ``cited`` (citation → full timestamp) meets the threshold."""
    too_close = [
        (a, b)
        for (a, ta), (b, tb) in combinations(cited.items(), 2)
        if abs((ta - tb).total_seconds()) < separation_hours * 3600
    ]
    return RecurrenceVerdict(
        met=len(cited) >= min_occurrences and not too_close,
        cited=len(cited),
        required=min_occurrences,
        separation_hours=separation_hours,
        too_close=too_close,
    )
