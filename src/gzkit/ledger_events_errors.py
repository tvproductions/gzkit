"""Typed ledger-event construction failures (RO-9, TRY003).

Kept beside :mod:`gzkit.ledger_events` because that module is over the
authoring-time module size limit (``.gzkit/rules/pythonic.md``).
"""


class RetirementFloorOverlapError(ValueError):
    """A corpus retirement names the same invariant id as both revived and un-bound."""

    def __init__(self, overlap: set[str]) -> None:
        """Build the message from ``overlap``."""
        self.overlap = sorted(overlap)
        super().__init__(
            f"floor_added and floor_removed overlap on {sorted(overlap)}: a retirement "
            "cannot both revive and un-bind the same invariant entry. The two sets come "
            "from one before/after fold and are disjoint by construction."
        )
