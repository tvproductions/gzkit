"""The NC runner never removes a path it was not given as a temp fixture (GHI #920).

`_run_single_claim` ends with `shutil.rmtree(fixture_path, ignore_errors=True)`
on whatever `Path` the registered fixture returned, with no precondition on what
that path IS. The runner inferred "this is a disposable fixture" from "this is a
`Path`" -- a presence check standing in for a state check -- and `ignore_errors`
guaranteed it would never complain about the difference.

Measured 2026-08-29: a fixture written as `return REPO` (the repository root,
handed over because the entrypoint needed *some* real directory) caused
`python -m unittest` to delete the working repository. The authoring mistake was
real; converting it into data loss was a separate defect, and this is that one.

`_mkroot` -- the only sanctioned fixture builder -- always returns
`tempfile.mkdtemp(...)`, so "under the temp root" is the invariant the runner was
already relying on without ever asserting it. A fixture path outside that root is
a caller error and must be REPORTED, never obeyed.
"""

import shutil
import tempfile
import unittest
from pathlib import Path
from uuid import uuid4

from gzkit.enforcement import EnforcementClaimRecord, _run_single_claim


def _entrypoint_catches(_root: Path) -> int:
    return 1


class TestFixtureCleanupGuard(unittest.TestCase):
    """A non-temp fixture path is a reported TEST_BUG, not a deletion."""

    def setUp(self) -> None:
        # Deliberately OUTSIDE the temp root, which is the whole point. Harmless
        # if the guard regresses -- this directory is created here and owned here
        # -- but its survival is the assertion that carries the safety property.
        self.canary = Path.home() / f".gzkit-nc-guard-canary-{uuid4().hex}"
        (self.canary / "keep").mkdir(parents=True)
        (self.canary / "keep" / "evidence.txt").write_text("do not delete", encoding="utf-8")

    def tearDown(self) -> None:
        shutil.rmtree(self.canary, ignore_errors=True)

    def _record(self, fixture) -> EnforcementClaimRecord:
        return EnforcementClaimRecord(
            claim_id="guard-probe",
            fixture=fixture,
            entrypoint=_entrypoint_catches,
            source_fn="tests._guard_probe",
        )

    def test_non_temp_fixture_path_is_not_deleted(self) -> None:
        """The safety property: the runner leaves a path it did not create alone."""
        result = _run_single_claim(self._record(lambda: self.canary))

        self.assertTrue(
            self.canary.is_dir(), "the runner deleted a fixture path outside the temp root"
        )
        self.assertTrue(
            (self.canary / "keep" / "evidence.txt").is_file(), "the runner removed tree contents"
        )
        self.assertEqual(result.outcome, "TEST_BUG")

    def test_the_refusal_names_the_path_and_the_sanctioned_builder(self) -> None:
        """A refusal an author cannot act on will be worked around, not fixed."""
        result = _run_single_claim(self._record(lambda: self.canary))

        self.assertIn(str(self.canary), result.message)
        self.assertIn("_mkroot", result.message)

    def test_a_legitimate_temp_fixture_is_still_cleaned_up(self) -> None:
        """The guard must not turn the runner into a leaker.

        Cleanup is the behaviour the guard is narrowing, so the narrowing has to
        be shown not to have removed it.
        """
        created = Path(tempfile.mkdtemp(prefix="gzkit-qc-nc-guard-"))
        (created / "planted.txt").write_text("violation", encoding="utf-8")

        result = _run_single_claim(self._record(lambda: created))

        self.assertEqual(result.outcome, "PASS")
        self.assertFalse(created.exists(), "the runner stopped cleaning up real temp fixtures")


if __name__ == "__main__":
    unittest.main()
