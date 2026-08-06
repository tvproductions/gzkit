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


class TestTheDeltaRuleHasExactlyOneDefinition(unittest.TestCase):
    """The "what has landed since this handoff" rule must not be re-stated either.

    Selection was coupled under GHI #758 and the DELTA question was left
    uncoupled, so it drifted the same way: `session_exit._covering_handoff` and
    `session_orientation` each built their own `<sha>..HEAD` range and each
    spelled the handoffs exclusion pathspec themselves — four copies across two
    modules, and each learned the GHI #760 lesson (anchor on identity, never a
    timestamp) in a separate commit with a separate test.

    Two copies is a convention. The fence is what makes it a mechanism: a reader
    that wants to ask this question must import the rule, and importing it puts
    `commits_since_range` in front of them at the same moment.
    """

    def test_the_exclusion_pathspec_appears_only_in_its_defining_module(self) -> None:
        owner = REPO_ROOT / "src" / "gzkit" / "handoff_selection.py"
        offenders: list[str] = []
        for root in (REPO_ROOT / "src" / "gzkit", REPO_ROOT / "scripts"):
            for path in root.rglob("*.py"):
                if path == owner:
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    continue
                for line in text.splitlines():
                    # The literal, not the NAME — importers legitimately mention
                    # HANDOFF_PATHSPEC_EXCLUDE; what may not recur is the string.
                    if re.search(r"""["']:\(exclude\)\.gzkit/handoffs["']""", line):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}: {line.strip()}")
        self.assertEqual(
            offenders,
            [],
            "the handoffs exclusion pathspec is re-stated instead of imported from "
            "gzkit.handoff_selection; a second copy is how the delta readers drift",
        )

    def test_an_absent_landing_commit_anchors_at_head(self) -> None:
        """A staged-but-uncommitted handoff has no landing commit and needs none:
        every commit in history predates it, so the range is empty (GHI #760)."""
        from gzkit.handoff_selection import commits_since_range

        self.assertEqual(commits_since_range(None), "HEAD..HEAD")
        self.assertEqual(commits_since_range(""), "HEAD..HEAD")

    def test_a_landing_commit_is_excluded_by_identity_not_by_timestamp(self) -> None:
        """`<sha>..HEAD` excludes the landing commit itself. A `--since=<its time>`
        window cannot: `gz git-sync` bundles `.gzkit/**`, so that commit carries
        adjacent files and reads as work the handoff failed to describe."""
        from gzkit.handoff_selection import commits_since_range

        self.assertEqual(commits_since_range("93e7e229a"), "93e7e229a..HEAD")
        self.assertEqual(commits_since_range("  93e7e229a\n"), "93e7e229a..HEAD")


class TestTheAccountAnchorAgreesWithSelection(unittest.TestCase):
    """A fourth reader over the same corpus, fenced like the other three.

    `collect_handoff_account` picks the newest AUTHORED handoff to measure from.
    Whenever an authored handoff exists that must be the same document
    `selection_rank` picks, or the banner would render an account measured from
    one handoff directly beneath a section naming another.

    They are allowed to differ in exactly one corpus — floor bookmarks only —
    where selection deprioritizes-but-never-drops and the account has no authored
    anchor at all. That divergence is asserted, not merely tolerated.
    """

    def setUp(self) -> None:
        self.mod = _load_orientation()
        self.now = datetime(2026, 4, 25, 12, 0, 0, tzinfo=UTC)

    def _anchor_via_selection(self, root: Path) -> Path | None:
        """The anchor `selection_rank` would pick, over production's admitted corpus.

        Mirrors production's two admission rules deliberately: `_looks_like_handoff`
        (`.gzkit/handoffs/AGENTS.md` is a directory README, not a handoff) and the
        mtime fallback for a missing frontmatter timestamp. A differential that
        admitted a different corpus would compare two answers to two questions.
        """
        candidates = []
        for path in sorted((root / ".gzkit" / "handoffs").glob("*.md")):
            text = path.read_text(encoding="utf-8", errors="replace")
            if not self.mod._looks_like_handoff(text):
                continue
            agent = self.mod.parse_frontmatter_agent(text)
            ts = self.mod.parse_frontmatter_timestamp(text)
            if ts is None:
                ts = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
            candidates.append((selection_rank(agent, ts), agent, path))
        if not candidates:
            return None
        _, agent, path = max(candidates, key=lambda row: row[0])
        return None if is_floor_bookmark(agent) else path

    def test_agree_when_an_authored_handoff_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "old.md", self.now - timedelta(days=2), "claude-code")
            _write(root, "new.md", self.now - timedelta(hours=2), "claude-code")
            _write(root, "bm.md", self.now - timedelta(minutes=1), FLOOR_BOOKMARK_AGENT)
            account = self.mod.collect_handoff_account(root, self.now)
            expected = self._anchor_via_selection(root)
            assert account is not None and expected is not None
            self.assertTrue(account["anchor"].endswith(expected.name))

    def test_agree_that_a_floor_only_corpus_has_no_authored_anchor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "bm.md", self.now - timedelta(minutes=1), FLOOR_BOOKMARK_AGENT)
            self.assertIsNone(self._anchor_via_selection(root))
            self.assertIsNone(self.mod.collect_handoff_account(root, self.now))

    def test_agree_on_the_live_repository_corpus(self) -> None:
        """The synthetic corpora above are the ones this session imagined; the
        live one is the corpus that actually ships."""
        expected = self._anchor_via_selection(REPO_ROOT)
        account = self.mod.collect_handoff_account(REPO_ROOT, self.now)
        if expected is None:
            self.assertIsNone(account)
            return
        assert account is not None
        self.assertTrue(account["anchor"].endswith(expected.name))


if __name__ == "__main__":
    unittest.main()
