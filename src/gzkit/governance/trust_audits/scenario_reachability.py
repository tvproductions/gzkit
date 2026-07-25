"""Scenario-reachability validator — ADR-0.0.33 Invariant 4.

Era-1: when data/agent-control-surface-scenarios.json is absent,
exit 0 with advisory to stderr.

Era-2: when registry present, validate JSON Schema (exit 3 on schema error),
then check every Mechanical/Promotable bullet is reachable from at least one
declared scenario's corpus set. Orphan bullets emit stderr warnings (advisory,
exit 0). Only schema violations return ValidationError.

Returns a list[ValidationError] — empty for clean or advisory, non-empty
for policy breach (schema violation).
"""

from __future__ import annotations

import contextlib
import json
import re
from pathlib import Path

from gzkit.advisory import emit_advisory
from gzkit.core.validation_rules import ValidationError

_REGISTRY_PATH = Path("data") / "agent-control-surface-scenarios.json"
_SCORECARD_PATH = Path("docs") / "governance" / "advisory-rules-audit.md"
_SURFACE_FILES = ("AGENTS.md", "CLAUDE.md")

_ENFORCED_CLASSES = frozenset({"mechanical", "promotable"})

# Inline JSON Schema (stdlib-only validation)
_REQUIRED_ITEM_KEYS = frozenset({"name", "corpus"})

_OUTPUT_PREFIX = "scenario-reachability:"

# Match a scorecard table row: | number | rule text | **Classification** | notes |
_TABLE_ROW_RE = re.compile(
    r"^\|\s*[^|]+\s*\|\s*(?P<rule>[^|]+?)\s*\|\s*\*\*(?P<cls>[^*]+)\*\*\s*\|"
)


def validate_scenario_reachability(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for registry schema violations; write advisory warnings to stderr."""
    registry_path = project_root / _REGISTRY_PATH
    if not registry_path.exists():
        emit_advisory(f"{_OUTPUT_PREFIX} registry absent (ADR-0.0.34); skipping reachability check")
        return []

    raw = _load_registry(registry_path)
    if raw is None:
        return [
            ValidationError(
                type="scenario_reachability",
                artifact=_REGISTRY_PATH.as_posix(),
                message=(
                    f"scenario-reachability: registry is not valid JSON: {registry_path.as_posix()}"
                ),
            )
        ]

    schema_error = _validate_registry_schema(raw)
    if schema_error:
        return [
            ValidationError(
                type="scenario_reachability",
                artifact=_REGISTRY_PATH.as_posix(),
                message=f"scenario-reachability: registry schema invalid: {schema_error}",
            )
        ]

    _check_reachability(project_root, raw)  # type: ignore
    return []


def _load_registry(path: Path) -> object | None:
    """Load and return registry JSON, or None on parse error."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _validate_registry_schema(data: object) -> str | None:
    """Return error description if data violates registry schema, else None."""
    if not isinstance(data, list):
        return f"expected array, got {type(data).__name__}"
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            return f"item[{i}] is not an object"
        missing = _REQUIRED_ITEM_KEYS - item.keys()
        if missing:
            return f"item[{i}] missing required keys: {sorted(missing)}"
        if not isinstance(item["name"], str):  # ty: ignore[invalid-argument-type]
            return f"item[{i}].name is not a string"
        corpus = item["corpus"]  # ty: ignore[invalid-argument-type]
        if not isinstance(corpus, list) or not all(isinstance(f, str) for f in corpus):
            return f"item[{i}].corpus must be an array of strings"
    return None


def _check_reachability(project_root: Path, registry: list[dict]) -> None:
    """Emit orphan-bullet warnings to stderr (advisory, never fail-closed)."""
    scorecard = project_root / _SCORECARD_PATH
    if not scorecard.exists():
        return

    bullets = _parse_scorecard(scorecard)
    if not bullets:
        return

    all_corpus: set[str] = {f for item in registry for f in item.get("corpus", [])}
    surface_map = _collect_surface_file_map(project_root)

    for rule_text, classification in bullets:
        if not _is_enforced(classification):
            continue
        normalized = _normalize(rule_text)
        if not normalized:
            continue
        covering_files = {
            name for name, content in surface_map.items() if normalized in _normalize(content)
        }
        if not covering_files.intersection(all_corpus):
            emit_advisory(
                f"{_OUTPUT_PREFIX} orphan bullet: {rule_text!r} not covered by any scenario corpus"
            )


def _parse_scorecard(path: Path) -> list[tuple[str, str]]:
    """Parse advisory-rules-audit.md and return (rule_text, classification) pairs."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return []
    results: list[tuple[str, str]] = []
    for line in content.splitlines():
        m = _TABLE_ROW_RE.match(line.strip())
        if m is None:
            continue
        rule_text = m.group("rule").strip()
        classification = m.group("cls").strip()
        if rule_text.lower() in {"rule", "#", "score", "notes"}:
            continue
        results.append((rule_text, classification))
    return results


def _collect_surface_file_map(project_root: Path) -> dict[str, str]:
    """Return {filename: content} for per-turn surface files (key is the bare filename)."""
    result: dict[str, str] = {}
    for name in _SURFACE_FILES:
        path = project_root / name
        if path.exists():
            with contextlib.suppress(OSError):
                result[name] = path.read_text(encoding="utf-8")
    rules_root = project_root / ".claude" / "rules"
    if rules_root.exists():
        for rule_path in sorted(rules_root.rglob("*.md")):
            with contextlib.suppress(OSError):
                rel = rule_path.relative_to(project_root).as_posix()
                result[rel] = rule_path.read_text(encoding="utf-8")
    return result


def _normalize(text: str) -> str:
    """Strip bullet markers and collapse whitespace for substring matching."""
    text = re.sub(r"^[\s\-\*]+", "", text.strip())
    text = re.sub(r"^\d+\.\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _is_enforced(classification: str) -> bool:
    """Return True when the classification is Mechanical or Promotable."""
    return classification.strip().lower() in _ENFORCED_CLASSES
