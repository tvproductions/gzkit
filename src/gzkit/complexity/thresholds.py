"""Threshold table data contract for ADR-0.0.28's complexity-doctrine cluster.

OBPI-0.0.28-02 — frozen Pydantic models + parser + lookup methods consumed by
ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance. The single loader is the
structural defense against parser-divergence drift across downstream consumers.

Polarity-aware ``band_for`` semantics for inverted metrics (``radon_mi``) are
tracked under GHI #405; this module ships the high-is-worse default. The rule
body's bootstrap carve-out exempts inverted metrics from validator portability
checks until the polarity-aware amendment lands.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from gzkit.complexity.citation import Citation, parse_citation
from gzkit.rules import _parse_canonical_frontmatter

CANONICAL_PERCENTILES: tuple[int, ...] = (50, 75, 90, 95, 99)
TRIGGER_VOCABULARY: tuple[str, ...] = ("block", "warn", "advise")
_SEVERITY_ORDER: dict[str, int] = {"block": 3, "warn": 2, "advise": 1}

_BAND_ROW_PATTERN = re.compile(
    r"^\|\s*(?P<trigger>\w+)\s*"
    r"\|\s*p(?P<percentile>\d{2,3})\s*"
    r"\|\s*(?P<absolute>[\d.]+)\s*"
    r"\|\s*(?P<anchor>[^|]+?)\s*\|",
    re.MULTILINE,
)
_METRIC_SECTION_PATTERN = re.compile(
    r"^###\s+Metric:\s+`(?P<metric>[a-z0-9_]+)`(?P<body>.*?)(?=^###\s|^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_CITATION_SECTION_PATTERN = re.compile(
    r"^##\s+Citation\s*\n(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_CITATION_BLOCK_PATTERN = re.compile(
    r"(docs/governance/complexity/\S+?\.md\s*§\s*[a-z0-9-]+\s*\(corpus revision \d+\))",
)


class ThresholdBand(BaseModel):
    """One per-metric (percentile, absolute, trigger) row from the rule body."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric: str = Field(min_length=1)
    corpus_percentile: int
    absolute_number: float = Field(ge=0.0)
    trigger_semantic: Literal["block", "warn", "advise"]

    @field_validator("corpus_percentile")
    @classmethod
    def _check_percentile(cls, value: int) -> int:
        if value not in CANONICAL_PERCENTILES:
            msg = f"corpus_percentile must be one of {CANONICAL_PERCENTILES!r}; got {value!r}"
            raise ValueError(msg)
        return value


class ThresholdTable(BaseModel):
    """Whole rule body parsed into bands plus a citation tuple."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    corpus_revision: int = Field(gt=0)
    bands: tuple[ThresholdBand, ...]
    citation: Citation

    @model_validator(mode="after")
    def _every_metric_has_block_band(self) -> ThresholdTable:
        triggers_by_metric: dict[str, set[str]] = {}
        for band in self.bands:
            triggers_by_metric.setdefault(band.metric, set()).add(band.trigger_semantic)
        missing = sorted(
            metric for metric, triggers in triggers_by_metric.items() if "block" not in triggers
        )
        if missing:
            msg = "every metric must declare a `block` band; missing for: " + ", ".join(missing)
            raise ValueError(msg)
        return self

    def band_for(self, metric: str, value: float) -> ThresholdBand | None:
        """Return the highest-severity band the value crosses (high-is-worse)."""
        crossed = [
            band for band in self.bands if band.metric == metric and value >= band.absolute_number
        ]
        if not crossed:
            return None
        return max(crossed, key=lambda b: _SEVERITY_ORDER[b.trigger_semantic])

    def bands_for_metric(self, metric: str) -> tuple[ThresholdBand, ...]:
        """Return per-metric bands sorted by ascending corpus_percentile."""
        per_metric = [b for b in self.bands if b.metric == metric]
        return tuple(sorted(per_metric, key=lambda b: b.corpus_percentile))


def load_threshold_table(rule_path: Path) -> ThresholdTable:
    """Parse a complexity-thresholds rule body into a ``ThresholdTable``."""
    _, body = _parse_canonical_frontmatter(rule_path)
    citation = _extract_citation(body)
    bands = tuple(_iter_threshold_bands(body))
    return ThresholdTable(
        corpus_revision=citation.corpus_revision,
        bands=bands,
        citation=citation,
    )


def _extract_citation(body: str) -> Citation:
    section_match = _CITATION_SECTION_PATTERN.search(body)
    section_body = section_match.group("body") if section_match else ""
    block_match = _CITATION_BLOCK_PATTERN.search(section_body)
    candidate = block_match.group(1) if block_match else ""
    return parse_citation(candidate)


def _iter_threshold_bands(body: str) -> Iterator[ThresholdBand]:
    for section in _METRIC_SECTION_PATTERN.finditer(body):
        metric = section.group("metric")
        for row in _BAND_ROW_PATTERN.finditer(section.group("body")):
            yield ThresholdBand.model_validate(
                {
                    "metric": metric,
                    "corpus_percentile": int(row.group("percentile")),
                    "absolute_number": float(row.group("absolute")),
                    "trigger_semantic": row.group("trigger"),
                }
            )
