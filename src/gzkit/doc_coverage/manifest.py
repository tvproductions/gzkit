"""Pydantic models and loader for the documentation coverage manifest."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import get_project_root

_MANIFEST_PATH = Path("config") / "doc-coverage.json"

_MANPAGE_DIR = Path("docs") / "user" / "commands"


def manpage_path_for(command_name: str) -> Path:
    """Derive the manpage path for a command name by convention.

    ``"plan create"`` -> ``docs/user/commands/plan-create.md``
    ``"closeout"``    -> ``docs/user/commands/closeout.md``
    """
    slug = command_name.replace(" ", "-")
    return _MANPAGE_DIR / f"{slug}.md"


class SurfaceRequirements(BaseModel):
    """Which documentation surfaces are required for a command."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    manpage: bool = Field(..., description="Requires a docs/user/commands/{slug}.md file")
    index_entry: bool = Field(..., description="Requires an entry in docs/user/commands/index.md")
    operator_runbook: bool = Field(..., description="Requires a reference in docs/user/runbook.md")
    governance_runbook: bool = Field(
        ..., description="Requires a reference in docs/governance/governance_runbook.md"
    )
    docstring: bool = Field(..., description="Requires a docstring on the handler function")


class CommandEntry(BaseModel):
    """Documentation obligation declaration for a single CLI command."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    surfaces: SurfaceRequirements = Field(..., description="Required documentation surfaces")
    governance_relevant: bool = Field(
        ..., description="Whether the governance runbook surface is checked"
    )


class DocCoverageManifest(BaseModel):
    """Per-command documentation obligation manifest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str = Field(..., description="Manifest version (semver)")
    description: str = Field(..., description="Human-readable description of the manifest")
    commands: dict[str, CommandEntry] = Field(
        ..., description="Per-command documentation obligations"
    )


def load_manifest(project_root: Path | None = None) -> DocCoverageManifest:
    """Load and validate the documentation coverage manifest.

    Reads config/doc-coverage.json relative to *project_root*, parses it as
    JSON, and returns a validated, immutable DocCoverageManifest instance.
    """
    if project_root is None:
        project_root = get_project_root()
    manifest_path = project_root / _MANIFEST_PATH
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    return DocCoverageManifest.model_validate(raw)


def find_undeclared_commands(
    manifest: DocCoverageManifest,
    discovered_names: set[str],
) -> list[str]:
    """Return command names present in AST discovery but absent from the manifest.

    These are commands that have no documentation obligation declared and must
    be added to config/doc-coverage.json before documentation coverage is
    considered complete.
    """
    return sorted(name for name in discovered_names if name not in manifest.commands)
