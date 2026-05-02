"""Code-quality trust audits — ty type-ignore syntax, class size, test tier discipline.

* ``audit_type_ignores`` — bracketed mypy-style ``# type: ignore[...]`` is
  unhonored by ty (GHI #197); only bare or ``# ty: ignore[<ty-code>]`` are valid.
* ``audit_class_size`` — fail on classes whose body exceeds 300 lines unless
  explicitly waived (GHI #204 / pythonic.md size limits).
* ``audit_test_tiers`` — re-introduction of ``tests/integration``, ``tests/e2e``,
  ``tests/slow``, ``tests/bdd`` or matching CLI flags is forbidden (GHI #209).
"""

from __future__ import annotations

import ast
import re
import tokenize
from pathlib import Path

from gzkit.validate import ValidationError

# Classes over 300 lines that are explicitly waived from the size limit.
# Each waiver must cite the reason and carry a tracking ticket or rationale
# (trust-doctrine T2 — explicit waivers over silent pass-lists).
_CLASS_SIZE_WAIVERS: dict[str, str] = {
    "src/gzkit/ledger.py::Ledger": (
        "Ledger aggregate root — rewrite tracked separately; splitting by "
        "event-type partition is an ADR-scope refactor."
    ),
    "src/gzkit/hooks/obpi.py::ObpiValidator": (
        "Precondition-chain validator; split by precondition category tracked "
        "as follow-up maintenance."
    ),
}

_FORBIDDEN_TYPE_IGNORE = re.compile(r"#\s*type:\s*ignore\[")


def audit_type_ignores(project_root: Path) -> list[ValidationError]:
    """Fail on any ``# type: ignore[<code>]`` under ``src/`` (GHI #197).

    ``ty`` does not honor bracketed mypy-style codes — the markers look valid
    but suppress nothing. Use bare ``# type: ignore`` or ``# ty: ignore[<ty-code>]``.

    Uses ``tokenize`` so only real Python comments match — docstrings and
    string literals that happen to contain the literal pattern are ignored.
    """
    src_root = project_root / "src"
    if not src_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for py_file in src_root.rglob("*.py"):
        try:
            with py_file.open("rb") as fp:
                tokens = list(tokenize.tokenize(fp.readline))
        except (SyntaxError, tokenize.TokenError):
            continue
        for tok in tokens:
            if tok.type != tokenize.COMMENT:
                continue
            if _FORBIDDEN_TYPE_IGNORE.search(tok.string):
                errors.append(
                    ValidationError(
                        type="type_ignores",
                        artifact=f"{py_file.relative_to(project_root).as_posix()}:{tok.start[0]}",
                        message=(
                            "`# type: ignore[<code>]` is not honored by ty. Use "
                            "bare `# type: ignore` or `# ty: ignore[<ty-code>]`."
                        ),
                    )
                )
    return errors


def audit_class_size(project_root: Path) -> list[ValidationError]:
    """Fail on classes whose body exceeds 300 lines (rule 21).

    Waivers are explicit in ``_CLASS_SIZE_WAIVERS`` and carry a rationale.
    """
    src_root = project_root / "src" / "gzkit"
    if not src_root.is_dir():
        return []
    limit = 300
    errors: list[ValidationError] = []
    extant: set[str] = set()
    for py_file in sorted(src_root.rglob("*.py")):
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        rel = py_file.relative_to(project_root).as_posix()
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            end = getattr(node, "end_lineno", node.lineno)
            span = end - node.lineno + 1
            key = f"{rel}::{node.name}"
            extant.add(key)
            if span <= limit:
                continue
            if key in _CLASS_SIZE_WAIVERS:
                continue
            errors.append(
                ValidationError(
                    type="class_size",
                    artifact=f"{rel}:{node.lineno}",
                    message=(
                        f"Class `{node.name}` spans {span} lines (>{limit}). "
                        "Split or add an explicit waiver with rationale in "
                        "`_CLASS_SIZE_WAIVERS` (`.gzkit/rules/pythonic.md`)."
                    ),
                )
            )
    for stale in sorted(_CLASS_SIZE_WAIVERS.keys() - extant):
        errors.append(
            ValidationError(
                type="class_size",
                artifact=f"CLASS_SIZE_WAIVERS::{stale}",
                message=(
                    f"Waiver `{stale}` references a class that no longer exists. "
                    "Remove the stale waiver."
                ),
            )
        )
    return errors


def audit_test_tiers(project_root: Path) -> list[ValidationError]:
    """Fail if a third test tier re-appears under ``tests/`` or CLI flags.

    GHI #182 removed ``tests/integration/`` and the ``--integration`` /
    ``--e2e`` / ``--slow`` flags on ``gz test``. The two runners —
    ``unittest`` over ``tests/`` and ``behave`` over ``features/`` — are the
    only test tiers. Any re-introduction is drift.
    """
    errors: list[ValidationError] = []
    forbidden_dirs = ("integration", "e2e", "slow", "bdd")
    tests_root = project_root / "tests"
    if tests_root.is_dir():
        for name in forbidden_dirs:
            path = tests_root / name
            if path.exists():
                errors.append(
                    ValidationError(
                        type="test_tiers",
                        artifact=path.relative_to(project_root).as_posix(),
                        message=(
                            f"Forbidden third test tier `tests/{name}/` — the "
                            "two runners are unittest and behave. See GHI #182."
                        ),
                    )
                )
    cli_root = project_root / "src" / "gzkit" / "cli"
    if cli_root.is_dir():
        forbidden_flags = ("--integration", "--e2e", "--slow", "--bdd-only")
        for py_file in sorted(cli_root.rglob("parser*.py")):
            try:
                text = py_file.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for flag in forbidden_flags:
                if flag in text:
                    errors.append(
                        ValidationError(
                            type="test_tiers",
                            artifact=py_file.relative_to(project_root).as_posix(),
                            message=(
                                f"Forbidden test-tier flag `{flag}` registered "
                                "on a parser — third test tier anti-pattern."
                            ),
                        )
                    )
    return errors
