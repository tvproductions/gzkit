import unittest

from gzkit.commands.common import GzCliError
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

    def test_heavy_lane_behave_uses_tags_when_provided(self) -> None:
        """GHI #420: Stage 3 scope discipline.

        When the runtime resolves @REQ-tagged behave scenarios for *this*
        OBPI, the Stage 3 behave invocation must pass them via ``--tags``
        so cross-OBPI feature-file rot (the GHI #420 surfaced failure mode)
        does not block new OBPIs.
        """
        commands = _pipeline_verification_commands(
            "",
            "heavy",
            obpi_id="OBPI-0.0.29-08",
            behave_tags=["@REQ-0.0.29-08-01", "@REQ-0.0.29-08-02"],
        )
        expected = (
            "uv run gz arb step --name behave -- "
            "uv run -m behave --tags=@REQ-0.0.29-08-01,@REQ-0.0.29-08-02 features/"
        )
        self.assertIn(expected, commands)
        unscoped = "uv run gz arb step --name behave -- uv run -m behave features/"
        self.assertNotIn(unscoped, commands)

    def test_heavy_lane_behave_skipped_when_obpi_has_no_tags(self) -> None:
        """GHI #420: when the runtime resolves zero @REQ-tagged behave
        scenarios for the OBPI, behave is omitted from Stage 3 entirely.

        The full ``features/`` sweep is deferred to ADR closeout (Stage 5
        of the parent ADR), per the SKILL.md scope-discipline doctrine.
        Skipping is preferable to running the full suite — the full suite
        is what cross-OBPI rot blocks.
        """
        commands = _pipeline_verification_commands(
            "",
            "heavy",
            obpi_id="OBPI-0.0.29-08",
            behave_tags=[],
        )
        for cmd in commands:
            self.assertNotIn(
                "behave",
                cmd,
                f"behave should be skipped at Stage 3 when no REQ tags: {cmd}",
            )

    def test_heavy_lane_full_behave_when_no_obpi_context(self) -> None:
        """Backward compat: callers without ``behave_tags`` (no OBPI scope
        context) keep the full ``features/`` invocation. Existing
        non-pipeline callers and lite-lane briefs without an OBPI
        identifier are unaffected.
        """
        commands = _pipeline_verification_commands("", "heavy")
        full = "uv run gz arb step --name behave -- uv run -m behave features/"
        self.assertIn(full, commands)


class TestSyncStageStepBuilder(unittest.TestCase):
    """GHI #422 fix #1 + fix #3: Stage 5 step ordering with --attestor-present."""

    def _build(self) -> list[tuple[str, str]]:
        return _build_sync_stage_steps(
            obpi_id="OBPI-0.0.29-08",
            resolved_parent="ADR-0.0.29",
            attestor="g0",
            evidence_json=(
                '{"value_narrative":"x","key_proof":"y",'
                '"attestation_text":"verified Stage 3 evidence"}'
            ),
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

    def test_complete_command_does_not_pass_evidence_json_flag(self) -> None:
        """GHI #435: `gz obpi complete` does not accept `--evidence-json`. The
        pipeline must translate the JSON payload into the discrete flags the
        inner CLI consumes (`--attestation-text`, etc.), never pass the raw
        `--evidence-json` token through.
        """
        steps = self._build()
        complete_cmd = steps[0][0]
        self.assertNotIn(
            "--evidence-json",
            complete_cmd,
            f"complete does not accept --evidence-json; pipeline must translate. {complete_cmd!r}",
        )

    def test_complete_command_carries_attestation_text_flag(self) -> None:
        """GHI #435: `attestation_text` from the evidence-json must surface as
        `--attestation-text <quoted>` on the inner `gz obpi complete` call.
        """
        steps = self._build()
        complete_cmd = steps[0][0]
        self.assertIn("--attestation-text", complete_cmd)
        self.assertIn("verified Stage 3 evidence", complete_cmd)

    def test_complete_command_translates_implementation_summary_and_key_proof(self) -> None:
        """GHI #435: optional fields in evidence-json forward as their flags."""
        steps = _build_sync_stage_steps(
            obpi_id="OBPI-0.0.29-08",
            resolved_parent="ADR-0.0.29",
            attestor="g0",
            evidence_json=(
                '{"attestation_text":"a","implementation_summary":"impl","key_proof":"proof"}'
            ),
        )
        complete_cmd = steps[0][0]
        self.assertIn("--implementation-summary", complete_cmd)
        self.assertIn("impl", complete_cmd)
        self.assertIn("--key-proof", complete_cmd)
        self.assertIn("proof", complete_cmd)

    def test_complete_command_translates_accept_uncovered_pairs(self) -> None:
        """GHI #435: paired waivers translate to repeated flag pairs preserving order."""
        steps = _build_sync_stage_steps(
            obpi_id="OBPI-0.0.29-08",
            resolved_parent="ADR-0.0.29",
            attestor="g0",
            evidence_json=(
                '{"attestation_text":"a","accept_uncovered":["REQ-1","REQ-2"],'
                '"accept_uncovered_reason":["r1","r2"]}'
            ),
        )
        complete_cmd = steps[0][0]
        self.assertEqual(complete_cmd.count("--accept-uncovered "), 2)
        self.assertEqual(complete_cmd.count("--accept-uncovered-reason"), 2)
        self.assertIn("REQ-1", complete_cmd)
        self.assertIn("REQ-2", complete_cmd)
        self.assertIn("r1", complete_cmd)
        self.assertIn("r2", complete_cmd)

    def test_missing_attestation_text_fails_closed_with_clear_error(self) -> None:
        """GHI #435: option B remediation — fail at the pipeline boundary with
        a clear error rather than letting the inner `gz obpi complete` die on
        a missing-required-flag message that doesn't name evidence-json.
        """
        with self.assertRaises(GzCliError) as ctx:
            _build_sync_stage_steps(
                obpi_id="OBPI-0.0.29-08",
                resolved_parent="ADR-0.0.29",
                attestor="g0",
                evidence_json='{"value_narrative":"x","key_proof":"y"}',
            )
        message = str(ctx.exception)
        self.assertIn("--evidence-json", message)
        self.assertIn("attestation_text", message)

    def test_invalid_json_fails_closed_with_clear_error(self) -> None:
        """GHI #435: malformed JSON fails closed at pipeline boundary."""
        with self.assertRaises(GzCliError):
            _build_sync_stage_steps(
                obpi_id="OBPI-0.0.29-08",
                resolved_parent="ADR-0.0.29",
                attestor="g0",
                evidence_json="{not json",
            )

    def test_accept_uncovered_length_mismatch_fails_closed(self) -> None:
        """GHI #435: pipeline mirrors `gz obpi complete`'s 1:1 pairing rule."""
        with self.assertRaises(GzCliError) as ctx:
            _build_sync_stage_steps(
                obpi_id="OBPI-0.0.29-08",
                resolved_parent="ADR-0.0.29",
                attestor="g0",
                evidence_json=(
                    '{"attestation_text":"a","accept_uncovered":["REQ-1","REQ-2"],'
                    '"accept_uncovered_reason":["only-one"]}'
                ),
            )
        self.assertIn("accept_uncovered", str(ctx.exception))
