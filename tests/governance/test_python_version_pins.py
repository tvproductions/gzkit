"""Interpreter-pin coherence audit (`gz validate --python-version-pins`).

The audit exists because the interpreter version was declared in five places
with nothing holding them in agreement. These tests assert the semantics of
that agreement, not the wording of any message.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.python_version_pins import (
    audit_python_version_pins,
    evaluate_python_version_pins,
)


class TestPinAgreement(unittest.TestCase):
    """Every declaration must equal the authoritative `.python-version`."""

    def test_agreeing_declarations_produce_no_finding(self) -> None:
        errors = evaluate_python_version_pins(
            "3.13.15",
            [("ci.yml:55", "3.13.15"), ("release.yml:46", "3.13.15")],
            "3.13",
        )
        self.assertEqual(errors, [])

    def test_a_differing_patch_level_is_a_finding(self) -> None:
        errors = evaluate_python_version_pins("3.13.15", [("ci.yml:55", "3.13.14")], "3.13")
        self.assertEqual(len(errors), 1)
        self.assertEqual(
            errors[0].artifact,
            "ci.yml:55",
            "the finding must name the disagreeing site, not the pin file",
        )

    def test_a_minor_only_declaration_is_a_finding(self) -> None:
        """`python-version: "3.13"` resolves to whatever patch the runner picks."""
        errors = evaluate_python_version_pins("3.13.15", [("docs.yml:31", "3.13")], "3.13")
        self.assertEqual(len(errors), 1, "a minor-only pin is the drift this audit exists to catch")

    def test_each_disagreeing_site_gets_its_own_finding(self) -> None:
        errors = evaluate_python_version_pins(
            "3.13.15",
            [("a.yml:1", "3.13.14"), ("b.yml:2", "3.13.15"), ("c.yml:3", "3.13")],
            None,
        )
        self.assertEqual(
            {e.artifact for e in errors},
            {"a.yml:1", "c.yml:3"},
            "agreeing sites must not be reported, disagreeing ones must be",
        )


class TestFloorIsNotAPin(unittest.TestCase):
    """`requires-python` is a floor; comparing it for equality would be wrong."""

    def test_pin_above_the_floor_is_accepted(self) -> None:
        errors = evaluate_python_version_pins("3.13.15", [], "3.13")
        self.assertEqual(errors, [], "a patch pin above a minor floor is the normal, correct state")

    def test_pin_below_the_floor_is_a_finding(self) -> None:
        errors = evaluate_python_version_pins("3.12.9", [], "3.13")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].artifact, ".python-version")

    def test_absent_floor_is_not_an_error(self) -> None:
        errors = evaluate_python_version_pins("3.13.15", [("ci.yml:1", "3.13.15")], None)
        self.assertEqual(errors, [])


class TestMissingAuthority(unittest.TestCase):
    """Declarations with no pin to agree with are incoherent, not merely unchecked."""

    def test_declarations_without_a_pin_are_a_finding(self) -> None:
        errors = evaluate_python_version_pins(None, [("ci.yml:55", "3.13.15")], "3.13")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].artifact, ".python-version")

    def test_no_pin_and_no_declarations_is_silent(self) -> None:
        """A project that pins nothing anywhere is coherent, if unpinned."""
        self.assertEqual(evaluate_python_version_pins(None, [], None), [])


class TestAdapterReadsTheTree(unittest.TestCase):
    """The adapter must find declarations by scanning, not from a hardcoded list."""

    def _tree(self, root: Path, pin: str, workflow_body: str) -> None:
        (root / ".python-version").write_text(f"{pin}\n", encoding="utf-8")
        (root / "pyproject.toml").write_text('requires-python = ">=3.13"\n', encoding="utf-8")
        wf = root / ".github" / "workflows"
        wf.mkdir(parents=True)
        (wf / "ci.yml").write_text(workflow_body, encoding="utf-8")

    def test_a_drifted_workflow_is_detected_end_to_end(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "3.13.15", '        python-version: "3.13.14"\n')
            errors = audit_python_version_pins(root)
        self.assertEqual(len(errors), 1)
        self.assertTrue(
            errors[0].artifact.startswith(".github/workflows/ci.yml:"),
            f"finding must locate the site by path:line, got {errors[0].artifact!r}",
        )

    def test_a_newly_added_workflow_is_covered_without_editing_the_audit(self) -> None:
        """Scanning the directory is what makes a new workflow covered by default."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "3.13.15", '        python-version: "3.13.15"\n')
            extra = root / ".github" / "workflows" / "brand-new.yml"
            extra.write_text("        run: uv python install 3.13.9\n", encoding="utf-8")
            errors = audit_python_version_pins(root)
        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].artifact.startswith(".github/workflows/brand-new.yml:"))

    def test_the_uv_install_form_is_recognised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._tree(root, "3.13.15", "        run: uv python install 3.13.15\n")
            self.assertEqual(audit_python_version_pins(root), [])


if __name__ == "__main__":
    unittest.main()
