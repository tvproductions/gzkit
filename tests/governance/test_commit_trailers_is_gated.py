"""The commit-trailer obligation is reached by a gate, not only by hand (GHI #1017).

``.claude/rules/task-discovery.md`` § Invariant makes a ``Task:`` trailer
mandatory on any commit touching ``src/**`` or ``tests/**``. Three surfaces
name ``gz validate --commit-trailers`` as the enforcement, and the stamping
hook is deliberately silent *because* it trusts that downstream catch:

    Every failure path is a silent no-op. This runs on every commit; a hook
    that raises blocks all work, and a missing trailer is caught downstream by
    `gz validate --commit-trailers` anyway.
    -- .gzkit/hooks/prepare-commit-msg-task-trailers

It was not caught downstream. The scope was registered ``"explicit"``, so the
no-flag ``gz check`` never reached it, and two non-compliant commits reached
``origin`` with every gate green (2026-09-17, and ``84ea8e435`` on 2026-09-20).
Both were found by running the validator by hand while checking something else.

Pre-commit cannot host this check: the validator scans HEAD, which at
pre-commit time is still the previous commit. ``gz check`` runs at pre-push,
where HEAD exists and the commit is still amendable, so that is the moment the
obligation can actually bind.
"""

from __future__ import annotations

import unittest

from gzkit.commands.validate_cmd import VALIDATOR_REGISTRY


class CommitTrailersGatedTests(unittest.TestCase):
    """The scope must sit in the tier the no-flag gate actually runs."""

    def _entry(self, stem: str):
        for entry in VALIDATOR_REGISTRY:
            if entry.stem == stem:
                return entry
        self.fail(f"{stem} is not registered in VALIDATOR_REGISTRY")

    def test_commit_trailers_is_in_the_default_tier(self) -> None:
        """An 'explicit' tier means gz check never reaches it, which was the defect."""
        self.assertEqual(
            self._entry("commit_trailers").tier,
            "default",
            "commit_trailers must run under the no-flag gz check; registering it "
            "'explicit' is what let two non-compliant commits reach origin green.",
        )

    def test_the_scope_is_still_registered_and_runnable(self) -> None:
        """Guards against 'fixing' the tier by deleting the scope."""
        entry = self._entry("commit_trailers")
        self.assertTrue(callable(entry.run))
        self.assertTrue(entry.in_other_scopes)


if __name__ == "__main__":
    unittest.main()
