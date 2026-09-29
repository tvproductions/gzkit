"""`gz tidy` derives its exit code and success line from its findings (GHI #1124).

The verb exited 0 with 456 findings and printed "Project is tidy" over an
actionable settings-vault notice. Operator rulings 2026-09-28: "Make findings
gate (Recommended)", and "Breaches gate; attestation informational
(Recommended)" -- validation issues, orphaned OBPIs and an actionable vault exit
3 (cli.md: policy breach); ADRs pending attestation are a workflow queue, printed
but never gating. `--check` is report-only and refuses `--fix`.
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from rich.console import Console

from gzkit.commands import tidy
from gzkit.settings_vault import VaultState, VaultStatus

_CONFIG = SimpleNamespace(paths=SimpleNamespace(ledger=".gzkit/ledger.jsonl"))
_SUCCESS = "Project is tidy"


def _vault(state: VaultState) -> VaultStatus:
    return VaultStatus(state=state, directory=Path("vault"), snapshot_count=1, message="vault note")


def _run(
    *,
    errors: list | None = None,
    graph: dict | None = None,
    pending: list | None = None,
    vault: VaultState = VaultState.CURRENT,
) -> tuple[int, str]:
    """Run `tidy` over stubbed sections; return (exit code, rendered output)."""
    buffer = io.StringIO()
    ledger = SimpleNamespace(
        get_artifact_graph=lambda: graph or {},
        get_pending_attestations=lambda: pending or [],
    )
    with (
        patch.object(tidy, "console", Console(file=buffer, width=200, color_system=None)),
        patch.object(tidy, "ensure_initialized", return_value=_CONFIG),
        patch.object(tidy, "get_project_root", return_value=Path(".")),
        patch.object(tidy, "validate_all", return_value=SimpleNamespace(errors=errors or [])),
        patch.object(tidy, "Ledger", return_value=ledger),
        patch.object(tidy, "vault_status", return_value=_vault(vault)),
    ):
        try:
            tidy.tidy(check_only=True, fix=False, dry_run=False)
        except SystemExit as exc:
            return int(exc.code or 0), buffer.getvalue()
    return 0, buffer.getvalue()


class TestTidyBreachesGate(unittest.TestCase):
    """Each breach section alone exits 3 and suppresses the success line."""

    def test_validation_issue_exits_3(self) -> None:
        code, out = _run(errors=[SimpleNamespace(type="header", message="broken")])
        self.assertEqual(code, 3)
        self.assertNotIn(_SUCCESS, out)

    def test_orphaned_obpi_exits_3(self) -> None:
        code, out = _run(graph={"OBPI-9.9.9-01": {"type": "obpi", "parent": "ADR-missing"}})
        self.assertEqual(code, 3)
        self.assertNotIn(_SUCCESS, out)

    def test_actionable_vault_exits_3_and_suppresses_success(self) -> None:
        for state in (VaultState.DRIFTED, VaultState.ABSENT, VaultState.RECOVERABLE):
            with self.subTest(state=state):
                code, out = _run(vault=state)
                self.assertEqual(code, 3)
                self.assertNotIn(_SUCCESS, out)


class TestTidyNonBreaches(unittest.TestCase):
    """A clean tree and an attestation queue both exit 0 with the success line."""

    def test_clean_tree_exits_0_with_success_line(self) -> None:
        code, out = _run()
        self.assertEqual(code, 0)
        self.assertIn(_SUCCESS, out)

    def test_pending_attestation_is_listed_but_does_not_gate(self) -> None:
        code, out = _run(pending=["ADR-pool.example"])
        self.assertEqual(code, 0)
        self.assertIn("ADR-pool.example", out)
        self.assertIn(_SUCCESS, out)

    def test_non_actionable_vault_does_not_gate(self) -> None:
        code, _ = _run(vault=VaultState.NOT_APPLICABLE)
        self.assertEqual(code, 0)


class TestFixVerdictIsPostRepair(unittest.TestCase):
    """`--fix` is judged on the tree it leaves: a repaired finding no longer gates."""

    def _fix(self, after: list) -> int:
        calls = iter([[SimpleNamespace(type="surface", message="out of sync")], after])
        ledger = SimpleNamespace(get_artifact_graph=dict, get_pending_attestations=list)
        with (
            patch.object(tidy, "console", Console(file=io.StringIO(), color_system=None)),
            patch.object(tidy, "ensure_initialized", return_value=_CONFIG),
            patch.object(tidy, "get_project_root", return_value=Path(".")),
            patch.object(
                tidy, "validate_all", side_effect=lambda _r: SimpleNamespace(errors=next(calls))
            ),
            patch.object(tidy, "Ledger", return_value=ledger),
            patch.object(tidy, "vault_status", return_value=_vault(VaultState.CURRENT)),
            patch.object(tidy, "refuse_on_sync_blockers"),
            patch.object(tidy, "sync_all"),
            patch.object(tidy, "_post_sync_check"),
        ):
            try:
                tidy.tidy(check_only=False, fix=True, dry_run=False)
            except SystemExit as exc:
                return int(exc.code or 0)
        return 0

    def test_repaired_finding_exits_0(self) -> None:
        self.assertEqual(self._fix(after=[]), 0)

    def test_finding_the_fix_cannot_repair_still_exits_3(self) -> None:
        self.assertEqual(self._fix(after=[SimpleNamespace(type="header", message="x")]), 3)


class TestCheckIsReportOnly(unittest.TestCase):
    """`--check` changes behaviour: it refuses to combine with `--fix`."""

    def test_check_with_fix_is_a_usage_error(self) -> None:
        from gzkit.cli.main import _build_parser

        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as ctx:
            _build_parser().parse_args(["tidy", "--check", "--fix"])
        self.assertEqual(ctx.exception.code, 2)

    def test_check_alone_parses_as_report_only(self) -> None:
        from gzkit.cli.main import _build_parser

        args = _build_parser().parse_args(["tidy", "--check"])
        self.assertTrue(args.check_only)
        self.assertFalse(args.fix)


if __name__ == "__main__":
    unittest.main()
