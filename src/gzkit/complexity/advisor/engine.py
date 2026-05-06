"""Trigger-time diagnosis engine for the complexity advisor (OBPI-0.0.29-02).

Given an :class:`AstContext` plus a ``(metric, value)`` crossing and a
:class:`gzkit.complexity.thresholds.ThresholdTable` (ADR-0.0.28-02), returns
an :class:`gzkit.complexity.advisor.diagnosis.AdvisorDiagnosis` (OBPI-0.0.29-01)
when the value crosses a band, else ``None``.

ADR-0.0.29 § Decision rationale binds three properties of this engine:

#1 — ``ThresholdTable`` is consumed directly; band classification is never
re-implemented (the parser-divergence drift class is closed at the
ADR-0.0.28-02 layer).

#5 — Verdict ↔ proof binding is mandatory; the engine fails closed if it
cannot produce a non-empty proof for a diagnosis (no plausible-looking advice
without traceable evidence).

#7 — Refactor-archetype detection rules are data-driven doctrine loaded from
``data/advisor_archetype_rules.json``; rule amendments flow through the
doctrine-amendment-protocol pool stub, not silent code edits.

The engine populates ``recommended_move`` and the default-fallback
``doctrinal_frame`` from the cited distilled-characteristics document
(OBPI-0.0.27-04). When the cited document is missing or the relevant section
is absent, the engine raises :class:`EngineError` naming OBPI-0.0.27-07 (the
link-integrity validator) as the resolution path.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.complexity.advisor.archetype_rules import (
    ArchetypeRule,
    load_archetype_rules,
)
from gzkit.complexity.advisor.diagnosis import (
    AdvisorDiagnosis,
    DoctrinalFrame,
    ProofRange,
    RefactorArchetype,
)
from gzkit.complexity.citation import Citation
from gzkit.complexity.thresholds import ThresholdTable

__all__ = [
    "AstContext",
    "DiagnosisEngine",
    "EngineError",
    "diagnose",
]

_AUTHORITY_KEYWORD_MAP: dict[str, str] = {
    "fowler": "fowler",
    "martin": "martin",
    "page-jones": "page_jones",
    "page_jones": "page_jones",
    "constantine": "constantine",
}

_METRIC_SECTION_PATTERN = re.compile(
    r"^##\s+Metric:\s+`(?P<metric>[a-z0-9_]+)`(?P<body>.*?)(?=^##\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_DOCTRINAL_FRAME_LINE_PATTERN = re.compile(
    r"^\*\*Doctrinal frame:\*\*\s+(?P<prose>.+?)$",
    re.MULTILINE,
)
_PRACTITIONER_EYE_SECTION_PATTERN = re.compile(
    r"^###\s+Practitioner-eye observation\s*\n(?P<body>.*?)(?=^##\s|^###\s|\Z)",
    re.MULTILINE | re.DOTALL,
)
_HTML_COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL)


class EngineError(Exception):
    """Raised when the diagnosis engine cannot construct a well-formed diagnosis."""


class AstContext(BaseModel):
    """Frozen carrier for the AST inputs the engine needs.

    AST construction is the caller's responsibility (the CLI in OBPI-03, the
    auto-chain hook in OBPI-05). The engine accepts the prepared context and
    extracts proof ranges from ``target_node`` only.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    file_path: str = Field(min_length=1)
    source: str = Field(min_length=1)
    tree: ast.Module
    target_node: ast.AST


class DiagnosisEngine:
    """Trigger-time diagnosis engine.

    Loads the rule table once at construction time (REQ-0.0.29-02-03). Pass
    ``rules`` to inject an in-memory rule list (typically for tests); pass
    ``rule_path`` to load from a non-canonical location. Passing both is a
    contract violation.
    """

    def __init__(
        self,
        rules: tuple[ArchetypeRule, ...] | None = None,
        rule_path: Path | None = None,
    ) -> None:
        if rules is not None and rule_path is not None:
            msg = "DiagnosisEngine accepts rules OR rule_path, not both"
            raise EngineError(msg)
        self._rules: tuple[ArchetypeRule, ...] = (
            rules if rules is not None else load_archetype_rules(rule_path)
        )

    def diagnose(
        self,
        ast_context: AstContext,
        metric: str,
        value: float,
        table: ThresholdTable,
    ) -> AdvisorDiagnosis | None:
        band = table.band_for(metric, value)
        if band is None:
            return None
        proof = _extract_proof(ast_context.target_node, ast_context.file_path)
        if not proof:
            msg = (
                f"engine produced empty proof for metric {metric!r} "
                f"crossing {band.trigger_semantic!r}"
            )
            raise EngineError(msg)
        distilled_text = _read_distilled_text(table.citation)
        recommended_move = _load_recommended_move(metric, distilled_text)
        matched_rule = _match_archetype_rule(
            self._rules, metric, band.trigger_semantic, ast_context.target_node
        )
        if matched_rule is not None:
            archetype = matched_rule.archetype
            doctrinal_frame = matched_rule.doctrinal_frame
        else:
            archetype = RefactorArchetype.LONG_PARAMETER_LIST
            doctrinal_frame = _resolve_default_doctrinal_frame(metric, distilled_text)
        return AdvisorDiagnosis(
            metric=metric,
            crossing_band=band.trigger_semantic,
            crossing_value=value,
            archetype=archetype,
            doctrinal_frame=doctrinal_frame,
            proof=proof,
            recommended_move=recommended_move,
        )


def diagnose(
    ast_context: AstContext,
    metric: str,
    value: float,
    table: ThresholdTable,
    rules: tuple[ArchetypeRule, ...] | None = None,
) -> AdvisorDiagnosis | None:
    """Module-level convenience wrapper around :class:`DiagnosisEngine`."""

    return DiagnosisEngine(rules=rules).diagnose(ast_context, metric, value, table)


def _extract_proof(target_node: ast.AST, file_path: str) -> tuple[ProofRange, ...]:
    seen: set[tuple[int, int, str]] = set()
    ranges: list[ProofRange] = []
    for node in ast.walk(target_node):
        line = getattr(node, "lineno", None)
        if line is None:
            continue
        end_line = getattr(node, "end_lineno", line) or line
        kind = type(node).__name__
        key = (line, end_line, kind)
        if key in seen:
            continue
        seen.add(key)
        ranges.append(
            ProofRange(
                file_path=file_path,
                start_line=line,
                end_line=end_line,
                ast_node_kind=kind,
            )
        )
    ranges.sort(key=lambda pr: (pr.start_line, pr.end_line))
    return tuple(ranges)


def _match_archetype_rule(
    rules: tuple[ArchetypeRule, ...],
    metric: str,
    band: str,
    target_node: ast.AST,
) -> ArchetypeRule | None:
    for rule in rules:
        if rule.metric_predicate.matches(metric, band) and rule.ast_predicate.matches(target_node):
            return rule
    return None


def _read_distilled_text(citation: Citation) -> str:
    path = Path(citation.distilled_characteristics_path)
    if not path.exists():
        msg = (
            f"distilled-characteristics document "
            f"{citation.distilled_characteristics_path!r} not found; "
            f"resolution path: gz validate --complexity-doctrine-links (OBPI-0.0.27-07)"
        )
        raise EngineError(msg)
    return path.read_text(encoding="utf-8")


def _resolve_default_doctrinal_frame(metric: str, distilled_text: str) -> DoctrinalFrame:
    section_body = _find_metric_section(metric, distilled_text)
    line_match = _DOCTRINAL_FRAME_LINE_PATTERN.search(section_body)
    if line_match is None:
        msg = (
            f"distilled-characteristics document missing doctrinal frame for "
            f"metric {metric!r}; resolution path: "
            f"gz validate --complexity-doctrine-links (OBPI-0.0.27-07)"
        )
        raise EngineError(msg)
    prose = line_match.group("prose").strip()
    authority_token, _, excerpt_token = prose.partition("—")
    authority_clean = authority_token.strip()
    excerpt_clean = excerpt_token.strip() or authority_clean
    authority_value = _resolve_authority(authority_clean)
    if authority_value is None:
        msg = (
            f"distilled-characteristics doctrinal frame for metric {metric!r} "
            f"names no recognized authority; resolution path: "
            f"gz validate --complexity-doctrine-links (OBPI-0.0.27-07)"
        )
        raise EngineError(msg)
    return DoctrinalFrame(
        authority=authority_value,  # type: ignore
        citation=authority_clean,
        excerpt=excerpt_clean,
    )


def _load_recommended_move(metric: str, distilled_text: str) -> str:
    section_body = _find_metric_section(metric, distilled_text)
    eye_match = _PRACTITIONER_EYE_SECTION_PATTERN.search(section_body)
    if eye_match is None:
        msg = (
            f"distilled-characteristics document missing practitioner-eye "
            f"observation for metric {metric!r}; resolution path: "
            f"gz validate --complexity-doctrine-links (OBPI-0.0.27-07)"
        )
        raise EngineError(msg)
    cleaned = _HTML_COMMENT_PATTERN.sub("", eye_match.group("body")).strip()
    if not cleaned:
        msg = (
            f"distilled-characteristics practitioner-eye observation for metric "
            f"{metric!r} is empty; resolution path: "
            f"gz validate --complexity-doctrine-links (OBPI-0.0.27-07)"
        )
        raise EngineError(msg)
    return cleaned


def _find_metric_section(metric: str, distilled_text: str) -> str:
    for section in _METRIC_SECTION_PATTERN.finditer(distilled_text):
        if section.group("metric") == metric:
            return section.group("body")
    msg = (
        f"distilled-characteristics document missing section for metric "
        f"{metric!r}; resolution path: "
        f"gz validate --complexity-doctrine-links (OBPI-0.0.27-07)"
    )
    raise EngineError(msg)


def _resolve_authority(prose: str) -> str | None:
    lowered = prose.lower()
    for keyword, value in _AUTHORITY_KEYWORD_MAP.items():
        if keyword in lowered:
            return value
    return None
