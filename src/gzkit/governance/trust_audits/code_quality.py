"""Code-quality trust audits — ty type-ignore syntax, class size, test tier discipline.

* ``audit_type_ignores`` — a bracketed ``# type: ignore[...]`` naming no
  ``ty:``-prefixed code is unhonored by ty (GHI #197); bare ``# type: ignore``,
  ``# ty: ignore[<ty-code>]``, and the interop form
  ``# type: ignore[<mypy-code>, ty:<ty-code>]`` are all valid.
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

_TYPE_IGNORE_DIRECTIVE = re.compile(r"#\s*type:\s*ignore\[([^\]]*)\]")

_TYPE_IGNORE_MESSAGE = (
    "`# type: ignore[<code>]` carries no `ty:`-prefixed code, so ty honors "
    "nothing on this line — the marker reads as a suppression and is not one. "
    "Write `# ty: ignore[<ty-code>]`, or keep the foreign checker's code and "
    "add ty's alongside it: `# type: ignore[<mypy-code>, ty:<ty-code>]`. "
    "`.claude/rules/pythonic.md` § Type-check suppression syntax."
)

# Every tree whose comments are scanned. `src` alone was the defect, not merely
# a limitation: while this audit reported green, 188 dead markers across 73
# files accumulated under `tests` and 324 across 42 under `features`, making the
# form this rule forbids the most common suppression shape in the repo. A guard
# scoped away from a surface reads as covering it. `.claude/hooks` is canonical,
# not a generated mirror (`.gzkit/manifest.json` declares `"hooks":
# ".claude/hooks"`); `.agents` and `.github` are mirrors and are deliberately
# absent — a marker there is fixed at its source, not in the copy. `tests` and
# `features` join on the terms `_SUBPROCESS_AUDIT_ROOTS` states for its own late
# additions: excluded while their sites stood, because a guard reporting known
# failures every run trains readers to ignore it; covered once swept clean so a
# new marker cannot re-enter.
_TYPE_IGNORE_AUDIT_ROOTS: tuple[tuple[str, ...], ...] = (
    ("src",),
    ("tests",),
    ("scripts",),
    (".claude", "hooks"),
    ("features",),
)


def _has_no_ty_code(comment: str) -> bool:
    """Return True when a bracketed ``type: ignore`` directive names no ty rule.

    ty reads a ``type: ignore[...]`` directive and **skips every code lacking a
    ``ty:`` prefix**, so one comment can serve several checkers —
    ``# type: ignore[arg-type, ty:invalid-argument-type]`` suppresses in mypy
    *and* ty. A directive whose codes are all foreign therefore suppresses
    nothing in ty while reading exactly like a suppression: the GHI #197 defect.

    Do not "simplify" this back to a plain "does the comment contain a bracketed
    type: ignore" search — that flags the two interop forms ty genuinely honors,
    forcing readers to delete working suppressions. Verified against ty 0.0.69
    rather than inferred: ``# type: ignore[misc]`` left an ``invalid-assignment``
    error standing, while ``# type: ignore[ty:invalid-assignment]`` and
    ``# type: ignore[arg-type, ty:invalid-argument-type]`` both suppressed it.
    See https://docs.astral.sh/ty/suppression/ — *"codes without a `ty:` prefix
    are ignored, which makes it possible to combine suppressions for multiple
    type checkers in a single comment."*
    """
    return any(
        not any(code.strip().startswith("ty:") for code in body.split(","))
        for body in _TYPE_IGNORE_DIRECTIVE.findall(comment)
    )


def audit_type_ignores(project_root: Path) -> list[ValidationError]:
    """Fail on ``# type: ignore[<code>]`` naming no ty rule (GHI #197).

    Bracketed codes that ty cannot read suppress nothing — the markers look
    valid and are inert. The fix is ``# ty: ignore[<ty-code>]``, or the interop
    form ``# type: ignore[<mypy-code>, ty:<ty-code>]`` when another checker also
    reads the line. Bare ``# type: ignore`` remains valid and is not flagged.

    Scans every tree named in ``_TYPE_IGNORE_AUDIT_ROOTS``, not ``src`` alone;
    that narrower scope is what let 512 markers accumulate unseen.

    Uses ``tokenize`` so only real Python comments match — docstrings and
    string literals that happen to contain the literal pattern are ignored.
    """
    errors: list[ValidationError] = []
    for parts in _TYPE_IGNORE_AUDIT_ROOTS:
        root = project_root.joinpath(*parts)
        if not root.is_dir():
            continue
        for py_file in sorted(root.rglob("*.py")):
            try:
                with py_file.open("rb") as fp:
                    tokens = list(tokenize.tokenize(fp.readline))
            except (SyntaxError, tokenize.TokenError):
                continue
            errors.extend(
                ValidationError(
                    type="type_ignores",
                    artifact=f"{py_file.relative_to(project_root).as_posix()}:{tok.start[0]}",
                    message=_TYPE_IGNORE_MESSAGE,
                )
                for tok in tokens
                if tok.type == tokenize.COMMENT and _has_no_ty_code(tok.string)
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
