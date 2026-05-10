"""Surface and skill validation for agent control surfaces."""

import tomllib
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

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


def _validate_codex_config(project_root: Path) -> list[ValidationError]:
    """Validate repo-local Codex feature flags for generated hook surfaces."""
    errors: list[ValidationError] = []
    config_path = project_root / ".codex" / "config.toml"
    hooks_path = project_root / ".codex" / "hooks.json"
    artifact = ".codex/config.toml"

    if not config_path.exists():
        if hooks_path.exists():
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=artifact,
                    message=".codex/hooks.json exists but .codex/config.toml is missing",
                    field="features.hooks",
                )
            )
        return errors

    try:
        payload = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [
            ValidationError(
                type="surface",
                artifact=artifact,
                message=f"Failed to parse Codex config: {exc}",
            )
        ]

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
