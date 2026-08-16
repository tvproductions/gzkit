"""The ACTIVE-campaign discriminator must have one spelling across its readers.

Two production readers decide which campaign plan governs, and they cannot share
an implementation. `scripts/session_orientation.py` is contracted to run on
stdlib alone -- its module docstring says "no gzkit import" -- so that the
digest still names the governing plan when the package itself is broken;
`collect_campaign` is deliberately filesystem-only, with every subprocess call
quarantined in `collect_live_adr_counts`. Meanwhile the wheel ships
`src/gzkit/**` and never `scripts/`. The two readers therefore sit on opposite
sides of the distribution boundary, and neither can import the other.

So the pattern is duplicated by construction, and this is the witness that keeps
the duplication honest -- the same shape
`test_task_envelope_coherence.TestTaskGrammarSingleSourced` uses for the TASK
grammar, and `test_brief_structure` uses for the pydantic/JSON-schema readers.

It is NOT a substitute for one implementation. It cannot stop the copies from
diverging; it can only stop them from diverging *silently*, which is the whole
of what the boundary permits. The class this guards is live rather than
theoretical: the `gzkit` copy was written in a session diagnosing a stale
hardcoded campaign pointer, without noticing the boot script already carried
one.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from gzkit.knowledge.generate import _ACTIVE_STATUS_RE as _PACKAGE_RE

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_orientation.py"


def _load_orientation_module():
    """Load the boot script by path -- it is not importable as a package."""
    spec = importlib.util.spec_from_file_location("session_orientation", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load {SCRIPT_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_orientation"] = module
    spec.loader.exec_module(module)
    return module


class ActiveStatusPatternAgreesAcrossReaders(unittest.TestCase):
    """Both readers must recognise exactly the same set of Status lines."""

    def test_the_two_production_copies_are_character_identical(self) -> None:
        """Divergence here splits which plan each surface thinks governs.

        The failure is not a crash. Both readers keep working and quietly
        disagree, so the orientation digest and the knowledge bundle can name
        different campaigns while each is internally consistent -- which is
        exactly how the bundle came to ship a plan superseded two editions
        earlier.
        """
        script_re = _load_orientation_module()._ACTIVE_STATUS_RE
        self.assertEqual(script_re.pattern, _PACKAGE_RE.pattern)

    def test_the_two_production_copies_share_their_flags(self) -> None:
        """`re.MULTILINE` is load-bearing, and equal patterns can differ in it.

        Without MULTILINE, `^` anchors to the start of the document, so a
        `Status:` line further down never matches and every campaign reads as
        superseded. Comparing pattern text alone would wave that through.
        """
        script_re = _load_orientation_module()._ACTIVE_STATUS_RE
        self.assertEqual(script_re.flags, _PACKAGE_RE.flags)


class TheSharedPatternDecidesWhatItClaimsTo(unittest.TestCase):
    """Agreement is worthless if both copies agree on the wrong thing.

    These pin the discriminator's actual contract, so the witness above cannot
    be satisfied by two identically-broken readers.
    """

    _ACTIVE = "# Plan\n\nStatus: **ACTIVE — the one canonical plan**\n"
    _SUPERSEDED = "# Plan\n\nStatus: **SUPERSEDED by the 2026-08-16 edition**\n"

    def test_an_active_status_line_matches(self) -> None:
        for name, pattern in (("script", None), ("package", _PACKAGE_RE)):
            regex = pattern or _load_orientation_module()._ACTIVE_STATUS_RE
            with self.subTest(reader=name):
                self.assertIsNotNone(regex.search(self._ACTIVE))

    def test_a_superseded_status_line_does_not_match(self) -> None:
        """Supersession is the flip; a plan that lost ACTIVE must stop matching."""
        for name, pattern in (("script", None), ("package", _PACKAGE_RE)):
            regex = pattern or _load_orientation_module()._ACTIVE_STATUS_RE
            with self.subTest(reader=name):
                self.assertIsNone(regex.search(self._SUPERSEDED))

    def test_the_status_line_is_matched_below_the_first_line(self) -> None:
        """The MULTILINE dependency, asserted through behavior rather than flags."""
        for name, pattern in (("script", None), ("package", _PACKAGE_RE)):
            regex = pattern or _load_orientation_module()._ACTIVE_STATUS_RE
            with self.subTest(reader=name):
                self.assertIsNotNone(regex.search("# Title\n\n\n\nStatus: **ACTIVE**\n"))

    def test_a_status_mention_mid_line_does_not_match(self) -> None:
        """`^` is load-bearing: prose about the status is not the status."""
        prose = "# Plan\n\nThe old edition had Status: **ACTIVE** until it was flipped.\n"
        for name, pattern in (("script", None), ("package", _PACKAGE_RE)):
            regex = pattern or _load_orientation_module()._ACTIVE_STATUS_RE
            with self.subTest(reader=name):
                self.assertIsNone(regex.search(prose))


if __name__ == "__main__":
    unittest.main()
