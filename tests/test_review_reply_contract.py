"""One reply envelope for Stage-2 reviewers (GHI #1095).

The composed prompt used to request a legacy ``ReviewResult`` AND a
``gzkit.acceptance.review.v1`` object. Both carry ``verdict`` and ``findings``
with different vocabularies and shapes, and reviewers merged them, crossed
their vocabularies or dropped a required field. The importer refused each one,
and every refusal cost a whole dispatch. The reply is now the acceptance object
alone; the orchestrator derives the legacy result from it.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from gzkit.acceptance import ReviewResponse
from gzkit.acceptance_store import acceptance_status, load_history, record_review
from gzkit.pipeline_dispatch import (
    DispatchTask,
    TaskComplexity,
    compose_quality_review_prompt,
    compose_spec_review_prompt,
    parse_review_result,
    review_blocks_advancement,
)
from gzkit.roles import ReviewVerdict
from tests import test_acceptance_store as store_tests
from tests.acceptance_fixtures import ACCEPTANCE_CONTEXT
from tests.test_acceptance_execution import REQ

_NO_PERSONA_ROOT = Path("/nonexistent-project-root")
_JSON_BLOCK = re.compile(r"```json\n(.*?)\n```", re.DOTALL)


def _prompts() -> dict[str, str]:
    task = DispatchTask(
        task_id=1,
        description="Implement the widget",
        allowed_paths=["src/gzkit/example.py"],
        complexity=TaskComplexity.SIMPLE,
        model="sonnet",
    )
    return {
        "spec": compose_spec_review_prompt(
            task,
            ["REQ-01: Reject invalid inputs."],
            ["src/gzkit/example.py"],
            why="reply-contract test",
            project_root=_NO_PERSONA_ROOT,
            acceptance_context=ACCEPTANCE_CONTEXT,
        ),
        "quality": compose_quality_review_prompt(
            ["src/gzkit/example.py"],
            ["tests/test_example.py"],
            why="reply-contract test",
            project_root=_NO_PERSONA_ROOT,
            acceptance_context=ACCEPTANCE_CONTEXT,
        ),
    }


def _envelope(**changes: object) -> dict:
    envelope = {
        "schema": "gzkit.acceptance.review.v1",
        "stage": "spec",
        "input_digest": "bytes-a",
        "obligation_ids": ["REQ-01"],
        "proof_ids": ["proof-a"],
        "accepted_proof_ids": ["proof-a"],
        "findings": [],
        "closures": [],
        "reviewer_id": "spec-reviewer-under-test",
        "verdict": "accepted",
    }
    envelope.update(changes)
    return envelope


class TestComposedPromptRequestsOneEnvelopeOutputContract(unittest.TestCase):
    """Prompt delivery: the reply contract the reviewer sees has one verdict vocabulary."""

    def test_every_verdict_bearing_example_is_the_importer_envelope(self) -> None:
        for stage, prompt in _prompts().items():
            with self.subTest(stage=stage):
                examples = [json.loads(block) for block in _JSON_BLOCK.findall(prompt)]
                verdicts = [obj for obj in examples if "verdict" in obj]
                self.assertTrue(verdicts, "the prompt must show the reply shape")
                for example in verdicts:
                    # The example must validate as the exact transport the importer reads.
                    ReviewResponse.model_validate(example)

    def test_the_prompt_states_the_closure_approval_rule_the_importer_enforces(self) -> None:
        # acceptance._closure_retains_subject refuses a closure whose proof the same
        # review did not approve; the prompt never said so (arb-step-specreview-06e58c19).
        for stage, prompt in _prompts().items():
            with self.subTest(stage=stage):
                self.assertIn("A closure's proof_id must also appear in accepted_proof_ids", prompt)


class TestLegacyResultDerivesFromTheEnvelope(unittest.TestCase):
    """The orchestrator's advancement decision reads the one envelope the reviewer wrote."""

    def _derive(self, **changes: object):
        output = "Review complete.\n\n```json\n" + json.dumps(_envelope(**changes)) + "\n```\n"
        result = parse_review_result(output)
        self.assertIsNotNone(result)
        return result

    def test_a_refuted_envelope_blocks_advancement(self) -> None:
        self.assertTrue(review_blocks_advancement(self._derive(verdict="refuted")))

    def test_a_mapped_finding_blocks_even_under_an_accepted_verdict(self) -> None:
        finding = {
            "id": "F1",
            "obligation_id": "REQ-01",
            "kind": "counterexample",
            "description": "Invalid input is accepted.",
        }
        self.assertTrue(review_blocks_advancement(self._derive(findings=[finding])))

    def test_an_auxiliary_observation_does_not_block(self) -> None:
        finding = {
            "id": "A1",
            "obligation_id": None,
            "kind": "counterexample",
            "description": "A helper name shadows a module function.",
        }
        result = self._derive(findings=[finding])
        self.assertFalse(review_blocks_advancement(result))
        self.assertEqual(len(result.findings), 1)

    def test_a_clean_accepted_envelope_passes(self) -> None:
        result = self._derive()
        self.assertEqual(result.verdict, ReviewVerdict.PASS)
        self.assertFalse(review_blocks_advancement(result))

    def test_verification_gaps_travel_to_the_derived_result(self) -> None:
        result = self._derive(verification_gaps=["No shell; could not run behave."])
        self.assertEqual(result.verification_gaps, ["No shell; could not run behave."])
        self.assertFalse(review_blocks_advancement(result))

    def test_the_envelope_outranks_a_stray_legacy_block(self) -> None:
        output = (
            '```json\n{"verdict": "PASS", "findings": [], "summary": "legacy"}\n```\n'
            "```json\n" + json.dumps(_envelope(verdict="refuted")) + "\n```\n"
        )
        self.assertTrue(review_blocks_advancement(parse_review_result(output)))


class TestVerificationGapsAreNonGoverning(unittest.TestCase):
    """A reviewer's own coverage limits import, and never approve or block (GHI #941)."""

    def setUp(self) -> None:
        self.fixture = store_tests.AcceptanceStoreTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.proof = self.fixture.synthetic_proof()

    def _receipt_with_gaps(self, stage: str) -> dict:
        receipt = self.fixture.receipt(self.proof, stage)
        payload = json.loads(receipt["stdout_tail"].removeprefix("```json\n").removesuffix("\n```"))
        payload["verification_gaps"] = ["No shell tool; could not execute the selector."]
        receipt["stdout_tail"] = json.dumps(payload)
        return receipt

    def test_an_envelope_carrying_gaps_imports_and_keeps_them(self) -> None:
        review = record_review(self.fixture.root, store_tests.OBPI, self._receipt_with_gaps("spec"))
        self.assertEqual(
            review.verification_gaps, ("No shell tool; could not execute the selector.",)
        )
        self.assertEqual(load_history(self.fixture.root, store_tests.OBPI).reviews[-1], review)

    def test_gaps_change_no_readiness_outcome(self) -> None:
        for stage in ("spec", "quality", "adversarial"):
            record_review(self.fixture.root, store_tests.OBPI, self._receipt_with_gaps(stage))
        self.assertTrue(acceptance_status(self.fixture.root, store_tests.OBPI).ready)

    def test_gaps_grant_no_approval(self) -> None:
        receipt = self._receipt_with_gaps("spec")
        payload = json.loads(receipt["stdout_tail"])
        payload["accepted_proof_ids"] = []
        receipt["stdout_tail"] = json.dumps(payload)
        review = record_review(self.fixture.root, store_tests.OBPI, receipt)
        self.assertEqual(review.accepted_proof_ids, ())
        blockers = acceptance_status(self.fixture.root, store_tests.OBPI).blockers
        self.assertTrue(any(REQ in b and "spec" in b for b in blockers), blockers)


if __name__ == "__main__":
    unittest.main()
