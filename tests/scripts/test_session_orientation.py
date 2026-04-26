"""Unit tests for scripts/session_orientation.py (GHI #326, SPEC-uplift CAP-13).

The orientation script aggregates seven session-boot sections into a markdown
digest used by SessionStart hooks. These tests pin the operator-facing
contract:

- All seven sections appear in the rendered output, in canonical order.
- Freshness classification honors the gz-session-handoff Fresh / Slightly-Stale
  / Stale / Very-Stale buckets.
- Empty state degrades gracefully — every section emits a "no data" line
  rather than disappearing or crashing the hook.
- Output is deterministic for a given (state, now) pair.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path

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

    def test_all_seven_sections_present_with_empty_state(self):
        empty_state = {
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

    def test_returns_none_when_no_handoffs_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.mod.collect_handoff(Path(tmp) / "missing", self.now)
            self.assertIsNone(result)

    def test_picks_latest_handoff_and_classifies_freshness(self):
        with tempfile.TemporaryDirectory() as tmp:
            handoffs = Path(tmp) / "handoffs"
            handoffs.mkdir()
            recent_ts = (self.now - timedelta(hours=2)).isoformat()
            stale_ts = (self.now - timedelta(days=4)).isoformat()
            (handoffs / "old-handoff.md").write_text(
                f"---\ntimestamp: {stale_ts}\n---\n\n## Immediate Next Steps\n\n1. Old action\n",
                encoding="utf-8",
            )
            new_body = (
                f"---\ntimestamp: {recent_ts}\n---\n\n"
                "## Immediate Next Steps\n\n1. Resume new work\n"
            )
            (handoffs / "new-handoff.md").write_text(new_body, encoding="utf-8")
            result = self.mod.collect_handoff(handoffs, self.now)
            self.assertIsNotNone(result)
            assert result is not None
            self.assertIn("new-handoff.md", result["path"])
            self.assertEqual(result["freshness"], "Fresh")
            self.assertEqual(result["first_action"], "Resume new work")


if __name__ == "__main__":
    unittest.main()
