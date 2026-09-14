"""`gz validate --json` reports the same exit status as plain mode (GHI #995).

Exit codes are what CI, pre-commit hooks and `gz check` consume. `--json`
changes how findings are RENDERED, never how they are CLASSIFIED: a failing
scope in `--json` mode that exits 0 reports failure in its body while signalling
success in its status — the one combination a caller checking `$?` cannot catch.

The family has three dispatch shapes, and each is driven here on its own:

* the aggregate path — every `VALIDATOR_REGISTRY` scope shares one renderer, so
  one injected finding set exercises all of them;
* the `--audits` umbrella, which runs the aggregate path in a pass of its own;
* the solo early-return scopes, each owning its own JSON branch — enumerated
  from `_dispatch_early_return_scopes`'s live signature, so a new solo scope
  fails this module until it is given a row.
"""

from __future__ import annotations

import inspect
import json
import unittest
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest import mock

from gzkit.cli import main
from gzkit.commands import validate_cmd
from gzkit.config import GzkitConfig
from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.attestation_receipts import (
    AttestationReceiptValidationResult,
)
from gzkit.ledger import Ledger, adr_created_event
from gzkit.validators.unscoped_rules import UnscopedRulesResult
from tests.commands.common import CliRunner, _quick_init

_POLICY = ValidationError(type="frontmatter", artifact="ADR-0.1.0", message="lane drift")
_OTHER = ValidationError(type="manifest", artifact=".gzkit/manifest.json", message="bad")


def _run(args: list[str]) -> tuple[int, str]:
    result = CliRunner().invoke(main, args)
    return result.exit_code, result.output


class TestAggregateJsonExitClassification(unittest.TestCase):
    """The shared aggregate renderer classifies exit status in both modes."""

    # (label, injected findings, exit status the 4-code map requires)
    CASES: tuple[tuple[str, list[ValidationError], int], ...] = (
        ("policy breach only", [_POLICY], 3),
        ("non-policy error only", [_OTHER], 1),
        ("mixed: non-policy wins", [_POLICY, _OTHER], 1),
        ("clean: the valid positive control", [], 0),
    )

    def test_json_exit_matches_plain_exit_for_every_finding_class(self) -> None:
        for label, errors, expected in self.CASES:
            with self.subTest(label), CliRunner().isolated_filesystem():
                _quick_init()
                with mock.patch.object(validate_cmd, "_collect_errors", return_value=errors):
                    plain_exit, _ = _run(["validate", "--ledger"])
                    json_exit, json_out = _run(["validate", "--ledger", "--json"])
                self.assertEqual(plain_exit, expected)
                self.assertEqual(json_exit, expected, "--json must not bypass exit classification")
                payload = json.loads(json_out)
                self.assertIs(payload["valid"], expected == 0)
                self.assertEqual(len(payload["errors"]), len(errors))

    def test_real_frontmatter_drift_exits_policy_breach_in_both_modes(self) -> None:
        # No injection: a genuinely drifted tree, the shape GHI #995 reproduced.
        with CliRunner().isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            Ledger(root / ".gzkit" / "ledger.jsonl").append(
                adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite")
            )
            design_root = GzkitConfig.load(root / ".gzkit.json").paths.design_root
            adr_dir = root / design_root / "adr" / "pre-release" / "ADR-0.1.0-test"
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.1.0-test.md").write_text(
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
                encoding="utf-8",
            )
            plain_exit, _ = _run(["validate", "--frontmatter"])
            json_exit, json_out = _run(["validate", "--frontmatter", "--json"])
        self.assertEqual(plain_exit, 3)
        self.assertEqual(json_exit, 3)
        self.assertFalse(json.loads(json_out)["valid"])


class TestAuditsUmbrellaJsonExit(unittest.TestCase):
    """`--audits` surfaces an aggregate-pass breach as its own exit in `--json`."""

    def test_umbrella_json_exit_matches_plain_on_aggregate_breach(self) -> None:
        with CliRunner().isolated_filesystem():
            _quick_init()
            with (
                mock.patch.object(validate_cmd, "_run_unscoped_rules_scope"),
                mock.patch.object(validate_cmd, "_run_sensitivity_scope"),
                mock.patch.object(validate_cmd, "_collect_errors", return_value=[_POLICY]),
            ):
                plain_exit, _ = _run(["validate", "--audits"])
                json_exit, _ = _run(["validate", "--audits", "--json"])
        self.assertEqual(plain_exit, 3)
        self.assertEqual(json_exit, 3)


def _unscoped_fail() -> UnscopedRulesResult:
    return UnscopedRulesResult(
        result="fail",
        violations=[],
        allowlist_entries=[],
        canonical_root=".gzkit/rules",
        files_checked=0,
        exit_code=3,
    )


_TA = "gzkit.governance.trust_audits"

#: Solo scope param → (CLI args, patch target, factory for a failing result).
_SOLO_SCOPES: dict[str, tuple[list[str], str, Callable[[], Any]]] = {
    "check_evaluation_justify_binding": (
        ["--evaluation-justify-binding"],
        "gzkit.commands.validate_cmd._evaluation_justify_binding_runner",
        lambda: [_POLICY],
    ),
    "check_unscoped_rules": (
        ["--unscoped-rules"],
        "gzkit.validators.unscoped_rules.run_unscoped_rules",
        _unscoped_fail,
    ),
    "check_sensitivity": (
        ["--sensitivity"],
        "gzkit.commands.validate_cmd._sensitivity_records",
        lambda: (
            [],
            [ValidationError(type="sensitivity-escape-attempt", artifact="b", message="m")],
        ),
    ),
    "check_qc_binding": (["--qc-binding"], f"{_TA}.qc_binding.audit_qc_binding", lambda: [_POLICY]),
    "check_fidelity_presence": (
        ["--fidelity-presence"],
        f"{_TA}.fidelity_presence.audit_fidelity_presence",
        lambda: [_POLICY],
    ),
    "check_waiver_ratchet": (
        ["--waiver-ratchet"],
        f"{_TA}.waiver_ratchet.audit_waiver_ratchet",
        lambda: [_POLICY],
    ),
    "check_config_registry": (
        ["--config-registry"],
        f"{_TA}.config_registry.audit_config_registry",
        lambda: [_POLICY],
    ),
    "check_gate_callers": (
        ["--gate-callers"],
        f"{_TA}.gate_callers.audit_gate_callers",
        lambda: [_POLICY],
    ),
    "check_exemption_controls": (
        ["--exemption-controls"],
        f"{_TA}.exemption_controls.audit_exemption_controls",
        lambda: [_POLICY],
    ),
    "check_population_controls": (
        ["--population-controls"],
        f"{_TA}.population_controls.audit_population_controls",
        lambda: [_POLICY],
    ),
    # Not a ``check_*`` param, so the roster assertion below cannot see it.
    "attestation_receipts": (
        ["--attestation-receipts", "no receipts cited"],
        "gzkit.commands.validate_cmd.validate_attestation_receipts",
        lambda: AttestationReceiptValidationResult(entries=(), exit_code=3, warn_only=False),
    ),
}

#: Early-return params that are not a solo check with its own JSON branch.
_NOT_SOLO_CHECKS = frozenset(
    {
        "check_audits",  # umbrella — TestAuditsUmbrellaJsonExit
        "check_distribution",  # aggregate runner; present only to gate --regenerate
        "check_distribution_regenerate",  # mutates the baseline; renders no finding
    }
)


class TestSoloScopeJsonExitClassification(unittest.TestCase):
    """Every solo early-return scope classifies exit status in both modes."""

    def test_roster_covers_every_live_solo_scope(self) -> None:
        params = inspect.signature(validate_cmd._dispatch_early_return_scopes).parameters
        live = {n for n in params if n.startswith("check_")} - _NOT_SOLO_CHECKS
        rostered = {n for n in _SOLO_SCOPES if n.startswith("check_")}
        self.assertEqual(
            sorted(live - rostered),
            [],
            "a solo scope owns its own --json branch; give it a row in _SOLO_SCOPES",
        )
        self.assertEqual(sorted(rostered - live), [], "roster names a scope that no longer exists")

    def test_failing_solo_scope_exits_the_same_in_json_as_plain(self) -> None:
        for param, (flags, target, failing) in _SOLO_SCOPES.items():
            with self.subTest(param), CliRunner().isolated_filesystem():
                _quick_init()
                with mock.patch(target, return_value=failing()):
                    plain_exit, _ = _run(["validate", *flags])
                    json_exit, _ = _run(["validate", *flags, "--json"])
                self.assertNotEqual(plain_exit, 0, "the injected failure must fail plain mode")
                self.assertEqual(json_exit, plain_exit)


if __name__ == "__main__":
    unittest.main()
