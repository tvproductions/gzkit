"""Unit tests for the MX awareness hook (OBPI-0.0.74-07).

Covers three behaviors:
  REQ-0.0.74-07-01 — banner injected every turn while marker present; no-op absent
  REQ-0.0.74-07-02 — liveness check reports unwired/dead adapter as detected defect

Tests are derived from brief acceptance criteria, not from the implementation.
"""

import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.traceability import covers

_REPO_ROOT = Path(__file__).resolve().parents[2]
_HOOK_PATH = _REPO_ROOT / ".claude" / "hooks" / "mx-awareness.py"

_BANNER = (
    "MX MODE ACTIVE — most guards advisory; gate5_invariants and the PRIME DIRECTIVE still bind"
)


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("mx_awareness_hook", _HOOK_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# REQ-0.0.74-07-01 — get_banner() from awareness module
# ---------------------------------------------------------------------------


class TestGetBannerFunction(unittest.TestCase):
    """get_banner() returns exact banner when marker present; empty string absent."""

    @covers("REQ-0.0.74-07-01")
    def test_banner_when_marker_present(self):
        from gzkit.mx.awareness import MX_BANNER, get_banner

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()
            (root / ".gzkit" / "mx.json").write_text("{}", encoding="utf-8")
            result = get_banner(root)

        self.assertEqual(result, MX_BANNER)

    def test_safe_mode_banner_names_the_mode_and_the_contract(self):
        """GHI #1244: under a safe-mode marker the banner says what is suspended and what binds."""
        from gzkit.mx.awareness import MX_BANNER, get_banner, safe_mode_banner

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()
            (root / ".gzkit" / "mx.json").write_text(
                '{"session_id": "s", "mode": "safe", "contract": "docs/governance/pilotage.md"}',
                encoding="utf-8",
            )
            result = get_banner(root)

        self.assertEqual(result, safe_mode_banner("docs/governance/pilotage.md"))
        self.assertNotEqual(result, MX_BANNER)
        self.assertIn("SAFE MODE ACTIVE", result)
        self.assertIn("docs/governance/pilotage.md", result)
        self.assertIn("gate5_invariants", result)

    def test_safe_mode_is_the_sole_term_of_the_banner(self):
        """Operator ruling 2026-10-16: safe mode is the sole term; the banner and the
        hook's stdlib fallback name no other regime."""
        from gzkit.mx.awareness import safe_mode_banner

        hook = _load_hook_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()
            (root / ".gzkit" / "mx.json").write_text(
                '{"session_id": "s", "mode": "safe", "contract": "docs/governance/pilotage.md"}',
                encoding="utf-8",
            )
            fallback = hook._banner_stdlib(str(root))
        for banner in (safe_mode_banner("docs/governance/pilotage.md"), fallback):
            with self.subTest(banner=banner[:40]):
                self.assertTrue(banner.startswith("SAFE MODE ACTIVE — "))
                self.assertNotIn("martial", banner.lower())

    def test_an_unreadable_or_non_object_marker_is_read_as_the_hangar(self):
        """GHI #1244: a marker that cannot say its mode keeps the hangar's presence reading."""
        from gzkit.mx.awareness import MX_BANNER, get_banner

        for raw in ("{not json", "[]", '"safe"'):
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as tmpdir:
                root = Path(tmpdir)
                (root / ".gzkit").mkdir()
                (root / ".gzkit" / "mx.json").write_text(raw, encoding="utf-8")
                self.assertEqual(get_banner(root), MX_BANNER)

    def test_the_hook_fallback_reads_the_mode_without_gzkit(self):
        """GHI #1244: the stdlib fallback in the hook script names safe mode and its contract."""
        from gzkit.mx.awareness import MX_BANNER, safe_mode_banner

        hook = _load_hook_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()
            marker = root / ".gzkit" / "mx.json"
            marker.write_text(
                '{"session_id": "s", "mode": "safe", "contract": "docs/governance/pilotage.md"}',
                encoding="utf-8",
            )
            self.assertEqual(
                hook._banner_stdlib(str(root)), safe_mode_banner("docs/governance/pilotage.md")
            )
            marker.write_text('{"session_id": "s"}', encoding="utf-8")
            self.assertEqual(hook._banner_stdlib(str(root)), MX_BANNER)
            marker.write_text("{not json", encoding="utf-8")
            self.assertEqual(hook._banner_stdlib(str(root)), MX_BANNER)

    @covers("REQ-0.0.74-07-01")
    def test_empty_when_marker_absent(self):
        from gzkit.mx.awareness import get_banner

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()
            result = get_banner(root)

        self.assertEqual(result, "")


# ---------------------------------------------------------------------------
# REQ-0.0.74-07-01 — hook adapter banner injection via stdout
# ---------------------------------------------------------------------------


class TestHookAdapterBannerInjection(unittest.TestCase):
    """Hook adapter injects banner to stdout when marker present; silent when absent."""

    def setUp(self):
        self._hook = _load_hook_module()

    @covers("REQ-0.0.74-07-01")
    def test_banner_injected_to_stdout_when_marker_present(self):
        from gzkit.mx.awareness import MX_BANNER

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()
            (root / ".gzkit" / "mx.json").write_text("{}", encoding="utf-8")

            payload = {"hook_event_name": "UserPromptSubmit", "cwd": str(root)}
            stdout = io.StringIO()
            with (
                patch.object(sys, "stdin", io.StringIO(json.dumps(payload))),
                patch.object(sys, "stdout", stdout),
            ):
                exit_code = self._hook.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), MX_BANNER)

    @covers("REQ-0.0.74-07-01")
    def test_no_stdout_when_marker_absent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()

            payload = {"hook_event_name": "UserPromptSubmit", "cwd": str(root)}
            stdout = io.StringIO()
            with (
                patch.object(sys, "stdin", io.StringIO(json.dumps(payload))),
                patch.object(sys, "stdout", stdout),
            ):
                exit_code = self._hook.main()

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue(), "")

    def test_fail_open_on_malformed_stdin(self):
        """Hook exits 0 even when stdin is malformed — a turn must always begin."""
        stdout = io.StringIO()
        with (
            patch.object(sys, "stdin", io.StringIO("not-json")),
            patch.object(sys, "stdout", stdout),
        ):
            exit_code = self._hook.main()

        self.assertEqual(exit_code, 0)


# ---------------------------------------------------------------------------
# REQ-0.0.74-07-02 — liveness check reports defects
# ---------------------------------------------------------------------------


class TestLivenessCheck(unittest.TestCase):
    """check_hook_liveness() reports unwired/dead adapter as a detected defect."""

    def _make_wired_root(self, tmpdir: str) -> Path:
        """Create a tmpdir tree with hook file + settings.json wired."""
        root = Path(tmpdir)
        hooks_dir = root / ".claude" / "hooks"
        hooks_dir.mkdir(parents=True)
        (hooks_dir / "mx-awareness.py").write_text("# hook", encoding="utf-8")

        settings = {
            "hooks": {
                "UserPromptSubmit": [
                    {
                        "matcher": "*",
                        "hooks": [
                            {
                                "type": "command",
                                "command": (
                                    'uv run python "$CLAUDE_PROJECT_DIR'
                                    '/.claude/hooks/mx-awareness.py"'
                                ),
                            }
                        ],
                    }
                ]
            }
        }
        settings_path = root / ".claude" / "settings.json"
        settings_path.write_text(json.dumps(settings), encoding="utf-8")
        return root

    @covers("REQ-0.0.74-07-02")
    def test_missing_hook_file_reports_defect(self):
        from gzkit.mx.awareness import check_hook_liveness

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # No .claude/hooks/mx-awareness.py
            result = check_hook_liveness(root)

        self.assertFalse(result.ok)
        self.assertIsNotNone(result.defect)
        assert result.defect is not None
        self.assertIn("mx-awareness.py", result.defect)

    @covers("REQ-0.0.74-07-02")
    def test_hook_not_in_settings_reports_defect(self):
        from gzkit.mx.awareness import check_hook_liveness

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Hook file exists but settings.json has no UserPromptSubmit hook
            hooks_dir = root / ".claude" / "hooks"
            hooks_dir.mkdir(parents=True)
            (hooks_dir / "mx-awareness.py").write_text("# hook", encoding="utf-8")
            (root / ".claude" / "settings.json").write_text(
                json.dumps({"hooks": {}}), encoding="utf-8"
            )
            result = check_hook_liveness(root)

        self.assertFalse(result.ok)
        self.assertIsNotNone(result.defect)
        assert result.defect is not None
        self.assertIn("settings.json", result.defect)

    @covers("REQ-0.0.74-07-02")
    def test_wired_hook_reports_ok(self):
        from gzkit.mx.awareness import check_hook_liveness

        with tempfile.TemporaryDirectory() as tmpdir:
            root = self._make_wired_root(tmpdir)
            result = check_hook_liveness(root)

        self.assertTrue(result.ok)
        self.assertIsNone(result.defect)


class TestSafeModeBannerStatesTheDemotion(unittest.TestCase):
    """Operator ruling 2026-10-17 (R6): safe mode lowers guards, and the banner says so."""

    def test_banner_and_stdlib_fallback_say_most_guards_are_advisory(self):
        from gzkit.mx.awareness import safe_mode_banner

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".gzkit").mkdir()
            (root / ".gzkit" / "mx.json").write_text(
                '{"session_id": "s", "mode": "safe", "contract": "docs/governance/pilotage.md"}',
                encoding="utf-8",
            )
            hook = _load_hook_module()
            fallback = hook._banner_stdlib(str(root))
        for banner in (safe_mode_banner("docs/governance/pilotage.md"), fallback):
            with self.subTest(banner=banner[:40]):
                self.assertIn("most guards advisory", banner)
                self.assertNotIn("full strength", banner)
