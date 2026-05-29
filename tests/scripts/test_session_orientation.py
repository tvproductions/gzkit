"""Unit tests for scripts/session_orientation.py (GHI #326, SPEC-uplift CAP-13).

The orientation script aggregates session-boot sections into a markdown
digest used by SessionStart hooks. These tests pin the operator-facing
contract:

- All canonical sections appear in the rendered output, in canonical order.
- Freshness classification honors the gz-session-handoff Fresh / Slightly-Stale
  / Stale / Very-Stale buckets.
- Empty state degrades gracefully — every section emits a "no data" line
  rather than disappearing or crashing the hook.
- Output is deterministic for a given (state, now) pair.
- Git-remote-state surfacing (GHI #338) names ahead/behind counts and emits
  a binding nudge when the local clone is behind origin.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "session_orientation.py"


def _load_orientation_module():
    spec = importlib.util.spec_from_file_location("session_orientation", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load {SCRIPT_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["session_orientation"] = module
    spec.loader.exec_module(module)
    return module


SECTION_HEADINGS = (
    "## Git remote state",
    "## Most-recent handoff",
    "## Open session-handoff GHIs",
    "## Active OBPI claims",
    "## Active ADR pipeline state",
    "## Recent ledger events (last 24h)",
    "## Open blockers",
    "## Skill-awareness re-injection",
)


class TestFreshnessClassification(unittest.TestCase):
    def setUp(self):
        self.mod = _load_orientation_module()
        self.now = datetime(2026, 4, 25, 12, 0, 0, tzinfo=UTC)

    def test_fresh_under_24h(self):
        ts = self.now - timedelta(hours=23)
        self.assertEqual(self.mod.classify_freshness(self.now, ts), "Fresh")

    def test_slightly_stale_24_to_72h(self):
        ts = self.now - timedelta(hours=48)
        self.assertEqual(self.mod.classify_freshness(self.now, ts), "Slightly-Stale")

    def test_stale_72h_to_7d(self):
        ts = self.now - timedelta(days=4)
        self.assertEqual(self.mod.classify_freshness(self.now, ts), "Stale")

    def test_very_stale_over_7d(self):
        ts = self.now - timedelta(days=10)
        self.assertEqual(self.mod.classify_freshness(self.now, ts), "Very-Stale")


class TestRenderEmitsAllSections(unittest.TestCase):
    def setUp(self):
        self.mod = _load_orientation_module()
        self.now = datetime(2026, 4, 25, 12, 0, 0, tzinfo=UTC)

    def test_all_canonical_sections_present_with_empty_state(self):
        empty_state = {
            "remote_state": None,
            "handoff": None,
            "session_handoff_ghis": [],
            "obpi_locks": [],
            "adr_pipeline": [],
            "recent_events": [],
            "blockers": [],
        }
        rendered = self.mod.render(empty_state, self.now)
        for heading in SECTION_HEADINGS:
            self.assertIn(heading, rendered, f"missing section: {heading}")

    def test_sections_appear_in_canonical_order(self):
        empty_state = {
            "remote_state": None,
            "handoff": None,
            "session_handoff_ghis": [],
            "obpi_locks": [],
            "adr_pipeline": [],
            "recent_events": [],
            "blockers": [],
        }
        rendered = self.mod.render(empty_state, self.now)
        positions = [rendered.find(h) for h in SECTION_HEADINGS]
        self.assertEqual(
            positions,
            sorted(positions),
            "section headings must appear in canonical order",
        )

    def test_handoff_block_includes_freshness_and_resume_action(self):
        state = {
            "remote_state": None,
            "handoff": {
                "path": ".gzkit/handoffs/2026-04-25-test.md",
                "freshness": "Fresh",
                "first_action": "Continue OBPI-X.Y.Z-01",
            },
            "session_handoff_ghis": [],
            "obpi_locks": [],
            "adr_pipeline": [],
            "recent_events": [],
            "blockers": [],
        }
        rendered = self.mod.render(state, self.now)
        self.assertIn("2026-04-25-test.md", rendered)
        self.assertIn("Fresh", rendered)
        self.assertIn("Continue OBPI-X.Y.Z-01", rendered)

    def test_render_is_deterministic(self):
        state = {
            "remote_state": None,
            "handoff": None,
            "session_handoff_ghis": [{"number": 325, "title": "Session handoff X"}],
            "obpi_locks": [],
            "adr_pipeline": [],
            "recent_events": [],
            "blockers": [],
        }
        a = self.mod.render(state, self.now)
        b = self.mod.render(state, self.now)
        self.assertEqual(a, b, "render must be deterministic for fixed state")


class TestCollectRecentEvents(unittest.TestCase):
    def setUp(self):
        self.mod = _load_orientation_module()
        self.now = datetime(2026, 4, 25, 12, 0, 0, tzinfo=UTC)

    def test_ledger_window_filters_to_last_24h(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            recent = (self.now - timedelta(hours=2)).isoformat()
            old = (self.now - timedelta(days=3)).isoformat()
            ledger.write_text(
                "\n".join(
                    [
                        json.dumps({"event": "adr_recorded", "ts": recent}),
                        json.dumps({"event": "obpi_completed", "ts": old}),
                        json.dumps({"event_type": "receipt", "timestamp": recent}),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            events = self.mod.collect_recent_events(ledger, self.now)
            self.assertEqual(len(events), 2, "must filter out events older than 24h")
            kinds = {e.get("event") or e.get("event_type") for e in events}
            self.assertEqual(kinds, {"adr_recorded", "receipt"})

    def test_missing_ledger_returns_empty_list(self):
        events = self.mod.collect_recent_events(Path("nonexistent-ledger.jsonl"), self.now)
        self.assertEqual(events, [])


class TestCollectHandoff(unittest.TestCase):
    def setUp(self):
        self.mod = _load_orientation_module()
        self.now = datetime(2026, 4, 25, 12, 0, 0, tzinfo=UTC)

    @staticmethod
    def _handoff(ts: str, action: str, *, adr_id: str = "ADR-0.0.1") -> str:
        return (
            f"---\nmode: CREATE\nadr_id: {adr_id}\ntimestamp: {ts}\nagent: claude-code\n---\n\n"
            f"## Immediate Next Steps\n\n1. {action}\n"
        )

    def test_returns_none_when_no_handoffs_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.mod.collect_handoff(Path(tmp), self.now)
            self.assertIsNone(result)

    def test_picks_latest_handoff_and_classifies_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            handoffs = Path(tmp) / ".gzkit" / "handoffs"
            handoffs.mkdir(parents=True)
            recent_ts = (self.now - timedelta(hours=2)).isoformat()
            stale_ts = (self.now - timedelta(days=4)).isoformat()
            (handoffs / "old-handoff.md").write_text(
                self._handoff(stale_ts, "Old action"), encoding="utf-8"
            )
            (handoffs / "new-handoff.md").write_text(
                self._handoff(recent_ts, "Resume new work"), encoding="utf-8"
            )
            result = self.mod.collect_handoff(Path(tmp), self.now)
            self.assertIsNotNone(result)
            assert result is not None
            self.assertIn("new-handoff.md", result["path"])
            self.assertEqual(result["freshness"], "Fresh")
            self.assertEqual(result["first_action"], "Resume new work")

    def test_excludes_non_handoff_markdown_in_handoffs_dir(self):
        """A non-handoff `.md` (no `adr_id` frontmatter, e.g. AGENTS.md) is never
        surfaced as the most-recent handoff even when newest by mtime (GHI #529)."""
        with tempfile.TemporaryDirectory() as tmp:
            handoffs = Path(tmp) / ".gzkit" / "handoffs"
            handoffs.mkdir(parents=True)
            ts = (self.now - timedelta(hours=2)).isoformat()
            (handoffs / "real-handoff.md").write_text(
                self._handoff(ts, "Resume work"), encoding="utf-8"
            )
            # AGENTS.md: generated subtree-rules file, no frontmatter; written last
            # so it is newest by mtime — must still be excluded.
            (handoffs / "AGENTS.md").write_text(
                "<!-- Generated -->\n# Handoffs subtree rules\n", encoding="utf-8"
            )
            result = self.mod.collect_handoff(Path(tmp), self.now)
            self.assertIsNotNone(result)
            assert result is not None
            self.assertIn("real-handoff.md", result["path"])
            self.assertNotIn("AGENTS.md", result["path"])

    def test_discovers_adr_package_handoffs_and_unions_with_gzkit(self):
        """Newest-wins across both `.gzkit/handoffs/` and `{ADR-package}/handoffs/`
        (the read/write split-brain, GHI #529)."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            gzkit_handoffs = root / ".gzkit" / "handoffs"
            gzkit_handoffs.mkdir(parents=True)
            adr_handoffs = (
                root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.63-x" / "handoffs"
            )
            adr_handoffs.mkdir(parents=True)
            older = (self.now - timedelta(hours=10)).isoformat()
            newer = (self.now - timedelta(hours=1)).isoformat()
            (gzkit_handoffs / "gzkit-handoff.md").write_text(
                self._handoff(older, "Old gzkit-dir action"), encoding="utf-8"
            )
            (adr_handoffs / "adr-handoff.md").write_text(
                self._handoff(newer, "Latest ADR-package action", adr_id="ADR-0.0.63"),
                encoding="utf-8",
            )
            result = self.mod.collect_handoff(root, self.now)
            self.assertIsNotNone(result)
            assert result is not None
            self.assertIn("adr-handoff.md", result["path"])
            self.assertEqual(result["first_action"], "Latest ADR-package action")


class TestCollectRemoteState(unittest.TestCase):
    """GHI #338 — orientation surfaces git-remote-divergence at session start."""

    def setUp(self):
        self.mod = _load_orientation_module()
        self.now = datetime(2026, 4, 26, 12, 0, 0, tzinfo=UTC)

    def _fake_run(self, mapping):
        """Return a subprocess.run side-effect that maps argv prefix → CompletedProcess."""

        def side_effect(args, **_kwargs):
            for prefix, result in mapping.items():
                if list(args[: len(prefix)]) == list(prefix):
                    return result
            raise AssertionError(f"unexpected git invocation: {args}")

        return side_effect

    def _completed(self, stdout="", returncode=0):
        return subprocess_completed(stdout=stdout, returncode=returncode)

    def test_clean_clone_reports_zero_behind(self):
        mapping = {
            ("git", "fetch"): self._completed(),
            ("git", "rev-parse", "--abbrev-ref"): self._completed(stdout="main\n"),
            ("git", "rev-list", "--left-right", "--count"): self._completed(stdout="0\t0\n"),
        }
        with (
            mock.patch.object(self.mod.subprocess, "run", side_effect=self._fake_run(mapping)),
            mock.patch.dict(self.mod.os.environ, {}, clear=False),
        ):
            self.mod.os.environ.pop("GZKIT_ORIENTATION_NO_FETCH", None)
            state = self.mod.collect_remote_state()
        self.assertIsNotNone(state)
        assert state is not None
        self.assertEqual(state["branch"], "main")
        self.assertEqual(state["ahead"], 0)
        self.assertEqual(state["behind"], 0)
        self.assertFalse(state["is_behind"])

    def test_behind_clone_reports_count_and_marks_behind(self):
        mapping = {
            ("git", "fetch"): self._completed(),
            ("git", "rev-parse", "--abbrev-ref"): self._completed(stdout="main\n"),
            # rev-list --left-right --count A...B prints "<left>\t<right>"
            # left = ahead, right = behind for HEAD...origin/main? we ordered origin/main...HEAD
            # so left = behind (commits in origin not in local), right = ahead
            ("git", "rev-list", "--left-right", "--count"): self._completed(stdout="10\t0\n"),
        }
        with (
            mock.patch.object(self.mod.subprocess, "run", side_effect=self._fake_run(mapping)),
            mock.patch.dict(self.mod.os.environ, {}, clear=False),
        ):
            self.mod.os.environ.pop("GZKIT_ORIENTATION_NO_FETCH", None)
            state = self.mod.collect_remote_state()
        self.assertIsNotNone(state)
        assert state is not None
        self.assertEqual(state["behind"], 10)
        self.assertEqual(state["ahead"], 0)
        self.assertTrue(state["is_behind"])

    def test_no_fetch_env_var_skips_fetch_subprocess(self):
        called: list[tuple] = []

        def record_run(args, **_kwargs):
            called.append(tuple(args[:2]))
            if args[:2] == ["git", "fetch"]:
                raise AssertionError("fetch must be skipped when GZKIT_ORIENTATION_NO_FETCH=1")
            if args[:3] == ["git", "rev-parse", "--abbrev-ref"]:
                return self._completed(stdout="main\n")
            if args[:4] == ["git", "rev-list", "--left-right", "--count"]:
                return self._completed(stdout="0\t0\n")
            raise AssertionError(f"unexpected git invocation: {args}")

        with (
            mock.patch.object(self.mod.subprocess, "run", side_effect=record_run),
            mock.patch.dict(
                self.mod.os.environ,
                {"GZKIT_ORIENTATION_NO_FETCH": "1"},
                clear=False,
            ),
        ):
            state = self.mod.collect_remote_state()
        self.assertIsNotNone(state)
        self.assertNotIn(("git", "fetch"), called)

    def test_git_unavailable_returns_none(self):
        with mock.patch.object(
            self.mod.subprocess,
            "run",
            side_effect=FileNotFoundError("git not on PATH"),
        ):
            state = self.mod.collect_remote_state()
        self.assertIsNone(state)


class TestRenderRemoteStateBlock(unittest.TestCase):
    """GHI #338 — render emits a binding nudge when the clone is behind origin."""

    def setUp(self):
        self.mod = _load_orientation_module()
        self.now = datetime(2026, 4, 26, 12, 0, 0, tzinfo=UTC)

    def _state(self, remote_state):
        return {
            "remote_state": remote_state,
            "handoff": None,
            "session_handoff_ghis": [],
            "obpi_locks": [],
            "adr_pipeline": [],
            "recent_events": [],
            "blockers": [],
        }

    def test_clean_clone_shows_synced_line_no_nudge(self):
        rendered = self.mod.render(
            self._state(
                {
                    "branch": "main",
                    "ahead": 0,
                    "behind": 0,
                    "is_behind": False,
                }
            ),
            self.now,
        )
        self.assertIn("## Git remote state", rendered)
        self.assertIn("ahead=0 behind=0", rendered)
        # Binding nudge text MUST NOT appear when the clone is current.
        self.assertNotIn("git pull --ff-only", rendered)

    def test_behind_clone_includes_binding_nudge(self):
        rendered = self.mod.render(
            self._state(
                {
                    "branch": "main",
                    "ahead": 0,
                    "behind": 10,
                    "is_behind": True,
                }
            ),
            self.now,
        )
        self.assertIn("ahead=0 behind=10", rendered)
        # The nudge names the remediation command and the binding language.
        self.assertIn("git pull --ff-only", rendered)
        self.assertIn("10 commits behind", rendered)

    def test_remote_state_unavailable_emits_no_data_line(self):
        rendered = self.mod.render(self._state(None), self.now)
        self.assertIn("## Git remote state", rendered)
        self.assertIn("(no remote state available)", rendered)


def subprocess_completed(stdout: str = "", returncode: int = 0):
    """Tiny stand-in for subprocess.CompletedProcess covering the fields we use."""
    import subprocess as _sp

    return _sp.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr="")


if __name__ == "__main__":
    unittest.main()
