"""Typed errors for the ``gz init`` / ``gz prd`` / ``gz constitute`` commands (``init_cmd.py``)."""


class InvalidPrdSlugError(SystemExit):
    """A PRD name yields no alphanumeric slug."""

    def __init__(self, name: str) -> None:
        """Build the message from *name*."""
        self.name = name
        super().__init__(f"Invalid PRD slug: {name!r} (need at least one alphanumeric character)")


class InvalidConstitutionSlugError(SystemExit):
    """A constitution name yields no alphanumeric slug."""

    def __init__(self, name: str) -> None:
        """Build the message from *name*."""
        self.name = name
        super().__init__(
            f"Invalid constitution slug: {name!r} (need at least one alphanumeric character)"
        )
