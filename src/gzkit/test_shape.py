"""Advisory test-shape inventory (GHI #571).

Two read-only screens over ``tests/``, neither of which ever gates:

1. **Tautological operations** — delegated to :mod:`gzkit.tautological_tests`, whose
   fail-closed validator blocks *growth* against a shrink-ratchet baseline. That gate
   proves no new content-echo test appears; it never tells an operator what debt
   remains, and it exposes no per-disposition roll-up. This module supplies one.

2. **Output/render assertions** — a test that asserts on ``result.output``, a captured
   ``stdout``/``stderr``, a ``.getvalue()``, or via ``assertRegex`` /
   ``assertMultiLineEqual``. Most such tests are legitimate: ``.gzkit/rules/tests.md``
   § Output-form fixture carve-out permits render-contract assertions, and
   ``tool-skill-runbook-alignment.md`` § Invariant 3 *requires* some of them.

**This screen is advisory and must stay advisory.** 125 files match today. Fail-closing
on it would redden a green trunk against tests the doctrine explicitly allows. What it
reports instead is whether the carve-out was *declared* — by an ``# output-contract:``
comment inside the test, or by a class named ``*OutputForm`` / ``*OutputContract`` /
``*Rendering``. Undeclared is a prompt to classify, never a verdict.
"""

from __future__ import annotations

import ast
import re
from collections import Counter
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.tautological_tests import propose_disposition, scan_test_tree

#: Attribute names that name a captured render surface.
_OUTPUT_ATTRS: frozenset[str] = frozenset({"output", "stdout", "stderr"})

#: Assertion methods whose very use implies a string/render comparison.
_RENDER_ASSERTIONS: frozenset[str] = frozenset({"assertRegex", "assertMultiLineEqual"})

#: Class-name suffixes that declare the output-form fixture carve-out.
_DECLARING_CLASS_SUFFIXES: tuple[str, ...] = ("OutputForm", "OutputContract", "Rendering")

_MARKER_RE = re.compile(r"#\s*output-contract:\s*(?P<reason>.+?)\s*$")

_FIXTURE_METHODS: frozenset[str] = frozenset(
    {"setUp", "tearDown", "setUpClass", "tearDownClass", "setUpModule", "tearDownModule"}
)


class OutputAssertion(BaseModel):
    """One test function that asserts on rendered output."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Repo-relative POSIX path")
    line_number: int = Field(..., ge=1)
    function_name: str = Field(..., min_length=1)
    class_name: str | None = Field(default=None, description="Enclosing TestCase class")
    source_kind: str = Field(
        ..., description="output | stdout | stderr | getvalue | assertRegex | ..."
    )
    declared: bool = Field(..., description="Carve-out declared by marker or class name")
    marker_reason: str | None = Field(default=None, description="Text after `# output-contract:`")


class TautologicalOp(BaseModel):
    """One tautological-shaped operation, with its proposed disposition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str
    line_number: int
    function_name: str
    operation_kind: str
    disposition: str


class TestShapeInventory(BaseModel):
    """The advisory roll-up. Never a gate."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tautological: list[TautologicalOp]
    output_assertions: list[OutputAssertion]

    @property
    def by_disposition(self) -> dict[str, int]:
        """Disposition roll-up.

        This is the structure GHI #571's predecessor receipt cited as evidence
        ("hundreds of candidates") but which never existed anywhere in the codebase.
        """
        return dict(Counter(op.disposition for op in self.tautological))

    @property
    def undeclared_output_assertions(self) -> list[OutputAssertion]:
        """Output assertions with no declared carve-out — a prompt to classify, not a verdict."""
        return [a for a in self.output_assertions if not a.declared]


def _marker_reason(lines: list[str], start: int, end: int) -> str | None:
    """Return the `# output-contract:` reason within a function's line span, if any."""
    for raw in lines[start - 1 : end]:
        match = _MARKER_RE.search(raw)
        if match:
            return match.group("reason")
    return None


def _output_source(node: ast.AST) -> str | None:
    """Name the render surface a node touches, or None."""
    if isinstance(node, ast.Attribute) and node.attr in _OUTPUT_ATTRS:
        return node.attr
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            if func.attr == "getvalue":
                return "getvalue"
            if func.attr in _RENDER_ASSERTIONS:
                return func.attr
    return None


def _has_assertion(fn: ast.FunctionDef) -> bool:
    """Return True when the function makes any assertion at all."""
    for node in ast.walk(fn):
        if isinstance(node, ast.Assert):
            return True
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr.startswith("assert")
        ):
            return True
    return False


def _declaring_class(class_name: str | None) -> bool:
    return class_name is not None and class_name.endswith(_DECLARING_CLASS_SUFFIXES)


def _scan_one_file(path: Path, project_root: Path) -> list[OutputAssertion]:
    """Flag each test function that asserts on rendered output."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
    except (OSError, SyntaxError):
        return []

    lines = source.splitlines()
    rel = path.relative_to(project_root).as_posix()
    found: list[OutputAssertion] = []

    for cls in [None, *[n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]]:
        scope = tree if cls is None else cls
        for fn in ast.iter_child_nodes(scope):
            if not isinstance(fn, ast.FunctionDef) or fn.name in _FIXTURE_METHODS:
                continue
            if not _has_assertion(fn):
                continue
            kinds = {k for node in ast.walk(fn) if (k := _output_source(node)) is not None}
            if not kinds:
                continue
            end = fn.end_lineno or fn.lineno
            reason = _marker_reason(lines, fn.lineno, end)
            class_name = cls.name if cls is not None else None
            found.append(
                OutputAssertion(
                    file_path=rel,
                    line_number=fn.lineno,
                    function_name=fn.name,
                    class_name=class_name,
                    source_kind=",".join(sorted(kinds)),
                    declared=reason is not None or _declaring_class(class_name),
                    marker_reason=reason,
                )
            )
    return found


def scan_output_assertions(tests_path: Path, project_root: Path) -> list[OutputAssertion]:
    """Scan ``tests_path`` for test functions asserting on rendered output."""
    if not tests_path.is_dir():
        return []
    results: list[OutputAssertion] = []
    for path in sorted(tests_path.rglob("test_*.py")):
        results.extend(_scan_one_file(path, project_root))
    return sorted(results, key=lambda a: (a.file_path, a.line_number))


def build_inventory(project_root: Path) -> TestShapeInventory:
    """Build the advisory test-shape inventory for ``project_root``."""
    tests_path = project_root / "tests"
    ops = [
        TautologicalOp(
            file_path=op.file_path,
            line_number=op.line_number,
            function_name=op.function_name,
            operation_kind=op.operation_kind,
            disposition=propose_disposition(op).value,
        )
        for op in scan_test_tree(tests_path)
    ]
    ops.sort(key=lambda o: (o.file_path, o.line_number))
    return TestShapeInventory(
        tautological=ops,
        output_assertions=scan_output_assertions(tests_path, project_root),
    )


__all__ = [
    "OutputAssertion",
    "TautologicalOp",
    "TestShapeInventory",
    "build_inventory",
    "scan_output_assertions",
]
