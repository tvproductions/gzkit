"""Skill-shape tests for `.gzkit/skills/gz-justify/SKILL.md` (OBPI-0.0.19-04).

Pins REQ-01, REQ-02, REQ-03, REQ-04, REQ-09 from the brief. All tests read the
canonical skill path read-only — no test mutates `.gzkit/skills/` or
`.claude/skills/` at the live repo (REQ-10).
"""

from __future__ import annotations

import re
import unittest
from datetime import UTC, datetime
from pathlib import Path

import yaml

from gzkit.hooks.obpi import verify_gz_chain
from gzkit.justify.anchors import resolve_anchor
from gzkit.justify.models import EvidenceBundle
from gzkit.justify.walkthrough import render_markdown, render_scaffold
from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = PROJECT_ROOT / ".gzkit" / "skills" / "gz-justify" / "SKILL.md"

REQUIRED_H2_SECTIONS_IN_ORDER = (
    "Purpose",
    "Common Rationalizations",
    "Red Flags",
    "Persona",
    "Trust Model",
    "Invocation",
    "When to Use",
    "Procedure",
    "Acceptance Criteria",
    "Related Skills",
)


def _read_skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def _parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        raise AssertionError("skill file does not begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("skill file frontmatter block is not closed")
    return yaml.safe_load(text[4:end])


class TestGzJustifyFrontmatter(unittest.TestCase):
    """REQ-0.0.19-04-01 — frontmatter has all required keys with expected values."""

    @covers("REQ-0.0.19-04-01")
    def test_frontmatter_required_keys_present(self) -> None:
        text = _read_skill_text()
        fm = _parse_frontmatter(text)

        self.assertEqual(fm.get("name"), "gz-justify")
        self.assertEqual(fm.get("persona"), "main-session")
        self.assertIsInstance(fm.get("description"), str)
        self.assertGreaterEqual(len(str(fm.get("description", ""))), 40)
        self.assertEqual(fm.get("category"), "obpi-pipeline")
        self.assertEqual(fm.get("lifecycle_state"), "active")
        self.assertEqual(fm.get("owner"), "gzkit-governance")
        self.assertIsInstance(fm.get("last_reviewed"), str)
        self.assertRegex(str(fm.get("last_reviewed", "")), r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(fm.get("gz_command"), "justify")

        metadata = fm.get("metadata")
        self.assertIsInstance(metadata, dict)
        assert isinstance(metadata, dict)
        self.assertRegex(str(metadata.get("skill-version", "")), r"^6\.")
        self.assertEqual(metadata.get("govzero-framework-version"), "v6")


class TestGzJustifyBodyShape(unittest.TestCase):
    """REQ-0.0.19-04-02 / REQ-0.0.19-04-03 — H2 sections in order + Red Flag row."""

    @covers("REQ-0.0.19-04-02")
    def test_body_sections_appear_in_order(self) -> None:
        text = _read_skill_text()
        h2_headings = [
            line[3:].strip()
            for line in text.splitlines()
            if line.startswith("## ") and not line.startswith("### ")
        ]
        indices = []
        for expected in REQUIRED_H2_SECTIONS_IN_ORDER:
            self.assertIn(
                expected,
                h2_headings,
                f"H2 section missing: '## {expected}'",
            )
            indices.append(h2_headings.index(expected))
        self.assertEqual(
            indices,
            sorted(indices),
            f"H2 sections out of order. got={h2_headings} "
            f"expected={list(REQUIRED_H2_SECTIONS_IN_ORDER)}",
        )

    @covers("REQ-0.0.19-04-03")
    def test_red_flags_section_names_fabrication(self) -> None:
        text = _read_skill_text()
        red_flag_match = re.search(
            r"^##\s+Red Flags\s*$(.*?)(?=^##\s+\w|\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(red_flag_match, "Red Flags section not found")
        assert red_flag_match is not None
        body = red_flag_match.group(1)
        self.assertRegex(
            body,
            r"(?i)fabricat",
            "Red Flags section must name fabrication as a red flag (REQ-03)",
        )


class TestGzJustifyCommandResolves(unittest.TestCase):
    """REQ-0.0.19-04-04 — `gz_command: justify` resolves via verify_gz_chain."""

    @covers("REQ-0.0.19-04-04")
    def test_gz_command_resolves_via_verify_chain(self) -> None:
        ok, reason = verify_gz_chain(["justify"])
        self.assertTrue(
            ok,
            f"gz_command 'justify' must resolve against the parser (reason={reason})",
        )


class TestGzJustifyOutputContract(unittest.TestCase):
    """REQ-0.0.19-04-09 — rendered scaffold begins with `---` or H1 (Invariant 3)."""

    @covers("REQ-0.0.19-04-09")
    def test_justify_first_line_is_frontmatter_or_h1(self) -> None:
        anchor = resolve_anchor(
            None,
            draft_text="test draft for output-contract check",
            draft_slug="test-output-contract",
        )
        evidence = EvidenceBundle(
            anchor=anchor,
            matching_rules=(),
            ledger_events=(),
            recent_commits=(),
            related_anchors=(),
            taxonomy_reference="docs/governance/model-regression-taxonomy.md",
            warnings=(),
        )
        walkthrough = render_scaffold(
            anchor,
            evidence,
            now=datetime(2026, 4, 22, tzinfo=UTC),
        )
        markdown = render_markdown(walkthrough)
        first_line = next(
            (line for line in markdown.splitlines() if line.strip()),
            "",
        )
        self.assertTrue(
            first_line == "---" or first_line.startswith("# "),
            f"first non-empty line must be '---' or start with '# '; got {first_line!r}",
        )


if __name__ == "__main__":
    unittest.main()
