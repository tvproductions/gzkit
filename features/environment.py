"""Behave environment hooks for isolated BDD scenarios."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


def before_scenario(context, _scenario) -> None:  # type: ignore[no-untyped-def]
    """Run each scenario in an isolated temporary workspace."""
    context._original_cwd = Path.cwd()
    context._tmpdir = Path(tempfile.mkdtemp(prefix="gzkit-behave-"))
    os.chdir(context._tmpdir)


def after_scenario(context, _scenario) -> None:  # type: ignore[no-untyped-def]
    """Restore cwd and clean up the temporary workspace."""
    os.chdir(context._original_cwd)
    shutil.rmtree(context._tmpdir, ignore_errors=True)
