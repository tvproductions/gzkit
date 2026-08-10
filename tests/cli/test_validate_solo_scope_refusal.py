"""Solo-only validate scopes refuse combination instead of silently dropping.

GHI #704: six scopes in ``_dispatch_early_return_scopes`` carried an
``and not other_scopes_active`` guard. When combined with any other scope the
branch was skipped entirely and no diagnostic was emitted — the requested scope
never ran, yet ``gz validate`` reported ``✓ All validations passed``. The
failure is silent in the direction that matters: false green, never false red.

These tests assert the REQ semantics ("a requested scope either runs, or the
command refuses the invocation"), not the wording of the refusal.

No ``@covers`` decorator: this is GHI-tracked direct-fix repair with no parent
REQ, and ``.claude/rules/adr-audit.md`` § Rules reserves ``@covers`` for
BEHAVIOR REQs' proof channel.
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from gzkit.commands import validate_cmd

# The scopes that own their full 0/2/3 lifecycle and early-return. Six at
# GHI #704; `check_gate_callers` joined under GHI #785.
SOLO_ONLY_KWARGS: dict[str, object] = {
    "check_evaluation_justify_binding": "some-adr",
    "check_unscoped_rules": True,
    "check_sensitivity": True,
    "check_qc_binding": True,
    "check_fidelity_presence": True,
    "check_waiver_ratchet": True,
    "check_gate_callers": True,
}

_DISPATCH_DEFAULTS: dict[str, object] = {
    "check_distribution_regenerate": False,
    "check_distribution": False,
    "attestation_receipts": None,
    "attestation_lane": "lite",
    "attestation_kind": "feature",
    "check_evaluation_justify_binding": None,
    "check_unscoped_rules": False,
    "unscoped_rules_allowlist_only": False,
    "check_sensitivity": False,
    "sensitivity_explain": None,
    "check_qc_binding": False,
    "check_fidelity_presence": False,
    "check_waiver_ratchet": False,
    "check_gate_callers": False,
    "as_json": False,
}


def _dispatch(*, other_scopes_active: bool, **overrides: object) -> tuple[bool, str]:
    """Run the dispatcher, returning its verdict and everything it printed."""
    kwargs = {**_DISPATCH_DEFAULTS, **overrides}
    buf = io.StringIO()
    with redirect_stdout(buf), redirect_stderr(buf):
        handled = validate_cmd._dispatch_early_return_scopes(
            Path("."),
            other_scopes_active=other_scopes_active,
            **kwargs,
        )
    return handled, buf.getvalue()


class TestSoloScopeCombinationRefused(unittest.TestCase):
    """A solo-only scope combined with another scope must fail closed."""

    def test_every_solo_only_scope_refuses_when_combined(self) -> None:
        """Each of them exits non-zero rather than being silently dropped.

        Pre-fix, the dispatcher returned ``False`` (fall through to the
        aggregate path), so the run reported success for a scope never executed.
        """
        for flag, value in SOLO_ONLY_KWARGS.items():
            with self.subTest(scope=flag):
                with self.assertRaises(SystemExit) as ctx:
                    _dispatch(other_scopes_active=True, **{flag: value})
                self.assertNotEqual(
                    ctx.exception.code,
                    0,
                    f"{flag} combined with another scope must not exit 0",
                )

    def test_refusal_names_the_offending_scope_and_a_next_step(self) -> None:
        """Recovery prose carries the finding and a runnable next step.

        `.gzkit/rules/guardrail-feedback-prose.md` requires what-failed plus a
        governed next step, not a bare exit code.
        """
        buf = io.StringIO()
        with (
            redirect_stdout(buf),
            redirect_stderr(buf),
            self.assertRaises(SystemExit),
        ):
            validate_cmd._dispatch_early_return_scopes(
                Path("."),
                other_scopes_active=True,
                **{**_DISPATCH_DEFAULTS, "check_fidelity_presence": True},
            )
        output = buf.getvalue()
        self.assertIn("--fidelity-presence", output)
        self.assertIn("alone", output)


class TestSoloScopeStillRunsAlone(unittest.TestCase):
    """The refusal must not break the solo invocation it protects."""

    def test_no_refusal_when_no_other_scope_is_active(self) -> None:
        """With ``other_scopes_active=False`` the scope runs its own lifecycle.

        Guards the regression where a blanket refusal would break every solo
        run — the shape these scopes are actually used in.
        """
        with self.assertRaises(SystemExit) as ctx:
            _dispatch(other_scopes_active=False, check_fidelity_presence=True)
        # The scope's own 0/3 verdict, never the combination refusal's exit 1.
        self.assertIn(ctx.exception.code, (0, 3))

    def test_non_solo_invocation_is_untouched(self) -> None:
        """No solo-only scope requested → dispatch declines to handle."""
        handled, _ = _dispatch(other_scopes_active=True)
        self.assertFalse(handled)


if __name__ == "__main__":
    unittest.main()
