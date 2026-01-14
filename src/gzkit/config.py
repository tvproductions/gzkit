"""Configuration management for gzkit.

Handles .gzkit.json parsing and project configuration.
"""

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Literal


@dataclass
class PathConfig:
    """Path configuration for gzkit artifacts."""

    canon: str = "docs/canon"
    adrs: str = "docs/adr"
    specs: str = "docs/specs"
    audits: str = "docs/audit"


@dataclass
class GzkitConfig:
    """Root configuration for a gzkit-enabled project."""

    mode: Literal["lite", "heavy"] = "lite"
    paths: PathConfig = field(default_factory=PathConfig)

    @classmethod
    def load(cls, path: Path | None = None) -> "GzkitConfig":
        """Load configuration from .gzkit.json.

        Args:
            path: Path to config file. Defaults to .gzkit.json in current directory.

        Returns:
            Parsed configuration, or defaults if file not found.
        """
        config_path = path or Path(".gzkit.json")

        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            content = f.read().strip()
            data = json.loads(content) if content else {}

        paths_data = data.get("paths", {})
        paths = PathConfig(
            canon=paths_data.get("canon", "docs/canon"),
            adrs=paths_data.get("adrs", "docs/adr"),
            specs=paths_data.get("specs", "docs/specs"),
            audits=paths_data.get("audits", "docs/audit"),
        )

        return cls(
            mode=data.get("mode", "lite"),
            paths=paths,
        )

    def save(self, path: Path | None = None) -> None:
        """Save configuration to .gzkit.json.

        Args:
            path: Path to config file. Defaults to .gzkit.json in current directory.
        """
        config_path = path or Path(".gzkit.json")

        data = {
            "mode": self.mode,
            "paths": {
                "canon": self.paths.canon,
                "adrs": self.paths.adrs,
                "specs": self.paths.specs,
                "audits": self.paths.audits,
            },
        }

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
