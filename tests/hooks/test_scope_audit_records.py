"""The scope audit holds delivered work against Allowed Paths, not gzkit's own records.

gzkit writes the ledger, handoffs, lock files and plan markers during every work
package. None is a brief's deliverable, so a refusal that counted them would
refuse every completion (GHI #1181). The brief being completed and its ADR
package's audit log are records of the same kind.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.hooks.obpi import brief_record_paths, out_of_scope_files, scope_finding
from gzkit.traceability import covers

_ALLOWLIST = ["src/gzkit/widget.py", "tests/widget/**"]
_ROOT = Path("/repo")
_BRIEF = _ROOT / "docs/design/adr/pre-release/ADR-0.1.0-demo/obpis/OBPI-0.1.0-01-demo.md"


class TestOutOfScopeFiles(unittest.TestCase):
    """REQ-0.11.0-02-01: out-of-allowlist changes are named; nothing else is."""

    @covers("REQ-0.11.0-02-01")
    def test_a_product_file_outside_allowed_paths_is_out_of_scope(self) -> None:
        changed = ["src/gzkit/widget.py", "src/gzkit/other.py", "docs/user/runbook.md"]
        self.assertEqual(
            out_of_scope_files(changed, _ALLOWLIST),
            ["src/gzkit/other.py", "docs/user/runbook.md"],
        )

    @covers("REQ-0.11.0-02-01")
    def test_files_inside_allowed_paths_are_in_scope(self) -> None:
        changed = ["src/gzkit/widget.py", "tests/widget/test_widget.py"]
        self.assertEqual(out_of_scope_files(changed, _ALLOWLIST), [])

    @covers("REQ-0.11.0-02-01")
    def test_gzkit_records_are_never_out_of_scope(self) -> None:
        changed = [
            ".gzkit/ledger.jsonl",
            ".gzkit/handoffs/20261010T000000Z-session-exit-bookmark.md",
            ".gzkit/locks/exchange/20261010T000000Z-OBPI-0.1.0-01-demo-complete.md",
            ".gzkit/insights/agent-insights.jsonl",
            ".gzkit/evidence/OBPI-0.1.0-01-demo.evidence.json",
            ".gzkit/ceremonies/ADR-0.1.0-demo.ceremony.json",
            ".claude/plans/.pipeline-active-OBPI-0.1.0-01-demo.json",
        ]
        self.assertEqual(out_of_scope_files(changed, _ALLOWLIST), [])

    @covers("REQ-0.11.0-02-01")
    def test_gzkit_canon_is_not_a_record(self) -> None:
        changed = [
            ".gzkit/skills/gz-demo/SKILL.md",
            ".gzkit/rules/tests.md",
            ".claude/settings.json",
        ]
        self.assertEqual(out_of_scope_files(changed, _ALLOWLIST), changed)

    @covers("REQ-0.11.0-02-01")
    def test_the_brief_and_its_package_log_are_records_of_that_package_only(self) -> None:
        own = brief_record_paths(_ROOT, _BRIEF)
        package = "docs/design/adr/pre-release/ADR-0.1.0-demo"
        changed = [
            f"{package}/obpis/OBPI-0.1.0-01-demo.md",
            f"{package}/logs/obpi-audit.jsonl",
            f"{package}/obpis/OBPI-0.1.0-02-sibling.md",
            f"{package}/ADR-0.1.0-demo.md",
        ]
        self.assertEqual(
            out_of_scope_files(changed, _ALLOWLIST, own_paths=own),
            [f"{package}/obpis/OBPI-0.1.0-02-sibling.md", f"{package}/ADR-0.1.0-demo.md"],
        )

    def test_a_brief_outside_the_project_has_no_record_paths(self) -> None:
        self.assertEqual(brief_record_paths(_ROOT, Path("/elsewhere/brief.md")), [])


class TestScopeFinding(unittest.TestCase):
    """The one finding `gz obpi precomplete` reports and `gz obpi complete` refuses on."""

    @covers("REQ-0.11.0-02-01")
    def test_no_out_of_scope_file_is_no_finding(self) -> None:
        self.assertIsNone(scope_finding({"out_of_scope_files": []}))

    @covers("REQ-0.11.0-02-01")
    def test_every_file_is_counted_and_a_long_list_is_cut_with_its_remainder(self) -> None:
        outside = [f"docs/outside-{n:02d}.md" for n in range(12)]
        finding = scope_finding({"out_of_scope_files": outside}) or ""
        self.assertIn("12 changed file(s)", finding)
        self.assertIn("docs/outside-09.md", finding)
        self.assertNotIn("docs/outside-10.md", finding)
        self.assertIn("(+2 more)", finding)


if __name__ == "__main__":
    unittest.main()
