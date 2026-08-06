"""The two handoff SELECTION readers must not drift apart (GHI #758).

WHY: three independent readers select over `.gzkit/handoffs/`, and the same
displacement bug was fixed in each of them separately — the release arm under
GHI #756, the resume gate and the orientation script under GHI #758. Nothing
coupled them, so each fix had to be rediscovered. The operator ruled that the
residual be closed rather than recorded as a note.

These assertions derive from the declared rule in `gzkit.handoff_selection`
(authored above floor, recency within class, deprioritize never drop), not from
either implementation — so a change to one reader that silently diverges from the
other fails here rather than in a future session's orientation.
"""

from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

from gzkit.handoff_resume_gate import newest_handoff
from gzkit.handoff_selection import FLOOR_BOOKMARK_AGENT, is_floor_bookmark, selection_rank

REPO_ROOT = Path(__file__).resolve().parents[2]
ORIENTATION = REPO_ROOT / "scripts" / "session_orientation.py"


def _load_orientation():
    spec = importlib.util.spec_from_file_location("session_orientation_sel", ORIENTATION)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_orientation_sel"] = module
    spec.loader.exec_module(module)
    return module


def _write(root: Path, name: str, ts: datetime, agent: str) -> Path:
    handoffs = root / ".gzkit" / "handoffs"
    handoffs.mkdir(parents=True, exist_ok=True)
    path = handoffs / name
    path.write_text(
        f"---\nmode: CHECKPOINT\nadr_id: ADR-0.0.65\nbranch: main\n"
        f"timestamp: '{ts.isoformat().replace('+00:00', 'Z')}'\nagent: {agent}\n---\n\n"
        f"## Decisions Made\n\n- [agent-chose] body\n",
        encoding="utf-8",
    )
    return path


class TestSelectionRankIsTheDeclaredRule(unittest.TestCase):
    def test_authored_outranks_floor_regardless_of_recency(self) -> None:
        older_authored = selection_rank("claude-code", "2026-01-01T00:00:00Z")
        newer_floor = selection_rank(FLOOR_BOOKMARK_AGENT, "2026-12-31T00:00:00Z")
        self.assertGreater(older_authored, newer_floor)

    def test_recency_orders_within_a_class_not_across_it(self) -> None:
        self.assertGreater(
            selection_rank(FLOOR_BOOKMARK_AGENT, "2026-02-01T00:00:00Z"),
            selection_rank(FLOOR_BOOKMARK_AGENT, "2026-01-01T00:00:00Z"),
        )
        self.assertGreater(
            selection_rank("claude-code", "2026-02-01T00:00:00Z"),
            selection_rank("claude-code", "2026-01-01T00:00:00Z"),
        )

    def test_an_absent_agent_is_not_a_floor_bookmark(self) -> None:
        """Fail toward AUTHORED on unknown authorship.

        The whole corpus predating the `agent` field would otherwise be demoted
        below every bookmark — a filter meant to surface authored work burying
        all of it. Unknown means "not provably mechanical", not "mechanical".
        """
        self.assertFalse(is_floor_bookmark(None))
        self.assertFalse(is_floor_bookmark(""))


class TestBothSelectionReadersAgree(unittest.TestCase):
    """The differential: same corpus in, same document out.

    This is the assertion the shared constant cannot make. The two readers have
    genuinely different iteration shapes — early exit over a pre-sorted list on a
    hot path, versus `max()` over parsed tuples — so they are two implementations
    of one rule by necessity. Only a differential holds them together.
    """

    def setUp(self) -> None:
        self.orientation = _load_orientation()
        self.now = datetime(2026, 4, 25, 12, 0, 0, tzinfo=UTC)

    def _agree_on(self, root: Path) -> None:
        gate_pick = newest_handoff(root)
        orientation_pick = self.orientation.collect_handoff(root, self.now)
        if gate_pick is None:
            self.assertIsNone(orientation_pick)
            return
        assert orientation_pick is not None
        self.assertEqual(
            Path(gate_pick).name,
            Path(str(orientation_pick["path"])).name,
            "the resume gate and session orientation selected different handoffs",
        )

    def test_agree_when_a_newer_floor_shadows_an_authored_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root, "20260425T100000Z-authored.md", self.now - timedelta(hours=2), "claude-code"
            )
            _write(
                root,
                "20260425T115900Z-session-exit-bookmark.md",
                self.now - timedelta(minutes=1),
                FLOOR_BOOKMARK_AGENT,
            )
            self._agree_on(root)

    def test_agree_when_only_floor_bookmarks_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(
                root,
                "20260425T100000Z-session-exit-bookmark.md",
                self.now - timedelta(hours=2),
                FLOOR_BOOKMARK_AGENT,
            )
            _write(
                root,
                "20260425T115900Z-session-exit-bookmark.md",
                self.now - timedelta(minutes=1),
                FLOOR_BOOKMARK_AGENT,
            )
            self._agree_on(root)

    def test_agree_when_only_authored_handoffs_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "20260425T100000Z-a.md", self.now - timedelta(hours=5), "claude-code")
            _write(root, "20260425T110000Z-b.md", self.now - timedelta(hours=1), "codex")
            self._agree_on(root)

    def test_agree_when_the_corpus_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._agree_on(Path(tmp))

    def test_agree_on_the_live_repository_corpus(self) -> None:
        """The real corpus, not only synthetic ones — this is where it broke."""
        self._agree_on(REPO_ROOT)


class TestTheIdentityHasExactlyOneDefinition(unittest.TestCase):
    """A fourth reader must not be able to hardcode the writer identity.

    Sharing a constant only helps if nothing re-states it. This is the structural
    fence: the literal may appear once, in the module that defines it. Anything
    else must import. Written as a scan rather than a convention because the
    convention is exactly what failed three times.
    """

    def test_the_identity_literal_appears_only_in_its_defining_module(self) -> None:
        owner = REPO_ROOT / "src" / "gzkit" / "handoff_selection.py"
        offenders: list[str] = []
        roots = [REPO_ROOT / "src" / "gzkit", REPO_ROOT / "scripts"]
        for root in roots:
            for path in root.rglob("*.py"):
                if path == owner:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                # The literal, not the NAME — importers legitimately mention
                # `FLOOR_BOOKMARK_AGENT`; what may not recur is the string.
                for line in text.splitlines():
                    if re.search(r"""["']gzkit-session-exit["']""", line):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}: {line.strip()}")
        self.assertEqual(
            offenders,
            [],
            "the floor-bookmark identity is re-stated instead of imported from "
            "gzkit.handoff_selection; a second copy is how the readers drift",
        )

    # No vacuity guard is needed, and one was removed rather than kept: the scan
    # is self-guarding. `owner` is excluded by PATH EQUALITY, so if the defining
    # module is ever renamed or moved, nothing matches the exclusion, the renamed
    # module is scanned like any other, and its own literal trips the assertion.
    # A guard reading the owner's text to prove it still defines the constant was
    # a filesystem-grep test — content, not behavior — and `gz check`'s
    # tautological-test audit flagged it correctly (`.gzkit/rules/tests.md`
    # § The discriminator: if behavior changed but text did not, would it fail?).


if __name__ == "__main__":
    unittest.main()
