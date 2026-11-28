"""Tests for ``audit_agents_md_numbering_citations`` (GHI #1375, a scope since GHI #1370).

Root `AGENTS.md` lost its Behavior Rules, Operator Economy and anti-vibing numbering on
2026-09-17; a live surface citing those numbers points at nothing. The audit reads
fixture trees here; the live tree is read by the `gz check` step.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import (
    agents_md_numbering_citations,
    audit_agents_md_numbering_citations,
)
from gzkit.governance.trust_audits.agents_md_numbering_citations import (
    ROOT_FILES,
    ROOTS,
    SKIPPED_FILES,
    dropped_numbering,
)

_STALE = "not resolve it unilaterally (Behavior Rule 9).\n"


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class AgentsMdNumberingCitationsTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), files)
            return [e.artifact for e in audit_agents_md_numbering_citations(root)]

    def test_a_dropped_number_on_each_root_and_root_file_is_flagged(self) -> None:
        files = {f"{rel}/x.md": _STALE for rel in ROOTS}
        files.update(dict.fromkeys(ROOT_FILES, _STALE))
        expected = sorted([f"{rel}/x.md" for rel in ROOTS] + list(ROOT_FILES))
        self.assertEqual(sorted(self._artifacts(files)), expected)

    def test_records_templates_and_the_handoff_parser_are_not_read(self) -> None:
        files = {
            ".gzkit/skills/s/proofs/p.md": _STALE,
            "docs/user/archive/a.md": _STALE,
            ".gzkit/rules/templates/t.md": _STALE,
            "docs/governance/g.md": _STALE,
            ".gzkit/skills/s/notes.txt": _STALE,
        }
        files.update(dict.fromkeys(SKIPPED_FILES, _STALE))
        self.assertEqual(self._artifacts(files), [])

    def test_the_fence_tells_a_dropped_number_from_a_live_citation(self) -> None:
        stale = (
            "not resolve it unilaterally (Behavior Rule 9).",
            "agent-writable only through gz verbs (`AGENTS.md` § Never #2).",
            "file it per `AGENTS.md` § Behavior Rules — Always #13.",
            "- **Never ask what canon already answers** (AGENTS.md § Operator Economy #7).",
            "The doctrine is explicit at `AGENTS.md` § Anti-vibing mantra operative claim 2:",
            "(see `AGENTS.md` § DO IT RIGHT, items 2 (6b) and 5 (6e)).",
            "`improvement` post-correction lessons (Behavior Rule #11), and",
            "(Behavior Rule Always #11) capturing the staleness and the adjustment.",
            "AGENTS.md § MAKE LLM STOCHASTIC VIBES INERT operative claim 3",
        )
        live = (
            (
                "The binding rule is `AGENTS.md` § Behavior Rules (the GHI-authoring rule; "
                "rationale in `docs/governance/behavior-rules.md` § Always #13)."
            ),
            "(see `AGENTS.md` § DO IT RIGHT, items 2 and 5).",
            "per the DO IT RIGHT maxim (`AGENTS.md` § DO IT RIGHT, items 1 and 7 (6c)).",
            "**Tests assert semantics, not strings (invariant 6f).**",
            (
                "``AGENTS.md`` § Behavior Rules was numbered until 2026-09, and the handoff "
                "corpus still cites it as ``Always #13``"
            ),
            "§ PRIME DIRECTIVE 4 and § DO IT RIGHT #3 bind here.",
            "See `AGENTS.md` § MAKE LLM STOCHASTIC VIBES INERT (doctrine drift).",
        )
        for text in stale:
            with self.subTest(stale=text):
                self.assertTrue(dropped_numbering(text))
        for text in live:
            with self.subTest(live=text):
                self.assertFalse(dropped_numbering(text))

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_agents_md_numbering_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_agents_md_numbering_citations(Path(tmp))
        self.assertEqual(on_gzkit, set(ROOTS) - {"src/gzkit"} | set(ROOT_FILES))
        self.assertEqual(on_adopter, [])

    def test_message_names_the_rule_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {".gzkit/skills/s/SKILL.md": _STALE})
            (error,) = audit_agents_md_numbering_citations(root)
        self.assertIn(".gzkit/skills/s/SKILL.md", error.message)
        self.assertIn("skill-authoring.md", error.message)
        self.assertIn("uv run gz validate --agents-md-numbering-citations", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["agents_md_numbering_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["agents-md-numbering-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(agents_md_numbering_citations, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_handoff_parser_is_read(self) -> None:
        with patch.object(agents_md_numbering_citations, "SKIPPED_FILES", ()):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
