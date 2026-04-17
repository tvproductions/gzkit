"""CLI adapter layer for gzkit.

This package contains CLI-specific adapters — output formatting,
argument parsing helpers, and command wiring. It lives in the
adapter layer and may import from core/, ports/, and adapters/.

Symbols previously available as ``from gzkit.cli import X`` are
lazy-loaded via module-level ``__getattr__`` so ``gz --help`` does
not pay the cost of importing formatters, logging, progress, gates,
or audit internals until something actually uses them.
"""

from __future__ import annotations

from typing import Any

from gzkit.cli.main import main

__all__ = [
    "OutputFormatter",
    "bind_correlation_id",
    "configure_logging",
    "main",
    "progress_bar",
    "progress_phase",
    "progress_spinner",
]

_LAZY_ATTRS: dict[str, tuple[str, str]] = {
    "OutputFormatter": ("gzkit.cli.formatters", "OutputFormatter"),
    "bind_correlation_id": ("gzkit.cli.logging", "bind_correlation_id"),
    "configure_logging": ("gzkit.cli.logging", "configure_logging"),
    "progress_bar": ("gzkit.cli.progress", "progress_bar"),
    "progress_phase": ("gzkit.cli.progress", "progress_phase"),
    "progress_spinner": ("gzkit.cli.progress", "progress_spinner"),
    "_write_audit_artifacts": ("gzkit.commands.audit_cmd", "_write_audit_artifacts"),
    "_run_eval_delta": ("gzkit.commands.gates", "_run_eval_delta"),
    "_run_gate_1": ("gzkit.commands.gates", "_run_gate_1"),
    "_run_gate_2": ("gzkit.commands.gates", "_run_gate_2"),
    "_run_gate_3": ("gzkit.commands.gates", "_run_gate_3"),
    "_run_gate_4": ("gzkit.commands.gates", "_run_gate_4"),
    "_run_gate_5": ("gzkit.commands.gates", "_run_gate_5"),
    "gates_cmd": ("gzkit.commands.gates", "gates_cmd"),
    "GzCliError": ("gzkit.commands.common", "GzCliError"),
    "console": ("gzkit.commands.common", "console"),
    "ensure_initialized": ("gzkit.commands.common", "ensure_initialized"),
    "get_project_root": ("gzkit.commands.common", "get_project_root"),
    "load_manifest": ("gzkit.commands.common", "load_manifest"),
    "resolve_adr_file": ("gzkit.commands.common", "resolve_adr_file"),
    "resolve_target_adr": ("gzkit.commands.common", "resolve_target_adr"),
    "resolve_adr_lane": ("gzkit.ledger", "resolve_adr_lane"),
    "run_all_checks": ("gzkit.quality", "run_all_checks"),
    "run_command": ("gzkit.quality", "run_command"),
}


def __getattr__(name: str) -> Any:
    target = _LAZY_ATTRS.get(name)
    if target is None:
        raise AttributeError(f"module 'gzkit.cli' has no attribute {name!r}")
    module_path, attr = target
    from importlib import import_module

    module = import_module(module_path)
    value = getattr(module, attr)
    globals()[name] = value
    return value
