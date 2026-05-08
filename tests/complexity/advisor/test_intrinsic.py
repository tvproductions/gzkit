"""Tests for the @intrinsic_complexity decorator and registry (OBPI-0.0.29-07).

Coverage:
    REQ-0.0.29-07-01 — decorator registers (file_path, qualname) -> (reason, attestor, date).
    REQ-0.0.29-07-02 — decorator is a strict runtime no-op.
"""

from __future__ import annotations

import inspect
import unittest

from gzkit.complexity.advisor.intrinsic import (
    clear_registry,
    get_attestation,
    intrinsic_complexity,
)
from gzkit.traceability import covers


class TestIntrinsicComplexityDecorator(unittest.TestCase):
    def setUp(self) -> None:
        clear_registry()

    @covers("REQ-0.0.29-07-01")
    def test_registry_lookup_after_decoration(self) -> None:
        """Registry lookup returns (reason, attestor, date) after decoration."""

        @intrinsic_complexity(
            reason="irreducibly complex query optimizer", attestor="Test Attestor"
        )
        def complex_fn() -> int:
            return 42

        result = get_attestation(inspect.getfile(complex_fn), complex_fn.__qualname__)
        self.assertIsNotNone(result)
        reason, attestor, decoration_date = result  # type: ignore
        self.assertEqual(reason, "irreducibly complex query optimizer")
        self.assertEqual(attestor, "Test Attestor")
        self.assertRegex(decoration_date, r"^\d{4}-\d{2}-\d{2}$")

    @covers("REQ-0.0.29-07-01")
    def test_registry_keyed_by_file_and_qualname(self) -> None:
        """Registry is keyed by (inspect.getfile(fn), fn.__qualname__), not just name."""

        @intrinsic_complexity(reason="outer reason", attestor="Test Attestor")
        def shared_name() -> str:
            return "outer"

        outer_file = inspect.getfile(shared_name)
        outer_qualname = shared_name.__qualname__

        # Decorate a second function with the same local name in a nested scope
        # to produce a different __qualname__.
        def make_inner() -> object:
            @intrinsic_complexity(reason="inner reason", attestor="Test Attestor")
            def shared_name() -> str:  # noqa: F841
                return "inner"

            return shared_name

        inner_fn = make_inner()
        inner_file = inspect.getfile(inner_fn)  # type: ignore
        inner_qualname = inner_fn.__qualname__  # type: ignore

        outer_result = get_attestation(outer_file, outer_qualname)
        inner_result = get_attestation(inner_file, inner_qualname)

        # Both must be present and carry distinct reasons.
        self.assertIsNotNone(outer_result)
        self.assertIsNotNone(inner_result)
        self.assertNotEqual(outer_qualname, inner_qualname)
        self.assertEqual(outer_result[0], "outer reason")  # type: ignore
        self.assertEqual(inner_result[0], "inner reason")  # type: ignore

    @covers("REQ-0.0.29-07-02")
    def test_decorator_is_noop_at_runtime(self) -> None:
        """Decorated function returns the same result as before decoration."""

        def original() -> int:
            return 99

        decorated = intrinsic_complexity(reason="cc=24 optimizer", attestor="Test Attestor")(
            original
        )

        self.assertEqual(decorated(), 99)

    @covers("REQ-0.0.29-07-02")
    def test_decorator_does_not_modify_function_identity(self) -> None:
        """Decorated function is the identical object — __name__ and __qualname__ unchanged."""

        def my_function() -> None:
            """Docstring."""

        original_name = my_function.__name__
        original_qualname = my_function.__qualname__
        original_doc = my_function.__doc__

        decorated = intrinsic_complexity(reason="no-op test", attestor="Test Attestor")(my_function)

        # Identity: the decorator must return the exact same object.
        self.assertIs(decorated, my_function)
        self.assertEqual(decorated.__name__, original_name)
        self.assertEqual(decorated.__qualname__, original_qualname)
        self.assertEqual(decorated.__doc__, original_doc)

    @covers("REQ-0.0.29-07-01")
    def test_get_attestation_returns_none_for_unregistered(self) -> None:
        """get_attestation returns None for unregistered (file_path, qualname) pairs."""
        result = get_attestation("/nonexistent/path.py", "SomeClass.some_method")
        self.assertIsNone(result)

    @covers("REQ-0.0.29-07-01")
    def test_registry_isolation_via_clear(self) -> None:
        """clear_registry() removes all entries, enabling per-test isolation."""

        @intrinsic_complexity(reason="to be cleared", attestor="Test Attestor")
        def soon_cleared() -> None:
            pass

        file_path = inspect.getfile(soon_cleared)
        qualname = soon_cleared.__qualname__

        # Confirm the entry exists before clearing.
        self.assertIsNotNone(get_attestation(file_path, qualname))

        clear_registry()

        # After clear, the entry must be gone.
        self.assertIsNone(get_attestation(file_path, qualname))


if __name__ == "__main__":
    unittest.main()
