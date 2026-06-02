"""REQ-derived tests for OBPI-0.0.54-04 (apply doctrine to CLAUDE.md and rules).

Covers the six acceptance criteria in the OBPI brief:
* REQ-0.0.54-04-01 — CLAUDE.md audit clean (no prohibited shapes)
* REQ-0.0.54-04-02 — .gzkit/rules/*.md prohibited shapes lifted; See-links present
* REQ-0.0.54-04-03 — data/instructions_files_budget.json finalized (glob 15000)
* REQ-0.0.54-04-04 — runbooks updated in same patch set as doctrine application
* REQ-0.0.54-04-05 — trust-doctrine cross-links agents-md-map-conformance scope
* REQ-0.0.54-04-06 — gz validate --agents-md-map-conformance green across named scope
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_MD = _PROJECT_ROOT / "CLAUDE.md"
_RULES_DIR = _PROJECT_ROOT / ".gzkit" / "rules"
_BUDGET_PATH = _PROJECT_ROOT / "data" / "instructions_files_budget.json"
_USER_RUNBOOK = _PROJECT_ROOT / "docs" / "user" / "runbook.md"
_GOV_RUNBOOK = _PROJECT_ROOT / "docs" / "governance" / "governance_runbook.md"
_TRUST_DOCTRINE = _PROJECT_ROOT / "docs" / "governance" / "trust-doctrine.md"

_PROHIBITED_TITLES = frozenset(
    {"anti-patterns", "rationale", "worked example", "why this is canon"}
)
_PROHIBITED_TITLE_PATTERN = re.compile(r"^why\s+.+\s+is\s+canon$", re.IGNORECASE)
_HEADING_RE = re.compile(r"^#{2,}\s+(.+?)\s*$", re.MULTILINE)


def _has_prohibited_title(text: str) -> list[str]:
    hits = []
    for m in _HEADING_RE.finditer(text):
        title = m.group(1).strip().lower()
        if title in _PROHIBITED_TITLES or _PROHIBITED_TITLE_PATTERN.match(title):
            hits.append(m.group(0).strip())
    return hits


class ClaudeMdCleanAudit(unittest.TestCase):
    """REQ-0.0.54-04-01: CLAUDE.md has no prohibited shapes."""

    @covers("REQ-0.0.54-04-01")
    def test_claude_md_has_no_prohibited_headings(self) -> None:
        text = _CLAUDE_MD.read_text(encoding="utf-8")
        hits = _has_prohibited_title(text)
        self.assertEqual(
            hits,
            [],
            f"CLAUDE.md contains prohibited heading(s): {hits}. "
            "Map-not-encyclopedia doctrine violated.",
        )

    @covers("REQ-0.0.54-04-01")
    def test_claude_md_within_budget(self) -> None:
        budget = json.loads(_BUDGET_PATH.read_text(encoding="utf-8"))
        char_limit = budget["files"].get("CLAUDE.md", 40000)
        actual = len(_CLAUDE_MD.read_text(encoding="utf-8"))
        self.assertLessEqual(
            actual,
            char_limit,
            f"CLAUDE.md is {actual} chars, exceeds budget {char_limit}",
        )


class RuleFilesProhibitedShapesLifted(unittest.TestCase):
    """REQ-0.0.54-04-02: .gzkit/rules/*.md shape-conformant; lifted sections have See-links."""

    def _canonical_rule_files(self) -> list[Path]:
        return [f for f in _RULES_DIR.glob("*.md") if f.name != "AGENTS.md"]

    @covers("REQ-0.0.54-04-02")
    def test_no_rule_file_has_prohibited_heading(self) -> None:
        for rule_file in self._canonical_rule_files():
            with self.subTest(rule=rule_file.name):
                text = rule_file.read_text(encoding="utf-8")
                hits = _has_prohibited_title(text)
                self.assertEqual(
                    hits,
                    [],
                    f"{rule_file.name}: prohibited heading(s) {hits}. Lift to docs/governance/.",
                )

    @covers("REQ-0.0.54-04-02")
    def test_model_selection_rationale_expansion_doc_exists(self) -> None:
        expansion = _PROJECT_ROOT / "docs" / "governance" / "model-selection-rationale.md"
        self.assertTrue(
            expansion.is_file(),
            "docs/governance/model-selection-rationale.md must exist "
            "(lifted from model-selection.md Rationale)",
        )

    @covers("REQ-0.0.54-04-02")
    def test_skill_surface_sync_rationale_expansion_doc_exists(self) -> None:
        expansion = _PROJECT_ROOT / "docs" / "governance" / "skill-surface-sync-rationale.md"
        self.assertTrue(
            expansion.is_file(),
            "docs/governance/skill-surface-sync-rationale.md must exist "
            "(lifted from skill-surface-sync.md Rationale)",
        )

    @covers("REQ-0.0.54-04-02")
    def test_model_selection_has_see_link_to_expansion(self) -> None:
        rule_file = _RULES_DIR / "model-selection.md"
        text = rule_file.read_text(encoding="utf-8")
        self.assertIn(
            "model-selection-rationale.md",
            text,
            "model-selection.md must contain See link to expansion doc after Rationale lift",
        )

    @covers("REQ-0.0.54-04-02")
    def test_skill_surface_sync_has_see_link_to_expansion(self) -> None:
        rule_file = _RULES_DIR / "skill-surface-sync.md"
        text = rule_file.read_text(encoding="utf-8")
        self.assertIn(
            "skill-surface-sync-rationale.md",
            text,
            "skill-surface-sync.md must contain See link to expansion doc after Rationale lift",
        )


class BudgetJsonFinalized(unittest.TestCase):
    """REQ-0.0.54-04-03: budget JSON tightened for rule-file glob after diet pass."""

    @covers("REQ-0.0.54-04-03")
    def test_rule_file_glob_tightened_to_15000(self) -> None:
        payload = json.loads(_BUDGET_PATH.read_text(encoding="utf-8"))
        rule_glob = next(g for g in payload["globs"] if g["pattern"] == ".claude/rules/*.md")
        self.assertEqual(
            rule_glob["max_chars_per_file"],
            15000,
            "per-rule-file glob MUST be 15000 chars (tightened by OBPI-0.0.54-04 diet pass)",
        )

    @covers("REQ-0.0.54-04-03")
    def test_agents_md_and_claude_md_budgets_unchanged(self) -> None:
        # REQ-04-03 fenced that OBPI-0.0.54-04's diet pass left the AGENTS.md /
        # CLAUDE.md budgets untouched (only the rule-glob tightened). That held for
        # OBPI-04. 2026-06-01: a later operator DIRECT-FIX MORATORIUM directive bumped
        # AGENTS.md 32000 → 33000 to seat the new Local Agent Rule; this fence now
        # pins the current contract value. CLAUDE.md stays at 4000.
        payload = json.loads(_BUDGET_PATH.read_text(encoding="utf-8"))
        files = payload["files"]
        self.assertEqual(
            files["AGENTS.md"], 33000, "AGENTS.md budget is 33000 (operator bump 2026-06-01)"
        )
        self.assertEqual(files["CLAUDE.md"], 4000, "CLAUDE.md budget must stay at 4000")


class RunbooksUpdated(unittest.TestCase):
    """REQ-0.0.54-04-04: runbooks updated with recovery path and Instruction Files section."""

    @covers("REQ-0.0.54-04-04")
    def test_user_runbook_has_gz_context_diet_recovery_path(self) -> None:
        text = _USER_RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(
            "gz-context-diet",
            text,
            "docs/user/runbook.md must document the gz-context-diet recovery path "
            "(AGENTS.md shape drift)",
        )

    @covers("REQ-0.0.54-04-04")
    def test_user_runbook_references_agents_md_map_conformance_validator(self) -> None:
        text = _USER_RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(
            "agents-md-map-conformance",
            text,
            "docs/user/runbook.md must name the gz validate --agents-md-map-conformance validator",
        )

    @covers("REQ-0.0.54-04-04")
    def test_governance_runbook_has_instruction_files_section(self) -> None:
        text = _GOV_RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(
            "## Instruction Files",
            text,
            "governance_runbook.md must have an Instruction Files section "
            "naming map-not-encyclopedia resting state",
        )

    @covers("REQ-0.0.54-04-04")
    def test_governance_runbook_names_map_not_encyclopedia_doctrine(self) -> None:
        text = _GOV_RUNBOOK.read_text(encoding="utf-8")
        self.assertIn(
            "map-not-encyclopedia",
            text,
            "governance_runbook.md must name the map-not-encyclopedia shape contract",
        )


class TrustDoctrineCrossLink(unittest.TestCase):
    """REQ-0.0.54-04-05: trust-doctrine promoted-scope catalogue includes the validator."""

    @covers("REQ-0.0.54-04-05")
    def test_trust_doctrine_cross_links_conformance_scope(self) -> None:
        text = _TRUST_DOCTRINE.read_text(encoding="utf-8")
        self.assertIn(
            "agents-md-map-conformance",
            text,
            "docs/governance/trust-doctrine.md must cross-link "
            "gz validate --agents-md-map-conformance scope",
        )

    @covers("REQ-0.0.54-04-05")
    def test_trust_doctrine_references_adr_0054(self) -> None:
        text = _TRUST_DOCTRINE.read_text(encoding="utf-8")
        self.assertIn(
            "ADR-0.0.54",
            text,
            "trust-doctrine.md conformance entry must cite ADR-0.0.54",
        )


class ConformanceValidatorGreen(unittest.TestCase):
    """REQ-0.0.54-04-06: gz validate --agents-md-map-conformance green across named scope."""

    @covers("REQ-0.0.54-04-06")
    def test_no_claude_md_prohibited_headings(self) -> None:
        text = _CLAUDE_MD.read_text(encoding="utf-8")
        hits = _has_prohibited_title(text)
        self.assertEqual(hits, [], f"CLAUDE.md prohibited heading(s): {hits}")

    @covers("REQ-0.0.54-04-06")
    def test_no_rule_files_prohibited_headings(self) -> None:
        for rule_file in [f for f in _RULES_DIR.glob("*.md") if f.name != "AGENTS.md"]:
            with self.subTest(rule=rule_file.name):
                text = rule_file.read_text(encoding="utf-8")
                hits = _has_prohibited_title(text)
                self.assertEqual(
                    hits,
                    [],
                    f"{rule_file.name} prohibited heading(s): {hits}",
                )

    @covers("REQ-0.0.54-04-06")
    def test_rule_files_within_tightened_budget(self) -> None:
        budget = json.loads(_BUDGET_PATH.read_text(encoding="utf-8"))
        rule_glob = next(g for g in budget["globs"] if g["pattern"] == ".claude/rules/*.md")
        limit = rule_glob["max_chars_per_file"]
        mirrors_dir = _PROJECT_ROOT / ".claude" / "rules"
        for mirror in mirrors_dir.glob("*.md"):
            size = len(mirror.read_text(encoding="utf-8"))
            with self.subTest(mirror=mirror.name):
                self.assertLessEqual(
                    size,
                    limit,
                    f"{mirror.name}: {size} chars exceeds {limit}-char budget",
                )


if __name__ == "__main__":
    unittest.main()
