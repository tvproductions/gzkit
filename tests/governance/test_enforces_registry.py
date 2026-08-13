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


class ClaimRecordsItsDelegatedGateTests(unittest.TestCase):
    """A claim record names the gate its entrypoint delegates to (GHI #798).

    The registry recorded a claim's WITNESS (the negative-control shim) but never
    its SUBJECT (the gate the shim calls), so every consumer asking "what does
    claim X actually gate?" had to walk the delegation chain by hand. Two
    heuristics failed on it -- naming-convention scan 0 of 70, module-stem
    correlation 7 of 71 -- because both asked the registry what it had STORED.
    The delegation is recoverable because the registry HOLDS the live callable.
    """

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    def test_shim_entrypoint_names_the_gate_it_delegates_to(self) -> None:
        def _fixture() -> str:
            return "v"

        def _shim(root: Any) -> list[Any]:
            from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
                audit_adr_status_fresh,
            )

            return audit_adr_status_fresh(root)

        @enforces("lint", _fixture, _shim)
        def _marker() -> None:
            pass

        record = get_enforcement_registry()[0]
        self.assertEqual(
            record.gate_targets,
            ("gzkit.governance.trust_audits.taxonomy:audit_adr_status_fresh",),
        )

    def test_a_shim_delegating_to_several_gates_names_all_of_them(self) -> None:
        """Multi-gate delegation is real -- adr-taxonomy calls two."""

        def _fixture() -> str:
            return "v"

        def _shim(root: Any) -> list[Any]:
            from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
                audit_foundation_closure,
                audit_obpi_lifecycle_coherence,
            )

            return audit_foundation_closure(root) + audit_obpi_lifecycle_coherence(root)

        @enforces("lint", _fixture, _shim)
        def _marker() -> None:
            pass

        self.assertEqual(
            get_enforcement_registry()[0].gate_targets,
            (
                "gzkit.governance.trust_audits.taxonomy:audit_foundation_closure",
                "gzkit.governance.trust_audits.taxonomy:audit_obpi_lifecycle_coherence",
            ),
        )

    def test_a_non_delegating_entrypoint_names_no_gate(self) -> None:
        """Silence is honest: `source_fn` already IS the gate for a co-located
        entrypoint, and a subprocess-backed one has no gzkit callable at all.
        Naming the shim's own module here would assert a gate that does not exist.
        """

        def _fixture() -> str:
            return "v"

        def _entrypoint(v: Any) -> list[Any]:
            return []

        @enforces("lint", _fixture, _entrypoint)
        def _marker() -> None:
            pass

        self.assertEqual(get_enforcement_registry()[0].gate_targets, ())

    def test_non_gzkit_imports_are_not_mistaken_for_gates(self) -> None:
        """A shim importing stdlib to drive a subprocess delegates to no gate."""

        def _fixture() -> str:
            return "v"

        def _shim(root: Any) -> int:
            import sys  # noqa: PLC0415
            from pathlib import Path  # noqa: PLC0415

            return len(str(Path(sys.executable)))

        @enforces("lint", _fixture, _shim)
        def _marker() -> None:
            pass

        self.assertEqual(get_enforcement_registry()[0].gate_targets, ())


class LiveRegistryResolvesTheKnownTruePairsTests(unittest.TestCase):
    """The production population resolves the pairs both heuristics missed (GHI #798).

    `adr-taxonomy` -> `taxonomy.py` and `surface-fidelity-surface-weight` ->
    the surface-fidelity gate are the two the issue names as known-true misses of
    the module-stem correlation. They are the regression witness: if a future
    change re-breaks resolution, these are what silently stop resolving.
    """

    def test_the_two_pairs_the_stem_heuristic_missed_now_resolve(self) -> None:
        from gzkit.enforcement import _ensure_production_claims_registered  # noqa: PLC0415

        _ensure_production_claims_registered()
        by_id = {r.claim_id: r for r in get_enforcement_registry()}

        self.assertIn(
            "gzkit.governance.trust_audits.taxonomy:audit_foundation_closure",
            by_id["adr-taxonomy"].gate_targets,
        )
        self.assertIn(
            "gzkit.governance.trust_audits:validate_surface_fidelity",
            by_id["surface-fidelity-surface-weight"].gate_targets,
        )

    def test_most_of_the_live_population_resolves_to_a_gate(self) -> None:
        """A resolution that covers a handful of claims would not have discharged
        the drain. The floor is stated as a proportion of the live population so
        it tracks the registry rather than pinning a count that rots.
        """
        from gzkit.enforcement import _ensure_production_claims_registered  # noqa: PLC0415

        _ensure_production_claims_registered()
        records = get_enforcement_registry()
        resolved = [r for r in records if r.gate_targets]

        self.assertGreater(len(resolved) / len(records), 0.5)


class TestEnforcesStructuralFence(unittest.TestCase):
    """Single enforcement-claim surface — no second NC framework forked (REQ-15-04)."""

    def setUp(self) -> None:
        reset_enforcement_registry()
        set_known_claims(_TEST_CLAIMS)

    def tearDown(self) -> None:
        reset_enforcement_registry()

    def test_enforcement_module_has_single_registry(self) -> None:
        import gzkit.enforcement as enforcement_mod

        self.assertTrue(hasattr(enforcement_mod, "_ENFORCEMENT_REGISTRY"))
        # No parallel PRODUCTION_NEGATIVE_CONTROLS-style mapping
        self.assertFalse(hasattr(enforcement_mod, "_PRODUCTION_NEGATIVE_CONTROLS"))

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
