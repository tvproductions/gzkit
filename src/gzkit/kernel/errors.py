"""Error values: expected failures returned as values, never raised (principle C2).

Each type is one member a handler's result union may carry. The four named here
are the variants the specification names (``docs/governance/hexagonal-architecture.md``
§ Testing): a validation failure, not found, a business-rule violation and a
persistence failure. A fault is still an exception and propagates uncaught.
"""

from typing import Self

import pydantic
from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "ErrorValue",
    "FieldError",
    "NotFound",
    "PersistenceFailure",
    "RuleViolation",
    "ValidationErrors",
]


class ErrorValue(BaseModel):
    """Base of every error value: frozen, with a message for its reader."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    message: str = Field(..., min_length=1, description="What failed, for the reader")


class FieldError(BaseModel):
    """One refused input: where it sits and why it was refused."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    location: tuple[str | int, ...] = Field(..., description="Path to the refused input")
    message: str = Field(..., min_length=1, description="Why the input was refused")


class ValidationErrors(ErrorValue):
    """Every refusal a factory found, returned instead of an invalid object (E2)."""

    errors: tuple[FieldError, ...] = Field(..., min_length=1, description="Each refusal")

    @classmethod
    def from_pydantic(cls, exc: pydantic.ValidationError) -> Self:
        """Translate a Pydantic refusal into an error value, one entry per refusal.

        Returns:
            The error value carrying every refusal *exc* reported.

        """
        errors = tuple(
            FieldError(location=tuple(item["loc"]), message=item["msg"]) for item in exc.errors()
        )
        count = len(errors)
        noun = "input" if count == 1 else "inputs"
        return cls(message=f"{exc.title}: {count} {noun} refused", errors=errors)


class NotFound(ErrorValue):
    """The thing asked for does not exist."""


class RuleViolation(ErrorValue):
    """A business rule refused the change."""


class PersistenceFailure(ErrorValue):
    """A driven adapter could not store or read what the handler needed."""
