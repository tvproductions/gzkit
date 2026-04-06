"""Backward-compatibility shim for OBPI lock commands.

All lock logic has been extracted to ``gzkit.commands.obpi_lock`` (new)
and ``gzkit.lock_manager`` (data layer).  This module re-exports the
public command functions so that existing imports continue to work until
the OBPI-03 skill migration replaces all callers.
"""

from gzkit.commands.obpi_lock import (  # noqa: F401
    obpi_lock_check_cmd,
    obpi_lock_claim_cmd,
    obpi_lock_list_cmd,
    obpi_lock_release_cmd,
)

# Legacy alias — old code imports obpi_lock_status_cmd.
obpi_lock_status_cmd = obpi_lock_list_cmd
