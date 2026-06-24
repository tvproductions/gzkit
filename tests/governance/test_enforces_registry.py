"""Tests for @enforces decorator and enforcement claim registry (OBPI-0.0.74-15).

Validates claim id format checking at decoration time, known-claims existence
validation, EnforcementClaimRecord registration, metadata-only behavior on
decorated callables, and the structural fence (single enforcement-claim surface).
"""

from __future__ import annotations

import functools
import unittest
from typing import Any

from gzkit.enforcement import (
    EnforcementClaimRecord,
    enforces,
    get_enforcement_registry,
    registered_claims,
    reset_enforcement_registry,
    set_known_claims,
)
from gzkit.traceability import covers

_TEST_CLAIMS = frozenset({"lint", "format", "typecheck", "test"})


class TestEnforcesRegistration(unittest.TestCase):
    """@enforces registers an EnforcementClaimRecord; registry is queryable (REQ-15-01)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-15-01")
    def test_registration_appends_record(self) -> None:
        def _fixture() -> str:
            return "violation"

        def _entrypoint(v: str) -> list[Any]:
            return []

        @enforces("lint", _fixture, _entrypoint)
        def _marker() -> None:
            pass

        registry = get_enforcement_registry()
        self.assertEqual(len(registry), 1)
        self.assertIsInstance(registry[0], EnforcementClaimRecord)
        self.assertEqual(registry[0].claim_id, "lint")

    @covers("REQ-0.0.74-15-01")
    def test_registered_claims_returns_all_claim_ids(self) -> None:
        def _fixture() -> str:
            return "v"

        def _ep(v: str) -> list[Any]:
            return []

        @enforces("lint", _fixture, _ep)
        def _m1() -> None:
            pass

        @enforces("format", _fixture, _ep)
        def _m2() -> None:
            pass

        self.assertIn("lint", registered_claims())
        self.assertIn("format", registered_claims())
        self.assertEqual(len(registered_claims()), 2)

    @covers("REQ-0.0.74-15-01")
    def test_record_stores_fixture_and_entrypoint_callables(self) -> None:
        def _fixture() -> str:
            return "violation"

        def _entrypoint(v: str) -> list[str]:
            return []

        @enforces("lint", _fixture, _entrypoint)
        def _marker() -> None:
            pass

        record = get_enforcement_registry()[0]
        self.assertIs(record.fixture, _fixture)
        self.assertIs(record.entrypoint, _entrypoint)

    @covers("REQ-0.0.74-15-01")
    def test_get_enforcement_registry_returns_copy(self) -> None:
        def _fixture() -> str:
            return "v"

        def _ep(v: str) -> list[Any]:
            return []

        @enforces("lint", _fixture, _ep)
        def _marker() -> None:
            pass

        r1 = get_enforcement_registry()
        r2 = get_enforcement_registry()
        self.assertEqual(r1, r2)
        self.assertIsNot(r1, r2)


class TestEnforcesFailClose(unittest.TestCase):
    """Decoration fails closed on malformed/typo or unknown claim id (REQ-15-02)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-15-02")
    def test_malformed_claim_with_space_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:

            @enforces("bad claim!", lambda: None, lambda v: None)
            def _fn() -> None:
                pass

        self.assertIn("Malformed", str(ctx.exception))

    @covers("REQ-0.0.74-15-02")
    def test_empty_claim_raises(self) -> None:
        with self.assertRaises(ValueError):

            @enforces("", lambda: None, lambda v: None)
            def _fn() -> None:
                pass

    @covers("REQ-0.0.74-15-02")
    def test_uppercase_slug_raises(self) -> None:
        with self.assertRaises(ValueError):

            @enforces("LINT", lambda: None, lambda v: None)
            def _fn() -> None:
                pass

    @covers("REQ-0.0.74-15-02")
    def test_claim_starting_with_digit_raises(self) -> None:
        with self.assertRaises(ValueError):

            @enforces("1lint", lambda: None, lambda v: None)
            def _fn() -> None:
                pass

    @covers("REQ-0.0.74-15-02")
    def test_unknown_claim_raises(self) -> None:
        with self.assertRaises(ValueError) as ctx:

            @enforces("no-such-step", lambda: None, lambda v: None)
            def _fn() -> None:
                pass

        self.assertIn("Unknown", str(ctx.exception))

    @covers("REQ-0.0.74-15-02")
    def test_valid_format_and_known_claim_does_not_raise(self) -> None:
        @enforces("lint", lambda: None, lambda v: None)
        def _fn() -> None:
            pass

        self.assertIn("lint", registered_claims())

    @covers("REQ-0.0.74-15-02")
    def test_hyphenated_slug_is_valid(self) -> None:
        set_known_claims(frozenset({"my-check"}))

        @enforces("my-check", lambda: None, lambda v: None)
        def _fn() -> None:
            pass

        self.assertIn("my-check", registered_claims())


class TestEnforcesMetadataOnly(unittest.TestCase):
    """Registration is metadata-only — decorated callable runs unchanged (REQ-15-03)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-15-03")
    def test_decorated_fn_is_returned_unchanged_by_identity(self) -> None:
        def _fixture() -> str:
            return "v"

        def _entrypoint(v: str) -> list[str]:
            return []

        def _original_marker() -> str:
            return "untouched"

        result = enforces("lint", _fixture, _entrypoint)(_original_marker)
        self.assertIs(result, _original_marker)

    @covers("REQ-0.0.74-15-03")
    def test_decorated_fn_call_returns_original_result(self) -> None:
        def _fixture() -> str:
            return "v"

        def _entrypoint(v: str) -> list[str]:
            return []

        sentinel = object()

        @enforces("lint", _fixture, _entrypoint)
        def _marker() -> object:
            return sentinel

        self.assertIs(_marker(), sentinel)

    @covers("REQ-0.0.74-15-03")
    def test_entrypoint_in_registry_is_original_not_partial(self) -> None:
        def _fixture() -> str:
            return "v"

        def _entrypoint(v: str, flag: bool = False) -> list[str]:
            return []

        @enforces("lint", _fixture, _entrypoint)
        def _marker() -> None:
            pass

        record = get_enforcement_registry()[0]
        self.assertNotIsInstance(record.entrypoint, functools.partial)
        self.assertIs(record.entrypoint, _entrypoint)

    @covers("REQ-0.0.74-15-03")
    def test_fixture_in_registry_is_original_callable(self) -> None:
        def _fixture() -> str:
            return "v"

        def _entrypoint(v: str) -> list[str]:
            return []

        @enforces("lint", _fixture, _entrypoint)
        def _marker() -> None:
            pass

        record = get_enforcement_registry()[0]
        self.assertIs(record.fixture, _fixture)
        self.assertNotIsInstance(record.fixture, functools.partial)


class TestEnforcesStructuralFence(unittest.TestCase):
    """Single enforcement-claim surface — no second NC framework forked (REQ-15-04)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    @covers("REQ-0.0.74-15-04")
    def test_enforcement_module_has_single_registry(self) -> None:
        import gzkit.enforcement as enforcement_mod

        self.assertTrue(hasattr(enforcement_mod, "_ENFORCEMENT_REGISTRY"))
        # No parallel PRODUCTION_NEGATIVE_CONTROLS-style mapping
        self.assertFalse(hasattr(enforcement_mod, "_PRODUCTION_NEGATIVE_CONTROLS"))

    @covers("REQ-0.0.74-15-04")
    def test_registered_claims_match_registry_exactly(self) -> None:
        def _fixture() -> str:
            return "v"

        def _ep(v: str) -> list[Any]:
            return []

        @enforces("lint", _fixture, _ep)
        def _m1() -> None:
            pass

        @enforces("format", _fixture, _ep)
        def _m2() -> None:
            pass

        claims = registered_claims()
        registry = get_enforcement_registry()
        self.assertEqual(set(claims), {r.claim_id for r in registry})
        self.assertEqual(len(claims), len(registry))


if __name__ == "__main__":
    unittest.main()
