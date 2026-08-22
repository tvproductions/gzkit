"""Ratchet-direction tests for the module-size gate (GHI #853).

`compute_breaches` enforced four directions and was silent on a fifth: an
entry looser than the module it governs. Measured 2026-08-22 at `6b2a1c67`,
928 SLOC across four entries were re-consumable with the gate at exit 0 —
`ADR-0.0.73` Boundary Invariant #8 requires "a committed baseline the list can
only decrease against", and a baseline nothing reports as un-advanced only
decreases when someone remembers.

These tests drive the pure `compute_breaches` function with synthetic data.
The committed data file carrying zero slack is enforced by the gate itself
inside `gz check`, not re-measured here: a second measurement path would be
the second threshold authority the chore's own docstring forbids.

There is deliberately NO test asserting the `--self-test` case list mentions
the slack direction. Such a test reads the gate's own source and asserts on
its text, which `gz validate --tautological-test-audit` rejects and
`.claude/rules/guardrail-feedback-prose.md` § Enforcement posture refuses on
the stated ground that an inferential prose-grader is weaker than a real
enforcement consumer. The direction's teeth are proven by the four
`compute_breaches` cases below; the self-test's own coverage is proven by
`run_module_size_audit`, which runs `--self-test` and short-circuits on it.
"""

from __future__ import annotations

import importlib.util
import unittest
from types import ModuleType

from gzkit.commands.common import get_project_root

# The canonical authored copy. `gz agent sync control-surfaces` mirrors it to
# `src/gzkit/chores/` for the wheel, and `gz validate --distribution` fails
# closed on any drift between them, so testing one tests both.
_SCRIPT = (
    get_project_root() / ".gzkit" / "chores" / "module-sloc-cap-radon" / "check_module_size.py"
)


def _load_gate() -> ModuleType:
    """Import the chore script by path; its directory name is not an identifier."""
    spec = importlib.util.spec_from_file_location("_module_size_gate", _SCRIPT)
    if spec is None or spec.loader is None:
        raise unittest.SkipTest(f"cannot load {_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestSlackDirection(unittest.TestCase):
    """An entry looser than its module must fail closed."""

    def setUp(self) -> None:
        self.gate = _load_gate()
        self.block = 1000.0

    def test_entry_looser_than_its_module_is_a_breach(self) -> None:
        """The fifth direction: recorded ceiling above current SLOC.

        Both values sit over the band, so no other arm fires — arm 1 skips a
        listed path, arm 2 wants growth, arm 4 wants the module under the band.
        Silence here is exactly the 928-line hole.
        """
        breaches = self.gate.compute_breaches(self.block, {"a.py": 1100}, {"a.py": 1500})

        self.assertTrue(
            breaches,
            "An entry recording 1500 for an 1100-SLOC module licenses 400 lines of "
            "silent re-growth; the ratchet must report it",
        )

    def test_the_breach_names_the_surrenderable_slack(self) -> None:
        """The report must be actionable without re-deriving the arithmetic.

        Asserts the quantity and the target, not the sentence: a message that
        omits how much is surrenderable makes the operator recompute what the
        gate already knows.
        """
        breaches = self.gate.compute_breaches(self.block, {"a.py": 1100}, {"a.py": 1500})
        text = "\n".join(breaches)

        self.assertIn("400", text, f"Breach must state the slack quantity; got {text!r}")
        self.assertIn("1100", text, f"Breach must state the tightened ceiling; got {text!r}")

    def test_an_entry_at_its_module_size_is_clean(self) -> None:
        """Zero headroom is the ratchet's resting state, never a breach.

        This is the direct consequence of the operator ruling of 2026-08-22
        (fail closed and tighten now): every entry lands at current SLOC, so a
        gate that objected to equality would fail on its own repaired data.
        """
        breaches = self.gate.compute_breaches(self.block, {"a.py": 1500}, {"a.py": 1500})

        self.assertEqual(breaches, [], f"Equality must be clean; got {breaches!r}")

    def test_a_module_still_shrinking_toward_the_band_is_not_excused(self) -> None:
        """Improvement is not an exemption.

        The pre-GHI-#853 gate called this case clean outright ("listed module
        shrank but is still over"). Shrinking earns the entry a tightening, not
        silence — otherwise the ratchet advances only when a human aims it.
        """
        breaches = self.gate.compute_breaches(self.block, {"a.py": 1200}, {"a.py": 1500})

        self.assertTrue(
            breaches,
            "A module that shrank 1500 -> 1200 must be asked to surrender the 300 "
            "lines, not passed over",
        )


if __name__ == "__main__":
    unittest.main()
