"""Pydantic data models for the OWASP Top 10:2025 scan report.

Defines the immutable schema contract that the chore runner, CLI verb,
and synthesizer skill all import. The hard invariant — no category may
report ``coverage == "mechanical"`` without a named analyzer finding or
zero-finding attestation — is enforced by ``_check_mechanical_floor``.

Categories A01..A10 use the OWASP 2025 nomenclature (verbatim from
ADR-0.47.0 Decision § A01-A10 coverage map). The ``A06`` honesty
invariant (must be ``not-mechanical``) and ``A07`` not-applicable
invariant are enforced at the model level so future drift is rejected
mechanically rather than by reviewer attention.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

OwaspCategory = Literal["A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"]
OwaspSource = Literal["ruff-S", "stdlib-ast", "chore-reused", "not-mechanical"]
OwaspSeverity = Literal["critical", "high", "medium", "low", "info"]
CoverageStatus = Literal["mechanical", "partial-mechanical", "not-mechanical", "not-applicable"]
ScopeMode = Literal["all", "touched", "path", "adr", "obpi"]

_ALL_CATS: frozenset[str] = frozenset(
    {"A01", "A02", "A03", "A04", "A05", "A06", "A07", "A08", "A09", "A10"}
)
_MECHANICAL_SOURCES: frozenset[str] = frozenset({"ruff-S", "stdlib-ast", "chore-reused"})


class OwaspFinding(BaseModel):
    """A single OWASP Top 10:2025 finding emitted by the chore runner."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: OwaspCategory = Field(..., description="OWASP 2025 category code")
    source: OwaspSource = Field(..., description="Analyzer family that produced the finding")
    severity: OwaspSeverity = Field(..., description="Finding severity")
    path: str = Field(..., description="Repo-relative posix path to the offending file")
    line: int | None = Field(None, ge=1, description="1-based line number; None if file-level")
    rule_id: str = Field(..., min_length=1, description="Analyzer rule identifier")
    summary: str = Field(..., min_length=1, description="One-line finding summary")
    evidence: str = Field(
        ..., max_length=200, description="Source-span or analyzer-output excerpt (<=200 chars)"
    )

    @field_validator("path")
    @classmethod
    def _path_posix(cls, value: str) -> str:
        if "\\" in value:
            msg = f"path must be posix-style (forward slashes only); got {value!r}"
            raise ValueError(msg)
        return value


class OwaspScanReport(BaseModel):
    """Top-level OWASP Top 10:2025 scan report."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0"] = Field(..., description="Report schema version")
    owasp_year: Literal[2025] = Field(..., description="OWASP Top 10 year (locked to 2025)")
    repo: str = Field(..., min_length=1, description="Repo identifier")
    commit: str = Field(..., min_length=1, description="Git SHA at scan time")
    scope_mode: ScopeMode = Field(..., description="Scope-resolution mode")
    scanned_paths: list[str] = Field(
        default_factory=list, description="Posix-style paths included in scope"
    )
    findings: list[OwaspFinding] = Field(
        default_factory=list, description="All findings emitted by the scan"
    )
    coverage: dict[str, CoverageStatus] = Field(
        ..., description="Coverage status keyed by OWASP 2025 category code (A01..A10)"
    )
    coverage_attestations: dict[str, bool] = Field(
        default_factory=dict,
        description="Explicit zero-finding attestations keyed by category code",
    )
    generated_at: datetime = Field(..., description="Scan completion timestamp")

    @field_validator("scanned_paths")
    @classmethod
    def _paths_posix(cls, value: list[str]) -> list[str]:
        for entry in value:
            if "\\" in entry:
                msg = f"scanned_paths entries must be posix-style; got {entry!r}"
                raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def _coverage_keys_complete(self) -> OwaspScanReport:
        keys = set(self.coverage.keys())
        if keys != _ALL_CATS:
            missing = _ALL_CATS - keys
            extra = keys - _ALL_CATS
            msg = (
                f"coverage must declare all of A01..A10; "
                f"missing={sorted(missing)} extra={sorted(extra)}"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_a06_not_mechanical(self) -> OwaspScanReport:
        if self.coverage.get("A06") != "not-mechanical":
            msg = (
                "A06 (Insecure Design) must report coverage='not-mechanical' per "
                "ADR-0.47.0 Decision § A01-A10 coverage map; got "
                f"{self.coverage.get('A06')!r}"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_a07_not_applicable(self) -> OwaspScanReport:
        if self.coverage.get("A07") != "not-applicable":
            msg = (
                "A07 (Authentication Failures) must report coverage='not-applicable' "
                "per ADR-0.47.0 Decision § A01-A10 coverage map (no auth surface in "
                f"Python library/CLI); got {self.coverage.get('A07')!r}"
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def _check_mechanical_floor(self) -> OwaspScanReport:
        for cat, status in self.coverage.items():
            if status != "mechanical":
                continue
            has_finding = any(
                f.category == cat and f.source in _MECHANICAL_SOURCES for f in self.findings
            )
            attested = self.coverage_attestations.get(cat) is True
            if not has_finding and not attested:
                msg = (
                    f"coverage[{cat!r}]='mechanical' requires either >=1 finding with "
                    f"source in {sorted(_MECHANICAL_SOURCES)} or "
                    f"coverage_attestations[{cat!r}]=True (zero-finding attestation); "
                    "ADR-0.47.0 hard invariant violated"
                )
                raise ValueError(msg)
        return self
