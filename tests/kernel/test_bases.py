"""The kernel's bases and error values hold the specification's construction rules.

Each assertion is read from `docs/governance/hexagonal-architecture.md`: frozen
models that refuse unknown fields; `create` returns the object or a
`ValidationErrors` value, never an invalid object (E2); an entity change returns
a new version (frozen entities); a DTO has no `create`.
"""

import unittest

import pydantic
from pydantic import Field

from gzkit.kernel import (
    Command,
    DomainEvent,
    Dto,
    Entity,
    ErrorValue,
    NotFound,
    PersistenceFailure,
    Query,
    RuleViolation,
    ValidationErrors,
    ValueObject,
)


class Semver(ValueObject):
    major: int = Field(..., ge=0)
    minor: int = Field(..., ge=0)


class Renamed(DomainEvent):
    old: str
    new: str


class Record(Entity):
    record_id: str
    title: str = Field(..., min_length=1)

    def rename(self, title: str) -> tuple[Record, Renamed] | RuleViolation:
        if title == self.title:
            return RuleViolation(message="the title is unchanged")
        return self._evolve(title=title), Renamed(old=self.title, new=title)


class Rename(Command):
    record_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)


class Show(Query):
    record_id: str = Field(..., min_length=1)


class RecordView(Dto):
    record_id: str
    title: str


class CreateReturnsTheObjectOrItsRefusals(unittest.TestCase):
    def test_valid_input_returns_the_object(self) -> None:
        result = Semver.create(major=1, minor=2)
        self.assertEqual(result, Semver(major=1, minor=2))

    def test_invalid_input_returns_every_refusal_as_a_value(self) -> None:
        result = Semver.create(major=-1, minor="x")
        self.assertIsInstance(result, ValidationErrors)
        assert isinstance(result, ValidationErrors)
        self.assertEqual({e.location for e in result.errors}, {("major",), ("minor",)})
        self.assertIn("2 inputs refused", result.message)

    def test_an_unknown_field_is_refused(self) -> None:
        result = Rename.create(record_id="r1", title="t", extra="no")
        self.assertIsInstance(result, ValidationErrors)
        assert isinstance(result, ValidationErrors)
        self.assertEqual([e.location for e in result.errors], [("extra",)])

    def test_commands_and_queries_validate_their_primitives(self) -> None:
        self.assertIsInstance(Rename.create(record_id="", title="t"), ValidationErrors)
        self.assertIsInstance(Show.create(record_id=""), ValidationErrors)
        self.assertEqual(Show.create(record_id="r1"), Show(record_id="r1"))

    def test_create_never_raises_on_a_refusal(self) -> None:
        try:
            result = Semver.create()
        except pydantic.ValidationError:  # pragma: no cover - the failure this test exists to catch
            self.fail("create raised instead of returning ValidationErrors")
        self.assertIsInstance(result, ValidationErrors)
        assert isinstance(result, ValidationErrors)
        self.assertTrue(result.errors)


class EveryBaseIsFrozen(unittest.TestCase):
    def test_no_base_allows_assignment(self) -> None:
        instances = [
            Semver(major=1, minor=0),
            Record(record_id="r1", title="t"),
            Renamed(old="a", new="b"),
            Rename(record_id="r1", title="t"),
            Show(record_id="r1"),
            RecordView(record_id="r1", title="t"),
            NotFound(message="m"),
        ]
        for instance in instances:
            with self.subTest(type(instance).__name__), self.assertRaises(pydantic.ValidationError):
                instance.title = "changed"  # type: ignore[misc, ty:invalid-assignment]

    def test_event_and_dto_refuse_unknown_fields(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            Renamed(old="a", new="b", extra=1)  # type: ignore[call-arg, ty:unknown-argument]
        with self.assertRaises(pydantic.ValidationError):
            RecordView(record_id="r1", title="t", extra=1)  # type: ignore[call-arg, ty:unknown-argument]


class EntityChangesReturnANewVersion(unittest.TestCase):
    def test_a_change_returns_the_new_version_and_its_event(self) -> None:
        before = Record(record_id="r1", title="old")
        result = before.rename("new")
        self.assertIsInstance(result, tuple)
        assert isinstance(result, tuple)
        after, event = result
        self.assertEqual(after, Record(record_id="r1", title="new"))
        self.assertEqual(event, Renamed(old="old", new="new"))
        self.assertEqual(before.title, "old")

    def test_a_refused_change_is_a_value(self) -> None:
        result = Record(record_id="r1", title="same").rename("same")
        self.assertIsInstance(result, RuleViolation)

    def test_evolve_revalidates_the_new_version(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            Record(record_id="r1", title="t")._evolve(title="")


class DtoAndEventHaveNoFactory(unittest.TestCase):
    def test_dto_and_event_carry_no_create(self) -> None:
        self.assertFalse(hasattr(Dto, "create"))
        self.assertFalse(hasattr(DomainEvent, "create"))


class ErrorValues(unittest.TestCase):
    def test_the_named_variants_are_error_values(self) -> None:
        for kind in (NotFound, RuleViolation, PersistenceFailure, ValidationErrors):
            with self.subTest(kind.__name__):
                self.assertTrue(issubclass(kind, ErrorValue))

    def test_an_error_needs_a_message(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            NotFound(message="")

    def test_validation_errors_is_never_empty(self) -> None:
        with self.assertRaises(pydantic.ValidationError):
            ValidationErrors(message="m", errors=())

    def test_one_refusal_reads_singular(self) -> None:
        result = Show.create(record_id="")
        assert isinstance(result, ValidationErrors)
        self.assertIn("1 input refused", result.message)


if __name__ == "__main__":
    unittest.main()
