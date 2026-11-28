"""Tests for ``audit_campaign_credit_citations`` (GHI #1376, a scope since GHI #1370).

Campaign work selection is carried by gz-obpi-pipeline; a live surface crediting root
`AGENTS.md` with naming or ruling the campaign is stale. The audit reads fixture trees
here; the live tree is read by the `gz check` step.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import (
    audit_campaign_credit_citations,
    campaign_credit_citations,
)
from gzkit.governance.trust_audits.campaign_credit_citations import (
    HISTORY_FILES,
    ROOT_FILES,
    ROOTS,
    campaign_credited_to_canon,
)

_STALE = "The active campaign is Magna Carta (`AGENTS.md` § Operator Doctrine) here.\n"


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class CampaignCreditCitationsTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), files)
            return [e.artifact for e in audit_campaign_credit_citations(root)]

    def test_a_credit_on_each_root_and_root_file_is_flagged(self) -> None:
        files = {f"{rel}/x.md": _STALE for rel in ROOTS}
        files.update(dict.fromkeys(ROOT_FILES, _STALE))
        expected = sorted([f"{rel}/x.md" for rel in ROOTS] + list(ROOT_FILES))
        self.assertEqual(sorted(self._artifacts(files)), expected)

    def test_dated_history_and_record_paths_are_not_read(self) -> None:
        files = {
            "docs/governance/build-to-1.0-campaign-2026-06-10.md": _STALE,
            "docs/governance/audit-2026-09-30/a.md": _STALE,
            ".gzkit/chores/c/proofs/p.md": _STALE,
            "docs/user/archive/a.md": _STALE,
        }
        files.update(dict.fromkeys(HISTORY_FILES, _STALE))
        self.assertEqual(self._artifacts(files), [])

    def test_the_fence_tells_a_credit_from_the_current_text(self) -> None:
        stale = (
            (
                "will compete with the active campaign, which is Magna Carta (`AGENTS.md` § "
                "Operator Doctrine). The sample's"
            ),
            (
                "acting on them is the work: `AGENTS.md` § Operator Doctrine states that the "
                'campaign plan *"rules every session"*.'
            ),
        )
        current = (
            (
                "will compete with the active campaign plan, which governs work selection "
                "(`gz-obpi-pipeline` carries that ruling, per `AGENTS.md` § Operator Doctrine)."
            ),
            "## Active campaign — Magna Carta",
            (
                "Boundary 1 was retired 2026-09-29: superseded by the Magna Carta's release "
                "prioritization, per AGENTS.md."
            ),
        )
        for text in stale:
            with self.subTest(stale=text):
                self.assertTrue(campaign_credited_to_canon(text))
        for text in current:
            with self.subTest(current=text):
                self.assertFalse(campaign_credited_to_canon(text))

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_campaign_credit_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_campaign_credit_citations(Path(tmp))
        expected = set(ROOTS) - {"src/gzkit"} | set(ROOT_FILES) | set(HISTORY_FILES)
        self.assertEqual(on_gzkit, expected)
        self.assertEqual(on_adopter, [])

    def test_message_names_the_new_home_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {".gzkit/skills/s/SKILL.md": _STALE})
            (error,) = audit_campaign_credit_citations(root)
        self.assertIn(".gzkit/skills/s/SKILL.md", error.message)
        self.assertIn("gz-obpi-pipeline", error.message)
        self.assertIn("uv run gz validate --campaign-credit-citations", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["campaign_credit_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["campaign-credit-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(campaign_credit_citations, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_history_file_is_read(self) -> None:
        with patch.object(campaign_credit_citations, "HISTORY_FILES", ()):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
