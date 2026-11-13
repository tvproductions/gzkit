"""The command bus and the query bus, stdlib only.

Each bus is built once, at start-up, by the configurator. Its registry fails fast:
construction refuses a bus when any message type the configurator expects has no
handler, so a missing handler is found when the program starts, never when a
request first reaches it (``docs/governance/hexagonal-architecture.md`` § Messages
and decorators). Cross-cutting work wraps the bus once, as middleware the
configurator chooses; the first middleware given is the outermost.
"""

from collections.abc import Callable, Iterable, Mapping, Sequence
from typing import Any

from gzkit.kernel.bases import Command, Query

__all__ = ["BusConfigurationError", "CommandBus", "Handler", "Middleware", "QueryBus"]

type Middleware = Callable[[object, Callable[[object], object]], object]
"""``(message, call_next) -> result``: work around one dispatch, then call the next layer."""

type Handler = Callable[[Any], object]
"""A handler's entry point. ``Any`` because a mapping cannot pair each key's type with its
handler's parameter; the registry pairs them, and construction checks each key."""


class BusConfigurationError(Exception):
    """The configurator wired a bus wrongly: a fault, raised at start-up."""


class _Bus[M: Command | Query]:
    """One message base's registry: exactly one handler per message type."""

    _message_base: type[Command | Query]

    def __init__(
        self,
        handlers: Mapping[type[M], Handler],
        *,
        expected: Iterable[type[M]],
        middleware: Sequence[Middleware] = (),
    ) -> None:
        """Build the registry, refusing it when it is incomplete or mistyped.

        Raises:
            BusConfigurationError: a key is not a message type of this bus, a handler
                cannot be called, or an expected message type has no handler.

        """
        base = self._message_base
        foreign = sorted(
            getattr(t, "__name__", repr(t))
            for t in handlers
            if not (isinstance(t, type) and issubclass(t, base))
        )
        if foreign:
            msg = f"{type(self).__name__} takes {base.__name__} types only; got {foreign}"
            raise BusConfigurationError(msg)
        uncallable = sorted(t.__name__ for t, handler in handlers.items() if not callable(handler))
        if uncallable:
            msg = f"{type(self).__name__}: the handler for {uncallable} cannot be called"
            raise BusConfigurationError(msg)
        missing = sorted(t.__name__ for t in expected if t not in handlers)
        if missing:
            msg = f"{type(self).__name__}: no handler for {missing}"
            raise BusConfigurationError(msg)
        self._handlers: dict[type[M], Handler] = dict(handlers)
        self._middleware = tuple(middleware)

    def dispatch(self, message: M) -> object:
        """Send *message* to its handler through the middleware.

        Returns:
            Whatever the handler returned: its result union's member.

        Raises:
            BusConfigurationError: no handler is registered for this message type,
                which a complete ``expected`` set rules out at start-up.

        """
        handler = self._handlers.get(type(message))
        if handler is None:
            msg = f"{type(self).__name__}: no handler for {type(message).__name__}"
            raise BusConfigurationError(msg)

        call: Callable[[object], object] = handler
        for layer in reversed(self._middleware):
            call = _wrap(layer, call)
        return call(message)


def _wrap(layer: Middleware, call_next: Callable[[object], object]) -> Callable[[object], object]:
    """Bind one middleware layer around the next.

    Returns:
        A callable that runs *layer* with *call_next* as its continuation.

    """

    def wrapped(message: object) -> object:
        return layer(message, call_next)

    return wrapped


class CommandBus(_Bus[Command]):
    """Routes each command to its one handler."""

    _message_base = Command


class QueryBus(_Bus[Query]):
    """Routes each query to its one handler."""

    _message_base = Query
