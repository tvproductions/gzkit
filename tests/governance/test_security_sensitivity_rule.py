"""REQ-derived tests for the canonical security-sensitivity rule file.

These tests pin the operator-facing contract for
``.gzkit/rules/security-sensitivity.md``: the rule file MUST exist, MUST have
valid frontmatter per ``RuleFrontmatter``, MUST carry the body-level rule
version marker per ``.gzkit/rules/skill-surface-sync.md``, and MUST document
every section the brief enumerates so the doctrine is addressable from a
single canonical home. Sister tests pin the cross-surface bindings the
brief requires: the AGENTS.md matrix citation, the advisory-scorecard entry
classified Mechanical, and the vendor-mirror propagation.

Coverage:
    REQ-0.0.22-06-01 — frontmatter validity, body version marker, block quote.
    REQ-0.0.22-06-02 — required labelled sections (invariant, registry,
    validate scope, walkthrough, scanner-unavailable).
    REQ-0.0.22-06-03 — AGENTS.md matrix cites the rule file and lists every
    (kind × lane × sensitivity) cell.
    REQ-0.0.22-06-04 — advisory-rules-audit.md carries a scorecard entry
    classified Mechanical with a citation to ``gz validate --sensitivity``.
    REQ-0.0.22-06-05 — vendor mirrors exist with matching body-level
    rule-version markers.
    REQ-0.0.22-06-06 — ``gz validate --advisory-scorecard`` and
    ``gz validate --documents`` produce no errors after the rule lands.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from gzkit.rules import RuleFrontmatter, _parse_canonical_frontmatter
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_RULE_PATH = _PROJECT_ROOT / ".gzkit" / "rules" / "security-sensitivity.md"


class SecuritySensitivityRuleAuthorship(unittest.TestCase):
    """Pin the rule file's authorship contract."""

    @covers("REQ-0.0.22-06-01")
    def test_rule_file_exists_with_valid_frontmatter(self) -> None:
        self.assertTrue(
            _RULE_PATH.is_file(),
            f"canonical rule file missing: {_RULE_PATH.relative_to(_PROJECT_ROOT)}",
        )
        frontmatter_dict, _ = _parse_canonical_frontmatter(_RULE_PATH)
        frontmatter = RuleFrontmatter(**frontmatter_dict)
        self.assertEqual(frontmatter.id, "security-sensitivity")
        self.assertGreater(
            len(frontmatter.paths),
            0,
            "frontmatter paths must list at least one glob pattern",
        )
        self.assertTrue(
            frontmatter.description.strip(),
            "frontmatter description must be a non-empty one-liner",
        )

    @covers("REQ-0.0.22-06-01")
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

    @covers("REQ-0.0.22-06-02")
    def test_rule_body_documents_required_sections(self) -> None:
        _, body = _parse_canonical_frontmatter(_RULE_PATH)
        required_section_patterns = {
            "invariant": r"^##+\s+Invariant\b",
            "registry contract": r"^##+\s+Registry contract\b",
            "validate scope": r"^##+\s+`gz validate --sensitivity`",
            "walkthrough enumeration": r"^##+\s+Heightened walkthrough\b",
        }
        for label, pattern in required_section_patterns.items():
            with self.subTest(section=label):
                self.assertRegex(
                    body,
                    re.compile(pattern, re.MULTILINE),
                    f"section heading missing: {label} ({pattern!r})",
                )
        # Scanner-unavailable was folded into the Heightened walkthrough
        # section during the diet pass (GHI #327). The binding invariant is
        # that scanner-unavailable behavior is documented as fail-closed,
        # not that it has its own heading.
        with self.subTest(section="scanner-unavailable failure mode"):
            self.assertRegex(
                body,
                re.compile(r"Scanner-unavailable.*fail-closed", re.IGNORECASE | re.DOTALL),
                "scanner-unavailable fail-closed behavior must be documented in the rule body",
            )


class SecuritySensitivityCrossSurfaceBindings(unittest.TestCase):
    """Pin the rule's binding into AGENTS.md, the scorecard, and mirrors."""

    @covers("REQ-0.0.22-06-03")
    def test_agents_md_matrix_cites_rule_and_lists_every_cell(self) -> None:
        # ADR-0.0.36 collapsed the Lane & Kind & Sensitivity Attestation Matrix
        # to a universal attestation rule. The new canonical surface is the
        # "Universal OBPI Attestation" section, which names all three axes for
        # gate-firing scope. The security-sensitivity rule file is still cited
        # via the Third-axis doctrine link.
        #
        # REQ-0.0.22-06-03 semantic: the canonical AGENTS.md surface names the
        # security-sensitivity axis and cites the rule file. This is satisfied
        # by the new universal attestation section.
        agents_md = (_PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn(
            "Universal OBPI Attestation",
            agents_md,
            "AGENTS.md must carry the universal attestation section (ADR-0.0.36)",
        )
        self.assertIn(
            ".gzkit/rules/security-sensitivity.md",
            agents_md,
            "AGENTS.md must cite the security-sensitivity rule file (Third-axis doctrine link)",
        )
        # All three axes must be named for gate-firing scope in the new section.
        for axis in ("`foundation`", "`heavy`", "`security`"):
            with self.subTest(axis=axis):
                self.assertIn(
                    axis,
                    agents_md,
                    f"universal attestation section must name gate-firing axis {axis}",
                )

    @covers("REQ-0.0.22-06-04")
    def test_advisory_scorecard_classifies_rule_mechanical(self) -> None:
        scorecard = (_PROJECT_ROOT / "docs" / "governance" / "advisory-rules-audit.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "security-sensitivity",
            scorecard,
            "scorecard must mention the security-sensitivity rule",
        )
        # The scorecard entry is a markdown table row in a section keyed by
        # `### Security Sensitivity`. Pin both the section header and the
        # `**Mechanical**` token within the same body span so the entry is
        # classified, not merely mentioned.
        self.assertRegex(
            scorecard,
            re.compile(
                r"###\s+Security Sensitivity.*?\*\*Mechanical\*\*",
                re.DOTALL,
            ),
            "scorecard section for security-sensitivity must be classified Mechanical",
        )
        self.assertIn(
            "gz validate --sensitivity",
            scorecard,
            "scorecard entry must cite gz validate --sensitivity",
        )

    @covers("REQ-0.0.22-06-05")
    def test_vendor_mirrors_carry_rule_version_marker(self) -> None:
        mirrors = (
            _PROJECT_ROOT / ".claude" / "rules" / "security-sensitivity.md",
            _PROJECT_ROOT / ".github" / "instructions" / "security_sensitivity.instructions.md",
        )
        for mirror in mirrors:
            with self.subTest(mirror=mirror.relative_to(_PROJECT_ROOT)):
                self.assertTrue(
                    mirror.is_file(),
                    f"vendor mirror missing: {mirror.relative_to(_PROJECT_ROOT)}",
                )
                self.assertIn(
                    "<!-- rule-version: 0.4.0 -->",
                    mirror.read_text(encoding="utf-8"),
                    "vendor mirror must carry the body-level rule-version marker",
                )

    @covers("REQ-0.0.22-06-06")
    def test_advisory_scorecard_audit_passes_for_new_rule(self) -> None:
        from gzkit.governance.trust_audits import audit_advisory_scorecard

        errors = audit_advisory_scorecard(_PROJECT_ROOT)
        rule_offenders = [err for err in errors if "security-sensitivity" in err.artifact]
        self.assertEqual(
            rule_offenders,
            [],
            "audit_advisory_scorecard must not flag the new rule (it must have a scorecard entry).",
        )


if __name__ == "__main__":
    unittest.main()
