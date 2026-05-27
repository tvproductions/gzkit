"""Foundation triage composer — diagnosis-only, ephemeral, read-only.

Gathers Draft/Proposed foundation ADRs and counts the governance signals
the gz-foundation-triage skill ranks against. All helpers are pure file
readers: no foundation ADR, ledger entry, or registry is mutated under
any code path. Rubric scoring (structured per-dimension weights) is the
foundation-triage-rubric OBPI's surface and lives at
`src/gzkit/foundation/rubric.py`; this module performs no scoring beyond
returning raw signal counts.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_IN_FLIGHT_STATUSES: frozenset[str] = frozenset({"Draft", "Proposed"})
_FOUNDATION_ID_PATTERN = re.compile(r"^ADR-\d+\.\d+\.\d+$")
_FOUNDATION_SHORT_ID_PREFIX = re.compile(r"^(ADR-\d+\.\d+\.\d+)")
_GHI_PATTERN = re.compile(r"GHI\s*#\d+|GHI-\d+", re.IGNORECASE)


def _parse_simple_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    body = text[3:end]
    fields: dict[str, str] = {}
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


def _extract_h1_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            _, _, after_colon = heading.partition(":")
            return after_colon.strip() or heading
    return ""


def _foundation_short_id(raw_id: str) -> str:
    """Extract the leading ADR-X.Y.Z prefix from a raw id string.

    Accepts either bare short form (``ADR-0.0.57``) or canonical-slug form
    (``ADR-0.0.57-<slug>``) and returns the leading ``ADR-X.Y.Z`` prefix.
    Returns the empty string when the input does not start with that shape.
    """
    if not raw_id:
        return ""
    match = _FOUNDATION_SHORT_ID_PREFIX.match(raw_id)
    return match.group(1) if match else ""


def gather_in_flight_foundations(project_root: Path) -> list[dict[str, str]]:
    """Return one dict per Draft/Proposed foundation ADR on disk.

    Each entry exposes ``id`` (short form, e.g. ``ADR-0.0.57``), ``status``
    (one of ``Draft``/``Proposed``), ``title`` (H1 title with any
    ``ADR-X:`` prefix stripped), and ``path`` (POSIX relative path).
    The function is a pure file reader.
    """
    foundation_root = project_root / "docs" / "design" / "adr" / "foundation"
    if not foundation_root.is_dir():
        return []
    entries: list[dict[str, str]] = []
    for adr_path in sorted(foundation_root.glob("*/ADR-*.md")):
        text = adr_path.read_text(encoding="utf-8")
        frontmatter = _parse_simple_frontmatter(text)
        status = frontmatter.get("status", "")
        if status not in _IN_FLIGHT_STATUSES:
            continue
        short_id = _foundation_short_id(frontmatter.get("id", ""))
        if not _FOUNDATION_ID_PATTERN.match(short_id):
            continue
        entries.append(
            {
                "id": short_id,
                "status": status,
                "title": _extract_h1_title(text),
                "path": adr_path.relative_to(project_root).as_posix(),
            }
        )
    return entries


def count_signals(project_root: Path, adr_id: str) -> dict[str, int]:
    """Count insights, GHI, and invariant references to an ADR id.

    Reads ``.gzkit/insights/agent-insights.jsonl`` for ``insight_count`` and
    ``ghi_count`` (the GHI pattern matched within insight rows that mention
    the ADR id), and ``AGENTS.md`` plus ``.gzkit/rules/*.md`` for
    ``invariant_mentions``. All file I/O is read-only.
    """
    insights_path = project_root / ".gzkit" / "insights" / "agent-insights.jsonl"
    insight_count = 0
    ghi_count = 0
    if insights_path.is_file():
        for raw_line in insights_path.read_text(encoding="utf-8").splitlines():
            if adr_id not in raw_line:
                continue
            insight_count += 1
            ghi_count += len(_GHI_PATTERN.findall(raw_line))
    invariant_mentions = 0
    agents_md = project_root / "AGENTS.md"
    if agents_md.is_file():
        invariant_mentions += agents_md.read_text(encoding="utf-8").count(adr_id)
    rules_root = project_root / ".gzkit" / "rules"
    if rules_root.is_dir():
        for rule_path in sorted(rules_root.glob("*.md")):
            try:
                invariant_mentions += rule_path.read_text(encoding="utf-8").count(adr_id)
            except OSError:
                continue
    return {
        "insight_count": insight_count,
        "ghi_count": ghi_count,
        "invariant_mentions": invariant_mentions,
    }


def run_foundation_triage(project_root: Path) -> None:
    """Emit the Step-1 JSON records to stdout. Diagnosis only; zero mutations."""
    entries = gather_in_flight_foundations(project_root)
    enriched: list[dict[str, object]] = []
    for entry in entries:
        signals = count_signals(project_root, entry["id"])
        enriched.append({**entry, **signals})
    json.dump(enriched, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
