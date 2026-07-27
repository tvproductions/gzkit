"""Configuration management for gzkit.

Handles .gzkit.json parsing and project configuration.
"""

import json
import warnings
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CODEX_CONFIG_DEFAULT_PATH = ".codex/config.toml"
CODEX_CONFIG_MARKER = "# gzkit-managed-codex-config: v1"


def resolve_codex_config_path(project_root: Path, configured_path: str) -> Path:
    """Resolve a configured Codex path and reject escapes from the project root."""
    root = project_root.resolve()
    resolved = (root / configured_path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError("Codex config path must stay within the project root")
    return resolved


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
    canonical_rules: str = ".gzkit/rules"
    canonical_schemas: str = ".gzkit/schemas"

    # Control surfaces
    agents_md: str = "AGENTS.md"
    claude_md: str = "CLAUDE.md"
    claude_hooks: str = ".claude/hooks"
    claude_settings: str = ".claude/settings.json"
    claude_rules: str = ".claude/rules"
    claude_skills: str = ".claude/skills"
    codex_config: str = CODEX_CONFIG_DEFAULT_PATH
    codex_skills: str = ".agents/skills"
    copilot_skills: str = ".github/skills"
    copilot_instructions: str = ".github/copilot-instructions.md"
    discovery_index: str = ".github/discovery-index.json"
    copilot_hooks: str = ".github/copilot/hooks"
    skills: str = ".gzkit/skills"
    personas: str = ".gzkit/personas"
    chores: str = ".gzkit/chores"


class ArbConfig(BaseModel):
    """ARB (Agent Self-Reporting) middleware configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    receipts_root: str = Field(
        default="artifacts/receipts",
        description="Directory where ARB writes receipt JSON files.",
    )
    default_limit: int = Field(
        default=20,
        description="Default number of recent receipts scanned by validate/advise.",
    )


class AuthorshipConfig(BaseModel):
    """Commit-authorship policy (GHI #725).

    Opt-in by design. gzkit ships to adopters, and an identity rule shaped by
    gzkit's own operator and enforced on every adopter is the dogfooding-leak
    complaint open at GHI #607 — so the default admits every address.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    required_email_suffix: str | None = Field(
        default=None,
        description=(
            "When set, `gz validate --authorship` fails closed unless the effective "
            "git user.email ends with this suffix (e.g. '@users.noreply.github.com'). "
            "Unset means no policy is declared and the scope is a no-op."
        ),
    )


class GzkitConfig(BaseModel):
    """Root configuration for a gzkit-enabled project."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    mode: Literal["lite", "heavy"] = "lite"
    paths: PathConfig = Field(default_factory=PathConfig)
    vendors: VendorsConfig = Field(default_factory=VendorsConfig)
    arb: ArbConfig = Field(default_factory=ArbConfig)
    authorship: AuthorshipConfig = Field(default_factory=AuthorshipConfig)
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

        with config_path.open() as f:
            content = f.read().strip()
            data = json.loads(content) if content else {}

        if "gates" in data:
            warnings.warn(
                "The 'gates' key in .gzkit.json is removed. "
                "Use the 'flags' key and the flag service instead "
                "(see ADR-0.0.8). Remove the 'gates' key from your config.",
                DeprecationWarning,
                stacklevel=2,
            )
            del data["gates"]

        # Select by the model's OWN fields rather than a hand-copied key list.
        # The list form silently discarded any block added to the model after it
        # was written — `extra="forbid"` catches a TYPO'd key loudly, but a
        # correctly-named new key just vanished, and the feature reading it saw
        # defaults forever (observed on `authorship`, GHI #725). Unknown keys are
        # still ignored, as before, so an adopter config carrying a stray key
        # does not newly fail closed.
        known = {key: data[key] for key in cls.model_fields if key in data}
        return cls.model_validate(known)

    def save(self, path: Path | None = None) -> None:
        """Save configuration to .gzkit.json.

        Args:
            path: Path to config file. Defaults to .gzkit.json in current directory.

        """
        config_path = path or Path(".gzkit.json")

        data = self.model_dump()

        if not self.project_name:
            data.pop("project_name", None)

        with config_path.open("w") as f:
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


def load_config(
    *,
    path: Path | None = None,
    cli_overrides: dict[str, str] | None = None,
) -> GzkitConfig:
    """Single entry point for config loading.

    Precedence (later wins): defaults → config file → CLI args.

    Args:
        path: Path to config file. Defaults to .gzkit.json in current directory.
        cli_overrides: CLI argument overrides (key=value pairs for top-level fields).

    Returns:
        Frozen GzkitConfig with all layers merged.

    """
    # Layer 1: Pydantic model defaults (automatic)
    # Layer 2: load from config file
    file_config = GzkitConfig.load(path)

    if not cli_overrides:
        return file_config

    # Layer 3: apply CLI overrides
    data = file_config.model_dump()
    data.update(cli_overrides)

    return GzkitConfig.model_validate(data)
