"""A floor bookmark must not sink the settled-ruling corpus (commit 02ca03ee).

The exit beat writes a mechanical floor bookmark at every session end. By
construction it carries no ``## Settled Rulings`` and books no operator rulings
-- its own body says so: *"a mechanical floor bookmark written at the exit beat,
not an authored handoff -- it records where the session stopped, not what the
work meant."*

It is nonetheless a valid ``continues_from`` target, and ``_carried_settled``
read it as an ordinary ancestor. So a handoff chaining from a bookmark inherited
the bookmark's empty corpus and nothing else, and every ruling booked upstream
stopped arriving. Measured on the 2026-08-22 chain: the authored ancestor carried
**453** settled rulings, the bookmark between them carried 0, and the successor
carried 0.

That is the exact decay ``_carried_settled`` exists to prevent, arriving through
a document written by the machine rather than by an author:

    a ruling booked once keeps arriving, so it is never re-filed as an open
    loop and re-adjudicated

The discriminator is AUTHORSHIP, not ``mode`` -- :func:`is_floor_bookmark`, the
same predicate ``newest_handoff`` already uses to deprioritize bookmarks in
selection. An operator-authored ``CHECKPOINT`` is a real document whose rulings
must still be inherited; only the machine-written floor is transparent. Filtering
on ``mode`` would discard the authored one, which is the mistake
``handoff_resume_gate`` records having already avoided on the selection arm.

Transparency, never substitution: the bookmark stays in ``continues_from`` and
stays selectable. Only its contribution to the RULING chain is looked through.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.handoff_api import _carried_settled
from gzkit.handoff_selection import FLOOR_BOOKMARK_AGENT

RULING = "Never work an OBPI without running it through the gz-obpi-pipeline skill."
SECOND = "GHIs are AUTHORIZED for direct repair, always."


def _write(
    directory: Path,
    *,
    name: str,
    timestamp: str,
    agent: str = "test-agent",
    mode: str = "CREATE",
    continues_from: str | None = None,
    settled: list[str] | None = None,
) -> Path:
    """Write a minimal fixture handoff."""
    lines = [
        "---",
        f"mode: {mode}",
        "branch: main",
        f"timestamp: {timestamp}",
        f"agent: {agent}",
    ]
    if continues_from is not None:
        lines.append(f"continues_from: {continues_from}")
    lines.append("---")
    body = "\n".join(lines) + "\n\n## Immediate Next Steps\n\n1. Resume.\n"
    if settled:
        body += "\n## Settled Rulings\n\n" + "\n".join(f"- {s}" for s in settled) + "\n"
    path = directory / name
    path.write_text(body, encoding="utf-8", newline="\n")
    return path


class TestFloorBookmarkIsTransparentToTheRulingChain(unittest.TestCase):
    """Rulings survive a machine-written bookmark standing between two authored handoffs."""

    def test_rulings_survive_a_bookmark_that_declares_no_lineage(self) -> None:
        """The real shape: the exit beat writes no `continues_from` at all.

        This is the observed instance, not a constructed one -- the on-disk
        bookmark carries no lineage key, so there is no pointer to follow and the
        nearest authored ancestor has to be resolved by recency.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoffs = root / ".gzkit" / "handoffs"
            handoffs.mkdir(parents=True)

            _write(
                handoffs,
                name="20260822T094133Z-authored.md",
                timestamp="2026-08-22T09:41:33Z",
                settled=[RULING, SECOND],
            )
            _write(
                handoffs,
                name="20260822T104010Z-session-exit-bookmark.md",
                timestamp="2026-08-22T10:40:10Z",
                agent=FLOOR_BOOKMARK_AGENT,
                mode="CHECKPOINT",
            )

            carried = _carried_settled(
                "20260822T104010Z-session-exit-bookmark.md",
                root,
            )

            self.assertIn(
                RULING,
                carried,
                "a machine-written bookmark must be transparent to the ruling chain; "
                "inheriting its empty corpus drops every ruling booked upstream (commit 02ca03ee)",
            )
            self.assertIn(SECOND, carried, "every upstream ruling survives, not merely the first")

    def test_an_authored_checkpoint_is_not_looked_through(self) -> None:
        """The control, and the reason the predicate is authorship rather than mode.

        An operator-authored CHECKPOINT is a real document. Looking through it
        would skip a genuine ancestor and inherit some older handoff's corpus
        instead -- silently substituting one lineage for another, which is worse
        than the bug being fixed.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoffs = root / ".gzkit" / "handoffs"
            handoffs.mkdir(parents=True)

            _write(
                handoffs,
                name="20260822T094133Z-older.md",
                timestamp="2026-08-22T09:41:33Z",
                settled=["An older ruling that must NOT be reached through the checkpoint."],
            )
            _write(
                handoffs,
                name="20260822T104010Z-authored-checkpoint.md",
                timestamp="2026-08-22T10:40:10Z",
                agent="claude-code",
                mode="CHECKPOINT",
                settled=[RULING],
            )

            carried = _carried_settled("20260822T104010Z-authored-checkpoint.md", root)

            self.assertEqual(
                [RULING],
                carried,
                "an authored CHECKPOINT contributes its own rulings and is not looked "
                "through; only the machine-written floor bookmark is transparent",
            )

    def test_a_bookmark_with_no_authored_ancestor_inherits_nothing(self) -> None:
        """A bookmark at the root of the corpus is a genuine chain root.

        Looking through it must not invent lineage where none exists -- an empty
        result is the honest answer, and must not raise.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoffs = root / ".gzkit" / "handoffs"
            handoffs.mkdir(parents=True)

            _write(
                handoffs,
                name="20260822T104010Z-session-exit-bookmark.md",
                timestamp="2026-08-22T10:40:10Z",
                agent=FLOOR_BOOKMARK_AGENT,
                mode="CHECKPOINT",
            )

            carried = _carried_settled("20260822T104010Z-session-exit-bookmark.md", root)
            self.assertEqual([], carried)


if __name__ == "__main__":
    unittest.main()
