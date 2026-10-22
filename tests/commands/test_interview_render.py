"""`gz interview <type> --from` renders each document type from complete answers.

GHI #1259: the OBPI door rendered the `obpi` template with the interview answers
alone, so every variable `gz specify` computes was missing and the strict render
(GHI #741) refused it. Both doors now share `obpi_template_vars`.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from gzkit.cli import main
from gzkit.commands import interview_cmd
from gzkit.ledger import Ledger
from tests.commands.common import CliRunner, _quick_init


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    _, block, _ = text.split("---\n", 2)
    return yaml.safe_load(block)


class TestInterviewObpiRendersFromCompleteAnswers(unittest.TestCase):
    """An OBPI authored from a full answer set carries the answers and the ADR item."""

    ANSWERS = {
        "id": "OBPI-0.1.0-01-f",
        "title": "F",
        "parent": "ADR-0.1.0-f",
        "item": "1",
        "lane": "lite",
        "objective": "Do f.",
        "allowed_paths": "1. `src/f.py` - the module\n2. `tests/test_f.py` - its test",
        "denied_paths": "1. `docs/` - out of scope",
        "acceptance_criteria": "1. f returns its input\n2. f rejects None",
    }

    def _author(self, runner: CliRunner, answers: dict, confirm: bool = False) -> tuple[int, str]:
        created = runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
        self.assertEqual(created.exit_code, 0, msg=created.output)
        Path("a.json").write_text(json.dumps(answers), encoding="utf-8")
        with patch.object(interview_cmd, "_confirm", return_value=confirm):
            result = runner.invoke(main, ["interview", "obpi", "--from", "a.json"])
        return result.exit_code, result.output

    def test_brief_is_written_with_the_answered_identity(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            exit_code, output = self._author(runner, self.ANSWERS)
            self.assertEqual(exit_code, 0, msg=output)

            brief = Path("design/adr/pre-release/ADR-0.1.0-f/obpis/OBPI-0.1.0-01-f.md")
            self.assertTrue(brief.is_file(), msg=output)
            front = _frontmatter(brief)
            self.assertEqual(front["id"], self.ANSWERS["id"])
            self.assertEqual(front["parent"], "ADR-0.1.0-f")
            self.assertEqual(front["item"], 1)

            created = [
                e
                for e in Ledger(Path(".gzkit/ledger.jsonl")).read_all()
                if e.event == "obpi_created"
            ]
            self.assertEqual([e.id for e in created], [self.ANSWERS["id"]])

    def test_authored_sections_drive_body_and_frontmatter(self) -> None:
        """The answers replace the inferred sections, and the frontmatter lists
        derive from what the body renders (GHI #615), so the two cannot disagree."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            exit_code, output = self._author(runner, self.ANSWERS)
            self.assertEqual(exit_code, 0, msg=output)

            brief = Path("design/adr/pre-release/ADR-0.1.0-f/obpis/OBPI-0.1.0-01-f.md")
            front = _frontmatter(brief)
            self.assertEqual(front["allowlist"], ["src/f.py", "tests/test_f.py"])
            self.assertEqual(front["reqs"], ["REQ-0.1.0-01-01", "REQ-0.1.0-01-02"])

            body = brief.read_text(encoding="utf-8")
            self.assertIn("REQ-0.1.0-01-01: f returns its input", body)
            self.assertIn("REQ-0.1.0-01-02: f rejects None", body)
            self.assertIn("`docs/` - out of scope", body)

    def test_unanswered_sections_fall_back_to_the_specify_inference(self) -> None:
        """An empty section answer gets what `gz specify` would infer, not a blank."""
        answers = {**self.ANSWERS, "acceptance_criteria": ""}
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            # An empty answer leaves the interview incomplete; the operator confirms.
            exit_code, output = self._author(runner, answers, confirm=True)
            self.assertEqual(exit_code, 0, msg=output)

            brief = Path("design/adr/pre-release/ADR-0.1.0-f/obpis/OBPI-0.1.0-01-f.md")
            reqs = _frontmatter(brief)["reqs"]
            self.assertEqual(reqs, ["REQ-0.1.0-01-01", "REQ-0.1.0-01-02", "REQ-0.1.0-01-03"])

    def test_an_item_the_parent_adr_lacks_is_refused(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            exit_code, output = self._author(runner, {**self.ANSWERS, "item": "99"})
            self.assertNotEqual(exit_code, 0)
            self.assertIn("out of range", output.replace("\n", " "))
            self.assertFalse(
                Path("design/adr/pre-release/ADR-0.1.0-f/obpis").exists()
                and any(Path("design/adr/pre-release/ADR-0.1.0-f/obpis").iterdir())
            )


class TestInterviewPrdAndAdrRenderFromCompleteAnswers(unittest.TestCase):
    """The sibling doors render their scaffolding templates from complete answers."""

    def test_prd(self) -> None:
        answers = {
            "id": "PRD-F-1.0.0",
            "title": "F",
            "semver": "1.0.0",
            "problem_statement": "Nobody can do f.",
            "north_star": "Everyone can do f.",
            "invariants": "1. f stays pure",
            "out_of_scope": "1. g",
        }
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            Path("a.json").write_text(json.dumps(answers), encoding="utf-8")
            result = runner.invoke(main, ["interview", "prd", "--from", "a.json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            prds = list(Path(".").rglob("PRD-F-1.0.0.md"))
            self.assertEqual(len(prds), 1, msg=result.output)
            self.assertIn("Nobody can do f.", prds[0].read_text(encoding="utf-8"))

    def test_adr(self) -> None:
        answers = {
            "id": "ADR-0.2.0-g",
            "title": "G",
            "semver": "0.2.0",
            "lane": "lite",
            "parent": "PRD-F-1.0.0",
            "intent": "g is needed.",
            "decision": "Build g.",
            "positive_consequences": "1. g exists",
            "negative_consequences": "1. g costs",
            "checklist": "1. Build g",
            "alternatives": "No g: rejected.",
            "pre_mortem": "g failed because h.",
            "wwhtbt": "h holds.",
            "constraint_archaeology": "Real.",
            "assumption_surfacing": "h.",
            "operator_2am": "A log.",
            "reversibility": "Two-way.",
            "scope_minimization": "g only.",
            "downstream_adrs": "None.",
        }
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            Path("a.json").write_text(json.dumps(answers), encoding="utf-8")
            result = runner.invoke(main, ["interview", "adr", "--from", "a.json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr = Path("design/adr/pre-release/ADR-0.2.0-g/ADR-0.2.0-g.md")
            self.assertTrue(adr.is_file(), msg=result.output)
            self.assertIn("g failed because h.", adr.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
