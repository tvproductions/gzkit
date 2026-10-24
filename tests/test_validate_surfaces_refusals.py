"""Each refusal ``gz validate --surfaces`` makes fails a test when it is removed.

A one-guard-at-a-time removal sweep (2026-10-14, ``60b994228``) found five
refusals in :func:`gzkit.validate_pkg.surface.validate_surfaces` that the whole
unit suite stayed green without (GHI #1212 to #1216). Every case here builds the
violation in a temporary project and asserts the finding the refusal owes, with
a clean control beside it so a check that reports on every tree cannot pass.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.core.validation_rules import ValidationError
from gzkit.schemas import load_schema
from gzkit.validate_pkg.surface import validate_surfaces

_REQUIRED_HEADERS: list[str] = load_schema("agents")["required_headers"]


def _agents_md(headers: list[str]) -> str:
    return "# AGENTS.md\n\n" + "".join(f"## {h}\n\nBody.\n\n" for h in headers)


def _surface_messages(root: Path, path: Path) -> list[str]:
    """The ``surface`` findings reported against *path*, parity check off."""
    return [
        e.message
        for e in validate_surfaces(root, check_sync_parity=False)
        if e.type == "surface" and e.artifact == str(path)
    ]


class TestAgentsMdPresence(unittest.TestCase):
    """GHI #1212: a project with no AGENTS.md is reported."""

    def test_missing_agents_md_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                _surface_messages(root, root / "AGENTS.md"), ["AGENTS.md does not exist"]
            )

    def test_complete_agents_md_is_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "AGENTS.md").write_text(_agents_md(_REQUIRED_HEADERS), encoding="utf-8")
            self.assertEqual(_surface_messages(root, root / "AGENTS.md"), [])


class TestAgentsMdRequiredHeaders(unittest.TestCase):
    """GHI #1213: each schema-required header absent from AGENTS.md is reported."""

    def test_each_missing_required_header_is_reported_by_name(self) -> None:
        self.assertGreater(len(_REQUIRED_HEADERS), 1, "schema must require headers")
        for missing in _REQUIRED_HEADERS:
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                present = [h for h in _REQUIRED_HEADERS if h != missing]
                (root / "AGENTS.md").write_text(_agents_md(present), encoding="utf-8")
                errors = [
                    e
                    for e in validate_surfaces(root, check_sync_parity=False)
                    if e.artifact == str(root / "AGENTS.md")
                ]
                self.assertEqual([e.field for e in errors], [missing])


class TestClaudeMdPresence(unittest.TestCase):
    """GHI #1214: a project with no CLAUDE.md is reported."""

    def test_missing_claude_md_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(
                _surface_messages(root, root / "CLAUDE.md"), ["CLAUDE.md does not exist"]
            )

    def test_present_claude_md_is_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
            self.assertEqual(_surface_messages(root, root / "CLAUDE.md"), [])


class TestHooksWithoutSettings(unittest.TestCase):
    """GHI #1215: a hooks directory without .claude/settings.json is reported."""

    def _settings_messages(self, root: Path) -> list[str]:
        return _surface_messages(root, root / ".claude" / "settings.json")

    def test_hooks_without_settings_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".claude" / "hooks").mkdir(parents=True)
            self.assertEqual(
                self._settings_messages(root),
                ["Hooks directory exists but settings.json is missing"],
            )

    def test_hooks_with_settings_is_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".claude" / "hooks").mkdir(parents=True)
            (root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
            self.assertEqual(self._settings_messages(root), [])

    def test_no_hooks_and_no_settings_is_not_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self._settings_messages(Path(tmp)), [])


class TestSyncParityIsConsulted(unittest.TestCase):
    """GHI #1216: ``check_sync_parity`` decides whether parity findings are reported.

    The parity comparison itself is exercised against a real ``gz init`` tree in
    ``tests/test_validate_sync_parity.py``; what no test held was that
    ``validate_surfaces`` calls it. The stand-in returns a known drift finding,
    so the assertion is about the wiring, not about any one drift shape.
    """

    _DRIFT = ValidationError(type="surface", artifact="AGENTS.md", message="parity drift probe")

    def _run(self, *, check_sync_parity: bool) -> tuple[list[ValidationError], int]:
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch(
                "gzkit.validate_pkg.sync_parity.check_sync_parity", return_value=[self._DRIFT]
            ) as parity,
        ):
            errors = validate_surfaces(Path(tmp), check_sync_parity=check_sync_parity)
            return errors, parity.call_count

    def test_parity_drift_is_reported_when_enabled(self) -> None:
        errors, calls = self._run(check_sync_parity=True)
        self.assertEqual(calls, 1)
        self.assertIn(self._DRIFT, errors)

    def test_parity_is_not_run_when_disabled(self) -> None:
        errors, calls = self._run(check_sync_parity=False)
        self.assertEqual(calls, 0)
        self.assertNotIn(self._DRIFT, errors)


if __name__ == "__main__":
    unittest.main()
