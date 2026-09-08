"""Real acceptance history governs pipeline transitions (GHI #985).

Semantic proof executes real fixture tests and controls. Reviewer transport
captures are synthetic. Unrelated quality-command dispatch is stubbed so these
checks exercise acceptance sequencing, not the complete project QA suite.
"""

import io
import json
from unittest.mock import patch

from rich.console import Console

from gzkit.acceptance_store import (
    acceptance_status,
    initialize,
    record_proof,
    record_review,
)
from gzkit.commands.obpi_precomplete import _check_acceptance_records
from gzkit.commands.obpi_stages import (
    _run_pipeline_ceremony_stage,
    _run_pipeline_verify_stage,
)
from tests.test_acceptance_execution import BRIEF, REQ, ExecutionFixture
from tests.test_acceptance_store import OBPI, captured_receipt


class TestAcceptanceAdvancement(ExecutionFixture):
    def setUp(self):
        super().setUp()
        self.write(".gzkit.json", json.dumps({"paths": {"design_root": "design"}}))
        self.brief = self.brief.rename(self.brief.with_name(f"{OBPI}.md"))
        initialize(self.root, OBPI, "implementer-session")
        self.output = io.StringIO()
        self.console = Console(file=self.output, width=180, color_system=None)

    def verify(self):
        _run_pipeline_verify_stage(
            project_root=self.root,
            plans_dir=self.root / ".claude/plans",
            obpi_id=OBPI,
            obpi_content=self.brief.read_text(encoding="utf-8"),
            lane="lite",
            resolved_parent="ADR-0.1.0-engine",
            requires_human_attestation=True,
            attestor=None,
            evidence_json=None,
        )

    def test_green_commands_cannot_advance_a_real_brief_without_required_proof(self):
        """The refusal identifies the missing REQ proof, not a missing fixture file."""
        with (
            patch("gzkit.commands.obpi_stages.console", self.console),
            patch(
                "gzkit.commands.obpi_stages._dispatch_verification_commands", return_value=[]
            ) as qa,
            patch("gzkit.commands.obpi_stages._run_pipeline_ceremony_stage") as ceremony,
            self.assertRaises(SystemExit) as raised,
        ):
            self.verify()
        self.assertEqual(raised.exception.code, 3)
        self.assertIn(f"{REQ}: missing proof", self.output.getvalue())
        self.assertNotIn("No canonical brief", self.output.getvalue())
        qa.assert_not_called()
        ceremony.assert_not_called()

    def test_real_proof_and_reviews_drive_ceremony_without_history_reopening_acceptance(self):
        proof = self.run_proof()
        self.assertTrue(proof.valid, proof.evidence)
        record_proof(self.root, OBPI, proof)
        for stage in ("spec", "quality"):
            record_review(self.root, OBPI, captured_receipt(proof, stage))
        self.assertTrue(acceptance_status(self.root, OBPI, stage="stage2").ready)
        self.assertFalse(_check_acceptance_records(self.root, OBPI).ok)
        with (
            patch("gzkit.commands.obpi_stages.console", self.console),
            patch(
                "gzkit.commands.obpi_stages._dispatch_verification_commands", return_value=[]
            ) as qa,
        ):
            self.verify()
        qa.assert_called_once()
        self.assertIn(
            "Stage 4a proof is ready for independent Step 4b review", self.output.getvalue()
        )
        self.assertNotIn("Human attestation required.", self.output.getvalue())

        record_review(self.root, OBPI, captured_receipt(proof, "adversarial"))
        self.brief.write_text(
            BRIEF.replace(
                "Historical round one was wrong.",
                "Standing verdict in historical round 14: refuted.\nThe optional audit was wrong.",
            ),
            encoding="utf-8",
        )
        self.assertTrue(_check_acceptance_records(self.root, OBPI).ok)
        self.output.seek(0)
        self.output.truncate()
        with (
            patch("gzkit.commands.obpi_stages.console", self.console),
            patch("gzkit.commands.obpi_stages._dispatch_verification_commands", return_value=[]),
        ):
            self.verify()
        self.assertIn("Human attestation required.", self.output.getvalue())
        self.assertNotIn("Record the independent review before requesting", self.output.getvalue())

        self.write("src/engine.py", "def double(value):\n    return value * 3\n")
        check = _check_acceptance_records(self.root, OBPI)
        self.assertFalse(check.ok)
        self.assertIn("stale inputs", check.message)
        with (
            patch("gzkit.commands.obpi_stages.console", self.console),
            patch("gzkit.commands.obpi_stages._dispatch_verification_commands") as qa,
            self.assertRaises(SystemExit) as raised,
        ):
            self.verify()
        self.assertEqual(raised.exception.code, 3)
        qa.assert_not_called()

    def test_direct_ceremony_entry_cannot_bypass_missing_proof(self):
        with (
            patch("gzkit.commands.obpi_stages.console", self.console),
            self.assertRaises(SystemExit) as raised,
        ):
            _run_pipeline_ceremony_stage(
                project_root=self.root,
                plans_dir=self.root / ".claude/plans",
                obpi_id=OBPI,
                obpi_content=self.brief.read_text(encoding="utf-8"),
                resolved_parent="ADR-0.1.0-engine",
                requires_human_attestation=True,
                attestor=None,
                evidence_json=None,
            )
        self.assertEqual(raised.exception.code, 3)
        self.assertIn(f"{REQ}: missing proof", self.output.getvalue())
        self.assertNotIn("Human attestation required.", self.output.getvalue())
