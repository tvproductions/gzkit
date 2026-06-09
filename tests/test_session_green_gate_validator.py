"""Tests for the session-green-gate validator (OBPI-0.0.68-02).

REQ-0.0.68-02-01: audit_session_green_gate exits 3 (returns errors) when no
pre-push gz check hook is declared; exits 0 (returns []) when declared; is
fail-closed for missing and unparseable .pre-commit-config.yaml.

REQ-0.0.68-02-02: --session-green-gate is part of the gz check default scope.
"""

import tempfile
import unittest
from pathlib import Path


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore
        return obj

    return _identity


_HOOK_WITH_PRE_PUSH = """\
repos:
  - repo: local
    hooks:
      - id: gz-check-pre-push
        name: gz check (pre-push gate)
        entry: uv run gz check
        language: system
        pass_filenames: false
        stages: [pre-push]
"""

_HOOK_WITHOUT_PRE_PUSH = """\
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff
        entry: uv run ruff check .
        language: system
        stages: [pre-commit]
"""

_INVALID_YAML = "key: [unclosed"


class TestAuditSessionGreenGateGreenPath(unittest.TestCase):
    """REQ-0.0.68-02-01: Returns [] when a pre-push gz check hook is declared."""

    @covers("REQ-0.0.68-02-01")
    def test_returns_empty_when_hook_declared(self) -> None:
        from gzkit.governance.trust_audits.session_green_gate import (
            audit_session_green_gate,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(_HOOK_WITH_PRE_PUSH, encoding="utf-8")
            errors = audit_session_green_gate(root)
        self.assertEqual(
            errors,
            [],
            "Expected no errors when a pre-push gz check hook is declared",
        )


class TestAuditSessionGreenGateRedPath(unittest.TestCase):
    """REQ-0.0.68-02-01: Returns ValidationError list when no pre-push gz check hook."""

    @covers("REQ-0.0.68-02-01")
    def test_returns_error_when_no_pre_push_hook(self) -> None:
        from gzkit.governance.trust_audits.session_green_gate import (
            audit_session_green_gate,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(_HOOK_WITHOUT_PRE_PUSH, encoding="utf-8")
            errors = audit_session_green_gate(root)
        self.assertTrue(errors, "Expected at least one ValidationError for missing hook")
        self.assertEqual(errors[0].type, "session_green_gate")

    @covers("REQ-0.0.68-02-01")
    def test_returns_error_when_config_missing(self) -> None:
        from gzkit.governance.trust_audits.session_green_gate import (
            audit_session_green_gate,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = audit_session_green_gate(root)
        self.assertTrue(errors, "Expected error for missing .pre-commit-config.yaml")
        self.assertEqual(errors[0].type, "session_green_gate")

    @covers("REQ-0.0.68-02-01")
    def test_returns_error_when_config_unparseable(self) -> None:
        from gzkit.governance.trust_audits.session_green_gate import (
            audit_session_green_gate,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(_INVALID_YAML, encoding="utf-8")
            errors = audit_session_green_gate(root)
        self.assertTrue(errors, "Expected error for unparseable .pre-commit-config.yaml")
        self.assertEqual(errors[0].type, "session_green_gate")

    @covers("REQ-0.0.68-02-01")
    def test_returns_error_when_repos_empty(self) -> None:
        from gzkit.governance.trust_audits.session_green_gate import (
            audit_session_green_gate,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text("repos: []\n", encoding="utf-8")
            errors = audit_session_green_gate(root)
        self.assertTrue(errors, "Expected error when repos list is empty")
        self.assertEqual(errors[0].type, "session_green_gate")


class TestSessionGreenGateInCheckScope(unittest.TestCase):
    """REQ-0.0.68-02-02: --session-green-gate is in the gz check default step list."""

    @covers("REQ-0.0.68-02-02")
    def test_session_green_gate_step_in_check_steps(self) -> None:
        from gzkit.commands.quality import _build_check_steps

        step_names = [name for name, _ in _build_check_steps()]
        self.assertIn(
            "Session green gate",
            step_names,
            "Expected 'Session green gate' step in gz check default scope",
        )


if __name__ == "__main__":
    unittest.main()
