#!/usr/bin/env python3
"""Portable competitor-radar renderer and validator.

The script intentionally uses only the Python standard library so the skill can
travel with its execution assets. Repository-specific state lives under
``artifacts/reports/competitor-radar/``; this script remains inside the skill.
"""

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[call-non-callable]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")  # ty: ignore[call-non-callable]

REPORT_DIR = Path("artifacts/reports/competitor-radar")
REGISTRY_PATH = REPORT_DIR / "registry.json"
SCAN_DIR = REPORT_DIR / "scans"
INDEX_PATH = REPORT_DIR / "index.md"

ROUTES = {
    "existing-pool-adr",
    "new-pool-adr",
    "open-feature-adr",
    "ghi",
    "explicit-rejection",
    "discussion-only",
}

WATCH_LEVELS = {"primary", "secondary", "reference", "discovery"}


class RadarError(Exception):
    """Validation or rendering error."""


class ProjectRootNotFoundError(RadarError):
    """No ancestor of the starting directory is the gzkit project root."""

    def __init__(self) -> None:
        super().__init__("Could not locate gzkit project root.")


class MissingJsonFileError(RadarError):
    """A required JSON file does not exist."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Missing JSON file: {path}")


class InvalidJsonError(RadarError):
    """A JSON file does not parse."""

    def __init__(self, path: Path, exc: json.JSONDecodeError) -> None:
        self.path = path
        super().__init__(f"Invalid JSON in {path}: {exc}")


class JsonNotObjectError(RadarError):
    """A JSON file's top-level value is not an object."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"{path} must contain a JSON object.")


class FieldNotNonEmptyStringError(RadarError):
    """A required field is missing, not a string, or blank."""

    def __init__(self, context: str, key: str) -> None:
        self.context = context
        self.key = key
        super().__init__(f"{context}.{key} must be a non-empty string.")


class FieldNotListError(RadarError):
    """A required field is not a list."""

    def __init__(self, context: str, key: str) -> None:
        self.context = context
        self.key = key
        super().__init__(f"{context}.{key} must be a list.")


class CompetitorNotObjectError(RadarError):
    """A registry competitor entry is not a JSON object."""

    def __init__(self, idx: int) -> None:
        self.idx = idx
        super().__init__(f"registry.competitors[{idx}] must be an object.")


class LinksNotObjectError(RadarError):
    """A registry competitor's links field is not a JSON object."""

    def __init__(self, context: str) -> None:
        self.context = context
        super().__init__(f"{context}.links must be an object.")


class PatternNotObjectError(RadarError):
    """A registry strength-pattern entry is not a JSON object."""

    def __init__(self, idx: int) -> None:
        self.idx = idx
        super().__init__(f"registry.strength_patterns[{idx}] must be an object.")


class SnapshotNotObjectError(RadarError):
    """A scan competitor snapshot is not a JSON object."""

    def __init__(self, idx: int) -> None:
        self.idx = idx
        super().__init__(f"scan.competitor_snapshots[{idx}] must be an object.")


class MoveNotObjectError(RadarError):
    """A scan suggested move is not a JSON object."""

    def __init__(self, idx: int) -> None:
        self.idx = idx
        super().__init__(f"scan.suggested_moves[{idx}] must be an object.")


class DuplicateCompetitorIdError(RadarError):
    """Two registry competitors share one id."""

    def __init__(self, competitor_id: str) -> None:
        self.competitor_id = competitor_id
        super().__init__(f"Duplicate competitor id: {competitor_id}")


class DuplicatePatternIdError(RadarError):
    """Two registry strength patterns share one id."""

    def __init__(self, pattern_id: str) -> None:
        self.pattern_id = pattern_id
        super().__init__(f"Duplicate strength pattern id: {pattern_id}")


class DuplicateSnapshotError(RadarError):
    """A scan carries two snapshots for one competitor."""

    def __init__(self, competitor_id: str) -> None:
        self.competitor_id = competitor_id
        super().__init__(f"Duplicate scan snapshot for competitor: {competitor_id}")


class InvalidChoiceError(RadarError):
    """A field holds a value outside its allowed set."""

    def __init__(self, context: str, key: str, value: str) -> None:
        self.context = context
        self.key = key
        self.value = value
        super().__init__(f"{context}.{key} is invalid: {value}")


class SnapshotCompetitorNotInRegistryError(RadarError):
    """A scan snapshot names a competitor the registry does not carry."""

    def __init__(self, context: str, competitor_id: str) -> None:
        self.context = context
        self.competitor_id = competitor_id
        super().__init__(f"{context}.competitor_id is not in registry: {competitor_id}")


class MoveUnknownCompetitorError(RadarError):
    """A suggested move references a competitor the registry does not carry."""

    def __init__(self, context: str, competitor_id: str) -> None:
        self.context = context
        self.competitor_id = competitor_id
        super().__init__(f"{context} references unknown competitor: {competitor_id}")


class ScanExistsError(RadarError):
    """A monthly scan already exists and overwrite was not requested."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Scan already exists: {path}")


class MissingReportError(RadarError):
    """A generated monthly report is absent."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Missing generated report: {path}")


class ReportDriftError(RadarError):
    """A generated monthly report differs from its JSON rendering."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Generated report drifted from JSON: {path}")


class MissingIndexError(RadarError):
    """The generated radar index is absent."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Missing generated index: {path}")


class IndexDriftError(RadarError):
    """The generated radar index differs from its JSON rendering."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"Generated index drifted from JSON: {path}")


def find_project_root(start: Path | None = None) -> Path:
    """Find the repository root from cwd or script path."""
    cursor = (start or Path.cwd()).resolve()
    for candidate in [cursor, *cursor.parents]:
        if (candidate / ".gzkit").is_dir() and (candidate / "artifacts").is_dir():
            return candidate
    raise ProjectRootNotFoundError


def read_json(path: Path) -> dict[str, Any]:
    """Read a JSON object."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise MissingJsonFileError(path) from exc
    except json.JSONDecodeError as exc:
        raise InvalidJsonError(path, exc) from exc
    if not isinstance(data, dict):
        raise JsonNotObjectError(path)
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    """Write deterministic JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
    path.write_text(payload + "\n", encoding="utf-8")


def _require_str(data: dict[str, Any], key: str, context: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise FieldNotNonEmptyStringError(context, key)
    return value


def _require_list(data: dict[str, Any], key: str, context: str) -> list[Any]:
    value = data.get(key)
    if not isinstance(value, list):
        raise FieldNotListError(context, key)
    return value


def validate_registry(registry: dict[str, Any]) -> list[str]:
    """Validate registry shape and return competitor ids."""
    _require_str(registry, "schema_version", "registry")
    _require_str(registry, "discovery_posture", "registry")
    _require_str(registry, "execution_posture", "registry")
    _require_str(registry, "report_structure", "registry")
    competitors = _require_list(registry, "competitors", "registry")
    patterns = _require_list(registry, "strength_patterns", "registry")

    ids: list[str] = []
    for idx, competitor in enumerate(competitors):
        if not isinstance(competitor, dict):
            raise CompetitorNotObjectError(idx)
        context = f"registry.competitors[{idx}]"
        competitor_id = _require_str(competitor, "id", context)
        if competitor_id in ids:
            raise DuplicateCompetitorIdError(competitor_id)
        ids.append(competitor_id)
        _require_str(competitor, "name", context)
        _require_str(competitor, "category", context)
        watch_level = _require_str(competitor, "watch_level", context)
        if watch_level not in WATCH_LEVELS:
            raise InvalidChoiceError(context, "watch_level", watch_level)
        for key in ("links", "known_strengths", "explicit_rejections", "gzkit_destinations"):
            value = competitor.get(key)
            if key == "links":
                if not isinstance(value, dict):
                    raise LinksNotObjectError(context)
            elif not isinstance(value, list):
                raise FieldNotListError(context, key)

    pattern_ids: list[str] = []
    for idx, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            raise PatternNotObjectError(idx)
        context = f"registry.strength_patterns[{idx}]"
        pattern_id = _require_str(pattern, "id", context)
        if pattern_id in pattern_ids:
            raise DuplicatePatternIdError(pattern_id)
        pattern_ids.append(pattern_id)
        _require_str(pattern, "name", context)
        _require_list(pattern, "gzkit_destinations", context)

    return ids


def validate_scan(scan: dict[str, Any], competitor_ids: set[str]) -> None:
    """Validate monthly scan shape."""
    _require_str(scan, "schema_version", "scan")
    _require_str(scan, "month", "scan")
    _require_str(scan, "scan_mode", "scan")
    snapshots = _require_list(scan, "competitor_snapshots", "scan")
    moves = _require_list(scan, "suggested_moves", "scan")
    _require_list(scan, "operator_decisions", "scan")

    seen: set[str] = set()
    for idx, snapshot in enumerate(snapshots):
        if not isinstance(snapshot, dict):
            raise SnapshotNotObjectError(idx)
        context = f"scan.competitor_snapshots[{idx}]"
        competitor_id = _require_str(snapshot, "competitor_id", context)
        if competitor_id not in competitor_ids:
            raise SnapshotCompetitorNotInRegistryError(context, competitor_id)
        if competitor_id in seen:
            raise DuplicateSnapshotError(competitor_id)
        seen.add(competitor_id)
        _require_str(snapshot, "status", context)
        _require_str(snapshot, "trajectory", context)
        _require_str(snapshot, "status_delta", context)
        _require_list(snapshot, "evidence", context)

    for idx, move in enumerate(moves):
        if not isinstance(move, dict):
            raise MoveNotObjectError(idx)
        context = f"scan.suggested_moves[{idx}]"
        _require_str(move, "id", context)
        _require_str(move, "title", context)
        route = _require_str(move, "route", context)
        if route not in ROUTES:
            raise InvalidChoiceError(context, "route", route)
        _require_list(move, "source_competitors", context)
        _require_list(move, "grill_questions", context)
        for competitor_id in move["source_competitors"]:
            if competitor_id not in competitor_ids:
                raise MoveUnknownCompetitorError(context, competitor_id)


def canonical_payload(registry: dict[str, Any], scan: dict[str, Any]) -> str:
    """Return canonical source payload for checksum."""
    data = {"registry": registry, "scan": scan}
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def source_checksum(registry: dict[str, Any], scan: dict[str, Any]) -> str:
    """Return short checksum over report-governing JSON."""
    return hashlib.sha256(canonical_payload(registry, scan).encode("utf-8")).hexdigest()[:16]


def md_escape(value: Any) -> str:
    """Escape Markdown table cell content."""
    text = str(value if value is not None else "")
    return text.replace("|", "\\|").replace("\n", " ").strip()


def md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    """Render a GitHub-flavored Markdown table."""
    lines = [
        "| " + " | ".join(md_escape(h) for h in headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(md_escape(cell) for cell in row) + " |")
    return lines


def competitor_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Index competitors by id."""
    return {item["id"]: item for item in registry.get("competitors", [])}


def format_links(links: dict[str, Any]) -> str:
    """Render compact Markdown links from a link map."""
    rendered: list[str] = []
    for label in ("homepage", "repository", "docs", "marketplace"):
        url = links.get(label)
        if isinstance(url, str) and url:
            rendered.append(f"[{label}]({url})")
    return ", ".join(rendered)


def summarize_evidence(evidence: list[Any]) -> str:
    """Render evidence summaries as compact Markdown links."""
    rendered: list[str] = []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        url = item.get("url", "")
        label = item.get("label") or item.get("summary") or url
        if url:
            rendered.append(f"[{label}]({url})")
        elif label:
            rendered.append(str(label))
    return "; ".join(rendered)


def render_report(registry: dict[str, Any], scan: dict[str, Any], scan_path: Path) -> str:
    """Render one monthly report from registry and scan JSON."""
    month = scan["month"]
    checksum = source_checksum(registry, scan)
    competitors = competitor_map(registry)
    lines: list[str] = []
    lines.append(
        "<!-- gz-competitor-radar: generated; "
        f"registry={REGISTRY_PATH.as_posix()}; scan={scan_path.as_posix()}; "
        f"checksum={checksum} -->"
    )
    lines.append("")
    lines.append(f"# Competitor Radar - {month}")
    lines.append("")
    lines.append("> Generated from JSON. Do not edit this Markdown directly.")
    lines.append("")
    lines.append("## Operating Posture")
    lines.append("")
    posture_rows = [
        ["Discovery", registry["discovery_posture"]],
        ["Execution", registry["execution_posture"]],
        ["Report structure", registry["report_structure"]],
        ["Scan mode", scan["scan_mode"]],
    ]
    lines.extend(md_table(["Axis", "Decision"], posture_rows))
    lines.append("")

    lines.append("## Product Snapshot Pass")
    lines.append("")
    snapshot_rows: list[list[Any]] = []
    for snapshot in scan.get("competitor_snapshots", []):
        competitor = competitors[snapshot["competitor_id"]]
        snapshot_rows.append(
            [
                competitor["name"],
                competitor["watch_level"],
                snapshot["status"],
                snapshot["trajectory"],
                snapshot["status_delta"],
                summarize_evidence(snapshot.get("evidence", [])),
            ]
        )
    lines.extend(
        md_table(
            ["Product", "Watch", "Status", "Trajectory", "Delta", "Evidence"],
            snapshot_rows,
        )
    )
    lines.append("")

    lines.append("## Strength Pattern Pass")
    lines.append("")
    pattern_rows = [
        [
            item["name"],
            ", ".join(item.get("competitor_examples", [])),
            ", ".join(item.get("gzkit_destinations", [])),
            item.get("mechanical_witness", ""),
        ]
        for item in registry.get("strength_patterns", [])
    ]
    lines.extend(
        md_table(
            ["Pattern", "Competitor evidence", "gzkit destinations", "Witness"],
            pattern_rows,
        )
    )
    lines.append("")

    lines.append("## Suggested gzkit Moves")
    lines.append("")
    move_rows = [
        [
            move["id"],
            move["title"],
            move["route"],
            move.get("destination", ""),
            move.get("recommendation", ""),
            move.get("mechanical_witness", ""),
            move.get("decision_status", "pending-grill"),
        ]
        for move in scan.get("suggested_moves", [])
    ]
    lines.extend(
        md_table(
            ["ID", "Move", "Route", "Destination", "Recommendation", "Witness", "Status"],
            move_rows,
        )
    )
    lines.append("")

    lines.append("## Grill Queue")
    lines.append("")
    for move in scan.get("suggested_moves", []):
        lines.append(f"### {move['id']}: {move['title']}")
        lines.append("")
        lines.append(move.get("rationale", ""))
        lines.append("")
        question_rows = []
        for question in move.get("grill_questions", []):
            if not isinstance(question, dict):
                continue
            question_rows.append(
                [
                    question.get("question", ""),
                    question.get("recommended_answer", ""),
                    question.get("answer", ""),
                    question.get("status", "pending"),
                ]
            )
        lines.extend(
            md_table(
                ["Question", "Recommended answer", "Recorded answer", "Status"],
                question_rows,
            )
        )
        lines.append("")

    lines.append("## Operator Decisions")
    lines.append("")
    decision_rows = [
        [
            item.get("id", ""),
            item.get("decision", ""),
            item.get("source", ""),
            item.get("recorded_at", ""),
        ]
        for item in scan.get("operator_decisions", [])
    ]
    lines.extend(md_table(["ID", "Decision", "Source", "Recorded"], decision_rows))
    lines.append("")

    lines.append("## Discovery Candidates")
    lines.append("")
    candidate_rows = [
        [
            item.get("name", ""),
            item.get("evidence", ""),
            item.get("recommended_action", ""),
        ]
        for item in scan.get("discovered_candidates", [])
    ]
    lines.extend(md_table(["Candidate", "Evidence", "Recommended action"], candidate_rows))
    lines.append("")

    lines.append("## Routed Follow-up")
    lines.append("")
    follow_rows = [
        [
            item.get("target", ""),
            item.get("action", ""),
            item.get("status", ""),
        ]
        for item in scan.get("routed_follow_up", [])
    ]
    lines.extend(md_table(["Target", "Action", "Status"], follow_rows))
    lines.append("")
    lines.append(f"_Source checksum: `{checksum}`._")
    lines.append("")
    return "\n".join(lines)


def render_index(registry: dict[str, Any], scan_paths: list[Path]) -> str:
    """Render the radar index from registry and scan list."""
    lines: list[str] = []
    lines.append(
        "<!-- gz-competitor-radar: generated; "
        f"registry={REGISTRY_PATH.as_posix()}; report_dir={REPORT_DIR.as_posix()} -->"
    )
    lines.append("")
    lines.append("# Competitor Radar")
    lines.append("")
    lines.append("> Generated from JSON. Do not edit this Markdown directly.")
    lines.append("")
    lines.append("## Registry")
    lines.append("")
    rows = [
        [
            item["name"],
            item["category"],
            item["watch_level"],
            format_links(item.get("links", {})),
            ", ".join(item.get("gzkit_destinations", [])),
        ]
        for item in registry.get("competitors", [])
    ]
    lines.extend(md_table(["Competitor", "Category", "Watch", "Links", "Destinations"], rows))
    lines.append("")
    lines.append("## Reports")
    lines.append("")
    for scan_path in scan_paths:
        month = scan_path.stem
        lines.append(f"- [{month}]({month}.md)")
    lines.append("")
    return "\n".join(lines)


def scan_json_paths(root: Path) -> list[Path]:
    """Return monthly scan JSON paths."""
    scan_dir = root / SCAN_DIR
    if not scan_dir.exists():
        return []
    return sorted(scan_dir.glob("*.json"))


def report_path_for_scan(root: Path, scan: dict[str, Any]) -> Path:
    """Return generated report path for scan."""
    return root / REPORT_DIR / f"{scan['month']}.md"


def new_scan(root: Path, month: str, overwrite: bool) -> Path:
    """Create a skeletal monthly scan from the registry."""
    registry = read_json(root / REGISTRY_PATH)
    validate_registry(registry)
    path = root / SCAN_DIR / f"{month}.json"
    if path.exists() and not overwrite:
        raise ScanExistsError(path)
    today = dt.date.today().isoformat()
    scan = {
        "schema_version": "1",
        "month": month,
        "scan_mode": "monthly",
        "created_at": today,
        "competitor_snapshots": [
            {
                "competitor_id": item["id"],
                "status": item.get("status", "unknown"),
                "trajectory": item.get("trajectory", "unknown"),
                "status_delta": "pending-agent-scan",
                "evidence": [],
                "agent_analysis": "",
            }
            for item in registry.get("competitors", [])
        ],
        "suggested_moves": [],
        "operator_decisions": [],
        "discovered_candidates": [],
        "routed_follow_up": [],
    }
    write_json(path, scan)
    return path


def render_all(root: Path) -> list[Path]:
    """Render index and all monthly reports."""
    registry = read_json(root / REGISTRY_PATH)
    competitor_ids = set(validate_registry(registry))
    scan_paths = scan_json_paths(root)
    written: list[Path] = []
    for scan_path in scan_paths:
        scan = read_json(scan_path)
        validate_scan(scan, competitor_ids)
        report_path = report_path_for_scan(root, scan)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            render_report(registry, scan, scan_path.relative_to(root)),
            encoding="utf-8",
        )
        written.append(report_path)
    index_path = root / INDEX_PATH
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(render_index(registry, scan_paths), encoding="utf-8")
    written.append(index_path)
    return written


def validate_all(root: Path) -> None:
    """Validate registry, scans, and generated reports."""
    registry = read_json(root / REGISTRY_PATH)
    competitor_ids = set(validate_registry(registry))
    scan_paths = scan_json_paths(root)
    for scan_path in scan_paths:
        scan = read_json(scan_path)
        validate_scan(scan, competitor_ids)
        expected = render_report(registry, scan, scan_path.relative_to(root))
        report_path = report_path_for_scan(root, scan)
        try:
            actual = report_path.read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            raise MissingReportError(report_path) from exc
        if actual != expected:
            raise ReportDriftError(report_path)
    expected_index = render_index(registry, scan_paths)
    try:
        actual_index = (root / INDEX_PATH).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise MissingIndexError(root / INDEX_PATH) from exc
    if actual_index != expected_index:
        raise IndexDriftError(root / INDEX_PATH)


def build_parser() -> argparse.ArgumentParser:
    """Build command parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p_new = sub.add_parser("new-scan", help="Create a monthly scan JSON skeleton.")
    p_new.add_argument("--month", required=True, help="Month in YYYY-MM form.")
    p_new.add_argument("--overwrite", action="store_true")
    sub.add_parser("render", help="Render generated Markdown reports.")
    sub.add_parser("validate", help="Validate registry, scans, and generated Markdown.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        root = find_project_root()
        if args.command == "new-scan":
            path = new_scan(root, args.month, args.overwrite)
            print(f"Created scan: {path.relative_to(root)}")  # noqa: T201
        elif args.command == "render":
            for path in render_all(root):
                print(f"Rendered: {path.relative_to(root)}")  # noqa: T201
        elif args.command == "validate":
            validate_all(root)
            print("competitor-radar validation passed")  # noqa: T201
        else:  # pragma: no cover - argparse enforces choices
            parser.error(f"unknown command: {args.command}")
    except RadarError as exc:
        sys.stderr.write(f"competitor-radar: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
