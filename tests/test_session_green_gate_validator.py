"""Tests for the session-green-gate validator (OBPI-0.0.68-02).

REQ-0.0.68-02-01: audit_session_green_gate exits 3 (returns errors) when no
pre-push gz check hook is declared; exits 0 (returns []) when declared; is
fail-closed for missing and unparseable .pre-commit-config.yaml.

REQ-0.0.68-02-02: --session-green-gate is part of the gz check default scope.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.traceability import covers

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

_HOOK_PRE_PUSH_CHECK_CONFIG_PATHS = """\
repos:
  - repo: local
    hooks:
      - id: gz-check-config-paths-pre-push
        name: gz check-config-paths (pre-push)
        entry: uv run gz check-config-paths
        language: system
        pass_filenames: false
        stages: [pre-push]
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
    def test_returns_error_when_only_hook_is_check_config_paths(self) -> None:
        # A pre-push hook running `gz check-config-paths` must NOT satisfy the
        # gate — only `gz check` does. Guards the un-removability guarantee
        # against a check-prefixed sibling verb false-passing the floor (#600).
        from gzkit.governance.trust_audits.session_green_gate import (
            audit_session_green_gate,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(
                _HOOK_PRE_PUSH_CHECK_CONFIG_PATHS, encoding="utf-8"
            )
            errors = audit_session_green_gate(root)
        self.assertTrue(
            errors,
            "Expected error: a pre-push 'gz check-config-paths' hook is not a 'gz check' gate",
        )
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


class SessionGreenGateDelivery(unittest.TestCase):
    """A declared pre-push hook must also be DELIVERED into the worktree.

    The declaration arm alone let a live regression through: this repo's
    .pre-commit-config.yaml declared gz-check-pre-push correctly while
    .git/hooks/ held only stock samples, because a local `core.hooksPath`
    setting made `pre-commit install` refuse. Every commit and push ran
    with zero enforcement and --session-green-gate stayed green throughout.
    Verifying the declaration is not verifying the gate.
    """

    def _worktree(self, root: Path, *, hooks_dir_name: str = "hooks") -> Path:
        (root / ".pre-commit-config.yaml").write_text(_HOOK_WITH_PRE_PUSH, encoding="utf-8")
        hooks = root / ".git" / hooks_dir_name
        hooks.mkdir(parents=True, exist_ok=True)
        return hooks

    def test_declared_but_not_installed_is_a_violation(self) -> None:
        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._worktree(root)  # .git/hooks exists but holds no pre-push
            errors = audit_session_green_gate(root, check_delivery=True)

        self.assertEqual(len(errors), 1, f"undelivered gate must fail closed, got {errors}")
        self.assertIn("not installed", errors[0].message)

    def test_declared_and_installed_passes(self) -> None:
        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hooks = self._worktree(root)
            (hooks / "pre-push").write_text(
                "#!/usr/bin/env bash\n# start templated\nINSTALL_PYTHON=...\n"
                "exec pre-commit hook-impl --hook-type=pre-push\n",
                encoding="utf-8",
            )
            self.assertEqual(audit_session_green_gate(root, check_delivery=True), [])

    def test_foreign_pre_push_hook_is_a_violation(self) -> None:
        """A pre-push file that is not the pre-commit shim does not deliver the gate."""
        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            hooks = self._worktree(root)
            (hooks / "pre-push").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            errors = audit_session_green_gate(root, check_delivery=True)

        self.assertEqual(len(errors), 1, f"non-pre-commit shim must fail, got {errors}")

    def test_hooks_path_redirect_is_followed(self) -> None:
        """core.hooksPath redirection must be honored, not assumed to be .git/hooks."""
        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._worktree(root)
            elsewhere = root / "custom-hooks"
            elsewhere.mkdir()
            (elsewhere / "pre-push").write_text(
                "exec pre-commit hook-impl --hook-type=pre-push\n", encoding="utf-8"
            )
            (root / ".git" / "config").write_text(
                f"[core]\n\thooksPath = {elsewhere.as_posix()}\n", encoding="utf-8"
            )
            self.assertEqual(audit_session_green_gate(root, check_delivery=True), [])

    def test_non_git_tree_skips_delivery_arm(self) -> None:
        """Fixture trees and exports carry no .git — delivery is not assertable there."""
        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(_HOOK_WITH_PRE_PUSH, encoding="utf-8")
            self.assertEqual(audit_session_green_gate(root, check_delivery=True), [])

    def test_delivery_arm_is_off_by_default(self) -> None:
        """Default call shape is unchanged, so CI and existing callers do not break."""
        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._worktree(root)  # declared, not installed
            self.assertEqual(audit_session_green_gate(root), [])

    def test_missing_declaration_still_fails_when_delivery_checked(self) -> None:
        """The delivery arm supplements the declaration arm; it does not replace it."""
        from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".pre-commit-config.yaml").write_text(_HOOK_WITHOUT_PRE_PUSH, encoding="utf-8")
            (root / ".git" / "hooks").mkdir(parents=True)
            errors = audit_session_green_gate(root, check_delivery=True)

        self.assertEqual(len(errors), 1)
        self.assertIn("declared", errors[0].message)
