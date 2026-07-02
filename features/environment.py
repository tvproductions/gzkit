"""Behave environment hooks for isolated BDD scenarios."""

from __future__ import annotations

import os

# Neutralize ambient color-forcing at environment-module import — which behave
# loads BEFORE any step module — so the pop lands ahead of the step files'
# ``from gzkit.cli import main``. That import constructs the module-level
# ``gzkit.commands.common.console`` singleton, which reads ``FORCE_COLOR`` once
# at import time and freezes ``force_terminal``. Modern terminals (Ghostty)
# export ``FORCE_COLOR=3``; left set, the frozen singleton emits ANSI SGR codes
# — color and bold — into behave's in-process captured output, breaking every
# plain-substring step assertion. A ``before_all`` hook is too late: the
# singleton is already frozen by then. This is the behave analog of
# ``tests/__init__.py`` popping FORCE_COLOR before ``unittest`` imports gzkit.
os.environ.pop("FORCE_COLOR", None)

import shutil  # noqa: E402
import tempfile  # noqa: E402
from pathlib import Path  # noqa: E402


def before_scenario(context, _scenario) -> None:
    """Run each scenario in an isolated temporary workspace."""
    context._original_cwd = Path.cwd()
    context._tmpdir = Path(tempfile.mkdtemp(prefix="gzkit-behave-"))
    os.chdir(context._tmpdir)


def after_scenario(context, _scenario) -> None:
    """Restore cwd, clean up the temporary workspace, and unset env overrides."""
    os.chdir(context._original_cwd)
    shutil.rmtree(context._tmpdir, ignore_errors=True)
    if hasattr(context, "_orig_arb_receipts_root"):
        if context._orig_arb_receipts_root is None:
            os.environ.pop("GZKIT_ARB_RECEIPTS_ROOT", None)
        else:
            os.environ["GZKIT_ARB_RECEIPTS_ROOT"] = context._orig_arb_receipts_root
