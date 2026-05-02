"""Behave environment hooks for isolated BDD scenarios."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


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
