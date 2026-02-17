"""Configuration management for gzkit.

Handles .gzkit.json parsing and project configuration.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal


@dataclass
class PathConfig:
    """Path configuration for gzkit artifacts."""

    # Design artifacts
    prd: str = "design/prd"
    constitutions: str = "design/constitutions"
    obpis: str = "design/obpis"
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
    claude_skills: str = ".claude/skills"
    codex_skills: str = ".codex/skills"
    copilot_skills: str = ".github/skills"
    copilot_instructions: str = ".github/copilot-instructions.md"
    copilot_hooks: str = ".github/copilot/hooks"
    skills: str = ".gzkit/skills"


@dataclass
class GzkitConfig:
    """Root configuration for a gzkit-enabled project."""

    mode: Literal["lite", "heavy"] = "lite"
    paths: PathConfig = field(default_factory=PathConfig)
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
        paths = PathConfig(
            # Design artifacts
            prd=paths_data.get("prd", "design/prd"),
            constitutions=paths_data.get("constitutions", "design/constitutions"),
            obpis=paths_data.get("obpis", "design/obpis"),
            adrs=paths_data.get("adrs", "design/adr"),
            # Project structure
            source_root=paths_data.get("source_root", "src"),
            tests_root=paths_data.get("tests_root", "tests"),
            docs_root=paths_data.get("docs_root", "docs"),
            design_root=paths_data.get("design_root", "design"),
            # gzkit internal
            gzkit_dir=paths_data.get("gzkit_dir", ".gzkit"),
            ledger=paths_data.get("ledger", ".gzkit/ledger.jsonl"),
            manifest=paths_data.get("manifest", ".gzkit/manifest.json"),
            # Control surfaces
            agents_md=paths_data.get("agents_md", "AGENTS.md"),
            claude_md=paths_data.get("claude_md", "CLAUDE.md"),
            claude_hooks=paths_data.get("claude_hooks", ".claude/hooks"),
            claude_settings=paths_data.get("claude_settings", ".claude/settings.json"),
            claude_skills=paths_data.get("claude_skills", ".claude/skills"),
            codex_skills=paths_data.get("codex_skills", ".codex/skills"),
            copilot_skills=paths_data.get("copilot_skills", ".github/skills"),
            copilot_instructions=paths_data.get(
                "copilot_instructions", ".github/copilot-instructions.md"
            ),
            copilot_hooks=paths_data.get("copilot_hooks", ".github/copilot/hooks"),
            skills=paths_data.get("skills", ".gzkit/skills"),
        )

        return cls(
            mode=data.get("mode", "lite"),
            paths=paths,
            project_name=data.get("project_name", ""),
        )

    def save(self, path: Path | None = None) -> None:
        """Save configuration to .gzkit.json.

        Args:
            path: Path to config file. Defaults to .gzkit.json in current directory.
        """
        config_path = path or Path(".gzkit.json")

        data: dict[str, Any] = {
            "mode": self.mode,
            "paths": {
                "prd": self.paths.prd,
                "constitutions": self.paths.constitutions,
                "obpis": self.paths.obpis,
                "adrs": self.paths.adrs,
                "source_root": self.paths.source_root,
                "tests_root": self.paths.tests_root,
                "docs_root": self.paths.docs_root,
                "design_root": self.paths.design_root,
                "agents_md": self.paths.agents_md,
                "claude_md": self.paths.claude_md,
                "claude_hooks": self.paths.claude_hooks,
                "claude_settings": self.paths.claude_settings,
                "claude_skills": self.paths.claude_skills,
                "codex_skills": self.paths.codex_skills,
                "copilot_skills": self.paths.copilot_skills,
                "copilot_instructions": self.paths.copilot_instructions,
                "copilot_hooks": self.paths.copilot_hooks,
                "skills": self.paths.skills,
            },
        }

        if self.project_name:
            data["project_name"] = self.project_name

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
