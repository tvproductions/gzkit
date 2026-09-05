"""REQ-derived tests for OBPI-0.0.54-04 (apply doctrine to CLAUDE.md and rules).

Covers the six acceptance criteria in the OBPI brief:
* REQ-0.0.54-04-01 — CLAUDE.md audit clean (no prohibited shapes)
* REQ-0.0.54-04-02 — .gzkit/rules/*.md prohibited shapes lifted; See-links present
* REQ-0.0.54-04-03 — data/instructions_files_budget.json enforces per-file budgets
* REQ-0.0.54-04-04 — runbooks updated in same patch set as doctrine application
* REQ-0.0.54-04-05 — trust-doctrine cross-links agents-md-map-conformance scope
* REQ-0.0.54-04-06 — gz validate --agents-md-map-conformance green across named scope
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import (
    audit_agents_md_map_conformance,
    audit_instructions_files_budget,
)
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CLAUDE_MD = _PROJECT_ROOT / "CLAUDE.md"
_RULES_DIR = _PROJECT_ROOT / ".gzkit" / "rules"
_BUDGET_PATH = _PROJECT_ROOT / "data" / "instructions_files_budget.json"
_USER_RUNBOOK = _PROJECT_ROOT / "docs" / "user" / "runbook.md"
_GOV_RUNBOOK = _PROJECT_ROOT / "docs" / "governance" / "governance_runbook.md"
_TRUST_DOCTRINE = _PROJECT_ROOT / "docs" / "governance" / "trust-doctrine.md"
_AGENTS_MD = _PROJECT_ROOT / "AGENTS.md"
_RULES_GLOB_DIR = _PROJECT_ROOT / ".claude" / "rules"

# gzkit's project-doc budget ceiling (BYTES). Codex's CLI default
# ``project_doc_max_bytes`` is 32768 B — root AGENTS.md is silently truncated
# past that UNDER CODEX (github.com/openai/codex issue #7138). Per operator
# ruling 2026-07-06 this ceiling is DECOUPLED from that vendor cap (hexagonal:
# an adapter limit must not gate the core). gzkit RAISES that default to the
# value in data/vendor-manifest.json via the .codex/config.toml it generates,
# which Codex loads in a trusted directory (GHI #962) — so the runtime cut is
# the configured cap, not 32768. `gz validate --instructions-files-budget`
# observes the delivered bytes; corpus-splitting (GHI #533) remains the durable
# headroom path.
_PROJECT_DOC_BUDGET_CEILING_BYTES = 65536


def _budget_within_ceiling(char_budget: int) -> bool:
    """A configured per-turn char budget must not exceed Codex's project-doc byte
    cap; a budget above the cap would green-light a silently-truncated surface."""
    return char_budget <= _PROJECT_DOC_BUDGET_CEILING_BYTES


class ClaudeMdCleanAudit(unittest.TestCase):
    """REQ-0.0.54-04-01: CLAUDE.md has no prohibited shapes."""

    @covers("REQ-0.0.54-04-01")
    def test_claude_md_passes_the_conformance_validator(self) -> None:
        """Delegate to the validator instead of re-implementing its rule.

        Folded under the `decommission-tautological-tests` chore. This replaced
        two tests that read CLAUDE.md and re-derived the doctrine check locally
        via `_has_prohibited_title` — a SECOND implementation of a rule that
        already ships as `gz validate --agents-md-map-conformance`. That is worse
        than a tautology: a local copy keeps passing against the OLD rule after
        the validator changes, so the test reports green precisely when the
        doctrine it guards has moved.
        """
        errors = [
            e
            for e in audit_agents_md_map_conformance(_PROJECT_ROOT)
            if "CLAUDE.md" in str(e.artifact)
        ]
        self.assertEqual(errors, [], [e.message for e in errors])


class RuleFilesProhibitedShapesLifted(unittest.TestCase):
    """REQ-0.0.54-04-02: .gzkit/rules/*.md shape-conformant; lifted sections have See-links."""

    def _canonical_rule_files(self) -> list[Path]:
        return [f for f in _RULES_DIR.glob("*.md") if f.name != "AGENTS.md"]

    @covers("REQ-0.0.54-04-02")
    def test_rule_files_pass_the_conformance_validator(self) -> None:
        """Delegate rather than re-derive — same fold as REQ-04-01.

        The corpus is asserted non-empty so a validator that silently stopped
        covering the rules tree cannot pass this by examining nothing.
        """
        self.assertTrue(self._canonical_rule_files(), "no canonical rule files to check")
        errors = audit_agents_md_map_conformance(_PROJECT_ROOT)
        self.assertEqual(errors, [], [e.message for e in errors])

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
    def test_configured_budgets_are_met(self) -> None:
        """Delegate to `gz validate --instructions-files-budget`.

        The two tests replaced here re-read the budget JSON and re-derived the
        per-file and per-glob comparisons the shipped validator already performs
        — a third copy of the same arithmetic, free to drift from the gate that
        actually blocks a commit.
        """
        errors = audit_instructions_files_budget(_PROJECT_ROOT)
        self.assertEqual(errors, [], [e.message for e in errors])

    @covers("REQ-0.0.54-04-03")
    def test_agents_md_fits_the_codex_project_doc_cap(self) -> None:
        """KEPT as a real assertion — no validator covers it.

        The budget validator enforces the CONFIGURED budget; this fence is about
        a vendor cap the configuration is deliberately decoupled from (operator
        ruling 2026-07-06: an adapter limit must not gate the core). Codex still
        truncates at 32768 B at runtime, so this is a behavioural claim about a
        surface no gz scope owns (GHI #519).
        """
        payload = json.loads(_BUDGET_PATH.read_text(encoding="utf-8"))
        self.assertTrue(
            _budget_within_ceiling(payload["files"]["AGENTS.md"]),
            f"AGENTS.md budget {payload['files']['AGENTS.md']} exceeds the Codex cap",
        )
        agents_bytes = len(_AGENTS_MD.read_text(encoding="utf-8").encode("utf-8"))
        self.assertLessEqual(
            agents_bytes,
            _PROJECT_DOC_BUDGET_CEILING_BYTES,
            f"AGENTS.md is {agents_bytes} B, over the Codex project-doc cap "
            f"{_PROJECT_DOC_BUDGET_CEILING_BYTES} B (silent truncation; GHI #519)",
        )


# REQ-0.0.54-04-04 and -04-05 were re-kinded BEHAVIOR -> SUPPORT (operator ruling
# 2026-08-15) and the six doc-grep tests that stood here are DELETED. They read
# `docs/user/runbook.md`, `docs/governance/governance_runbook.md` and
# `docs/governance/trust-doctrine.md` and asserted substrings were present —
# `grep` wearing a `unittest` costume, which cannot fail when behaviour breaks,
# only when someone rewords a sentence (`.gzkit/rules/tests.md` § The
# discriminator). Both REQs claim an ARTIFACT property, so their proof channel is
# SUPPORT: the cited artifact present on disk plus a structural validator
# admitting its shape — no `@covers` test is required or appropriate.
#
# They were not deletable before the ruling: the brief is Completed, so its REQ
# kinds were sealed, and a BEHAVIOR REQ with no covering test fails the
# REQ-coverage gate. The tests were forbidden by the rule and mandated by the
# kind at the same time.


class ConformanceValidatorGreen(unittest.TestCase):
    """REQ-0.0.54-04-06: gz validate --agents-md-map-conformance green across named scope."""

    @covers("REQ-0.0.54-04-06")
    def test_the_conformance_scope_is_green(self) -> None:
        """Call the validator the REQ names.

        Folded under the `decommission-tautological-tests` chore. This class was
        named `ConformanceValidatorGreen` and contained three tests that NEVER
        INVOKED THE VALIDATOR — they re-derived its heading rule via the local
        `_has_prohibited_title` and re-derived the budget arithmetic from the
        budget JSON. A test asserting "the validator is green" that never runs
        the validator cannot fail when the validator does, which is the exact
        facade shape gzkit's negative-control system exists to refuse.
        """
        errors = audit_agents_md_map_conformance(_PROJECT_ROOT)
        self.assertEqual(errors, [], [e.message for e in errors])

    @covers("REQ-0.0.54-04-06")
    def test_the_budget_scope_is_green(self) -> None:
        """The other half of the same REQ, delegated the same way."""
        errors = audit_instructions_files_budget(_PROJECT_ROOT)
        self.assertEqual(errors, [], [e.message for e in errors])


if __name__ == "__main__":
    unittest.main()
