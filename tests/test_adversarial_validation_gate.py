"""Tests for what Step 4b leaves on `gz obpi complete` (GHI #676, #985, #1163).

The refusal lives in the acceptance reducer and is tested with it
(`tests/test_acceptance.py`, `tests/test_acceptance_store.py`). This module holds
the completion side: the completion path consults that reducer before writing,
the cross-vendor proof reads the argv that ran, and the `adversarial_validation`
event carries the tier and receipt it is given.
"""

from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from gzkit.cli.main import _build_parser
from gzkit.commands.obpi_complete_adversarial import (
    ADVERSARY_VERDICTS,
    _build_adversarial_event,
    _is_cross_vendor_adversary,
    _receipt_proves_cross_vendor,
)
from gzkit.events import parse_typed_event


class TestVerdictVocabulary(unittest.TestCase):
    def test_verdict_vocabulary_is_closed_to_exactly_four_members(self) -> None:
        self.assertEqual(
            ADVERSARY_VERDICTS,
            ("refuted", "not-refuted", "refuted-with-caveats", "degraded-human-only"),
        )


class TestCompletionTakesNoVerdictFromItsCaller(unittest.TestCase):
    """A flag the command accepts must be read by it (GHI #1163).

    The verdict, reviewer, tier and receipt come from the accepted review. Flags
    that claimed to supply them were accepted and ignored after GHI #985 moved the
    refusal, so a caller could believe it had recorded a tier it never recorded.
    """

    _BASE = (
        "obpi",
        "complete",
        "OBPI-0.0.99-01-example",
        "--attestor",
        "g0",
        "--attestation-text",
        "attest completed",
    )

    def test_flags_that_claimed_the_verdict_are_usage_errors(self) -> None:
        parser = _build_parser()
        for flag, value in (
            ("--adversary-verdict", "not-refuted"),
            ("--adversary", "codex/gpt-5.4"),
            ("--adversary-receipt", "arb-step-codexadversary-0"),
            ("--adversary-fallback-reason", "codex setup reported ready=false"),
            ("--adversary-tier", "1"),
        ):
            with (
                self.subTest(flag=flag),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit) as ctx,
            ):
                parser.parse_args([*self._BASE, flag, value])
            self.assertEqual(ctx.exception.code, 2, flag)

    def test_provenance_flags_reach_the_event_beside_the_reviews_own_facts(self) -> None:
        from gzkit.commands import obpi_complete as mod

        args = _build_parser().parse_args(
            [
                *self._BASE,
                "--adversary-job-id",
                "task-1",
                "--refuted-claim",
                "closed vocabularies are not fail-closed",
                "--adversary-resolution",
                "membership assertions added; the adversary's check re-run",
            ]
        )
        review = SimpleNamespace(tier=2, reviewer_id="claude/reviewer", receipt_id="arb-step-x")
        with mock.patch.object(mod, "completion_review", return_value=review):
            event = mod._current_adversarial_event(
                Path("."),
                "OBPI-0.0.99-01-example",
                False,
                args.adversary_job_id,
                args.refuted_claim,
                args.adversary_resolution,
            )
        assert event is not None
        recorded = event.model_dump()
        # The caller supplies detail; the review supplies who, which tier and what ran.
        self.assertEqual(recorded["job_id"], "task-1")
        self.assertEqual(recorded["refuted_claim"], "closed vocabularies are not fail-closed")
        self.assertEqual(
            recorded["resolution"], "membership assertions added; the adversary's check re-run"
        )
        self.assertEqual(
            (recorded["adversary"], recorded["adversary_tier"], recorded["adversary_receipt"]),
            ("claude/reviewer", 2, "arb-step-x"),
        )
        self.assertEqual(recorded["verdict"], "not-refuted")


class TestDeclaredTierReachesTheLedger(unittest.TestCase):
    """The tier must be DURABLE, not merely checked — GHI #678's 'record the tier'.

    A gate that validates a tier and then discards it leaves the ledger unable to
    answer 'which tier ran?' after the fact; 13 of 19 recorded events carried no
    corroborating artifact at all when this was reopened.
    """

    def _dump(self, **overrides: object) -> dict[str, object]:
        kwargs: dict[str, object] = {
            "obpi_id": "OBPI-0.33.0-01-airlock-data-model-and-events",
            "verdict": "not-refuted",
            "adversary": "codex/gpt-5.4",
            "job_id": None,
            "refuted_claim": None,
            "resolution": None,
        }
        kwargs.update(overrides)
        event = _build_adversarial_event(**kwargs)
        assert event is not None
        return event.model_dump()

    def test_declared_tier_reaches_the_serialized_ledger_record(self) -> None:
        # The durable form is what a later audit reads — asserting on the in-memory
        # object alone would not prove the tier survives to the ledger line.
        self.assertEqual(self._dump(tier=1)["adversary_tier"], 1)

    def test_undeclared_tier_is_omitted_rather_than_recorded_as_null(self) -> None:
        # Absent detail is omitted, never emitted as a null a reader could mistake
        # for a recorded tier — matching how job_id/resolution already behave.
        self.assertNotIn("adversary_tier", self._dump(tier=None))

    def test_typed_event_model_admits_the_recorded_tier(self) -> None:
        # The discriminated union is the typed read path (parse_typed_event,
        # req_kind_support, ontology/corpus). A field the writer emits but the
        # typed model rejects would fail closed on replay.
        parsed = parse_typed_event(self._dump(tier=2))
        self.assertEqual(parsed.adversary_tier, 2)


class TestGateIsWiredIntoCompletion(unittest.TestCase):
    """The gate must be INVOKED by `obpi_complete_cmd`, not merely defined.

    A correct enforcement function that nothing calls is the facade shape this
    codebase exists to kill (cf. GHI #187's `_canonicalize_obpi_id`). Mock past the
    earlier reconcile gate and assert the completion path reaches Step 4b.
    """

    def test_obpi_complete_cmd_invokes_the_gate_before_writing(self) -> None:
        """Assert the gate is CALLED — not merely that completion exits.

        An earlier version of this test asserted only `SystemExit`, and survived a
        mutation that unwired the gate entirely: the exit came from a later
        evidence check. Spy on the gate itself so the assertion cannot pass
        without it.
        """
        from gzkit.commands import obpi_complete as mod

        obpi_id = "OBPI-0.33.0-02-airlock-in-pipeline-tracer"
        with (
            self._completion_harness(mod, obpi_id) as (gate, execute, _preview),
            # Captured so the refusal's prose stays out of the suite's stdout (GHI #705).
            contextlib.redirect_stdout(io.StringIO()),
            self.assertRaises(SystemExit),
        ):
            mod.obpi_complete_cmd(
                obpi=obpi_id,
                attestor="g0",
                attestation_text="attest completed",
                implementation_summary="- Files created: x",
                key_proof="ran the thing; observed the output",
                as_json=False,
                dry_run=False,
            )

        gate.assert_called_once()
        # The durable closure reader is the governing boundary. Old caller
        # verdict/tier flags are not arguments capable of licensing this gate.
        self.assertEqual(gate.call_args.args[1], obpi_id)
        self.assertEqual(gate.call_args.kwargs, {})
        # The transaction must never run when Step 4b is unrecorded.
        execute.assert_not_called()

    @contextlib.contextmanager
    def _completion_harness(self, mod: object, obpi_id: str, *, gate_raises: bool = True):  # noqa: ANN202
        """Mock every gate BETWEEN resolve and Step 4b, leaving 4b as the spy.

        The gate deliberately sits last, after the structural gates, so an operator
        with an uncovered REQ hears about the REQ rather than the adversary. Reaching
        it in a test therefore means clearing those gates first.

        Every intervening gate MUST be mocked. `_resolve_and_validate` yields a
        MagicMock brief path, and an unmocked gate that reads it hands that mock to
        `yaml.safe_load`, which treats any object with `.read()` as a stream. A
        MagicMock's `.read()` never returns the empty string that signals EOF, so
        PyYAML's reader loops forever and the process grows without bound (observed:
        23 GB before the OOM killer). A missing patch here does not fail the test —
        it hangs the suite.
        """
        with (
            mock.patch.object(mod, "ensure_initialized"),
            mock.patch.object(mod, "get_project_root"),
            mock.patch.object(mod, "Ledger"),
            mock.patch.object(mod, "_enforce_reconcile_receipt_gate"),
            mock.patch.object(mod, "_enforce_security_review_gate"),
            mock.patch.object(mod, "_enforce_attestation_receipt_gate"),
            mock.patch.object(mod, "_enforce_req_coverage_gate"),
            mock.patch.object(mod, "_enforce_task_envelope_gate"),
            mock.patch.object(mod, "resolve_adr_file", return_value=(mock.MagicMock(), None)),
            mock.patch.object(mod, "_read_adr_kind", return_value="feature"),
            mock.patch.object(mod, "_build_completed_brief", return_value="brief"),
            # return_value=[] — a bare MagicMock is truthy, and the caller does
            # `if validation_errors:` — so the default mock would fail the brief.
            mock.patch.object(mod, "_validate_would_be_content", return_value=[]),
            mock.patch.object(mod, "_print_dry_run") as preview,
            mock.patch.object(mod, "_execute_transaction") as execute,
            mock.patch.object(
                mod,
                "completion_review",
                side_effect=ValueError("required acceptance proof missing")
                if gate_raises
                else None,
            ) as gate,
            mock.patch.object(
                mod,
                "_resolve_and_validate",
                return_value=(
                    mock.MagicMock(),
                    obpi_id,
                    "content",
                    "ADR-0.33.0",
                    "heavy",
                    False,
                    "absent",
                ),
            ),
        ):
            yield gate, execute, preview

    def test_dry_run_skips_the_gate(self) -> None:
        """--dry-run previews headlessly; it writes nothing, so it gates nothing.

        No exception is suppressed here. An earlier version wrapped the call in
        `contextlib.suppress(SystemExit, Exception)`, which let the command die at
        any earlier gate and still satisfy `assert_not_called()` — the assertion
        passed for the wrong reason. A dry run must return cleanly.
        """
        from gzkit.commands import obpi_complete as mod

        obpi_id = "OBPI-0.33.0-02-airlock-in-pipeline-tracer"
        with self._completion_harness(mod, obpi_id, gate_raises=False) as (gate, execute, preview):
            mod.obpi_complete_cmd(
                obpi=obpi_id,
                attestor="g0",
                attestation_text="attest completed",
                # Required evidence: without it the command exits at `_resolve_evidence`
                # BEFORE Step 4b, and `gate.assert_not_called()` would pass for the
                # wrong reason.
                implementation_summary="- Files created: x",
                key_proof="ran the thing; observed the output",
                as_json=False,
                dry_run=True,
            )

        # The run reached the dry-run return, so "gate not called" means skipped —
        # not that the command died at an earlier gate.
        preview.assert_called_once()
        gate.assert_not_called()
        # A preview writes nothing: no brief flip, no ledger append.
        execute.assert_not_called()


class TestNameScanCannotDistinguishMentionFromUse(unittest.TestCase):
    """GHI #765: the adversary NAME is not a sound channel for the tier-1 property.

    `_is_cross_vendor_adversary` prefix-scans, so a vendor named anywhere but the
    first token reads as not-cross-vendor. The obvious repair — token membership —
    is worse, and these assertions pin why: two adversary names recorded in
    `.gzkit/ledger.jsonl` mention Codex precisely to say it was UNAVAILABLE. A scan
    that admits a mentioned vendor classifies a degraded Claude-family run as
    tier-1, which fails OPEN on the exact substitution Step 4b exists to catch.

    The prefix scan's conservatism is therefore deliberate, not a bug to fix: its
    wrong answers demand a fallback reason. Authority for the tier belongs to the
    receipt channel, which reads argv and cannot confuse mention with use.
    """

    def test_a_name_mentioning_codex_as_unavailable_is_not_cross_vendor(self) -> None:
        # Verbatim from .gzkit/ledger.jsonl. Both name Codex to record its ABSENCE.
        for name in (
            "independent-claude-subagent (codex-unavailable; degraded tier)",
            "independent-claude-subagent (degraded from unavailable codex/gpt-5)",
        ):
            with self.subTest(name=name):
                self.assertFalse(_is_cross_vendor_adversary(name))

    def test_claude_family_name_is_not_cross_vendor(self) -> None:
        self.assertFalse(_is_cross_vendor_adversary("claude/general-purpose"))

    def test_a_genuinely_codex_led_name_is_cross_vendor(self) -> None:
        for name in ("codex", "codex/gpt-5", "codex-cli-0.146.0"):
            with self.subTest(name=name):
                self.assertTrue(_is_cross_vendor_adversary(name))


class TestReceiptProvesCrossVendorFromArgv(unittest.TestCase):
    """GHI #765: tier 1 is proven by what RAN, not by what the caller typed.

    An ARB step receipt is written by a different process at invocation time and
    records `step.command` — the argv actually executed. These assertions derive
    from the requirement that the proof read that argv, never a display name.
    """

    @staticmethod
    def _receipt(command: list[str], *, exit_status: int = 0) -> dict[str, object]:
        return {
            "schema": "gzkit.arb.step_receipt.v1",
            "run_id": "arb-step-codexadversary-" + "0" * 32,
            "exit_status": exit_status,
            "step": {"name": "codexadversary", "command": command},
        }

    def test_argv_invoking_codex_proves_cross_vendor(self) -> None:
        self.assertTrue(_receipt_proves_cross_vendor(self._receipt(["codex", "exec", "refute"])))

    def test_plugin_dispatch_through_a_runtime_wrapper_proves_cross_vendor(self) -> None:
        """The operator-mandated tier-1 surface runs `node .../codex-companion.mjs`.

        A scan reading argv[0] alone saw "node" and refused the claim, so the
        2026-08-25 directive making the Codex PLUGIN the only permitted tier-1
        surface (and FORBIDDING `codex exec`) made a tier-1 claim structurally
        unclaimable for any OBPI that obeyed it. Both rules landed the same day.
        """
        self.assertTrue(
            _receipt_proves_cross_vendor(
                self._receipt(
                    [
                        "node",
                        "/Users/x/.claude/plugins/cache/openai-codex/codex/1.0.6/"
                        "scripts/codex-companion.mjs",
                        "adversarial-review",
                        "--wait",
                    ]
                )
            )
        )

    def test_a_wrapper_fronting_a_same_vendor_binary_does_not_prove_cross_vendor(self) -> None:
        """Walking past a wrapper must not become walking until something matches."""
        self.assertFalse(
            _receipt_proves_cross_vendor(self._receipt(["node", "/x/claude-helper.mjs", "review"]))
        )

    def test_a_vendor_named_only_in_the_prompt_does_not_prove_cross_vendor(self) -> None:
        """The adversary PROMPT is in argv and routinely names vendors.

        Stopping at the first non-wrapper is what keeps a MENTIONED vendor from
        satisfying the gate — the fail-open this function exists to close. A scan
        that kept walking would accept this receipt.
        """
        self.assertFalse(
            _receipt_proves_cross_vendor(
                self._receipt(["node", "/x/claude-helper.mjs", "please ask codex to refute this"])
            )
        )

    def test_an_argv_of_only_wrappers_does_not_prove_cross_vendor(self) -> None:
        self.assertFalse(_receipt_proves_cross_vendor(self._receipt(["node", "uv"])))

    def test_windows_runtime_wrappers_reach_the_executed_vendor(self) -> None:
        """Windows interpreter spellings must preserve the same dispatch proof."""
        for command in (
            [r"C:\project\.venv\Scripts\python.exe", "codex-fixture.py"],
            ["python3.exe", "codex-fixture.py"],
            [r"C:\Program Files\nodejs\NODE.EXE", "codex-companion.mjs"],
            ["uv.exe", "python.exe", "codex-fixture.py"],
        ):
            with self.subTest(command=command):
                self.assertTrue(_receipt_proves_cross_vendor(self._receipt(command)))

    def test_windows_wrapper_normalization_does_not_skip_non_wrappers(self) -> None:
        """A suffix must not turn prompt text or an unknown executable into proof."""
        for command in (
            ["node.exe", "claude-helper.mjs", "codex"],
            ["unknown.exe", "codex"],
            ["uv.exe", "python.exe"],
            ["node.exe.exe", "codex-companion.mjs"],
        ):
            with self.subTest(command=command):
                self.assertFalse(_receipt_proves_cross_vendor(self._receipt(command)))

    def test_absolute_binary_path_still_proves_cross_vendor(self) -> None:
        # The recorded argv may carry a resolved path; the binary name is the claim.
        self.assertTrue(
            _receipt_proves_cross_vendor(self._receipt(["/opt/homebrew/bin/codex", "exec"]))
        )

    def test_windows_binary_path_still_proves_cross_vendor(self) -> None:
        # .claude/rules/cross-platform.md: platforms are co-equal.
        self.assertTrue(
            _receipt_proves_cross_vendor(self._receipt([r"C:\tools\codex.exe", "exec"]))
        )

    def test_argv_invoking_a_claude_family_tool_does_not_prove_cross_vendor(self) -> None:
        self.assertFalse(_receipt_proves_cross_vendor(self._receipt(["claude", "-p", "refute"])))

    def test_a_receipt_whose_argv_merely_mentions_codex_does_not_prove(self) -> None:
        # The distinction the name channel structurally cannot make: the binary that
        # ran is `echo`, and "codex" is an argument to it.
        self.assertFalse(_receipt_proves_cross_vendor(self._receipt(["echo", "codex ran, honest"])))

    def test_malformed_receipts_do_not_prove(self) -> None:
        for receipt in (
            {},
            {"step": {}},
            {"step": {"command": []}},
            {"step": "not-a-mapping"},
        ):
            with self.subTest(receipt=receipt):
                self.assertFalse(_receipt_proves_cross_vendor(receipt))


class TestReceiptReachesTheLedger(unittest.TestCase):
    """GHI #765: the resolved receipt id must outlive the session, like the tier."""

    def test_receipt_id_reaches_the_serialized_ledger_record(self) -> None:
        event = _build_adversarial_event(
            obpi_id="OBPI-0.33.0-01-airlock-data-model-and-events",
            verdict="not-refuted",
            adversary="independent Codex subagent",
            job_id=None,
            refuted_claim=None,
            resolution=None,
            tier=1,
            receipt="arb-step-codexadversary-" + "a" * 32,
        )
        assert event is not None
        self.assertEqual(
            event.model_dump()["adversary_receipt"],
            "arb-step-codexadversary-" + "a" * 32,
        )

    def test_absent_receipt_is_omitted_rather_than_recorded_as_null(self) -> None:
        event = _build_adversarial_event(
            obpi_id="OBPI-0.33.0-01-airlock-data-model-and-events",
            verdict="not-refuted",
            adversary="codex/gpt-5.4",
            job_id=None,
            refuted_claim=None,
            resolution=None,
            tier=None,
            receipt=None,
        )
        assert event is not None
        self.assertNotIn("adversary_receipt", event.model_dump())


if __name__ == "__main__":
    unittest.main()
