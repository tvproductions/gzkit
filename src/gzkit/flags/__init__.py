"""Feature flag system for gzkit.

Provides typed flag models, a source-controlled registry, and a validation
pipeline. See ADR-0.0.8 for the full architecture.
"""

from gzkit.flags.models import (
    FlagCategory,
    FlagError,
    FlagEvaluation,
    FlagSpec,
    InvalidFlagValueError,
    UnknownFlagError,
)
from gzkit.flags.registry import load_registry
from gzkit.flags.service import FlagService

__all__ = [
    "FlagCategory",
    "FlagError",
    "FlagEvaluation",
    "FlagService",
    "FlagSpec",
    "InvalidFlagValueError",
    "UnknownFlagError",
    "load_registry",
]
