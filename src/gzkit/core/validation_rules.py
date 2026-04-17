"""Core validation rules — pure domain models and string parsing.

Extracted from gzkit.validate. Contains ValidationError/ValidationResult
models and pure parsing functions. No I/O operations.
"""

import re
from typing import Any

from pydantic import BaseModel, ConfigDict


class ValidationError(BaseModel):
    """A validation error with context."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    type: str  # "schema", "frontmatter", "header", "manifest", "ledger", "surface"
    artifact: str  # Path or identifier
    message: str
    field: str | None = None  # Specific field that failed
    ledger_value: str | None = None  # Ledger-derived value (frontmatter drift)
    frontmatter_value: str | None = None  # Observed frontmatter value (frontmatter drift)


class ValidationResult(BaseModel):
    """Result of validation with errors."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    valid: bool
    errors: list[ValidationError]


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from Markdown content.

    Args:
        content: Full Markdown content with optional frontmatter.

    Returns:
        Tuple of (frontmatter dict, remaining content).
        Returns empty dict if no frontmatter found.

    """
    # Match YAML frontmatter between --- delimiters
    pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return {}, content

    frontmatter_str = match.group(1)
    body = match.group(2)

    # Parse YAML manually (simple key: value pairs)
    frontmatter: dict[str, Any] = {}
    for line in frontmatter_str.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()
            # Remove quotes if present
            is_double_quoted = value.startswith('"') and value.endswith('"')
            is_single_quoted = value.startswith("'") and value.endswith("'")
            if is_double_quoted or is_single_quoted:
                value = value[1:-1]
            frontmatter[key] = value

    return frontmatter, body


def extract_headers(content: str) -> list[str]:
    """Extract all ## level headers from Markdown content.

    Args:
        content: Markdown content (without frontmatter).

    Returns:
        List of header texts (without ## prefix).

    """
    headers = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## "):
            header_text = line[3:].strip()
            # Remove any trailing anchors or formatting
            header_text = re.sub(r"\s*\{#[^}]+\}$", "", header_text)
            headers.append(header_text)
    return headers
