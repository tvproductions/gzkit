"""Tests for `gz obpi precomplete` (GHI #196).

Each precondition check has a positive test (passes when the precondition
holds) and a negative test (fails with a named remediation when it doesn't).
"""

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.commands.obpi_precomplete import (
    _check_adversarial_validation,
    _check_arb_receipts_present,
    _check_behave_req_coverage_scoped,
    _check_brief_headings_scoped,
    _check_brief_readiness,
    _check_lock_held,
    _check_operator_block,
    _check_plan_audit_receipt,
    _check_reconcile_idempotent,
    _check_task_envelope_coherence,
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
        "## Denied Paths\n- `docs/user/manpages/` - No operator-surface changes\n\n"
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


class TestPrecompleteIdPrefixIsNotIdentity(unittest.TestCase):
    """`OBPI-<semver>-<index>` is not an identity (GHI #826).

    Demoting a feature ADR to pool releases its semver for reuse, and the parked
    OBPI ids keep it. So one prefix can name two different OBPIs under two
    different parent ADRs, and prefix-matching a fully-qualified id hands back
    the wrong artifact. Measured live: `ADR-0.35.0-pre-commit-hook-absorption`
    was parked 2026-07-22 and `ADR-0.35.0-canon-entry-corpus-landing` reused
    `0.35.0`, so `OBPI-0.35.0-01` names both `-arb-ruff` and
    `-corpus-tombstone-schema-and-fold`.
    """

    def test_fully_qualified_id_never_resolves_to_a_prefix_sibling(self) -> None:
        """A full id matching no brief is NOT FOUND, never a sibling's brief.

        Resolving `-other-slug` to `-01`'s brief is not a near-miss: the two ids
        can belong to different parent ADRs, so the caller silently operates on
        an OBPI it did not name.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            sibling = _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            self.assertTrue(sibling.is_file())
            resolved = _resolve_brief_path(root, "OBPI-0.1.0-01-a-different-obpi")
            self.assertIsNone(
                resolved,
                f"fully-qualified id resolved to a prefix sibling: {resolved}",
            )

    def test_short_form_still_resolves(self) -> None:
        """The short form remains a supported lookup — this fix narrows only full ids."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            self.assertEqual(_resolve_brief_path(root, "OBPI-0.1.0-01"), path)

    def test_lock_check_is_not_satisfied_by_a_prefix_siblings_lock(self) -> None:
        """A lock claimed for one OBPI must not clear the gate for another.

        The lock is the multi-agent coordination primitive; honoring a sibling's
        lock hands two agents the same green light.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            locks = root / ".gzkit" / "locks" / "obpi"
            locks.mkdir(parents=True, exist_ok=True)
            (locks / "OBPI-0.1.0-01-the-held-one.json").write_text("{}", encoding="utf-8")
            result = _check_lock_held(root, "OBPI-0.1.0-01-a-different-obpi")
            self.assertFalse(
                result.ok,
                "a prefix sibling's lock satisfied the gate for an unlocked OBPI",
            )

    def test_plan_audit_receipt_is_not_satisfied_by_a_prefix_siblings_receipt(self) -> None:
        """A plan-audit receipt for one OBPI must not clear the gate for another."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            plans = root / ".claude" / "plans"
            plans.mkdir(parents=True, exist_ok=True)
            (plans / ".plan-audit-receipt-OBPI-0.1.0-01-the-audited-one.json").write_text(
                json.dumps({"verdict": "PASS"}), encoding="utf-8"
            )
            result = _check_plan_audit_receipt(root, "OBPI-0.1.0-01-a-different-obpi")
            self.assertFalse(
                result.ok,
                "a prefix sibling's plan-audit receipt satisfied the gate",
            )


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

    def test_refused_rewrites_are_surfaced_not_silently_clean(self) -> None:
        """A refused-only receipt passes (no deadlock) but MUST name the refusals.

        Coupled-surface coherence for the OBPI-0.31.0-03 receipt contract: a
        monitor-refused rewrite is not pending drift (fail would deadlock the
        refused OBPI's own completion), but reporting it as a bare "no pending
        frontmatter rewrites" hides live ledger/frontmatter disagreement.
        """
        from gzkit.ledger import obpi_created_event  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            # Refused shape: ledger pending, frontmatter hand-marked Completed
            # (ATTESTED -> DRAFTED is not in CANONICAL_TRANSITIONS).
            ledger.append(obpi_created_event("OBPI-0.1.0-01-test", "ADR-0.1.0"))
            config = GzkitConfig.load(root / ".gzkit.json")
            obpi_dir = (
                root / config.paths.design_root / "adr" / "pre-release" / "ADR-0.1.0-test" / "obpis"
            )
            obpi_dir.mkdir(parents=True)
            (obpi_dir / "OBPI-0.1.0-01-test.md").write_text(
                "---\nid: OBPI-0.1.0-01-test\nparent: ADR-0.1.0\n"
                "item: 1\nlane: lite\nstatus: Completed\n---\n# OBPI\n",
                encoding="utf-8",
            )
            result = _check_reconcile_idempotent(root)
            self.assertTrue(result.ok, msg=result.message)
            self.assertIn(
                "refused",
                result.message.lower(),
                "refused rewrites must be named in the check message, not hidden",
            )


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
            locks_dir = root / ".gzkit" / "locks" / "obpi"
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
            (root / ".gzkit" / "locks" / "obpi").mkdir(parents=True, exist_ok=True)
            (root / ".gzkit" / "locks" / "obpi" / "OBPI-0.1.0-01.json").write_text(
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
            self.assertEqual(len(payload["checks"]), 11)
            self.assertEqual(
                {c["name"] for c in payload["checks"]},
                {
                    "brief_readiness",
                    "reconcile_idempotent",
                    "lock_held",
                    "arb_receipts",
                    "plan_audit_receipt",
                    "brief_headings",
                    "behave_req_coverage",
                    "task_envelope_coherence",
                    "adversarial_validation",  # GHI #676
                    "stage2_dispatch",  # GHI #845
                    "operator_block",  # GHI #887
                },
            )


class TestPrecompleteBriefHeadingsScopedCheck(unittest.TestCase):
    """GHI #422 fix #2: brief evidence headings checked at Stage 3."""

    def test_passes_when_no_evidence_headings(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            result = _check_brief_headings_scoped(root, path)
            self.assertTrue(result.ok, msg=result.message)

    def test_fails_when_evidence_section_uses_h2(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            text = path.read_text(encoding="utf-8")
            path.write_text(
                text + "\n## Implementation Summary\nDrifted heading.\n",
                encoding="utf-8",
            )
            result = _check_brief_headings_scoped(root, path)
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("h2", result.message.lower())


class TestPrecompleteBehaveReqCoverageScopedCheck(unittest.TestCase):
    """GHI #422 fix #2: heavy-lane REQ scenario tags checked at Stage 3."""

    def _scaffold_heavy_brief(self, root: Path, obpi_id: str, req_id: str) -> Path:
        """Heavy-lane authored brief with one REQ in Acceptance Criteria."""
        config = GzkitConfig.load(root / ".gzkit.json")
        adr_dir = root / config.paths.design_root / "adr" / "pre-release" / "ADR-0.1.0-test"
        obpi_dir = adr_dir / "obpis"
        obpi_dir.mkdir(parents=True, exist_ok=True)
        path = obpi_dir / f"{obpi_id}-test.md"
        path.write_text(
            f"---\nid: {obpi_id}\nparent: ADR-0.1.0\nstatus: pending\nlane: Heavy\n---\n\n"
            f"# {obpi_id}\n\n"
            f"## Acceptance Criteria\n- [ ] {req_id}: Real criterion.\n",
            encoding="utf-8",
        )
        return path

    def test_passes_for_lite_lane_brief(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = _scaffold_authored_brief(root, "ADR-0.1.0", "OBPI-0.1.0-01")
            result = _check_behave_req_coverage_scoped(root, path, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)
            self.assertIn("lite", result.message.lower())

    def test_fails_for_heavy_brief_with_untagged_req(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = self._scaffold_heavy_brief(root, "OBPI-0.1.0-01", "REQ-0.1.0-01-01")
            (root / "features").mkdir(exist_ok=True)
            result = _check_behave_req_coverage_scoped(root, path, "OBPI-0.1.0-01")
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("REQ-0.1.0-01-01", result.message)
            remediation = (result.remediation or "").lower()
            self.assertIn("scenario", remediation)
            self.assertIn("@covers", remediation)

    def test_passes_for_heavy_brief_with_tagged_req(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = self._scaffold_heavy_brief(root, "OBPI-0.1.0-01", "REQ-0.1.0-01-01")
            features_dir = root / "features"
            features_dir.mkdir(exist_ok=True)
            (features_dir / "test.feature").write_text(
                "Feature: x\n\n  @REQ-0.1.0-01-01\n  Scenario: y\n    Given z\n",
                encoding="utf-8",
            )
            result = _check_behave_req_coverage_scoped(root, path, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)

    def test_passes_when_obpi_is_waived(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = self._scaffold_heavy_brief(root, "OBPI-0.1.0-01", "REQ-0.1.0-01-01")
            (root / "data").mkdir(exist_ok=True)
            (root / "data" / "behave_coverage_waivers.json").write_text(
                json.dumps(
                    {
                        "default_rationale": {"test-waiver": "test rationale"},
                        "waivers": {"OBPI-0.1.0-01": "test-waiver"},
                    }
                ),
                encoding="utf-8",
            )
            result = _check_behave_req_coverage_scoped(root, path, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)
            self.assertIn("waived", result.message.lower())

    def _scaffold_heavy_brief_kind(self, root: Path, obpi_id: str, req_id: str, kind: str) -> Path:
        """Heavy-lane brief with one REQ carrying an explicit ``[kind]`` tag."""
        config = GzkitConfig.load(root / ".gzkit.json")
        adr_dir = root / config.paths.design_root / "adr" / "pre-release" / "ADR-0.1.0-test"
        obpi_dir = adr_dir / "obpis"
        obpi_dir.mkdir(parents=True, exist_ok=True)
        path = obpi_dir / f"{obpi_id}-test.md"
        path.write_text(
            f"---\nid: {obpi_id}\nparent: ADR-0.1.0\nstatus: pending\nlane: Heavy\n---\n\n"
            f"# {obpi_id}\n\n"
            f"## Acceptance Criteria\n- [ ] {req_id} [{kind}]: Real criterion.\n",
            encoding="utf-8",
        )
        return path

    def test_passes_for_structural_fence_req_without_scenario(self) -> None:
        """STRUCTURAL-FENCE REQs are exempt by kind (ADR-0.0.59 / GHI #636)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = self._scaffold_heavy_brief_kind(
                root, "OBPI-0.1.0-01", "REQ-0.1.0-01-01", "structural-fence"
            )
            (root / "features").mkdir(exist_ok=True)
            result = _check_behave_req_coverage_scoped(root, path, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)

    def test_passes_for_support_req_without_scenario(self) -> None:
        """SUPPORT REQs are exempt by kind (proven by ledger + structural validator)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = self._scaffold_heavy_brief_kind(
                root, "OBPI-0.1.0-01", "REQ-0.1.0-01-01", "support"
            )
            (root / "features").mkdir(exist_ok=True)
            result = _check_behave_req_coverage_scoped(root, path, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)

    def test_passes_for_behavior_req_covered_by_unit_test(self) -> None:
        """A BEHAVIOR REQ is satisfied by an @covers unit test, not only a scenario tag."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            path = self._scaffold_heavy_brief_kind(
                root, "OBPI-0.1.0-01", "REQ-0.1.0-01-01", "behavior"
            )
            (root / "features").mkdir(exist_ok=True)
            tests_dir = root / "tests"
            tests_dir.mkdir(exist_ok=True)
            (tests_dir / "test_cover_fixture.py").write_text(
                "from gzkit.traceability import covers\n\n\n"
                "class T:\n"
                '    @covers("REQ-0.1.0-01-01")\n'
                "    def test_x(self):\n"
                "        pass\n",
                encoding="utf-8",
            )
            result = _check_behave_req_coverage_scoped(root, path, "OBPI-0.1.0-01")
            self.assertTrue(result.ok, msg=result.message)


class TestPrecompleteTaskEnvelopeCoherence(unittest.TestCase):
    """Precomplete early-warns on Sig(b) residue before `gz obpi complete` (GHI #590)."""

    @staticmethod
    def _seed(root: Path, req_atomic: list[str] | None) -> Path:
        gzkit_dir = root / ".gzkit"
        gzkit_dir.mkdir(parents=True, exist_ok=True)
        (gzkit_dir / "ledger.jsonl").write_text(
            json.dumps(
                {
                    "event": "task_started",
                    "task_id": "TASK-0.0.64-04-01-01",
                    "obpi_id": "OBPI-0.0.64-04",
                    "id": "evt-1",
                    "schema_": "1.0",
                    "timestamp": "2026-05-30T15:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        brief_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.64-fixture" / "obpis"
        brief_dir.mkdir(parents=True, exist_ok=True)
        path = brief_dir / "OBPI-0.0.64-04-fixture.md"
        atomic_line = f"req_atomic:\n  - {req_atomic[0]}\n" if req_atomic else ""
        path.write_text(
            f"---\nid: OBPI-0.0.64-04\nparent: ADR-0.0.64-fixture\nstatus: pending\n"
            f"lane: Heavy\n{atomic_line}---\n\n# Fixture\n",
            encoding="utf-8",
        )
        return path

    def test_fails_on_seq01_only_without_req_atomic(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = self._seed(root, req_atomic=None)
            result = _check_task_envelope_coherence(root, path)
            self.assertEqual(result.name, "task_envelope_coherence")
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("Signature (b)", result.message)
            self.assertIsNotNone(result.remediation)

    def test_passes_when_req_atomic_present(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            path = self._seed(root, req_atomic=["REQ-0.0.64-04-01"])
            result = _check_task_envelope_coherence(root, path)
            self.assertTrue(result.ok, msg=result.message)


class TestPrecompleteAdversarialValidationCheck(unittest.TestCase):
    """The Step-4b precondition reads the VERDICT, not the heading (GHI #879).

    A heading match cannot tell a brief recording ``REFUTED`` from one recording
    ``NOT-REFUTED``, so the pre-flight reported READY on refuted work and an agent
    read that as authorization to solicit attestation. Each test below drives one
    verdict the section can record; together they enumerate what the check must
    distinguish.
    """

    @staticmethod
    def _seed(step_4b_body: str, *, lane: str = "Heavy", trailing: str = "") -> Path:
        """Write a brief whose Step-4b section carries ``step_4b_body``."""
        import tempfile

        td = tempfile.mkdtemp()
        path = Path(td) / "OBPI-0.1.0-01-fixture.md"
        path.write_text(
            f"---\nid: OBPI-0.1.0-01\nparent: ADR-0.1.0\nstatus: pending\n"
            f"lane: {lane}\n---\n\n# Fixture\n\n"
            "### Step 4b - Independent Adversarial Validation\n\n"
            f"{step_4b_body}\n" + trailing,
            encoding="utf-8",
        )
        return path

    def test_fails_when_the_recorded_verdict_is_a_refutation(self) -> None:
        """The reported instance: READY on a brief recording REFUTED, twice."""
        path = self._seed(
            "| Round | Verdict |\n|---|---|\n"
            "| 1 | `REFUTED` |\n| 2 (post-fix) | `REFUTED` - 5 further findings |\n"
        )
        result = _check_adversarial_validation(path)
        self.assertEqual(result.name, "adversarial_validation")
        self.assertFalse(result.ok, msg=result.message)
        self.assertIn("refuted", result.message.lower())
        self.assertIsNotNone(result.remediation)

    def test_fails_when_the_recorded_verdict_carries_caveats(self) -> None:
        """A known caveat must never be handed to the operator dressed as clean."""
        result = _check_adversarial_validation(
            self._seed("**Verdict: REFUTED-WITH-CAVEATS** - two findings deferred.")
        )
        self.assertFalse(result.ok, msg=result.message)
        self.assertIn("refuted-with-caveats", result.message.lower())

    def test_passes_when_the_recorded_verdict_is_not_refuted(self) -> None:
        """A clean verdict is the one state that licenses the next step."""
        result = _check_adversarial_validation(
            self._seed("**Verdict: NOT-REFUTED (SHIP)** - job `review-abc`, zero findings.")
        )
        self.assertTrue(result.ok, msg=result.message)
        self.assertIn("not-refuted", result.message.lower())

    def test_not_refuted_is_never_read_as_a_refutation(self) -> None:
        """`refuted` is a substring of `not-refuted`; a naive scan inverts the verdict.

        This is the GHI #888 failure shape applied to verdicts - a denial read as an
        assertion. The boundary is asserted on its own so a future regex edit that
        drops the token guards fails here rather than in the field.
        """
        result = _check_adversarial_validation(self._seed("Verdict: not-refuted."))
        self.assertTrue(result.ok, msg=result.message)

    def test_fails_when_the_section_records_no_verdict_at_all(self) -> None:
        """A section that says nothing is the presence-check hole in its pure form."""
        result = _check_adversarial_validation(
            self._seed("The adversary was dispatched and produced findings.")
        )
        self.assertFalse(result.ok, msg=result.message)
        self.assertIsNotNone(result.remediation)

    def test_passes_when_the_degraded_human_floor_is_recorded(self) -> None:
        """`degraded-human-only` is a recordable floor, not a refutation.

        The completion chokepoint returns early on it, so blocking here would make
        the pre-flight stricter than the gate it fronts.
        """
        result = _check_adversarial_validation(
            self._seed("**Verdict: degraded-human-only** - no cross-vendor adversary available.")
        )
        self.assertTrue(result.ok, msg=result.message)

    def test_verdict_scan_stops_at_the_end_of_the_step_4b_section(self) -> None:
        """A verdict word in a LATER section is prose, not this OBPI's Step-4b verdict."""
        result = _check_adversarial_validation(
            self._seed(
                "**Verdict: NOT-REFUTED** - zero findings.",
                trailing=(
                    "\n### Value Narrative\n\nBefore this OBPI a refuted claim could "
                    "reach attestation.\n"
                ),
            )
        )
        self.assertTrue(result.ok, msg=result.message)

    def test_missing_step_4b_section_still_fails(self) -> None:
        """GHI #676's original assertion survives the content check."""
        import tempfile

        td = tempfile.mkdtemp()
        path = Path(td) / "OBPI-0.1.0-01-fixture.md"
        path.write_text(
            "---\nid: OBPI-0.1.0-01\nparent: ADR-0.1.0\nstatus: pending\n"
            "lane: Heavy\n---\n\n# Fixture\n",
            encoding="utf-8",
        )
        result = _check_adversarial_validation(path)
        self.assertFalse(result.ok, msg=result.message)

    def test_lite_lane_brief_is_exempt_regardless_of_verdict(self) -> None:
        """Step 4b is a heavy-lane gate; the lite lane never reaches the verdict read."""
        result = _check_adversarial_validation(self._seed("**Verdict: REFUTED**", lane="Lite"))
        self.assertTrue(result.ok, msg=result.message)


class TestPrecompleteStandingVerdictDeclaration(unittest.TestCase):
    """A discharged refutation must be declarable, not permanently blocking (GHI #964).

    GHI #879 made the check fail closed whenever a refutation token APPEARS, because
    position cannot tell which verdict stands. That direction is right, but it left a
    converged Step 4b with no way out: under the GHI #960 loop doctrine a refutation is
    an INPUT to ``if(4a && 4b) pass; else loop``, so the normal shape of a finished
    Step 4b is a history of refuted rounds ending in a clean one. The more faithfully a
    brief records its rounds, the more certainly the pre-flight failed.

    The remedy is a DECLARATION the check can read, never a position rule: a brief says
    which verdict stands, and the check believes the declaration rather than guessing.
    Absent a declaration the pre-existing fail-closed behavior is unchanged.
    """

    _seed = staticmethod(TestPrecompleteAdversarialValidationCheck._seed)

    def test_declared_standing_verdict_clears_discharged_refutation_history(self) -> None:
        # The GHI #964 reproduction: rounds 6-11 REFUTED, round 12 not-refuted and
        # declared standing. This is the case that could never pass before.
        result = _check_adversarial_validation(
            self._seed(
                "**Standing verdict:** not-refuted (round 12, receipt "
                "`arb-step-codexadversary-fe5cf406`)\n\n"
                "Round 11 is SUPERSEDED. Its verdict was `REFUTED`.\n"
                "Round 10 is SUPERSEDED. Its verdict was `REFUTED-WITH-CAVEATS`.\n"
            )
        )
        self.assertTrue(result.ok, msg=result.message)
        self.assertIn("not-refuted", result.message.lower())

    def test_declared_standing_refutation_still_fails(self) -> None:
        # A declaration is not an escape hatch: declaring that a REFUTATION stands
        # must still block. The check believes the brief in both directions.
        result = _check_adversarial_validation(
            self._seed(
                "**Standing verdict:** refuted\n\nRound 1 returned `not-refuted`, "
                "but round 2 found a blocking defect.\n"
            )
        )
        self.assertFalse(result.ok, msg=result.message)
        self.assertIn("refuted", result.message.lower())

    def test_declaration_is_tolerant_of_emphasis_and_case(self) -> None:
        # Briefs are hand-authored markdown; the declaration must not hinge on
        # whether the author bolded it.
        for body in (
            "Standing verdict: NOT-REFUTED\n\nEarlier round: `REFUTED`.\n",
            "**Standing Verdict:** not-refuted\n\nEarlier round: `REFUTED`.\n",
            "**standing verdict**: not-refuted\n\nEarlier round: `REFUTED`.\n",
        ):
            with self.subTest(body=body.splitlines()[0]):
                result = _check_adversarial_validation(self._seed(body))
                self.assertTrue(result.ok, msg=result.message)

    def test_conflicting_declarations_fail_rather_than_pick_one(self) -> None:
        # Two declarations disagreeing is the exact ambiguity this check exists to
        # refuse. Picking either one silently would reintroduce the position rule
        # by the back door.
        result = _check_adversarial_validation(
            self._seed("**Standing verdict:** not-refuted\n\n**Standing verdict:** refuted\n")
        )
        self.assertFalse(result.ok, msg=result.message)
        self.assertIn("conflict", result.message.lower())

    def test_unrecognized_declared_verdict_fails(self) -> None:
        # A declaration naming a token outside the completion command's vocabulary
        # is not a verdict; treating it as one would let any word license the step.
        result = _check_adversarial_validation(
            self._seed("**Standing verdict:** shipped\n\nEarlier round: `REFUTED`.\n")
        )
        self.assertFalse(result.ok, msg=result.message)

    def test_declaration_outside_the_step_4b_section_is_ignored(self) -> None:
        # The section boundary is load-bearing: a declaration in a later section
        # must not reach back and clear this OBPI's refutation.
        result = _check_adversarial_validation(
            self._seed(
                "Round 1 verdict: `REFUTED`.\n",
                trailing="\n### Value Narrative\n\n**Standing verdict:** not-refuted\n",
            )
        )
        self.assertFalse(result.ok, msg=result.message)

    def test_remediation_does_not_offer_the_completion_path_960_removed(self) -> None:
        # The old remediation told the operator to run
        # `--adversary-verdict refuted --adversary-resolution`. GHI #960 removed that
        # path: _enforce_adversarial_validation refuses every refutation verdict
        # regardless of resolution. Naming a refused remedy is worse than naming none.
        result = _check_adversarial_validation(self._seed("Round 1 verdict: `REFUTED`.\n"))
        self.assertFalse(result.ok, msg=result.message)
        assert result.remediation is not None
        self.assertNotIn("--adversary-verdict refuted", result.remediation)

    def test_remediation_names_the_declaration_as_the_overturn_remedy(self) -> None:
        # The old remediation said "if the refutation was overturned, say so in the
        # section" while nothing the section could say cleared the check. The
        # remediation must name a remedy that actually works.
        result = _check_adversarial_validation(self._seed("Round 1 verdict: `REFUTED`.\n"))
        assert result.remediation is not None
        self.assertIn("Standing verdict", result.remediation)

    def test_headings_and_prose_using_the_words_are_not_declarations(self) -> None:
        """A sentence using the words is not a declaration — the real-world shape.

        OBPI-0.35.0-04 carries three round headings of exactly this form. A
        colon-only rule read all three as declarations and then refused the brief for
        "conflicting standing verdicts" it had invented itself. The declaration must
        own its line; caught by running the check against the real brief, not by the
        fixtures above, which is why this shape is pinned verbatim.
        """
        result = _check_adversarial_validation(
            self._seed(
                "#### Round 10 — THE STANDING VERDICT: round 9's root CLOSED, a new high\n\n"
                "#### Round 12 — THE STANDING VERDICT: NOT-REFUTED, the acceptance round\n\n"
                "Round 11 verdict was `REFUTED`.\n"
            )
        )
        # No declaration was made, so the refutation in the history still fails closed.
        self.assertFalse(result.ok, msg=result.message)
        self.assertNotIn("conflict", result.message.lower())
        self.assertIn("refuted", result.message.lower())

    def test_declaration_is_found_when_indented_or_quoted(self) -> None:
        """Leading indentation, a list dash or a blockquote marker are still line-start."""
        for prefix in ("  ", "- ", "> "):
            with self.subTest(prefix=prefix):
                result = _check_adversarial_validation(
                    self._seed(
                        f"{prefix}**Standing verdict:** not-refuted\n\nEarlier round: `REFUTED`.\n"
                    )
                )
                self.assertTrue(result.ok, msg=result.message)

    def test_no_declaration_and_no_refutation_still_passes(self) -> None:
        # The declaration is required only to discharge a refutation; a clean
        # section needs nothing new.
        result = _check_adversarial_validation(self._seed("**Verdict: NOT-REFUTED** - clean."))
        self.assertTrue(result.ok, msg=result.message)


class TestPrecompleteOperatorBlockCheck(unittest.TestCase):
    """Precomplete must not report READY while a human ruling is outstanding (GHI #887).

    `gz obpi precomplete` exists to spare the operator a rejected completion, and
    an agent reads `READY: all N preconditions met` as authorization to solicit
    attestation. On `OBPI-0.35.0-02` four operator decisions were pending while the
    pipeline kept running; nothing in the vocabulary could say so.
    """

    OBPI = "OBPI-0.1.0-01"

    @staticmethod
    def _seed(root: Path, events: list[dict]) -> None:
        gzkit_dir = root / ".gzkit"
        gzkit_dir.mkdir(parents=True, exist_ok=True)
        (gzkit_dir / "ledger.jsonl").write_text(
            "".join(json.dumps(e) + "\n" for e in events), encoding="utf-8"
        )

    def test_passes_when_no_block_is_recorded(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._seed(root, [])
            result = _check_operator_block(root, self.OBPI)
            self.assertEqual(result.name, "operator_block")
            self.assertTrue(result.ok, msg=result.message)

    def test_fails_while_an_operator_ruling_is_outstanding(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._seed(
                root,
                [
                    {
                        "event": "obpi_blocked_on_operator",
                        "id": self.OBPI,
                        "reason": "REQ-04 amendment",
                        "next_operator_action": "amend REQ-04 under attestation",
                    }
                ],
            )
            result = _check_operator_block(root, self.OBPI)
            self.assertFalse(result.ok, msg=result.message)
            self.assertIn("amend REQ-04 under attestation", result.message)
            self.assertIsNotNone(result.remediation)
            assert result.remediation is not None
            self.assertIn("gz obpi unblock", result.remediation)

    def test_passes_again_once_the_operator_has_ruled(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._seed(
                root,
                [
                    {
                        "event": "obpi_blocked_on_operator",
                        "id": self.OBPI,
                        "reason": "REQ-04 amendment",
                        "next_operator_action": "amend REQ-04",
                    },
                    {
                        "event": "obpi_unblocked",
                        "id": self.OBPI,
                        "ruling": "amended",
                        "operator": "g0",
                    },
                ],
            )
            result = _check_operator_block(root, self.OBPI)
            self.assertTrue(result.ok, msg=result.message)

    def test_a_sibling_obpis_block_does_not_stall_this_one(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._seed(
                root,
                [
                    {
                        "event": "obpi_blocked_on_operator",
                        "id": "OBPI-0.1.0-02",
                        "reason": "unrelated",
                        "next_operator_action": "rule on the sibling",
                    }
                ],
            )
            result = _check_operator_block(root, self.OBPI)
            self.assertTrue(result.ok, msg=result.message)

    def test_a_missing_ledger_does_not_invent_a_block(self) -> None:
        """Absence of a ledger is absence of evidence, never a fabricated blocker."""
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            result = _check_operator_block(Path(td), self.OBPI)
            self.assertTrue(result.ok, msg=result.message)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
