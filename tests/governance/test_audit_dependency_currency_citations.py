"""Tests for ``audit_dependency_currency_citations`` (GHI #1368, a scope since GHI #1370).

The dependency-currency chore owns the currency grade; a live surface that states
a dependency age as a grade drifts from it. The audit reads fixture trees here;
the live tree is read by the `gz check` step that runs the scope.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.commands import validate_cmd
from gzkit.enforcement import _run_single_claim, production_enforcement_registry
from gzkit.governance.trust_audits import (
    audit_dependency_currency_citations,
    dependency_currency_citations,
)
from gzkit.governance.trust_audits.dependency_currency_citations import (
    AUTHORITY,
    ROOT_FILES,
    ROOTS,
    currency_ages,
)

_GRADE = "A dependency older than 2 years is stale.\n"
_CHORE_GRADE = "An analyzer with no release in 1y is abandoned.\n"


def _tree(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    return root


class DependencyCurrencyCitationsTests(unittest.TestCase):
    def _artifacts(self, files: dict[str, str]) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), files)
            return [e.artifact for e in audit_dependency_currency_citations(root)]

    def test_a_grade_on_each_root_and_root_file_is_flagged(self) -> None:
        files = {f"{rel}/x.md": _GRADE for rel in ROOTS}
        files.update(dict.fromkeys(ROOT_FILES, _GRADE))
        expected = sorted([f"{rel}/x.md" for rel in ROOTS] + list(ROOT_FILES))
        self.assertEqual(sorted(self._artifacts(files)), expected)

    def test_dated_records_proofs_and_archives_are_not_read(self) -> None:
        artifacts = self._artifacts(
            {
                "docs/rnd/r.md": _GRADE,
                ".gzkit/chores/c/proofs/p.md": _GRADE,
                "docs/archive/a.md": _GRADE,
            }
        )
        self.assertEqual(artifacts, [])

    def test_the_chore_may_state_its_own_grade(self) -> None:
        self.assertEqual(self._artifacts(dict.fromkeys(AUTHORITY, _CHORE_GRADE)), [])

    def test_a_chore_that_states_no_grade_is_a_finding(self) -> None:
        artifacts = self._artifacts({AUTHORITY[0]: "Bring each dependency to latest.\n"})
        self.assertEqual(artifacts, [AUTHORITY[0]])

    def test_the_fence_tells_a_currency_grade_from_other_ages(self) -> None:
        grades = (
            (
                "| `dep-currency` | `dependency-currency` chore "
                "| Outdated runtime deps (>5y aging policy) |"
            ),
            "TODO older than 90 days, dependency >2y stale (not yet 5y), CLI verb registered",
            "Flag any dependency more than 18 months out of date.",
            "A package two years behind upstream is High.",
            "Dependencies\n   older than 2 years are\n   *stale*.",
            "An analyzer with no release in 1y is abandoned.",
            "A dependency not updated in 400 days is High.",
            "A pin 18 months old.",
            "The last release was 3 years ago for that library.",
            "No release for 24 months on the analyzer.",
            "Lagged upstream by 9 months.",
            "Deps over 1y old.",
            "Tool versions more than 6 months stale.",
            "A dependency older than 12 weeks.",
        )
        not_grades = (
            "Five-year aging is the minimum signal for ecosystem trust.",
            "TODOs older than 90 days, FIXMEs without GHI refs",
            "Maintenance health: active releases in last 12 months OR project declares done state.",
            "Stale (>6 months, no promotion signal): Candidate for archival with rationale.",
            "Dependencies behind upstream latest, as the dependency-currency chore grades them.",
            "TODO older than 90 days, a dependency or analyzer the dep-currency probe reports",
            "A library adopted after five years of releases.",
            "Runs ~1 week behind, skips releases with major regressions.",
            "- If ledger entries are older than 7 days\n- If Layer 1 tools have been updated",
            "rows 45b-45d landed; the rule left its grandfather pin behind at rule 0.6.0",
        )
        for text in grades:
            with self.subTest(grade=text):
                self.assertTrue(currency_ages(text))
        for text in not_grades:
            with self.subTest(not_grade=text):
                self.assertFalse(currency_ages(text))

    def test_a_missing_root_is_a_finding_on_gzkits_tree_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            framework = _tree(Path(tmp), {"src/gzkit/__init__.py": ""})
            on_gzkit = {e.artifact for e in audit_dependency_currency_citations(framework)}
        with tempfile.TemporaryDirectory() as tmp:
            on_adopter = audit_dependency_currency_citations(Path(tmp))
        expected = set(ROOTS) - {"src/gzkit"} | set(ROOT_FILES) | set(AUTHORITY)
        self.assertEqual(on_gzkit, expected)
        self.assertEqual(on_adopter, [])

    def test_message_names_the_chore_and_the_recovery_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _tree(Path(tmp), {".gzkit/skills/s/SKILL.md": _GRADE})
            (error,) = audit_dependency_currency_citations(root)
        self.assertIn(".gzkit/skills/s/SKILL.md", error.message)
        self.assertIn("dependency-currency/CHORE.md", error.message)
        self.assertIn("uv run gz validate --dependency-currency-citations", error.message)


class DispatchAndControlTests(unittest.TestCase):
    """The scope runs in the default tier, and its control fails when the scope narrows."""

    def test_scope_runs_in_the_default_tier(self) -> None:
        entries = {e.stem: e for e in validate_cmd.VALIDATOR_REGISTRY}
        self.assertEqual("default", entries["dependency_currency_citations"].tier)

    def _control_outcome(self) -> str:
        records = {r.claim_id: r for r in production_enforcement_registry()}
        return _run_single_claim(records["dependency-currency-citations"]).outcome

    def test_the_control_catches_its_fixture(self) -> None:
        self.assertEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_scope_drops_a_root(self) -> None:
        with patch.object(dependency_currency_citations, "ROOTS", ROOTS[1:]):
            self.assertNotEqual(self._control_outcome(), "PASS")

    def test_the_control_fails_when_the_dated_records_are_read(self) -> None:
        with patch.object(dependency_currency_citations, "DATED_RECORDS", ()):
            self.assertNotEqual(self._control_outcome(), "PASS")


if __name__ == "__main__":
    unittest.main()
