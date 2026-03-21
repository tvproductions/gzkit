"""Unit tests for REQ-level parallel verification dispatch in pipeline_runtime.

Tests cover: verification scope extraction from brief requirements, path overlap
detection, REQ partitioning into independent groups, verification prompt
composition, result parsing and aggregation, sequential fallback logic,
and edge cases (zero reqs, single req, all overlap, timeout/error).
"""

from __future__ import annotations

import json
import unittest

from gzkit.pipeline_runtime import (
    MAX_VERIFICATION_FIX_CYCLES,
    VerificationOutcome,
    VerificationPlan,
    VerificationResult,
    VerificationScope,
    aggregate_verification_results,
    build_verification_plan,
    compose_verification_prompt,
    compute_path_overlap,
    extract_verification_scopes,
    parse_verification_results,
    partition_independent_groups,
    should_fallback_to_sequential,
)

# ---------------------------------------------------------------------------
# Helper factories
# ---------------------------------------------------------------------------


def _make_scope(
    req_index: int = 1,
    requirement_text: str = "Test requirement",
    test_paths: list[str] | None = None,
    verification_commands: list[str] | None = None,
    pass_criteria: str = "All tests pass",
) -> VerificationScope:
    """Return a VerificationScope with sensible defaults."""
    return VerificationScope(
        req_index=req_index,
        requirement_text=requirement_text,
        test_paths=test_paths or [],
        verification_commands=verification_commands or [],
        pass_criteria=pass_criteria,
    )


def _make_result(
    req_index: int = 1,
    outcome: VerificationOutcome = VerificationOutcome.PASS,
    detail: str = "",
    commands_run: list[str] | None = None,
) -> VerificationResult:
    """Return a VerificationResult with sensible defaults."""
    return VerificationResult(
        req_index=req_index,
        outcome=outcome,
        detail=detail,
        commands_run=commands_run or [],
    )


# ---------------------------------------------------------------------------
# extract_verification_scopes
# ---------------------------------------------------------------------------


class TestExtractVerificationScopes(unittest.TestCase):
    """Test parsing brief requirements into verification scopes."""

    def test_extracts_numbered_requirements(self) -> None:
        brief = (
            "## Requirements\n"
            "1. REQUIREMENT: Stage 3 MUST identify non-overlapping paths.\n"
            "1. REQUIREMENT: Overlapping paths MUST be sequential.\n"
            "1. REQUIREMENT: Each subagent receives requirement text.\n"
        )
        scopes = extract_verification_scopes(brief)
        self.assertEqual(len(scopes), 3)
        self.assertEqual(scopes[0].req_index, 1)
        self.assertEqual(scopes[1].req_index, 2)
        self.assertEqual(scopes[2].req_index, 3)
        self.assertIn("non-overlapping", scopes[0].requirement_text)

    def test_attaches_test_paths_when_provided(self) -> None:
        brief = "1. REQUIREMENT: Something must work.\n"
        paths = ["tests/test_foo.py", "tests/test_bar.py"]
        scopes = extract_verification_scopes(brief, test_paths=paths)
        self.assertEqual(len(scopes), 1)
        self.assertEqual(scopes[0].test_paths, paths)

    def test_empty_test_paths_when_not_provided(self) -> None:
        brief = "1. REQUIREMENT: Something must work.\n"
        scopes = extract_verification_scopes(brief)
        self.assertEqual(len(scopes), 1)
        self.assertEqual(scopes[0].test_paths, [])

    def test_no_requirements_returns_empty(self) -> None:
        brief = "## Overview\nThis is just text with no requirements.\n"
        scopes = extract_verification_scopes(brief)
        self.assertEqual(scopes, [])

    def test_ignores_non_requirement_numbered_items(self) -> None:
        brief = (
            "1. This is just a numbered list item.\n"
            "2. REQUIREMENT: This is a real requirement.\n"
            "3. Another plain item.\n"
        )
        scopes = extract_verification_scopes(brief)
        self.assertEqual(len(scopes), 1)
        self.assertEqual(scopes[0].requirement_text, "This is a real requirement.")

    def test_case_insensitive_requirement_keyword(self) -> None:
        brief = "1. Requirement: lowercase requirement text.\n"
        scopes = extract_verification_scopes(brief)
        self.assertEqual(len(scopes), 1)
        self.assertEqual(scopes[0].requirement_text, "lowercase requirement text.")

    def test_never_and_always_lines_not_extracted(self) -> None:
        brief = (
            "1. REQUIREMENT: Real requirement.\n"
            "1. NEVER: Do something bad.\n"
            "1. ALWAYS: Do something good.\n"
        )
        scopes = extract_verification_scopes(brief)
        self.assertEqual(len(scopes), 1)

    def test_default_pass_criteria(self) -> None:
        brief = "1. REQUIREMENT: Something.\n"
        scopes = extract_verification_scopes(brief)
        self.assertEqual(scopes[0].pass_criteria, "All tests pass")


# ---------------------------------------------------------------------------
# compute_path_overlap
# ---------------------------------------------------------------------------


class TestComputePathOverlap(unittest.TestCase):
    """Test path overlap detection between verification scopes."""

    def test_no_overlap(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_b.py"]),
        ]
        overlaps = compute_path_overlap(scopes)
        self.assertEqual(overlaps, {})

    def test_full_overlap(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_a.py"]),
        ]
        overlaps = compute_path_overlap(scopes)
        self.assertEqual(overlaps, {(1, 2): ["tests/test_a.py"]})

    def test_partial_overlap(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py", "tests/test_b.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_b.py", "tests/test_c.py"]),
        ]
        overlaps = compute_path_overlap(scopes)
        self.assertEqual(overlaps, {(1, 2): ["tests/test_b.py"]})

    def test_three_way_overlap(self) -> None:
        shared = "tests/test_shared.py"
        scopes = [
            _make_scope(req_index=1, test_paths=[shared, "tests/test_1.py"]),
            _make_scope(req_index=2, test_paths=[shared, "tests/test_2.py"]),
            _make_scope(req_index=3, test_paths=[shared, "tests/test_3.py"]),
        ]
        overlaps = compute_path_overlap(scopes)
        self.assertIn((1, 2), overlaps)
        self.assertIn((1, 3), overlaps)
        self.assertIn((2, 3), overlaps)

    def test_empty_scopes(self) -> None:
        overlaps = compute_path_overlap([])
        self.assertEqual(overlaps, {})

    def test_empty_test_paths(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=[]),
            _make_scope(req_index=2, test_paths=[]),
        ]
        overlaps = compute_path_overlap(scopes)
        self.assertEqual(overlaps, {})

    def test_single_scope_no_overlap(self) -> None:
        scopes = [_make_scope(req_index=1, test_paths=["tests/test_a.py"])]
        overlaps = compute_path_overlap(scopes)
        self.assertEqual(overlaps, {})


# ---------------------------------------------------------------------------
# partition_independent_groups
# ---------------------------------------------------------------------------


class TestPartitionIndependentGroups(unittest.TestCase):
    """Test partitioning scopes into independent groups."""

    def test_no_overlaps_all_independent(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_b.py"]),
            _make_scope(req_index=3, test_paths=["tests/test_c.py"]),
        ]
        groups = partition_independent_groups(scopes, {})
        self.assertEqual(len(groups), 3)
        self.assertEqual(groups, [[1], [2], [3]])

    def test_all_overlap_single_group(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=3, test_paths=["tests/test_a.py"]),
        ]
        overlaps = compute_path_overlap(scopes)
        groups = partition_independent_groups(scopes, overlaps)
        self.assertEqual(len(groups), 1)
        self.assertEqual(sorted(groups[0]), [1, 2, 3])

    def test_partial_overlap_mixed_groups(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=3, test_paths=["tests/test_c.py"]),
        ]
        overlaps = compute_path_overlap(scopes)
        groups = partition_independent_groups(scopes, overlaps)
        self.assertEqual(len(groups), 2)
        # 1 and 2 overlap, 3 is independent
        group_with_overlap = [g for g in groups if len(g) > 1]
        self.assertEqual(len(group_with_overlap), 1)
        self.assertEqual(sorted(group_with_overlap[0]), [1, 2])

    def test_transitive_overlap(self) -> None:
        """A overlaps B, B overlaps C → all in same group (transitivity)."""
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_a.py", "tests/test_b.py"]),
            _make_scope(req_index=3, test_paths=["tests/test_b.py"]),
        ]
        overlaps = compute_path_overlap(scopes)
        groups = partition_independent_groups(scopes, overlaps)
        self.assertEqual(len(groups), 1)
        self.assertEqual(sorted(groups[0]), [1, 2, 3])

    def test_empty_scopes(self) -> None:
        groups = partition_independent_groups([], {})
        self.assertEqual(groups, [])

    def test_single_scope(self) -> None:
        scopes = [_make_scope(req_index=1, test_paths=["tests/test_a.py"])]
        groups = partition_independent_groups(scopes, {})
        self.assertEqual(groups, [[1]])

    def test_groups_are_sorted(self) -> None:
        scopes = [
            _make_scope(req_index=5, test_paths=["tests/test_e.py"]),
            _make_scope(req_index=3, test_paths=["tests/test_c.py"]),
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
        ]
        groups = partition_independent_groups(scopes, {})
        # Each group internally sorted, groups sorted by first element
        self.assertEqual(groups, [[1], [3], [5]])


# ---------------------------------------------------------------------------
# build_verification_plan
# ---------------------------------------------------------------------------


class TestBuildVerificationPlan(unittest.TestCase):
    """Test the top-level dispatch plan builder."""

    def test_zero_scopes_sequential(self) -> None:
        plan = build_verification_plan([])
        self.assertEqual(plan.strategy, "sequential")
        self.assertEqual(plan.scopes, [])
        self.assertEqual(plan.independent_groups, [])

    def test_no_test_paths_sequential_fallback(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=[]),
            _make_scope(req_index=2, test_paths=[]),
        ]
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.strategy, "sequential")
        self.assertEqual(plan.independent_groups, [[1, 2]])

    def test_all_independent_parallel_strategy(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_b.py"]),
            _make_scope(req_index=3, test_paths=["tests/test_c.py"]),
        ]
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.strategy, "parallel")
        self.assertEqual(len(plan.independent_groups), 3)

    def test_all_overlap_sequential_strategy(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_shared.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_shared.py"]),
        ]
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.strategy, "sequential")
        self.assertEqual(len(plan.independent_groups), 1)

    def test_mixed_strategy(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=3, test_paths=["tests/test_c.py"]),
        ]
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.strategy, "mixed")
        self.assertEqual(len(plan.independent_groups), 2)

    def test_single_scope_sequential(self) -> None:
        scopes = [_make_scope(req_index=1, test_paths=["tests/test_a.py"])]
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.strategy, "sequential")
        self.assertEqual(plan.independent_groups, [[1]])

    def test_plan_preserves_scopes(self) -> None:
        scopes = [
            _make_scope(req_index=1, test_paths=["tests/test_a.py"]),
            _make_scope(req_index=2, test_paths=["tests/test_b.py"]),
        ]
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.scopes, scopes)


# ---------------------------------------------------------------------------
# compose_verification_prompt
# ---------------------------------------------------------------------------


class TestComposeVerificationPrompt(unittest.TestCase):
    """Test verification subagent prompt composition."""

    def test_basic_prompt_structure(self) -> None:
        scopes = [_make_scope(req_index=1, requirement_text="Check paths")]
        prompt = compose_verification_prompt(scopes)
        self.assertIn("## REQ Verification", prompt)
        self.assertIn("### Requirements to Verify", prompt)
        self.assertIn("REQ-1", prompt)
        self.assertIn("Check paths", prompt)
        self.assertIn("read-only", prompt)

    def test_includes_test_paths(self) -> None:
        scopes = [_make_scope(req_index=1, test_paths=["tests/test_foo.py", "tests/test_bar.py"])]
        prompt = compose_verification_prompt(scopes)
        self.assertIn("`tests/test_foo.py`", prompt)
        self.assertIn("`tests/test_bar.py`", prompt)

    def test_includes_verification_commands(self) -> None:
        scopes = [
            _make_scope(req_index=1, verification_commands=["uv run -m unittest tests.test_foo"])
        ]
        prompt = compose_verification_prompt(scopes)
        self.assertIn("`uv run -m unittest tests.test_foo`", prompt)

    def test_includes_group_label(self) -> None:
        scopes = [_make_scope(req_index=1)]
        prompt = compose_verification_prompt(scopes, group_label="Group A")
        self.assertIn("**Group:** Group A", prompt)

    def test_no_group_label(self) -> None:
        scopes = [_make_scope(req_index=1)]
        prompt = compose_verification_prompt(scopes)
        self.assertNotIn("**Group:**", prompt)

    def test_multiple_reqs_in_prompt(self) -> None:
        scopes = [
            _make_scope(req_index=1, requirement_text="First req"),
            _make_scope(req_index=2, requirement_text="Second req"),
        ]
        prompt = compose_verification_prompt(scopes)
        self.assertIn("REQ-1", prompt)
        self.assertIn("REQ-2", prompt)
        self.assertIn("First req", prompt)
        self.assertIn("Second req", prompt)

    def test_includes_json_result_template(self) -> None:
        scopes = [_make_scope(req_index=1)]
        prompt = compose_verification_prompt(scopes)
        self.assertIn('"req_index"', prompt)
        self.assertIn('"outcome"', prompt)


# ---------------------------------------------------------------------------
# parse_verification_results
# ---------------------------------------------------------------------------


class TestParseVerificationResults(unittest.TestCase):
    """Test parsing verification subagent output."""

    def test_parses_valid_json_array(self) -> None:
        output = (
            "Here are the results:\n"
            "```json\n"
            '[{"req_index": 1, "outcome": "PASS", "detail": "ok", "commands_run": []}]\n'
            "```\n"
        )
        results = parse_verification_results(output)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].req_index, 1)
        self.assertEqual(results[0].outcome, VerificationOutcome.PASS)

    def test_parses_multiple_results(self) -> None:
        data = [
            {"req_index": 1, "outcome": "PASS", "detail": "ok"},
            {"req_index": 2, "outcome": "FAIL", "detail": "test failed"},
        ]
        output = f"```json\n{json.dumps(data)}\n```"
        results = parse_verification_results(output)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].outcome, VerificationOutcome.PASS)
        self.assertEqual(results[1].outcome, VerificationOutcome.FAIL)

    def test_no_json_block_returns_empty(self) -> None:
        output = "No JSON here, just text."
        results = parse_verification_results(output)
        self.assertEqual(results, [])

    def test_invalid_json_returns_empty(self) -> None:
        output = "```json\n[{invalid json}]\n```"
        results = parse_verification_results(output)
        self.assertEqual(results, [])

    def test_json_object_not_array_returns_empty(self) -> None:
        output = '```json\n{"req_index": 1, "outcome": "PASS"}\n```'
        results = parse_verification_results(output)
        # This matches the object regex, not the array regex
        self.assertEqual(results, [])

    def test_error_outcome(self) -> None:
        data = [{"req_index": 1, "outcome": "ERROR", "detail": "timeout"}]
        output = f"```json\n{json.dumps(data)}\n```"
        results = parse_verification_results(output)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].outcome, VerificationOutcome.ERROR)


# ---------------------------------------------------------------------------
# aggregate_verification_results
# ---------------------------------------------------------------------------


class TestAggregateVerificationResults(unittest.TestCase):
    """Test result aggregation across all REQs."""

    def test_all_pass(self) -> None:
        results = [
            _make_result(req_index=1, outcome=VerificationOutcome.PASS),
            _make_result(req_index=2, outcome=VerificationOutcome.PASS),
        ]
        all_passed, failures = aggregate_verification_results(results, [1, 2])
        self.assertTrue(all_passed)
        self.assertEqual(failures, [])

    def test_one_fail(self) -> None:
        results = [
            _make_result(req_index=1, outcome=VerificationOutcome.PASS),
            _make_result(req_index=2, outcome=VerificationOutcome.FAIL, detail="broken"),
        ]
        all_passed, failures = aggregate_verification_results(results, [1, 2])
        self.assertFalse(all_passed)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].req_index, 2)

    def test_missing_result_treated_as_fail(self) -> None:
        results = [_make_result(req_index=1, outcome=VerificationOutcome.PASS)]
        all_passed, failures = aggregate_verification_results(results, [1, 2])
        self.assertFalse(all_passed)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].req_index, 2)
        self.assertIn("No result received", failures[0].detail)

    def test_error_treated_as_failure(self) -> None:
        results = [_make_result(req_index=1, outcome=VerificationOutcome.ERROR)]
        all_passed, failures = aggregate_verification_results(results, [1])
        self.assertFalse(all_passed)
        self.assertEqual(len(failures), 1)

    def test_empty_expected_all_pass(self) -> None:
        all_passed, failures = aggregate_verification_results([], [])
        self.assertTrue(all_passed)
        self.assertEqual(failures, [])

    def test_extra_results_ignored(self) -> None:
        results = [
            _make_result(req_index=1, outcome=VerificationOutcome.PASS),
            _make_result(req_index=99, outcome=VerificationOutcome.FAIL),
        ]
        all_passed, failures = aggregate_verification_results(results, [1])
        self.assertTrue(all_passed)
        self.assertEqual(failures, [])

    def test_skipped_treated_as_failure(self) -> None:
        results = [_make_result(req_index=1, outcome=VerificationOutcome.SKIPPED)]
        all_passed, failures = aggregate_verification_results(results, [1])
        self.assertFalse(all_passed)


# ---------------------------------------------------------------------------
# should_fallback_to_sequential
# ---------------------------------------------------------------------------


class TestShouldFallbackToSequential(unittest.TestCase):
    """Test sequential fallback detection."""

    def test_sequential_strategy(self) -> None:
        plan = VerificationPlan(strategy="sequential")
        self.assertTrue(should_fallback_to_sequential(plan))

    def test_parallel_strategy(self) -> None:
        plan = VerificationPlan(strategy="parallel")
        self.assertFalse(should_fallback_to_sequential(plan))

    def test_mixed_strategy(self) -> None:
        plan = VerificationPlan(strategy="mixed")
        self.assertFalse(should_fallback_to_sequential(plan))


# ---------------------------------------------------------------------------
# Data model validation
# ---------------------------------------------------------------------------


class TestVerificationModels(unittest.TestCase):
    """Test Pydantic model constraints and immutability."""

    def test_scope_is_frozen(self) -> None:
        from pydantic import ValidationError

        scope = _make_scope(req_index=1)
        with self.assertRaises(ValidationError):
            scope.req_index = 2  # type: ignore[misc]

    def test_scope_forbids_extra(self) -> None:
        from pydantic import ValidationError

        with self.assertRaises(ValidationError):
            VerificationScope(
                req_index=1,
                requirement_text="test",
                extra_field="bad",  # type: ignore[call-arg]
            )

    def test_result_is_frozen(self) -> None:
        from pydantic import ValidationError

        result = _make_result(req_index=1)
        with self.assertRaises(ValidationError):
            result.outcome = VerificationOutcome.FAIL  # type: ignore[misc]

    def test_plan_is_frozen(self) -> None:
        from pydantic import ValidationError

        plan = VerificationPlan()
        with self.assertRaises(ValidationError):
            plan.strategy = "parallel"  # type: ignore[misc]

    def test_verification_outcome_values(self) -> None:
        self.assertEqual(VerificationOutcome.PASS, "PASS")
        self.assertEqual(VerificationOutcome.FAIL, "FAIL")
        self.assertEqual(VerificationOutcome.ERROR, "ERROR")
        self.assertEqual(VerificationOutcome.SKIPPED, "SKIPPED")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


class TestConstants(unittest.TestCase):
    """Test verification dispatch constants."""

    def test_max_fix_cycles(self) -> None:
        self.assertEqual(MAX_VERIFICATION_FIX_CYCLES, 1)


# ---------------------------------------------------------------------------
# Integration: end-to-end brief → plan
# ---------------------------------------------------------------------------


class TestEndToEndBriefToPlan(unittest.TestCase):
    """Integration tests: parse a brief, build a plan, compose prompts."""

    SAMPLE_BRIEF = (
        "## Requirements (FAIL-CLOSED)\n"
        "\n"
        "1. REQUIREMENT: Stage 3 MUST identify non-overlapping test paths.\n"
        "1. REQUIREMENT: Overlapping paths MUST be verified sequentially.\n"
        "1. REQUIREMENT: Each subagent receives requirement text and commands.\n"
        "1. REQUIREMENT: Results aggregated by controller.\n"
    )

    def test_brief_to_parallel_plan(self) -> None:
        """Each REQ gets a distinct test file → parallel dispatch."""
        scopes = extract_verification_scopes(self.SAMPLE_BRIEF)
        self.assertEqual(len(scopes), 4)
        # Assign distinct test paths to each scope
        enriched = [
            VerificationScope(
                req_index=s.req_index,
                requirement_text=s.requirement_text,
                test_paths=[f"tests/test_req{s.req_index}.py"],
            )
            for s in scopes
        ]
        plan = build_verification_plan(enriched)
        self.assertEqual(plan.strategy, "parallel")
        self.assertEqual(len(plan.independent_groups), 4)

    def test_brief_to_sequential_plan(self) -> None:
        """All REQs share the same test file → sequential dispatch."""
        scopes = extract_verification_scopes(self.SAMPLE_BRIEF, test_paths=["tests/test_shared.py"])
        plan = build_verification_plan(scopes)
        self.assertEqual(plan.strategy, "sequential")
        self.assertEqual(len(plan.independent_groups), 1)

    def test_brief_to_prompt_roundtrip(self) -> None:
        """Scopes extracted from brief produce a valid prompt."""
        scopes = extract_verification_scopes(self.SAMPLE_BRIEF)
        prompt = compose_verification_prompt(scopes, group_label="All REQs")
        self.assertIn("REQ-1", prompt)
        self.assertIn("REQ-4", prompt)
        self.assertIn("**Group:** All REQs", prompt)

    def test_full_roundtrip_with_results(self) -> None:
        """Extract → plan → mock results → aggregate."""
        scopes = extract_verification_scopes(self.SAMPLE_BRIEF)
        plan = build_verification_plan(scopes)

        # Simulate all-pass results
        results = [_make_result(req_index=i, outcome=VerificationOutcome.PASS) for i in range(1, 5)]
        expected = [s.req_index for s in plan.scopes]
        all_passed, failures = aggregate_verification_results(results, expected)
        self.assertTrue(all_passed)
        self.assertEqual(failures, [])

    def test_full_roundtrip_with_one_failure(self) -> None:
        """Extract → plan → one FAIL → aggregate reports failure."""
        scopes = extract_verification_scopes(self.SAMPLE_BRIEF)
        plan = build_verification_plan(scopes)

        results = [
            _make_result(req_index=1, outcome=VerificationOutcome.PASS),
            _make_result(req_index=2, outcome=VerificationOutcome.FAIL, detail="bad"),
            _make_result(req_index=3, outcome=VerificationOutcome.PASS),
            _make_result(req_index=4, outcome=VerificationOutcome.PASS),
        ]
        expected = [s.req_index for s in plan.scopes]
        all_passed, failures = aggregate_verification_results(results, expected)
        self.assertFalse(all_passed)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0].req_index, 2)


if __name__ == "__main__":
    unittest.main()
