"""Distillation pass — render distilled-characteristics doctrine documents.

Consumes a :class:`gzkit.complexity.baseline.BaselineArtifact` produced by
the OBPI-0.0.27-03 measurement pipeline and emits a dated
``distilled-characteristics-{YYYY-MM-DD}.md`` document under
``docs/governance/complexity/`` (or any caller-chosen directory).

The document is the load-bearing artifact cited by ADR-0.0.28 / 0.0.29 /
0.0.30 per the citation contract in ``.gzkit/rules/complexity-doctrine.md``;
this module enforces the structural contract while leaving the
practitioner-eye observation per metric to the operator at Gate 5
(REQ-0.0.27-04-10 — agent never fabricates the practitioner-eye block).

The diff-narration mechanism (REQ-0.0.27-04-04) is fully exercised on
subsequent runs and emits a canonical cold-start sentinel on first run;
the cold-start branch is canon, not a temporary affordance, so the
no-prior-distillation case has its own structural surface in the document.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.complexity.baseline import (
    BaselineArtifact,
    CrossMetricAggregate,
)
from gzkit.complexity.measurement import CANONICAL_METRICS

QUALITATIVE_BAND_LABELS: tuple[str, ...] = (
    "comfortable craft",
    "investigate",
    "refactor",
)

# The "investigate / refactor" boundary on the corpus distribution.  Anchored
# to p90 because (a) the literature places single-responsibility cyclomatic
# ceilings near McCabe's CC > 10, which lands near corpus p90 for radon_cc
# in observed practice; (b) a single canonical percentile across all metrics
# keeps the boundary line consistent and operator-readable.  Operators may
# narrate per-metric exceptions in the practitioner-eye section.
_BOUNDARY_PERCENTILE = "p90"
_BOUNDARY_BAND = "investigate"

# Movement threshold for the diff-narration section (REQ-04).
_DIFF_MOVEMENT_THRESHOLD_PCT = 10.0

# Doctrinal-frame attribution per canonical metric.  Each frame names the
# practitioner authority whose canon speaks to a violation at the boundary.
_DOCTRINAL_FRAMES: dict[str, str] = {
    "radon_cc": (
        "Martin (Clean Code) — cyclomatic complexity above the corpus p90 "
        "violates the single-responsibility ceiling Martin names for "
        "function decomposition."
    ),
    "radon_mi": (
        "Fowler (Refactoring 2e) — maintainability index is the aggregate "
        "smell signal across long-method, large-class, and divergent-change "
        "smells; corpus p90 demarcates the smell-attention threshold."
    ),
    "radon_hal_volume": (
        "Fowler (Refactoring 2e) — Halstead volume past the corpus p90 "
        "presents the long-method smell from a token-count vantage."
    ),
    "radon_hal_difficulty": (
        "Fowler (Refactoring 2e) — Halstead difficulty above the corpus "
        "p90 indicates comprehensibility loss; the operand/operator ratio "
        "exceeds the audience the function can carry."
    ),
    "radon_hal_effort": (
        "Fowler (Refactoring 2e) — Halstead effort = volume * difficulty "
        "composite; corpus p90 names the practitioner-readable ceiling."
    ),
    "radon_raw_nloc": (
        "Fowler (Refactoring 2e) — non-comment LOC above corpus p90 "
        "names the long-method / large-class smell directly."
    ),
    "radon_raw_lloc": (
        "Fowler (Refactoring 2e) — logical LOC above corpus p90 strips "
        "comment-padding from the long-method smell."
    ),
    "lizard_nloc": (
        "Fowler (Refactoring 2e) — lizard non-comment LOC corroborates "
        "radon's long-method signal across the corpus."
    ),
    "lizard_param_count": (
        "Martin (Clean Code) — long parameter list above corpus p90 is the "
        "canonical decomposition signal Martin names ahead of all other "
        "function-shape smells."
    ),
    "lizard_nesting_depth": (
        "Martin (Clean Code) — nested-block depth past corpus p90 is the "
        "extract-method / guard-clause signal Martin names; depth is the "
        "shape that resists testability."
    ),
    "lizard_ccn": (
        "Martin (Clean Code) — lizard cyclomatic complexity number "
        "corroborates radon_cc's single-responsibility-ceiling signal."
    ),
    "cohesion_lcom4": (
        "Constantine (cohesion / coupling foundations) and Page-Jones "
        "(connascence) — LCOM4 above corpus p90 is the structural signal "
        "that a class has fractured into independent responsibilities."
    ),
}


class DocumentExistsError(FileExistsError):
    """Raised when a dated distilled-characteristics document already exists.

    REQ-0.0.27-04-05: previous distilled-characteristics documents are
    NEVER overwritten — every distillation run produces a new document
    and the doctrine evolution audit trail is permanent and append-only.
    """


class PerMetricTriple(BaseModel):
    """Per-metric triple: numeric boundary + qualitative band + doctrinal frame.

    REQ-0.0.27-04-02 names the triple as the load-bearing per-metric
    structural surface.  Frozen + extra-forbid because doctrine drift is
    invariant drift (AGENTS.md § Anti-Vibing Mantra).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric_key: str = Field(..., min_length=1)
    percentile: str = Field(..., pattern=r"^p\d{2}$")
    absolute: float = Field(...)
    band: str = Field(...)
    doctrinal_frame: str = Field(..., min_length=1)


class _PriorMetricBoundary(BaseModel):
    """Internal helper: parse a prior distillation's per-metric boundary."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metric_key: str = Field(..., min_length=1)
    percentile: str = Field(..., pattern=r"^p\d{2}$")
    absolute: float = Field(...)


def _select_cross_metric(baseline: BaselineArtifact, metric_key: str) -> CrossMetricAggregate:
    """Look up a cross-project aggregate by metric key, fail closed if absent."""

    for aggregate in baseline.cross_project.metrics:
        if aggregate.metric_key == metric_key:
            return aggregate
    msg = f"baseline.cross_project missing canonical metric: {metric_key!r}"
    raise ValueError(msg)


def render_metric_triple(metric_key: str, baseline: BaselineArtifact) -> PerMetricTriple:
    """Build the per-metric triple from the cross-project p90 boundary."""

    cross = _select_cross_metric(baseline, metric_key)
    absolute = getattr(cross, _BOUNDARY_PERCENTILE)
    return PerMetricTriple(
        metric_key=metric_key,
        percentile=_BOUNDARY_PERCENTILE,
        absolute=absolute,
        band=_BOUNDARY_BAND,
        doctrinal_frame=_DOCTRINAL_FRAMES[metric_key],
    )


def _render_metric_aggregate_prose(metric_key: str, baseline: BaselineArtifact) -> str:
    """Agent-drafted percentile prose per metric (REQ-03 prose surface)."""

    cross = _select_cross_metric(baseline, metric_key)
    return (
        f"Across the corpus ({cross.project_count} project(s) contributing "
        f"to this aggregate), `{metric_key}` lands at "
        f"p50 = {cross.p50:.2f}, p75 = {cross.p75:.2f}, p90 = {cross.p90:.2f}, "
        f"p95 = {cross.p95:.2f}, p99 = {cross.p99:.2f}.  "
        f"Inter-project variance of the per-project medians: "
        f"{cross.inter_project_variance:.4f} — "
        f"{_variance_commentary(cross.inter_project_variance)}."
    )


def _variance_commentary(variance: float) -> str:
    """One-line commentary on inter-project variance shape."""

    if variance < 0.5:
        return "low variance, the corpus speaks with one voice on this metric"
    if variance < 2.0:
        return "moderate variance, project-to-project drift is bounded"
    return "high variance, the corpus disagrees and per-domain narration matters"


def _render_practitioner_eye_block(metric_key: str) -> str:
    """Operator-attested practitioner-eye placeholder (REQ-10 surface)."""

    return (
        "### Practitioner-eye observation\n\n"
        f"<!-- OPERATOR: practitioner-eye observation for `{metric_key}` "
        "goes here per OEE doctrine (operator-attested at Gate 5; agent "
        "never authors the practitioner-eye prose). -->\n"
    )


def _render_metric_section(metric_key: str, baseline: BaselineArtifact) -> str:
    """Render one full metric section: header + prose + triple + practitioner-eye."""

    triple = render_metric_triple(metric_key, baseline)
    prose = _render_metric_aggregate_prose(metric_key, baseline)
    practitioner = _render_practitioner_eye_block(metric_key)
    return (
        f"## Metric: `{metric_key}`\n\n"
        f"{prose}\n\n"
        f"**Numeric boundary:** {triple.percentile} = {triple.absolute:.2f} "
        f"(at-or-below this corpus boundary the band is {triple.band}; "
        f"above it, the band escalates to refactor).\n\n"
        f"**Qualitative band (at-or-below boundary):** {triple.band}.\n\n"
        f"**Doctrinal frame:** {triple.doctrinal_frame}\n\n"
        f"{practitioner}\n"
    )


def _render_cold_start_diff() -> str:
    """REQ-03/04: first-run cold-start diff sentinel."""

    return (
        "Cold start — no prior distillation; this document establishes "
        "the baseline.  Subsequent runs will narrate every boundary that "
        f"moved by more than {_DIFF_MOVEMENT_THRESHOLD_PCT:.0f}%.\n"
    )


_PRIOR_BOUNDARY_PATTERN = re.compile(
    r"## Metric: `(?P<metric_key>[a-z0-9_]+)`.*?"
    r"\*\*Numeric boundary:\*\* (?P<percentile>p\d{2}) = (?P<absolute>-?\d+\.\d+)",
    re.DOTALL,
)


def _parse_prior_boundaries(prior_text: str) -> dict[str, _PriorMetricBoundary]:
    """Extract per-metric boundaries from a prior distillation document."""

    boundaries: dict[str, _PriorMetricBoundary] = {}
    for match in _PRIOR_BOUNDARY_PATTERN.finditer(prior_text):
        entry = _PriorMetricBoundary(
            metric_key=match.group("metric_key"),
            percentile=match.group("percentile"),
            absolute=float(match.group("absolute")),
        )
        boundaries[entry.metric_key] = entry
    return boundaries


def _render_movement_line(metric_key: str, prior_absolute: float, current_absolute: float) -> str:
    """Render one boundary-movement narration with operator placeholder."""

    if prior_absolute == 0.0:
        return (
            f"- `{metric_key}`: prior boundary was zero; cannot compute "
            f"percent movement (now {current_absolute:.2f}).  "
            f"<!-- OPERATOR: narrate why this metric was zero before. -->\n"
        )
    movement_pct = (current_absolute - prior_absolute) / prior_absolute * 100.0
    return (
        f"- `{metric_key}`: boundary moved by {movement_pct:+.1f}% "
        f"({prior_absolute:.2f} -> {current_absolute:.2f}).  "
        f"<!-- OPERATOR: narrate why this boundary shifted. -->\n"
    )


def render_diff_section(
    prior_distillation: Path | None,
    current_baseline: BaselineArtifact,
) -> str:
    """REQ-04: diff against prior distillation, or cold-start sentinel."""

    if prior_distillation is None:
        return _render_cold_start_diff()
    prior_text = prior_distillation.read_text(encoding="utf-8")
    prior_boundaries = _parse_prior_boundaries(prior_text)
    movements: list[str] = []
    for metric_key in CANONICAL_METRICS:
        prior = prior_boundaries.get(metric_key)
        if prior is None:
            continue
        current = _select_cross_metric(current_baseline, metric_key)
        current_absolute = getattr(current, prior.percentile)
        if prior.absolute == 0.0:
            movements.append(_render_movement_line(metric_key, prior.absolute, current_absolute))
            continue
        movement_pct = abs((current_absolute - prior.absolute) / prior.absolute * 100.0)
        if movement_pct > _DIFF_MOVEMENT_THRESHOLD_PCT:
            movements.append(_render_movement_line(metric_key, prior.absolute, current_absolute))
    if not movements:
        return (
            "No boundaries moved by more than "
            f"{_DIFF_MOVEMENT_THRESHOLD_PCT:.0f}% relative to the prior "
            f"distillation at `{prior_distillation.as_posix()}`.\n"
        )
    return (
        "Boundaries that moved by more than "
        f"{_DIFF_MOVEMENT_THRESHOLD_PCT:.0f}% (each line carries an operator "
        f"narration placeholder; operator authors the rationale at Gate 5):\n\n"
        + "".join(movements)
    )


def _render_frontmatter(
    *,
    baseline: BaselineArtifact,
    baseline_artifact_path: Path,
    prior_distillation_path: Path | None,
    today: date,
) -> str:
    """Render the YAML frontmatter for the distilled document."""

    prior_value = (
        "null" if prior_distillation_path is None else f'"{prior_distillation_path.as_posix()}"'
    )
    return (
        "---\n"
        f"corpus_revision: {baseline.corpus_revision}\n"
        f'baseline_artifact_path: "{baseline_artifact_path.as_posix()}"\n'
        f'distillation_date: "{today.isoformat()}"\n'
        f"prior_distillation_path: {prior_value}\n"
        "---\n"
    )


def _render_citation_form_section(baseline: BaselineArtifact) -> str:
    """REQ-06: name the canonical citation tuple."""

    return (
        "## Citation form\n\n"
        "Downstream foundation ADRs (per ADR-0.0.27 § Citation contract and "
        "`.gzkit/rules/complexity-doctrine.md`) cite this document by the "
        "canonical tuple `(file path, section anchor, corpus_revision)`.  "
        "Example:\n\n"
        "```\n"
        "docs/governance/complexity/distilled-characteristics-2026-05-04.md "
        f"§ Cyclomatic Complexity (corpus_revision {baseline.corpus_revision})\n"
        "```\n\n"
        "Citing the raw distributions or the corpus registry directly is a "
        "policy breach: the distilled document is the operator-witnessed, "
        "Gate-5-attested doctrine surface; the raw distributions are "
        "measurement evidence; the corpus is the source registry.  The "
        "link-integrity validator (`gz validate "
        "--complexity-doctrine-links`, OBPI-0.0.27-07) fails closed when a "
        "downstream ADR cites a document that does not exist or is out of "
        "date.\n"
    )


def _resolve_output_path(*, output_dir: Path, today: date, allow_dated_sibling: bool) -> Path:
    """Pick the dated output path, fail or suffix on collision per REQ-05."""

    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"distilled-characteristics-{today.isoformat()}"
    primary = output_dir / f"{stem}.md"
    if not primary.exists():
        return primary
    if not allow_dated_sibling:
        msg = (
            f"distilled-characteristics document already exists at "
            f"{primary.as_posix()}; pass allow_dated_sibling=True to write "
            f"a -1-suffixed sibling, or wait until tomorrow."
        )
        raise DocumentExistsError(msg)
    counter = 1
    while True:
        candidate = output_dir / f"{stem}-{counter}.md"
        if not candidate.exists():
            return candidate
        counter += 1


def render_document(
    *,
    baseline: BaselineArtifact,
    baseline_artifact_path: Path,
    prior_distillation_path: Path | None,
    output_dir: Path,
    today: date,
    allow_dated_sibling: bool = False,
) -> Path:
    """Render the full distilled-characteristics document and return its path."""

    output_path = _resolve_output_path(
        output_dir=output_dir, today=today, allow_dated_sibling=allow_dated_sibling
    )
    parts: list[str] = []
    parts.append(
        _render_frontmatter(
            baseline=baseline,
            baseline_artifact_path=baseline_artifact_path,
            prior_distillation_path=prior_distillation_path,
            today=today,
        )
    )
    parts.append(
        f"\n# Distilled complexity characteristics — {today.isoformat()}\n\n"
        "Doctrine document for the gzkit complexity cluster (ADR-0.0.27 / "
        "ADR-0.0.28 / ADR-0.0.29 / ADR-0.0.30).  Per-metric numeric "
        "boundaries are sourced from the cross-project corpus aggregate; "
        "the qualitative band the boundary represents and the doctrinal "
        f"frame for a violation at that boundary are the load-bearing "
        f"per-metric structural surface.  Boundary percentile = "
        f"{_BOUNDARY_PERCENTILE} (canonical across all metrics).\n\n"
    )
    for metric_key in CANONICAL_METRICS:
        parts.append(_render_metric_section(metric_key, baseline))
    parts.append("## Diff against prior distillation\n\n")
    parts.append(
        render_diff_section(
            prior_distillation=prior_distillation_path,
            current_baseline=baseline,
        )
    )
    parts.append("\n")
    parts.append(_render_citation_form_section(baseline))
    output_path.write_text("".join(parts), encoding="utf-8")
    return output_path


__all__ = [
    "QUALITATIVE_BAND_LABELS",
    "DocumentExistsError",
    "PerMetricTriple",
    "render_diff_section",
    "render_document",
    "render_metric_triple",
]
