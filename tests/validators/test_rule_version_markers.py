"""Behavior tests for the rule-version-marker validator.

These assert what ``audit_rule_version_markers`` *does* given a rules tree —
not what any shipped rule file contains. An earlier draft grepped
``.gzkit/rules/*.md`` directly and was correctly flagged by
``gz validate --tautological-test-audit``: a test that greps a production doc
proves content, not behavior (`.gzkit/rules/tests.md` § The discriminator).
The content invariant belongs to the validator (the SUPPORT channel's
structural arm); the validator's logic is what a unit test can prove.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.validators.rule_version_markers import (
    audit_rule_version_markers,
    canonical_rule_files,
    format_violation,
    run_rule_version_markers,
)

_GOOD = """---
id: sample
paths:
  - "**/*.py"
description: A well-formed rule
---

<!-- rule-version: 1.2.3 -->

# Sample

> **Rule version:** `1.2.3` — initial authoring.

Body.
"""

_NO_MARKER = """---
id: sample
paths:
  - "**/*.py"
description: A rule with no version marker
---

# Sample

Body with no marker at all.
"""

_DRIFTED = """---
id: sample
paths:
  - "**/*.py"
description: A rule whose marker and block quote disagree
---

<!-- rule-version: 2.0.0 -->

# Sample

> **Rule version:** `1.9.0` — bumped the comment, forgot the quote.
"""

_NO_BLOCKQUOTE = """---
id: sample
paths:
  - "**/*.py"
description: A rule with a marker but no visible block quote
---

<!-- rule-version: 3.1.0 -->

# Sample

Body with no visible version block quote.
"""


class RuleVersionMarkerAudit(unittest.TestCase):
    """The audit reports exactly the rules that break the invariant."""

    def _tree(self, **files: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        rules = root / ".gzkit" / "rules"
        rules.mkdir(parents=True)
        for name, text in files.items():
            (rules / f"{name}.md").write_text(text, encoding="utf-8")
        return root

    def test_well_formed_rule_produces_no_violation(self) -> None:
        root = self._tree(sample=_GOOD)
        self.assertEqual(audit_rule_version_markers(root), [])

    def test_missing_marker_is_reported(self) -> None:
        root = self._tree(sample=_NO_MARKER)
        violations = audit_rule_version_markers(root)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].reason, "missing-marker")
        self.assertEqual(violations[0].file, "sample.md")

    def test_marker_blockquote_drift_is_reported_with_both_versions(self) -> None:
        root = self._tree(sample=_DRIFTED)
        violations = audit_rule_version_markers(root)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].reason, "marker-blockquote-drift")
        self.assertEqual(violations[0].marker_version, "2.0.0")
        self.assertEqual(violations[0].blockquote_version, "1.9.0")

    def test_marker_without_blockquote_is_drift(self) -> None:
        root = self._tree(sample=_NO_BLOCKQUOTE)
        violations = audit_rule_version_markers(root)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].reason, "marker-blockquote-drift")
        self.assertIsNone(violations[0].blockquote_version)

    def test_package_internal_agents_md_is_exempt(self) -> None:
        """The generated concatenation is not an authored rule."""
        root = self._tree(sample=_GOOD)
        (root / ".gzkit" / "rules" / "AGENTS.md").write_text(_NO_MARKER, encoding="utf-8")
        self.assertEqual(audit_rule_version_markers(root), [])
        self.assertEqual(
            [p.name for p in canonical_rule_files(root / ".gzkit" / "rules")], ["sample.md"]
        )

    def test_absent_rules_dir_yields_no_files_rather_than_raising(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.assertEqual(audit_rule_version_markers(Path(tmp.name)), [])

    def test_violations_are_reported_per_file_not_collapsed(self) -> None:
        root = self._tree(good=_GOOD, bare=_NO_MARKER, drift=_DRIFTED)
        violations = audit_rule_version_markers(root)
        self.assertEqual(
            {(v.file, v.reason) for v in violations},
            {("bare.md", "missing-marker"), ("drift.md", "marker-blockquote-drift")},
        )


class RuleVersionMarkersScope(unittest.TestCase):
    """The scope runner's result carries a fail-closed exit code."""

    def _tree(self, **files: str) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        rules = root / ".gzkit" / "rules"
        rules.mkdir(parents=True)
        for name, text in files.items():
            (rules / f"{name}.md").write_text(text, encoding="utf-8")
        return root

    def test_clean_tree_passes_with_exit_zero(self) -> None:
        result = run_rule_version_markers(self._tree(sample=_GOOD))
        self.assertEqual(result.result, "pass")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.files_checked, 1)

    def test_violation_fails_closed_with_exit_three(self) -> None:
        result = run_rule_version_markers(self._tree(sample=_NO_MARKER))
        self.assertEqual(result.result, "fail")
        self.assertEqual(result.exit_code, 3)
        self.assertEqual(len(result.violations), 1)

    def test_format_violation_names_the_file_and_the_governing_clause(self) -> None:
        root = self._tree(sample=_NO_MARKER)
        message = format_violation(audit_rule_version_markers(root)[0])
        self.assertIn("sample.md", message)
        self.assertIn("skill-surface-sync", message)


if __name__ == "__main__":
    unittest.main()
