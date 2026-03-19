"""Configuration management for gzkit.

Handles .gzkit.json parsing and project configuration.
"""

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VendorConfig(BaseModel):
    """Configuration for a single agent vendor surface."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    enabled: bool = Field(False, description="Whether this vendor surface is generated")
    surface_root: str = Field("", description="Root directory for vendor control surface")
    instruction_format: str = Field(
        "generic", description="Instruction format: claude-rules, github-instructions, generic"
    )


class VendorsConfig(BaseModel):
    """Vendor enablement configuration for all supported agent harnesses."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    claude: VendorConfig = Field(
        default_factory=lambda: VendorConfig(
            enabled=True, surface_root=".claude", instruction_format="claude-rules"
        ),
        description="Claude Code agent surface",
    )
    copilot: VendorConfig = Field(
        default_factory=lambda: VendorConfig(
            enabled=False, surface_root=".github", instruction_format="github-instructions"
        ),
        description="GitHub Copilot agent surface",
    )
    codex: VendorConfig = Field(
        default_factory=lambda: VendorConfig(
            enabled=False, surface_root=".agents", instruction_format="generic"
        ),
        description="OpenAI Codex agent surface",
    )
    gemini: VendorConfig = Field(
        default_factory=lambda: VendorConfig(
            enabled=False, surface_root=".gemini", instruction_format="generic"
        ),
        description="Google Gemini CLI agent surface",
    )
    opencode: VendorConfig = Field(
        default_factory=lambda: VendorConfig(
            enabled=False, surface_root=".opencode", instruction_format="generic"
        ),
        description="OpenCode agent surface",
    )


class PathConfig(BaseModel):
    """Path configuration for gzkit artifacts."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Design artifacts
    prd: str = "design/prd"
    constitutions: str = "design/constitutions"
    obpis: str = "design/adr"
    adrs: str = "design/adr"

    # Project structure
    source_root: str = "src"
    tests_root: str = "tests"
    docs_root: str = "docs"
    design_root: str = "design"

    # gzkit internal
    gzkit_dir: str = ".gzkit"
    ledger: str = ".gzkit/ledger.jsonl"
    manifest: str = ".gzkit/manifest.json"

    # Control surfaces
    agents_md: str = "AGENTS.md"
    claude_md: str = "CLAUDE.md"
    claude_hooks: str = ".claude/hooks"
    claude_settings: str = ".claude/settings.json"
    claude_rules: str = ".claude/rules"
    claude_skills: str = ".claude/skills"
    codex_skills: str = ".agents/skills"
    copilot_skills: str = ".github/skills"
    copilot_instructions: str = ".github/copilot-instructions.md"
    discovery_index: str = ".github/discovery-index.json"
    copilot_hooks: str = ".github/copilot/hooks"
    skills: str = ".gzkit/skills"


class GzkitConfig(BaseModel):
    """Root configuration for a gzkit-enabled project."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: Literal["lite", "heavy"] = "lite"
    paths: PathConfig = Field(default_factory=PathConfig)
    vendors: VendorsConfig = Field(default_factory=VendorsConfig)
    project_name: str = ""

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
        vendors_data = data.get("vendors", {})

        return cls.model_validate(
            {
                "mode": data.get("mode", "lite"),
                "paths": paths_data,
                "vendors": vendors_data,
                "project_name": data.get("project_name", ""),
            }
        )

    def save(self, path: Path | None = None) -> None:
        """Save configuration to .gzkit.json.

        Args:
            path: Path to config file. Defaults to .gzkit.json in current directory.

        """
        config_path = path or Path(".gzkit.json")

        data = self.model_dump()

        if not self.project_name:
            data.pop("project_name", None)

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

    def get_path(self, name: str) -> Path:
        """Get a path by name as a Path object.

        Args:
            name: Name of the path attribute.

        Returns:
            Path object for the requested path.

        """
        return Path(getattr(self.paths, name))
