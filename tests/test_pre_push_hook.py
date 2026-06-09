"""Tests for the pre-push gz-check hook declaration in .pre-commit-config.yaml.

Covers REQ-0.0.68-01-01 (pre-push gz check hook declared and version-controlled).
"""

import unittest
from pathlib import Path

import yaml


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore
        return obj

    return _identity


def _pre_push_gz_hooks() -> list[dict]:
    """Return all declared hooks with stages: [pre-push] whose entry runs gz check."""
    with Path(".pre-commit-config.yaml").open(encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    all_hooks = [hook for repo in config.get("repos", []) for hook in repo.get("hooks", [])]
    return [
        h
        for h in all_hooks
        if "pre-push" in (h.get("stages") or []) and "gz check" in h.get("entry", "")
    ]


class TestPrePushHookDeclared(unittest.TestCase):
    """REQ-0.0.68-01-01: .pre-commit-config.yaml declares a pre-push gz check hook."""

    @covers("REQ-0.0.68-01-01")
    def test_pre_push_hook_entry_exists(self) -> None:
        """A hook with stages: [pre-push] running gz check must be declared."""
        self.assertTrue(
            _pre_push_gz_hooks(),
            "Expected at least one hook with stages: [pre-push] whose entry contains 'gz check'",
        )

    @covers("REQ-0.0.68-01-01")
    def test_pre_push_hook_pass_filenames_false(self) -> None:
        """The pre-push gz check hook must not pass filenames (it runs the full suite)."""
        hooks = _pre_push_gz_hooks()
        self.assertTrue(hooks, "No pre-push gz check hook declared")
        for hook in hooks:
            self.assertFalse(
                hook.get("pass_filenames", True),
                f"Hook {hook.get('id', '?')} must have pass_filenames: false",
            )


if __name__ == "__main__":
    unittest.main()
