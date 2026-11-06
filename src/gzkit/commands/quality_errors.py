"""Typed errors for the quality commands (``quality.py``)."""


class MalformedObpiIdError(ValueError):
    """An OBPI id does not parse as ``OBPI-<semver>-<item>``."""

    def __init__(self, obpi: str) -> None:
        """Build the message from *obpi*."""
        self.obpi = obpi
        super().__init__(f"Expected OBPI-<semver>-<item> form, got {obpi!r}")
