"""Tests for the Step-4b adversarial-validation completion gate (GHI #676).

Assertions derive from the requirement — `gz obpi complete` must fail closed on a
missing or unresolved adversary verdict — not from a run of the implementation.

Every block assertion captures stdout, even when it asserts only the exit (GHI
#705). ``_fail``'s non-JSON branch renders through the shared Rich console, which
resolves ``sys.stdout`` at print time, so an uncaptured block writes its full
recovery prose into the suite's own stdout. Any wrapper that echoes a subordinate
command's output — ``gz gates`` via ``_print_command_output`` — then replays that
prose as its own error, making a passing Gate 2 read as a hard block.
"""

from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.obpi_complete_adversarial import (
    ADVERSARY_VERDICTS,
    _build_adversarial_event,
    _enforce_adversarial_validation,
    _is_cross_vendor_adversary,
    _receipt_proves_cross_vendor,
)
from gzkit.events import parse_typed_event


def _enforce(**overrides: object) -> None:
    kwargs: dict[str, object] = {
        "obpi_id": "OBPI-0.33.0-01-airlock-data-model-and-events",
        "parent_lane": "heavy",
        "verdict": "not-refuted",
        "adversary": "claude/general-purpose",
        "resolution": None,
        "as_json": False,
        "fallback_reason": "codex setup reported ready=false (not authenticated)",
    }
    kwargs.update(overrides)
    _enforce_adversarial_validation(**kwargs)


class _ReceiptFixture(unittest.TestCase):
    """Write real ARB step receipts under a temp root.

    Shared because three suites need receipts since GHI #780: a cross-vendor claim
    is admissible only on receipt proof, so every test that exercises an admissible
    tier-1 path must produce the artifact rather than assert around it.
    """

    def setUp(self) -> None:
        self._dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.root = Path(self._dir.name)

    def _write(self, run_id: str, command: list[str], *, exit_status: int = 0) -> str:
        payload = {
            "schema": "gzkit.arb.step_receipt.v1",
            "run_id": run_id,
            "exit_status": exit_status,
            "step": {"name": "codexadversary", "command": command},
        }
        (self.root / f"{run_id}.json").write_text(json.dumps(payload), encoding="utf-8")
        return run_id

    def _codex_receipt(self, suffix: str = "a") -> str:
        """Return a receipt id proving a genuine Codex run."""
        return self._write("arb-step-codexadversary-" + suffix * 32, ["codex", "exec"])


class TestAdversarialValidationGate(unittest.TestCase):
    def test_verdict_vocabulary_is_closed_to_exactly_four_members(self) -> None:
        self.assertEqual(
            ADVERSARY_VERDICTS,
            ("refuted", "not-refuted", "refuted-with-caveats", "degraded-human-only"),
        )

    def test_heavy_lane_blocks_when_verdict_absent(self) -> None:
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(verdict=None)

    def test_heavy_lane_blocks_when_adversary_absent(self) -> None:
        # A verdict with no named adversary cannot be audited: "who refuted it?"
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary=None)

    def test_refuted_without_resolution_blocks(self) -> None:
        # Never hand the operator a known refutation dressed as clean.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(verdict="refuted", resolution=None)

    def test_refuted_with_resolution_passes(self) -> None:
        _enforce(verdict="refuted", resolution="membership assertions added; mutation now FAILS")

    def test_degraded_human_only_is_recordable(self) -> None:
        # The skill's degraded floor must be an explicit, attested value —
        # never silence indistinguishable from a passing adversary.
        _enforce(verdict="degraded-human-only", adversary="human")

    def test_not_refuted_passes_without_resolution(self) -> None:
        _enforce(verdict="not-refuted", resolution=None)

    def test_lite_lane_is_exempt(self) -> None:
        # The gate rides the lane that already carries fail-closed Gate 3/4.
        _enforce(parent_lane="lite", verdict=None, adversary=None)

    def test_block_message_names_cause_and_runnable_next_step(self) -> None:
        # .claude/rules/guardrail-feedback-prose.md: the block must state what
        # failed, why it is forbidden, and a runnable next step. A bare exit code
        # forces the next agent to reconstruct intent from training memory.
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(buffer):
            _enforce(verdict=None, as_json=True)
        error = json.loads(buffer.getvalue())["error"]
        self.assertIn("adversarial validation", error.lower())
        self.assertIn("--adversary-verdict", error)
        self.assertIn("degraded-human-only", error)

    def test_refuted_block_message_demands_resolution(self) -> None:
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(buffer):
            _enforce(verdict="refuted", resolution=None, as_json=True)
        error = json.loads(buffer.getvalue())["error"]
        self.assertIn("refuted", error)
        self.assertIn("--adversary-resolution", error)


class TestStep4bTierBindingGate(_ReceiptFixture):
    """GHI #678: a tier-2 (Claude-family) adversary verdict must justify the fallback.

    Codex (tier 1, a different vendor) is REQUIRED first — a Claude validating Claude
    shares this agent's blind spots. A Claude-family adversary is admissible only when
    Codex was genuinely unavailable, and that reason must be recorded, not assumed.
    """

    def test_proven_cross_vendor_adversary_needs_no_fallback_reason(self) -> None:
        # A tier-1 adversary owes no unavailability reason — but since GHI #780 the
        # tier-1 claim itself must be PROVEN, so the receipt is what makes this path
        # admissible. The name alone no longer buys the exemption.
        _enforce(
            adversary="codex/gpt-5.4",
            receipt=self._codex_receipt(),
            receipts_root=self.root,
            fallback_reason=None,
        )

    def test_human_floor_needs_no_fallback_reason(self) -> None:
        # The degraded floor is already explicit via its verdict — no reason demanded.
        _enforce(verdict="degraded-human-only", adversary="human", fallback_reason=None)

    def test_claude_family_adversary_without_fallback_reason_blocks(self) -> None:
        # A Claude subagent that ran because it was convenient — not because Codex was
        # unavailable — is the exact GHI #678 bypass. Fail closed.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="claude/general-purpose", fallback_reason=None)

    def test_claude_family_adversary_with_fallback_reason_passes(self) -> None:
        _enforce(
            adversary="claude/general-purpose",
            fallback_reason="codex setup reported ready=false (not authenticated)",
        )

    def test_unrecognized_adversary_fails_closed_without_reason(self) -> None:
        # An unrecognized vendor is treated as NOT cross-vendor — must justify.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="mystery-model-x", fallback_reason=None)

    def test_claude_block_message_names_codex_and_next_step(self) -> None:
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(buffer):
            _enforce(adversary="claude/general-purpose", fallback_reason=None, as_json=True)
        error = json.loads(buffer.getvalue())["error"].lower()
        self.assertIn("codex", error)
        self.assertIn("--adversary-fallback-reason", error)


class TestDeclaredTierGovernsOverNameInference(_ReceiptFixture):
    """GHI #678 reopened: tier was INFERRED from a caller-supplied string, never recorded.

    `_is_cross_vendor_adversary` prefix-scans the adversary name, so "names something
    codex-shaped" and "ran on Codex" were the same claim, with no corroborating artifact
    required. A declared tier is the recorded claim; these assertions derive from the
    requirement that the declaration governs and that a declaration contradicting the
    name fails closed — the contradiction the name scan cannot see by construction.

    Since GHI #780 the declaration governs but no longer AUTHORIZES: precedence still
    reads proven > declared > inferred, and only the proven rung admits a tier-1 claim.
    """

    def test_declared_tier_1_with_cross_vendor_name_passes_on_proof(self) -> None:
        _enforce(
            adversary="codex/gpt-5.4",
            tier=1,
            receipt=self._codex_receipt(),
            receipts_root=self.root,
            fallback_reason=None,
        )

    def test_declared_tier_1_with_claude_family_name_blocks(self) -> None:
        # Claiming a different vendor re-derived the completion while naming a
        # same-vendor adversary is a contradiction; the pre-fix gate passed it,
        # because the name scan alone decided the tier.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="claude/general-purpose", tier=1, fallback_reason=None)

    def test_declared_tier_2_still_requires_reason_despite_cross_vendor_name(self) -> None:
        # The declaration governs: a tier-2 run does not become tier 1 by being
        # named after a tier-1 vendor. Pre-fix, the name exempted it outright.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="codex/gpt-5.4", tier=2, fallback_reason=None)

    def test_declared_tier_2_with_reason_passes(self) -> None:
        _enforce(
            adversary="claude/general-purpose",
            tier=2,
            fallback_reason="codex setup reported ready=false (not authenticated)",
        )

    def test_undeclared_tier_no_longer_authorizes_by_name_alone(self) -> None:
        # REVERSED by GHI #780. This asserted the opposite until 2026-08-09: an
        # undeclared tier resolved cross-vendor from the NAME, on the stated ground
        # that "backward compatibility is load-bearing" for events predating the flag.
        # Measurement retired that ground — of 17 recorded adversarial_validation
        # events, ZERO carry a tier and 14 resolved cross-vendor by name, so the
        # compatibility path was not a legacy tail, it was the only path in use and
        # the whole of the self-assertion surface GHI #765 named.
        #
        # The gate is a completion-time check over the invocation in hand; it never
        # re-reads historical events, so nothing recorded is retroactively invalidated.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="codex/gpt-5.4", tier=None, fallback_reason=None)
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="claude/general-purpose", tier=None, fallback_reason=None)

    def test_human_floor_is_exempt_from_tier_binding(self) -> None:
        _enforce(verdict="degraded-human-only", adversary="human", tier=3, fallback_reason=None)

    def test_contradiction_block_message_names_both_halves_and_next_step(self) -> None:
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(buffer):
            _enforce(
                adversary="claude/general-purpose",
                tier=1,
                fallback_reason=None,
                as_json=True,
            )
        error = json.loads(buffer.getvalue())["error"]
        self.assertIn("--adversary-tier 1", error)
        self.assertIn("claude/general-purpose", error)
        self.assertIn("--adversary-tier 2", error)
        self.assertIn("--adversary-fallback-reason", error)


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
        kwargs = gate.call_args.kwargs
        self.assertEqual(kwargs["obpi_id"], obpi_id)
        self.assertEqual(kwargs["parent_lane"], "heavy")
        self.assertIsNone(kwargs["verdict"])
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
                "_enforce_adversarial_validation",
                side_effect=SystemExit(1) if gate_raises else None,
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


class TestReceiptGovernsTheDeclaredTier(_ReceiptFixture):
    """GHI #765: a receipt that contradicts the declared tier fails closed.

    Precedence is proven > declared > inferred. A caller declaring tier 1 while
    supplying a receipt whose argv ran a same-family tool is asserting against
    evidence it supplied itself; that contradiction must block, not pass.
    """

    def test_receipt_proving_codex_admits_tier_1_without_fallback_reason(self) -> None:
        run_id = self._codex_receipt()
        _enforce(
            adversary="independent Codex subagent",
            tier=1,
            receipt=run_id,
            receipts_root=self.root,
            fallback_reason=None,
        )

    def test_unresolvable_receipt_blocks(self) -> None:
        # A receipt id naming no file on disk is the fabrication case.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(tier=1, receipt="arb-step-codexadversary-" + "f" * 32, receipts_root=self.root)

    def test_receipt_recording_a_failed_run_blocks(self) -> None:
        run_id = self._write(
            "arb-step-codexadversary-" + "b" * 32, ["codex", "exec"], exit_status=1
        )
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(tier=1, receipt=run_id, receipts_root=self.root)

    def test_declared_tier_1_contradicting_the_receipt_argv_blocks(self) -> None:
        run_id = self._write("arb-step-codexadversary-" + "c" * 32, ["claude", "-p", "refute"])
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="codex/gpt-5.4", tier=1, receipt=run_id, receipts_root=self.root)

    def test_block_message_names_the_receipt_and_a_runnable_next_step(self) -> None:
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(buffer):
            _enforce(
                tier=1,
                receipt="arb-step-codexadversary-" + "f" * 32,
                receipts_root=self.root,
                as_json=True,
            )
        error = json.loads(buffer.getvalue())["error"]
        self.assertIn("--adversary-receipt", error)
        self.assertIn("gz arb step", error)


class TestCrossVendorClaimRequiresReceipt(_ReceiptFixture):
    """GHI #780: a cross-vendor claim is admissible ONLY on receipt proof.

    GHI #765 made the receipt channel authoritative when cited and left it optional
    when absent, which closed nothing: the gate cannot tell "no receipt because the
    adversary could not be wrapped" from "no receipt because none was run", so the
    honest and the hollow completion remained the same input. These assertions derive
    from that requirement — every rung of the precedence ladder below `proven` is a
    string the claiming agent typed, so neither may authorize on its own.

    Scope is the resolved claim, not the declared one. Gating `--adversary-tier 1`
    alone would fence a path no recorded completion has ever used: of 17
    `adversarial_validation` events, zero declare a tier and 14 resolved cross-vendor
    through the name scan.
    """

    def test_cross_vendor_name_without_receipt_blocks(self) -> None:
        # The 14-of-17 shape: a codex-shaped name, no tier, no receipt.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="codex/gpt-5.4", tier=None, fallback_reason=None)

    def test_declared_tier_1_without_receipt_blocks(self) -> None:
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(adversary="codex/gpt-5.4", tier=1, fallback_reason=None)

    def test_a_fallback_reason_does_not_buy_a_tier_1_claim(self) -> None:
        # Recording why Codex was unavailable is the tier-2 path; it must not
        # launder an unproven tier-1 claim into admissibility.
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(
                adversary="codex/gpt-5.4",
                tier=1,
                fallback_reason="codex setup reported ready=false",
            )

    def test_proven_cross_vendor_claim_passes(self) -> None:
        _enforce(
            adversary="codex/gpt-5.4",
            tier=1,
            receipt=self._codex_receipt(),
            receipts_root=self.root,
            fallback_reason=None,
        )

    def test_tier_2_fallback_remains_usable_without_any_receipt(self) -> None:
        # Load-bearing: an unavailable Codex must stay RECORDABLE. If the only
        # admissible shape required a receipt, the honest degraded run would have
        # no path and the gate would push callers toward a false tier-1 claim.
        _enforce(
            adversary="claude/general-purpose",
            tier=2,
            fallback_reason="codex setup reported ready=false (not authenticated)",
        )

    def test_human_degraded_floor_remains_exempt(self) -> None:
        _enforce(verdict="degraded-human-only", adversary="human", fallback_reason=None)

    def test_receipt_proving_a_claude_family_run_still_demands_a_reason(self) -> None:
        # A receipt resolves the claim DOWN as well as up: argv that ran a
        # same-family tool proves not-cross-vendor, which lands on the tier-2 rule.
        run_id = self._write("arb-step-codexadversary-" + "d" * 32, ["claude", "-p", "refute"])
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(io.StringIO()):
            _enforce(
                adversary="claude/general-purpose",
                tier=None,
                receipt=run_id,
                receipts_root=self.root,
                fallback_reason=None,
            )

    def test_block_message_names_the_receipt_flag_and_the_tier_2_escape(self) -> None:
        # .claude/rules/guardrail-feedback-prose.md: name what failed, why it is
        # forbidden, and a runnable next step — here BOTH exits, since a caller
        # who genuinely cannot wrap the run needs the fallback path spelled out.
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(buffer):
            _enforce(adversary="codex/gpt-5.4", tier=None, fallback_reason=None, as_json=True)
        error = json.loads(buffer.getvalue())["error"]
        self.assertIn("--adversary-receipt", error)
        self.assertIn("gz arb step", error)
        self.assertIn("--adversary-tier 2", error)
        self.assertIn("--adversary-fallback-reason", error)


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
