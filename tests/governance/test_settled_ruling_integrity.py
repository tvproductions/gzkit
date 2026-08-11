"""A settled ruling must not reach the chain head clipped mid-sentence.

WHY: `_section_items` matched the bullet marker per LINE and kept only the
matched line, so any wrapped `Decisions Made` / `Settled Rulings` entry lost
everything after its first line. Fixed forward in `e84e6a85b` — and that fix is
FORWARD-ONLY. Nothing heals a clip already sitting in the chain, and nothing
notices one, so the residue propagates through `_carried_settled` into every
successor for as long as the chain runs.

Two properties make the residue worse than an ordinary stale line, both named in
the `_section_items` docstring: a ruling cut mid-sentence can INVERT its own
meaning (*"leave the"* reads as an instruction to leave something, not to leave
five advised steps unauthorized), and the fragment no longer dedups against its
untruncated twin under :func:`_ruling_key`, so both forms propagate side by side.

The assertion derives from that declared property — a carried ruling is the
operator's booked words and must arrive whole — not from a run of the composer.
It scans the newest RESUMABLE handoff because that is the document a resuming
session reads and the one a successor most likely chains from.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.handoff_api import parse_decisions, settled_rulings
from gzkit.handoff_resume_gate import newest_handoff

REPO_ROOT = Path(__file__).resolve().parents[2]
HANDOFFS = REPO_ROOT / ".gzkit" / "handoffs"


def _normalize(text: str) -> str:
    """Fold whitespace and case only — never anything that distinguishes rulings."""
    return " ".join(text.casefold().split())


def _corpus_bullets() -> list[tuple[str, str]]:
    """Every ruling-bearing bullet on disk, from both composition channels."""
    bullets: list[tuple[str, str]] = []
    for path in sorted(HANDOFFS.rglob("*.md")):
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        origin = path.relative_to(REPO_ROOT).as_posix()
        bullets.extend((entry, origin) for entry in settled_rulings(content))
        bullets.extend((decision.text, origin) for decision in parse_decisions(content))
    return bullets


class TestSettledRulingsReachTheHeadWhole(unittest.TestCase):
    """The chain head carries no ruling truncated away from a recoverable original."""

    def test_no_head_ruling_is_a_clipped_prefix_of_a_recoverable_fuller_form(self) -> None:
        head = newest_handoff(REPO_ROOT)
        self.assertIsNotNone(head, "no resumable handoff on disk to audit")
        assert head is not None

        rulings = settled_rulings(head.read_text(encoding="utf-8"))
        self.assertTrue(rulings, f"{head.name} carries no Settled Rulings to audit")
        carried = {_normalize(entry) for entry in rulings}

        corpus = [(_normalize(text), text, origin) for text, origin in _corpus_bullets()]

        clipped: list[str] = []
        for ruling in rulings:
            key = _normalize(ruling)
            fuller = [
                (norm, text, origin)
                for norm, text, origin in corpus
                if norm.startswith(key) and len(norm) > len(key)
            ]
            if not fuller:
                continue
            # ABRIDGED TWIN, not a clip: the fuller form is already carried in this
            # very document, so no operator words were lost on the way in. That is a
            # DEDUP condition `_ruling_key` deliberately declines to collapse —
            # folding two entries that merely look alike would drop a booked ruling
            # silently, which is the failure direction the channel exists to stop.
            # Narrow and named on purpose; it must never widen into a clip escape.
            if any(norm in carried for norm, _text, _origin in fuller):
                continue
            _norm, whole, origin = max(fuller, key=lambda item: len(item[0]))
            clipped.append(f"\n  CLIPPED: {ruling}\n  WHOLE  : {whole}\n  SOURCE : {origin}")

        self.assertEqual(
            [],
            clipped,
            f"{head.name} carries {len(clipped)} ruling(s) truncated away from a fuller form "
            f"still recoverable on disk. A clipped ruling can invert its own meaning and "
            f"never dedups against its untruncated twin, so it propagates down the chain "
            f"forever. Heal the head in place from the SOURCE text:{''.join(clipped)}",
        )


if __name__ == "__main__":
    unittest.main()
