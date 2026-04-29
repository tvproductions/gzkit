"""Pydantic-discipline trust audit (GHI #203 / rules 25, 26).

Asserts that governance code uses Pydantic ``BaseModel`` (not stdlib
``dataclass``) and that every BaseModel subclass declares
``model_config = ConfigDict(...)``.
"""

from __future__ import annotations

import ast
from pathlib import Path

from gzkit.validate import ValidationError

# ``@dataclass`` sites explicitly waived from the BaseModel discipline.
# Non-governance internal value objects may use stdlib dataclass where no
# serialization/validation is required.
_DATACLASS_WAIVERS: dict[str, str] = {
    "src/gzkit/commands/obpi_precomplete.py::CheckResult": (
        "Internal check-result record consumed only by obpi_precomplete CLI; "
        "no persistence, no cross-surface contract."
    ),
}


def audit_pydantic_models(project_root: Path) -> list[ValidationError]:
    """Fail on stdlib ``@dataclass`` in governance code and BaseModels missing ConfigDict.

    Rule 25: no stdlib ``dataclass`` for governance data models.
    Rule 26: every ``BaseModel`` subclass declares ``model_config = ConfigDict(...)``.
    """
    src_root = project_root / "src" / "gzkit"
    if not src_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for py_file in sorted(src_root.rglob("*.py")):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        rel = py_file.relative_to(project_root).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            artifact_key = f"{rel}::{node.name}"
            if _has_dataclass_decorator(node) and artifact_key not in _DATACLASS_WAIVERS:
                errors.append(
                    ValidationError(
                        type="pydantic_models",
                        artifact=f"{rel}:{node.lineno}",
                        message=(
                            f"Class `{node.name}` uses stdlib `@dataclass`. "
                            "Governance data must use Pydantic `BaseModel` "
                            "(`.gzkit/rules/models.md`)."
                        ),
                    )
                )
            if _extends_basemodel(node) and not _has_model_config(node):
                errors.append(
                    ValidationError(
                        type="pydantic_models",
                        artifact=f"{rel}:{node.lineno}",
                        message=(
                            f"BaseModel subclass `{node.name}` is missing "
                            "`model_config = ConfigDict(...)` (rule 26)."
                        ),
                    )
                )
    for stale in sorted(_DATACLASS_WAIVERS.keys() - _extant_class_keys(src_root, project_root)):
        errors.append(
            ValidationError(
                type="pydantic_models",
                artifact=f"DATACLASS_WAIVERS::{stale}",
                message=(
                    f"Waiver `{stale}` references a class that no longer exists. "
                    "Remove the stale waiver."
                ),
            )
        )
    return errors


def _has_dataclass_decorator(node: ast.ClassDef) -> bool:
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "dataclass":
            return True
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Name)
            and dec.func.id == "dataclass"
        ):
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == "dataclass":
            return True
    return False


def _extends_basemodel(node: ast.ClassDef) -> bool:
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id == "BaseModel":
            return True
        if isinstance(base, ast.Attribute) and base.attr == "BaseModel":
            return True
    return False


def _has_model_config(node: ast.ClassDef) -> bool:
    for stmt in node.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "model_config":
                    return True
        if (
            isinstance(stmt, ast.AnnAssign)
            and isinstance(stmt.target, ast.Name)
            and stmt.target.id == "model_config"
        ):
            return True
    return False


def _extant_class_keys(src_root: Path, project_root: Path) -> set[str]:
    keys: set[str] = set()
    for py_file in src_root.rglob("*.py"):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        rel = py_file.relative_to(project_root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                keys.add(f"{rel}::{node.name}")
    return keys
