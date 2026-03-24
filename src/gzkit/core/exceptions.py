"""Domain exception hierarchy with retryability-oriented classification.

Exit code mapping follows the ADR Standard 4-Code Map:
  0 = Success
  1 = User/Config Error (PermanentError, OperatorError)
  2 = System/IO Error (TransientError)
  3 = Policy Breach (PolicyError)
"""


class GzError(Exception):
    """Base exception for all gzkit domain errors."""

    @property
    def exit_code(self) -> int:
        """Return the CLI exit code for this error type."""
        return 1


class TransientError(GzError):
    """Retryable failure — network issues, temporary I/O errors."""

    @property
    def exit_code(self) -> int:
        return 2


class PermanentError(GzError):
    """Non-retryable failure — data corruption, schema mismatch."""

    @property
    def exit_code(self) -> int:
        return 1


class OperatorError(GzError):
    """Human-action-needed failure — config errors, permission issues."""

    @property
    def exit_code(self) -> int:
        return 1


class PolicyError(GzError):
    """Governance policy breach — exit code 3."""

    @property
    def exit_code(self) -> int:
        return 3
