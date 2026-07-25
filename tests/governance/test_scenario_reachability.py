"""Tests for scenario-reachability validator (OBPI-0.0.33-04).

Covers:
    REQ-0.0.33-04-01 — Registry absent → exit 0 (empty errors), advisory to stderr
    REQ-0.0.33-04-02 — Registry present, all bullets covered → exit 0, no orphan warnings
    REQ-0.0.33-04-03 — Registry present, orphan bullets → exit 0, stderr orphan warnings
    REQ-0.0.33-04-04 — Registry malformed → ValidationError(type="scenario_reachability")
    REQ-0.0.33-04-05 — validate_scenario_reachability resolves from trust_audits re-export

All tests use tempfile.TemporaryDirectory for sandbox isolation.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from gzkit.governance.trust_audits.scenario_reachability import (
    validate_scenario_reachability,
)
from gzkit.traceability import covers
from tests.governance.common import QuietAdvisoriesMixin

# ---------------------------------------------------------------------------
# Minimal synthetic scorecard content
# ---------------------------------------------------------------------------

_SCORECARD_ONE_MECHANICAL = """\
| # | Rule | Score | Notes |
|---|------|-------|-------|
| 1 | use uv run for commands | **Mechanical** | enforced by hook |
"""


def _make_tree(
    tmp: str,
    *,
    registry_content: str | None = None,  # None = absent, str = file content
    scorecard_content: str = _SCORECARD_ONE_MECHANICAL,
    agents_content: str = "",
) -> Path:
    """Seed a minimal project root for scenario-reachability tests.

    Creates:
      docs/governance/advisory-rules-audit.md  ← scorecard
      AGENTS.md                                 ← per-turn surface (optional body)
      CLAUDE.md                                 ← empty per-turn surface
      data/agent-control-surface-scenarios.json ← registry (only when provided)
    """
    root = Path(tmp)
    # scorecard
    scorecard_path = root / "docs" / "governance" / "advisory-rules-audit.md"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(scorecard_content, encoding="utf-8")
    # AGENTS.md
    (root / "AGENTS.md").write_text(agents_content, encoding="utf-8")
    (root / "CLAUDE.md").write_text("", encoding="utf-8")
    # registry (only when provided)
    if registry_content is not None:
        data_dir = root / "data"
        data_dir.mkdir(exist_ok=True)
        (data_dir / "agent-control-surface-scenarios.json").write_text(
            registry_content, encoding="utf-8"
        )
    return root


class TestREQ01_RegistryAbsent(QuietAdvisoriesMixin):
    """REQ-0.0.33-04-01: Registry absent → exit 0, advisory to stderr."""

    @covers("REQ-0.0.33-04-01")
    def test_registry_absent_returns_empty_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp)
            stderr_buf = io.StringIO()
            with redirect_stderr(stderr_buf):
                errors = validate_scenario_reachability(root)
            self.assertEqual(errors, [], "Registry absent must return no ValidationErrors")
            self.assertIn(
                "scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check",
                stderr_buf.getvalue(),
                "Registry absent must emit advisory message to stderr",
            )


class TestREQ02_RegistryPresentNoOrphans(QuietAdvisoriesMixin):
    """REQ-0.0.33-04-02: Registry present, all bullets covered → exit 0, no orphan warnings."""

    @covers("REQ-0.0.33-04-02")
    def test_all_bullets_covered_no_errors(self) -> None:
        registry = json.dumps([{"name": "main-session", "corpus": ["AGENTS.md"]}])
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                registry_content=registry,
                agents_content="use uv run for commands when executing Python",
            )
            stderr_buf = io.StringIO()
            with redirect_stderr(stderr_buf):
                errors = validate_scenario_reachability(root)
            self.assertEqual(errors, [], "All bullets covered must return no ValidationErrors")
            self.assertNotIn(
                "orphan bullet",
                stderr_buf.getvalue(),
                "All bullets covered must not emit any orphan warnings",
            )


class TestREQ03_RegistryPresentWithOrphans(QuietAdvisoriesMixin):
    """REQ-0.0.33-04-03: Registry present, orphan bullets → exit 0, stderr orphan warnings."""

    @covers("REQ-0.0.33-04-03")
    def test_uncovered_bullet_is_advisory_not_error(self) -> None:
        # Registry corpus points to a file NOT in the surface map
        registry = json.dumps([{"name": "task-mode", "corpus": ["some_unrelated_file.md"]}])
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(
                tmp,
                registry_content=registry,
                agents_content="use uv run for commands here",
            )
            stderr_buf = io.StringIO()
            with redirect_stderr(stderr_buf):
                errors = validate_scenario_reachability(root)
            self.assertEqual(
                errors,
                [],
                "Orphan bullet must be advisory (exit 0) not a ValidationError",
            )
            self.assertIn(
                "scenario-reachability: orphan bullet",
                stderr_buf.getvalue(),
                "Orphan bullet must emit 'scenario-reachability: orphan bullet' to stderr",
            )


class TestREQ04_RegistryMalformed(QuietAdvisoriesMixin):
    """REQ-0.0.33-04-04: Registry malformed → ValidationError(type="scenario_reachability")."""

    @covers("REQ-0.0.33-04-04")
    def test_malformed_registry_returns_validation_error(self) -> None:
        # Object, not array — fails schema
        registry = '{"not": "a list"}'
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp, registry_content=registry)
            errors = validate_scenario_reachability(root)
            self.assertGreaterEqual(
                len(errors), 1, "Malformed registry must return at least one ValidationError"
            )
            self.assertEqual(
                errors[0].type,
                "scenario_reachability",
                "ValidationError type must be 'scenario_reachability'",
            )

    @covers("REQ-0.0.33-04-04")
    def test_invalid_json_returns_validation_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp, registry_content="not-valid-json{{")
            errors = validate_scenario_reachability(root)
            self.assertGreaterEqual(
                len(errors), 1, "Invalid JSON registry must return at least one ValidationError"
            )
            self.assertEqual(errors[0].type, "scenario_reachability")

    @covers("REQ-0.0.33-04-04")
    def test_item_missing_required_key_returns_validation_error(self) -> None:
        # Array item lacks 'corpus' key
        registry = json.dumps([{"name": "incomplete-scenario"}])
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp, registry_content=registry)
            errors = validate_scenario_reachability(root)
            self.assertGreaterEqual(
                len(errors), 1, "Registry item missing required key must return ValidationError"
            )
            self.assertEqual(errors[0].type, "scenario_reachability")


class TestREQ05_PackageReExport(QuietAdvisoriesMixin):
    """REQ-0.0.33-04-05: validate_scenario_reachability resolves from trust_audits re-export."""

    @covers("REQ-0.0.33-04-05")
    def test_validate_scenario_reachability_importable_from_trust_audits(self) -> None:
        from gzkit.governance.trust_audits import validate_scenario_reachability as fn

        self.assertTrue(callable(fn), "validate_scenario_reachability must be callable")

    @covers("REQ-0.0.33-04-05")
    def test_function_returns_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _make_tree(tmp)
            result = validate_scenario_reachability(root)
            self.assertIsInstance(result, list, "Function must return a list")


class TestScenarioReachabilityRoutesToExit3(QuietAdvisoriesMixin):
    """REQ-0.0.33-04-04: schema-malformed registry breach exits 3, not 1.

    The REQ explicitly prescribes ``exit 3 with a ValidationError of
    type=scenario_reachability`` on malformed registry schema. Without
    ``scenario_reachability`` registered in ``_POLICY_BREACH_ERROR_TYPES``,
    the CLI dispatch routes the schema-breach finding through the non-policy
    branch and exits 1 — silently narrowing the REQ contract.
    """

    @covers("REQ-0.0.33-04-04")
    def test_error_type_registered_as_policy_breach(self) -> None:
        from gzkit.commands import validate_cmd

        self.assertIn(
            "scenario_reachability",
            validate_cmd._POLICY_BREACH_ERROR_TYPES,
            msg=(
                "scenario_reachability must route through the exit-3 "
                "policy-breach path per REQ-04-04"
            ),
        )

    @covers("REQ-0.0.33-04-04")
    def test_cli_dispatch_raises_systemexit_3_on_scenario_reachability_breach(self) -> None:
        import contextlib

        from gzkit.commands import validate_cmd
        from gzkit.core.validation_rules import ValidationError

        breach = ValidationError(
            type="scenario_reachability",
            artifact="data/loading_scenarios.json",
            message="registry schema malformed: missing 'scenarios' key",
        )
        with (
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit) as ctx,
        ):
            validate_cmd._print_validation_result(
                errors=[breach],
                scopes=["scenario_reachability"],
                frontmatter_only=False,
            )
        self.assertEqual(ctx.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
