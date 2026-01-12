"""Configuration management for gzkit.

Handles .gzkit.yaml parsing and project configuration.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml


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
        """Load configuration from .gzkit.yaml.

        Args:
            path: Path to config file. Defaults to .gzkit.yaml in current directory.

        Returns:
            Parsed configuration, or defaults if file not found.
        """
        config_path = path or Path(".gzkit.yaml")

        if not config_path.exists():
            return cls()

        with open(config_path) as f:
            data = yaml.safe_load(f) or {}

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
        """Save configuration to .gzkit.yaml.

        Args:
            path: Path to config file. Defaults to .gzkit.yaml in current directory.
        """
        config_path = path or Path(".gzkit.yaml")

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
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
