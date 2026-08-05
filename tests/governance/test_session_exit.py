"""Tests for the session-exit floor bookmark (GHI #756).

`gz handoff create` shipped under ADR-0.0.65 and nothing called it: continuity
depended on an agent remembering to author a handoff. These assertions derive
from the GHI's declared constraints — the beat must WRITE rather than refuse,
must never block, and must never produce an artifact that could discharge a
token surrender the session did not perform.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.handoff_validation import (
    find_handoff_for_release,
    parse_frontmatter,
    validate_handoff_document,
)
from gzkit.session_exit import book_exit_bookmark


class SessionExitBookmarkTests(unittest.TestCase):
    """The exit edge books; it never refuses (GHI #756).

    The fail-closed energy sat entirely on the entry edge: resume blocked hard
    while exit had no trigger at all. The airlock solved the same asymmetry by
    BOOKING (`_book_aborted_exit`, GHI #679) rather than REFUSING, and the
    operator ruled the handoff must copy it: "DO NOT BLOCK HERE. Observe,
    contextualize, update status, develop suggestions, pose questions, write
    them all to the handoff bookmark, and leave."
    """

    def _root(self) -> Path:
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        (root / ".gzkit" / "handoffs").mkdir(parents=True)
        return root

    def test_exit_writes_a_bookmark(self) -> None:
        root = self._root()
        result = book_exit_bookmark(root, session_id="s-1", exit_reason="clear")

        self.assertTrue(result.written, f"expected a bookmark; got {result.detail!r}")
        self.assertIsNotNone(result.path)

    def test_the_bookmark_is_checkpoint_mode(self) -> None:
        """A machine firing on exit cannot know the operator is finished.

        `CREATE` would mean "departure notice", and a departure notice
        postdating a lock claim satisfies token-block § Sub-Invariant 5. An
        automatic writer emitting those would let any session's lock be
        released on the evidence of an artifact nobody authored.
        """
        root = self._root()
        result = book_exit_bookmark(root, session_id="s-1", exit_reason="exit")

        assert result.path is not None
        frontmatter = parse_frontmatter(Path(result.path).read_text(encoding="utf-8"))
        assert isinstance(frontmatter, dict)
        self.assertEqual(frontmatter["mode"], "CHECKPOINT")

    def test_the_bookmark_cannot_surrender_a_token(self) -> None:
        """The coupling that makes the automatic writer safe to run at all."""
        root = self._root()
        book_exit_bookmark(
            root,
            session_id="s-1",
            exit_reason="clear",
            obpi_id="OBPI-0.25.0-32",
        )

        self.assertIsNone(
            find_handoff_for_release(
                root,
                obpi_id="OBPI-0.25.0-32",
                after_timestamp="2000-01-01T00:00:00Z",
            ),
            "an auto-written exit bookmark must never discharge a lock release",
        )

    def test_the_bookmark_passes_the_authoring_gate(self) -> None:
        """A mechanically-written handoff is held to the same bar as an authored one.

        `create_handoff` refuses an invalid document, so a producer that drafted
        a hollow bookmark would silently write nothing. Asserting validity here
        makes that a failing test rather than a silent absence (GHI #692's
        shape, arriving through a mechanical producer).
        """
        root = self._root()
        result = book_exit_bookmark(root, session_id="s-1", exit_reason="clear")

        assert result.path is not None
        content = Path(result.path).read_text(encoding="utf-8")
        self.assertEqual(validate_handoff_document(content, root), [])

    def test_exit_reason_and_session_are_recorded(self) -> None:
        root = self._root()
        result = book_exit_bookmark(root, session_id="s-42", exit_reason="clear")

        assert result.path is not None
        content = Path(result.path).read_text(encoding="utf-8")
        frontmatter = parse_frontmatter(content)
        assert isinstance(frontmatter, dict)
        self.assertEqual(frontmatter["session_id"], "s-42")
        self.assertIn("clear", content, "the exit reason is part of the state being preserved")

    def test_a_write_failure_is_reported_never_raised(self) -> None:
        """The beat must not block, and an exception at exit IS a block.

        `SessionEnd` cannot block by platform contract, but the gz-side function
        is the reusable surface — a raising producer would take down any caller
        that is not a hook. Booking-not-refusing is enforced here, not left to
        the adapter's try/except.
        """
        root = self._root()
        with patch(
            "gzkit.session_exit.create_handoff",
            side_effect=OSError("disk gone"),
        ):
            result = book_exit_bookmark(root, session_id="s-1", exit_reason="clear")

        self.assertFalse(result.written)
        self.assertIsNone(result.path)
        self.assertIn("disk gone", result.detail)


class SessionEndIsShippedToAdoptersTests(unittest.TestCase):
    """A hook gzkit does not own ships to nobody (GHI #756).

    `SessionStart` was hand-wired in this repo's own `.claude/settings.json` and
    absent from `gzkit_owned_phases`, so the orientation an adopter would need
    reached only the repo that authored it. Registering the phase is what turns
    a local convenience into a delivered surface; a hook script that exists but
    is unowned is the same defect as a verb with no trigger.
    """

    def test_session_end_is_a_gzkit_owned_phase(self) -> None:
        from gzkit.hooks.claude import gzkit_owned_phases

        self.assertIn("SessionEnd", gzkit_owned_phases())

    def test_session_end_is_wired_in_generated_settings(self) -> None:
        from gzkit.config import GzkitConfig
        from gzkit.hooks.claude import generate_claude_settings

        phase = generate_claude_settings(GzkitConfig()).get("hooks", {}).get("SessionEnd", [])
        commands = [hook.get("command", "") for group in phase for hook in group.get("hooks", [])]
        self.assertTrue(
            any("session-exit-bookmark.py" in command for command in commands),
            f"SessionEnd must invoke the bookmark hook; got {commands}",
        )

    def test_an_existing_unowned_phase_still_passes_through(self) -> None:
        """The negative pole: owning a phase must not evict a user's own hooks."""
        from gzkit.hooks.claude import gzkit_owned_phases

        self.assertNotIn("PreCompact", gzkit_owned_phases())


if __name__ == "__main__":
    unittest.main()
