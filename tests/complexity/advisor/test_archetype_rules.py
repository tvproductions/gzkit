"""REQ-derived tests for the advisor archetype-rule loader (OBPI-0.0.29-02).

Pin the rule-table contract: JSON Schema validation at load time, frozen
Pydantic construction, predicate-match semantics, and round-trip parity with
the canonical ``data/advisor_archetype_rules.json`` seed.

Coverage (mapped to brief Acceptance Criteria REQ-IDs):
    REQ-0.0.29-02-05 — JSON Schema validates each rule; malformed rules
        cause load to fail closed. Every test in this module asserts a
        sub-case of this REQ.
    REQ-0.0.29-02-02 — predicate `matches()` semantics back the rule-
        evaluation flow the engine consumes when returning a warn-band
        diagnosis.
"""

from __future__ import annotations

import ast
import json
import tempfile
import unittest
from pathlib import Path

from gzkit.complexity.advisor.archetype_rules import (
    CANONICAL_RULE_TABLE_PATH,
    ArchetypeRule,
    AstPredicate,
    MetricPredicate,
    load_archetype_rules,
)
from gzkit.traceability import covers


def _write_rule_fixture(payload: object) -> Path:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as handle:
        json.dump(payload, handle)
        return Path(handle.name)


class LoadArchetypeRulesTest(unittest.TestCase):
    """Pin the load_archetype_rules contract."""

    @covers("REQ-0.0.29-02-05")
    def test_canonical_rule_table_loads_into_at_least_one_rule(self) -> None:
        rules = load_archetype_rules()
        self.assertGreater(len(rules), 0)
        for rule in rules:
            self.assertIsInstance(rule, ArchetypeRule)

    @covers("REQ-0.0.29-02-05")
    def test_loader_returns_immutable_tuple(self) -> None:
        rules = load_archetype_rules()
        self.assertIsInstance(rules, tuple)

    @covers("REQ-0.0.29-02-05")
    def test_load_rules_rejects_empty_array(self) -> None:
        path = _write_rule_fixture([])
        with self.assertRaises(ValueError) as ctx:
            load_archetype_rules(path)
        self.assertIn("validation", str(ctx.exception).lower())

    @covers("REQ-0.0.29-02-05")
    def test_load_rules_rejects_missing_required_field(self) -> None:
        path = _write_rule_fixture(
            [
                {
                    "archetype": "long_parameter_list",
                    "metric_predicate": {
                        "metrics": ["lizard_param_count"],
                        "bands": ["warn"],
                    },
                    "ast_predicate": {"node_kind": "FunctionDef"},
                    # doctrinal_frame intentionally omitted
                }
            ]
        )
        with self.assertRaises(ValueError):
            load_archetype_rules(path)

    @covers("REQ-0.0.29-02-05")
    def test_load_rules_rejects_unknown_archetype(self) -> None:
        path = _write_rule_fixture(
            [
                {
                    "archetype": "made_up_archetype",
                    "metric_predicate": {
                        "metrics": ["lizard_param_count"],
                        "bands": ["warn"],
                    },
                    "ast_predicate": {"node_kind": "FunctionDef"},
                    "doctrinal_frame": {
                        "authority": "fowler",
                        "citation": "test",
                        "excerpt": "test",
                    },
                }
            ]
        )
        with self.assertRaises(ValueError):
            load_archetype_rules(path)

    @covers("REQ-0.0.29-02-05")
    def test_load_rules_rejects_unknown_authority(self) -> None:
        path = _write_rule_fixture(
            [
                {
                    "archetype": "long_parameter_list",
                    "metric_predicate": {
                        "metrics": ["lizard_param_count"],
                        "bands": ["warn"],
                    },
                    "ast_predicate": {"node_kind": "FunctionDef"},
                    "doctrinal_frame": {
                        "authority": "uncle_bob",
                        "citation": "test",
                        "excerpt": "test",
                    },
                }
            ]
        )
        with self.assertRaises(ValueError):
            load_archetype_rules(path)

    @covers("REQ-0.0.29-02-05")
    def test_load_rules_rejects_empty_metric_list(self) -> None:
        path = _write_rule_fixture(
            [
                {
                    "archetype": "long_parameter_list",
                    "metric_predicate": {"metrics": [], "bands": ["warn"]},
                    "ast_predicate": {"node_kind": "FunctionDef"},
                    "doctrinal_frame": {
                        "authority": "fowler",
                        "citation": "test",
                        "excerpt": "test",
                    },
                }
            ]
        )
        with self.assertRaises(ValueError):
            load_archetype_rules(path)

    @covers("REQ-0.0.29-02-05")
    def test_load_rules_rejects_empty_ast_predicate(self) -> None:
        path = _write_rule_fixture(
            [
                {
                    "archetype": "long_parameter_list",
                    "metric_predicate": {
                        "metrics": ["lizard_param_count"],
                        "bands": ["warn"],
                    },
                    "ast_predicate": {},
                    "doctrinal_frame": {
                        "authority": "fowler",
                        "citation": "test",
                        "excerpt": "test",
                    },
                }
            ]
        )
        with self.assertRaises(ValueError):
            load_archetype_rules(path)


class MetricPredicateTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-02")
    def test_matches_returns_true_for_listed_metric_and_band(self) -> None:
        predicate = MetricPredicate(metrics=("lizard_param_count",), bands=("warn", "block"))
        self.assertTrue(predicate.matches("lizard_param_count", "warn"))
        self.assertTrue(predicate.matches("lizard_param_count", "block"))

    @covers("REQ-0.0.29-02-02")
    def test_matches_returns_false_for_unlisted_metric(self) -> None:
        predicate = MetricPredicate(metrics=("lizard_param_count",), bands=("warn",))
        self.assertFalse(predicate.matches("radon_cc", "warn"))

    @covers("REQ-0.0.29-02-02")
    def test_matches_returns_false_for_unlisted_band(self) -> None:
        predicate = MetricPredicate(metrics=("lizard_param_count",), bands=("warn",))
        self.assertFalse(predicate.matches("lizard_param_count", "advise"))


class AstPredicateTest(unittest.TestCase):
    @covers("REQ-0.0.29-02-02")
    def test_node_kind_match_succeeds_on_function_def(self) -> None:
        predicate = AstPredicate(node_kind="FunctionDef")
        tree = ast.parse("def f():\n    pass\n")
        node = tree.body[0]
        self.assertTrue(predicate.matches(node))

    @covers("REQ-0.0.29-02-02")
    def test_node_kind_match_fails_on_class_def(self) -> None:
        predicate = AstPredicate(node_kind="FunctionDef")
        tree = ast.parse("class C:\n    pass\n")
        node = tree.body[0]
        self.assertFalse(predicate.matches(node))

    @covers("REQ-0.0.29-02-02")
    def test_min_param_count_match_succeeds_when_threshold_met(self) -> None:
        predicate = AstPredicate(min_param_count=4)
        tree = ast.parse("def f(a, b, c, d):\n    pass\n")
        node = tree.body[0]
        self.assertTrue(predicate.matches(node))

    @covers("REQ-0.0.29-02-02")
    def test_min_param_count_match_fails_when_below_threshold(self) -> None:
        predicate = AstPredicate(min_param_count=4)
        tree = ast.parse("def f(a, b):\n    pass\n")
        node = tree.body[0]
        self.assertFalse(predicate.matches(node))

    @covers("REQ-0.0.29-02-02")
    def test_min_branch_count_match_succeeds_for_arrowhead(self) -> None:
        predicate = AstPredicate(min_branch_count=3)
        source = (
            "def f(x):\n"
            "    if x:\n"
            "        if x > 1:\n"
            "            if x > 2:\n"
            "                return 1\n"
            "    return 0\n"
        )
        tree = ast.parse(source)
        node = tree.body[0]
        self.assertTrue(predicate.matches(node))

    @covers("REQ-0.0.29-02-02")
    def test_pydantic_model_construction_rejects_empty_predicate(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            AstPredicate()


class CanonicalSeedRoundTripTest(unittest.TestCase):
    """The seeded data/advisor_archetype_rules.json must load cleanly."""

    @covers("REQ-0.0.29-02-05")
    def test_canonical_seed_round_trips(self) -> None:
        self.assertTrue(CANONICAL_RULE_TABLE_PATH.exists())
        rules = load_archetype_rules(CANONICAL_RULE_TABLE_PATH)
        self.assertGreaterEqual(len(rules), 5)


if __name__ == "__main__":
    unittest.main()
