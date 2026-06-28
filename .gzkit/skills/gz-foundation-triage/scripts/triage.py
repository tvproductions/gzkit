#!/usr/bin/env python3
"""gz-foundation-triage: gather in-flight foundation ADRs and render the rank.

Self-contained to the skill directory. Stdlib-only. Invoke via:

    uv run python .gzkit/skills/gz-foundation-triage/scripts/triage.py [args]

Output formats:
  - json (Step 1 input)  — structured records the agent reads for cognition
  - rank (Step 3 output) — deterministic markdown deliverable (requires --rank-input)

The script is read-only over the governance corpus — it parses ADR files,
the insights stream, AGENTS.md, and `.gzkit/rules/*.md` and never writes to
any of them. Rubric scoring is the foundation-triage-rubric OBPI's surface
and is not invoked here; ranking falls back to raw signal totals when no
rubric module is available.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path

_IN_FLIGHT_STATUSES: frozenset[str] = frozenset({"Draft", "Proposed"})
_ADR_ID_PATTERN = re.compile(r"^ADR-(?:pool\.[a-z0-9-]+|\d+\.\d+\.\d+)", re.IGNORECASE)
_FOUNDATION_ID_PATTERN = re.compile(r"^ADR-\d+\.\d+\.\d+$")
_FOUNDATION_SHORT_ID_PREFIX = re.compile(r"^(ADR-\d+\.\d+\.\d+)")


def _project_root_from_script(script_path: Path) -> Path:
    """Resolve repo root from this script's location.

    Script lives at ``<repo>/.gzkit/skills/<skill>/scripts/triage.py`` —
    four directory levels below the repository root.
    """
    return script_path.resolve().parents[4]


def _parse_simple_frontmatter(text: str) -> dict[str, str]:
    """Parse top-of-file YAML frontmatter into a flat str->str mapping.

    Avoids a PyYAML dependency: the script is stdlib-only by contract. The
    frontmatter block is the leading `---` ... `---` fence; each non-empty
    line is parsed as `key: value`. Nested structures are ignored — the
    only fields the triage cares about (id, status, title) are flat.
    """
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    body = text[3:end]
    fields: dict[str, str] = {}
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, _, value = stripped.partition(":")
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


def _extract_title(text: str) -> str:
    """Return the first H1 title, stripping any `ADR-X:` prefix."""
    for line in text.splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            _, _, after_colon = heading.partition(":")
            return after_colon.strip() or heading
    return ""


def _iter_foundation_adr_files(project_root: Path) -> Iterable[Path]:
    foundation_root = project_root / "docs" / "design" / "adr" / "foundation"
    if not foundation_root.is_dir():
        return []
    return sorted(foundation_root.glob("*/ADR-*.md"))


def _count_insights_signal(project_root: Path, adr_id: str) -> tuple[int, int]:
    """Return (insights_count, ghi_count) mined from the insights stream."""
    insights_path = project_root / ".gzkit" / "insights" / "agent-insights.jsonl"
    if not insights_path.is_file():
        return 0, 0
    insight_count = 0
    ghi_count = 0
    ghi_pattern = re.compile(r"GHI\s*#\d+|GHI-\d+", re.IGNORECASE)
    for raw_line in insights_path.read_text(encoding="utf-8").splitlines():
        if adr_id not in raw_line:
            continue
        insight_count += 1
        ghi_count += len(ghi_pattern.findall(raw_line))
    return insight_count, ghi_count


def _count_invariant_mentions(project_root: Path, adr_id: str) -> int:
    """Count occurrences of an ADR id across AGENTS.md and rules surfaces."""
    surfaces: list[Path] = []
    agents_md = project_root / "AGENTS.md"
    if agents_md.is_file():
        surfaces.append(agents_md)
    rules_root = project_root / ".gzkit" / "rules"
    if rules_root.is_dir():
        surfaces.extend(sorted(rules_root.glob("*.md")))
    total = 0
    for surface in surfaces:
        try:
            total += surface.read_text(encoding="utf-8").count(adr_id)
        except OSError:
            continue
    return total


def gather_records(project_root: Path) -> list[dict[str, object]]:
    """Return one record per in-flight foundation ADR with signal counts."""
    records: list[dict[str, object]] = []
    for adr_path in _iter_foundation_adr_files(project_root):
        text = adr_path.read_text(encoding="utf-8")
        frontmatter = _parse_simple_frontmatter(text)
        status = frontmatter.get("status", "")
        if status not in _IN_FLIGHT_STATUSES:
            continue
        adr_id = frontmatter.get("id", "")
        prefix_match = _FOUNDATION_SHORT_ID_PREFIX.match(adr_id) if adr_id else None
        adr_short = prefix_match.group(1) if prefix_match else ""
        if not _FOUNDATION_ID_PATTERN.match(adr_short):
            continue
        title = _extract_title(text)
        insight_count, ghi_count = _count_insights_signal(project_root, adr_short)
        invariant_mentions = _count_invariant_mentions(project_root, adr_short)
        records.append(
            {
                "id": adr_short,
                "status": status,
                "title": title,
                "path": adr_path.relative_to(project_root).as_posix(),
                "insight_count": insight_count,
                "ghi_count": ghi_count,
                "invariant_mentions": invariant_mentions,
                "signal_total": insight_count + ghi_count + invariant_mentions,
            }
        )
    return records


def _validate_rank_input(payload: dict[str, object], known_ids: set[str]) -> dict[str, list]:
    """Reject any agent-supplied prose fields; enforce structural schema."""
    rankings_raw = payload.get("rankings", [])
    if not isinstance(rankings_raw, list):
        raise SystemExit("rank-input 'rankings' must be a list")
    allowed_severity = {"urgent", "next-quarter", "latent"}
    rankings: list[dict[str, str]] = []
    for entry in rankings_raw:
        if not isinstance(entry, dict):
            raise SystemExit(f"rankings entry must be a JSON object, got {type(entry).__name__}")
        extra_keys = set(entry) - {"id", "severity"}
        if extra_keys:
            raise SystemExit(
                f"rankings entry {entry.get('id')!r} carries forbidden keys: {sorted(extra_keys)}"
            )
        adr_id = entry.get("id")
        severity = entry.get("severity")
        if not isinstance(adr_id, str) or adr_id not in known_ids:
            raise SystemExit(f"rankings entry id {adr_id!r} not in fetched candidate set")
        if not isinstance(severity, str) or severity not in allowed_severity:
            raise SystemExit(
                f"rankings entry {adr_id} severity {severity!r} not in {sorted(allowed_severity)}"
            )
        rankings.append({"id": adr_id, "severity": severity})
    reclassify_raw = payload.get("reclassify_foundation", [])
    if not isinstance(reclassify_raw, list):
        raise SystemExit("rank-input 'reclassify_foundation' must be a list")
    reclassify: list[dict[str, str]] = []
    for entry in reclassify_raw:
        if not isinstance(entry, dict):
            raise SystemExit("reclassify_foundation entry must be a JSON object")
        extra_keys = set(entry) - {"id", "reclassify"}
        if extra_keys:
            raise SystemExit(
                f"reclassify_foundation entry carries forbidden keys: {sorted(extra_keys)}"
            )
        adr_id = entry.get("id")
        reclassify_value = entry.get("reclassify")
        if not isinstance(adr_id, str) or not _ADR_ID_PATTERN.match(adr_id):
            raise SystemExit(f"reclassify_foundation id {adr_id!r} is not a valid ADR id")
        if reclassify_value != "foundation":
            raise SystemExit(
                f"reclassify_foundation entry {adr_id} reclassify must be 'foundation'"
            )
        reclassify.append({"id": adr_id, "reclassify": "foundation"})
    return {"rankings": rankings, "reclassify_foundation": reclassify}


def render_rank(records: list[dict[str, object]], rank_input: dict[str, list]) -> str:
    """Render the deterministic markdown deliverable."""
    title_by_id = {str(record["id"]): str(record["title"]) for record in records}
    lines: list[str] = ["# Foundation Triage — Recommended Order", ""]
    rankings = rank_input["rankings"]
    if rankings:
        for index, entry in enumerate(rankings, start=1):
            adr_id = entry["id"]
            severity = entry["severity"]
            title = title_by_id.get(adr_id, "(title unavailable)")
            lines.append(f"{index}. [{severity}] {adr_id}: {title}")
    else:
        lines.append("_No foundations ranked for this pass._")
    reclassify = rank_input["reclassify_foundation"]
    if reclassify:
        lines.extend(["", "## Reclassification candidates", ""])
        for entry in reclassify:
            lines.append(f"- {entry['id']} → foundation")
    lines.append("")
    return "\n".join(lines)


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gz-foundation-triage",
        description="Gather in-flight foundation ADRs and render the rank.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "rank"),
        default="json",
        help="json: emit Step-1 records; rank: render Step-3 deliverable from --rank-input.",
    )
    parser.add_argument(
        "--rank-input",
        type=Path,
        default=None,
        help="Path to the agent's rank-input JSON file (required for --format rank).",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Override the resolved project root (defaults to git toplevel).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    project_root = args.project_root or _project_root_from_script(Path(__file__))
    records = gather_records(project_root)
    if args.format == "json":
        json.dump(records, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        return 0
    if args.rank_input is None:
        raise SystemExit("--format rank requires --rank-input <path>")
    try:
        payload = json.loads(args.rank_input.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"failed to read rank-input: {exc}") from exc
    known_ids = {str(record["id"]) for record in records}
    validated = _validate_rank_input(payload, known_ids)
    sys.stdout.write(render_rank(records, validated))
    return 0


if __name__ == "__main__":
    sys.exit(main())
