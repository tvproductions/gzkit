"""Regression test for the settings.local backup vault escaping the repo (GHI #1071).

``scripts/settings_local_backup.py`` exists so that destroying a repository does
not destroy the operator's local settings with it. Its vault must therefore sit
OUTSIDE the repository root on every supported platform.

The original ``_vault`` built its slug with ``str(root).replace("/", "-")``.
``Path.__str__`` emits the platform separator, so on Windows the replacement
matched nothing and the slug kept both its backslashes and its drive letter.
``pathlib`` then treats a component carrying a drive as absolute and discards
everything to its left, collapsing
``Path.home() / ".claude" / "backups" / <slug> / "settings.local"`` to
``<repo>/settings.local`` — the backup written inside the thing it exists to
survive, with the real vault left empty.

The shaping is pure string work, so both platform cases are asserted here
without needing to run on either one.
"""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path, PureWindowsPath

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "settings_local_backup.py"


def _load_module():
    """Import the hook script by path; it is a script, not a package module."""
    spec = importlib.util.spec_from_file_location("settings_local_backup", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SettingsLocalVaultTests(unittest.TestCase):
    """The vault never lands inside the repository it protects."""

    def setUp(self) -> None:
        self.module = _load_module()

    def test_slug_carries_no_separator_or_drive_from_a_windows_root(self) -> None:
        """A Windows-shaped root must not leak separators or a drive into the slug.

        This is the actual defect. A slug containing a drive letter makes the
        joined path absolute, so the vault silently relocates into the repo.
        """
        root = PureWindowsPath(r"C:\Users\Jeff\source\repos\va\gzkit")
        slug = self.module._slug(root)

        self.assertNotIn("\\", slug)
        self.assertNotIn("/", slug)
        self.assertNotIn(":", slug)
        self.assertTrue(slug, "slug must not be empty")

    def test_slug_is_stable_for_a_posix_root(self) -> None:
        """The POSIX case is the control and must keep working."""
        slug = self.module._slug(Path("/home/jeff/src/gzkit"))

        self.assertNotIn("/", slug)
        self.assertNotIn(":", slug)
        self.assertIn("gzkit", slug)

    def test_vault_is_not_inside_the_repository_root(self) -> None:
        """The end-to-end property the hook's whole purpose depends on."""
        root = Path(__file__).resolve().parents[2]
        vault = self.module._vault(root)

        self.assertFalse(
            str(vault).startswith(str(root)),
            f"vault {vault} is inside the repository root {root}",
        )

    def test_distinct_roots_do_not_share_a_vault(self) -> None:
        """Two checkouts must not overwrite each other's snapshots."""
        a = self.module._vault(Path("/home/jeff/src/gzkit"))
        b = self.module._vault(Path("/home/jeff/other/gzkit"))

        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
