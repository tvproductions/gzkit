"""Skill-shape tests for `.gzkit/skills/complexity-guide/SKILL.md`.

Pins REQ-0.0.30-02-01 through REQ-0.0.30-02-06 from
`docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-02-complexity-guide-skill.md`.

REQ-07 (tests cover all above) is satisfied by the existence of test classes
below. REQ-08 (TDD, no subprocess spawn) is structural. REQ-09 (no PII)
is asserted by TestNoOperatorPersonalEmail without @covers.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import cast

import yaml

from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = PROJECT_ROOT / ".gzkit" / "skills" / "complexity-guide"
SKILL_PATH = SKILL_DIR / "SKILL.md"

VENDOR_MIRROR_PATHS = (
    PROJECT_ROOT / ".claude" / "skills" / "complexity-guide" / "SKILL.md",
    PROJECT_ROOT / ".agents" / "skills" / "complexity-guide" / "SKILL.md",
    PROJECT_ROOT / ".github" / "skills" / "complexity-guide" / "SKILL.md",
)


def _read_skill_text() -> str:
    return SKILL_PATH.read_text(encoding="utf-8")


def _parse_frontmatter(text: str) -> dict[str, object]:
    if not text.startswith("---\n"):
        raise AssertionError("skill file does not begin with YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise AssertionError("skill file frontmatter block is not closed")
    return cast(dict[str, object], yaml.safe_load(text[4:end]))


def _section_body(text: str, heading: str) -> str:
    """Return the body between an H2 heading and the next H2/EOF."""
    pattern = rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s+\S|\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.DOTALL)
    if match is None:
        raise AssertionError(f"H2 section not found: '## {heading}'")
    return match.group(1)


class TestSkillFrontmatter(unittest.TestCase):
    """REQ-0.0.30-02-01 — frontmatter validates against skill schema."""

    @covers("REQ-0.0.30-02-01")
    def test_frontmatter_required_identity_fields_present(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(fm.get("name"), "complexity-guide")
        description = fm.get("description")
        self.assertIsInstance(description, str)
        self.assertGreaterEqual(len(str(description or "")), 40)
        self.assertLessEqual(len(str(description or "")), 1024)

    @covers("REQ-0.0.30-02-01")
    def test_frontmatter_lifecycle_fields_present(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(fm.get("lifecycle_state"), "active")
        self.assertEqual(fm.get("owner"), "gzkit-governance")
        self.assertRegex(str(fm.get("last_reviewed", "")), r"^\d{4}-\d{2}-\d{2}$")

    @covers("REQ-0.0.30-02-01")
    def test_skill_version_is_initial_release(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        metadata = fm.get("metadata")
        self.assertIsInstance(metadata, dict)
        meta = cast(dict[str, object], metadata)
        self.assertEqual(str(meta.get("skill-version", "")), "0.1.0")

    @covers("REQ-0.0.30-02-01")
    def test_description_triggers_on_operator_phrases(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        description = str(fm.get("description", "")).lower()
        self.assertIn(
            "authoring-time",
            description,
            "description must mention 'authoring-time' to trigger discovery",
        )
        self.assertIn(
            "complexity",
            description,
            "description must mention 'complexity' to trigger discovery",
        )
        self.assertTrue(
            "hint" in description or "preview" in description,
            "description must mention 'hint' or 'preview' to trigger discovery",
        )


class TestOperatorMoment(unittest.TestCase):
    """REQ-0.0.30-02-02 — body documents ad-hoc authoring-time review as primary surface."""

    @covers("REQ-0.0.30-02-02")
    def test_ad_hoc_authoring_time_review_named_as_primary_surface(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)authoring[- ]time",
            "Skill body must document the authoring-time review moment",
        )
        self.assertIn(
            "gz complexity guide",
            text,
            "Operator moment section must show the CLI invocation",
        )

    @covers("REQ-0.0.30-02-02")
    def test_first_stop_authoring_surface_named(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)first[- ]stop",
            "Skill body must name this as the first-stop authoring surface",
        )


class TestOutputContract(unittest.TestCase):
    """REQ-0.0.30-02-03 — Output Contract declares in-line hint prose + --json."""

    @covers("REQ-0.0.30-02-03")
    def test_output_contract_section_present(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertGreater(
            len(body.strip()),
            40,
            "Output Contract section must be substantive",
        )

    @covers("REQ-0.0.30-02-03")
    def test_output_contract_names_inline_hint_prose_as_default(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertRegex(
            body,
            r"(?i)in[- ]line hint prose",
            "Output Contract must name in-line hint prose as the default form",
        )

    @covers("REQ-0.0.30-02-03")
    def test_output_contract_names_json_as_machine_readable(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertIn(
            "--json",
            body,
            "Output Contract must name --json as the machine-readable mode",
        )


class TestGzCommandResolution(unittest.TestCase):
    """REQ-0.0.30-02-04 — gz_command resolves to a registered CLI verb (Invariant 1)."""

    @covers("REQ-0.0.30-02-04")
    def test_gz_command_field_set_to_complexity_guide(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(
            fm.get("gz_command"),
            "complexity guide",
            "gz_command must declare the registered CLI verb",
        )

    @covers("REQ-0.0.30-02-04")
    def test_declared_verb_resolves_in_live_argparse_parser(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        with self.assertRaises(SystemExit) as captured:
            parser.parse_args(["complexity", "guide", "--help"])
        self.assertEqual(
            captured.exception.code,
            0,
            "gz_command 'complexity guide' must resolve to a registered subparser",
        )


class TestCrossReference(unittest.TestCase):
    """REQ-0.0.30-02-05 — cross-reference to complexity-advisor with trigger-time distinction."""

    @covers("REQ-0.0.30-02-05")
    def test_complexity_advisor_sister_skill_named(self) -> None:
        text = _read_skill_text()
        self.assertIn(
            "complexity-advisor",
            text,
            "Skill body must cross-reference the complexity-advisor sister skill",
        )

    @covers("REQ-0.0.30-02-05")
    def test_trigger_time_vs_authoring_time_distinction_present(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)trigger[- ]time",
            "Skill body must name the trigger-time vs authoring-time distinction",
        )
        self.assertRegex(
            text,
            r"(?i)authoring[- ]time",
            "Skill body must name the authoring-time surface",
        )


class TestVendorMirrorEquality(unittest.TestCase):
    """REQ-0.0.30-02-06 — vendor mirrors are byte-equal after sync."""

    @covers("REQ-0.0.30-02-06")
    def test_each_vendor_mirror_matches_canonical(self) -> None:
        canonical = SKILL_PATH.read_bytes()
        for mirror in VENDOR_MIRROR_PATHS:
            self.assertTrue(
                mirror.exists(),
                f"vendor mirror missing: {mirror.relative_to(PROJECT_ROOT).as_posix()} "
                "(run `gz agent sync control-surfaces`)",
            )
            self.assertEqual(
                mirror.read_bytes(),
                canonical,
                "vendor mirror diverges from canonical: "
                f"{mirror.relative_to(PROJECT_ROOT).as_posix()} "
                "(run `gz agent sync control-surfaces`)",
            )


class TestNoOperatorPersonalEmail(unittest.TestCase):
    """REQ-09 doctrine assertion (no @covers — doctrine constraint)."""

    def test_skill_contains_no_personal_email_addresses(self) -> None:
        text = _read_skill_text()
        candidate_addresses = re.findall(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            text,
        )
        for address in candidate_addresses:
            self.assertTrue(
                address.endswith("@users.noreply.github.com"),
                f"non-noreply email found in skill body: {address!r} "
                "(see AGENTS.md § Local Agent Rules — Operator PII)",
            )

    def test_test_module_contains_no_personal_email_addresses(self) -> None:
        text = Path(__file__).read_text(encoding="utf-8")
        candidate_addresses = re.findall(
            r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            text,
        )
        for address in candidate_addresses:
            self.assertTrue(
                address.endswith("@users.noreply.github.com"),
                f"non-noreply email found in test module: {address!r}",
            )


if __name__ == "__main__":
    unittest.main()
