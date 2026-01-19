"""JSON Schemas for gzkit governance artifacts.

This package contains schemas for validating:
- Governance manifest (.gzkit/manifest.json)
- PRD documents (frontmatter + headers)
- ADR documents (frontmatter + headers)
- Brief documents (frontmatter + headers)
- AGENTS.md (required sections)
"""

import json
from importlib.resources import files
from pathlib import Path
from typing import Any


def load_schema(name: str) -> dict[str, Any]:
    """Load a JSON schema by name.

    Args:
        name: Schema name without .json extension (e.g., 'manifest', 'prd', 'adr')

    Returns:
        Parsed JSON schema as a dictionary.

    Raises:
        FileNotFoundError: If schema file doesn't exist.
    """
    schema_dir = files("gzkit.schemas")
    schema_file = schema_dir.joinpath(f"{name}.json")
    return json.loads(schema_file.read_text())


def get_schema_path(name: str) -> Path:
    """Get the filesystem path to a schema file.

    Args:
        name: Schema name without .json extension.

    Returns:
        Path to the schema file.
    """
    schema_dir = files("gzkit.schemas")
    return Path(str(schema_dir.joinpath(f"{name}.json")))


__all__ = ["load_schema", "get_schema_path"]
