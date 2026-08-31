"""Hook emitters derive their bytes from the root they are handed (GHI #909).

``sync_all(project_root)`` and every emitter it calls take an explicit root, so
each call site reads as though it fully determines the target. It did not. The
ruff normalization step shells out to ``uv run ruff format``, and ``uv run``
resolves ITS project from the process working directory — so the same root
produced different bytes depending on where the caller happened to be standing.

Measured 2026-08-28 at ``1fd8d6ec`` on a freshly initialized tree, syncing it
from inside itself and then from the gzkit repo: five generated hooks differed.
From the gzkit repo ``uv run`` finds ruff and formats; from the target tree it
tries to build that tree, fails, and the failure is swallowed by the emitter's
``suppress(...)`` — so the hooks are written unformatted and sync reports
success. Nothing at any call site could show that, which is the class of
failure: a function that accepts an explicit root and then consults ambient
state for part of its answer.

The property test needs a tree ``uv`` cannot build, because that is the only
condition under which the two directions diverge — a tree ``uv`` handles from
anywhere formats identically from anywhere, and a fixture like that would be
green for the wrong reason. The fixture therefore names a build backend that
does not exist, with no requirements to resolve, so the failure is local,
offline, and immediate rather than a network timeout.
"""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.config import GzkitConfig
from gzkit.hooks.claude import setup_claude_hooks

GZKIT_REPO = Path(__file__).resolve().parents[2]

# A syntactically valid project that uv can never build: the backend does not
# exist and nothing needs resolving, so `uv run` fails locally in milliseconds.
UNBUILDABLE_PYPROJECT = """\
[project]
name = "probe-tree"
version = "0.1.0"

[build-system]
requires = []
build-backend = "gzkit_no_such_backend"

[tool.ruff]
line-length = 100
"""


def _emit_all_hooks(project_root: Path, config: GzkitConfig, *, standing_in: Path) -> None:
    """Emit every hook into ``project_root`` while standing in ``standing_in``."""
    previous = Path.cwd()
    os.chdir(standing_in)
    try:
        setup_claude_hooks(project_root, config)
    finally:
        os.chdir(previous)


def _hook_bytes(project_root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(project_root).as_posix(): path.read_bytes()
        for path in sorted(project_root.rglob("*.py"))
    }


class TestHookEmitterRootBinding(unittest.TestCase):
    """The synced root, not the caller's shell, decides the emitted bytes."""

    def test_emitted_hooks_are_identical_from_inside_and_outside_the_tree(self) -> None:
        """Two callers passing the same root get the same bytes."""
        config = GzkitConfig()
        with tempfile.TemporaryDirectory(prefix="gzkit-root-binding-") as name:
            root = Path(name).resolve()
            (root / "pyproject.toml").write_text(UNBUILDABLE_PYPROJECT, encoding="utf-8")

            _emit_all_hooks(root, config, standing_in=root)
            from_inside = _hook_bytes(root)
            _emit_all_hooks(root, config, standing_in=GZKIT_REPO)
            from_outside = _hook_bytes(root)

        self.assertEqual(
            sorted(from_inside),
            sorted(from_outside),
            "the same root emitted a different set of hook files from a different cwd",
        )
        drifted = sorted(n for n in from_inside if from_inside[n] != from_outside[n])
        self.assertEqual(
            drifted,
            [],
            f"hook bytes depend on the caller's working directory, not the synced root: {drifted}",
        )

    def test_formatter_subprocess_is_bound_to_the_synced_root(self) -> None:
        """The mechanism: ruff resolves against the target tree, not ambient cwd."""
        config = GzkitConfig()
        with tempfile.TemporaryDirectory(prefix="gzkit-root-binding-") as name:
            root = Path(name).resolve()
            (root / "pyproject.toml").write_text(UNBUILDABLE_PYPROJECT, encoding="utf-8")
            with mock.patch.object(subprocess, "run", wraps=subprocess.run) as run:
                _emit_all_hooks(root, config, standing_in=GZKIT_REPO)

            observed = [call.kwargs.get("cwd") for call in run.call_args_list]
            self.assertTrue(observed, "no formatter subprocess ran; the seam moved")
            self.assertEqual(
                [cwd for cwd in observed if cwd != root],
                [],
                "a formatter subprocess inherited the caller's cwd instead of the synced root",
            )


if __name__ == "__main__":
    unittest.main()
