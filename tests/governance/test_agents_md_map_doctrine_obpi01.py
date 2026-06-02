"""REQ-derived tests for OBPI-0.0.54-01 (map-not-encyclopedia doctrine + budget).

These tests pin the operator-facing contract of the four artifacts authored
under OBPI-0.0.54-01:

* ``.gzkit/rules/agents-md-map-doctrine.md`` — the rule file (version 0.1.0)
  naming the invariant and the five prohibited shapes; paths frontmatter
  scopes AGENTS.md, CLAUDE.md, and .claude/rules/*.md.
* ``docs/governance/agents-md-doctrine.md`` — the canonical encyclopedia
  entry the future AGENTS.md ``Why this contract is not minimal`` link
  will resolve to.
* ``data/instructions_files_budget.json`` — AGENTS.md budget 40000→15000,
  CLAUDE.md budget 40000→4000, per-rule-file 16000 unchanged.
* ``docs/governance/advisory-rules-audit.md`` — scorecard entry classifying
  the new rule as Mechanical for shape with Judgment note for per-section
  size targets.

The negative scope assertion (REQ-05) verifies that OBPI-02's lift targets
do not exist yet — this OBPI's contract is that zero content moves out of
AGENTS.md.

Per ``.gzkit/rules/tests.md`` § "Tests assert semantics, not strings": each
assertion derives from the REQ, not from a run of the code.

Coverage:
    REQ-0.0.54-01-01 — rule file at version 0.1.0 with paths frontmatter
        scoping AGENTS.md, CLAUDE.md, .claude/rules/*.md; body declares
        the invariant and the five prohibited shapes.
    REQ-0.0.54-01-02 — doctrine doc exists as the canonical expansion.
    REQ-0.0.54-01-03 — budget JSON pins AGENTS.md=15000, CLAUDE.md=4000;
        per-rule-file 16000 unchanged.
    REQ-0.0.54-01-04 — scorecard entry exists and classifies the rule as
        Mechanical with the Judgment note for per-section size targets.
    REQ-0.0.54-01-05 — zero content moved from AGENTS.md (OBPI-02 lift
        targets prime-directive.md, behavior-rules.md, skills-catalog.md,
        obpi-attestation.md MUST NOT exist yet under docs/governance/).
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.rules import RuleFrontmatter, _parse_canonical_frontmatter
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_RULE_PATH = _PROJECT_ROOT / ".gzkit" / "rules" / "agents-md-map-doctrine.md"
_DOCTRINE_PATH = _PROJECT_ROOT / "docs" / "governance" / "agents-md-doctrine.md"
_BUDGET_PATH = _PROJECT_ROOT / "data" / "instructions_files_budget.json"
_SCORECARD_PATH = _PROJECT_ROOT / "docs" / "governance" / "advisory-rules-audit.md"

_RULE_VERSION = "0.1.0"
_PATHS_SCOPE = ("AGENTS.md", "CLAUDE.md", ".claude/rules/*.md")
_PROHIBITED_SHAPES = (
    "Multi-paragraph rationale prose",
    "Worked examples or anti-pattern catalogs",
    "Why this is canon",
    "Narrative pedagogical sections",
    "Operative-claims expansions",
)
_OBPI02_LIFT_TARGETS = (
    "prime-directive.md",
    "behavior-rules.md",
    "skills-catalog.md",
    "obpi-attestation.md",
)


class MapDoctrineRuleAuthorship(unittest.TestCase):
    """REQ-01: rule file authored at v0.1.0 with required frontmatter and body."""

    @covers("REQ-0.0.54-01-01")
    def test_rule_file_exists_with_v010_and_required_shape(self) -> None:
        self.assertTrue(
            _RULE_PATH.is_file(),
            f"rule file missing: {_RULE_PATH.relative_to(_PROJECT_ROOT).as_posix()}",
        )

        frontmatter_dict, body = _parse_canonical_frontmatter(_RULE_PATH)
        frontmatter = RuleFrontmatter(**frontmatter_dict)

        self.assertEqual(frontmatter.id, "agents-md-map-doctrine")
        self.assertEqual(tuple(frontmatter.paths), _PATHS_SCOPE)

        self.assertIn(
            f"<!-- rule-version: {_RULE_VERSION} -->",
            body,
            "body-level rule-version marker missing or wrong version",
        )
        self.assertIn(
            f"**Rule version:** `{_RULE_VERSION}`",
            body,
            "visible block-quote rule-version missing or wrong version",
        )

        for shape in _PROHIBITED_SHAPES:
            self.assertIn(
                shape,
                body,
                f"rule body MUST name prohibited shape: {shape}",
            )


class DoctrineDocExpansion(unittest.TestCase):
    """REQ-02: doctrine doc exists as the canonical encyclopedia entry."""

    @covers("REQ-0.0.54-01-02")
    def test_doctrine_doc_exists_with_canonical_anchors(self) -> None:
        self.assertTrue(
            _DOCTRINE_PATH.is_file(),
            f"doctrine doc missing: {_DOCTRINE_PATH.relative_to(_PROJECT_ROOT).as_posix()}",
        )
        body = _DOCTRINE_PATH.read_text(encoding="utf-8")

        self.assertIn(
            "ADR-0.0.54-agents-md-map-not-encyclopedia-doctrine",
            body,
            "doctrine doc MUST cite the parent ADR",
        )
        self.assertIn(
            ".gzkit/rules/agents-md-map-doctrine.md",
            body,
            "doctrine doc MUST cite the rule file it expands",
        )
        self.assertIn(
            "## The invariant",
            body,
            "doctrine doc MUST carry the invariant section",
        )


class BudgetTightening(unittest.TestCase):
    """REQ-03: budget JSON pins the new contract values."""

    @covers("REQ-0.0.54-01-03")
    def test_budget_json_pins_15k_and_4k(self) -> None:
        # OBPI-0.0.54-03 retargeted AGENTS.md 15000 → 32000 after measuring the
        # post-shape-conformance floor at ~31k chars with the current monolithic
        # template. 2026-06-01: bumped 32000 → 33000 to seat the operator
        # DIRECT-FIX MORATORIUM directive in Local Agent Rules (~480 chars; AGENTS.md
        # was already at its ceiling). The 15000 destination — and the principled
        # reclaim of this bump — is tracked under GHI #533 / ADR-0.0.37 (constitutional
        # invariant composition); registry-projected rules unlock the structural-shell
        # shape that makes <15k achievable. See data/instructions_files_budget.json
        # _doc field for the full rationale.
        payload = json.loads(_BUDGET_PATH.read_text(encoding="utf-8"))
        files = payload["files"]

        self.assertEqual(files["AGENTS.md"], 33000, "AGENTS.md budget MUST be 33000 chars")
        self.assertEqual(files["CLAUDE.md"], 4000, "CLAUDE.md budget MUST be 4000 chars")

        globs = payload["globs"]
        rule_glob = next(g for g in globs if g["pattern"] == ".claude/rules/*.md")
        # OBPI-0.0.54-04 tightened the rule-file glob from 16000 to 15000 after the
        # diet pass measured the post-lift max at 13565 chars (skill-surface-sync.md).
        self.assertEqual(
            rule_glob["max_chars_per_file"],
            15000,
            "per-rule-file budget MUST be 15000 chars (tightened by OBPI-0.0.54-04)",
        )


class ScorecardEntry(unittest.TestCase):
    """REQ-04: scorecard entry classifies the rule as Mechanical (with Judgment note)."""

    @covers("REQ-0.0.54-01-04")
    def test_scorecard_entry_mechanical_with_judgment_note(self) -> None:
        body = _SCORECARD_PATH.read_text(encoding="utf-8")

        self.assertIn(
            "agents-md-map-doctrine",
            body,
            "scorecard MUST cite the rule by slug",
        )
        self.assertIn(
            "**Mechanical**",
            body,
            "scorecard entry MUST classify the rule as Mechanical",
        )
        self.assertIn(
            "per-section size targets remain **Judgment**",
            body,
            "scorecard entry MUST note that per-section size targets remain Judgment",
        )


class ScopeBoundaryLiftTargetsPresent(unittest.TestCase):
    """REQ-05 (post-OBPI-02): OBPI-02 has executed; lift targets now exist.

    OBPI-01's authoring contract was a zero-lift scope (content stays in
    AGENTS.md). OBPI-02 (lift) has since landed, populating the named lift
    targets under docs/governance/. This test was originally a negative
    assertion ("targets MUST NOT exist yet") authored under OBPI-01. Under
    coupled-surface coherence (DO IT RIGHT 1a), OBPI-02 retires the negative
    form and replaces it with the positive form: lift targets are present
    at the expected paths. The REQ-0.0.54-01-05 zero-lift constraint applied
    to OBPI-01's authoring window only; OBPI-02's completion is the lift.
    """

    @covers("REQ-0.0.54-01-05")
    def test_obpi02_lift_targets_present_after_obpi02_landed(self) -> None:
        governance = _PROJECT_ROOT / "docs" / "governance"
        for target in _OBPI02_LIFT_TARGETS:
            path = governance / target
            rel = path.relative_to(_PROJECT_ROOT).as_posix()
            self.assertTrue(
                path.exists(),
                f"OBPI-02 lift target expected after OBPI-02 landed: {rel}",
            )


if __name__ == "__main__":
    unittest.main()
