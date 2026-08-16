"""The knowledge bundle's active-campaign source follows supersession.

``TRACER_SLICE`` names the campaign plan by path. That path was **hardcoded** to
``build-to-1.0-campaign-2026-06-30.md`` and stayed there through two
supersessions — 06-30 → 07-18 → 08-16 — so ``gz knowledge`` generated an
"Active Campaign" concept page sourced from a plan that had not steered since
2026-07-18, and the generated artifact under ``.gzkit/governance/knowledge/``
disagreed with the generator that wrote it.

Nothing coupled the constant to the thing that actually decides which plan is
active. `scripts/session_orientation.py` already resolves it correctly —
``Status: **ACTIVE`` is the discriminator, supersession flips it, and Operating
Rule 1 guarantees at most one match — but that logic lived in a boot script no
package module could reach, so the generator carried its own stale copy.

This is the same shape the campaign's own § Movement C family names: a declared
relationship ("the bundle ships the active campaign") with no mechanical witness,
decaying silently because a hardcoded path cannot report that it is wrong.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.knowledge.generate import (
    _ACTIVE_STATUS_RE,
    TRACER_SLICE,
    resolve_active_campaign,
)

# Imported rather than redeclared. A third copy of the discriminator would put
# this test in the position of agreeing with a production reader by coincidence,
# and it has nothing to add: pattern agreement between the two production copies
# is witnessed by
# `tests/scripts/test_active_status_pattern_single_sourced.py`, which also pins
# what the pattern must decide. What this file uniquely asserts is the SELECTION
# rule built on top of it.
_CAMPAIGN_GLOB = "*-campaign-*.md"


def _active_campaign_on_disk() -> Path:
    """The one campaign plan whose Status line declares it ACTIVE."""
    matches = [
        path
        for path in sorted(Path("docs/governance").glob(_CAMPAIGN_GLOB))
        if _ACTIVE_STATUS_RE.search(path.read_text(encoding="utf-8", errors="replace"))
    ]
    if len(matches) != 1:  # pragma: no cover - Operating Rule 1 violation
        raise AssertionError(f"expected exactly one ACTIVE campaign, found {len(matches)}")
    return matches[0]


class TestActiveCampaignResolution(unittest.TestCase):
    """The bundle sources the ACTIVE plan, not a plan that was active once."""

    def test_tracer_slice_names_the_active_campaign(self) -> None:
        entries = dict(TRACER_SLICE)
        self.assertIn("active-campaign", entries)
        self.assertEqual(
            entries["active-campaign"],
            _active_campaign_on_disk(),
            "the knowledge bundle's active-campaign source does not follow "
            "supersession — it names a plan that no longer steers, so "
            "`gz knowledge` ships a superseded campaign as canon",
        )


class TestResolverSelection(unittest.TestCase):
    """The resolver's decision logic, exercised without the live corpus.

    `gz validate --tautological-test-audit` refused this class's first form,
    which asserted that each tracer source ``is_file()``. It was right: file
    existence is content, not behavior (`.gzkit/rules/tests.md` § The
    discriminator — *if the production code's behavior changed but its text did
    not, would this test fail?*). These exercise the selection rule instead, on
    a temp corpus, so they fail when the rule changes rather than when the
    repository does.
    """

    def _corpus(self, root: Path, **editions: str) -> None:
        for name, status in editions.items():
            (root / f"build-to-1.0-campaign-{name}.md").write_text(
                f"# Campaign {name}\n\nStatus: **{status}**\n", encoding="utf-8"
            )

    def test_status_decides_not_filename_date(self) -> None:
        """An older edition marked ACTIVE beats a newer one that is superseded."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._corpus(root, **{"2026-01-01": "ACTIVE — the one canonical plan"})
            self._corpus(root, **{"2026-09-09": "SUPERSEDED"})
            self.assertEqual(
                resolve_active_campaign(root).name,
                "build-to-1.0-campaign-2026-01-01.md",
            )

    def test_falls_back_to_newest_when_none_declares_active(self) -> None:
        """A governance-state anomaly must not fail bundle generation closed."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._corpus(root, **{"2026-01-01": "SUPERSEDED", "2026-09-09": "SUPERSEDED"})
            self.assertEqual(
                resolve_active_campaign(root).name,
                "build-to-1.0-campaign-2026-09-09.md",
            )
