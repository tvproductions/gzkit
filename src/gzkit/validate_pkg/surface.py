"""Surface and skill validation for agent control surfaces."""

import tomllib
from pathlib import Path
from typing import Any

from pydantic import ValidationError as PydanticValidationError

from gzkit.config import (
    CODEX_CONFIG_DEFAULT_PATH,
    GzkitConfig,
    resolve_codex_config_path,
)
from gzkit.core.validation_rules import (
    ValidationError,
    extract_headers,
    parse_frontmatter,
)
from gzkit.rules import validate_rule_placement
from gzkit.schemas import load_schema


def validate_surfaces(
    project_root: Path, *, check_sync_parity: bool = True
) -> list[ValidationError]:
    """Validate agent control surfaces exist, have valid shape, and are synced.

    When ``check_sync_parity`` is True (the default), the validator also verifies
    that every generated surface file matches what ``sync_all()`` would produce
    for the current canonical state. This catches direct hand-edits of
    ``.claude/``, ``.github/``, ``.agents/``, and root-level generated files that
    would otherwise pass shape validation.

    Args:
        project_root: Project root directory.
        check_sync_parity: When True, enforce canonical/mirror sync parity.

    Returns:
        List of validation errors.

    """
    errors = []

    # Check AGENTS.md exists and has required sections
    agents_md = project_root / "AGENTS.md"
    if agents_md.exists():
        try:
            content = agents_md.read_text(encoding="utf-8")
            _, body = parse_frontmatter(content)
            headers = extract_headers(body)

            schema = load_schema("agents")
            required_headers = schema.get("required_headers", [])

            for required in required_headers:
                if required not in headers:
                    errors.append(
                        ValidationError(
                            type="surface",
                            artifact=str(agents_md),
                            message=f"Missing required section: '{required}'",
                            field=required,
                        )
                    )
        except (OSError, ValueError, KeyError) as e:
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(agents_md),
                    message=f"Failed to validate: {e}",
                )
            )
    else:
        errors.append(
            ValidationError(
                type="surface",
                artifact=str(agents_md),
                message="AGENTS.md does not exist",
            )
        )

    # Check CLAUDE.md exists
    claude_md = project_root / "CLAUDE.md"
    if not claude_md.exists():
        errors.append(
            ValidationError(
                type="surface",
                artifact=str(claude_md),
                message="CLAUDE.md does not exist",
            )
        )

    # Check .claude/settings.json exists if hooks directory exists
    claude_settings = project_root / ".claude" / "settings.json"
    hooks_dir = project_root / ".claude" / "hooks"
    if hooks_dir.exists() and not claude_settings.exists():
        errors.append(
            ValidationError(
                type="surface",
                artifact=str(claude_settings),
                message="Hooks directory exists but settings.json is missing",
            )
        )

    errors.extend(_validate_skill_frontmatter(project_root))
    errors.extend(_validate_instruction_frontmatter(project_root))
    errors.extend(_validate_codex_config(project_root))

    for warning_msg in validate_rule_placement(project_root):
        errors.append(
            ValidationError(
                type="surface",
                artifact="rule-placement",
                message=warning_msg,
            )
        )

    if check_sync_parity:
        from gzkit.validate_pkg.sync_parity import (
            check_sync_parity as _check_parity,  # noqa: PLC0415
        )

        errors.extend(_check_parity(project_root))

    return errors


def _load_codex_config(
    config_path: Path, artifact: str
) -> tuple[str | None, dict[str, Any] | None, list[ValidationError]]:
    """Read and parse one Codex config while preserving precise diagnostics."""
    try:
        content = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        error = ValidationError(
            type="surface",
            artifact=artifact,
            message=f"Failed to read Codex config: {exc}",
        )
        return None, None, [error]
    try:
        return content, tomllib.loads(content), []
    except tomllib.TOMLDecodeError as exc:
        error = ValidationError(
            type="surface",
            artifact=artifact,
            message=f"Failed to parse Codex config: {exc}",
        )
        return content, None, [error]


def _managed_codex_config_errors(content: str, artifact: str) -> list[ValidationError]:
    """Return drift diagnostics for a marked gzkit-managed baseline."""
    from gzkit.sync_surfaces import (  # noqa: PLC0415
        is_managed_codex_config,
        render_codex_config,
    )

    if is_managed_codex_config(content) and content != render_codex_config():
        return [
            ValidationError(
                type="surface",
                artifact=artifact,
                message=(
                    "Managed Codex config is out of sync with the gzkit baseline. "
                    "Remove the marker to accept operator ownership, or delete the "
                    "file and run `uv run gz agent sync control-surfaces` to replace it."
                ),
            )
        ]
    return []


def _obsolete_codex_config_errors(project_root: Path, config: GzkitConfig) -> list[ValidationError]:
    """Report a preserved default file when a different path is configured."""
    configured = resolve_codex_config_path(project_root, config.paths.codex_config)
    default_path = resolve_codex_config_path(project_root, CODEX_CONFIG_DEFAULT_PATH)
    if configured == default_path or not default_path.is_file():
        return []
    return [
        ValidationError(
            type="surface",
            artifact=CODEX_CONFIG_DEFAULT_PATH,
            message=(
                "Obsolete default Codex config conflicts with the configured path "
                f"{Path(config.paths.codex_config).as_posix()}. Preserve its settings, "
                "then remove it."
            ),
            field="codex_config",
        )
    ]


def _missing_codex_config_errors(artifact: str, hooks_path: Path) -> list[ValidationError]:
    """Return the configured-path diagnostic for an absent Codex config."""
    message = "Configured Codex config is missing"
    field = "codex_config"
    if hooks_path.exists():
        message = f".codex/hooks.json exists but {artifact} is missing"
        field = "features.hooks"
    return [
        ValidationError(
            type="surface",
            artifact=artifact,
            message=message,
            field=field,
        )
    ]


def _validate_codex_config(project_root: Path) -> list[ValidationError]:
    """Validate repo-local Codex feature flags for generated hook surfaces."""
    config = GzkitConfig.load(project_root / ".gzkit.json")
    artifact = Path(config.paths.codex_config).as_posix()
    try:
        config_path = resolve_codex_config_path(project_root, config.paths.codex_config)
    except ValueError as exc:
        return [ValidationError(type="surface", artifact=artifact, message=str(exc))]
    hooks_path = project_root / ".codex" / "hooks.json"
    errors = _obsolete_codex_config_errors(project_root, config)
    if not config_path.exists():
        errors.extend(_missing_codex_config_errors(artifact, hooks_path))
        return errors

    content, payload, load_errors = _load_codex_config(config_path, artifact)
    errors.extend(load_errors)
    if content is None or payload is None:
        return errors
    errors.extend(_managed_codex_config_errors(content, artifact))
    features = payload.get("features")
    if not isinstance(features, dict):
        features = {}

    if "codex_hooks" in features:
        errors.append(
            ValidationError(
                type="surface",
                artifact=artifact,
                message="[features].codex_hooks is deprecated; use [features].hooks instead",
                field="features.codex_hooks",
            )
        )

    if hooks_path.exists() and features.get("hooks") is not True:
        errors.append(
            ValidationError(
                type="surface",
                artifact=artifact,
                message=".codex/hooks.json exists but [features].hooks is not enabled",
                field="features.hooks",
            )
        )

    return errors


def _validate_skill_frontmatter(project_root: Path) -> list[ValidationError]:
    """Validate skill SKILL.md frontmatter against SkillFrontmatter model."""
    from gzkit.models.frontmatter import SkillFrontmatter  # noqa: PLC0415

    errors: list[ValidationError] = []
    skills_dir = project_root / ".gzkit" / "skills"
    if not skills_dir.exists():
        return errors

    for skill_dir in sorted(skills_dir.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_file.exists():
            continue

        try:
            content = skill_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
            if fm.get("lifecycle_state") == "retired":
                continue
        except (OSError, ValueError) as e:
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(skill_file),
                    message=f"Failed to parse frontmatter: {e}",
                )
            )
            continue

        try:
            SkillFrontmatter(**fm)
        except PydanticValidationError as exc:
            for err in exc.errors():
                field = str(err["loc"][0]) if err["loc"] else None
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(skill_file),
                        message=f"Skill frontmatter: {err['msg']}",
                        field=field,
                    )
                )

    return errors


def _validate_instruction_frontmatter(project_root: Path) -> list[ValidationError]:
    """Validate instruction file frontmatter against InstructionFrontmatter model."""
    from gzkit.models.frontmatter import InstructionFrontmatter  # noqa: PLC0415

    errors: list[ValidationError] = []
    instructions_dir = project_root / ".github" / "instructions"
    if not instructions_dir.exists():
        return errors

    for inst_file in sorted(instructions_dir.iterdir()):
        if not inst_file.name.endswith(".instructions.md"):
            continue

        try:
            content = inst_file.read_text(encoding="utf-8")
            fm, _ = parse_frontmatter(content)
        except (OSError, ValueError) as e:
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(inst_file),
                    message=f"Failed to parse frontmatter: {e}",
                )
            )
            continue

        try:
            InstructionFrontmatter(**fm)
        except PydanticValidationError as exc:
            for err in exc.errors():
                field = str(err["loc"][0]) if err["loc"] else None
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(inst_file),
                        message=f"Instruction frontmatter: {err['msg']}",
                        field=field,
                    )
                )

    return errors
