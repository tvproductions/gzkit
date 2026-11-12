"""The kernel: the building blocks a hexagon is built on, for gzkit and its adopters.

A sibling of ``core/`` that imports stdlib and Pydantic only and holds no gzkit
governance concept (``docs/governance/hexagonal-architecture.md`` § The packages).
The name ``kernel`` is a draft, held open by the hexagonal specification run until
its diamond 2 (RP-15 tranche 6, ruled 2026-11-12).
"""

from gzkit.kernel.bases import Command, DomainEvent, Dto, Entity, Query, ValueObject
from gzkit.kernel.buses import BusConfigurationError, CommandBus, Handler, Middleware, QueryBus
from gzkit.kernel.errors import (
    ErrorValue,
    FieldError,
    NotFound,
    PersistenceFailure,
    RuleViolation,
    ValidationErrors,
)

__all__ = [
    "BusConfigurationError",
    "Command",
    "CommandBus",
    "DomainEvent",
    "Dto",
    "Entity",
    "ErrorValue",
    "FieldError",
    "Handler",
    "Middleware",
    "NotFound",
    "PersistenceFailure",
    "Query",
    "QueryBus",
    "RuleViolation",
    "ValidationErrors",
    "ValueObject",
]
