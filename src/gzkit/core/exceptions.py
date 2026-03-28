"""Domain exception hierarchy with typed exit codes.

Exit code mapping follows the ADR Standard 4-Code Map:
  0 = Success
  1 = User/Config Error (ValidationError, ResourceNotFoundError, OperatorError, PermanentError)
  2 = System/IO Error (TransientError)
  3 = Policy Breach (PolicyBreachError)

The canonical base is ``GzkitError``.  ``GzError`` is retained as a
backward-compatibility alias.
"""


class GzkitError(Exception):
    """Base exception for all gzkit domain errors.

    Subclasses override ``exit_code`` only where the standard 4-code map
    requires a value other than 1.
    """

    @property
    def exit_code(self) -> int:
        """Return the CLI exit code for this error type."""
        return 1


# Backward-compatibility alias — existing callers may reference GzError.
GzError = GzkitError


# --- Exit code 1: User / Config Error ------------------------------------


class ValidationError(GzkitError):
    """Input or configuration validation failure."""

    @property
    def exit_code(self) -> int:
        """Return exit code 1 for user/config errors."""
        return 1


class ResourceNotFoundError(GzkitError):
    """A required file, ADR, OBPI, or governance resource was not found."""

    @property
    def exit_code(self) -> int:
        """Return exit code 1 for resource-not-found errors."""
        return 1


class PermanentError(GzkitError):
    """Non-retryable failure — data corruption, schema mismatch."""

    @property
    def exit_code(self) -> int:
        """Return exit code 1 for permanent errors."""
        return 1


class OperatorError(GzkitError):
    """Human-action-needed failure — config errors, permission issues."""

    @property
    def exit_code(self) -> int:
        """Return exit code 1 for operator errors."""
        return 1


# --- Exit code 2: System / IO Error --------------------------------------


class TransientError(GzkitError):
    """Retryable failure — network issues, temporary I/O errors."""

    @property
    def exit_code(self) -> int:
        """Return exit code 2 for system/IO errors."""
        return 2


# --- Exit code 3: Policy Breach ------------------------------------------


class PolicyBreachError(GzkitError):
    """Governance policy breach — exit code 3."""

    @property
    def exit_code(self) -> int:
        """Return exit code 3 for policy breaches."""
        return 3


# Backward-compatibility alias.
PolicyError = PolicyBreachError
