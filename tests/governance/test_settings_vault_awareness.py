"""The settings vault has a witness, and gzkit agrees with the hook (GHI #1072).

``scripts/settings_local_backup.py`` writes snapshots of
``.claude/settings.local.json`` outside the repository. Until now nothing read
them, so the guarantee in its docstring had no mechanical witness: the vault
path was wrong on Windows for an unknown period (GHI #1071), every snapshot
landed inside the repo, the external vault was empty, and no check fired.

Two properties are covered here.

1. gzkit can report the vault's state: present and current, present and stale,
   or absent. Absence must be reported rather than passed over in silence,
   because absence is indistinguishable from "nobody looked".
2. gzkit's vault location AGREES with the hook's. The hook is deliberately
   stdlib-only and standalone -- "a backup failure must not cost the operator a
   session" -- so it must not import gzkit. Two implementations of one value
   are held in agreement by a coherence test, the same shape
   ``test_active_campaign_registry.py`` uses for the campaign pointer.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path, PureWindowsPath

from gzkit.settings_vault import VaultState, vault_dir, vault_slug, vault_status

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / "scripts" / "settings_local_backup.py"


def _load_hook():
    """Import the standalone hook by path so its slug can be compared."""
    spec = importlib.util.spec_from_file_location("settings_local_backup", HOOK)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VaultCoherenceTests(unittest.TestCase):
    """gzkit and the hook must compute the same vault, without sharing code."""

    def test_slug_agrees_with_the_hook_for_a_posix_root(self) -> None:
        root = Path("/home/jeff/src/gzkit")
        self.assertEqual(vault_slug(root), _load_hook()._slug(root))

    def test_slug_agrees_with_the_hook_for_a_windows_root(self) -> None:
        """The shape that broke in GHI #1071, pinned on both sides."""
        root = PureWindowsPath(r"C:\Users\Jeff\source\repos\va\gzkit")
        self.assertEqual(vault_slug(root), _load_hook()._slug(root))

    def test_vault_dir_agrees_with_the_hook(self) -> None:
        root = Path("/home/jeff/src/gzkit")
        self.assertEqual(vault_dir(root), _load_hook()._vault(root))

    def test_vault_is_never_inside_the_project_root(self) -> None:
        """The property the hook exists for, asserted from gzkit's side too."""
        self.assertFalse(str(vault_dir(REPO_ROOT)).startswith(str(REPO_ROOT)))


class VaultStatusTests(unittest.TestCase):
    """The three reportable states, each distinguishable from the others."""

    def _project(self, tmp: str, live_text: str | None) -> Path:
        root = Path(tmp) / "project"
        (root / ".claude").mkdir(parents=True)
        if live_text is not None:
            (root / ".claude" / "settings.local.json").write_text(
                live_text, encoding="utf-8", newline=""
            )
        return root

    def test_absent_vault_is_reported_not_silent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, json.dumps({"permissions": {}}))
            status = vault_status(root, vault_root=Path(tmp) / "vault")

            self.assertEqual(status.state, VaultState.ABSENT)
            self.assertEqual(status.snapshot_count, 0)
            self.assertTrue(status.message)

    def test_current_vault_reports_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body = json.dumps({"permissions": {"allow": ["Bash(ls)"]}})
            root = self._project(tmp, body)
            vault = Path(tmp) / "vault"
            vault.mkdir(parents=True)
            (vault / "settings.local.20260920T000000Z.json").write_text(
                body, encoding="utf-8", newline=""
            )

            status = vault_status(root, vault_root=vault)
            self.assertEqual(status.state, VaultState.CURRENT)
            self.assertEqual(status.snapshot_count, 1)

    def test_drifted_vault_reports_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, json.dumps({"permissions": {"allow": ["new"]}}))
            vault = Path(tmp) / "vault"
            vault.mkdir(parents=True)
            (vault / "settings.local.20260920T000000Z.json").write_text(
                json.dumps({"permissions": {"allow": ["old"]}}), encoding="utf-8", newline=""
            )

            status = vault_status(root, vault_root=vault)
            self.assertEqual(status.state, VaultState.DRIFTED)
            self.assertEqual(status.snapshot_count, 1)

    def test_no_live_file_with_snapshots_is_recoverable(self) -> None:
        """The restore case: the live file is gone but the vault held on."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp, None)
            vault = Path(tmp) / "vault"
            vault.mkdir(parents=True)
            (vault / "settings.local.20260920T000000Z.json").write_text(
                json.dumps({"permissions": {}}), encoding="utf-8", newline=""
            )

            status = vault_status(root, vault_root=vault)
            self.assertEqual(status.state, VaultState.RECOVERABLE)
            self.assertIn("settings.local.20260920T000000Z.json", status.message)


if __name__ == "__main__":
    unittest.main()
