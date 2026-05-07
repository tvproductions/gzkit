"""Skill-shape tests for `.gzkit/skills/complexity-advisor/SKILL.md`.

Pins REQ-0.0.29-04-01 through REQ-0.0.29-04-06 from
`docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-04-complexity-advisor-skill.md`.

REQ-07 (tests cover all above) is satisfied by the existence of test classes
below. REQ-08 (TDD, no subprocess spawn) is structural. REQ-09 (no PII)
is asserted by TestNoOperatorPersonalEmail without @covers — it is a
doctrine constraint not enumerated in Acceptance Criteria.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import cast

import yaml

from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = PROJECT_ROOT / ".gzkit" / "skills" / "complexity-advisor"
SKILL_PATH = SKILL_DIR / "SKILL.md"

VENDOR_MIRROR_PATHS = (
    PROJECT_ROOT / ".claude" / "skills" / "complexity-advisor" / "SKILL.md",
    PROJECT_ROOT / ".agents" / "skills" / "complexity-advisor" / "SKILL.md",
    PROJECT_ROOT / ".github" / "skills" / "complexity-advisor" / "SKILL.md",
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
    """REQ-0.0.29-04-01 — frontmatter validates against skill schema."""

    @covers("REQ-0.0.29-04-01")
    def test_frontmatter_required_identity_fields_present(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(fm.get("name"), "complexity-advisor")
        description = fm.get("description")
        self.assertIsInstance(description, str)
        self.assertGreaterEqual(len(str(description or "")), 40)
        self.assertLessEqual(len(str(description or "")), 1024)

    @covers("REQ-0.0.29-04-01")
    def test_frontmatter_lifecycle_fields_present(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(fm.get("lifecycle_state"), "active")
        self.assertEqual(fm.get("owner"), "gzkit-governance")
        self.assertRegex(str(fm.get("last_reviewed", "")), r"^\d{4}-\d{2}-\d{2}$")

    @covers("REQ-0.0.29-04-01")
    def test_skill_version_is_initial_release(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        metadata = fm.get("metadata")
        self.assertIsInstance(metadata, dict)
        meta = cast(dict[str, object], metadata)
        self.assertEqual(str(meta.get("skill-version", "")), "0.1.0")

    @covers("REQ-0.0.29-04-01")
    def test_description_triggers_on_operator_phrases(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        description = str(fm.get("description", "")).lower()
        for phrase in ("complexity", "advisor", "diagnosis"):
            self.assertIn(
                phrase,
                description,
                f"description must mention '{phrase}' to trigger discovery",
            )


class TestThreeOperatorMoments(unittest.TestCase):
    """REQ-0.0.29-04-02 — body documents all three operator moments."""

    @covers("REQ-0.0.29-04-02")
    def test_ad_hoc_preview_before_fail_documented(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)ad[- ]?hoc|preview[- ]before[- ]fail",
            "Skill body must document the ad-hoc preview-before-fail moment",
        )
        self.assertIn(
            "gz complexity advise",
            text,
            "Ad-hoc section must show the CLI invocation",
        )

    @covers("REQ-0.0.29-04-02")
    def test_auto_chain_context_documented(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)auto[- ]?chain",
            "Skill body must document the auto-chain context moment",
        )
        self.assertIn(
            "--auto-chain",
            text,
            "Auto-chain section must reference the --auto-chain flag",
        )

    @covers("REQ-0.0.29-04-02")
    def test_intrinsic_attestation_guidance_documented(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)intrinsic[- ]?complexity",
            "Skill body must document intrinsic-complexity attestation",
        )
        self.assertIn(
            "@intrinsic_complexity",
            text,
            "Intrinsic section must reference the decorator path",
        )
        self.assertIn(
            "--attest-intrinsic",
            text,
            "Intrinsic section must reference the commit-time flag path",
        )


class TestOutputContract(unittest.TestCase):
    """REQ-0.0.29-04-03 — Output Contract declares structured prose + --json."""

    @covers("REQ-0.0.29-04-03")
    def test_output_contract_section_present(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertGreater(
            len(body.strip()),
            40,
            "Output Contract section must be substantive",
        )

    @covers("REQ-0.0.29-04-03")
    def test_output_contract_names_structured_prose_as_default(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertRegex(
            body,
            r"(?i)structured prose",
            "Output Contract must name structured prose as the default form",
        )

    @covers("REQ-0.0.29-04-03")
    def test_output_contract_names_json_as_machine_readable(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertIn(
            "--json",
            body,
            "Output Contract must name --json as the machine-readable mode",
        )


class TestCrossReferences(unittest.TestCase):
    """REQ-0.0.29-04-04 — skill cross-references runbook and manpage."""

    @covers("REQ-0.0.29-04-04")
    def test_runbook_cross_reference_present(self) -> None:
        text = _read_skill_text()
        self.assertIn(
            "docs/user/runbook.md",
            text,
            "Skill body must cross-reference the runbook",
        )

    @covers("REQ-0.0.29-04-04")
    def test_manpage_cross_reference_present(self) -> None:
        text = _read_skill_text()
        self.assertIn(
            "docs/user/manpages/gz-complexity-advise.md",
            text,
            "Skill body must cross-reference the manpage",
        )


class TestVerbResolution(unittest.TestCase):
    """REQ-0.0.29-04-05 — gz_command resolves to a registered CLI verb."""

    @covers("REQ-0.0.29-04-05")
    def test_gz_command_field_set_to_complexity_advise(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(
            fm.get("gz_command"),
            "complexity advise",
            "gz_command must declare the registered CLI verb",
        )

    @covers("REQ-0.0.29-04-05")
    def test_declared_verb_resolves_in_live_argparse_parser(self) -> None:
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        with self.assertRaises(SystemExit) as captured:
            parser.parse_args(["complexity", "advise", "--help"])
        self.assertEqual(
            captured.exception.code,
            0,
            "gz_command 'complexity advise' must resolve to a registered subparser",
        )


class TestVendorMirrorEquality(unittest.TestCase):
    """REQ-0.0.29-04-06 — vendor mirrors are byte-equal after sync."""

    @covers("REQ-0.0.29-04-06")
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
