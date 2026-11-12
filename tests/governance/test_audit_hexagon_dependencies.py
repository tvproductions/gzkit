"""`gz validate --hexagon-dependencies`: the package map, the checker and the baseline.

The scope holds a project to `docs/governance/hexagonal-architecture.md` § The
dependency rules, with today's findings in a shrink-only baseline (RP-15 tranche 6).
Its error prose carries the three parts `.gzkit/rules/guardrail-feedback-prose.md`
requires of every fail-closed surface: what failed, why, and the runnable next step.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.governance.trust_audits.hexagon_dependencies import (
    BASELINE_NAME,
    audit_hexagon_dependencies,
)

MAP = """
[tool.py-gzkit.hexagon]
package = "app"
source-root = "src"
domain = ["app.core.domain"]
driving-adapters = ["app.cli"]
"""

TREE = {
    "app/__init__.py": "",
    "app/core/__init__.py": "",
    "app/core/domain/__init__.py": "",
    "app/cli/__init__.py": "",
    "app/cli/main.py": "",
}

BREACH = "import app.core.domain.record -> app.cli"


def _project(root: Path, pyproject: str, files: dict[str, str], held: list[str] | None) -> None:
    (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
    for rel, body in {**TREE, **files}.items():
        target = root / "src" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    if held is not None:
        (root / "data").mkdir(parents=True, exist_ok=True)
        (root / "data" / BASELINE_NAME).write_text(json.dumps({"findings": held}), encoding="utf-8")


def _audit(pyproject: str, files: dict[str, str], held: list[str] | None = None) -> list[str]:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        _project(root, pyproject, files, held)
        return [e.message for e in audit_hexagon_dependencies(root)]


PLANTED = {"app/core/domain/record.py": "from app.cli import main\n"}


class TheScopeJudgesAgainstTheBaseline(unittest.TestCase):
    def test_a_conforming_tree_passes(self) -> None:
        self.assertEqual(_audit(MAP, {}), [])

    def test_a_new_finding_fails(self) -> None:
        messages = _audit(MAP, PLANTED)
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].startswith(BREACH))

    def test_a_held_finding_passes(self) -> None:
        self.assertEqual(_audit(MAP, PLANTED, held=[BREACH]), [])

    def test_a_repaired_finding_left_in_the_baseline_fails(self) -> None:
        messages = _audit(MAP, {}, held=[BREACH])
        self.assertEqual(len(messages), 1)
        self.assertTrue(messages[0].startswith(f"{BREACH}: repaired"))


class TheScopeReadsThePackageMap(unittest.TestCase):
    def test_a_project_with_no_map_has_nothing_to_check(self) -> None:
        self.assertEqual(_audit("[project]\nname = 'app'\n", PLANTED), [])

    def test_a_malformed_map_fails(self) -> None:
        malformed = MAP + 'adapters = ["app.x"]\n'
        messages = _audit(malformed, {})
        self.assertEqual(len(messages), 1)
        self.assertIn("unknown keys", messages[0])


class TheProseNamesTheCauseTheRuleAndTheNextStep(unittest.TestCase):
    """Three-part recovery prose (`.gzkit/rules/guardrail-feedback-prose.md`)."""

    RERUN = "uv run gz validate --hexagon-dependencies"
    RULE = "docs/governance/hexagonal-architecture.md § The dependency rules"

    def test_every_failure_shape_carries_all_three_parts(self) -> None:
        cases = {
            "new finding": (_audit(MAP, PLANTED), BREACH),
            "repaired finding": (_audit(MAP, {}, held=[BREACH]), BREACH),
            "malformed map": (_audit(MAP + 'adapters = ["app.x"]\n', {}), "unknown keys"),
        }
        for name, (messages, cause) in cases.items():
            with self.subTest(name):
                self.assertEqual(len(messages), 1)
                self.assertIn(cause, messages[0])
                self.assertIn(self.RULE, messages[0])
                self.assertIn(self.RERUN, messages[0])


if __name__ == "__main__":
    unittest.main()
