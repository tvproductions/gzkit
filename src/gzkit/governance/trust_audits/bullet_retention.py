"""Bullet-retention validator — ADR-0.0.33 Invariant 1.

Reads ``docs/governance/advisory-rules-audit.md``, extracts every bullet
classified **Mechanical** or **Promotable**, and asserts each bullet's
normalized semantic text is present as a substring in the per-turn surface
corpus (``AGENTS.md``, ``CLAUDE.md``, ``.claude/rules/**``).

Returns a ``ValidationError(type="bullet_retention")`` for every missing
bullet. An empty list means the surface is clean.

Era-2 forward compatibility: the function signature
``validate_bullet_retention(project_root: Path) -> list[ValidationError]``
matches the ``trust_audits`` package pattern established by
``validate_advisor_proof_binding`` so the Era-2 Pydantic-content-model upgrade
(per ADR-0.0.34) can replace the substring check without rewriting the
registration.
"""

from __future__ import annotations

import contextlib
import re
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_SCORECARD_PATH = Path("docs") / "governance" / "advisory-rules-audit.md"
_SURFACE_FILES = ("AGENTS.md", "CLAUDE.md")
_RULES_GLOB = ".claude/rules/**/*.md"

_ENFORCED_CLASSES = frozenset({"mechanical", "promotable"})

# Match a scorecard table row: | number | rule text | **Classification** | notes |
# The classification cell is mandatory; the notes cell is optional.
_TABLE_ROW_RE = re.compile(
    r"^\|\s*[^|]+\s*\|\s*(?P<rule>[^|]+?)\s*\|\s*\*\*(?P<cls>[^*]+)\*\*\s*\|"
)


def validate_bullet_retention(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for enforced bullets absent from the per-turn surface."""
    scorecard = project_root / _SCORECARD_PATH
    if not scorecard.exists():
        return []

    bullets = _parse_scorecard(scorecard)
    if not bullets:
        return []

    corpus = _collect_surface_corpus(project_root)

    errors: list[ValidationError] = []
    for rule_text, classification in bullets:
        if not _is_enforced(classification):
            continue
        normalized_rule = _normalize(rule_text)
        if not normalized_rule:
            continue
        if normalized_rule not in _normalize(corpus):
            errors.append(
                ValidationError(
                    type="bullet_retention",
                    artifact=_SCORECARD_PATH.as_posix(),
                    message=(
                        f"Bullet-retention violation: {classification!r} bullet "
                        f"not found verbatim in per-turn surface.\n"
                        f"  Bullet: {rule_text!r}\n"
                        f"  Source: {_SCORECARD_PATH.as_posix()}"
                    ),
                )
            )
    return errors


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
        # Skip header rows (rule text is literally "Rule" or similar)
        if rule_text.lower() in {"rule", "#", "score", "notes"}:
            continue
        results.append((rule_text, classification))
    return results


def _collect_surface_corpus(project_root: Path) -> str:
    """Concatenate AGENTS.md, CLAUDE.md, and .claude/rules/**/*.md into one string."""
    parts: list[str] = []
    for name in _SURFACE_FILES:
        path = project_root / name
        if path.exists():
            with contextlib.suppress(OSError):
                parts.append(path.read_text(encoding="utf-8"))

    rules_root = project_root / ".claude" / "rules"
    if rules_root.exists():
        for rule_path in sorted(rules_root.rglob("*.md")):
            with contextlib.suppress(OSError):
                parts.append(rule_path.read_text(encoding="utf-8"))

    return "\n".join(parts)


def _normalize(text: str) -> str:
    """Strip bullet markers and collapse whitespace for substring matching."""
    # Strip leading markdown bullet markers: -, *, digits followed by .
    text = re.sub(r"^[\s\-\*]+", "", text.strip())
    text = re.sub(r"^\d+\.\s*", "", text)
    # Collapse runs of whitespace to a single space
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def _is_enforced(classification: str) -> bool:
    """Return True when the classification is Mechanical or Promotable."""
    return classification.strip().lower() in _ENFORCED_CLASSES
