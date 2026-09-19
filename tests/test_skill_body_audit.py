"""Countable skill-body authoring contracts (GHI #1037)."""

import tempfile
import unittest
from pathlib import Path

from gzkit.skills import scaffold_skill
from gzkit.skills_audit import _validate_canonical_skill


class TestSkillBodyAudit(unittest.TestCase):
    def test_scaffold_is_reported_unfinished_until_authored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = scaffold_skill(root, "demo", ".gzkit/skills")
            issues = []
            _validate_canonical_skill(root, issues, "demo", path.parent, 90)
            self.assertTrue(any(i.code == "SKA-BODY-UNFINISHED" and i.blocking for i in issues))
            text = path.read_text(encoding="utf-8")
            for number in (1, 2, 3):
                text = text.replace(
                    f"Step {number}", f"Verify condition {number} and stop on failure."
                )
            path.write_text(text, encoding="utf-8")
            issues = []
            _validate_canonical_skill(root, issues, "demo", path.parent, 90)
            self.assertFalse(any(i.code == "SKA-BODY-UNFINISHED" for i in issues))

    def test_markers_are_distinguished_from_substantive_or_quoted_examples(self) -> None:
        from gzkit.skills_audit import _unfinished_body_lines

        for marker in (
            "1. Step 1",
            "- Example input",
            "Constraint 2",
            "Skill 1",
            "TODO: author",
            "TODO author the procedure",
            "TBD",
            "FIXME: proof",
        ):
            with self.subTest(marker=marker):
                self.assertEqual(_unfinished_body_lines(marker), [1])
        for content in (
            "1. Step 1: verify the signed receipt.",
            "Discuss TODO markers with the operator.",
            "> TODO: example",
            "```text\n1. Step 1\n```",
            "~~~text\nTBD\n~~~",
        ):
            with self.subTest(content=content):
                self.assertEqual(_unfinished_body_lines(content), [])

    def test_fenced_examples_close_only_with_matching_character_length_and_suffix(self) -> None:
        from gzkit.skills_audit import _unfinished_body_lines

        for opener, inner, closer in (
            ("````markdown", "```text", "````"),
            ("~~~~markdown", "~~~text", "~~~~"),
            ("```text", "~~~", "```"),
            ("~~~text", "```", "~~~"),
            ("```text", "```not-a-closer", "`````   "),
            ("~~~text", "~~~not-a-closer", "~~~~~   "),
        ):
            with self.subTest(opener=opener, inner=inner, closer=closer):
                body = "\n".join(
                    (opener, inner, "TODO: quoted example", closer, "TODO: unfinished")
                )
                self.assertEqual(_unfinished_body_lines(body), [5])

    def test_size_boundaries_and_grandfather_growth(self) -> None:
        from unittest.mock import patch

        from gzkit.skill_contract import SKILL_BODY_MAX_LINES
        from gzkit.skills_audit import _validate_skill_body

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "SKILL.md"
            for name, lines, blocking, expected in (
                ("new", SKILL_BODY_MAX_LINES, False, False),
                ("new", SKILL_BODY_MAX_LINES + 1, True, True),
                ("old", SKILL_BODY_MAX_LINES + 1, False, True),
                ("old", SKILL_BODY_MAX_LINES + 2, True, True),
            ):
                with self.subTest(name=name, lines=lines):
                    path.write_text("Instruction.\n" * lines, encoding="utf-8")
                    issues = []
                    with patch(
                        "gzkit.skills_audit.SKILL_BODY_GRANDFATHER",
                        {"old": SKILL_BODY_MAX_LINES + 1},
                    ):
                        _validate_skill_body(
                            root, issues, path, {"name": name, "lifecycle_state": "active"}
                        )
                    self.assertEqual(bool(issues), expected)
                    if expected:
                        self.assertEqual(issues[0].blocking, blocking)
                        self.assertEqual(issues[0].code, "SKA-BODY-OVERSIZED")


class TestSkillAuditWarningRendering(unittest.TestCase):
    def test_success_displays_warning_code_path_and_reason(self) -> None:
        # output-contract: a nonblocking finding must identify what needs repair.
        from io import StringIO
        from unittest.mock import patch

        from rich.console import Console

        from gzkit.commands.skills_cmd import _print_skill_audit_success, _skill_audit_counts
        from gzkit.skills import SkillAuditIssue, SkillAuditReport

        issue = SkillAuditIssue(
            severity="warning",
            code="SKA-BODY-OVERSIZED",
            path=".gzkit/skills/demo/SKILL.md",
            message="Body exceeds the declared ceiling.",
            blocking=False,
        )
        report = SkillAuditReport(
            valid=True, issues=[issue], checked_skills=1, checked_roots=[".gzkit/skills"]
        )
        output = StringIO()
        with patch(
            "gzkit.commands.skills_cmd.console", Console(file=output, width=160, color_system=None)
        ):
            _print_skill_audit_success(report, 90, _skill_audit_counts(report))
        for detail in (issue.code, issue.path, issue.message):
            self.assertIn(detail, output.getvalue())


class TestSkillBodyBaseline(unittest.TestCase):
    def test_packaged_ceilings_only_shrink_against_committed_baseline(self) -> None:
        """Pre-commit check: a source edit cannot add exemptions or raise ceilings."""
        import json
        import subprocess

        from gzkit.skill_contract import SKILL_BODY_GRANDFATHER
        from tests.commands.common import _isolated_git_env

        root = Path(__file__).resolve().parents[1]
        relative = "src/gzkit/skill_body_grandfather.json"
        previous = subprocess.run(
            ["git", "show", f"HEAD:{relative}"],
            cwd=root,
            env=_isolated_git_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if previous.returncode:
            self.skipTest("No committed cutover baseline yet (or Git history unavailable).")
        old = json.loads(previous.stdout)
        current = SKILL_BODY_GRANDFATHER
        self.assertLessEqual(current.keys(), old.keys(), "Grandfather entries may only be removed.")
        for name, ceiling in current.items():
            self.assertLessEqual(ceiling, old[name], f"{name}: ceiling may only decrease.")


class TestSkillBodyLifecycle(unittest.TestCase):
    def test_draft_warns_active_blocks_retired_is_excluded(self) -> None:
        from gzkit.skills_audit import _validate_skill_body

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "SKILL.md"
            path.write_text("1. Step 1\n", encoding="utf-8")
            for state, count, blocking in (
                ("draft", 1, False),
                ("active", 1, True),
                ("deprecated", 1, True),
                ("retired", 0, False),
            ):
                with self.subTest(state=state):
                    issues = []
                    _validate_skill_body(
                        root, issues, path, {"name": "demo", "lifecycle_state": state}
                    )
                    self.assertEqual(len(issues), count)
                    if count:
                        self.assertEqual(issues[0].blocking, blocking)

    def test_frontmatter_does_not_spend_body_budget(self) -> None:
        from gzkit.skill_contract import SKILL_BODY_MAX_LINES
        from gzkit.skills_audit import _validate_skill_body

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "SKILL.md"
            path.write_text(
                "---\nname: demo\n"
                + "# metadata commentary\n" * 50
                + "---\n"
                + "Instruction.\n" * SKILL_BODY_MAX_LINES,
                encoding="utf-8",
            )
            issues = []
            _validate_skill_body(root, issues, path, {"name": "demo", "lifecycle_state": "active"})
            self.assertEqual(issues, [])


class TestSkillScaffoldAuditOutput(unittest.TestCase):
    def test_new_skill_audit_reports_unfinished_procedure(self) -> None:
        # output-contract: scaffold production must connect to actionable audit output.
        from io import StringIO
        from unittest.mock import patch

        from rich.console import Console

        from gzkit.commands.skills_cmd import skill_audit_cmd, skill_new
        from gzkit.config import GzkitConfig

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(project_name="demo")
            output = StringIO()
            with (
                patch("gzkit.commands.skills_cmd.ensure_initialized", return_value=config),
                patch("gzkit.commands.skills_cmd.get_project_root", return_value=root),
                patch(
                    "gzkit.commands.skills_cmd.console",
                    Console(file=output, width=160, color_system=None),
                ),
            ):
                skill_new("demo", "An unfinished procedure.")
                with self.assertRaises(SystemExit) as caught:
                    skill_audit_cmd(False, False, 90)
            self.assertEqual(caught.exception.code, 1)
            self.assertIn("SKA-BODY-UNFINISHED", output.getvalue())
            self.assertIn(".gzkit/skills/demo/SKILL.md", output.getvalue())
