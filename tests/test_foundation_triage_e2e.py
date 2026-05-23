"""E2E integration tests for OBPI-0.0.57-05 -- exercises OBPI-02, OBPI-03, OBPI-04 surfaces."""

from __future__ import annotations

import contextlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

from gzkit.traceability import covers

_REPO_ROOT = Path(__file__).parent.parent
_FIXTURE = _REPO_ROOT / "tests" / "fixtures" / "foundation_triage_e2e"
_TRIAGE_SCRIPT = _REPO_ROOT / ".gzkit" / "skills" / "gz-foundation-triage" / "scripts" / "triage.py"


class TestRubricScoringE2E(unittest.TestCase):
    """REQ-0.0.57-05-04: E2E rubric scoring via score_foundation (exercises OBPI-04 surface)."""

    @covers("REQ-0.0.57-05-04")
    def test_adr_0_0_1_scores_higher_than_adr_0_0_4(self) -> None:
        """ADR-0.0.1 (2 insights + 1 GHI) must outrank ADR-0.0.4 (zero signals)."""
        from gzkit.foundation.rubric import score_foundation

        entry_high = score_foundation(_FIXTURE, "ADR-0.0.1")
        entry_low = score_foundation(_FIXTURE, "ADR-0.0.4")
        self.assertGreater(
            entry_high.priority_score,
            entry_low.priority_score,
            msg=(
                f"ADR-0.0.1 score ({entry_high.priority_score}) must be greater than "
                f"ADR-0.0.4 score ({entry_low.priority_score})"
            ),
        )

    @covers("REQ-0.0.57-05-04")
    def test_adr_0_0_2_feature_unblocking_counted(self) -> None:
        """ADR-0.0.2 is blocked by a pool ADR; its feature_unblocking must be > 0."""
        from gzkit.foundation.rubric import score_foundation

        entry = score_foundation(_FIXTURE, "ADR-0.0.2")
        self.assertGreater(
            entry.priority_score,
            0,
            msg=f"ADR-0.0.2 priority_score expected > 0, got {entry.priority_score}",
        )
        unblocking_ref = next(r for r in entry.evidence if r.dimension == "feature_unblocking")
        self.assertGreater(
            unblocking_ref.count,
            0,
            msg="feature_unblocking count for ADR-0.0.2 must be >= 1 (pool ADR depends on it)",
        )


class TestNominalAllocatorE2E(unittest.TestCase):
    """REQ-0.0.57-05-04: E2E nominal allocator — gap suggestion (exercises OBPI-02 surface)."""

    @covers("REQ-0.0.57-05-04")
    def test_gap_fill_suggests_0_0_3(self) -> None:
        """When foundations 1, 2, 4 exist, plan create must suggest 0.0.3."""
        from gzkit.cli import main
        from tests.commands.common import CliRunner, _quick_init

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init(mode="heavy")
            # Stub foundation ADRs for IDs 1, 2, 4 — gap at 3
            foundation_root = Path("design/adr/foundation")
            for n in (1, 2, 4):
                adr_dir = foundation_root / f"ADR-0.0.{n}-fixture-{n}"
                adr_dir.mkdir(parents=True, exist_ok=True)
                (adr_dir / ".gitkeep").write_text("", encoding="utf-8")

            args = [
                "plan",
                "create",
                "gap-test",
                "--kind",
                "foundation",
                "--semver",
                "99.0.0",
                "--dry-run",
            ]
            result = runner.invoke(main, args)
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn(
                "0.0.3",
                result.output,
                msg=f"Expected gap suggestion '0.0.3' in output: {result.output!r}",
            )


class TestTriageScriptE2E(unittest.TestCase):
    """REQ-0.0.57-05-04: E2E triage script via subprocess (exercises OBPI-03 surface)."""

    @classmethod
    def setUpClass(cls) -> None:
        """Run triage script once and parse output for all tests in this class."""
        result = subprocess.run(
            [
                sys.executable,
                str(_TRIAGE_SCRIPT),
                "--format",
                "json",
                "--project-root",
                str(_FIXTURE),
            ],
            capture_output=True,
            text=True,
        )
        cls.triage_output = result.stdout
        cls.triage_returncode = result.returncode
        cls.triage_records: list[dict[str, object]] = []
        if result.returncode == 0:
            with contextlib.suppress(json.JSONDecodeError):
                cls.triage_records = json.loads(result.stdout)

    @covers("REQ-0.0.57-05-04")
    def test_json_output_shape(self) -> None:
        """Triage script --format json emits a non-empty list with required fields."""
        self.assertEqual(
            self.triage_returncode,
            0,
            msg=f"Triage script exited {self.triage_returncode}",
        )
        self.assertIsInstance(self.triage_records, list)
        self.assertGreater(len(self.triage_records), 0, msg="Expected at least one record")
        required_keys = {"id", "status", "title", "insight_count", "ghi_count"}
        for record in self.triage_records:
            missing = required_keys - set(record.keys())
            self.assertFalse(
                missing,
                msg=f"Record {record.get('id')!r} missing keys: {missing}",
            )

    @covers("REQ-0.0.57-05-04")
    def test_fixture_adr_0_0_1_present(self) -> None:
        """Triage output must include a record with id containing 'ADR-0.0.1'."""
        ids = [str(r.get("id", "")) for r in self.triage_records]
        self.assertTrue(
            any("ADR-0.0.1" in i for i in ids),
            msg=f"No record with id containing 'ADR-0.0.1'. Got: {ids}",
        )

    @covers("REQ-0.0.57-05-04")
    def test_fixture_adr_0_0_4_present(self) -> None:
        """Triage output must include a record with id containing 'ADR-0.0.4'."""
        ids = [str(r.get("id", "")) for r in self.triage_records]
        self.assertTrue(
            any("ADR-0.0.4" in i for i in ids),
            msg=f"No record with id containing 'ADR-0.0.4'. Got: {ids}",
        )


class TestDocsFixturesCoverageE2E(unittest.TestCase):
    """REQ-derived checks for documentation and fixture artifacts (OBPI-0.0.57-05)."""

    @covers("REQ-0.0.57-05-01")
    def test_plan_create_manpage_exists_and_covers_cli_audit(self) -> None:
        """plan-create.md must exist and cli audit must pass (101/101 commands covered)."""
        import io
        from contextlib import redirect_stderr, redirect_stdout

        from gzkit.cli import main

        manpage = _REPO_ROOT / "docs" / "user" / "manpages" / "plan-create.md"
        self.assertTrue(manpage.exists(), f"Missing manpage: {manpage}")
        buf = io.StringIO()
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                rc = main(["cli", "audit"])
            except SystemExit as e:
                rc = e.code
        self.assertEqual(rc, 0, msg=f"gz cli audit failed: {buf.getvalue()}")

    @covers("REQ-0.0.57-05-02")
    def test_foundation_triage_skill_doc_exists_with_template_form(self) -> None:
        """docs/user/skills/gz-foundation-triage.md must exist with heading, purpose, steps."""
        skill_doc = _REPO_ROOT / "docs" / "user" / "skills" / "gz-foundation-triage.md"
        self.assertTrue(skill_doc.exists(), f"Missing skill doc: {skill_doc}")
        content = skill_doc.read_text(encoding="utf-8")
        self.assertIn("gz-foundation-triage", content, "Skill name missing from doc")
        self.assertIn("Signal Dimensions", content, "Signal Dimensions section missing")
        self.assertIn("insight_count", content, "Triage output example fields missing")

    @covers("REQ-0.0.57-05-05")
    def test_nominal_example_in_plan_create_manpage(self) -> None:
        """plan-create.md must have nominal allocator section with real CLI output."""
        manpage = _REPO_ROOT / "docs" / "user" / "manpages" / "plan-create.md"
        content = manpage.read_text(encoding="utf-8")
        self.assertIn("Nominal Allocator", content, "Nominal Allocator section missing")
        self.assertIn(
            "Next\nfree nominal foundation ID:",
            content,
            "Real CLI output missing from plan-create.md",
        )

    @covers("REQ-0.0.57-05-06")
    def test_both_runbooks_contain_foundation_triage_section(self) -> None:
        """Both runbooks must contain foundation-triage content."""
        op_runbook = _REPO_ROOT / "docs" / "user" / "runbook.md"
        gov_runbook = _REPO_ROOT / "docs" / "governance" / "governance_runbook.md"
        self.assertIn(
            "Foundation Triage",
            op_runbook.read_text(encoding="utf-8"),
            "foundation-triage section missing from operator runbook",
        )
        self.assertIn(
            "foundation-triage",
            gov_runbook.read_text(encoding="utf-8").lower(),
            "foundation-triage content missing from governance runbook",
        )

    @covers("REQ-0.0.57-05-07")
    def test_skill_doc_example_contains_real_output_not_placeholder(self) -> None:
        """gz-foundation-triage.md must contain real CLI output, no placeholders."""
        skill_doc = _REPO_ROOT / "docs" / "user" / "skills" / "gz-foundation-triage.md"
        content = skill_doc.read_text(encoding="utf-8")
        self.assertNotIn("<output>", content, "Placeholder <output> found in skill doc")
        self.assertNotIn("<example output>", content, "Placeholder text found in skill doc")
        self.assertIn(
            "insight_count",
            content,
            "Real JSON output fields missing from skill doc example",
        )
        self.assertIn(
            "ghi_count",
            content,
            "Real JSON output fields missing from skill doc example",
        )


if __name__ == "__main__":
    unittest.main()
