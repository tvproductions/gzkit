"""Typed exceptions for :mod:`gzkit.foundation.sunset_migrate`.

Held apart from the migration module, which is over the module-size guidance in
``.gzkit/rules/pythonic.md``.
"""


class PartitionNotBijectionError(RuntimeError):
    """The foundation partition does not map one row to each on-disk package."""

    def __init__(self, row_count: int, package_count: int) -> None:
        """Name both counts."""
        self.row_count = row_count
        self.package_count = package_count
        super().__init__(
            f"BLOCKERS: partition is not a bijection with on-disk packages "
            f"({row_count} rows vs {package_count} packages)"
        )


class ApplyAttestationMissingError(ValueError):
    """An applying migration was requested without an attestor and attestation text."""

    def __init__(self) -> None:
        """Build the fixed missing-witness message."""
        super().__init__(
            "--apply requires a non-empty attestor AND attestation text. The Gate-5 "
            "human attestation IS the terminality witness for pre-ledger foundations; "
            "emitting these events without it would fabricate the witness."
        )
