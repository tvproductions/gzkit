"""Structural coverage for OBPI-0.0.35-04 documentation/feature REQs.

These tests assert artifact presence/shape, not validator behavior.

REQ bindings here were shifted one place off the brief from the day the file
was authored (repaired under GHI #944). The original docstring said the file
existed to "satisfy the REQ-coverage gate ... so `gz obpi complete` does not
require waiver flags" — and the gate matches REQ *id strings* found anywhere
under `tests/`, never the subject a test asserts. Written to clear that gate,
three artifact tests were mapped onto the last three REQ numbers by position:
behave->09, manpage->10, runbook->11. The brief's last four are 08 behave,
09 manpage, 10 runbook, 11 ARB-receipts-in-the-closeout-commit. REQ-11 is the
one REQ here that no artifact test can prove, so shifting the window by one
displaced exactly the requirement that was inconvenient, and made the gap
invisible for four months.

Each binding below now names the REQ whose subject the test actually asserts.
"""

from __future__ import annotations

import ast
import json
import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

#: The OBPI whose REQs this file provides structural coverage for.
OBPI_ID = "OBPI-0.0.35-04-kind-invariance-validator"


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

#: Tests that exercise this scope but prove no REQ of this brief, so they owe
#: no `@covers`. Demanding one would force a fabricated claim — the exact
#: defect the shifted bindings above came from. Each entry states what the
#: test proves instead; the set must stay small and justified, never a
#: convenience hatch for a test nobody wants to bind.
NON_REQ_TESTS: dict[str, str] = {
    # Asserts `.gzkit/rules/tests.md` § Tests assert semantics, not strings.
    # No REQ of this brief states that discipline.
    "test_validator_tests_assert_semantics_not_strings": (
        "repo-wide test-quality discipline, not a requirement of this brief"
    ),
}


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
    return owing - _covered_test_methods(path) - set(NON_REQ_TESTS)


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

    @covers("REQ-0.0.35-04-08")
    def test_behave_scenario_tagged_with_req(self):
        """features/kind_invariance.feature carries @REQ-0.0.35-04-NN tags."""
        feature = PROJECT_ROOT / "features" / "kind_invariance.feature"
        content = feature.read_text(encoding="utf-8")
        tags = re.findall(r"@REQ-0\.0\.35-04-\d+", content)
        self.assertGreater(len(tags), 0, "feature file must carry @REQ-0.0.35-04-NN tags")

    @covers("REQ-0.0.35-04-09")
    def test_manpage_documents_kind_invariance(self):
        """docs/user/manpages/validate.md lists --kind-invariance with example."""
        manpage = PROJECT_ROOT / "docs" / "user" / "manpages" / "validate.md"
        content = manpage.read_text(encoding="utf-8")
        self.assertIn("--kind-invariance", content)
        self.assertIn("gz validate --kind-invariance", content)

    @covers("REQ-0.0.35-04-10")
    def test_runbook_cross_references_kind_invariance(self):
        """docs/user/runbook.md references the kind-invariance verification step."""
        runbook = PROJECT_ROOT / "docs" / "user" / "runbook.md"
        content = runbook.read_text(encoding="utf-8")
        self.assertIn("--kind-invariance", content)

    @covers("REQ-0.0.35-04-11")
    def test_closeout_evidence_cites_arb_receipts(self):
        """This OBPI's closeout evidence resolves all five ARB receipt classes.

        REQ-11 originally named "the closeout commit body" as the surface. No
        commit in this repo cites this OBPI's receipt ids — the work landed in
        git-sync chores — so it was unmet as written, and the shifted bindings
        repaired under GHI #944 had hidden that by parking the runbook test in
        its slot. The receipts were never missing; the requirement named the
        wrong surface for evidence that existed, and was amended 2026-09-04 to
        name the ledger event that actually carries it.

        Asserts the receipt *classes* AGENTS.md § Attestation names, not the
        receipt ids: an id is a run of a command, the class is the claim.
        """
        required_classes = {
            "arb-ruff",
            "arb-step-typecheck",
            "arb-step-unittest",
            "arb-step-coverage",
            "arb-step-mkdocs",
        }
        ledger = PROJECT_ROOT / ".gzkit" / "ledger.jsonl"

        bound: set[str] = set()
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if OBPI_ID not in line:
                continue
            event = json.loads(line)
            evidence = event.get("evidence") or {}
            if (
                event.get("event") != "audit_receipt_emitted"
                or event.get("receipt_event") != "meta-receipt-bind"
                or evidence.get("obpi_id") != OBPI_ID
                or evidence.get("exit_status") != 0
            ):
                continue
            bound |= {
                receipt_id.rsplit("-", 1)[0]
                for receipt_id in evidence.get("resolved_receipt_ids", [])
            }

        self.assertFalse(
            required_classes - bound,
            f"closeout evidence for {OBPI_ID} resolves no receipt for: "
            f"{sorted(required_classes - bound)}",
        )

    def test_validator_tests_assert_semantics_not_strings(self):
        """`test_kind_invariance.py` asserts error type and shape, not message bytes.

        Carries no `@covers`, deliberately. This asserts the discipline in
        `.gzkit/rules/tests.md` § Tests assert semantics, not strings — which no
        REQ of this brief states. It previously claimed REQ-07 ("every test for
        this scope is decorated with `@covers`"), a subject it does not touch.
        A test that proves no requirement must not claim one; see
        `NON_REQ_TESTS` for why the fence exempts it rather than forcing a
        fabricated binding (GHI #944).
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

    @covers("REQ-0.0.35-04-07")
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
