"""CLI tests for `gz validate --evaluation-justify-binding` exit-code routing.

Regression coverage for GHI #394: the dedicated solo handler at
``_run_evaluation_justify_binding_solo`` was unreachable because the
``_other_scopes_active`` predicate self-included the flag, forcing the
solo branch's ``and not _other_scopes_active`` guard to evaluate False
and the run to fall through to the generic validator path.  The generic
path mapped ``evaluation-justify-binding`` errors to exit 1 instead of
the policy-breach exit 3 that ADR-0.0.26 / OBPI-0.0.26-02 REQ-02-01
prescribes.

These tests pin both code paths:

- Solo path: when only ``--evaluation-justify-binding`` is set, the
  dedicated handler fires and exits 3 on violation, 0 when clean.
- Combined-flag path: when other scopes are active *alongside*
  ``--evaluation-justify-binding`` and the gate produces violations,
  the generic validator path also exits 3 because the error type is
  registered in ``_POLICY_BREACH_ERROR_TYPES``.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands import validate_cmd
from gzkit.governance.trust_audits.evaluation_justify_binding import ValidationError
from gzkit.traceability import covers


def _binding_violation(artifact: str = "ADR-0.0.fixture") -> ValidationError:
    """Return a single synthetic evaluation-justify-binding violation."""
    return ValidationError(
        type="evaluation-justify-binding",
        artifact=artifact,
        message="missing gz-justify artifact for low score",
    )


class TestSoloHandlerFiresWhenOnlyFlagSet(unittest.TestCase):
    """GHI #394: ``--evaluation-justify-binding`` alone routes to the solo handler."""

    @covers("REQ-0.0.26-02-01")
    def test_solo_handler_invoked_when_no_other_scope_active(self) -> None:
        """``_run_evaluation_justify_binding_solo`` is called with the artifact id."""
        with (
            mock.patch.object(validate_cmd, "get_project_root", return_value=Path(".")),
            mock.patch.object(validate_cmd, "_run_evaluation_justify_binding_solo") as solo,
        ):
            # The mocked solo handler returns normally instead of raising
            # SystemExit (which the real handler does); the contract under
            # test is that the dispatch routes to the solo handler at all.
            validate_cmd.validate(
                check_manifest=False,
                check_documents=False,
                check_surfaces=False,
                check_ledger=False,
                check_instructions=False,
                check_briefs=False,
                check_evaluation_justify_binding="ADR-0.0.26",
            )
        solo.assert_called_once()
        # First positional arg is project_root, second is the sentinel/id.
        call_args = solo.call_args
        self.assertEqual(call_args.args[1], "ADR-0.0.26")


class TestSoloHandlerExitCodeContract(unittest.TestCase):
    """REQ-0.0.26-02-01: gate exits 3 with the failing dimension named."""

    @covers("REQ-0.0.26-02-01")
    def test_solo_handler_exits_3_on_violation(self) -> None:
        """A non-empty violation list raises SystemExit(3) from the solo handler."""
        with (
            mock.patch.object(
                validate_cmd,
                "_evaluation_justify_binding_runner",
                return_value=[_binding_violation()],
            ),
            self.assertRaises(SystemExit) as ctx,
        ):
            validate_cmd._run_evaluation_justify_binding_solo(
                Path("."),
                "ADR-0.0.fixture",
                as_json=False,
            )
        self.assertEqual(ctx.exception.code, 3)

    @covers("REQ-0.0.26-02-01")
    def test_solo_handler_exits_0_when_clean(self) -> None:
        """An empty violation list raises SystemExit(0) from the solo handler."""
        with (
            mock.patch.object(
                validate_cmd,
                "_evaluation_justify_binding_runner",
                return_value=[],
            ),
            self.assertRaises(SystemExit) as ctx,
        ):
            validate_cmd._run_evaluation_justify_binding_solo(
                Path("."),
                "ADR-0.0.fixture",
                as_json=False,
            )
        self.assertEqual(ctx.exception.code, 0)


class TestEvaluationJustifyBindingInPolicyBreachTypes(unittest.TestCase):
    """GHI #394 belt-and-suspenders: combined-flag path also exits 3 on this gate."""

    @covers("REQ-0.0.26-02-01")
    def test_error_type_registered_as_policy_breach(self) -> None:
        """``evaluation-justify-binding`` is in ``_POLICY_BREACH_ERROR_TYPES``.

        This pins the combined-flag path: when ``--evaluation-justify-binding``
        runs alongside another scope (e.g. ``--documents``) and the gate
        produces a violation, the generic validator path routes the error
        through ``_print_validation_result`` which exits 3 only when the
        error type is registered as a policy breach.  Without this
        registration, mixed runs masked the gate behind exit 1.
        """
        self.assertIn(
            "evaluation-justify-binding",
            validate_cmd._POLICY_BREACH_ERROR_TYPES,
            msg="evaluation-justify-binding must route through the exit-3 policy-breach path",
        )


class TestOtherScopesActivePredicateExcludesSelfFlag(unittest.TestCase):
    """GHI #394: ``_other_scopes_active`` must not self-include the eval-binding flag."""

    @covers("REQ-0.0.26-02-01")
    def test_predicate_source_does_not_self_include_eval_binding_flag(self) -> None:
        """Source guard: ``_other_scopes_active`` no longer self-includes the flag.

        The ``_other_scopes_active`` ``any([...])`` predicate at the
        dispatch site must not contain ``check_evaluation_justify_binding
        is not None`` as a list element — that self-reference is the
        GHI #394 defect.  Other uses of the same expression elsewhere
        in the file (the scopes dict that surfaces in JSON output) are
        legitimate and not part of this guard's scope.

        The guard inspects the slice of the source between the marker
        line opening the predicate and its closing bracket.
        """
        source = Path(validate_cmd.__file__).read_text(encoding="utf-8")
        marker = "_other_scopes_active = any("
        start = source.index(marker)
        end = source.index("    )", start)
        predicate_block = source[start:end]
        self.assertNotIn(
            "check_evaluation_justify_binding is not None",
            predicate_block,
            msg=(
                "GHI #394 regression: the self-reference in _other_scopes_active "
                "would re-disable the dedicated solo handler"
            ),
        )


if __name__ == "__main__":  # pragma: no cover - convenience runner
    unittest.main()


__all__: tuple[str, ...] = ()
