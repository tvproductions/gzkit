"""Closeout + audit fidelity-gate integration (ADR-0.0.73, OBPI-0.0.73-04).

Both ceremonies invoke the SAME bound fidelity gate
(``gzkit.fidelity.assert_fidelity_for_ceremony``), replacing the prose
'Demonstrate Value' step — one gate, two consumers.

Tests derive from the brief's Acceptance Criteria, not from implementation:

- REQ-0.0.73-04-01 [BEHAVIOR]: closeout invokes the gate and fails the ceremony
  when any fidelity assertion fails.
- REQ-0.0.73-04-02 [BEHAVIOR]: audit invokes the same standalone gate (one gate,
  two consumers).
- REQ-0.0.73-04-03 [BEHAVIOR]: a missing ## Fidelity Assertions block is flagged
  (the prose 'Demonstrate Value' step is gone) rather than silently accepted.
  Absence policy is graceful-warning (operator-ratified 2026-06-17): absence
  warns but does not hard-block mid-flight; presence is enforced at ADR closeout
  (Boundary Invariant #4).
"""

from __future__ import annotations

import shlex
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from gzkit.core.exceptions import PolicyBreachError
from gzkit.fidelity import assert_fidelity_for_ceremony
from gzkit.traceability import covers


def _py_exit(code: int) -> str:
    """Cross-platform stand-in for the Unix ``true``/``false`` builtins.

    The ceremony gate runs each assertion command via
    ``subprocess.run(shlex.split(...), shell=False)``; ``true``/``false`` are
    shell builtins, not executables, so they return ``observed=-1`` on Windows.
    A quoted ``python -c 'raise SystemExit(<code>)'`` exits deterministically on
    every platform and survives the runner's POSIX ``shlex.split``.
    """
    return f"{shlex.quote(sys.executable)} -c {shlex.quote(f'raise SystemExit({code})')}"


# ---------------------------------------------------------------------------
# ADR fixtures
# ---------------------------------------------------------------------------

_ADR_FAILING = textwrap.dedent(f"""\
    ---
    id: ADR-test-fid
    ---

    # ADR Test

    ## Decision

    A decision with a fidelity assertion that fails.

    ## Fidelity Assertions

    | Claim | Command | Expected exit |
    |-------|---------|---------------|
    | This gate always fails | {_py_exit(1)} | 0 |
    """)

_ADR_PASSING = textwrap.dedent(f"""\
    ---
    id: ADR-test-fid
    ---

    # ADR Test

    ## Decision

    A decision with a fidelity assertion that passes.

    ## Fidelity Assertions

    | Claim | Command | Expected exit |
    |-------|---------|---------------|
    | This gate always passes | {_py_exit(0)} | 0 |
    """)

_ADR_NO_BLOCK = textwrap.dedent("""\
    ---
    id: ADR-test-fid
    ---

    # ADR Test

    ## Decision

    A decision with no Fidelity Assertions block — the prose 'Demonstrate Value'
    surface that this OBPI removes.

    ## Consequences

    None.
    """)


def _write_adr(tmpdir: Path, content: str) -> Path:
    path = tmpdir / "ADR-test-fid.md"
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# The shared gate — assert_fidelity_for_ceremony (one gate, two consumers)
# ---------------------------------------------------------------------------


class TestSharedFidelityGate(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.73-04-01")
    @covers("REQ-0.0.73-04-02")
    def test_failing_assertion_raises_policy_breach(self) -> None:
        """A present block with a failing assertion hard-fails the gate — the
        behaviour both closeout (REQ-01) and audit (REQ-02) inherit."""
        adr = _write_adr(self._dir, _ADR_FAILING)
        with self.assertRaises(PolicyBreachError) as ctx:
            assert_fidelity_for_ceremony(adr, "ADR-test-fid")
        self.assertIn("Fidelity gate", str(ctx.exception))
        self.assertIn("failed", str(ctx.exception))

    @covers("REQ-0.0.73-04-01")
    def test_passing_assertion_returns_results(self) -> None:
        adr = _write_adr(self._dir, _ADR_PASSING)
        results = assert_fidelity_for_ceremony(adr, "ADR-test-fid")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].result, "pass")

    @covers("REQ-0.0.73-04-03")
    def test_absent_block_flags_warning_without_blocking(self) -> None:
        """Absence is flagged (the prose step is gone) but, per the ratified
        graceful-migration policy, does not hard-block — it returns no
        assertions and emits a warning rather than raising."""
        adr = _write_adr(self._dir, _ADR_NO_BLOCK)
        # A stderr warning is emitted; no PolicyBreachError is raised.
        with mock.patch("rich.console.Console.print") as warn:
            results = assert_fidelity_for_ceremony(adr, "ADR-test-fid")
        self.assertEqual(results, [])
        self.assertTrue(warn.called, "absence must be flagged with a warning")
        warned_text = " ".join(str(c.args[0]) for c in warn.call_args_list if c.args)
        self.assertIn("Fidelity Assertions", warned_text)


# ---------------------------------------------------------------------------
# REQ-0.0.73-04-02: one gate, two consumers — closeout and audit share it
# ---------------------------------------------------------------------------


class TestOneGateTwoConsumers(unittest.TestCase):
    @covers("REQ-0.0.73-04-02")
    def test_both_ceremonies_import_the_same_gate(self) -> None:
        """closeout and audit must invoke the identical gate function object —
        not two prose copies of the check (ADR-0.0.73 Decision part 4)."""
        from gzkit import fidelity
        from gzkit.commands import audit_cmd, closeout_ceremony

        # audit binds the symbol at module import; closeout imports it locally
        # inside _gate_closeout_proof. Both must resolve to the one function.
        self.assertIs(audit_cmd.assert_fidelity_for_ceremony, fidelity.assert_fidelity_for_ceremony)
        src = Path(closeout_ceremony.__file__).read_text(encoding="utf-8")
        self.assertIn("assert_fidelity_for_ceremony", src)


# ---------------------------------------------------------------------------
# REQ-0.0.73-04-01: closeout ceremony wiring (EXECUTE -> ATTESTATION edge)
# ---------------------------------------------------------------------------


class TestCloseoutWiring(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self._dir = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _execute_state(self):
        from gzkit.commands.ceremony_state import CeremonyState, CeremonyStep

        return CeremonyState(
            adr_id="ADR-test-fid",
            current_step=CeremonyStep.EXECUTE,
            is_foundation=False,
            started_at="2026-06-17T10:00:00Z",
            updated_at="2026-06-17T10:00:00Z",
        )

    @covers("REQ-0.0.73-04-01")
    def test_closeout_gate_blocks_on_failing_fidelity(self) -> None:
        from gzkit.commands.closeout_ceremony import _gate_closeout_proof

        adr = _write_adr(self._dir, _ADR_FAILING)
        with (
            mock.patch(
                "gzkit.governance.trust_audits.closeout_proof.validate_closeout_proof",
                return_value=[],
            ),
            mock.patch(
                "gzkit.commands.closeout_ceremony.ensure_initialized", return_value=mock.MagicMock()
            ),
            mock.patch(
                "gzkit.commands.common.resolve_adr_file",
                return_value=(adr, "ADR-test-fid"),
            ),
            self.assertRaises(PolicyBreachError),
        ):
            _gate_closeout_proof(self._dir, self._execute_state())

    def test_closeout_gate_skips_when_adr_unresolvable(self) -> None:
        """If the ADR file cannot be resolved there is nothing to gate — the
        closeout-proof gate must not crash."""
        from gzkit.commands.closeout_ceremony import _gate_closeout_proof
        from gzkit.commands.common import GzCliError

        with (
            mock.patch(
                "gzkit.governance.trust_audits.closeout_proof.validate_closeout_proof",
                return_value=[],
            ),
            mock.patch(
                "gzkit.commands.closeout_ceremony.ensure_initialized", return_value=mock.MagicMock()
            ),
            mock.patch(
                "gzkit.commands.common.resolve_adr_file",
                side_effect=GzCliError("ADR not found: ADR-test-fid"),
            ),
        ):
            # Must return cleanly, not raise.
            _gate_closeout_proof(self._dir, self._execute_state())


# ---------------------------------------------------------------------------
# REQ-0.0.73-04-02: audit ceremony wiring (gate runs before the receipt)
# ---------------------------------------------------------------------------


class TestAuditWiring(unittest.TestCase):
    @covers("REQ-0.0.73-04-02")
    def test_audit_invokes_gate_before_validation_receipt(self) -> None:
        """audit_cmd must call assert_fidelity_for_ceremony, and it must run
        BEFORE the validation receipt is emitted so a fidelity failure cannot
        record a false 'validated'."""
        import inspect

        from gzkit.commands import audit_cmd as audit_mod

        src = inspect.getsource(audit_mod.audit_cmd)
        gate_pos = src.find("assert_fidelity_for_ceremony(")
        receipt_pos = src.find("audit_receipt_emitted_event")
        self.assertNotEqual(gate_pos, -1, "audit_cmd must invoke the fidelity gate")
        self.assertNotEqual(receipt_pos, -1)
        self.assertLess(
            gate_pos,
            receipt_pos,
            "fidelity gate must run before the validation receipt is emitted",
        )


if __name__ == "__main__":
    unittest.main()
