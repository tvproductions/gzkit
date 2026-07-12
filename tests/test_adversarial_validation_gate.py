"""Tests for the Step-4b adversarial-validation completion gate (GHI #676).

Assertions derive from the requirement — `gz obpi complete` must fail closed on a
missing or unresolved adversary verdict — not from a run of the implementation.
"""

from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest import mock

from gzkit.commands.obpi_complete import (
    ADVERSARY_VERDICTS,
    _enforce_adversarial_validation,
)


def _enforce(**overrides: object) -> None:
    kwargs: dict[str, object] = {
        "obpi_id": "OBPI-0.33.0-01-airlock-data-model-and-events",
        "parent_lane": "heavy",
        "verdict": "not-refuted",
        "adversary": "codex/gpt-5.4",
        "resolution": None,
        "as_json": False,
        "fallback_reason": None,
    }
    kwargs.update(overrides)
    _enforce_adversarial_validation(**kwargs)  # ty: ignore


class TestAdversarialValidationGate(unittest.TestCase):
    def test_verdict_vocabulary_is_closed_to_exactly_four_members(self) -> None:
        self.assertEqual(
            ADVERSARY_VERDICTS,
            ("refuted", "not-refuted", "refuted-with-caveats", "degraded-human-only"),
        )

    def test_heavy_lane_blocks_when_verdict_absent(self) -> None:
        with self.assertRaises(SystemExit):
            _enforce(verdict=None)

    def test_heavy_lane_blocks_when_adversary_absent(self) -> None:
        # A verdict with no named adversary cannot be audited: "who refuted it?"
        with self.assertRaises(SystemExit):
            _enforce(adversary=None)

    def test_refuted_without_resolution_blocks(self) -> None:
        # Never hand the operator a known refutation dressed as clean.
        with self.assertRaises(SystemExit):
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


class TestStep4bTierBindingGate(unittest.TestCase):
    """GHI #678: a tier-2 (Claude-family) adversary verdict must justify the fallback.

    Codex (tier 1, a different vendor) is REQUIRED first — a Claude validating Claude
    shares this agent's blind spots. A Claude-family adversary is admissible only when
    Codex was genuinely unavailable, and that reason must be recorded, not assumed.
    """

    def test_cross_vendor_adversary_needs_no_fallback_reason(self) -> None:
        # codex/... is the tier-1 cross-vendor adversary — always admissible.
        _enforce(adversary="codex/gpt-5.4", fallback_reason=None)

    def test_human_floor_needs_no_fallback_reason(self) -> None:
        # The degraded floor is already explicit via its verdict — no reason demanded.
        _enforce(verdict="degraded-human-only", adversary="human", fallback_reason=None)

    def test_claude_family_adversary_without_fallback_reason_blocks(self) -> None:
        # A Claude subagent that ran because it was convenient — not because Codex was
        # unavailable — is the exact GHI #678 bypass. Fail closed.
        with self.assertRaises(SystemExit):
            _enforce(adversary="claude/general-purpose", fallback_reason=None)

    def test_claude_family_adversary_with_fallback_reason_passes(self) -> None:
        _enforce(
            adversary="claude/general-purpose",
            fallback_reason="codex setup reported ready=false (not authenticated)",
        )

    def test_unrecognized_adversary_fails_closed_without_reason(self) -> None:
        # An unrecognized vendor is treated as NOT cross-vendor — must justify.
        with self.assertRaises(SystemExit):
            _enforce(adversary="mystery-model-x", fallback_reason=None)

    def test_claude_block_message_names_codex_and_next_step(self) -> None:
        buffer = io.StringIO()
        with self.assertRaises(SystemExit), contextlib.redirect_stdout(buffer):
            _enforce(adversary="claude/general-purpose", fallback_reason=None, as_json=True)
        error = json.loads(buffer.getvalue())["error"].lower()
        self.assertIn("codex", error)
        self.assertIn("--adversary-fallback-reason", error)


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


if __name__ == "__main__":
    unittest.main()
