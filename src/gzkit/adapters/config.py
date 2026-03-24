"""ConfigStore adapter — file-based configuration persistence.

Satisfies the ConfigStore port Protocol via structural subtyping.
"""

import json
from pathlib import Path


class FileConfigStore:
    """File-based configuration store using .gzkit.json."""

    def __init__(self, path: Path | None = None) -> None:
        self._path = path or Path(".gzkit.json")

    def load(self) -> dict:
        """Load configuration from JSON file."""
        if not self._path.exists():
            return {}
        content = self._path.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else {}

    def save(self, data: dict) -> None:
        """Save configuration to JSON file."""
        self._path.write_text(
            json.dumps(data, indent=2) + "\n",
            encoding="utf-8",
        )
