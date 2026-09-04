"""Structural coverage for OBPI-0.0.35-04 documentation/feature REQs.

These tests assert artifact presence/shape, not validator behavior. They
satisfy the REQ-coverage gate for REQ-09 (behave scenario tagged), REQ-10
(manpage updated), REQ-11 (runbook updated) so `gz obpi complete` does not
require waiver flags for them.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


#: Files whose entire subject is the kind-invariance scope. Every test in one
#: of these is "a test for this scope" by construction.
SCOPE_OWNED_TEST_FILES = (
    PROJECT_ROOT / "tests" / "governance" / "test_kind_invariance.py",
    PROJECT_ROOT / "tests" / "governance" / "test_kind_invariance_docs.py",
)

#: General-purpose files that host tests for many scopes at once. Membership
#: here is decided per method, never per file.
SHARED_TEST_FILES = (
    PROJECT_ROOT / "tests" / "commands" / "test_validate.py",
    PROJECT_ROOT / "tests" / "commands" / "test_quality.py",
)

#: What makes a method in a shared file a test *for this scope*: it exercises
#: the validator this OBPI built. A test that never names it is not one.
SCOPE_MARKERS = ("kind_invariance", "kind-invariance")

COVERS_RE = re.compile(r"REQ-0\.0\.35-04-\d+")


def _test_functions(path: Path) -> list[ast.FunctionDef]:
    """Every `test_*` function defined in one test module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]


def _test_methods(path: Path) -> set[str]:
    """Names of every test method in one module."""
    return {node.name for node in _test_functions(path)}


def _covered_test_methods(path: Path) -> set[str]:
    """Tests carrying an `@covers("REQ-0.0.35-04-NN")` decorator."""
    return {
        node.name
        for node in _test_functions(path)
        if any(COVERS_RE.search(ast.unparse(d)) for d in node.decorator_list)
    }


def _scope_test_methods(path: Path) -> set[str]:
    """Tests in a shared module that actually exercise the kind-invariance scope."""
    source = path.read_text(encoding="utf-8")
    scoped = set()
    for node in _test_functions(path):
        segment = ast.get_source_segment(source, node) or ""
        if any(marker in segment for marker in SCOPE_MARKERS):
            scoped.add(node.name)
    return scoped


def _uncovered_tests(path: Path, *, scope_only: bool) -> set[str]:
    """Tests owing `@covers` that do not carry it."""
    owing = _scope_test_methods(path) if scope_only else _test_methods(path)
    return owing - _covered_test_methods(path)


def fence_roster() -> list[tuple[Path, bool]]:
    """Each file the fence checks, paired with whether it is scoped per-method.

    This is the fence's policy in one place, so a guard can observe it rather
    than infer it. `True` means "only the tests in this file that exercise the
    scope owe `@covers`"; `False` means the whole file does, which is only
    honest for a file whose entire subject is the scope.
    """
    return [(path, False) for path in SCOPE_OWNED_TEST_FILES] + [
        (path, True) for path in SHARED_TEST_FILES
    ]


class TestKindInvarianceArtifacts(unittest.TestCase):
    """Verify the documentation/feature artifacts the brief requires."""

    @covers("REQ-0.0.35-04-09")
    def test_behave_scenario_tagged_with_req(self):
        """features/kind_invariance.feature carries @REQ-0.0.35-04-NN tags."""
        feature = PROJECT_ROOT / "features" / "kind_invariance.feature"
        content = feature.read_text(encoding="utf-8")
        tags = re.findall(r"@REQ-0\.0\.35-04-\d+", content)
        self.assertGreater(len(tags), 0, "feature file must carry @REQ-0.0.35-04-NN tags")

    @covers("REQ-0.0.35-04-10")
    def test_manpage_documents_kind_invariance(self):
        """docs/user/manpages/validate.md lists --kind-invariance with example."""
        manpage = PROJECT_ROOT / "docs" / "user" / "manpages" / "validate.md"
        content = manpage.read_text(encoding="utf-8")
        self.assertIn("--kind-invariance", content)
        self.assertIn("gz validate --kind-invariance", content)

    @covers("REQ-0.0.35-04-11")
    def test_runbook_cross_references_kind_invariance(self):
        """docs/user/runbook.md references the kind-invariance verification step."""
        runbook = PROJECT_ROOT / "docs" / "user" / "runbook.md"
        content = runbook.read_text(encoding="utf-8")
        self.assertIn("--kind-invariance", content)

    @covers("REQ-0.0.35-04-07")
    def test_validator_tests_assert_semantics_not_strings(self):
        """REQ-07: tests in test_kind_invariance.py assert on error type and shape,
        not on pinned error message bytes. Mechanical proxy: no assertion against
        a quoted substring of the validator's error messages.
        """
        test_file = PROJECT_ROOT / "tests" / "governance" / "test_kind_invariance.py"
        content = test_file.read_text(encoding="utf-8")
        # Anti-pattern: assertIn("specific bytes from the validator", ...)
        forbidden_pinned_phrases = [
            "Foundation ADR is missing",
            "Foundation ADR has a",
            "Recovery: add",
            "Recovery: replace",
        ]
        for phrase in forbidden_pinned_phrases:
            self.assertNotIn(
                phrase,
                content,
                f"REQ-07 violation: test_kind_invariance.py pins validator error string {phrase!r}",
            )

    @covers("REQ-0.0.35-04-08")
    def test_every_obpi_test_carries_covers_decorator(self):
        """Every test *for this scope* carries `@covers("REQ-0.0.35-04-NN")`.

        The requirement's subject is "every test for this scope", not "every
        test in a file this OBPI happened to touch". Those are different sets,
        and the difference is load-bearing: `test_validate.py` and
        `test_quality.py` are general-purpose files that accrue tests for
        every `gz validate` and `gz check` concern. Asserting over every method
        in them closed both files to any unrelated test — a defect fix for
        `gz validate` output rendering (GHI #944) had to be moved to a separate
        file, and the only alternative on offer was a fabricated `@covers`.

        So membership is decided two ways. A file whose entire subject is this
        scope contributes all of its tests. A shared file contributes only the
        methods that actually exercise the scope.
        """
        for path, scope_only in fence_roster():
            uncovered = _uncovered_tests(path, scope_only=scope_only)
            self.assertFalse(
                uncovered,
                f"tests without @covers in {path.name}: {sorted(uncovered)}",
            )


if __name__ == "__main__":
    unittest.main()
