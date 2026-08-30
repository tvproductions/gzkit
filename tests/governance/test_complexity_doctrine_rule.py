"""REQ-derived tests for the canonical complexity-doctrine rule file.

These tests pin the operator-facing contract for
``.gzkit/rules/complexity-doctrine.md``: the rule file MUST exist, MUST have
valid frontmatter per ``RuleFrontmatter``, MUST carry the body-level rule
version marker, MUST document all seven selection criteria, seven corpus
anti-patterns, three cadence triggers, the citation contract, and the
project-doctrine-fitness criterion. Sister tests pin the advisory-scorecard
entry and vendor-mirror propagation.

Coverage:
    REQ-0.0.27-01-01 — frontmatter validity, body version marker, block quote.
    REQ-0.0.27-01-02 — all seven selection criteria present in rule body.
    REQ-0.0.27-01-03 — all seven corpus anti-patterns present in rule body.
    REQ-0.0.27-01-04 — three cadence triggers + 6-month minimum guard present.
    REQ-0.0.27-01-05 — citation contract names distilled-characteristics and
    excludes raw distributions / corpus from direct citation.
    REQ-0.0.27-01-06 — project-doctrine-fitness criterion present; pytest-mention
    demerit lesson cited as the canonical failure it closes.
    REQ-0.0.27-01-07 — advisory-rules-audit.md carries a scorecard entry
    classified Mechanical; ``gz validate --advisory-scorecard`` exits 0.
    REQ-0.0.27-01-08 — vendor mirrors exist with matching body-level
    rule-version markers (``gz agent sync control-surfaces`` propagation).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.rules import RuleFrontmatter, _parse_canonical_frontmatter
from gzkit.traceability import covers
from tests.vendor_surfaces import rule_mirror_paths

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_RULE_PATH = _PROJECT_ROOT / ".gzkit" / "rules" / "complexity-doctrine.md"


class ComplexityDoctrineRuleAuthorship(unittest.TestCase):
    """Pin the rule file's authorship contract."""

    @covers("REQ-0.0.27-01-01")
    def test_rule_file_exists_with_valid_frontmatter(self) -> None:
        self.assertTrue(
            _RULE_PATH.is_file(),
            f"canonical rule file missing: {_RULE_PATH.relative_to(_PROJECT_ROOT).as_posix()}",
        )
        frontmatter_dict, _ = _parse_canonical_frontmatter(_RULE_PATH)
        frontmatter = RuleFrontmatter(**frontmatter_dict)
        self.assertEqual(frontmatter.id, "complexity-doctrine")
        self.assertGreater(
            len(frontmatter.paths),
            0,
            "frontmatter paths must list at least one glob pattern",
        )
        self.assertTrue(
            frontmatter.description.strip(),
            "frontmatter description must be a non-empty one-liner",
        )

    @covers("REQ-0.0.27-01-01")
    def test_rule_body_carries_version_marker_and_block_quote(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        self.assertIn(
            "<!-- rule-version: 0.4.0 -->",
            body,
            "body must carry the canonical body-level rule-version HTML comment",
        )
        self.assertRegex(
            body,
            r">\s+\*\*Rule version:\*\*\s+`0\.4\.0`",
            "body must carry the visible rule-version block quote",
        )

    @covers("REQ-0.0.27-01-02")
    def test_seven_selection_criteria_present(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        criteria_patterns = {
            "longevity (5 years)": r"5\s+years",
            "maintenance health (12 months)": r"12\s+months",
            "practitioner reputation (not GitHub-star count)": r"GitHub-star",
            "pure-Python predominance (80%)": r"80\s*%",
            "author craftsmanship signal": r"craftsmanship",
            "project doctrine fitness": r"doctrine fitness",
            "pinned commit SHA": r"commit\s+SHA",
        }
        for criterion, pattern in criteria_patterns.items():
            with self.subTest(criterion=criterion):
                self.assertRegex(
                    body,
                    re.compile(pattern, re.IGNORECASE),
                    f"selection criterion missing from rule body: {criterion!r}",
                )

    @covers("REQ-0.0.27-01-03")
    def test_seven_corpus_anti_patterns_present(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        anti_pattern_keys = {
            "post-hoc fitting": r"post.hoc",
            "GitHub-star count selection": r"GitHub-star",
            "only modern projects": r"modern\s+projects?|only\s+modern",
            "only legacy projects": r"legacy\s+projects?|only\s+legacy",
            "monoculture / same domain": r"monoculture|same\s+domain",
            "agent training memory without operator audit": r"training\s+memory|operator\s+audit",
            "violates doctrinal commitments": r"doctrinal\s+commitments?",
        }
        for label, pattern in anti_pattern_keys.items():
            with self.subTest(anti_pattern=label):
                self.assertRegex(
                    body,
                    re.compile(pattern, re.IGNORECASE),
                    f"anti-pattern missing from rule body: {label!r}",
                )

    @covers("REQ-0.0.27-01-04")
    def test_three_cadence_triggers_and_six_month_minimum_present(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        cadence_checks = {
            "annual calendar default": r"annual",
            "drift signal trigger >25%": r"25\s*%",
            "judgment / ad-hoc trigger": r"judgment|ad.hoc|ground.breaking",
            "6-month minimum re-distillation guard": r"6.month|six.month",
        }
        for label, pattern in cadence_checks.items():
            with self.subTest(cadence_element=label):
                self.assertRegex(
                    body,
                    re.compile(pattern, re.IGNORECASE),
                    f"cadence element missing from rule body: {label!r}",
                )

    @covers("REQ-0.0.27-01-05")
    def test_citation_contract_names_distilled_characteristics_and_excludes_raw(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        self.assertRegex(
            body,
            re.compile(r"distilled.characteristics", re.IGNORECASE),
            "citation contract must name 'distilled-characteristics' as the cited artifact",
        )
        self.assertRegex(
            body,
            re.compile(r"not.*cited.*directly|raw.*distribut|corpus.*not.*cited", re.IGNORECASE),
            "citation contract must exclude raw distributions / corpus from direct citation",
        )

    @covers("REQ-0.0.27-01-06")
    def test_project_doctrine_fitness_and_pytest_demerit_lesson(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        self.assertRegex(
            body,
            re.compile(r"doctrine\s+fitness", re.IGNORECASE),
            "rule body must state the project-doctrine-fitness criterion",
        )
        self.assertRegex(
            body,
            re.compile(r"pytest", re.IGNORECASE),
            "rule body must cite the pytest-mention demerit lesson as the canonical failure",
        )


class ComplexityDoctrineCrossSurfaceBindings(unittest.TestCase):
    """Pin the rule's binding into the scorecard and vendor mirrors."""

    @covers("REQ-0.0.27-01-07")
    def test_advisory_scorecard_classifies_rule_mechanical(self) -> None:
        scorecard = (_PROJECT_ROOT / "docs" / "governance" / "advisory-rules-audit.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "complexity-doctrine",
            scorecard,
            "scorecard must mention the complexity-doctrine rule",
        )
        self.assertRegex(
            scorecard,
            re.compile(
                r"###\s+Exemplar Corpus Doctrine.*?\*\*Mechanical\*\*",
                re.DOTALL,
            ),
            "scorecard section for complexity-doctrine must be classified Mechanical",
        )

    @covers("REQ-0.0.27-01-07")
    def test_advisory_scorecard_audit_passes_for_new_rule(self) -> None:
        from gzkit.governance.trust_audits import audit_advisory_scorecard

        errors = audit_advisory_scorecard(_PROJECT_ROOT)
        rule_offenders = [err for err in errors if "complexity-doctrine" in err.artifact]
        self.assertEqual(
            rule_offenders,
            [],
            "audit_advisory_scorecard must not flag complexity-doctrine (needs a scorecard entry).",
        )

    @covers("REQ-0.0.27-01-08")
    def test_vendor_mirrors_carry_rule_version_marker(self) -> None:
        mirrors = rule_mirror_paths("complexity_doctrine")
        for mirror in mirrors:
            with self.subTest(mirror=mirror.relative_to(_PROJECT_ROOT).as_posix()):
                self.assertTrue(
                    mirror.is_file(),
                    f"vendor mirror missing: {mirror.relative_to(_PROJECT_ROOT).as_posix()}",
                )
                self.assertIn(
                    "<!-- rule-version: 0.4.0 -->",
                    mirror.read_text(encoding="utf-8"),
                    "vendor mirror must carry the body-level rule-version marker",
                )

    @covers("REQ-0.0.27-01-08")
    def test_vendor_mirror_body_contains_key_canonical_content(self) -> None:
        # No existence guard and no `if ...is_file():` wrapper. The former was a
        # skipTest, the latter silently passed the whole body when the mirror was
        # absent — both green-by-emptiness. `read_text` raises FileNotFoundError,
        # which is the loud failure a missing generated mirror deserves.
        claude_mirror = _PROJECT_ROOT / ".claude" / "rules" / "complexity-doctrine.md"
        mirror_text = claude_mirror.read_text(encoding="utf-8")
        key_phrases = ("doctrine fitness", "distilled-characteristics", "6-month", "commit SHA")
        for key_phrase in key_phrases:
            with self.subTest(key_phrase=key_phrase):
                self.assertIn(
                    key_phrase,
                    mirror_text,
                    f"mirror must contain canonical content phrase: {key_phrase!r}",
                )


if __name__ == "__main__":
    unittest.main()
