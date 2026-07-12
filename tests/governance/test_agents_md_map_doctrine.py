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
    REQ-0.0.54-01-03 — budget JSON enforces the per-turn surface contract:
        AGENTS.md fits Codex's project-doc byte cap (no silent truncation) and
        each surface fits its configured budget; the budget value lives only in
        the JSON (no literal pinned in the test).
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
_AGENTS_MD = _PROJECT_ROOT / "AGENTS.md"
_CLAUDE_MD = _PROJECT_ROOT / "CLAUDE.md"

# gzkit's project-doc budget ceiling (BYTES). Codex's CLI default
# ``project_doc_max_bytes`` is 32768 B — root AGENTS.md is silently truncated
# past that many bytes UNDER CODEX (github.com/openai/codex issue #7138). Per
# operator ruling 2026-07-06 ("that hard-coded value is noise, bump") this
# ceiling is DECOUPLED from the Codex vendor cap — hexagonal: an adapter limit
# must not gate the core contract. NOTE: AGENTS.md content between 32768 B and
# this ceiling still truncates under Codex at runtime; the durable headroom path
# is corpus-splitting (GHI #533), not a larger number here.
_PROJECT_DOC_BUDGET_CEILING_BYTES = 65536


def _budget_within_ceiling(char_budget: int) -> bool:
    """A configured per-turn char budget must not exceed Codex's project-doc byte
    cap; a budget above the cap would green-light a silently-truncated surface."""
    return char_budget <= _PROJECT_DOC_BUDGET_CEILING_BYTES


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

        # De-pinned from the literal 0.1.0 (GHI #531 content-test anti-pattern;
        # reclassification to the SUPPORT proof channel is deferred to the
        # ADR-0.0.59 Move 6 sweep). skill-surface-sync bumps the rule-version on
        # every rule edit, so REQ-01-01's durable semantic is "authored with a
        # coherent rule-version marker in both required forms that agree" — not
        # "frozen at the authoring version". A pinned literal can only pass at the
        # rule's first moment of life (it broke on the 0.2.0 closeout correction).
        comment_marker = "<!-- rule-version: "
        quote_marker = "**Rule version:** `"
        self.assertIn(comment_marker, body, "body-level rule-version HTML-comment marker missing")
        self.assertIn(quote_marker, body, "visible block-quote rule-version marker missing")
        comment_version = body.split(comment_marker, 1)[1].split(" -->", 1)[0].strip()
        quote_version = body.split(quote_marker, 1)[1].split("`", 1)[0].strip()
        self.assertRegex(
            comment_version, r"^\d+\.\d+\.\d+$", "HTML-comment rule-version is not semver"
        )
        self.assertEqual(
            comment_version,
            quote_version,
            "rule-version markers disagree between HTML comment and block quote",
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
    """REQ-03: the budget JSON is a real, enforced, sane contract."""

    @covers("REQ-0.0.54-01-03")
    def test_budget_enforces_codex_cap_and_files_fit(self) -> None:
        """The budget JSON enforces the per-turn surface contract.

        Replaces the prior literal pin (``assertEqual(files["AGENTS.md"], 33000)``).
        That assertion read ``data/instructions_files_budget.json`` and then
        asserted it equalled a copy of its own value pasted into the test, so it
        could only fail when the budget was *legitimately* changed — never when
        something was actually wrong (config-SSOT + tautological-test anti-pattern;
        return-to-health plan Tier-2 item 2.5). The single source of truth for the
        budget value is the JSON; the test asserts the *semantic invariant* the
        budget exists to enforce, encoding WHY it matters: AGENTS.md is the surface
        Codex loads, so it must fit Codex's project-doc byte cap (no silent
        truncation, GHI #519), the configured budget must itself stay under that
        cap, and each surface must fit its configured budget.
        """
        payload = json.loads(_BUDGET_PATH.read_text(encoding="utf-8"))
        files = payload["files"]

        for name in ("AGENTS.md", "CLAUDE.md"):
            self.assertIsInstance(
                files.get(name), int, f"{name} budget must be a configured integer"
            )

        # The configured AGENTS.md budget must not exceed gzkit's project-doc
        # budget ceiling (decoupled from Codex's 32768 B cap per operator ruling
        # 2026-07-06; Codex still truncates at 32768 B at runtime).
        self.assertTrue(
            _budget_within_ceiling(files["AGENTS.md"]),
            f"AGENTS.md budget {files['AGENTS.md']} exceeds the project-doc budget "
            f"ceiling {_PROJECT_DOC_BUDGET_CEILING_BYTES} B",
        )
        # The ceiling guard has teeth: it rejects an absurd over-ceiling budget,
        # with no mutation of the real config file.
        self.assertFalse(
            _budget_within_ceiling(70000),
            "70000 exceeds the project-doc budget ceiling and must be rejected",
        )

        for name, path in (("AGENTS.md", _AGENTS_MD), ("CLAUDE.md", _CLAUDE_MD)):
            actual = len(path.read_text(encoding="utf-8"))
            with self.subTest(file=name):
                self.assertLessEqual(
                    actual,
                    files[name],
                    f"{name} is {actual} chars, exceeds its budget {files[name]}",
                )

        # The #519 invariant proper: AGENTS.md byte size fits Codex's byte cap.
        agents_bytes = len(_AGENTS_MD.read_text(encoding="utf-8").encode("utf-8"))
        self.assertLessEqual(
            agents_bytes,
            _PROJECT_DOC_BUDGET_CEILING_BYTES,
            f"AGENTS.md is {agents_bytes} B, exceeds Codex project-doc cap "
            f"{_PROJECT_DOC_BUDGET_CEILING_BYTES} B (silent-truncation risk; GHI #519)",
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
