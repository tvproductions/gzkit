"""The `@covers` fence's subject must stay "tests for this scope" (GHI #944).

`test_kind_invariance_docs.py` asserts that every test for OBPI-0.0.35-04's
scope carries `@covers("REQ-0.0.35-04-NN")`. That requirement's subject is
"every test for this scope" — but the fence was implemented as "every test
method in four named files", two of which are general-purpose.

The difference is load-bearing. `tests/commands/test_validate.py` accrues
tests for every `gz validate` concern, so asserting over all of it closed the
file: a defect fix for output rendering could not add a test there without
fabricating a REQ claim. Worse, the closure had already manufactured false
coverage — three `--receipt-shape` tests carry `@covers("REQ-0.0.35-04-01")`
despite having nothing to do with kind-invariance, because that was the only
way past the fence.

These tests pin the repaired subject. They live here rather than beside the
fence because their subject is the fence, not kind-invariance — putting them
in a scope-owned file would have required exactly the fabricated `@covers`
this repair exists to stop.
"""

from __future__ import annotations

import unittest

from tests.governance.test_kind_invariance_docs import (
    PROJECT_ROOT,
    SHARED_TEST_FILES,
    _scope_test_methods,
    _test_methods,
    _uncovered_tests,
    fence_roster,
)


class TestCoversFenceScope(unittest.TestCase):
    """The fence demands coverage only from tests that are for its scope."""

    def test_shared_files_are_scoped_per_method_in_the_roster(self):
        """The fence's own policy must mark every shared file scoped.

        This is the guard that actually bites. The other tests here describe
        today's tree, and today's tree passes a whole-file assertion by
        accident — every existing test happens to carry `@covers`, because the
        broken fence forced them to. The defect only surfaces when someone adds
        an unrelated test. So the witness has to observe the policy, not its
        current outcome: flip a shared file back to whole-file and this fails
        immediately, rather than waiting for the next contributor to discover it.
        """
        roster = dict(fence_roster())

        for path in SHARED_TEST_FILES:
            self.assertIn(path, roster, f"{path.name} missing from the fence roster")
            self.assertTrue(
                roster[path],
                f"{path.name} is a general-purpose file; the fence must demand "
                "@covers only from the tests in it that exercise this scope.",
            )

    def test_fence_never_demands_coverage_from_a_non_scope_test(self):
        """The fence may only demand `@covers` from tests that are for this scope.

        Pins the repair itself. `test_quality.py` happens to hold only one
        test and it is a scope test, so a proper-subset pin would be wrong
        there; what must hold in every shared file is that the set the fence
        demands from never grows beyond the scope set.
        """
        for path in SHARED_TEST_FILES:
            owing = _scope_test_methods(path)

            self.assertLessEqual(
                owing,
                _test_methods(path),
                f"{path.name}: scope set is not a subset of the file's tests",
            )
            self.assertFalse(
                _uncovered_tests(path, scope_only=True) - owing,
                f"{path.name}: the fence is demanding @covers from a test that "
                "is not for this scope.",
            )

    def test_the_motivating_shared_file_stays_open(self):
        """`test_validate.py` holds tests for scopes this OBPI never touched.

        This is the concrete state the old fence broke: it asserted over every
        method in this file, so a `gz validate` output-rendering fix (GHI #944)
        could not add a test here without fabricating a `REQ-0.0.35-04-NN`
        claim. If this set ever empties, the fence has closed the file again.
        """
        path = PROJECT_ROOT / "tests" / "commands" / "test_validate.py"

        self.assertTrue(
            _test_methods(path) - _scope_test_methods(path),
            "every test in test_validate.py now reads as a kind-invariance "
            "test; the fence's scope distinction has lost its subject.",
        )


if __name__ == "__main__":
    unittest.main()
