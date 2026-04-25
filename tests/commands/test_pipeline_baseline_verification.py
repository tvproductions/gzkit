import unittest

from gzkit.commands.obpi_cmd import _pipeline_verification_commands


class TestPipelineBaselineVerification(unittest.TestCase):
    """Tests for mandatory baseline checks in pipeline Stage 3."""

    _CANONICAL_BASELINE = (
        "uv run gz arb ruff",
        "uv run gz arb typecheck",
        "uv run gz arb step --name unittest -- uv run -m unittest -q",
    )

    def test_baseline_commands_present_when_brief_is_empty(self) -> None:
        result = _pipeline_verification_commands("", "lite")
        self.assertEqual(result[: len(self._CANONICAL_BASELINE)], list(self._CANONICAL_BASELINE))

    def test_baseline_commands_present_when_brief_has_custom_commands(self) -> None:
        brief = (
            "## Verification\n\n"
            "```bash\n"
            "uv run gz validate --documents\n"
            "python -c \"print('ok')\"\n"
            "```\n"
        )
        result = _pipeline_verification_commands(brief, "lite")
        self.assertEqual(result[: len(self._CANONICAL_BASELINE)], list(self._CANONICAL_BASELINE))
        self.assertIn("uv run gz validate --documents", result)
        self.assertIn("python -c \"print('ok')\"", result)

    def test_baseline_not_duplicated_when_brief_includes_them(self) -> None:
        brief = (
            "## Verification\n\n"
            "```bash\n"
            "uv run gz arb ruff\n"
            "uv run gz arb typecheck\n"
            "uv run gz arb step --name unittest -- uv run -m unittest -q\n"
            "uv run gz validate --documents\n"
            "```\n"
        )
        result = _pipeline_verification_commands(brief, "lite")
        for canonical in self._CANONICAL_BASELINE:
            self.assertEqual(result.count(canonical), 1)

    def test_heavy_lane_extras_append_after_brief_commands(self) -> None:
        brief = "## Verification\n\n```bash\nuv run gz validate --documents\n```\n"
        result = _pipeline_verification_commands(brief, "heavy")
        mkdocs_cmd = "uv run gz arb step --name mkdocs -- uv run mkdocs build --strict"
        behave_cmd = "uv run gz arb step --name behave -- uv run -m behave features/"
        self.assertIn(mkdocs_cmd, result)
        self.assertIn(behave_cmd, result)
        validate_idx = result.index("uv run gz validate --documents")
        mkdocs_idx = result.index(mkdocs_cmd)
        self.assertGreater(mkdocs_idx, validate_idx)

    def test_baseline_commands_produce_arb_receipts(self) -> None:
        """REQ from GHI #317: every Stage 3 baseline command MUST be ARB-wrapped
        so the pipeline emits canonical attestation receipts at parity with
        AGENTS.md § Attestation. A baseline command that bypasses ARB cannot
        cite a receipt ID in the close-out evidence package, which is the
        evidence-parity break RHEA observed.
        """
        for lane in ("lite", "heavy"):
            for cmd in _pipeline_verification_commands("", lane):
                self.assertTrue(
                    cmd.startswith("uv run gz arb "),
                    f"Stage 3 baseline command must produce ARB receipt: {cmd}",
                )
