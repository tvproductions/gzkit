"""Threshold table data contract for ADR-0.0.28's complexity-doctrine cluster.

OBPI-0.0.28-02 — frozen Pydantic models + JSON loader + lookup methods consumed
by ADR-0.0.29 advisor and ADR-0.0.30 authoring-guidance. The single loader is
the structural defense against parser-divergence drift across downstream
consumers.

Data source-of-truth is ``.gzkit/rules/complexity-thresholds.json`` (GHI #426 —
deterministic config is structured data, not regex-parsed prose). The companion
``.gzkit/rules/complexity-thresholds.md`` carries the doctrine narrative
(invariant, vocabulary, bootstrap carve-out, amendment protocol) and links to
this JSON file as the runtime source of truth.

Polarity-aware ``band_for`` semantics for inverted metrics (``radon_mi``) are
tracked under GHI #405; this module ships the high-is-worse default.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from gzkit.complexity.citation import Citation

CANONICAL_PERCENTILES: tuple[int, ...] = (50, 75, 90, 95, 99)
TRIGGER_VOCABULARY: tuple[str, ...] = ("block", "warn", "advise")
_SEVERITY_ORDER: dict[str, int] = {"block": 3, "warn": 2, "advise": 1}


class ThresholdBand(BaseModel):
    """One per-metric (percentile, absolute, trigger) row from the data file."""

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
    """Whole data file parsed into bands plus a citation tuple."""

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

    def metrics(self) -> tuple[str, ...]:
        """Return the unique set of metrics declared in the table, in order."""
        seen: list[str] = []
        for band in self.bands:
            if band.metric not in seen:
                seen.append(band.metric)
        return tuple(seen)


def load_threshold_table(data_path: Path) -> ThresholdTable:
    """Parse a complexity-thresholds JSON file into a ``ThresholdTable``.

    The path must point at a ``.json`` document conforming to
    ``src/gzkit/schemas/complexity_thresholds.json``. Any other suffix raises
    ``ValueError`` — the markdown rule body is doctrine narrative, not data.
    """
    if data_path.suffix != ".json":
        msg = (
            f"complexity-thresholds data must be a .json file; got {data_path.name!r}. "
            "The markdown rule body carries narrative only; data lives in JSON (GHI #426)."
        )
        raise ValueError(msg)
    raw: Any = json.loads(data_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        msg = f"complexity-thresholds JSON must decode to an object; got {type(raw).__name__}"
        raise ValueError(msg)
    payload = {key: value for key, value in raw.items() if not key.startswith("$")}
    return ThresholdTable.model_validate(_normalize_payload(payload))


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Coerce list-of-dicts into the tuple-of-models shape Pydantic expects."""
    bands_raw: Iterable[Any] = payload.get("bands", ())
    return {
        **payload,
        "bands": tuple(bands_raw),
    }
