import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import date
from pathlib import Path
from unittest.mock import patch

from gzkit.hooks.core import record_artifact_edit
from gzkit.hooks.obpi import ObpiValidator
from gzkit.ledger import Ledger, adr_created_event, project_init_event
from gzkit.traceability import covers  # noqa: F401


class TestObpiValidator(unittest.TestCase):
    def setUp(self):
        self._tmp_ctx = tempfile.TemporaryDirectory()
        self.test_dir = Path(self._tmp_ctx.name)
        self.project_root = self.test_dir
        self.gzkit_dir = self.project_root / ".gzkit"
        self.gzkit_dir.mkdir()

        manifest_path = self.gzkit_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(
                {
                    "schema": "gzkit.manifest.v1",
                    "structure": {"design_root": "docs/design"},
                    "gates": {"lite": [1, 2], "heavy": [1, 2, 3, 4, 5]},
                }
            ),
            encoding="utf-8",
        )

        config_path = self.project_root / ".gzkit.json"
        config_path.write_text(
            json.dumps({"mode": "lite", "paths": {"ledger": ".gzkit/ledger.jsonl"}}),
            encoding="utf-8",
        )

        self.ledger_path = self.gzkit_dir / "ledger.jsonl"
        self.ledger = Ledger(self.ledger_path)
        self.ledger.append(project_init_event("test-project", "lite"))

        self._git("init", "-b", "main")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test User")
        self._commit_all("chore: initial")

        self.validator = ObpiValidator(self.project_root)

    def tearDown(self):
        self._tmp_ctx.cleanup()

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.project_root,
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def _commit_all(self, message: str) -> None:
        self._git("add", "-A")
        status = self._git("status", "--porcelain")
        if status:
            self._git("commit", "-m", message)

    def _register_adr(self, adr_id: str, lane: str = "lite") -> None:
        self.ledger.append(adr_created_event(adr_id, "PRD-TEST", lane))
        self._commit_all(f"chore: register {adr_id}")

    def _create_obpi(
        self,
        adr_id: str,
        *,
        status: str = "Draft",
        summary: str = "- Evidence: Done",
        proof: str = "Proof here",
        attestation: str | None = None,
        lane: str = "lite",
        relative_path: str | None = None,
        allowed_paths: list[str] | None = None,
    ) -> Path:
        self._register_adr(adr_id, lane)

        obpi_id = f"OBPI-{adr_id}-01"
        rel_path = relative_path or f"{obpi_id}.md"
        path = self.project_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)

        allowlist = allowed_paths or [rel_path]
        allowlist_lines = "\n".join(f"- `{item}` - in scope" for item in allowlist)
        content = f"""---
id: {obpi_id}
parent: {adr_id}
status: {status}
---

# {obpi_id}

## Allowed Paths
{allowlist_lines}

### Implementation Summary
{summary}

## Key Proof
{proof}
"""
        if attestation:
            content += f"\n## Human Attestation\n{attestation}\n"

        path.write_text(content, encoding="utf-8")
        return path

    def test_validate_draft_is_always_valid(self):
        path = self._create_obpi("ADR-0.1.0", status="Draft", summary="...")
        errors = self.validator.validate_file(path)
        self.assertEqual(errors, [])

    @covers("REQ-0.11.0-02-01")
    def test_validate_completed_passes_with_allowlisted_changes(self):
        obpi_path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: Finished implementation",
            proof="Works as expected",
            allowed_paths=["OBPI-ADR-0.1.0-01.md", "src/**"],
        )
        module_path = self.project_root / "src" / "demo.py"
        module_path.parent.mkdir(parents=True, exist_ok=True)
        module_path.write_text("print('ok')\n", encoding="utf-8")

        errors = self.validator.validate_file(obpi_path)
        self.assertEqual(errors, [])

    @covers("REQ-0.11.0-01-01")
    def test_validate_completed_blocks_out_of_scope_changes(self):
        obpi_path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: Finished implementation",
            proof="Works as expected",
        )
        outside_path = self.project_root / "docs" / "outside.md"
        outside_path.parent.mkdir(parents=True, exist_ok=True)
        outside_path.write_text("out of scope\n", encoding="utf-8")

        errors = self.validator.validate_file(obpi_path)
        self.assertIn(
            "Changed-files audit found out-of-allowlist path: docs/outside.md. "
            "Amend the OBPI or revert the change.",
            errors,
        )

    @covers("REQ-0.11.0-02-02")
    def test_validate_completed_requires_allowed_paths(self):
        self._register_adr("ADR-0.1.0")
        obpi_path = self.project_root / "OBPI-ADR-0.1.0-01.md"
        obpi_path.write_text(
            "---\n"
            "id: OBPI-ADR-0.1.0-01\n"
            "parent: ADR-0.1.0\n"
            "status: Completed\n"
            "---\n\n"
            "# OBPI-ADR-0.1.0-01\n\n"
            "### Implementation Summary\n"
            "- Task: Finished implementation\n\n"
            "## Key Proof\n"
            "Works as expected\n",
            encoding="utf-8",
        )

        errors = self.validator.validate_file(obpi_path)
        self.assertIn("Missing or empty 'Allowed Paths' allowlist.", errors)

    @covers("REQ-0.11.0-02-03")
    def test_validate_heavy_completed_missing_attestation(self):
        path = self._create_obpi(
            "ADR-0.2.0",
            status="Completed",
            summary="- Done: Yes",
            proof="Proof",
            lane="heavy",
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

    def test_validate_requires_git_repo(self):
        path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: Finished implementation",
            proof="Works as expected",
        )
        import shutil
        import stat

        def _force_remove_readonly(func, path, exc_info):  # noqa: ARG001
            os.chmod(path, stat.S_IWRITE)
            func(path)

        shutil.rmtree(self.project_root / ".git", onexc=_force_remove_readonly)

        errors = self.validator.validate_file(path)
        self.assertIn("Not a git repository.", errors)

    def test_validate_blocks_skip_values_that_bypass_xenon(self):
        path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: Finished implementation",
            proof="Works as expected",
        )
        original_skip = os.environ.get("SKIP")
        os.environ["SKIP"] = "xenon-complexity"
        try:
            errors = self.validator.validate_file(path)
        finally:
            if original_skip is None:
                os.environ.pop("SKIP", None)
            else:
                os.environ["SKIP"] = original_skip

        self.assertIn(
            "Refusing completion validation with SKIP that can bypass xenon complexity checks.",
            errors,
        )

    @covers("REQ-0.11.0-03-01")
    @covers("REQ-0.11.0-03-02")
    def test_recorder_appends_receipt_to_ledger(self):
        final_rel_path = "docs/design/adr/pre-release/ADR-0.1.0/obpis/OBPI-ADR-0.1.0-01.md"
        final_path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Done: Yes",
            proof="Verified",
            relative_path=final_rel_path,
            allowed_paths=["docs/design/adr/pre-release/ADR-0.1.0/**"],
        )
        rel_path = final_path.relative_to(self.project_root).as_posix()

        record_artifact_edit(self.project_root, rel_path, session="test-session")

        events = self.ledger.read_all()
        self.assertTrue(any(e.event == "obpi_receipt_emitted" for e in events))

        receipt = [e for e in events if e.event == "obpi_receipt_emitted"][-1]
        self.assertEqual(receipt.extra.get("receipt_event"), "completed")
        self.assertEqual(receipt.id, final_path.stem)
        evidence = receipt.extra.get("evidence")
        self.assertIsInstance(evidence, dict)
        assert isinstance(evidence, dict)
        self.assertEqual(evidence.get("key_proof"), "Verified")
        self.assertTrue(evidence.get("req_proof_inputs"))
        self.assertEqual(evidence.get("recorder_source"), "hook:auto")
        self.assertEqual(
            evidence.get("recorder_warnings"),
            ["Working tree was dirty when the completion receipt was captured."],
        )

        scope_audit = evidence.get("scope_audit")
        self.assertEqual(
            scope_audit,
            {
                "allowlist": ["docs/design/adr/pre-release/ADR-0.1.0/**"],
                "changed_files": [rel_path],
                "out_of_scope_files": [],
            },
        )
        git_sync_state = evidence.get("git_sync_state")
        self.assertIsInstance(git_sync_state, dict)
        self.assertTrue(git_sync_state.get("dirty"))
        self.assertIsInstance(git_sync_state.get("ahead"), int)
        self.assertIsInstance(git_sync_state.get("behind"), int)
        self.assertIsInstance(git_sync_state.get("blockers"), list)

        anchor = receipt.extra.get("anchor")
        self.assertIsNotNone(anchor)
        assert isinstance(anchor, dict)
        self.assertNotEqual(anchor.get("commit"), "0000000")
        self.assertEqual(anchor.get("semver"), "0.1.0")

    @covers("REQ-0.11.0-03-03")
    def test_recorder_warns_but_keeps_receipt_when_anchor_capture_degrades(self):
        final_rel_path = "docs/design/adr/pre-release/ADR-0.1.0/obpis/OBPI-ADR-0.1.0-01.md"
        final_path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Done: Yes",
            proof="Verified",
            relative_path=final_rel_path,
            allowed_paths=["docs/design/adr/pre-release/ADR-0.1.0/**"],
        )
        rel_path = final_path.relative_to(self.project_root).as_posix()

        with patch(
            "gzkit.hooks.core.capture_validation_anchor_with_warnings",
            return_value=(None, ["Could not resolve HEAD commit for receipt anchor."]),
        ):
            record_artifact_edit(self.project_root, rel_path, session="test-session")

        receipt = [e for e in self.ledger.read_all() if e.event == "obpi_receipt_emitted"][-1]
        evidence = receipt.extra.get("evidence")
        self.assertIsInstance(evidence, dict)
        assert isinstance(evidence, dict)
        self.assertIn(
            "Could not resolve HEAD commit for receipt anchor.",
            evidence.get("recorder_warnings", []),
        )
        self.assertNotIn("anchor", receipt.extra)

    @covers("REQ-0.11.0-03-02")
    def test_recorder_append_failure_is_warning_only(self):
        final_rel_path = "docs/design/adr/pre-release/ADR-0.1.0/obpis/OBPI-ADR-0.1.0-01.md"
        final_path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Done: Yes",
            proof="Verified",
            relative_path=final_rel_path,
            allowed_paths=["docs/design/adr/pre-release/ADR-0.1.0/**"],
        )
        rel_path = final_path.relative_to(self.project_root).as_posix()
        stderr = io.StringIO()

        with (
            patch.object(Ledger, "append", side_effect=[None, OSError("disk full")]),
            redirect_stderr(stderr),
        ):
            result = record_artifact_edit(self.project_root, rel_path, session="test-session")

        self.assertTrue(result)
        self.assertIn("Could not append OBPI completion receipt", stderr.getvalue())

    def test_validate_blocks_merge_head(self):
        path = self._create_obpi(
            "ADR-0.1.0",
            status="Completed",
            summary="- Task: Finished implementation",
            proof="Works as expected",
        )
        current_branch = self._git("rev-parse", "--abbrev-ref", "HEAD")
        self._git("checkout", "-b", "feature")
        (self.project_root / "feature.txt").write_text("feature\n", encoding="utf-8")
        self._commit_all("feat: branch change")
        self._git("checkout", current_branch)
        (self.project_root / "main.txt").write_text("main\n", encoding="utf-8")
        self._commit_all("feat: main change")
        self._git("merge", "--no-ff", "feature", "-m", "merge feature")
        path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

        errors = self.validator.validate_file(path)
        self.assertIn("Merge commit at HEAD. Linearize history before completion.", errors)

    # ------------------------------------------------------------------
    # Template scaffold detection (GHI #27)
    # ------------------------------------------------------------------

    def _create_scaffold_obpi(self, adr_id: str, *, status: str = "Draft") -> Path:
        """Create an OBPI with the exact template defaults from superbook."""
        self._register_adr(adr_id)
        obpi_id = f"OBPI-{adr_id}-01"
        path = self.project_root / f"{obpi_id}.md"
        path.write_text(
            f"---\nid: {obpi_id}\nparent: {adr_id}\nstatus: {status}\n---\n\n"
            f"# {obpi_id}\n\n"
            "## Allowed Paths\n"
            "- `src/module/` - Reason this is in scope\n"
            "- `tests/test_module.py` - Reason\n\n"
            "## Requirements (FAIL-CLOSED)\n"
            "1. REQUIREMENT: First constraint\n"
            "1. REQUIREMENT: Second constraint\n"
            "1. NEVER: What must not happen\n"
            "1. ALWAYS: What must always be true\n\n"
            "## Acceptance Criteria\n"
            "- [ ] REQ-0.1.0-01-01: Given/When/Then behavior criterion 1\n"
            "- [ ] REQ-0.1.0-01-02: Given/When/Then behavior criterion 2\n\n"
            "### Implementation Summary\n"
            "- Files created/modified:\n"
            "- Tests added:\n\n"
            "## Key Proof\n\n",
            encoding="utf-8",
        )
        return path

    def test_draft_scaffold_detected(self):
        """Draft OBPIs with template scaffold return warnings."""
        path = self._create_scaffold_obpi("ADR-0.1.0", status="Draft")
        errors = self.validator.validate_file(path)
        self.assertTrue(len(errors) >= 3, f"Expected >=3 scaffold warnings, got {errors}")
        self.assertTrue(any("src/module/" in e for e in errors))
        self.assertTrue(any("First constraint" in e for e in errors))
        self.assertTrue(any("Given/When/Then" in e for e in errors))

    def test_completed_scaffold_also_detected(self):
        """Completed OBPIs with template scaffold include scaffold errors."""
        path = self._create_scaffold_obpi("ADR-0.1.0", status="Completed")
        errors = self.validator.validate_file(path)
        self.assertTrue(any("src/module/" in e for e in errors))

    def test_draft_without_scaffold_passes(self):
        """Draft OBPIs with real content return no warnings."""
        path = self._create_obpi("ADR-0.1.0", status="Draft", summary="- Done: Real work")
        errors = self.validator.validate_file(path)
        self.assertEqual(errors, [])

    def test_scaffold_partial_detection(self):
        """Brief with only some scaffold sections still catches those."""
        self._register_adr("ADR-0.1.0")
        obpi_id = "OBPI-ADR-0.1.0-01"
        path = self.project_root / f"{obpi_id}.md"
        path.write_text(
            f"---\nid: {obpi_id}\nparent: ADR-0.1.0\nstatus: Draft\n---\n\n"
            f"# {obpi_id}\n\n"
            "## Allowed Paths\n"
            "- `src/gzkit/closeout.py` - Real path\n\n"
            "## Requirements (FAIL-CLOSED)\n"
            "1. REQUIREMENT: First constraint\n\n"
            "## Acceptance Criteria\n"
            "- [ ] REQ-0.1.0-01-01: Closeout bumps version\n",
            encoding="utf-8",
        )
        errors = self.validator.validate_file(path)
        self.assertEqual(len(errors), 1)
        self.assertIn("First constraint", errors[0])
