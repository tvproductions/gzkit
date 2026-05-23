"""Tests for SessionStart orientation freshness audit (GHI #341).

Each test pins one of the four acceptance criteria from GHI #341 with a
deliberately-broken fixture and asserts the audit returns at least one
``ValidationError`` so ``gz validate --orientation-freshness`` exits 3.

Per ``.gzkit/rules/tests.md`` § Tests assert semantics, not strings — the
assertions check the semantic ("the audit caught the regression"), not
exact error message text.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_orientation_freshness

_CODEX_PROJECT_UV_HOOK = (
    'uv run --cache-dir "$(git rev-parse --show-toplevel)/.gzkit/cache/uv" '
    'python "$(git rev-parse --show-toplevel)/scripts/session_orientation.py"'
)
_CODEX_USER_CACHE_HOOK = (
    'uv run python "$(git rev-parse --show-toplevel)/scripts/session_orientation.py"'
)

_CLAUDE_OK = {
    "hooks": {
        "SessionStart": [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": "uv run python scripts/session_orientation.py",
                    }
                ],
            }
        ]
    }
}


_CODEX_OK = {
    "hooks": {
        "SessionStart": [
            {
                "command": [
                    "sh",
                    "-c",
                    _CODEX_PROJECT_UV_HOOK,
                ],
                "inject": "additionalContext",
            }
        ]
    }
}


_SCRIPT_OK = '''\
"""Stub orientation script."""

SECTION_HEADINGS = (
    "Git remote state",
    "Most-recent handoff",
)


def collect_remote_state():
    return None


def collect_state(repo_root, now):
    return {"remote_state": collect_remote_state()}
'''


def _seed_baseline(root: Path) -> None:
    """Seed a project root that passes audit_orientation_freshness clean."""
    (root / ".claude").mkdir()
    (root / ".claude" / "settings.json").write_text(json.dumps(_CLAUDE_OK), encoding="utf-8")
    (root / ".codex").mkdir()
    (root / ".codex" / "hooks.json").write_text(json.dumps(_CODEX_OK), encoding="utf-8")
    (root / "scripts").mkdir()
    (root / "scripts" / "session_orientation.py").write_text(_SCRIPT_OK, encoding="utf-8")


class TestOrientationFreshnessBaseline(unittest.TestCase):
    """The baseline fixture must pass clean — guards against false positives."""

    def test_baseline_fixture_passes_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            errors = audit_orientation_freshness(root)
            self.assertEqual(errors, [])


class TestOrientationFreshnessFailClose(unittest.TestCase):
    """Each broken fixture must produce at least one orientation_freshness error."""

    def test_claude_settings_missing_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            (root / ".claude" / "settings.json").unlink()
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any(e.artifact == ".claude/settings.json" for e in errors),
                f"expected .claude/settings.json error, got {errors}",
            )

    def test_claude_settings_hook_command_drift_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            drifted = {
                "hooks": {
                    "SessionStart": [
                        {
                            "matcher": "*",
                            "hooks": [{"type": "command", "command": "echo no-op"}],
                        }
                    ]
                }
            }
            (root / ".claude" / "settings.json").write_text(json.dumps(drifted), encoding="utf-8")
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any(e.artifact == ".claude/settings.json" for e in errors),
                f"expected hook-drift error on .claude/settings.json, got {errors}",
            )

    def test_codex_hooks_missing_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            (root / ".codex" / "hooks.json").unlink()
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any(e.artifact == ".codex/hooks.json" for e in errors),
                f"expected .codex/hooks.json error, got {errors}",
            )

    def test_codex_hooks_command_drift_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            drifted = {
                "hooks": {
                    "SessionStart": [{"command": ["echo", "no-op"], "inject": "additionalContext"}]
                }
            }
            (root / ".codex" / "hooks.json").write_text(json.dumps(drifted), encoding="utf-8")
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any(e.artifact == ".codex/hooks.json" for e in errors),
                f"expected hook-drift error on .codex/hooks.json, got {errors}",
            )

    def test_codex_hooks_user_cache_dependency_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            drifted = {
                "hooks": {
                    "SessionStart": [
                        {
                            "command": [
                                "sh",
                                "-c",
                                _CODEX_USER_CACHE_HOOK,
                            ],
                            "inject": "additionalContext",
                        }
                    ]
                }
            }
            (root / ".codex" / "hooks.json").write_text(json.dumps(drifted), encoding="utf-8")
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any(
                    e.artifact == ".codex/hooks.json" and "project-local uv cache" in e.message
                    for e in errors
                ),
                f"expected project-local cache error on .codex/hooks.json, got {errors}",
            )

    def test_section_heading_missing_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            drifted = '''\
"""Stub orientation script."""

SECTION_HEADINGS = (
    "Most-recent handoff",
)


def collect_remote_state():
    return None


def collect_state(repo_root, now):
    return {"remote_state": collect_remote_state()}
'''
            (root / "scripts" / "session_orientation.py").write_text(drifted, encoding="utf-8")
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any("SECTION_HEADINGS" in e.message for e in errors),
                f"expected SECTION_HEADINGS regression error, got {errors}",
            )

    def test_collect_state_missing_collector_reference_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            drifted = '''\
"""Stub orientation script with regressed wiring."""

SECTION_HEADINGS = (
    "Git remote state",
    "Most-recent handoff",
)


def collect_remote_state():
    return None


def collect_state(repo_root, now):
    return {"remote_state": None}
'''
            (root / "scripts" / "session_orientation.py").write_text(drifted, encoding="utf-8")
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any("collect_state" in e.message for e in errors),
                f"expected collect_state wiring error, got {errors}",
            )

    def test_script_missing_fails_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _seed_baseline(root)
            (root / "scripts" / "session_orientation.py").unlink()
            errors = audit_orientation_freshness(root)
            self.assertTrue(
                any(e.artifact == "scripts/session_orientation.py" for e in errors),
                f"expected missing-script error, got {errors}",
            )


class TestOrientationFreshnessRealRepo(unittest.TestCase):
    """The live repo must pass — guards against false negatives in production."""

    def test_repo_root_passes_clean(self):
        repo_root = Path(__file__).resolve().parents[2]
        errors = audit_orientation_freshness(repo_root)
        self.assertEqual(
            errors,
            [],
            f"orientation freshness audit failing on live repo: {errors}",
        )


if __name__ == "__main__":
    unittest.main()
