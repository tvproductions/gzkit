"""Tests for ``audit_size_limit_citations`` (GHI #1366, ported to a scope by GHI #1370).

Function and module size are the threshold table's bands; an instruction surface
may state no size limit as a number, and source may state one only as dated
history. The audit reads fixture trees here; the live tree is read by the
`gz check` step that runs the scope.
"""

import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import audit_size_limit_citations, size_limit_citations
from gzkit.governance.trust_audits.size_limit_citations import (
    HISTORY,
    INSTRUCTION_ROOTS,
    SOURCE_ROOT,
    states_size_limit,
)


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class SizeLimitCitationsTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            return [e.artifact for e in audit_size_limit_citations(_tree(Path(tmp), files))]

    def test_a_limit_on_each_instruction_surface_is_flagged(self) -> None:
        files = {
            f"{rel}/x.md": "intro\nKeep functions under 50 lines.\n" for rel in INSTRUCTION_ROOTS
        }
        self.assertEqual(
            sorted(self._artifacts(files)), sorted(f"{rel}/x.md:2" for rel in INSTRUCTION_ROOTS)
        )

    def test_source_states_a_limit_only_as_dated_history(self) -> None:
        artifacts = self._artifacts(
            {
                f"{SOURCE_ROOT}/a.py": (
                    '"""Split to stay under the 600-line module cap then in force."""\n'
                ),
                f"{SOURCE_ROOT}/b.py": '"""Keep modules under the 600-line cap."""\n',
            }
        )
        self.assertEqual(artifacts, [f"{SOURCE_ROOT}/b.py:1"])

    def test_the_authority_and_other_suffixes_are_not_read(self) -> None:
        artifacts = self._artifacts(
            {
                ".gzkit/rules/complexity-thresholds.md": "Functions over 50 lines warn.\n",
                ".gzkit/rules/notes.txt": "Functions over 50 lines warn.\n",
            }
        )
        self.assertEqual(artifacts, [])

    def test_the_fence_tells_a_limit_from_a_measurement(self) -> None:
        limits = (
            "Functions exceeding 50 lines or modules exceeding 600 lines",
            "| size-cap | Functions >50 LOC, modules >600 LOC |",
            "The 600-line module cap and 50-line function cap are the floor.",
            "A function over fifty lines is not inherently wrong.",
            "Extracted to keep both modules under the 600-line cap.",
        )
        not_limits = (
            "This 87-line function has three responsibility boundaries.",
            "Classes >300 lines (pythonic.md owns this one).",
            "Past the warn band of lizard_nloc in the threshold table.",
            "Instruction files: trim before attestation (200-line ceiling).",
        )
        for text in limits:
            with self.subTest(limit=text):
                self.assertTrue(states_size_limit(text))
        for text in not_limits:
            with self.subTest(not_limit=text):
                self.assertFalse(states_size_limit(text))

    def test_dated_history_is_a_limit_the_history_allowance_admits(self) -> None:
        line = "Split to stay under the 600-line module cap then in force."
        self.assertTrue(states_size_limit(line))
        self.assertTrue(HISTORY.search(line))

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_size_limit_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_size_limit_citations(Path(tmp))
        self.assertEqual(on_gzkit, set(INSTRUCTION_ROOTS))
        self.assertEqual(on_adopter, [])

    def test_message_names_the_rule_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {".gzkit/skills/s/SKILL.md": "modules >600 LOC\n"})
            (error,) = audit_size_limit_citations(root)
        self.assertIn(".gzkit/skills/s/SKILL.md:1", error.message)
        self.assertIn("pythonic.md", error.message)
        self.assertIn("complexity-thresholds.json", error.message)
        self.assertIn("uv run gz validate --size-limit-citations", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["size_limit_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["size-limit-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        narrowed = INSTRUCTION_ROOTS[1:]
        with patch.object(size_limit_citations, "INSTRUCTION_ROOTS", narrowed):
            self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_history_allowance_is_lost(self) -> None:
        with patch.object(size_limit_citations, "HISTORY", re.compile(r"(?!)")):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
