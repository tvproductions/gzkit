"""GHI #987: retain review output through the real ARB CLI and persisted receipt."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestStepOutputRetentionCli(unittest.TestCase):
    """Exercise parser, handler, child execution and receipt storage without mocks."""

    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory()
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name)
        self.receipts = self.root / "receipts"
        self.project = Path(__file__).resolve().parents[2]
        self.stdout = "stdout-begin:" + "界" * 9001 + ":stdout-end\n"
        self.stderr = "stderr-begin:" + "é" * 9011 + ":stderr-end\n"

    def invoke(self, limit=None, *, exit_status=0):
        command = [
            "uv",
            "run",
            "--project",
            str(self.project),
            "--no-sync",
            "gz",
            "arb",
            "step",
            "--name",
            "outputprobe",
            "--quiet",
        ]
        if limit is not None:
            command.extend(["--max-output-chars", str(limit)])
        child = (
            "import sys; sys.stdout.write(sys.argv[1]); sys.stderr.write(sys.argv[2]); "
            "sys.exit(int(sys.argv[3]))"
        )
        command.extend(
            ["--", sys.executable, "-c", child, self.stdout, self.stderr, str(exit_status)]
        )
        completed = subprocess.run(
            command,
            cwd=self.root,
            env={**os.environ, "GZKIT_ARB_RECEIPTS_ROOT": str(self.receipts)},
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
        self.assertEqual(completed.returncode, exit_status, completed.stdout + completed.stderr)
        paths = list(self.receipts.glob("arb-step-outputprobe-*.json"))
        self.assertEqual(len(paths), 1, completed.stdout + completed.stderr)
        return json.loads(paths[0].read_text(encoding="utf-8"))

    def test_negative_limit_retains_complete_stdout_and_stderr(self):
        receipt = self.invoke(-1)
        self.assertEqual(receipt["stdout_tail"], self.stdout)
        self.assertEqual(receipt["stderr_tail"], self.stderr)
        self.assertFalse(receipt["stdout_truncated"])
        self.assertFalse(receipt["stderr_truncated"])

    def test_omitted_limit_preserves_eight_thousand_character_tails(self):
        receipt = self.invoke()
        self.assertEqual(receipt["stdout_tail"], self.stdout[-8000:])
        self.assertEqual(receipt["stderr_tail"], self.stderr[-8000:])
        self.assertTrue(receipt["stdout_truncated"])
        self.assertTrue(receipt["stderr_truncated"])

    def test_finite_limit_retains_exact_requested_suffix(self):
        receipt = self.invoke(127)
        self.assertEqual(receipt["stdout_tail"], self.stdout[-127:])
        self.assertEqual(receipt["stderr_tail"], self.stderr[-127:])
        self.assertTrue(receipt["stdout_truncated"])
        self.assertTrue(receipt["stderr_truncated"])

    def test_zero_limit_retains_no_characters(self):
        receipt = self.invoke(0)
        self.assertEqual(receipt["stdout_tail"], "")
        self.assertEqual(receipt["stderr_tail"], "")
        self.assertTrue(receipt["stdout_truncated"])
        self.assertTrue(receipt["stderr_truncated"])

    def test_larger_limit_keeps_shorter_output_without_truncation(self):
        receipt = self.invoke(10000)
        self.assertEqual(receipt["stdout_tail"], self.stdout)
        self.assertEqual(receipt["stderr_tail"], self.stderr)
        self.assertFalse(receipt["stdout_truncated"])
        self.assertFalse(receipt["stderr_truncated"])

    def test_unbounded_capture_preserves_failing_commands_exit_status(self):
        receipt = self.invoke(-2, exit_status=7)
        self.assertEqual(receipt["exit_status"], 7)
        self.assertEqual(receipt["stdout_tail"], self.stdout)
        self.assertEqual(receipt["stderr_tail"], self.stderr)
        self.assertFalse(receipt["stdout_truncated"])
        self.assertFalse(receipt["stderr_truncated"])


class TestLongReviewReceiptImport(unittest.TestCase):
    """Synthetic reviewer transport exercises persisted ARB output → real CLI import."""

    def test_complete_long_review_json_imports_from_the_emitted_run_id(self):
        from gzkit.acceptance_store import initialize, load_history
        from tests.test_acceptance_execution import REQ, ExecutionFixture
        from tests.test_acceptance_store import OBPI

        fixture = ExecutionFixture()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.write(".gzkit.json", json.dumps({"paths": {"design_root": "design"}}))
        fixture.brief = fixture.brief.rename(fixture.brief.with_name(f"{OBPI}.md"))
        initialize(fixture.root, OBPI, "fixture-implementer")
        description = "Synthetic missing-proof finding: " + "界" * 9000
        review = {
            "schema": "gzkit.acceptance.review.v1",
            "stage": "spec",
            "obligation_ids": [REQ],
            "proof_ids": [],
            "accepted_proof_ids": [],
            "findings": [
                {
                    "id": "F-output",
                    "obligation_id": REQ,
                    "kind": "missing-proof",
                    "description": description,
                }
            ],
            "closures": [],
            "reviewer_id": "synthetic-codex-fixture",
            "verdict": "refuted",
        }
        # This file deliberately models the transport shape; it is not an
        # independent reviewer and establishes no semantic approval claim.
        script = fixture.write(
            "codex-fixture.py",
            (
                "import json, sys\nfrom pathlib import Path\n"
                "from gzkit.acceptance_execution import input_digest\n"
                f"review = {review!r}\n"
                f"review['input_digest'] = input_digest(Path.cwd(), Path({str(fixture.brief)!r}))\n"
                "print(json.dumps(review, ensure_ascii=False))\n"
                "sys.stderr.write('Synthetic transport diagnostic: ' + 'x' * 9000)\n"
            ),
        )
        project = Path(__file__).resolve().parents[2]
        prefix = ["uv", "run", "--project", str(project), "--no-sync", "gz"]
        receipts = fixture.root / "receipts"
        environment = {**os.environ, "GZKIT_ARB_RECEIPTS_ROOT": str(receipts)}
        wrapped = subprocess.run(
            [
                *prefix,
                "arb",
                "step",
                "--name",
                "reviewfixture",
                "--quiet",
                "--max-output-chars",
                "-1",
                "--",
                "python",
                str(script),
            ],
            cwd=fixture.root,
            env=environment,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
        self.assertEqual(wrapped.returncode, 0, wrapped.stdout + wrapped.stderr)
        (receipt_path,) = receipts.glob("arb-step-reviewfixture-*.json")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        self.assertFalse(receipt["stdout_truncated"])
        self.assertFalse(receipt["stderr_truncated"])
        self.assertGreater(len(receipt["stdout_tail"]), 8000)
        imported = subprocess.run(
            [*prefix, "obpi", "acceptance", OBPI, "review", "--receipt", receipt["run_id"]],
            cwd=fixture.root,
            env=environment,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            check=False,
            timeout=60,
        )
        self.assertEqual(imported.returncode, 0, imported.stdout + imported.stderr)
        history = load_history(fixture.root, OBPI)
        self.assertEqual(history.reviews[-1].receipt_id, receipt["run_id"])
        self.assertEqual(history.reviews[-1].findings[0].description, description)
        self.assertEqual(history.reviews[-1].verdict, "refuted")
