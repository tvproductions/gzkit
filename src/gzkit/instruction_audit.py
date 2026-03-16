"""Instruction audit and drift detection.

Detects unreachable applyTo globs, foreign-project references,
content drift between canonical instructions and generated rules,
and policy-vs-code mismatches.
"""

import re
from pathlib import Path

from gzkit.rules import (
    _convert_apply_to_paths,
    _extract_body_after_frontmatter,
    _parse_instruction_frontmatter,
)
from gzkit.validate import ValidationError

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_FOREIGN_INDICATORS = {"airlineops", "opsdev"}
_FOREIGN_PATTERN = re.compile(r"\b(airlineops|opsdev)\b")


# ---------------------------------------------------------------------------
# REQ-04-01: Instruction reachability
# ---------------------------------------------------------------------------


def audit_instruction_reachability(project_root: Path) -> list[ValidationError]:
    """Check that every applyTo glob pattern matches at least one file.

    Args:
        project_root: Project root directory.

    Returns:
        List of validation errors for unreachable patterns.
    """
    errors: list[ValidationError] = []
    instructions_dir = project_root / ".github" / "instructions"
    if not instructions_dir.exists():
        return errors

    for src_file in sorted(instructions_dir.iterdir()):
        if not src_file.name.endswith(".instructions.md"):
            continue

        content = src_file.read_text(encoding="utf-8")
        fm = _parse_instruction_frontmatter(content)

        apply_to = fm.get("applyTo", "")
        if not apply_to:
            continue

        patterns = _convert_apply_to_paths(apply_to)
        for pattern in patterns:
            # Global patterns like **/* always match conceptually
            if pattern.startswith("**"):
                continue
            matches = list(project_root.glob(pattern))
            if not matches:
                errors.append(
                    ValidationError(
                        type="instruction",
                        artifact=src_file.name,
                        message=f"applyTo pattern '{pattern}' matches zero files",
                        field="applyTo",
                    )
                )

    return errors


# ---------------------------------------------------------------------------
# REQ-04-02: Foreign reference detection
# ---------------------------------------------------------------------------


def audit_foreign_references(project_root: Path) -> list[ValidationError]:
    """Scan instruction and rule files for foreign-project references.

    Args:
        project_root: Project root directory.

    Returns:
        List of validation errors for files containing foreign references.
    """
    errors: list[ValidationError] = []

    # Scan instruction files
    instructions_dir = project_root / ".github" / "instructions"
    if instructions_dir.exists():
        for src_file in sorted(instructions_dir.iterdir()):
            if not src_file.name.endswith(".instructions.md"):
                continue
            content = src_file.read_text(encoding="utf-8")
            body = _extract_body_after_frontmatter(content)
            match = _FOREIGN_PATTERN.search(body)
            if match:
                errors.append(
                    ValidationError(
                        type="instruction",
                        artifact=src_file.name,
                        message=f"Foreign reference '{match.group()}' found in instruction body",
                        field="body",
                    )
                )

    # Scan generated rule files
    rules_dir = project_root / ".claude" / "rules"
    if rules_dir.exists():
        for rule_file in sorted(rules_dir.iterdir()):
            if not rule_file.is_file() or not rule_file.name.endswith(".md"):
                continue
            content = rule_file.read_text(encoding="utf-8")
            match = _FOREIGN_PATTERN.search(content)
            if match:
                errors.append(
                    ValidationError(
                        type="instruction",
                        artifact=f".claude/rules/{rule_file.name}",
                        message=f"Foreign reference '{match.group()}' found in generated rule",
                        field="body",
                    )
                )

    return errors


# ---------------------------------------------------------------------------
# REQ-04-03: Generated surface drift
# ---------------------------------------------------------------------------


def audit_generated_surface_drift(project_root: Path) -> list[ValidationError]:
    """Detect drift between canonical instructions and generated .claude/rules/.

    Args:
        project_root: Project root directory.

    Returns:
        List of validation errors for drifted, missing, or orphan rules.
    """
    errors: list[ValidationError] = []
    instructions_dir = project_root / ".github" / "instructions"
    rules_dir = project_root / ".claude" / "rules"

    expected_names: set[str] = set()

    if instructions_dir.exists():
        for src_file in sorted(instructions_dir.iterdir()):
            if not src_file.name.endswith(".instructions.md"):
                continue

            content = src_file.read_text(encoding="utf-8")
            fm = _parse_instruction_frontmatter(content)

            exclude = fm.get("excludeAgent", "")
            if exclude in ("coding-agent", "all"):
                continue

            apply_to = fm.get("applyTo", "")
            if not apply_to:
                continue

            body = _extract_body_after_frontmatter(content)
            target_name = src_file.name.replace(".instructions.md", ".md")
            expected_names.add(target_name)

            # Compute expected content using same transform as sync_claude_rules
            if apply_to.strip() == "**/*":
                expected_content = body.lstrip("\n")
            else:
                paths = _convert_apply_to_paths(apply_to)
                paths_yaml = "\n".join(f'  - "{p}"' for p in paths)
                expected_content = f"---\npaths:\n{paths_yaml}\n---\n{body}"

            target = rules_dir / target_name
            if not target.exists():
                errors.append(
                    ValidationError(
                        type="instruction",
                        artifact=target_name,
                        message=f"Expected rule file .claude/rules/{target_name} is missing",
                        field="sync",
                    )
                )
            else:
                actual_content = target.read_text(encoding="utf-8")
                if actual_content != expected_content:
                    errors.append(
                        ValidationError(
                            type="instruction",
                            artifact=target_name,
                            message=(
                                f"Rule file .claude/rules/{target_name} has drifted "
                                f"from source instruction"
                            ),
                            field="sync",
                        )
                    )

    # Check for orphan rule files
    if rules_dir.exists():
        for existing in sorted(rules_dir.iterdir()):
            if (
                existing.is_file()
                and existing.name.endswith(".md")
                and existing.name not in expected_names
            ):
                errors.append(
                    ValidationError(
                        type="instruction",
                        artifact=f".claude/rules/{existing.name}",
                        message=(
                            f"Orphan rule file .claude/rules/{existing.name} "
                            f"has no source instruction"
                        ),
                        field="sync",
                    )
                )

    return errors


# ---------------------------------------------------------------------------
# REQ-04-04: Code contract mismatches
# ---------------------------------------------------------------------------


def audit_code_contract_mismatches(project_root: Path) -> list[ValidationError]:
    """Detect mismatches between instruction policy and actual code.

    v1: Checks whether a Pydantic-only models policy is contradicted by
    dataclass usage in source files.

    Args:
        project_root: Project root directory.

    Returns:
        List of validation errors for policy violations.
    """
    errors: list[ValidationError] = []
    instructions_dir = project_root / ".github" / "instructions"

    # Check if models instruction exists and mandates Pydantic
    if not instructions_dir or not instructions_dir.exists():
        return errors

    models_instruction = instructions_dir / "models.instructions.md"
    if not models_instruction.exists():
        return errors

    content = models_instruction.read_text(encoding="utf-8")
    body = _extract_body_after_frontmatter(content)
    if "Pydantic" not in body and "BaseModel" not in body:
        return errors

    # Scan source files for dataclass usage
    src_dir = project_root / "src"
    if not src_dir.exists():
        return errors

    dataclass_pattern = re.compile(r"(?:from dataclasses import dataclass|@dataclass)")
    for py_file in sorted(src_dir.rglob("*.py")):
        try:
            py_content = py_file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if dataclass_pattern.search(py_content):
            rel_path = py_file.relative_to(project_root)
            errors.append(
                ValidationError(
                    type="instruction",
                    artifact="models.instructions.md",
                    message=f"Policy requires Pydantic but {rel_path} uses dataclasses",
                    field="models",
                )
            )

    return errors


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def audit_instructions(project_root: Path) -> list[ValidationError]:
    """Run all instruction audit checks.

    Args:
        project_root: Project root directory.

    Returns:
        Aggregated list of validation errors from all sub-audits.
    """
    errors: list[ValidationError] = []
    errors.extend(audit_instruction_reachability(project_root))
    errors.extend(audit_foreign_references(project_root))
    errors.extend(audit_generated_surface_drift(project_root))
    errors.extend(audit_code_contract_mismatches(project_root))
    return errors
