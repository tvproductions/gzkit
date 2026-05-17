"""Validation hook entrypoint — re-exports ADR-0.0.33 hook wiring (OBPI-0.0.34-06)."""

from . import hooks
from .hooks import FidelityHookError, validate_render, validate_save

__all__ = ["FidelityHookError", "hooks", "validate_render", "validate_save"]
