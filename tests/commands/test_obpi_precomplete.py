"""Tests for `gz obpi precomplete` (GHI #196).

Each precondition check has a positive test (passes when the precondition
holds) and a negative test (fails with a named remediation when it doesn't).
"""

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.commands.obpi_precomplete import (
    _check_arb_receipts_present,
    _check_brief_readiness,
    _check_lock_held,
    _check_plan_audit_receipt,
    _check_reconcile_idempotent,
    _resolve_brief_path,
)
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event, obpi_created_event
from tests.commands.common import CliRunner, _quick_init


def _scaffold_authored_brief(project_root: Path, adr_id: str, obpi_id: str) -> Path:
    """Create a minimally-authored brief that passes ObpiValidator authored mode.

    Uses ``status: pending`` (the canonical ledger form for a freshly-created
    OBPI) so that ``_check_reconcile_idempotent`` does not flag drift.
    """
    config = GzkitConfig.load(project_root / ".gzkit.json")
    adr_dir = project_root / config.paths.design_root / "adr" / "pre-release" / f"{adr_id}-test"
    obpi_dir = adr_dir / "obpis"
    obpi_dir.mkdir(parents=True, exist_ok=True)
    path = obpi_dir / f"{obpi_id}-test.md"
    path.write_text(
        f"---\nid: {obpi_id}\nparent: {adr_id}\nstatus: pending\nlane: Lite\n---\n\n"
        f"# {obpi_id}\n\n"
        "## Objective\nA fully authored brief for precomplete tests.\n\n"
        "## Lane\n**Lite** - Internal contract.\n\n"
        "## Allowed Paths\n- `src/gzkit/ports/` - Port definitions\n\n"
        "## Denied Paths\n- `docs/user/commands/` - No operator-surface changes\n\n"
        "## Requirements (FAIL-CLOSED)\n"
        "1. REQUIREMENT: Real requirement.\n\n"
        "## Discovery Checklist\n"
        "**Prerequisites (check existence, STOP if missing):**\n"
        "- [ ] `src/gzkit/runtime.py`\n\n"
        "**Existing Code (understand current state):**\n"
        "- [ ] `src/gzkit/ports.py`\n\n"
        "## Verification\n```bash\nuv run gz lint\n"
        "uv run -m unittest tests.commands.test_obpi_precomplete\n```\n\n"
        "## Acceptance Criteria\n- [ ] REQ-0.1.0-01-01: Real criterion.\n",
        encoding="utf-8",
    )
    return path


class TestPrecompleteResolveBriefPath(unittest.TestCase):
    """Brief lookup must find the canonical OBPI under obpis/ or briefs/."""

    def test_resolves_brief_under_obpis_layout(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            resolved = _resolve_brief_path(root, "OBPI-0.1.0-01")
            self.assertIsNotNone(resolved)
            self.assertEqual(resolved, path)

    def test_returns_none_when_brief_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            self.assertIsNone(_resolve_brief_path(root, "OBPI-9.9.9-99"))


class TestPrecompleteBriefReadinessCheck(unittest.TestCase):
    """Brief MUST pass `gz obpi validate --authored` for completion."""

    def test_passes_for_authored_brief(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
            result = _check_brief_readiness(root, path)
            self.assertTrue(result.ok, msg=result.message)

    def test_fails_for_thin_brief(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            config = GzkitConfig.load(root / ".gzkit.json")
            adr_dir = root / config.paths.design_root / "adr" / "pre-release" / "ADR-0.1.0-test"
            (adr_dir / "obpis").mkdir(parents=True)
            path = adr_dir / "obpis" / "OBPI-0.1.0-01-test.md"
            # Thin brief: missing Objective, Discovery Checklist, etc.
            path.write_text(
                "---\nid: OBPI-0.1.0-01\nparent: ADR-0.1.0\nstatus: Draft\nlane: Lite\n---\n\n"
                "# OBPI-0.1.0-01\n\n"
                "## Allowed Paths\n- `src/x/` - x\n\n"
                "## Acceptance Criteria\n- [ ] REQ-0.1.0-01-01: x\n",
                encoding="utf-8",
            )
            result = _check_brief_readiness(root, path)
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("validator", result.message.lower())


class TestPrecompleteReconcileCheck(unittest.TestCase):
    """`gz frontmatter reconcile --dry-run` MUST produce empty rewrite list."""

    def test_passes_when_no_drift(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            # Fresh project — no ADRs registered, no drift possible
            result = _check_reconcile_idempotent(root)
            self.assertTrue(result.ok, msg=result.message)

    def test_fails_when_brief_status_drifts(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            # Seed an ADR file with drifted status (frontmatter says Completed,
            # ledger derivation says Pending)
            config = GzkitConfig.load(root / ".gzkit.json")
            adr_dir = root / config.paths.design_root / "adr" / "pre-release" / "ADR-0.1.0-test"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-0.1.0-test.md").write_text(
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n"
                "status: Completed\n---\n# ADR\n",
                encoding="utf-8",
            )
            result = _check_reconcile_idempotent(root)
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("rewritten", result.message.lower())


class TestPrecompleteLockCheck(unittest.TestCase):
    """OBPI lock MUST exist before `gz obpi complete` runs."""

    def test_fails_when_lock_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            result = _check_lock_held(root, "OBPI-0.1.0-01")
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("lock", result.message.lower())
            self.assertIsNotNone(result.remediation)
            self.assertIn("lock claim", (result.remediation or "").lower())

    def test_passes_when_lock_file_exists(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            locks_dir = root / ".gzkit" / "locks"
            locks_dir.mkdir(parents=True, exist_ok=True)
            (locks_dir / "OBPI-0.1.0-01.json").write_text(
                json.dumps({"agent": "test-agent", "claimed_at": "2026-04-18T00:00:00Z"}),
                encoding="utf-8",
            )
            result = _check_lock_held(root, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)


class TestPrecompleteArbReceiptsCheck(unittest.TestCase):
    """ARB receipts SHOULD be present for Heavy-lane attestation."""

    def test_fails_when_no_receipts_dir(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            result = _check_arb_receipts_present(root)
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("artifacts/receipts", result.message.lower())

    def test_passes_when_arb_receipt_present(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            receipts_dir = root / "artifacts" / "receipts"
            receipts_dir.mkdir(parents=True, exist_ok=True)
            (receipts_dir / "arb-ruff-test.json").write_text("{}", encoding="utf-8")
            result = _check_arb_receipts_present(root)
            self.assertTrue(result.ok, msg=result.message)


class TestPrecompletePlanAuditReceiptCheck(unittest.TestCase):
    """Plan-audit receipt MUST exist with verdict PASS for the target OBPI."""

    def test_fails_when_no_plans_dir(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            result = _check_plan_audit_receipt(root, "OBPI-0.1.0-01")
            self.assertFalse(result.ok, msg=result.message)

    def test_fails_when_receipt_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            (root / ".claude" / "plans").mkdir(parents=True)
            result = _check_plan_audit_receipt(root, "OBPI-0.1.0-01")
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("plan-audit", result.message.lower())

    def test_fails_when_receipt_verdict_is_fail(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            (plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.1.0-01", "verdict": "FAIL"}),
                encoding="utf-8",
            )
            result = _check_plan_audit_receipt(root, "OBPI-0.1.0-01")
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("fail", result.message.lower())

    def test_passes_when_receipt_verdict_is_pass(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            (plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.1.0-01", "verdict": "PASS"}),
                encoding="utf-8",
            )
            result = _check_plan_audit_receipt(root, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)


class TestPrecompleteCliEndToEnd(unittest.TestCase):
    """End-to-end: `gz obpi precomplete` exits 3 on broken fixture, 0 on ready fixture."""

    def test_exits_3_when_brief_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["obpi", "precomplete", "OBPI-9.9.9-99"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("not found", result.output.lower())

    def test_exits_3_when_preconditions_fail(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
            _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            # No lock, no plan-audit receipt → at least 2 checks fail
            result = runner.invoke(main, ["obpi", "precomplete", "OBPI-0.1.0-01"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("BLOCKED", result.output)

    def test_exits_0_when_all_preconditions_met(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
            _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            # Seed lock
            (root / ".gzkit" / "locks").mkdir(parents=True, exist_ok=True)
            (root / ".gzkit" / "locks" / "OBPI-0.1.0-01.json").write_text(
                json.dumps({"agent": "test-agent"}), encoding="utf-8"
            )
            # Seed ARB receipt
            (root / "artifacts" / "receipts").mkdir(parents=True, exist_ok=True)
            (root / "artifacts" / "receipts" / "arb-ruff-test.json").write_text(
                "{}", encoding="utf-8"
            )
            # Seed plan-audit receipt
            (root / ".claude" / "plans").mkdir(parents=True, exist_ok=True)
            (root / ".claude" / "plans" / ".plan-audit-receipt-OBPI-0.1.0-01.json").write_text(
                json.dumps({"obpi_id": "OBPI-0.1.0-01", "verdict": "PASS"}),
                encoding="utf-8",
            )
            result = runner.invoke(main, ["obpi", "precomplete", "OBPI-0.1.0-01"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("READY", result.output)

    def test_json_output_shape(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))
            _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            result = runner.invoke(main, ["obpi", "precomplete", "OBPI-0.1.0-01", "--json"])
            payload = json.loads(result.output)
            self.assertEqual(payload["obpi_id"], "OBPI-0.1.0-01")
            self.assertIn("ready", payload)
            self.assertEqual(len(payload["checks"]), 5)
            self.assertEqual(
                {c["name"] for c in payload["checks"]},
                {
                    "brief_readiness",
                    "reconcile_idempotent",
                    "lock_held",
                    "arb_receipts",
                    "plan_audit_receipt",
                },
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
