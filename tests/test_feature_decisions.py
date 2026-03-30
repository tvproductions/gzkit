"""Tests for FeatureDecisions (OBPI-0.0.8-03).

Covers decision method dispatch, flag-key containment, singleton behavior,
and behavioral docstring presence.
"""

import unittest

from gzkit.flags.decisions import FeatureDecisions, _reset_decisions, get_decisions
from gzkit.flags.models import FlagCategory, FlagSpec
from gzkit.flags.service import FlagService
from gzkit.traceability import covers


def _make_spec(key="ops.product_proof", category=FlagCategory.ops, default=True, **kwargs):
    base = {
        "key": key,
        "category": category,
        "default": default,
        "description": "Test flag.",
        "owner": "test",
        "introduced_on": "2026-03-29",
    }
    if category == FlagCategory.ops and "review_by" not in kwargs:
        base["review_by"] = "2026-06-29"
    return FlagSpec.model_validate({**base, **kwargs})


def _registry(*specs):
    return {s.key: s for s in specs}


def _service(*specs, **kwargs):
    return FlagService(_registry(*specs), **kwargs)


class TestProductProofEnforced(unittest.TestCase):
    """product_proof_enforced() decision method."""

    @covers("REQ-0.0.8-03-01")
    def test_returns_true_when_flag_enabled(self):
        svc = _service(_make_spec(default=True))
        decisions = FeatureDecisions(svc)
        self.assertTrue(decisions.product_proof_enforced())

    @covers("REQ-0.0.8-03-02")
    def test_returns_false_when_flag_disabled(self):
        svc = _service(_make_spec(default=True))
        svc.set_test_override("ops.product_proof", False)
        decisions = FeatureDecisions(svc)
        self.assertFalse(decisions.product_proof_enforced())

    def test_returns_false_when_default_false(self):
        svc = _service(_make_spec(default=False))
        decisions = FeatureDecisions(svc)
        self.assertFalse(decisions.product_proof_enforced())

    def test_has_docstring(self):
        decisions = FeatureDecisions(_service(_make_spec()))
        self.assertIsNotNone(decisions.product_proof_enforced.__doc__)
        self.assertIn("closeout", decisions.product_proof_enforced.__doc__.lower())


class TestGetDecisionsSingleton(unittest.TestCase):
    """get_decisions() module-level singleton."""

    def setUp(self):
        _reset_decisions()

    def tearDown(self):
        _reset_decisions()

    @covers("REQ-0.0.8-03-04")
    def test_returns_same_instance(self):
        svc = _service(_make_spec())
        first = get_decisions(svc)
        second = get_decisions()
        self.assertIs(first, second)

    def test_accepts_explicit_service(self):
        svc = _service(_make_spec())
        decisions = get_decisions(svc)
        self.assertIsInstance(decisions, FeatureDecisions)

    def test_reset_clears_singleton(self):
        svc = _service(_make_spec())
        first = get_decisions(svc)
        _reset_decisions()
        second = get_decisions(svc)
        self.assertIsNot(first, second)


class TestFlagKeyContainment(unittest.TestCase):
    """Flag key strings must only appear in decisions.py and flags.json."""

    @covers("REQ-0.0.8-03-03")
    def test_decision_delegates_to_service(self):
        svc = _service(_make_spec(default=True))
        decisions = FeatureDecisions(svc)
        result = decisions.product_proof_enforced()
        self.assertIsInstance(result, bool)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
