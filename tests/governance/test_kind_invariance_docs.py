"""Structural coverage for OBPI-0.0.35-04 documentation/feature REQs.

These tests assert artifact presence/shape, not validator behavior. They
satisfy the REQ-coverage gate for REQ-09 (behave scenario tagged), REQ-10
(manpage updated), REQ-11 (runbook updated) so `gz obpi complete` does not
require waiver flags for them.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


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
        """REQ-08: every test method in OBPI-0.0.35-04's test files carries @covers."""
        target_files = [
            PROJECT_ROOT / "tests" / "governance" / "test_kind_invariance.py",
            PROJECT_ROOT / "tests" / "governance" / "test_kind_invariance_docs.py",
            PROJECT_ROOT / "tests" / "commands" / "test_validate.py",
            PROJECT_ROOT / "tests" / "commands" / "test_quality.py",
        ]
        for tf in target_files:
            content = tf.read_text(encoding="utf-8")
            test_methods = re.findall(r"    def (test_\w+)\(", content)
            covers_decorators = re.findall(
                r'@covers\("REQ-0\.0\.35-04-\d+"\)\s*\n\s*def (test_\w+)\(',
                content,
            )
            uncovered = set(test_methods) - set(covers_decorators)
            self.assertFalse(
                uncovered,
                f"REQ-08 violation: tests without @covers in {tf.name}: {uncovered}",
            )


if __name__ == "__main__":
    unittest.main()
