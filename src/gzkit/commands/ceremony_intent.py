"""Intent ↔ OBPI pairing for closeout ceremony Step 2 (GHI #259).

Parses the parent ADR's ``## Intent`` bullets, matches each bullet to the
OBPIs that deliver it via token overlap on slug/title/objective, and renders
the pairing as a 2-column table. Split from ``ceremony_data.py`` to keep that
module under the 600-line cap.
"""

from __future__ import annotations

import re
from typing import Any

from gzkit.commands.ceremony_data import _render_to_text, _short_obpi_id
from gzkit.reporter.presets import ColumnDef, status_table

_INTENT_PAIRING_COLUMNS = [
    ColumnDef(header="ADR Intent", key="heading", style="bold", overflow="fold"),
    ColumnDef(header="Delivered by", key="delivered", overflow="fold"),
]

_NUMBER_BOLD = re.compile(r"^\s*\d+\.\s+\*\*(.+?)\*\*\.?\s*(.*)$")
_DASH_BOLD = re.compile(r"^\s*[-*]\s+\*\*(.+?)\*\*\.?\s*(.*)$")
_NUMBER_PLAIN = re.compile(r"^\s*\d+\.\s+(.+)$")
_DASH_PLAIN = re.compile(r"^\s*[-*]\s+(.+)$")

_STOPWORDS = frozenset(
    {
        "the",
        "a",
        "an",
        "of",
        "and",
        "or",
        "for",
        "to",
        "in",
        "on",
        "is",
        "are",
        "with",
        "how",
        "why",
        "when",
        "does",
        "do",
        "this",
        "that",
        "what",
        "into",
        "from",
        "by",
        "as",
        "it",
        "its",
        "be",
        "been",
        "will",
        "can",
        "not",
        "but",
        "if",
        "via",
        "obpi",
        "adr",
        "vs",
    }
)


def parse_intent_items(intent_text: str) -> list[dict[str, str]]:
    """Parse an ADR ``## Intent`` body into structured bullet items.

    Recognised shapes:

    - Numbered bullets with a bold-prefix heading: ``1. **Heading**. Body.``
    - Dash bullets with a bold-prefix heading: ``- **Heading**. Body.``
    - Plain numbered bullets: ``1. Heading without bold prefix.`` — the first
      sentence becomes the heading and the body carries the rest.

    Prose-only intent sections return an empty list; the Step 2 renderer
    falls back to prose display in that case.
    """
    items: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    def _flush() -> None:
        if current is not None:
            current["body"] = current["body"].strip()
            items.append(current)

    for raw in intent_text.splitlines():
        line = raw.rstrip()
        m = _NUMBER_BOLD.match(line) or _DASH_BOLD.match(line)
        if m:
            _flush()
            current = {"heading": m.group(1).strip(), "body": m.group(2).strip()}
            continue
        m = _NUMBER_PLAIN.match(line) or _DASH_PLAIN.match(line)
        if m:
            _flush()
            body = m.group(1).strip()
            heading, sep, rest = body.partition(". ")
            if sep:
                current = {"heading": heading.strip() + ".", "body": rest.strip()}
            else:
                current = {"heading": body, "body": ""}
            continue
        if current is not None and line.strip():
            current["body"] = (current["body"] + " " + line.strip()).strip()

    _flush()
    return items


def _tokenise(text: str) -> set[str]:
    """Lowercase token set for keyword overlap — drops stopwords and short tokens."""
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return {t for t in tokens if len(t) >= 3 and t not in _STOPWORDS}


def pair_intent_with_obpis(
    items: list[dict[str, str]],
    briefs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Match each intent item to the OBPIs that deliver it.

    Scoring is token-overlap between the intent item's **heading** and each
    OBPI's slug, title, and objective. Heading is the signal-rich surface;
    intent bodies include narrative context that otherwise leaks false
    positives into every brief. When the best heading-overlap has a strong
    match (>= 2 meaningful tokens) every OBPI that also clears that bar is
    kept, capturing the ``one intent → several OBPIs`` case; when the best
    match is weak (single token), only OBPIs tied at that top score are kept.
    Empty ``delivered_by`` surfaces as ``(review BOM below)`` at render time.
    """
    result: list[dict[str, Any]] = []
    for item in items:
        heading_tokens = _tokenise(item["heading"])
        scored: list[tuple[int, str]] = []
        for brief in briefs:
            obpi_id = str(brief.get("id", ""))
            brief_tokens = _tokenise(
                f"{obpi_id} {brief.get('title', '')} {brief.get('objective', '')}"
            )
            score = len(heading_tokens & brief_tokens)
            if score > 0:
                scored.append((score, obpi_id))
        top_score = max((s for s, _ in scored), default=0)
        threshold = 2 if top_score >= 2 else top_score
        delivered = [obpi_id for s, obpi_id in scored if s >= threshold] if top_score else []
        result.append({**item, "delivered_by": delivered})
    return result


def format_intent_pairing_table(pairings: list[dict[str, Any]]) -> str:
    """Render the intent ↔ OBPI pairing as a 2-column table.

    Empty ``delivered_by`` lists render as ``(review BOM below)`` so the
    operator knows the pairing could not be derived and the Bill of Materials
    is the fallback surface.
    """
    rows = []
    for p in pairings:
        delivered = p.get("delivered_by") or []
        shortened = [_short_obpi_id(obpi_id) for obpi_id in delivered]
        rows.append(
            {
                "heading": p.get("heading", ""),
                "delivered": ", ".join(shortened) if shortened else "(review BOM below)",
            }
        )
    table = status_table(
        title="ADR Intent ↔ OBPI Delivery",
        columns=_INTENT_PAIRING_COLUMNS,
        rows=rows,
        empty_message="(no intent items parsed)",
    )
    return _render_to_text(table)
