"""Code quality commands for gzkit.

Provides unified interface to linting, formatting, testing, and type checking.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class QualityResult:
    """Result of a quality check."""

    success: bool
    command: str
    stdout: str
    stderr: str
    returncode: int

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "command": self.command,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
        }


def run_command(command: str, cwd: Path | None = None) -> QualityResult:
    """Run a shell command and capture output.

    Args:
        command: Command to run.
        cwd: Working directory.

    Returns:
        QualityResult with command output.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        return QualityResult(
            success=result.returncode == 0,
            command=command,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
        )
    except Exception as e:
        return QualityResult(
            success=False,
            command=command,
            stdout="",
            stderr=str(e),
            returncode=-1,
        )


def run_lint(project_root: Path) -> QualityResult:
    """Run linting (ruff check).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from linting.
    """
    return run_command("uvx ruff check src tests", cwd=project_root)


def run_format_check(project_root: Path) -> QualityResult:
    """Run format check (ruff format --check).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from format check.
    """
    return run_command("uvx ruff format --check .", cwd=project_root)


def run_format(project_root: Path) -> QualityResult:
    """Run auto-formatting (ruff format + ruff check --fix).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from formatting.
    """
    # Run ruff format first
    format_result = run_command("uvx ruff format .", cwd=project_root)
    if not format_result.success:
        return format_result

    # Then run ruff check --fix
    fix_result = run_command("uvx ruff check --fix src tests", cwd=project_root)

    # Combine results
    return QualityResult(
        success=fix_result.success,
        command="uvx ruff format . && uvx ruff check --fix src tests",
        stdout=format_result.stdout + "\n" + fix_result.stdout,
        stderr=format_result.stderr + "\n" + fix_result.stderr,
        returncode=fix_result.returncode,
    )


def run_typecheck(project_root: Path) -> QualityResult:
    """Run type checking (ty check).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from type checking.
    """
    return run_command("uvx ty check src", cwd=project_root)


def run_tests(project_root: Path) -> QualityResult:
    """Run unit tests (unittest discover).

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from testing.
    """
    return run_command("uv run -m unittest discover tests", cwd=project_root)


@dataclass
class CheckResult:
    """Result of running all quality checks."""

    success: bool
    lint: QualityResult
    format: QualityResult
    typecheck: QualityResult
    test: QualityResult

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "success": self.success,
            "lint": self.lint.to_dict(),
            "format": self.format.to_dict(),
            "typecheck": self.typecheck.to_dict(),
            "test": self.test.to_dict(),
        }


def run_all_checks(project_root: Path) -> CheckResult:
    """Run all quality checks.

    Args:
        project_root: Project root directory.

    Returns:
        CheckResult with all check results.
    """
    lint = run_lint(project_root)
    format_check = run_format_check(project_root)
    typecheck = run_typecheck(project_root)
    test = run_tests(project_root)

    return CheckResult(
        success=all([lint.success, format_check.success, typecheck.success, test.success]),
        lint=lint,
        format=format_check,
        typecheck=typecheck,
        test=test,
    )


def run_pymarkdown(project_root: Path) -> QualityResult:
    """Run PyMarkdown linting on documentation.

    Args:
        project_root: Project root directory.

    Returns:
        QualityResult from PyMarkdown.
    """
    return run_command("uv run -m pymarkdown scan docs/", cwd=project_root)
