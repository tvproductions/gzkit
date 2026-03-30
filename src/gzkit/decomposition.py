"""Deterministic ADR decomposition helpers for OBPI planning and validation.

Pure domain logic lives in ``gzkit.core.scoring``. This module re-exports
all public symbols for backward compatibility.
"""

from gzkit.core.scoring import (
    DecompositionScorecard,
    WbsRow,
    baseline_range_for_total,
    build_checklist_seed,
    compute_scorecard,
    default_dimension_scores,
    extract_markdown_section,
    parse_checklist_items,
    parse_scorecard,
    parse_wbs_table,
)

__all__ = [
    "DecompositionScorecard",
    "WbsRow",
    "baseline_range_for_total",
    "build_checklist_seed",
    "compute_scorecard",
    "default_dimension_scores",
    "extract_markdown_section",
    "parse_checklist_items",
    "parse_scorecard",
    "parse_wbs_table",
]
