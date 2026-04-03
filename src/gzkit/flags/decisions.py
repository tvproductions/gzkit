"""FeatureDecisions — named decision methods over the flag system.

Maps raw flag keys to typed, documented decision methods. This is the ONLY
place in the codebase where flag key strings appear outside the registry.
Commands and workflows consume named decisions, never raw flag keys.

Implements ADR-0.0.8 checklist item #5.
"""

from __future__ import annotations

from gzkit.flags.registry import load_registry
from gzkit.flags.service import FlagService


class FeatureDecisions:
    """Named decision methods backed by the flag system.

    Consumers call decision methods (e.g. ``product_proof_enforced()``)
    instead of raw ``is_enabled("ops.product_proof")``.  This keeps flag
    key strings contained in one module and gives each toggle a clear
    behavioral docstring.
    """

    def __init__(self, svc: FlagService) -> None:
        """Initialize with a FlagService instance."""
        self._svc = svc

    def product_proof_enforced(self) -> bool:
        """Whether the product-proof check blocks OBPI closeout.

        True — closeout is blocked for OBPIs missing operator-facing docs.
        False — closeout warns but does not block.
        """
        return self._svc.is_enabled("ops.product_proof")


# Module-level singleton
_instance: FeatureDecisions | None = None


def get_decisions(svc: FlagService | None = None) -> FeatureDecisions:
    """Return the lazily-initialized FeatureDecisions singleton.

    On first call, *svc* must be provided (or a default FlagService is created
    from the on-disk registry).  Subsequent calls return the cached instance.
    """
    global _instance  # noqa: PLW0603
    if _instance is None:
        if svc is None:
            svc = FlagService(load_registry())
        _instance = FeatureDecisions(svc)
    return _instance


def _reset_decisions() -> None:
    """Reset the singleton (test-only)."""
    global _instance  # noqa: PLW0603
    _instance = None
