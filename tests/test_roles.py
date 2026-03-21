"""Tests for agent role taxonomy and handoff protocols."""

import unittest

from pydantic import ValidationError

from gzkit.roles import (
    CONFLICT_PRECEDENCE,
    ROLE_NAMES,
    ROLE_REGISTRY,
    AgentFileSpec,
    ArtifactContract,
    HandoffResult,
    HandoffStatus,
    ReviewFinding,
    ReviewFindingSeverity,
    ReviewResult,
    ReviewVerdict,
    RoleDefinition,
    get_role,
    get_roles_for_stage,
    resolve_conflict,
    validate_tool_boundaries,
)


class TestRoleTaxonomy(unittest.TestCase):
    """Validate the four-role taxonomy definition."""

    def test_exactly_four_roles_defined(self) -> None:
        self.assertEqual(len(ROLE_REGISTRY), 4)
        self.assertEqual(
            set(ROLE_REGISTRY.keys()), {"Planner", "Implementer", "Reviewer", "Narrator"}
        )

    def test_role_names_constant_matches_registry(self) -> None:
        self.assertEqual(set(ROLE_NAMES), set(ROLE_REGISTRY.keys()))

    def test_each_role_has_artifacts(self) -> None:
        for name, role in ROLE_REGISTRY.items():
            with self.subTest(role=name):
                self.assertGreater(len(role.artifacts.produces), 0, f"{name} produces nothing")
                self.assertGreater(len(role.artifacts.consumes), 0, f"{name} consumes nothing")

    def test_each_role_has_agent_spec(self) -> None:
        for name, role in ROLE_REGISTRY.items():
            with self.subTest(role=name):
                self.assertGreater(len(role.agent_spec.tools), 0)
                self.assertGreater(role.agent_spec.max_turns, 0)

    def test_each_role_has_pipeline_stages(self) -> None:
        for name, role in ROLE_REGISTRY.items():
            with self.subTest(role=name):
                self.assertGreater(len(role.pipeline_stages), 0, f"{name} has no stages")

    def test_get_role_returns_correct_definition(self) -> None:
        for name in ROLE_NAMES:
            role = get_role(name)
            self.assertEqual(role.name, name)

    def test_roles_are_not_vendor_specific(self) -> None:
        """Roles must not encode vendor-specific details."""
        for name, role in ROLE_REGISTRY.items():
            with self.subTest(role=name):
                self.assertEqual(role.agent_spec.model, "inherit")


class TestToolBoundaries(unittest.TestCase):
    """Validate that tool allowlists enforce write access structurally."""

    def test_implementer_has_write_tools(self) -> None:
        impl = get_role("Implementer")
        self.assertTrue(impl.can_write)
        self.assertIn("Edit", impl.agent_spec.tools)
        self.assertIn("Write", impl.agent_spec.tools)

    def test_reviewer_has_no_write_tools(self) -> None:
        reviewer = get_role("Reviewer")
        self.assertFalse(reviewer.can_write)
        self.assertNotIn("Edit", reviewer.agent_spec.tools)
        self.assertNotIn("Write", reviewer.agent_spec.tools)
        self.assertNotIn("Bash", reviewer.agent_spec.tools)

    def test_narrator_has_no_write_tools(self) -> None:
        narrator = get_role("Narrator")
        self.assertFalse(narrator.can_write)
        self.assertNotIn("Edit", narrator.agent_spec.tools)
        self.assertNotIn("Write", narrator.agent_spec.tools)

    def test_planner_has_no_write_tools(self) -> None:
        planner = get_role("Planner")
        self.assertFalse(planner.can_write)
        self.assertNotIn("Edit", planner.agent_spec.tools)
        self.assertNotIn("Write", planner.agent_spec.tools)

    def test_validate_tool_boundaries_all_roles_clean(self) -> None:
        for name, role in ROLE_REGISTRY.items():
            with self.subTest(role=name):
                violations = validate_tool_boundaries(role)
                self.assertEqual(violations, [], f"{name} has boundary violations: {violations}")

    def test_validate_tool_boundaries_detects_mismatch(self) -> None:
        bad_role = RoleDefinition(
            name="Reviewer",
            description="A reviewer with write tools",
            pipeline_stages=["stage-3"],
            artifacts=ArtifactContract(produces=["verdict"], consumes=["code"]),
            agent_spec=AgentFileSpec(
                tools=["Read", "Edit", "Write"],
                max_turns=10,
            ),
            can_write=False,
        )
        violations = validate_tool_boundaries(bad_role)
        self.assertEqual(len(violations), 1)
        self.assertIn("can_write=False", violations[0])


class TestHandoffProtocol(unittest.TestCase):
    """Validate handoff result contract serialization."""

    def test_handoff_result_done(self) -> None:
        result = HandoffResult(
            status=HandoffStatus.DONE,
            files_changed=["src/gzkit/roles.py"],
            tests_added=["tests/test_roles.py"],
        )
        data = result.model_dump()
        self.assertEqual(data["status"], "DONE")
        self.assertEqual(data["files_changed"], ["src/gzkit/roles.py"])

    def test_handoff_result_blocked(self) -> None:
        result = HandoffResult(
            status=HandoffStatus.BLOCKED,
            concerns=["Missing dependency"],
        )
        self.assertEqual(result.status, HandoffStatus.BLOCKED)
        self.assertEqual(result.concerns, ["Missing dependency"])

    def test_handoff_result_roundtrip(self) -> None:
        original = HandoffResult(
            status=HandoffStatus.DONE_WITH_CONCERNS,
            files_changed=["a.py", "b.py"],
            tests_added=["test_a.py"],
            concerns=["Performance not benchmarked"],
        )
        json_str = original.model_dump_json()
        restored = HandoffResult.model_validate_json(json_str)
        self.assertEqual(original, restored)

    def test_handoff_result_rejects_extra_fields(self) -> None:
        with self.assertRaises(ValidationError):
            HandoffResult(
                status=HandoffStatus.DONE,
                extra_field="not allowed",  # type: ignore[unknown-argument]
            )

    def test_all_handoff_statuses_exist(self) -> None:
        expected = {"DONE", "DONE_WITH_CONCERNS", "NEEDS_CONTEXT", "BLOCKED"}
        actual = {s.value for s in HandoffStatus}
        self.assertEqual(actual, expected)


class TestReviewResult(unittest.TestCase):
    """Validate review result contract."""

    def test_review_pass_verdict(self) -> None:
        result = ReviewResult(verdict=ReviewVerdict.PASS, summary="All good")
        self.assertEqual(result.verdict, ReviewVerdict.PASS)
        self.assertEqual(result.findings, [])

    def test_review_with_findings(self) -> None:
        finding = ReviewFinding(
            file="src/foo.py",
            line=42,
            severity=ReviewFindingSeverity.MAJOR,
            message="Missing error handling",
        )
        result = ReviewResult(
            verdict=ReviewVerdict.CONCERNS,
            findings=[finding],
            summary="One major issue found",
        )
        self.assertEqual(len(result.findings), 1)
        self.assertEqual(result.findings[0].severity, ReviewFindingSeverity.MAJOR)

    def test_review_result_roundtrip(self) -> None:
        original = ReviewResult(
            verdict=ReviewVerdict.FAIL,
            findings=[
                ReviewFinding(
                    file="x.py",
                    severity=ReviewFindingSeverity.CRITICAL,
                    message="Security vulnerability",
                )
            ],
            summary="Blocked",
        )
        json_str = original.model_dump_json()
        restored = ReviewResult.model_validate_json(json_str)
        self.assertEqual(original, restored)


class TestConflictResolution(unittest.TestCase):
    """Validate conflict resolution rules."""

    def test_precedence_order(self) -> None:
        self.assertEqual(
            CONFLICT_PRECEDENCE,
            ["Planner", "Implementer", "Reviewer", "Narrator"],
        )

    def test_implementer_beats_reviewer(self) -> None:
        self.assertEqual(resolve_conflict("Implementer", "Reviewer"), "Implementer")

    def test_planner_beats_implementer(self) -> None:
        self.assertEqual(resolve_conflict("Planner", "Implementer"), "Planner")

    def test_same_role_returns_self(self) -> None:
        for name in ROLE_NAMES:
            with self.subTest(role=name):
                self.assertEqual(resolve_conflict(name, name), name)

    def test_symmetry(self) -> None:
        """resolve_conflict(a, b) == resolve_conflict(b, a)."""
        self.assertEqual(
            resolve_conflict("Reviewer", "Implementer"),
            resolve_conflict("Implementer", "Reviewer"),
        )


class TestStageMapping(unittest.TestCase):
    """Validate role-to-stage mapping queries."""

    def test_stage_2_has_implementer_and_reviewer(self) -> None:
        roles = get_roles_for_stage("stage-2")
        names = {r.name for r in roles}
        self.assertIn("Implementer", names)
        self.assertIn("Reviewer", names)

    def test_stage_4_has_narrator(self) -> None:
        roles = get_roles_for_stage("stage-4")
        names = {r.name for r in roles}
        self.assertIn("Narrator", names)

    def test_unknown_stage_returns_empty(self) -> None:
        roles = get_roles_for_stage("stage-99")
        self.assertEqual(roles, [])

    def test_single_session_can_fill_multiple_roles(self) -> None:
        """A single agent session CAN fill multiple roles sequentially (REQ-8)."""
        # This is a design constraint, not a runtime enforcement.
        # We verify that roles are independent definitions that don't
        # encode mutual exclusion.
        all_roles = [get_role(name) for name in ROLE_NAMES]
        self.assertEqual(len(all_roles), 4)
        # All are distinct definitions
        names = {r.name for r in all_roles}
        self.assertEqual(len(names), 4)


class TestModelImmutability(unittest.TestCase):
    """Validate that role models are frozen (immutable)."""

    def test_role_definition_is_frozen(self) -> None:
        role = get_role("Implementer")
        with self.assertRaises(ValidationError):
            role.name = "Hacker"  # type: ignore[misc]

    def test_handoff_result_is_frozen(self) -> None:
        result = HandoffResult(status=HandoffStatus.DONE)
        with self.assertRaises(ValidationError):
            result.status = HandoffStatus.BLOCKED

    def test_review_result_is_frozen(self) -> None:
        result = ReviewResult(verdict=ReviewVerdict.PASS)
        with self.assertRaises(ValidationError):
            result.verdict = ReviewVerdict.FAIL


if __name__ == "__main__":
    unittest.main()
