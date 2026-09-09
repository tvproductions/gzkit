"""The real response schema and captured context reach review ingestion together."""

import json
import unittest

from gzkit.acceptance_context import build_review_context
from gzkit.acceptance_execution import canonical_obligations, input_digest
from gzkit.acceptance_store import acceptance_status, load_history, record_proof, record_review
from gzkit.pipeline_dispatch import _acceptance_review_frame
from tests import test_acceptance_store as store_tests
from tests.test_acceptance_execution import REQ


class ReviewContextTests(unittest.TestCase):
    def setUp(self):
        self.fixture = store_tests.AcceptanceStoreTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.proof = self.fixture.synthetic_proof()

    def test_missing_context_fails_locally_before_review_dispatch(self):
        with self.assertRaisesRegex(ValueError, "context"):
            _acceptance_review_frame("spec", "")

    def test_changed_initialized_roster_refuses_dispatch_even_with_current_proof(self):
        """WP3 review finding: a known source contradiction is a local error."""
        f = self.fixture
        f.brief.write_text(
            f.brief.read_text(encoding="utf-8").replace(REQ, "REQ-0.1.0-01-02"),
            encoding="utf-8",
        )
        obligation = canonical_obligations(f.root, f.brief)[0]
        current = self.proof.model_copy(
            update={
                "id": "proof-new-roster",
                "obligation_id": obligation.id,
                "contract_digest": obligation.contract_digest,
                "input_digest": input_digest(f.root, f.brief),
            }
        )
        record_proof(f.root, store_tests.OBPI, current)
        with self.assertRaisesRegex(ValueError, "roster"):
            context = build_review_context(f.root, store_tests.OBPI, stage="stage2")
            _acceptance_review_frame("spec", context.model_dump_json())

    def test_context_example_uses_current_identity_and_real_closure_schema(self):
        context = build_review_context(self.fixture.root, store_tests.OBPI, stage="stage2")
        frame = "\n".join(_acceptance_review_frame("spec", context.model_dump_json()))
        blocks = frame.split("```json\n")[1:]
        objects = [json.loads(block.split("\n```", 1)[0]) for block in blocks]
        response = next(obj for obj in objects if obj.get("schema") == "gzkit.acceptance.review.v1")
        self.assertEqual(response["input_digest"], self.proof.input_digest)
        self.assertEqual(response["proof_ids"], [self.proof.id])
        self.assertEqual(response["accepted_proof_ids"], [])
        closure = next(obj for obj in objects if "finding_id" in obj)
        self.assertEqual(set(closure), {"finding_id", "obligation_id", "proof_id"})

    def test_generated_subject_and_nonempty_closure_cross_captured_receipt_importer(self):
        """WP3: transport is synthetic; the real store and readiness consumer run."""
        finding = {
            "id": "F-oracle",
            "obligation_id": REQ,
            "kind": "missing-proof",
            "description": "The independent literal boundary has not been reviewed.",
        }
        record_review(
            self.fixture.root,
            store_tests.OBPI,
            self.fixture.receipt(self.proof, findings=[finding], verdict="refuted"),
        )
        context = build_review_context(self.fixture.root, store_tests.OBPI, stage="stage2")
        frame = "\n".join(_acceptance_review_frame("spec", context.model_dump_json()))
        objects = [json.loads(block.split("\n```", 1)[0]) for block in frame.split("```json\n")[1:]]
        response = next(obj for obj in objects if obj.get("schema") == "gzkit.acceptance.review.v1")
        closure = next(obj for obj in objects if "finding_id" in obj)
        self.assertEqual(closure["finding_id"], finding["id"])
        # Simulated reviewer judgment, never a controller default or real agent claim.
        response.update(accepted_proof_ids=[self.proof.id], closures=[closure], verdict="accepted")
        receipt = self.fixture.receipt(self.proof, "spec")
        receipt["stdout_tail"] = (
            json.dumps({"verdict": "PASS", "findings": [], "summary": "Synthetic legacy response"})
            + "\n"
            + json.dumps(response)
        )
        review = record_review(self.fixture.root, store_tests.OBPI, receipt)
        self.assertEqual(review.closures[0].finding_id, finding["id"])
        self.assertFalse(acceptance_status(self.fixture.root, store_tests.OBPI).ready)
        for stage in ("quality", "adversarial"):
            record_review(
                self.fixture.root, store_tests.OBPI, self.fixture.receipt(self.proof, stage)
            )
        self.assertTrue(acceptance_status(self.fixture.root, store_tests.OBPI).ready)

    def test_malformed_or_mismapped_responses_cannot_gain_credit(self):
        for changes in (
            {"verification_gaps": []},
            {"obligation_ids": ["unknown"]},
            {"proof_ids": ["unknown"], "accepted_proof_ids": ["unknown"]},
            {
                "closures": [
                    {"finding_id": "unknown", "obligation_id": REQ, "proof_id": self.proof.id}
                ]
            },
            {
                "closures": [
                    {
                        "finding_id": "unknown",
                        "obligation_id": REQ,
                        "proof_id": self.proof.id,
                        "description": "wrong field",
                    }
                ]
            },
        ):
            with self.subTest(changes=changes):
                receipt = self.fixture.receipt(self.proof)
                payload = json.loads(
                    receipt["stdout_tail"].removeprefix("```json\n").removesuffix("\n```")
                )
                receipt["stdout_tail"] = json.dumps({**payload, **changes})
                with self.assertRaises(ValueError):
                    record_review(self.fixture.root, store_tests.OBPI, receipt)
                self.assertEqual(load_history(self.fixture.root, store_tests.OBPI).reviews, [])

    def test_format_only_recapture_preserves_original_refutation_and_subject(self):
        """WP3: synthetic fresh transport repairs shape, never substantive judgment."""
        f = self.fixture
        f.accept(self.proof)
        self.assertTrue(acceptance_status(f.root, store_tests.OBPI).ready)
        source = f.root / "src/engine.py"
        before_source = source.read_bytes()
        original = f.receipt(
            self.proof,
            verdict="refuted",
            findings=[
                {
                    "id": "F-required-oracle",
                    "obligation_id": REQ,
                    "kind": "missing-proof",
                    "description": "The expected value uses the same helper as production.",
                }
            ],
        )
        judgment = json.loads(original["stdout_tail"].split("```json\n")[1].split("\n```")[0])
        original["stdout_tail"] = json.dumps({**judgment, "verification_gaps": []})
        original_path = f.write(
            f"artifacts/receipts/{original['run_id']}.json", json.dumps(original)
        )
        original_bytes = original_path.read_bytes()
        with self.assertRaises(ValueError):
            record_review(f.root, store_tests.OBPI, original)

        # This is a separate disclosed transport fixture, not an edit to its receipt.
        corrected = f.receipt(self.proof)
        corrected["step"]["command"].append(
            f"Formatting-only recapture of {original['run_id']}; preserve the reviewed judgment."
        )
        corrected["stdout_tail"] = (
            json.dumps({"verdict": "FAIL", "verification_gaps": [], "findings": []})
            + "\n"
            + json.dumps(judgment)
        )
        f.write(f"artifacts/receipts/{corrected['run_id']}.json", json.dumps(corrected))
        observed = record_review(f.root, store_tests.OBPI, corrected)
        retained = load_history(f.root, store_tests.OBPI).reviews[-1]
        self.assertEqual(retained, observed)
        self.assertEqual(retained.receipt_id, corrected["run_id"])
        self.assertNotEqual(retained.receipt_id, original["run_id"])
        self.assertIn(original["run_id"], corrected["step"]["command"][-1])
        for name, value in judgment.items():
            if name != "schema":
                self.assertEqual(retained.model_dump(mode="json")[name], value)
        status = acceptance_status(f.root, store_tests.OBPI)
        self.assertFalse(status.ready)
        self.assertEqual(status.open_findings, ("F-required-oracle",))
        self.assertEqual(original_path.read_bytes(), original_bytes)
        self.assertEqual(source.read_bytes(), before_source)
        self.assertEqual(load_history(f.root, store_tests.OBPI).proofs, [self.proof])

    def test_contradictory_context_is_rejected_before_dispatch(self):
        context = build_review_context(
            self.fixture.root, store_tests.OBPI, stage="stage2"
        ).model_dump(mode="json")
        for changes in (
            {"input_digest": "wrong-subject"},
            {"obligation_ids": ["unknown"]},
            {"proofs": []},
        ):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                _acceptance_review_frame("spec", json.dumps({**context, **changes}))
