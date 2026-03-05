import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from gzkit.hooks.core import record_artifact_edit
from gzkit.hooks.obpi import ObpiValidator
from gzkit.ledger import Ledger, adr_created_event, project_init_event


class TestObpiValidator(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_root = self.test_dir
        self.gzkit_dir = self.project_root / ".gzkit"
        self.gzkit_dir.mkdir()

        # Initialize manifest
        self.manifest_path = self.gzkit_dir / "manifest.json"
        self.manifest_data = {
            "schema": "gzkit.manifest.v1",
            "structure": {"design_root": "docs/design"},
            "gates": {"lite": [1, 2], "heavy": [1, 2, 3, 4, 5]},
        }
        self.manifest_path.write_text(json.dumps(self.manifest_data))

        # Initialize .gzkit.json
        self.config_path = self.project_root / ".gzkit.json"
        self.config_data = {"mode": "lite", "paths": {"ledger": ".gzkit/ledger.jsonl"}}
        self.config_path.write_text(json.dumps(self.config_data))

        # Initialize ledger
        self.ledger_path = self.gzkit_dir / "ledger.jsonl"
        self.ledger = Ledger(self.ledger_path)
        self.ledger.append(project_init_event("test-project", "lite"))

        self.validator = ObpiValidator(self.project_root)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def _create_obpi(
        self,
        adr_id,
        status="Draft",
        summary="- Evidence: Done",
        proof="Proof here",
        attestation=None,
        lane="lite",
    ):
        # Ensure ADR exists in ledger
        self.ledger.append(adr_created_event(adr_id, "PRD-TEST", lane))

        obpi_id = f"OBPI-{adr_id}-01"
        content = f"""---
id: {obpi_id}
parent: {adr_id}
status: {status}
---

# {obpi_id}

### Implementation Summary
{summary}

## Key Proof
{proof}
"""
        if attestation:
            content += f"\n## Human Attestation\n{attestation}\n"

        obpi_path = self.project_root / f"{obpi_id}.md"
        obpi_path.write_text(content)
        return obpi_path

    def test_validate_draft_is_always_valid(self):
        path = self._create_obpi("ADR-0.1.0", status="Draft", summary="...")
        errors = self.validator.validate_file(path)
        self.assertEqual(errors, [])

    def test_validate_lite_completed_substantive(self):
        path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: Finished implementation",
            proof="Works as expected",
        )
        errors = self.validator.validate_file(path)
        self.assertEqual(errors, [])

    def test_validate_lite_completed_missing_summary(self):
        path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: TBD",
            proof="Proof",
        )
        errors = self.validator.validate_file(path)
        self.assertIn("Missing or non-substantive 'Implementation Summary'.", errors)

    def test_validate_heavy_completed_missing_attestation(self):
        # Heavy lane inherits human attestation requirement
        path = self._create_obpi(
            "ADR-0.2.0",
            status="Completed",
            summary="- Done: Yes",
            proof="Proof",
            lane="heavy",
        )
        errors = self.validator.validate_file(path)
        self.assertIn("Heavy/Foundation OBPI requires a '## Human Attestation' section.", errors)

    def test_validate_foundation_completed_requires_attestation(self):
        # 0.0.x series always requires attestation
        path = self._create_obpi(
            "ADR-0.0.1",
            status="Completed",
            summary="- Done: Yes",
            proof="Proof",
            lane="lite",
        )
        errors = self.validator.validate_file(path)
        self.assertIn("Heavy/Foundation OBPI requires a '## Human Attestation' section.", errors)

    def test_validate_heavy_completed_valid_attestation(self):
        attestation = (
            f"- Attestor: human:jeff\n- Attestation: Looks good\n- Date: {date.today().isoformat()}"
        )
        path = self._create_obpi(
            "ADR-0.2.0",
            status="Completed",
            summary="- Done: Yes",
            proof="Proof",
            attestation=attestation,
            lane="heavy",
        )
        errors = self.validator.validate_file(path)
        self.assertEqual(errors, [])

    def test_validate_heavy_completed_invalid_attestor(self):
        attestation = (
            f"- Attestor: agent:claudia\n- Attestation: Done\n- Date: {date.today().isoformat()}"
        )
        path = self._create_obpi(
            "ADR-0.2.0",
            status="Completed",
            summary="- Done: Yes",
            proof="Proof",
            attestation=attestation,
            lane="heavy",
        )
        errors = self.validator.validate_file(path)
        self.assertIn("Human attestation block requires 'Attestor: human:<name>'.", errors)

    def test_validate_strict_placeholders(self):
        path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: TODO",
            proof="...",
        )
        errors = self.validator.validate_file(path)
        self.assertIn("Missing or non-substantive 'Implementation Summary'.", errors)
        self.assertIn("Missing or non-substantive 'Key Proof'.", errors)

    def test_recorder_appends_receipt_to_ledger(self):
        # Create a valid completed OBPI
        adr_id = "ADR-0.1.0"
        obpi_path = self._create_obpi(
            adr_id,
            status="Completed",
            summary="- Done: Yes",
            proof="Verified",
        )
        # Move it to a subfolder to match GOVERNANCE_PATTERNS
        final_dir = self.project_root / "docs/design/adr/pre-release/ADR-0.1.0/obpis"
        final_dir.mkdir(parents=True, exist_ok=True)
        final_path = final_dir / obpi_path.name
        obpi_path.rename(final_path)
        rel_path = str(final_path.relative_to(self.project_root))

        # Run the record_artifact_edit hook
        record_artifact_edit(self.project_root, rel_path, session="test-session")

        # Check ledger
        events = self.ledger.read_all()

        # Should have: project_init, adr_created, artifact_edited, obpi_receipt_emitted
        self.assertTrue(any(e.event == "obpi_receipt_emitted" for e in events))

        receipt = [e for e in events if e.event == "obpi_receipt_emitted"][-1]
        self.assertEqual(receipt.extra.get("receipt_event"), "completed")
        self.assertEqual(receipt.id, final_path.stem)

        # Check anchor (will be 0000000 since we're in a temp dir without git)
        anchor = receipt.extra.get("anchor")
        self.assertIsNotNone(anchor)
        self.assertEqual(anchor.get("commit"), "0000000")
        self.assertEqual(anchor.get("semver"), "0.1.0")
