import unittest

from gzkit.commands.obpi_cmd import _pipeline_verification_commands
from gzkit.commands.obpi_stages import _build_sync_stage_steps


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
        skip_prefixes = ("uv run gz obpi precomplete",)
        for lane in ("lite", "heavy"):
            for cmd in _pipeline_verification_commands("", lane):
                if cmd.startswith(skip_prefixes):
                    continue
                self.assertTrue(
                    cmd.startswith("uv run gz arb "),
                    f"Stage 3 baseline command must produce ARB receipt: {cmd}",
                )

    def test_precomplete_runs_at_stage3_when_obpi_id_provided(self) -> None:
        """GHI #422 fix #2: brief-shape audits must fire BEFORE brief mutation.

        The pipeline runtime should invoke `gz obpi precomplete <id>` at Stage 3
        so behave_req_tags + brief_headings defects abort the pipeline cleanly,
        rather than firing at git-sync (Stage 5) after `gz obpi complete` has
        already mutated the brief to Completed.
        """
        commands = _pipeline_verification_commands("", "heavy", obpi_id="OBPI-0.0.29-08")
        precomplete_cmd = "uv run gz obpi precomplete OBPI-0.0.29-08"
        self.assertIn(precomplete_cmd, commands)

    def test_precomplete_omitted_when_obpi_id_not_provided(self) -> None:
        """Backward compat: callers without an obpi_id (existing tests) get the
        baseline sequence unchanged.
        """
        commands = _pipeline_verification_commands("", "heavy")
        for cmd in commands:
            self.assertFalse(
                cmd.startswith("uv run gz obpi precomplete"),
                f"precomplete should not appear without obpi_id: {cmd}",
            )


class TestSyncStageStepBuilder(unittest.TestCase):
    """GHI #422 fix #1 + fix #3: Stage 5 step ordering with --attestor-present."""

    def _build(self) -> list[tuple[str, str]]:
        return _build_sync_stage_steps(
            obpi_id="OBPI-0.0.29-08",
            resolved_parent="ADR-0.0.29",
            attestor="Jeffry Babb",
            evidence_json='{"value_narrative":"x","key_proof":"y"}',
        )

    def test_complete_is_first_step(self) -> None:
        """GHI #422 fix #1: brief mutation via `gz obpi complete` is the first
        Stage 5 step (was missing entirely; runtime jumped straight to sync).
        """
        steps = self._build()
        first_cmd, _ = steps[0]
        self.assertTrue(
            first_cmd.startswith("uv run gz obpi complete OBPI-0.0.29-08"),
            f"First step must be `gz obpi complete`, got: {first_cmd}",
        )

    def test_complete_passes_attestor_present(self) -> None:
        """GHI #422 fix #3: --attestor-present auto-passed when active marker
        exists. Stage 5 only runs when marker exists (by construction), so the
        flag is always safe.
        """
        steps = self._build()
        complete_cmd = steps[0][0]
        self.assertIn("--attestor-present", complete_cmd)

    def test_sync_follows_complete(self) -> None:
        """Brief mutation must commit BEFORE reconcile, so sync follows complete."""
        steps = self._build()
        sync_idx = next(i for i, (c, _) in enumerate(steps) if "git-sync" in c)
        self.assertGreater(sync_idx, 0, "git-sync must come after complete (first step)")

    def test_reconcile_and_status_follow_sync(self) -> None:
        """Reconcile reads the synced brief; ADR status refreshes the derived view."""
        steps = self._build()
        sync_idx = next(i for i, (c, _) in enumerate(steps) if "git-sync" in c)
        reconcile_idx = next(i for i, (c, _) in enumerate(steps) if "obpi reconcile" in c)
        status_idx = next(i for i, (c, _) in enumerate(steps) if "adr status" in c)
        self.assertGreater(reconcile_idx, sync_idx)
        self.assertGreater(status_idx, sync_idx)

    def test_no_emit_receipt_step(self) -> None:
        """`gz obpi complete` already emits the completed receipt internally;
        the previous standalone `gz obpi emit-receipt` step would have caused
        a duplicate ledger event.
        """
        steps = self._build()
        for cmd, _ in steps:
            self.assertNotIn(
                "obpi emit-receipt",
                cmd,
                f"emit-receipt removed; complete now emits internally. Got: {cmd}",
            )
