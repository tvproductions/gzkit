"""Consistency fence over the `gz validate` dispatch surfaces (#618).

The validate dispatch is hand-synced across several enumerations: the
``validate()`` signature (``check_*`` params), the early-return dispatch
(``_dispatch_early_return_scopes``), the runner registries
(``_default_scope_runners`` / ``_explicit_scope_runners``), and the argparse
forwarding lambda in ``parser_maintenance``. When these drift, a scope can be
*accepted at the CLI but never dispatched* — it passes ``gz validate --scope``
green while checking nothing (the #394 self-include class; the governance-facade
failure ADR-0.0.73 exists to kill).

This fence asserts the surfaces agree. It is the parity net the Magna Carta
Sanity-Reduction track (2026-06-19) requires before the surfaces are collapsed
to a single ``VALIDATOR_REGISTRY``: any collapse must keep this test green,
proving no scope was silently dropped. Cut #618, step 1.

It is deliberately introspection-based (no brittle source-regex of the
predicate / collect_errors lists): every ``check_*`` param MUST be dispatched
by a runner or the early-return path, and every runner/early-return scope MUST
have a param. That is the load-bearing invariant; the predicate and
``_collect_errors`` lists are optimizations over it.
"""

from __future__ import annotations

import inspect
import re
import unittest
from pathlib import Path

from gzkit.commands import validate_cmd


def _signature_check_params() -> set[str]:
    params = inspect.signature(validate_cmd.validate).parameters
    return {n for n in params if n.startswith("check_")}


def _early_return_check_params() -> set[str]:
    sig = inspect.signature(validate_cmd._dispatch_early_return_scopes)
    return {n for n in sig.parameters if n.startswith("check_")}


def _runner_check_params() -> set[str]:
    # Runner registries are keyed by scope stem (no ``check_`` prefix).
    root = Path(".")
    keys = set(validate_cmd._default_scope_runners(root, None)) | set(
        validate_cmd._explicit_scope_runners(root)
    )
    return {f"check_{k}" for k in keys}


class TestValidateDispatchConsistency(unittest.TestCase):
    """Fence: the validate dispatch surfaces may not drift apart (#618)."""

    def test_every_scope_param_is_dispatched(self) -> None:
        # The load-bearing invariant: a check_* param the CLI accepts must reach
        # a dispatch path. A param that is neither a runner nor an early-return
        # scope is accepted-but-never-run — the silent-bypass facade.
        sig = _signature_check_params()
        dispatched = _runner_check_params() | _early_return_check_params()
        orphans = sorted(sig - dispatched)
        self.assertEqual(
            orphans,
            [],
            f"validate() accepts these check_* params but no runner or early-return "
            f"path dispatches them — they pass `gz validate --scope` green while "
            f"checking nothing (#394 class): {orphans}",
        )

    def test_every_runner_has_a_scope_param(self) -> None:
        # The inverse: a runner with no param is unreachable from the CLI.
        sig = _signature_check_params()
        orphan_runners = sorted(_runner_check_params() - sig)
        self.assertEqual(
            orphan_runners,
            [],
            f"these runner registry keys have no matching check_* param on "
            f"validate(), so the CLI cannot reach them: {orphan_runners}",
        )

    def test_every_early_return_scope_has_a_scope_param(self) -> None:
        sig = _signature_check_params()
        orphan_er = sorted(_early_return_check_params() - sig)
        self.assertEqual(
            orphan_er,
            [],
            f"these early-return scopes have no matching check_* param: {orphan_er}",
        )

    def test_parser_lambda_forwards_every_scope_param(self) -> None:
        # The argparse forwarding lambda must pass every check_* param validate()
        # declares; a flag defined but not forwarded is dead at the CLI.
        sig = _signature_check_params()
        pm = Path("src/gzkit/cli/parser_maintenance.py").read_text(encoding="utf-8")
        block = re.search(r"p_validate\.set_defaults\((.*?)\n    \)", pm, re.S)
        self.assertIsNotNone(block, "could not locate p_validate.set_defaults block")
        assert block is not None  # narrow for ty
        lam = block.group(1)
        missing = sorted(p for p in sig if f"{p}=" not in lam)
        self.assertEqual(
            missing,
            [],
            f"the p_validate forwarding lambda does not pass these check_* params "
            f"to validate(), so their CLI flags are dead: {missing}",
        )


if __name__ == "__main__":
    unittest.main()
