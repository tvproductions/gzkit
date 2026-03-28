"""CLI adapter layer for gzkit.

This package contains CLI-specific adapters — output formatting,
argument parsing helpers, and command wiring. It lives in the
adapter layer and may import from core/, ports/, and adapters/.

All symbols previously available as ``from gzkit.cli import X``
are re-exported from ``gzkit.cli.main`` so existing imports are
unchanged.
"""

from gzkit.cli.formatters import OutputFormatter
from gzkit.cli.logging import bind_correlation_id, configure_logging
from gzkit.cli.main import *  # noqa: F401, F403
from gzkit.cli.progress import progress_bar, progress_phase, progress_spinner

# Re-export private names that existing tests import directly.
from gzkit.commands.audit_cmd import _write_audit_artifacts  # noqa: F401
from gzkit.commands.gates import (  # noqa: F401
    _run_gate_1,
    _run_gate_2,
    _run_gate_3,
    _run_gate_4,
    _run_gate_5,
    gates_cmd,
)

__all__ = [
    "OutputFormatter",
    "bind_correlation_id",
    "configure_logging",
    "progress_bar",
    "progress_phase",
    "progress_spinner",
]
