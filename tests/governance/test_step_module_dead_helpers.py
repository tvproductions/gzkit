"""No step module keeps a private helper nothing calls (GHI #918).

`features/steps/justify_steps.py` defined `_stop_gh_patcher` and never called
it. The consequence was already neutralized -- GHI #916 put
`mock.patch.stopall()` in `after_scenario`, which stops that patcher too -- so
nothing failed. What survived was the SHAPE, and its hazard is that it reads as
handled: a reader auditing the module for the GHI #916 leak pattern finds a
teardown next to the `start()`, matches them, and moves on.

A decoy is worse than an absence. `features/steps/patch_release_steps.py` calls
`.start()` with no teardown at all and is CORRECT, because the net owns
scenario teardown; the module that looked more careful was the one that was
wrong. This fence exists so that asymmetry cannot be re-introduced by someone
"restoring" a teardown that only appears to discharge an obligation.
"""

import ast
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STEPS = REPO / "features" / "steps"


class TestStepModuleDeadHelpers(unittest.TestCase):
    """A private helper defined and never referenced is dead or a decoy."""

    def test_no_private_helper_is_defined_and_never_referenced(self) -> None:
        """Every `_`-prefixed function in a step module is called somewhere.

        Scoped to private helpers on purpose. Behave's `@given`/`@when`/`@then`
        functions are invoked by the decorator's registry, never by name, so a
        name-reference check would report every step as dead.
        """
        orphans: list[str] = []
        for module in sorted(STEPS.glob("*.py")):
            source = module.read_text(encoding="utf-8")
            tree = ast.parse(source)
            defined = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, ast.FunctionDef) and node.name.startswith("_")
            }
            if not defined:
                continue
            # Count NAME references across the whole tree, then discount the
            # single binding occurrence each definition contributes.
            used: dict[str, int] = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used[node.id] = used.get(node.id, 0) + 1
                elif isinstance(node, ast.Attribute):
                    used[node.attr] = used.get(node.attr, 0) + 1
            for name in sorted(defined):
                if used.get(name, 0) == 0:
                    orphans.append(f"{module.relative_to(REPO)}::{name}")

        self.assertEqual(
            orphans,
            [],
            "private step-module helper defined but never called — wire it or "
            "delete it; the middle state reads as a discharged obligation "
            f"while discharging nothing: {orphans}",
        )


if __name__ == "__main__":
    unittest.main()
