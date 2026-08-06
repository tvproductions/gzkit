"""Tests for the session-exit floor bookmark (GHI #756).

`gz handoff create` shipped under ADR-0.0.65 and nothing called it: continuity
depended on an agent remembering to author a handoff. These assertions derive
from the GHI's declared constraints — the beat must WRITE rather than refuse,
must never block, and must never produce an artifact that could discharge a
token surrender the session did not perform.
"""

from __future__ import annotations

import subprocess
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


class TestExitBeatIsIntentionalAboutBookmarks(unittest.TestCase):
    """The bookmark is a safety valve; it should not fire when there is nothing
    to relieve (operator ruling 2026-08-05).

    Emitting one at every session end made the artifact carry no information: a
    bookmark's PRESENCE should mean something was unfinished. The skip predicate
    is "provably nothing has happened since the authored handoff was written",
    not "the handoff looks recent" — age measures when a document was written,
    never whether it still describes reality.
    """

    def _repo(self, tmp: str) -> Path:
        root = Path(tmp)
        (root / ".gzkit" / "handoffs").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for key, val in (("user.email", "t@e.com"), ("user.name", "t")):
            subprocess.run(["git", "-C", str(root), "config", key, val], check=True)
        return root

    def _commit(self, root: Path, message: str) -> None:
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-qm", message], check=True)

    def _authored(self, root: Path, name: str = "20260101T000000Z-real.md") -> Path:
        path = root / ".gzkit" / "handoffs" / name
        path.write_text(
            "---\nmode: CREATE\nadr_id: ADR-0.0.65\nbranch: main\n"
            "timestamp: '2026-01-01T00:00:00Z'\nagent: claude-code\n---\n\n"
            "## Decisions Made\n\n- [agent-chose] body\n",
            encoding="utf-8",
        )
        return path

    def test_skips_when_an_authored_handoff_covers_a_clean_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self._authored(root)
            self._commit(root, "land handoff")
            result = book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            self.assertFalse(result.written)
            self.assertTrue(result.skipped, "a deliberate no-op must not read as a failure")

    def test_the_skip_is_recorded_on_the_ledger_not_silent(self):
        """A silent skip is indistinguishable from a crashed hook — the exact
        does-it-fire ambiguity GHI #756 was filed to close."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self._authored(root)
            self._commit(root, "land handoff")
            book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            ledger = (root / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("session_exit_bookmark_skipped", ledger)
            self.assertIn("20260101T000000Z-real.md", ledger)

    def test_books_when_work_landed_after_the_handoff(self):
        """The hole a freshness test would leave: a recent handoff, then real work,
        all committed. The handoff is young and no longer describes reality."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self._authored(root)
            self._commit(root, "land handoff")
            (root / "src.py").write_text("x = 1\n", encoding="utf-8")
            self._commit(root, "work after the handoff")
            result = book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            self.assertTrue(result.written)

    def test_books_when_the_tree_is_dirty(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self._authored(root)
            self._commit(root, "land handoff")
            (root / "wip.py").write_text("unfinished\n", encoding="utf-8")
            result = book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            self.assertTrue(result.written)

    def test_books_when_the_authored_handoff_is_untracked(self):
        """Staged or committed counts as durable; untracked does not survive the tree."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "seed.txt").write_text("x\n", encoding="utf-8")
            self._commit(root, "seed")
            self._authored(root)  # written, never added
            result = book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            self.assertTrue(result.written)

    def test_books_when_only_floor_bookmarks_exist(self):
        """No authored handoff means nothing covers the session, whatever else is true."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "seed.txt").write_text("x\n", encoding="utf-8")
            self._commit(root, "seed")
            first = book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            self.assertTrue(first.written)
            self._commit(root, "land bookmark")
            second = book_exit_bookmark(root, session_id="s2", exit_reason="clear")
            self.assertTrue(second.written, "a floor bookmark must not cover the next session")

    def test_a_staged_bookmark_does_not_block_the_next_skip(self):
        """The two operator rulings cancel out without the handoffs-dir exclusion.

        Staging makes `git status --porcelain` report the bookmark, so an unscoped
        cleanliness test would read the PREVIOUS session's bookmark as a dirty
        tree, refuse to skip, and write another — each bookmark guaranteeing the
        next, forever, with nothing failing loudly.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            self._authored(root)
            self._commit(root, "land handoff")
            stray = root / ".gzkit" / "handoffs" / "20260102T000000Z-session-exit-bookmark.md"
            stray.write_text(
                "---\nmode: CHECKPOINT\nadr_id: null\nbranch: main\n"
                "timestamp: '2026-01-02T00:00:00Z'\nagent: gzkit-session-exit\n---\n\n"
                "## Decisions Made\n\n- [agent-chose] floor\n",
                encoding="utf-8",
            )
            subprocess.run(["git", "-C", str(root), "add", "--", str(stray)], check=True)
            result = book_exit_bookmark(root, session_id="s2", exit_reason="clear")
            self.assertTrue(result.skipped, "a staged bookmark must not count as a dirty tree")

    def test_a_written_bookmark_is_staged(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "seed.txt").write_text("x\n", encoding="utf-8")
            self._commit(root, "seed")
            result = book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            self.assertTrue(result.written)
            self.assertTrue(result.staged)
            staged = subprocess.run(
                ["git", "-C", str(root), "diff", "--cached", "--name-only"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            ).stdout
            self.assertIn("session-exit-bookmark", staged)

    def test_a_staged_bookmark_rides_the_next_commit(self):
        """The property staging buys: `git commit` commits the INDEX, so the
        referent can no longer land after the ledger event that cites it."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "seed.txt").write_text("x\n", encoding="utf-8")
            self._commit(root, "seed")
            book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            (root / "later.py").write_text("y = 2\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "--", "later.py"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "unrelated"], check=True)
            tree = subprocess.run(
                ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "HEAD"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            ).stdout
            self.assertIn("session-exit-bookmark", tree)

    def test_no_git_still_books_rather_than_skipping(self):
        """Fail toward writing: a spurious bookmark is noise, a missing one is
        lost context, and this surface exists to prevent the second."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit" / "handoffs").mkdir(parents=True)
            self._authored(root)
            result = book_exit_bookmark(root, session_id="s1", exit_reason="clear")
            self.assertTrue(result.written)
