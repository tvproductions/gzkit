"""Shared skill metadata compatibility contract.

A leaf module: the skills package and the skill audit both read these names, and
neither may be the other's source for them. While the audit took its report
types from the package, and the package re-exported the audit, each could load
only if the other had loaded first (GHI #1039).
"""

import json
from importlib.resources import files
from typing import Any

from pydantic import BaseModel, ConfigDict

SKILL_DESCRIPTION_MAX_CHARS = 1024
SUPPORTED_SKILL_HARNESSES = "Claude Code and Codex"

# Skill-authoring-quality § Body Quality: physical body lines after frontmatter.
SKILL_BODY_ALIAS_MIN_LINES = 30
SKILL_BODY_NORMAL_MAX_LINES = 200
SKILL_BODY_MAX_LINES = 300
# Fixed cutover ceilings (GHI #1037, 2026-09-19). Source edits may only
# remove entries or lower ceilings; projects cannot add local exemptions.
SKILL_BODY_GRANDFATHER: dict[str, int] = json.loads(
    files("gzkit").joinpath("skill_body_grandfather.json").read_text(encoding="utf-8")
)


class SkillAuditIssue(BaseModel):
    """Represents one skill-audit finding."""

    model_config = ConfigDict(extra="forbid")

    severity: str  # error | warning
    code: str
    path: str
    message: str
    blocking: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "blocking": self.blocking,
        }


class SkillAuditReport(BaseModel):
    """Structured report from skill audit checks."""

    model_config = ConfigDict(extra="forbid")

    valid: bool
    issues: list[SkillAuditIssue]
    checked_skills: int
    checked_roots: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "valid": self.valid,
            "checked_skills": self.checked_skills,
            "checked_roots": self.checked_roots,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse top-level YAML frontmatter key-values from markdown."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content

    frontmatter: dict[str, str] = {}
    active_map_key: str | None = None
    end_idx = -1
    for idx, raw in enumerate(lines[1:], start=1):
        stripped = raw.strip()
        if stripped == "---":
            end_idx = idx
            break
        if not stripped or raw.lstrip().startswith("#"):
            continue

        if raw.startswith((" ", "\t")):
            if active_map_key and ":" in stripped:
                key, value = stripped.split(":", 1)
                nested_key = f"{active_map_key}.{key.strip()}"
                frontmatter[nested_key] = value.strip().strip("\"'")
            continue

        active_map_key = None
        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        normalized_key = key.strip()
        normalized_value = value.strip().strip("\"'")
        if not value.strip() and normalized_key == "metadata":
            active_map_key = normalized_key
            continue

        frontmatter[normalized_key] = normalized_value

    if end_idx == -1:
        return {}, content

    body = "\n".join(lines[end_idx + 1 :])
    return frontmatter, body
