"""Typed parse-boundary errors for the governance subparser registrations."""

import argparse


class BlankTargetError(argparse.ArgumentTypeError):
    """A ``--target`` value was blank or whitespace-only."""

    def __init__(self) -> None:
        """Build the fixed message."""
        super().__init__("must name a non-empty file or region")
