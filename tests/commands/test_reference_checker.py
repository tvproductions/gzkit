"""BEHAVIOR tests for the ``gh`` adapter behind the ``ReferenceChecker`` port.

The adapter reads ONE repository — the project root it is built for. A citation
that names another repository is outside what it can answer, and answering it
from the local repository is worse than not answering: the number resolves, so
the wrong verdict arrives wearing the same confidence as a right one.

Observed instance (2026-09-21): a handoff advised "Rule on gz-skills#1". That
issue is OPEN in ``tvproductions/gz-skills``; ``tvproductions/gzkit`` issue 1 is
a closed Gate-5 attestation from the project's first week. The adapter resolved
the local one and the annotator stamped the step ``gz-skills#1 [settled]``.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.reference_checker import live_reference_checker
from gzkit.handoff_api import ReferenceKind, ReferenceState, StepReference


class TestForeignRepositoryReferencesAreNotResolvedLocally(unittest.TestCase):
    """A citation naming another repository resolves UNKNOWN, unread."""

    def setUp(self) -> None:
        self._root = tempfile.TemporaryDirectory()
        self.addCleanup(self._root.cleanup)
        self.root = Path(self._root.name)
        self.calls: list[str] = []
        patcher = mock.patch(
            "gzkit.commands.reference_checker.gh_issue_state",
            side_effect=self._record,
        )
        self.gh = patcher.start()
        self.addCleanup(patcher.stop)

    def _record(self, number: str, _root: Path) -> ReferenceState:
        self.calls.append(number)
        return ReferenceState.SETTLED

    def test_foreign_citation_is_never_asked_of_the_local_repository(self) -> None:
        check = live_reference_checker(self.root)

        state = check(StepReference(kind=ReferenceKind.GHI, identifier="1", repo="gz-skills"))

        self.assertEqual(state, ReferenceState.UNKNOWN)
        self.assertEqual(
            self.calls,
            [],
            "the local repository was read for another repository's issue number",
        )

    def test_local_citation_is_still_resolved(self) -> None:
        check = live_reference_checker(self.root)

        state = check(StepReference(kind=ReferenceKind.GHI, identifier="1069"))

        self.assertEqual(state, ReferenceState.SETTLED)
        self.assertEqual(self.calls, ["1069"])

    def test_a_foreign_citation_does_not_latch_the_adapter_off(self) -> None:
        """Refusing to answer is not a failure — the next local citation still resolves.

        The adapter latches off after an UNKNOWN from ``gh`` so an offline run
        costs one failed call. A foreign reference never reaches ``gh``, so it
        must not consume that latch and blind every citation after it.
        """
        check = live_reference_checker(self.root)

        check(StepReference(kind=ReferenceKind.GHI, identifier="4", repo="owner/other"))
        state = check(StepReference(kind=ReferenceKind.GHI, identifier="1069"))

        self.assertEqual(state, ReferenceState.SETTLED)
        self.assertEqual(self.calls, ["1069"])

    def test_same_number_in_two_repositories_does_not_share_one_verdict(self) -> None:
        """The memo is keyed per citation, so a local answer cannot leak abroad."""
        check = live_reference_checker(self.root)

        local = check(StepReference(kind=ReferenceKind.GHI, identifier="1"))
        foreign = check(StepReference(kind=ReferenceKind.GHI, identifier="1", repo="gz-skills"))

        self.assertEqual(local, ReferenceState.SETTLED)
        self.assertEqual(foreign, ReferenceState.UNKNOWN)


if __name__ == "__main__":
    unittest.main()
