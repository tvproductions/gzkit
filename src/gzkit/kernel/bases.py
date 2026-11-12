"""The bases a hexagon's types subclass, all frozen Pydantic models.

Each base belongs to one region of the hexagon, and the dependency checker refuses
a subclass outside it (``docs/governance/hexagonal-architecture.md`` § The
dependency rules): value objects, entities and domain events in the domain;
commands and queries in the driving ports; DTOs in either port package.

``create`` is the validating factory (principle E2): it returns the object, or a
``ValidationErrors`` value and never an invalid object. A subclass adds its own
rules by overriding ``create`` and calling the base's.
"""

from typing import Any, Self

import pydantic
from pydantic import BaseModel, ConfigDict

from gzkit.kernel.errors import ValidationErrors

__all__ = ["Command", "DomainEvent", "Dto", "Entity", "Query", "ValueObject"]


class _Frozen(BaseModel):
    """A frozen model that refuses unknown fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class _Created(_Frozen):
    """A frozen model built through its validating factory."""

    @classmethod
    def create(cls, **values: Any) -> Self | ValidationErrors:  # noqa: ANN401 - a factory takes each field's own type
        """Build the object, or return every refusal as a value.

        Returns:
            The validated object, or ``ValidationErrors`` naming each refused input.

        """
        try:
            return cls.model_validate(values)
        except pydantic.ValidationError as exc:
            return ValidationErrors.from_pydantic(exc)


class ValueObject(_Created):
    """A value defined by its fields alone; a rule about it is a method on its type."""


class Entity(_Created):
    """A domain object with identity, frozen: a change returns its new version.

    A change is a method that checks its rule, then returns the new version with
    the event it records (``_evolve`` builds the version).
    """

    def _evolve(self, **changes: Any) -> Self:  # noqa: ANN401 - each change takes its field's own type
        """Return a validated copy with *changes* applied.

        A refusal here is a fault, not an expected outcome: the calling method
        checks its rule before it evolves.

        Returns:
            The new version of this entity.

        """
        return type(self).model_validate({**dict(self), **changes})


class DomainEvent(_Frozen):
    """A fact an entity method records; the handler dispatches it, never the domain."""


class Command(_Created):
    """A request to change state, carrying primitives it validates in ``create``."""


class Query(_Created):
    """A request to read state, carrying primitives it validates in ``create``."""


class Dto(_Frozen):
    """Data carried across a port, checked for types only, with no ``create``."""
