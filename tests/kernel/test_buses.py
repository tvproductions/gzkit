"""The buses fail fast at start-up and route each message through its middleware.

Read from `docs/governance/hexagonal-architecture.md` § Messages and decorators:
registries are built at start-up and fail fast on a missing handler; cross-cutting
work wraps the bus once, as middleware the configurator chooses.
"""

import unittest
from typing import TYPE_CHECKING

from gzkit.kernel import BusConfigurationError, Command, CommandBus, Query, QueryBus

if TYPE_CHECKING:
    from collections.abc import Callable


class Rename(Command):
    title: str


class Archive(Command):
    record_id: str


class Show(Query):
    record_id: str


class RegistryFailsFast(unittest.TestCase):
    def test_a_missing_expected_handler_refuses_construction(self) -> None:
        with self.assertRaises(BusConfigurationError) as caught:
            CommandBus({Rename: lambda _c: None}, expected=[Rename, Archive])
        self.assertIn("Archive", str(caught.exception))

    def test_a_complete_registry_builds(self) -> None:
        bus = CommandBus({Rename: lambda c: c.title}, expected=[Rename])
        self.assertEqual(bus.dispatch(Rename(title="t")), "t")

    def test_a_query_is_refused_on_the_command_bus(self) -> None:
        with self.assertRaises(BusConfigurationError):
            CommandBus({Show: lambda _q: None}, expected=[])  # ty: ignore[invalid-argument-type]

    def test_a_command_is_refused_on_the_query_bus(self) -> None:
        with self.assertRaises(BusConfigurationError):
            QueryBus({Rename: lambda _c: None}, expected=[])  # ty: ignore[invalid-argument-type]

    def test_an_unregistered_message_is_a_fault_at_dispatch(self) -> None:
        bus = CommandBus({Rename: lambda _c: None}, expected=[Rename])
        with self.assertRaises(BusConfigurationError):
            bus.dispatch(Archive(record_id="r1"))


class DispatchRoutesByType(unittest.TestCase):
    def test_each_message_reaches_its_own_handler(self) -> None:
        bus = QueryBus({Show: lambda q: f"shown {q.record_id}"}, expected=[Show])
        self.assertEqual(bus.dispatch(Show(record_id="r1")), "shown r1")

    def test_the_handler_result_is_returned_unchanged(self) -> None:
        sentinel = object()
        bus = CommandBus({Archive: lambda _c: sentinel}, expected=[Archive])
        self.assertIs(bus.dispatch(Archive(record_id="r1")), sentinel)


class MiddlewareWrapsTheBusOnce(unittest.TestCase):
    def test_the_first_middleware_is_outermost(self) -> None:
        calls: list[str] = []

        def layer(name: str) -> Callable[[object, Callable[[object], object]], object]:
            def run(message: object, call_next: Callable[[object], object]) -> object:
                calls.append(f"{name} in")
                result = call_next(message)
                calls.append(f"{name} out")
                return result

            return run

        def handle(_c: Rename) -> str:
            calls.append("handler")
            return "done"

        bus = CommandBus({Rename: handle}, expected=[Rename], middleware=[layer("a"), layer("b")])
        self.assertEqual(bus.dispatch(Rename(title="t")), "done")
        self.assertEqual(calls, ["a in", "b in", "handler", "b out", "a out"])

    def test_middleware_can_stop_a_dispatch(self) -> None:
        handled: list[object] = []

        def gate(_message: object, _call_next: Callable[[object], object]) -> object:
            return "refused"

        bus = CommandBus({Rename: handled.append}, expected=[Rename], middleware=[gate])
        self.assertEqual(bus.dispatch(Rename(title="t")), "refused")
        self.assertEqual(handled, [])


if __name__ == "__main__":
    unittest.main()
