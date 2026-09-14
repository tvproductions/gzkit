"""BEHAVIOR tests for population-declared enforcement claims (GHI #1007).

WHY: a negative control plants ONE violation, authored at the same narrowness as
the witness it proves, so a witness that scans a literal subset of a set declared
elsewhere passes its own control. A claim that declares its population must be
proven at EVERY member, and the finding must name the member it caught — a
witness that fails generically for any input cannot pass by failing loudly.

Each arm carries its opposite pole, so an always-pass or always-fail runner
cannot false-pass.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.enforcement import (
    POPULATION_NONE,
    EnforcementClaimRecord,
    _run_single_claim,
    create_fixture_tempdir,
    enforces,
    reset_enforcement_registry,
    set_known_claims,
)

_MEMBERS = ("alpha", "beta", "gamma")


def _plant(member: str) -> Path:
    """Build a tree whose only violation sits at *member*."""
    root = create_fixture_tempdir(prefix="gzkit-population-test-")
    (root / "violation.txt").write_text(member, encoding="utf-8")
    return root


def _witness_seeing(seen: frozenset[str]):
    """Return a witness that reports the planted member only when it is in *seen*."""

    def witness(root: Path) -> list[ValidationError]:
        member = (root / "violation.txt").read_text(encoding="utf-8")
        if member not in seen:
            return []
        return [ValidationError(type="t", artifact=member, message=f"caught {member}")]

    return witness


def _record(witness, population) -> EnforcementClaimRecord:
    return EnforcementClaimRecord(
        claim_id="population-test",
        fixture=_plant,
        entrypoint=witness,
        source_fn="tests.population_test.witness",
        population=population,
    )


class PopulationClaimsAreProvenAtEveryMemberTests(unittest.TestCase):
    """The class GHI #1007 names: a subset witness must not pass its own control."""

    def test_a_witness_covering_every_member_passes(self) -> None:
        result = _run_single_claim(_record(_witness_seeing(frozenset(_MEMBERS)), lambda: _MEMBERS))
        self.assertEqual(result.outcome, "PASS", result.message)

    def test_a_witness_covering_a_strict_subset_is_a_facade(self) -> None:
        subset = frozenset({"alpha", "beta"})
        result = _run_single_claim(_record(_witness_seeing(subset), lambda: _MEMBERS))
        self.assertEqual(result.outcome, "FACADE", result.message)
        self.assertIn("gamma", result.message, "the uncaught member must be named")

    def test_a_finding_that_does_not_name_the_member_is_a_facade(self) -> None:
        """A witness failing generically for every input cannot pass by being loud."""

        def always_fails(_root: Path) -> list[ValidationError]:
            return [ValidationError(type="t", artifact="x", message="something is wrong")]

        result = _run_single_claim(_record(always_fails, lambda: _MEMBERS))
        self.assertEqual(result.outcome, "FACADE", result.message)

    def test_an_empty_population_proves_nothing(self) -> None:
        result = _run_single_claim(_record(_witness_seeing(frozenset(_MEMBERS)), lambda: ()))
        self.assertEqual(result.outcome, "TEST_BUG", result.message)

    def test_a_population_that_cannot_be_read_is_a_test_bug(self) -> None:
        def unreadable() -> tuple[str, ...]:
            raise OSError("declaration missing")

        result = _run_single_claim(_record(_witness_seeing(frozenset(_MEMBERS)), unreadable))
        self.assertEqual(result.outcome, "TEST_BUG", result.message)

    def test_a_claim_without_a_population_runs_its_fixture_once(self) -> None:
        """The existing single-control contract is unchanged for undeclared claims."""
        calls: list[int] = []

        def fixture() -> Path:
            calls.append(1)
            return _plant("alpha")

        record = EnforcementClaimRecord(
            claim_id="population-test",
            fixture=fixture,
            entrypoint=_witness_seeing(frozenset({"alpha"})),
            source_fn="tests.population_test.witness",
            population=POPULATION_NONE,
        )
        result = _run_single_claim(record)
        self.assertEqual(result.outcome, "PASS", result.message)
        self.assertEqual(len(calls), 1)


class PopulationDeclarationIsValidatedAtDecorationTests(unittest.TestCase):
    """A declaration naming nothing checkable must fail at import, like a bad claim id."""

    def setUp(self) -> None:
        set_known_claims(frozenset({"population-test"}))

    def tearDown(self) -> None:
        reset_enforcement_registry()

    def test_an_unrecognised_string_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            enforces("population-test", _plant, _witness_seeing(frozenset()), population="all")

    def test_a_non_callable_object_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            enforces("population-test", _plant, _witness_seeing(frozenset()), population=_MEMBERS)

    def test_none_the_token_and_a_callable_are_accepted(self) -> None:
        for population in (None, POPULATION_NONE, lambda: _MEMBERS):
            enforces(
                "population-test", _plant, _witness_seeing(frozenset()), population=population
            )(lambda: None)


if __name__ == "__main__":
    unittest.main()
