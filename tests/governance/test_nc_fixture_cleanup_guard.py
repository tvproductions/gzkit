"""The NC runner removes only the private workspace it created (GHI #920).

The vulnerable runner ended with ``shutil.rmtree(fixture_path, ignore_errors=True)``
on whatever ``Path`` a registered fixture returned. The first repair admitted any
path beneath the system temp root, which still confused location with ownership:
another process's temp directory remained a valid cleanup target.

Measured 2026-08-29: a fixture written as `return REPO` (the repository root,
handed over because the entrypoint needed *some* real directory) caused
`python -m unittest` to delete the working repository. The authoring mistake was
real; converting it into data loss was a separate defect, and this is that one.

The fixed runner creates a private ``TemporaryDirectory`` for each claim and exposes
that parent only while the fixture builder runs. Fixture paths must be allocated
through ``create_fixture_tempdir`` beneath that parent. Most importantly, the path
returned by fixture code is never used as cleanup authority: only the runner-owned
workspace handle is cleaned.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.enforcement import EnforcementClaimRecord, _run_single_claim, create_fixture_tempdir


def _entrypoint_catches(_root: Path) -> int:
    return 1


class TestFixtureCleanupGuard(unittest.TestCase):
    """A path the runner did not create is a reported TEST_BUG, not a deletion."""

    def _record(self, fixture) -> EnforcementClaimRecord:
        return EnforcementClaimRecord(
            claim_id="guard-probe",
            fixture=fixture,
            entrypoint=_entrypoint_catches,
            source_fn="tests._guard_probe",
        )

    def test_non_temp_fixture_path_is_not_deleted(self) -> None:
        """The safety property: the runner leaves a path it did not create alone."""
        with tempfile.TemporaryDirectory(prefix=".gzkit-foreign-owner-", dir=Path.cwd()) as tmp:
            canary = Path(tmp)
            evidence = canary / "owned-by-another-caller.txt"
            evidence.write_text("do not delete", encoding="utf-8")

            result = _run_single_claim(self._record(lambda: canary))

            self.assertTrue(evidence.is_file(), "the runner deleted a path it did not create")
            self.assertEqual(result.outcome, "TEST_BUG")

    def test_foreign_temp_fixture_path_is_not_deleted(self) -> None:
        """Temp-root containment does not grant the runner deletion authority."""
        with tempfile.TemporaryDirectory(prefix="gzkit-foreign-owner-") as tmp:
            foreign = Path(tmp)
            evidence = foreign / "owned-by-another-caller.txt"
            evidence.write_text("do not delete", encoding="utf-8")

            result = _run_single_claim(self._record(lambda: foreign))

            self.assertTrue(evidence.is_file(), "the runner deleted a temp path it did not create")
            self.assertEqual(result.outcome, "TEST_BUG")

    def test_the_refusal_names_the_path_and_the_sanctioned_builder(self) -> None:
        """A refusal an author cannot act on will be worked around, not fixed."""
        with tempfile.TemporaryDirectory(prefix=".gzkit-foreign-owner-", dir=Path.cwd()) as tmp:
            canary = Path(tmp)

            result = _run_single_claim(self._record(lambda: canary))

            self.assertIn(str(canary), result.message)
            self.assertIn("create_fixture_tempdir", result.message)

    def test_a_legitimate_temp_fixture_is_still_cleaned_up(self) -> None:
        """The guard must not turn the runner into a leaker.

        Cleanup is the behaviour the guard is narrowing, so the narrowing has to
        be shown not to have removed it.
        """
        created: list[Path] = []

        def fixture() -> Path:
            root = create_fixture_tempdir(prefix="gzkit-qc-nc-guard-")
            created.append(root)
            (root / "planted.txt").write_text("violation", encoding="utf-8")
            return root

        result = _run_single_claim(self._record(fixture))

        self.assertEqual(result.outcome, "PASS")
        self.assertEqual(len(created), 1)
        self.assertFalse(created[0].exists(), "the runner stopped cleaning up its fixture")


if __name__ == "__main__":
    unittest.main()
