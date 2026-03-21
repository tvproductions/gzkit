"""Tests for red-team prompt composition and result parsing."""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.adr_eval_redteam import (
    CHALLENGE_NAMES,
    compose_adr_redteam_prompt,
    load_framework_redteam_prompt,
    parse_redteam_result,
)


class TestComposeRedTeamPrompt(unittest.TestCase):
    def test_includes_adr_content(self) -> None:
        prompt = compose_adr_redteam_prompt(
            adr_content="# My ADR",
            obpi_contents=[("OBPI-01", "# Brief 1")],
            framework_prompt="You are a red-team reviewer.",
        )
        self.assertIn("# My ADR", prompt)
        self.assertIn("OBPI-01", prompt)
        self.assertIn("You are a red-team reviewer", prompt)

    def test_includes_response_format(self) -> None:
        prompt = compose_adr_redteam_prompt(
            adr_content="content",
            obpi_contents=[],
            framework_prompt="prompt",
        )
        self.assertIn("challenge_number", prompt)
        self.assertIn("All 10 challenges", prompt)

    def test_multiple_obpis(self) -> None:
        prompt = compose_adr_redteam_prompt(
            adr_content="adr",
            obpi_contents=[("A", "content-a"), ("B", "content-b")],
            framework_prompt="prompt",
        )
        self.assertIn("OBPI: A", prompt)
        self.assertIn("OBPI: B", prompt)


class TestParseRedTeamResult(unittest.TestCase):
    def _make_output(self, challenges: list[dict]) -> str:
        return f"Here are the results:\n```json\n{json.dumps({'challenges': challenges})}\n```"

    def test_parses_valid_10_challenges(self) -> None:
        challenges = [
            {
                "challenge_number": i,
                "challenge_name": CHALLENGE_NAMES[i - 1],
                "passed": i <= 8,
                "notes": f"Notes for {i}",
            }
            for i in range(1, 11)
        ]
        result = parse_redteam_result(self._make_output(challenges))
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 10)
        self.assertTrue(result[0].passed)
        self.assertFalse(result[8].passed)

    def test_returns_none_on_missing_json(self) -> None:
        self.assertIsNone(parse_redteam_result("No JSON here."))

    def test_returns_none_on_malformed_json(self) -> None:
        self.assertIsNone(parse_redteam_result("```json\n{bad json}\n```"))

    def test_returns_none_on_wrong_count(self) -> None:
        challenges = [
            {"challenge_number": i, "challenge_name": f"C{i}", "passed": True, "notes": ""}
            for i in range(1, 6)
        ]
        self.assertIsNone(parse_redteam_result(self._make_output(challenges)))

    def test_returns_none_on_missing_fields(self) -> None:
        challenges = [{"challenge_number": i} for i in range(1, 11)]
        self.assertIsNone(parse_redteam_result(self._make_output(challenges)))

    def test_parses_flat_array(self) -> None:
        challenges = [
            {
                "challenge_number": i,
                "challenge_name": CHALLENGE_NAMES[i - 1],
                "passed": True,
                "notes": "",
            }
            for i in range(1, 11)
        ]
        output = f"```json\n{json.dumps(challenges)}\n```"
        result = parse_redteam_result(output)
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 10)


class TestLoadFrameworkPrompt(unittest.TestCase):
    def test_raises_on_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(FileNotFoundError):
            load_framework_redteam_prompt(Path(tmp))

    def test_loads_from_real_assets(self) -> None:
        assets = Path(".claude/skills/gz-adr-eval/assets")
        if not assets.exists():
            self.skipTest("Skill assets not available")
        prompt = load_framework_redteam_prompt(assets)
        self.assertIn("red team", prompt.lower())
        self.assertIn("ADR DOCUMENT", prompt)


if __name__ == "__main__":
    unittest.main()
