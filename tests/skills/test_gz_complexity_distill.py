"""Skill-shape tests for `.gzkit/skills/gz-complexity-distill/SKILL.md`.

Pins REQ-0.0.27-06-01 through REQ-0.0.27-06-06 from
`docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/OBPI-0.0.27-06-distill-skill.md`.

REQ-11 (NEVER include operator's personal email) is a binding doctrine
constraint asserted by the test classes below without `@covers` decoration —
the brief's Acceptance Criteria section currently enumerates REQ-01..06 only,
and parity-gate counts derive from Acceptance Criteria.

All tests read canonical artifacts read-only — no test mutates
`.gzkit/skills/`, `.claude/skills/`, `.agents/skills/`, or `.github/skills/`
in the live repo (REQ-10 inheritance from parent test discipline).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import cast

import yaml

from gzkit.traceability import covers

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = PROJECT_ROOT / ".gzkit" / "skills" / "gz-complexity-distill"
SKILL_PATH = SKILL_DIR / "SKILL.md"

VENDOR_MIRROR_PATHS = (
    PROJECT_ROOT / ".claude" / "skills" / "gz-complexity-distill" / "SKILL.md",
    PROJECT_ROOT / ".agents" / "skills" / "gz-complexity-distill" / "SKILL.md",
    PROJECT_ROOT / ".github" / "skills" / "gz-complexity-distill" / "SKILL.md",
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
    """REQ-0.0.27-06-01 — frontmatter validates against canonical skill schema."""

    @covers("REQ-0.0.27-06-01")
    def test_frontmatter_required_identity_fields_present(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(fm.get("name"), "gz-complexity-distill")
        description = fm.get("description")
        self.assertIsInstance(description, str)
        self.assertGreaterEqual(len(str(description or "")), 40)
        self.assertLessEqual(len(str(description or "")), 1024)

    @covers("REQ-0.0.27-06-01")
    def test_frontmatter_lifecycle_fields_present(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(fm.get("lifecycle_state"), "active")
        self.assertEqual(fm.get("owner"), "gzkit-governance")
        self.assertRegex(str(fm.get("last_reviewed", "")), r"^\d{4}-\d{2}-\d{2}$")

    @covers("REQ-0.0.27-06-01")
    def test_skill_version_is_initial_release(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        metadata = fm.get("metadata")
        self.assertIsInstance(metadata, dict)
        meta = cast(dict[str, object], metadata)
        self.assertEqual(str(meta.get("skill-version", "")), "0.1.0")

    @covers("REQ-0.0.27-06-01")
    def test_description_triggers_on_operator_phrases(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        description = str(fm.get("description", "")).lower()
        for phrase in ("distill", "complexity", "corpus"):
            self.assertIn(
                phrase,
                description,
                f"description must mention '{phrase}' to trigger discovery",
            )


class TestCadenceTriggers(unittest.TestCase):
    """REQ-0.0.27-06-02 — body documents the three cadence triggers verbatim."""

    @covers("REQ-0.0.27-06-02")
    def test_annual_calendar_trigger_present(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)annual",
            "Cadence section must name the annual calendar trigger",
        )

    @covers("REQ-0.0.27-06-02")
    def test_drift_signal_trigger_with_baseline_named(self) -> None:
        text = _read_skill_text()
        self.assertIn(
            "25%",
            text,
            "Cadence section must name the 25% drift threshold from parent ADR",
        )
        self.assertRegex(
            text,
            r"(?i)baseline",
            "Drift trigger must reference baseline of last distillation",
        )

    @covers("REQ-0.0.27-06-02")
    def test_six_month_minimum_re_distillation_guard(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)6[- ]month|six[- ]month",
            "Drift trigger must name the 6-month minimum re-distillation guard",
        )

    @covers("REQ-0.0.27-06-02")
    def test_judgment_trigger_for_groundbreaking_project(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)judgment|ground[- ]?breaking|operator may also trigger",
            "Cadence section must name the operator-judgment trigger",
        )


class TestCorpusReference(unittest.TestCase):
    """REQ-0.0.27-06-03 — corpus + path filters cited by reference, not duplicated."""

    @covers("REQ-0.0.27-06-03")
    def test_corpus_cited_by_canonical_path(self) -> None:
        text = _read_skill_text()
        self.assertIn(
            "data/exemplar_corpus.json",
            text,
            "Skill body must cite the canonical corpus file path",
        )

    @covers("REQ-0.0.27-06-03")
    def test_skill_body_does_not_duplicate_corpus_entries(self) -> None:
        text = _read_skill_text()
        # The corpus uses pinned_sha + project URL fields; embedding either
        # signals duplication of corpus content the skill is required to
        # reference.
        self.assertNotRegex(
            text,
            r"(?im)^\s*pinned_sha\s*[:=]",
            "Skill body must NOT inline corpus entries (pinned_sha keys)",
        )
        # Corpus URLs live in data/exemplar_corpus.json; tolerate the
        # gzkit project URL in references but not a list of corpus URLs.
        github_url_count = len(re.findall(r"github\.com/[^/\s]+/[^/\s)]+", text))
        self.assertLessEqual(
            github_url_count,
            2,
            "Skill body should not list corpus project URLs verbatim",
        )

    @covers("REQ-0.0.27-06-03")
    def test_path_filters_referenced_not_duplicated(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)per[- ]project path filter",
            "Skill body must reference per-project path filters (not duplicate)",
        )


class TestOutputContractWaiver(unittest.TestCase):
    """REQ-0.0.27-06-04 — Output Contract section declares the deferred verb's form.

    Waiver path (gz_command_status: deferred): the Output Contract section
    declares the form the verb is required to produce on GHI #400 closeout.
    """

    @covers("REQ-0.0.27-06-04")
    def test_output_contract_section_present_and_substantive(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertGreater(
            len(body.strip()),
            40,
            "Output Contract section must declare the destination verb's output form",
        )

    @covers("REQ-0.0.27-06-04")
    def test_output_contract_names_destination_artifact_directory(self) -> None:
        body = _section_body(_read_skill_text(), "Output Contract")
        self.assertIn(
            "docs/governance/complexity/",
            body,
            "Output Contract must name the dated distilled-characteristics output dir",
        )

    @covers("REQ-0.0.27-06-04")
    def test_methodology_documents_oee_binding(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)agent[- ]drafted|agent[- ]driven",
            "Skill body must document the agent-driven methodology",
        )
        self.assertRegex(
            text,
            r"(?i)operator[- ]attested|operator[- ]reviewed|practitioner[- ]eye",
            "Skill body must document operator-attested OEE binding",
        )

    @covers("REQ-0.0.27-06-04")
    def test_obpi_04_brief_shape_referenced(self) -> None:
        text = _read_skill_text()
        self.assertIn(
            "OBPI-0.0.27-04",
            text,
            "Skill body must reference the OBPI-04 brief shape it produces",
        )


class TestDeferredCommandWaiver(unittest.TestCase):
    """REQ-0.0.27-06-05 — gz_command resolves OR waiver shape is declared.

    OBPI-06 ships under the waiver path tracked by GHI #400 (REQUIREMENT 9).
    On GHI #400 closeout, the frontmatter migrates to a live `gz_command:`
    and these tests are amended to assert verb resolution instead.
    """

    @covers("REQ-0.0.27-06-05")
    def test_gz_command_status_declared_deferred(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        self.assertEqual(
            fm.get("gz_command_status"),
            "deferred",
            "Waiver path: gz_command_status must be 'deferred' until GHI #400 lands",
        )

    @covers("REQ-0.0.27-06-05")
    def test_deferred_gh_issue_references_open_tracking_issue(self) -> None:
        fm = _parse_frontmatter(_read_skill_text())
        deferred = fm.get("deferred_gh_issue")
        self.assertEqual(
            deferred,
            400,
            "Waiver path: deferred_gh_issue must reference GHI #400",
        )

    @covers("REQ-0.0.27-06-05")
    def test_skill_body_discloses_waiver_to_operator(self) -> None:
        text = _read_skill_text()
        self.assertRegex(
            text,
            r"(?i)deferred|waiver|GHI\s*#?\s*400",
            "Skill body must disclose the deferred-verb waiver to the operator",
        )


class TestVendorMirrorEquality(unittest.TestCase):
    """REQ-0.0.27-06-06 — vendor mirrors are byte-equal to canonical after sync."""

    @covers("REQ-0.0.27-06-06")
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
    """REQ-11 doctrine assertion (not in Acceptance Criteria, no @covers)."""

    def test_skill_contains_no_personal_email_addresses(self) -> None:
        text = _read_skill_text()
        # Allow @users.noreply.github.com (canonical noreply); reject anything else.
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
