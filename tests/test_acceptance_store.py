"""Durable acceptance proof and closure survive review-history edits."""

import json
import unittest
import uuid
from unittest.mock import patch

from gzkit.acceptance import Proof
from gzkit.acceptance_execution import (
    canonical_obligations,
    execution_conditions_digest,
    input_digest,
)
from gzkit.acceptance_store import (
    REVIEW_SCHEMA,
    acceptance_ledger,
    acceptance_status,
    completion_review,
    initialize,
    load_history,
    record_human_review,
    record_proof,
    record_review,
    review_from_receipt,
)
from gzkit.events import parse_typed_event
from tests.test_acceptance_execution import BRIEF, REQ, ExecutionFixture

OBPI = "OBPI-0.1.0-01-engine"


def captured_receipt(proof, stage="adversarial", *, findings=(), closures=(), verdict="accepted"):
    """Fixture models captured transport output; semantic runs are real."""
    review = {
        "schema": REVIEW_SCHEMA,
        "stage": stage,
        "input_digest": proof.input_digest,
        "obligation_ids": [REQ],
        "proof_ids": [proof.id],
        "accepted_proof_ids": [proof.id] if verdict == "accepted" else [],
        "findings": list(findings),
        "closures": list(closures),
        "reviewer_id": "independent-session",
        "verdict": verdict,
    }
    return {
        "schema": "gzkit.arb.step_receipt.v1",
        "exit_status": 0,
        "run_id": f"arb-step-review-{uuid.uuid4().hex}",
        "step": {"command": ["node", "codex-companion.mjs", "adversarial-review"]},
        "stdout_tail": "```json\n" + json.dumps(review) + "\n```",
        "stderr_tail": "",
    }


class AcceptanceStoreTests(ExecutionFixture):
    def setUp(self):
        super().setUp()
        self.write(".gzkit.json", json.dumps({"paths": {"design_root": "design"}}))
        self.brief = self.brief.rename(self.brief.with_name(f"{OBPI}.md"))
        initialize(self.root, OBPI, "implementer-session")

    def receipt(self, proof, stage="adversarial", *, findings=(), closures=(), verdict="accepted"):
        return captured_receipt(proof, stage, findings=findings, closures=closures, verdict=verdict)

    def prove_and_record(self):
        proof = self.run_proof()
        self.assertTrue(proof.valid, proof.evidence)
        record_proof(self.root, OBPI, proof)
        return proof

    def accept(self, proof):
        for stage in ("spec", "quality", "adversarial"):
            record_review(self.root, OBPI, self.receipt(proof, stage))

    def test_windows_interpreter_receipt_imports_the_captured_review(self):
        """The importer consumes the same executed wrapper argv Windows emits."""
        proof = self.synthetic_proof()
        receipt = self.receipt(proof, "spec")
        receipt["step"]["command"] = [
            r"C:\project\.venv\Scripts\python.exe",
            r"C:\fixture\codex-fixture.py",
        ]
        review = review_from_receipt(receipt)
        self.assertEqual(review.receipt_id, receipt["run_id"])
        self.assertEqual(review.accepted_proof_ids, (proof.id,))
        self.assertEqual(review.tier, 1)

    def synthetic_proof(self):
        """Isolate persistence from execution, which has separate process controls."""
        obligation = canonical_obligations(self.root, self.brief)[0]
        proof = Proof(
            id=f"proof-{uuid.uuid4().hex}",
            obligation_id=REQ,
            contract_digest=obligation.contract_digest,
            input_digest=input_digest(self.root, self.brief),
            selectors=("tests.test_engine.Case.test_double",),
            evidence='{"fixture":"synthetic executed proof for store tests"}',
            valid=True,
        )
        record_proof(self.root, OBPI, proof)
        return proof

    def test_delayed_mapped_finding_is_retained_without_current_approval(self):
        """AS-1: a historical observation survives a real subject change and reload."""
        old = self.synthetic_proof()
        self.write("src/engine.py", "def double(value):\n    return value + value\n")
        current = self.synthetic_proof()
        finding = {
            "id": "delayed-boundary",
            "obligation_id": REQ,
            "kind": "missing-proof",
            "description": "The required negative input boundary was never exercised.",
        }
        observed = record_review(self.root, OBPI, self.receipt(old, findings=[finding]))
        history = load_history(self.root, OBPI)
        self.assertEqual(history.reviews, [observed])
        self.assertEqual(history.reviews[0].input_digest, old.input_digest)
        status = acceptance_status(self.root, OBPI)
        self.assertFalse(status.ready)
        self.assertEqual(status.open_findings, (finding["id"],))
        self.assertTrue(any(current.id in blocker for blocker in status.blockers))

    def test_repeated_historical_finding_preserves_newer_independent_closure(self):
        """AS-2/AS-3: repetition is history; a current counterexample still blocks."""
        old = self.synthetic_proof()
        finding = {
            "id": "F-repair",
            "obligation_id": REQ,
            "kind": "counterexample",
            "description": "Negative inputs violate the required result.",
        }
        record_review(self.root, OBPI, self.receipt(old, findings=[finding], verdict="refuted"))
        self.write("src/engine.py", "def double(value):\n    return value + value\n")
        current = self.synthetic_proof()
        self.accept(current)
        closure = {"finding_id": finding["id"], "obligation_id": REQ, "proof_id": current.id}
        record_review(self.root, OBPI, self.receipt(current, closures=[closure]))
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        record_review(self.root, OBPI, self.receipt(old, findings=[finding], verdict="refuted"))
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        self.assertEqual(load_history(self.root, OBPI).reviews[-1].findings[0].id, finding["id"])
        record_review(self.root, OBPI, self.receipt(current, findings=[finding], verdict="refuted"))
        self.assertEqual(acceptance_status(self.root, OBPI).open_findings, (finding["id"],))

    def test_scoped_reviews_preserve_complete_completion_provenance(self):
        """AS-6: no single intersecting review represents two required approvals."""
        from gzkit.commands.obpi_complete import _current_adversarial_event

        # A second obligation is canon before initialization in this independent fixture.
        other = "REQ-0.1.0-01-02"
        self.brief.write_text(
            BRIEF.replace(
                "reqs:\n- " + REQ,
                "reqs:\n- " + other + "\n- " + REQ,
            ).replace(
                "## Evidence", f"- [ ] {other} [BEHAVIOR]: Double three to six.\n## Evidence"
            ),
            encoding="utf-8",
        )
        # Existing initialization is deliberately replaced only in a new empty temp ledger.
        self.write(
            ".gzkit.json",
            json.dumps(
                {
                    "paths": {
                        "design_root": "design",
                        "ledger": ".gzkit/scoped-ledger.jsonl",
                    }
                }
            ),
        )
        initialize(self.root, OBPI, "implementer-session")
        first = self.synthetic_proof()
        second = first.model_copy(update={"id": "second-proof", "obligation_id": other})
        record_proof(self.root, OBPI, second)
        self.accept(first)
        self.assertFalse(acceptance_status(self.root, OBPI).ready)
        expected = [review.id for review in load_history(self.root, OBPI).reviews]
        for stage in ("spec", "quality", "adversarial"):
            receipt = self.receipt(second, stage)
            payload = json.loads(
                receipt["stdout_tail"].removeprefix("```json\n").removesuffix("\n```")
            )
            payload["obligation_ids"] = [other]
            if stage == "adversarial":
                receipt["step"]["command"] = ["claude", "-p", "review"]
                payload["fallback_reason"] = "Synthetic unavailable cross-vendor transport"
            receipt["stdout_tail"] = json.dumps(payload)
            expected.append(record_review(self.root, OBPI, receipt).id)
        status = acceptance_status(self.root, OBPI)
        self.assertTrue(status.ready, status.blockers)
        event = _current_adversarial_event(self.root, OBPI, False, None, None, None)
        self.assertEqual(set(event.extra["acceptance_review_ids"]), set(expected))
        self.assertEqual(event.extra["adversary_tier"], 2)
        parse_typed_event(event.model_dump())

    def test_declared_conditions_are_checked_at_the_readiness_consumer(self):
        """AS-5: an unrelated shell variable stays irrelevant to approval."""
        with patch.dict("os.environ", {"ENGINE_MODE": "required"}):
            original = self.synthetic_proof()
            proof = original.model_copy(
                update={
                    "id": "conditioned-proof",
                    "environment_keys": ("ENGINE_MODE",),
                    "conditions_digest": execution_conditions_digest(("ENGINE_MODE",)),
                }
            )
            record_proof(self.root, OBPI, proof)
            self.accept(proof)
            with patch.dict("os.environ", {"COLUMNS": "999"}):
                self.assertTrue(acceptance_status(self.root, OBPI).ready)
            with patch.dict("os.environ", {"ENGINE_MODE": "changed"}):
                status = acceptance_status(self.root, OBPI)
                self.assertFalse(status.ready)
                self.assertTrue(
                    any("declared execution conditions" in item for item in status.blockers)
                )

    def test_future_equivalent_proof_cannot_erase_a_recorded_current_counterexample(self):
        """AS-3 review finding: replay must preserve observation-time meaning."""
        original = self.synthetic_proof()
        proof = original.model_copy(update={"id": "explicit-claim", "claim_digest": "same-claim"})
        record_proof(self.root, OBPI, proof)
        finding = {
            "id": "F-current",
            "obligation_id": REQ,
            "kind": "counterexample",
            "description": "A required boundary still violates the contract.",
        }
        record_review(self.root, OBPI, self.receipt(proof, findings=[finding], verdict="refuted"))
        self.accept(proof)
        closure = {"finding_id": finding["id"], "obligation_id": REQ, "proof_id": proof.id}
        record_review(self.root, OBPI, self.receipt(proof, closures=[closure]))
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        record_review(self.root, OBPI, self.receipt(proof, findings=[finding], verdict="refuted"))
        self.assertEqual(acceptance_status(self.root, OBPI).open_findings, (finding["id"],))
        repeated = proof.model_copy(update={"id": "later-equivalent-execution"})
        record_proof(self.root, OBPI, repeated)
        status = acceptance_status(self.root, OBPI)
        self.assertFalse(status.ready)
        self.assertEqual(status.open_findings, (finding["id"],))

    def test_actual_semantic_proof_and_independent_reviews_reach_readiness(self):
        proof = self.prove_and_record()
        self.assertFalse(acceptance_status(self.root, OBPI).ready)
        self.accept(proof)
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        self.assertEqual(completion_review(self.root, OBPI).proof_ids, (proof.id,))
        for event in acceptance_ledger(self.root).read_all():
            parse_typed_event(event.model_dump())

    def test_history_edits_preserve_closure_but_changed_production_invalidates(self):
        proof = self.prove_and_record()
        self.accept(proof)
        self.brief.write_text(
            BRIEF.replace("Historical round one was wrong.", "Refuted round 14."), encoding="utf-8"
        )
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        self.write("src/engine.py", "def double(value):\n    return value * 3\n")
        status = acceptance_status(self.root, OBPI)
        self.assertFalse(status.ready)
        self.assertTrue(any("stale inputs" in blocker for blocker in status.blockers))

    def test_stale_review_refusal_stops_blaming_file_contents(self):
        """The refusal names what it can establish, and nothing more (GHI #989).

        A review record carries only the composite digest, so WHICH term moved is
        not derivable at the refusal site. The message must therefore stop
        asserting "stale file contents" -- it was said whichever term differed,
        and sent readers hunting a file change that need not exist. It names both
        composing terms and prints the digests instead. Both branches below are
        genuinely stale for different reasons and get the same honest message.
        """
        proof = self.prove_and_record()
        receipt = self.receipt(proof)
        payload = json.loads(receipt["stdout_tail"].removeprefix("```json\n").removesuffix("\n```"))
        payload["input_digest"] = "unrecognized-subject"
        receipt["stdout_tail"] = json.dumps(payload)

        self.write("src/engine.py", "def double(value):\n    return value * 7\n")
        with self.assertRaises(ValueError) as ctx:
            record_review(self.root, OBPI, receipt)
        roster_message = str(ctx.exception)

        self.write("src/engine.py", "def double(value):\n    return value * 2\n")
        self.brief.write_text(
            BRIEF.replace("Double two to four.", "Triple two to six."), encoding="utf-8"
        )
        with self.assertRaises(ValueError) as ctx:
            record_review(self.root, OBPI, receipt)
        contract_message = str(ctx.exception)

        for message in (roster_message, contract_message):
            self.assertNotIn("stale file contents", message)
            self.assertIn("superseded acceptance inputs", message)
            self.assertIn("files roster", message)
            self.assertIn("contract", message)
            self.assertIn("unrecognized", message)

    def test_findings_survive_auxiliary_deletion_and_require_explicit_closure(self):
        proof = self.prove_and_record()
        finding = {
            "id": "F-boundary",
            "obligation_id": REQ,
            "kind": "missing-proof",
            "description": "Required boundary expectation was production-derived",
        }
        record_review(self.root, OBPI, self.receipt(proof, findings=[finding], verdict="refuted"))
        self.write(".gzkit/evidence/optional-audit.txt", "wrong historical count")
        (self.root / ".gzkit/evidence/optional-audit.txt").unlink()
        self.accept(proof)
        self.assertEqual(acceptance_status(self.root, OBPI).open_findings, ("F-boundary",))
        closure = {"finding_id": "F-boundary", "obligation_id": REQ, "proof_id": proof.id}
        record_review(self.root, OBPI, self.receipt(proof, closures=[closure]))
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        self.assertEqual(len(load_history(self.root, OBPI).reviews), 5)

    def test_auxiliary_observation_is_retained_without_creating_an_obligation(self):
        proof = self.prove_and_record()
        self.accept(proof)
        finding = {
            "id": "history-typo",
            "obligation_id": None,
            "kind": "counterexample",
            "description": "Optional historical count is wrong",
        }
        record_review(self.root, OBPI, self.receipt(proof, findings=[finding]))
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        self.assertEqual(load_history(self.root, OBPI).reviews[-1].findings[0].id, "history-typo")

    def test_bad_closure_rejected_before_immutable_append(self):
        proof = self.prove_and_record()
        count = len(acceptance_ledger(self.root).read_all())
        bad = {"finding_id": "never-recorded", "obligation_id": REQ, "proof_id": proof.id}
        with self.assertRaisesRegex(ValueError, "original finding"):
            record_review(self.root, OBPI, self.receipt(proof, closures=[bad]))
        self.assertEqual(len(acceptance_ledger(self.root).read_all()), count)
        self.accept(proof)
        self.assertTrue(acceptance_status(self.root, OBPI).ready)

    def test_missing_or_substituted_review_output_does_not_become_evidence(self):
        proof = self.prove_and_record()
        receipt = self.receipt(proof)
        for change in (
            {"exit_status": 1},
            {"stdout_tail": "PASS"},
            {"step": {"command": ["cat", "agent-authored.json"]}},
            {"stdout_tail": receipt["stdout_tail"] * 2},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                review_from_receipt({**receipt, **change})

    def test_reinitialization_cannot_erase_prior_history(self):
        proof = self.prove_and_record()
        self.accept(proof)
        initialize(self.root, OBPI, "implementer-session")
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        with self.assertRaisesRegex(ValueError, "already initialized"):
            initialize(self.root, OBPI, "different-author")
        self.assertEqual(len(load_history(self.root, OBPI).reviews), 3)

    def test_completion_receipt_stays_bound_to_current_proof_after_historical_review(self):
        old = self.prove_and_record()
        current = self.prove_and_record()
        self.assertEqual(old.input_digest, current.input_digest)
        self.accept(current)
        selected = completion_review(self.root, OBPI)
        self.assertEqual(selected.proof_ids, (current.id,))
        historical = record_review(self.root, OBPI, self.receipt(old))
        self.assertEqual(historical.proof_ids, (old.id,))
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        self.assertEqual(completion_review(self.root, OBPI).id, selected.id)

    def test_claude_tier_two_requires_unavailability_reason_and_retains_it(self):
        proof = self.prove_and_record()
        for stage in ("spec", "quality"):
            record_review(self.root, OBPI, self.receipt(proof, stage))
        receipt = self.receipt(proof)
        receipt["step"]["command"] = ["claude", "-p", "independent acceptance review"]
        with self.assertRaisesRegex(ValueError, "cross-vendor unavailability"):
            record_review(self.root, OBPI, receipt)
        self.assertFalse(acceptance_status(self.root, OBPI).ready)
        payload = json.loads(receipt["stdout_tail"].removeprefix("```json\n").removesuffix("\n```"))
        reason = "Synthetic transport fixture: codex setup returned ready=false, executable absent"
        payload["fallback_reason"] = reason
        receipt["stdout_tail"] = json.dumps(payload)
        review = record_review(self.root, OBPI, receipt)
        self.assertEqual(review.tier, 2)
        self.assertEqual(review.fallback_reason, reason)
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        self.assertEqual(load_history(self.root, OBPI).reviews[-1], review)

    def test_explicit_human_review_preserves_ruling_without_recording_attestation(self):
        proof = self.prove_and_record()
        for stage in ("spec", "quality"):
            record_review(self.root, OBPI, self.receipt(proof, stage))
        with self.assertRaisesRegex(ValueError, "verbatim ruling"):
            record_human_review(self.root, OBPI, attestor="g0", ruling="")
        self.assertFalse(acceptance_status(self.root, OBPI).ready)
        ruling = "I reviewed this proof and accept the required behavior."
        review = record_human_review(self.root, OBPI, attestor="g0", ruling=ruling)
        self.assertEqual(
            (review.tier, review.reviewer_id, review.fallback_reason), (3, "human:g0", ruling)
        )
        self.assertTrue(acceptance_status(self.root, OBPI).ready)
        events = acceptance_ledger(self.root).read_all()
        self.assertEqual(events[-1].extra["record_type"], "human-review")
        self.assertEqual(events[-1].extra["payload"]["ruling"], ruling)
        self.assertEqual({event.event for event in events}, {"acceptance_recorded"})
        self.assertEqual(load_history(self.root, OBPI).reviews[-1], review)

    def test_missing_proof_can_be_recorded_before_first_execution_and_survives_new_proof(self):
        finding = {
            "id": "F-initial-proof",
            "obligation_id": REQ,
            "kind": "missing-proof",
            "description": "No test execution demonstrates the required result",
        }
        payload = {
            "schema": REVIEW_SCHEMA,
            "stage": "spec",
            "input_digest": input_digest(self.root, self.brief),
            "obligation_ids": [REQ],
            "proof_ids": [],
            "accepted_proof_ids": [],
            "findings": [finding],
            "closures": [],
            "reviewer_id": "independent-session",
            "verdict": "refuted",
        }
        # Synthetic capture of an initial review with no proof to cite.
        receipt = {
            "schema": "gzkit.arb.step_receipt.v1",
            "exit_status": 0,
            "run_id": f"arb-step-review-{uuid.uuid4().hex}",
            "step": {"command": ["node", "codex-companion.mjs", "review"]},
            "stdout_tail": json.dumps(payload),
            "stderr_tail": "",
        }
        record_review(self.root, OBPI, receipt)
        history = load_history(self.root, OBPI)
        self.assertEqual(history.proofs, [])
        self.assertEqual(history.reviews[0].proof_ids, ())
        self.assertEqual(acceptance_status(self.root, OBPI).open_findings, ("F-initial-proof",))
        proof = self.prove_and_record()
        self.accept(proof)
        self.assertFalse(acceptance_status(self.root, OBPI).ready)
        closure = {"finding_id": "F-initial-proof", "obligation_id": REQ, "proof_id": proof.id}
        record_review(self.root, OBPI, self.receipt(proof, closures=[closure]))
        self.assertTrue(acceptance_status(self.root, OBPI).ready)


if __name__ == "__main__":
    unittest.main()
