"""Fixture-level tests for ``audit_instructions_files_budget`` (GHI #373).

These tests pin the scan semantics — at-budget passes, +1 char is reported —
and isolate the audit from the live AGENTS.md / CLAUDE.md / .claude/rules/.

**Posture: advisory until 1.0** (operator ruling 2026-08-17, verbatim: *"temporary
stay of all control surface budget limits until version 1.0. I want to be warned,
and we may lift the limits as needed, but no blockers."*). The two properties that
must hold together are therefore in tension by design, and each is asserted
separately: an overrun is still MEASURED and REPORTED, and it contributes NO
finding. A test that only checked the empty return would pass against an audit
that had stopped looking, which is the failure mode the stay must not become.
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_instructions_files_budget


def _run(root: Path) -> tuple[list[object], str]:
    """Run the audit, returning (findings, captured advisory stream)."""
    buffer = io.StringIO()
    with contextlib.redirect_stderr(buffer):
        findings = audit_instructions_files_budget(root)
    return list(findings), buffer.getvalue()


class InstructionsFilesBudgetAuditTests(unittest.TestCase):
    """Audit walks AGENTS.md / CLAUDE.md / glob-matched rule files."""

    def _write_budget(
        self, root: Path, files: dict[str, int], globs: list[dict[str, object]] | None = None
    ) -> None:
        target = root / "data" / "instructions_files_budget.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {"files": files}
        if globs is not None:
            payload["globs"] = globs
        target.write_text(json.dumps(payload), encoding="utf-8")

    def test_at_budget_boundary_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 100, encoding="utf-8")
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertNotIn("AGENTS.md", advisories)

    def test_overrun_contributes_no_finding(self) -> None:
        """The stay: an overrun must not change the exit code."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 101, encoding="utf-8")
            findings, _ = _run(root)
            self.assertEqual(findings, [])

    def test_overrun_is_still_measured_and_reported(self) -> None:
        """The stay suspends the consequence, never the observation."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100})
            (root / "AGENTS.md").write_text("x" * 175, encoding="utf-8")
            _, advisories = _run(root)
            self.assertIn("AGENTS.md", advisories)
            self.assertIn("175", advisories)
            self.assertIn("100", advisories)
            self.assertIn("75", advisories)

    def test_overrun_advisory_names_the_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 10})
            (root / "AGENTS.md").write_text("x" * 11, encoding="utf-8")
            _, advisories = _run(root)
            self.assertIn("gz-context-diet", advisories)

    def test_under_budget_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"CLAUDE.md": 100})
            (root / "CLAUDE.md").write_text("x" * 50, encoding="utf-8")
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertNotIn("CLAUDE.md", advisories)

    def test_missing_file_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 100, "CLAUDE.md": 100})
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertEqual(advisories, "")

    def test_glob_arm_reports_only_the_overrunning_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "ok.md").write_text("x" * 100, encoding="utf-8")
            (rules / "fat.md").write_text("x" * 200, encoding="utf-8")
            self._write_budget(
                root, {}, [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 100}]
            )
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertIn("fat.md", advisories)
            self.assertNotIn("ok.md", advisories)

    def test_glob_no_matches_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(
                root, {}, [{"pattern": ".claude/rules/*.md", "max_chars_per_file": 100}]
            )
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertEqual(advisories, "")

    def test_missing_budget_data_uses_packaged_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text("x" * 100, encoding="utf-8")
            findings, advisories = _run(root)
            self.assertEqual(findings, [])
            self.assertEqual(advisories, "")

    def test_budgets_stay_per_file_so_they_can_be_lifted_individually(self) -> None:
        """ "we may lift the limits as needed" — the data file stays the dial."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_budget(root, {"AGENTS.md": 10, "CLAUDE.md": 10_000})
            (root / "AGENTS.md").write_text("x" * 50, encoding="utf-8")
            (root / "CLAUDE.md").write_text("x" * 50, encoding="utf-8")
            _, advisories = _run(root)
            self.assertIn("AGENTS.md", advisories)
            self.assertNotIn("CLAUDE.md", advisories)


if __name__ == "__main__":
    unittest.main()
