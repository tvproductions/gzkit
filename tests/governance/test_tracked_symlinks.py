"""No committed symlink may point outside the repository.

``uv build`` unpacks the sdist to build the wheel and refuses a symlink whose
target is absolute or escapes the tree ("external symlinks are not allowed").
v0.34.8 never reached PyPI because three Codex runtime symlinks to
``/opt/homebrew/bin/codex`` under ``.codex/tmp/`` were committed. The index is
checked, not the working tree: a clean checkout is what the release job builds.
"""

from __future__ import annotations

import posixpath
import subprocess
import tempfile
import unittest
from pathlib import Path, PurePosixPath

from tests.commands.common import _isolated_git_env

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        errors="replace",
        env=_isolated_git_env(),
    ).stdout


def _external_symlinks(root: Path) -> list[str]:
    """Return ``path -> target`` for every indexed symlink leaving the tree."""
    found = []
    for line in _git(root, "ls-files", "-s").splitlines():
        meta, path = line.split("\t", 1)
        mode, sha, _stage = meta.split()
        if mode != "120000":
            continue
        target = _git(root, "cat-file", "-p", sha)
        # Git stores link targets with '/', so resolve them as POSIX paths on every
        # host; os.path.normpath turns '../..' into '..\\..' on Windows.
        resolved = posixpath.normpath(f"{PurePosixPath(path).parent}/{target}")
        if PurePosixPath(target).is_absolute() or resolved.split("/")[0] == "..":
            found.append(f"{path} -> {target}")
    return found


class TestExternalSymlinkScan(unittest.TestCase):
    def test_flags_absolute_and_escaping_targets_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git(root, "init", "-q")
            # Symlinks are written straight into the index: os.symlink needs a
            # privilege Windows runners lack, and the scan reads only the index.
            links = {
                "sub/absolute": "/opt/homebrew/bin/codex",
                "sub/escaping": "../../outside",
                "sub/inside": "real.txt",
                "sub/inside_via_parent": "../sub/real.txt",
            }
            for path, target in links.items():
                sha = subprocess.run(
                    ["git", "-C", str(root), "hash-object", "-w", "--stdin"],
                    input=target,
                    check=True,
                    capture_output=True,
                    text=True,
                    errors="replace",
                    env=_isolated_git_env(),
                ).stdout.strip()
                _git(root, "update-index", "--add", "--cacheinfo", f"120000,{sha},{path}")

            self.assertEqual(
                sorted(_external_symlinks(root)),
                ["sub/absolute -> /opt/homebrew/bin/codex", "sub/escaping -> ../../outside"],
            )


class TestRepositoryHasNoExternalSymlinks(unittest.TestCase):
    def test_index_carries_no_external_symlink(self) -> None:
        self.assertEqual(_external_symlinks(_REPO_ROOT), [])


if __name__ == "__main__":
    unittest.main()
