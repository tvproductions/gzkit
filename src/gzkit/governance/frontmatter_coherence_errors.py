"""Typed exceptions for :mod:`gzkit.governance.frontmatter_coherence`.

Held apart from the reconcile module, which was over the 600-line module guidance then in
``.gzkit/rules/pythonic.md``.
"""


class ReceiptConstructionError(RuntimeError):
    """``reconcile_frontmatter`` reached its return without building a receipt."""

    def __init__(self) -> None:
        """Build the fixed construction-failure message."""
        super().__init__("reconcile_frontmatter: receipt construction failed")
