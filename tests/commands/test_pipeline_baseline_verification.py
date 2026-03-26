import unittest

from gzkit.commands.obpi_cmd import _pipeline_verification_commands


class TestPipelineBaselineVerification(unittest.TestCase):
    """Tests for mandatory baseline checks in pipeline Stage 3."""

    def test_baseline_commands_present_when_brief_is_empty(self) -> None:
        result = _pipeline_verification_commands("", "lite")
        self.assertEqual(
            result[:3],
            ["uv run gz lint", "uv run gz typecheck", "uv run gz test"],
        )

    def test_baseline_commands_present_when_brief_has_custom_commands(self) -> None:
        brief = (
            "## Verification\n\n"
            "```bash\n"
            "uv run gz validate --documents\n"
            "python -c \"print('ok')\"\n"
            "```\n"
        )
        result = _pipeline_verification_commands(brief, "lite")
        self.assertEqual(
            result[:3],
            ["uv run gz lint", "uv run gz typecheck", "uv run gz test"],
        )
        self.assertIn("uv run gz validate --documents", result)
        self.assertIn("python -c \"print('ok')\"", result)

    def test_baseline_not_duplicated_when_brief_includes_them(self) -> None:
        brief = (
            "## Verification\n\n"
            "```bash\n"
            "uv run gz lint\n"
            "uv run gz test\n"
            "uv run gz validate --documents\n"
            "```\n"
        )
        result = _pipeline_verification_commands(brief, "lite")
        lint_count = result.count("uv run gz lint")
        test_count = result.count("uv run gz test")
        self.assertEqual(lint_count, 1)
        self.assertEqual(test_count, 1)

    def test_heavy_lane_extras_append_after_brief_commands(self) -> None:
        brief = "## Verification\n\n```bash\nuv run gz validate --documents\n```\n"
        result = _pipeline_verification_commands(brief, "heavy")
        self.assertIn("uv run mkdocs build --strict", result)
        self.assertIn("uv run -m behave features/", result)
        # Heavy extras come after baseline and brief commands
        validate_idx = result.index("uv run gz validate --documents")
        mkdocs_idx = result.index("uv run mkdocs build --strict")
        self.assertGreater(mkdocs_idx, validate_idx)
