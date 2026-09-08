"""Acceptance exit codes cross the real process boundary (GHI #988).

Proof controls execute temporary production code and documented unittest tests.
Review receipts are explicitly synthetic transport fixtures; no agent judgment
is claimed by these process/ledger integration checks.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from gzkit.acceptance import Proof
from tests.test_acceptance_execution import REQ, SELECTOR, TEST, ExecutionFixture
from tests.test_acceptance_store import OBPI, captured_receipt


class TestAcceptanceProcessExit(ExecutionFixture):
    """The shell must see refusal and success from the same actual command path."""

    def setUp(self):
        super().setUp()
        self.write(".gzkit.json", json.dumps({"paths": {"design_root": "design"}}))
        self.brief = self.brief.rename(self.brief.with_name(f"{OBPI}.md"))
        self.write(
            "tests/test_engine.py",
            TEST.replace(
                "    def test_double(self):\n",
                '    def test_double(self):\n        """Two must double to four."""\n',
            ),
        )
        self.env = {
            **os.environ,
            "GZKIT_ARB_RECEIPTS_ROOT": str(self.root / "artifacts/receipts"),
        }
        self.controls = self.write(
            "controls.json",
            json.dumps(
                {
                    "req_id": REQ,
                    "source": "src/engine.py",
                    "selectors": [SELECTOR],
                    "mutations": [
                        {
                            "find": "return value * 2",
                            "replace": "return value * 3",
                            "label": "tripling violates doubling",
                            "expected_tests": [SELECTOR],
                        }
                    ],
                }
            ),
        )

    def cli(self, *arguments, console_script=False):
        """Invoke the installed entrypoint without replacing parser or handlers."""
        entrypoint = [sys.executable, "-m", "gzkit"]
        if console_script:
            executable = shutil.which("gz")
            if executable is None:
                self.fail("The installed gz console script is required")
            entrypoint = [executable]
        return subprocess.run(
            [
                "uv",
                "run",
                "--project",
                str(Path(__file__).resolve().parents[2]),
                "--no-sync",
                *entrypoint,
                "obpi",
                "acceptance",
                OBPI,
                *arguments,
            ],
            cwd=self.root,
            env=self.env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
            check=False,
        )

    def initialize(self):
        result = self.cli("init", "--author", "implementer-session")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["author_id"], "implementer-session")

    def prove(self):
        self.initialize()
        result = self.cli("prove", "--spec", str(self.controls))
        payload = json.loads(result.stdout)
        self.assertTrue(payload["valid"], result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(
            (self.root / "src/engine.py").read_text(encoding="utf-8"),
            "def double(value):\n    return value * 2\n",
        )
        return Proof.model_validate(payload)

    def import_review(self, proof, stage, **kwargs):
        """Import a labeled synthetic capture through the actual receipt resolver."""
        receipt = captured_receipt(proof, stage, **kwargs)
        self.write(f"artifacts/receipts/{receipt['run_id']}.json", json.dumps(receipt))
        result = self.cli("review", "--receipt", receipt["run_id"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["receipt_id"], receipt["run_id"])
        return json.loads(result.stdout)

    def test_blocked_readiness_exits_three_at_both_stages_and_entrypoints(self):
        self.initialize()
        for stage in ("stage2", "stage4"):
            for console_script in (False, True):
                with self.subTest(stage=stage, console_script=console_script):
                    result = self.cli(
                        "status", "--stage", stage, "--json", console_script=console_script
                    )
                    payload = json.loads(result.stdout)
                    self.assertFalse(payload["ready"])
                    self.assertTrue(payload["blockers"])
                    self.assertEqual(result.returncode, 3, result.stdout)

    def test_rejected_init_cannot_exit_success_or_change_recorded_author(self):
        self.initialize()
        before = (self.root / ".gzkit/ledger.jsonl").read_bytes()
        for args in (("init",), ("init", "--author", "replacement-author")):
            with self.subTest(args=args):
                result = self.cli(*args, "--json")
                self.assertIn("error", json.loads(result.stdout))
                self.assertEqual(result.returncode, 3, result.stdout)
                self.assertEqual((self.root / ".gzkit/ledger.jsonl").read_bytes(), before)

    def test_documented_semantic_proof_exits_zero_and_surviving_control_exits_three(self):
        self.prove()
        spec = json.loads(self.controls.read_text(encoding="utf-8"))
        spec["mutations"][0]["replace"] = "return 2 * value"
        self.controls.write_text(json.dumps(spec), encoding="utf-8")
        result = self.cli("prove", "--spec", str(self.controls))
        payload = json.loads(result.stdout)
        self.assertFalse(payload["valid"])
        self.assertEqual(result.returncode, 3, result.stdout)
        witness = json.loads(payload["evidence"])["sweep"]["witnesses"][0]
        self.assertEqual(witness["outcome"], "survived")

    def test_rejected_proof_request_exits_three(self):
        result = self.cli("prove", "--spec", str(self.controls), "--json")
        self.assertIn("error", json.loads(result.stdout))
        self.assertEqual(result.returncode, 3, result.stdout)

    def test_missing_and_malformed_receipts_exit_three_without_appending(self):
        self.initialize()
        before = (self.root / ".gzkit/ledger.jsonl").read_bytes()
        invalid = "arb-step-malformed-fixture"
        self.write(f"artifacts/receipts/{invalid}.json", json.dumps({"run_id": invalid}))
        for receipt in ("arb-step-does-not-exist", invalid):
            with self.subTest(receipt=receipt):
                result = self.cli("review", "--receipt", receipt, "--json")
                self.assertIn("error", json.loads(result.stdout))
                self.assertEqual(result.returncode, 3, result.stdout)
                self.assertEqual((self.root / ".gzkit/ledger.jsonl").read_bytes(), before)

    def test_successful_reviews_and_satisfied_readiness_exit_zero(self):
        proof = self.prove()
        for review_stage in ("spec", "quality", "adversarial"):
            self.import_review(proof, review_stage)
        for stage in ("stage2", "stage4"):
            with self.subTest(stage=stage):
                result = self.cli("status", "--stage", stage, "--json")
                self.assertTrue(json.loads(result.stdout)["ready"], result.stdout)
                self.assertEqual(result.returncode, 0, result.stdout)

    def test_recording_refutation_succeeds_while_readiness_stays_blocked(self):
        proof = self.prove()
        finding = {
            "id": "F-required-proof",
            "obligation_id": REQ,
            "kind": "missing-proof",
            "description": "Synthetic reviewer requests the required boundary case",
        }
        review = self.import_review(proof, "spec", verdict="refuted", findings=[finding])
        self.assertEqual(review["findings"][0]["id"], "F-required-proof")
        result = self.cli("status", "--stage", "stage4", "--json")
        self.assertEqual(json.loads(result.stdout)["open_findings"], ["F-required-proof"])
        self.assertEqual(result.returncode, 3, result.stdout)

    def test_human_review_refusal_and_success_reach_the_process_exit(self):
        proof = self.prove()
        for stage in ("spec", "quality"):
            self.import_review(proof, stage)
        result = self.cli("human-review", "--attestor", "g0", "--json")
        self.assertIn("error", json.loads(result.stdout))
        self.assertEqual(result.returncode, 3, result.stdout)
        result = self.cli(
            "human-review", "--attestor", "g0", "--ruling", "Synthetic test-only judgment."
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reviewer_id"], "human:g0")
