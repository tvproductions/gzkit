"""Handoff document validation for session handoff governance.

Extracted from tests/governance/test_handoff_schema.py (OBPI-0.0.25-06).
Provides fail-closed validation: every check returns a list of violations,
and an empty list means the document is clean.

@covers ADR-0.0.25 (OBPI-0.0.25-06)
@covers ADR-0.25.0 (OBPI-0.25.0-32)
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator

__all__ = [
    "HANDOFF_SCHEMA_VERSION",
    "REQUIRED_SECTIONS",
    "HandoffFrontmatter",
    "HandoffValidationError",
    "parse_frontmatter",
    "validate_handoff_document",
    "validate_no_placeholders",
    "validate_no_secrets",
    "validate_referenced_files",
    "validate_sections_present",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HANDOFF_SCHEMA_VERSION = "govzero.handoff.v1"

REQUIRED_SECTIONS = (
    "Current State Summary",
    "Important Context",
    "Decisions Made",
    "Immediate Next Steps",
    "Pending Work / Open Loops",
    "Verification Checklist",
    "Evidence / Artifacts",
)

# ---------------------------------------------------------------------------
# Compiled patterns
# ---------------------------------------------------------------------------

_ADR_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+$")
_OBPI_ID_RE = re.compile(r"^OBPI-\d+\.\d+\.\d+-\d{2}$")

_PLACEHOLDER_RE = re.compile(
    r"\b(TBD|TODO|FIXME|PLACEHOLDER|XXX|CHANGEME)\b"
    r"|(?:^|\s)\.{3}(?:\s|$)",
    re.IGNORECASE | re.MULTILINE,
)

_SECRET_RE = re.compile(
    r"password\s*="
    r"|secret\s*="
    r"|token\s*="
    r"|api_key\s*="
    r"|Bearer\s+\S+"
    r"|PRIVATE KEY"
    r"|(?<![a-zA-Z])sk-[A-Za-z0-9]{20,}"
    r"|(?<![a-zA-Z])ghp_[A-Za-z0-9]{20,}",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Schema — HandoffFrontmatter model
# ---------------------------------------------------------------------------


class HandoffFrontmatter(BaseModel):
    """Pydantic model for handoff document YAML frontmatter."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["CREATE", "RESUME"]
    adr_id: str
    branch: str
    timestamp: str
    agent: str
    obpi_id: str | None = None
    session_id: str | None = None
    continues_from: str | None = None

    @field_validator("adr_id")
    @classmethod
    def _validate_adr_id(cls, v: str) -> str:
        if not _ADR_ID_RE.match(v):
            msg = f"Invalid ADR ID format: {v!r} (expected ADR-X.Y.Z)"
            raise ValueError(msg)
        return v

    @field_validator("timestamp")
    @classmethod
    def _validate_timestamp(cls, v: str) -> str:
        try:
            datetime.fromisoformat(v)
        except ValueError as exc:
            msg = f"Invalid ISO 8601 timestamp: {v!r}"
            raise ValueError(msg) from exc
        return v

    @field_validator("obpi_id")
    @classmethod
    def _validate_obpi_id(cls, v: str | None) -> str | None:
        if v is not None and not _OBPI_ID_RE.match(v):
            msg = f"Invalid OBPI ID format: {v!r} (expected OBPI-X.Y.Z-NN)"
            raise ValueError(msg)
        return v


# ---------------------------------------------------------------------------
# Validation functions
# ---------------------------------------------------------------------------


class HandoffValidationError(Exception):
    """Raised when a handoff document fails validation."""


def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from Markdown content.

    Args:
        content: Full Markdown document text.

    Returns:
        Parsed YAML as a dict.

    Raises:
        HandoffValidationError: If frontmatter delimiters are missing or YAML is invalid.
    """
    content = content.replace("\r\n", "\n")
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        raise HandoffValidationError("Missing opening frontmatter delimiter (---)")

    end_index = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = i
            break

    if end_index is None:
        raise HandoffValidationError("Missing closing frontmatter delimiter (---)")

    yaml_text = "\n".join(lines[1:end_index])
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        raise HandoffValidationError(f"Invalid YAML in frontmatter: {exc}") from exc

    if not isinstance(data, dict):
        raise HandoffValidationError("Frontmatter must be a YAML mapping")

    return data


def validate_no_placeholders(content: str) -> list[str]:
    """Scan body for placeholder markers.

    Args:
        content: Full Markdown document text.

    Returns:
        List of violation descriptions (empty = clean).
    """
    content = content.replace("\r\n", "\n")
    # Strip frontmatter before scanning
    body = _strip_frontmatter(content)
    # Strip HTML comments before scanning
    body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
    violations: list[str] = []
    for match in _PLACEHOLDER_RE.finditer(body):
        violations.append(f"Placeholder found: {match.group(0).strip()!r}")
    return violations


def validate_no_secrets(content: str) -> list[str]:
    """Scan content for potential secrets.

    Args:
        content: Full Markdown document text.

    Returns:
        List of violation descriptions (empty = clean).
    """
    content = content.replace("\r\n", "\n")
    violations: list[str] = []
    for match in _SECRET_RE.finditer(content):
        violations.append(f"Potential secret found: {match.group(0).strip()!r}")
    return violations


def validate_sections_present(content: str) -> list[str]:
    """Check that all required section headings are present.

    Args:
        content: Full Markdown document text.

    Returns:
        List of missing section names (empty = all present).
    """
    content = content.replace("\r\n", "\n")
    missing: list[str] = []
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+{re.escape(section)}\s*$"
        if not re.search(pattern, content, re.MULTILINE):
            missing.append(section)
    return missing


def validate_referenced_files(content: str, base_path: Path) -> list[str]:
    """Verify that file paths referenced in Evidence section exist on disk.

    Args:
        content: Full Markdown document text.
        base_path: Repository root to resolve relative paths against.

    Returns:
        List of nonexistent file paths (empty = all exist).
    """
    content = content.replace("\r\n", "\n")
    body = _strip_frontmatter(content)
    # Find the Evidence / Artifacts section
    evidence_match = re.search(
        r"^##\s+Evidence\s*/\s*Artifacts\s*$",
        body,
        re.MULTILINE,
    )
    if evidence_match is None:
        return []

    # Extract text until next section heading or end
    rest = body[evidence_match.end() :]
    next_section = re.search(r"^##\s+", rest, re.MULTILINE)
    evidence_text = rest[: next_section.start()] if next_section else rest

    # Strip HTML comments
    evidence_text = re.sub(r"<!--.*?-->", "", evidence_text, flags=re.DOTALL)

    # Find backtick-quoted paths (the convention: `path/to/file`)
    missing: list[str] = []
    for match in re.finditer(r"`([^`]+)`", evidence_text):
        candidate = match.group(1)
        # Skip things that look like commands or inline code, not paths
        if candidate.startswith(("-", "$", "uv ", "git ")):
            continue
        # Must look like a file path (contains / or .)
        if "/" not in candidate and "." not in candidate:
            continue
        resolved = base_path / candidate
        if not resolved.exists():
            missing.append(candidate)

    return missing


def validate_handoff_document(content: str, base_path: Path) -> list[str]:
    """Run all validation checks on a handoff document.

    Args:
        content: Full Markdown document text.
        base_path: Repository root for file reference checks.

    Returns:
        List of all violation messages (empty = valid).
    """
    content = content.replace("\r\n", "\n")
    errors: list[str] = []

    # 1. Parse and validate frontmatter
    try:
        fm_data = parse_frontmatter(content)
        HandoffFrontmatter(**fm_data)
    except (HandoffValidationError, ValidationError) as exc:
        errors.append(f"Frontmatter: {exc}")

    # 2. No placeholders
    errors.extend(validate_no_placeholders(content))

    # 3. No secrets
    errors.extend(validate_no_secrets(content))

    # 4. Required sections
    for section in validate_sections_present(content):
        errors.append(f"Missing required section: {section}")

    # 5. Referenced files exist
    for path in validate_referenced_files(content, base_path):
        errors.append(f"Referenced file not found: {path}")

    return errors


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _strip_frontmatter(content: str) -> str:
    """Remove YAML frontmatter from content, returning body only."""
    content = content.replace("\r\n", "\n")
    lines = content.split("\n")
    if not lines or lines[0].strip() != "---":
        return content
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1 :])
    return content
