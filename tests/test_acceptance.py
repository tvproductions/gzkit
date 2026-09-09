"""Acceptance preserves contract obligations through independent repair review."""

import unittest

from gzkit.acceptance import (
    Closure,
    Finding,
    Obligation,
    Proof,
    Review,
    assess_readiness,
    validate_review_record,
)


class TestAcceptance(unittest.TestCase):
    """Exercise readiness transitions, including legitimate successful completion."""

    def setUp(self) -> None:
        self.obligation = Obligation(
            id="REQ-02",
            kind="BEHAVIOR",
            statement="Persist exact contract-derived section boundaries.",
            authority="brief.md#REQ-02",
            contract_digest="contract-a",
        )
        self.proof = Proof(
            id="proof-a",
            obligation_id="REQ-02",
            contract_digest="contract-a",
            input_digest="bytes-a",
            selectors=("tests.test_lineage.TestPersist.test_literal_offsets",),
            evidence='{"baseline":"passed","control":"assertion-failure"}',
            valid=True,
        )

    def review(self, stage: str, **changes: object) -> Review:
        values: dict[str, object] = {
            "id": f"review-{stage}",
            "stage": stage,
            "input_digest": "bytes-a",
            "obligation_ids": ("REQ-02",),
            "proof_ids": ("proof-a",),
            "accepted_proof_ids": ("proof-a",),
            "receipt_id": f"receipt-{stage}",
            "reviewer_id": "independent-reviewer",
        }
        values.update(changes)
        return Review.model_validate(values)

    def assess(self, *, proofs=None, reviews=None, **changes):
        return assess_readiness(
            (self.obligation,),
            (self.proof,) if proofs is None else proofs,
            tuple(self.review(stage) for stage in ("spec", "quality", "adversarial"))
            if reviews is None
            else reviews,
            input_digest=changes.pop("input_digest", "bytes-a"),
            author_id="implementer",
            **changes,
        )

    def test_clean_independently_reviewed_proof_reaches_readiness(self) -> None:
        result = self.assess()
        self.assertTrue(result.ready, result.blockers)
        self.assertEqual(result.open_findings, ())

    def test_stage2_requires_spec_and_quality_but_not_adversarial(self) -> None:
        reviews = (self.review("spec"), self.review("quality"))
        self.assertTrue(self.assess(reviews=reviews, stage="stage2").ready)
        self.assertFalse(self.assess(reviews=reviews).ready)

    def test_hollow_test_without_valid_execution_blocks(self) -> None:
        for changes in ({"valid": False}, {"evidence": ""}, {"selectors": ()}):
            with self.subTest(changes=changes):
                proof = self.proof.model_copy(update=changes)
                self.assertFalse(self.assess(proofs=(proof,)).ready)

    def test_missing_proof_blocks_even_with_pass_reviews(self) -> None:
        self.assertFalse(self.assess(proofs=()).ready)

    def test_changed_bytes_invalidate_proof_and_review(self) -> None:
        self.assertFalse(self.assess(input_digest="bytes-b").ready)

    def test_contract_mismatch_blocks_current_proof(self) -> None:
        proof = self.proof.model_copy(update={"contract_digest": "other-contract"})
        self.assertFalse(self.assess(proofs=(proof,)).ready)

    def test_unrelated_proof_or_obligation_in_review_blocks(self) -> None:
        for changes in ({"proof_ids": ("unknown",)}, {"obligation_ids": ("unknown",)}):
            with self.subTest(changes=changes):
                reviews = (self.review("spec", **changes), self.review("quality"))
                self.assertFalse(self.assess(reviews=reviews, stage="stage2").ready)

    def test_implementer_cannot_supply_independent_review(self) -> None:
        reviews = (
            self.review("spec", reviewer_id="implementer"),
            self.review("quality"),
        )
        self.assertFalse(self.assess(reviews=reviews, stage="stage2").ready)

    def test_refuted_review_without_findings_does_not_grant_approval(self) -> None:
        reviews = (
            self.review("spec", verdict="refuted", accepted_proof_ids=()),
            self.review("quality"),
        )
        self.assertFalse(self.assess(reviews=reviews, stage="stage2").ready)

    def finding_review(self) -> Review:
        return self.review(
            "spec",
            verdict="refuted",
            findings=(
                Finding(
                    id="F7",
                    obligation_id="REQ-02",
                    kind="missing-proof",
                    description="Both expected and actual spans derive from production output.",
                ),
            ),
        )

    def test_later_pass_cannot_erase_unclosed_finding(self) -> None:
        reviews = (
            self.finding_review(),
            self.review("spec", id="spec-repair", receipt_id="receipt-repair"),
            self.review("quality"),
            self.review("adversarial"),
        )
        result = self.assess(reviews=reviews)
        self.assertFalse(result.ready)
        self.assertEqual(result.open_findings, ("F7",))

    def test_auxiliary_observation_does_not_create_acceptance_obligation(self) -> None:
        observation = Finding(
            id="N1", kind="counterexample", description="Historical audit sentence is inaccurate."
        )
        reviews = (
            self.review("spec", findings=(observation,)),
            self.review("quality"),
            self.review("adversarial"),
        )
        self.assertTrue(self.assess(reviews=reviews).ready)

    def test_removing_auxiliary_audit_preserves_mapped_finding(self) -> None:
        reviews = (
            self.finding_review(),
            self.review("spec", id="without-audit", receipt_id="receipt-without-audit"),
            self.review("quality"),
            self.review("adversarial"),
        )
        self.assertEqual(self.assess(reviews=reviews).open_findings, ("F7",))

    def closure_reviews(self, **closure_changes):
        values = {"finding_id": "F7", "obligation_id": "REQ-02", "proof_id": "proof-a"}
        values.update(closure_changes)
        return (
            self.finding_review(),
            self.review("spec", id="spec-repair", receipt_id="receipt-repair"),
            self.review("quality"),
            self.review("adversarial", closures=(Closure(**values),)),
        )

    def test_independent_closure_reaches_readiness_preserving_old_refutation(self) -> None:
        reviews = self.closure_reviews()
        self.assertTrue(self.assess(reviews=reviews).ready)
        self.assertEqual(reviews[0].verdict, "refuted")

    def test_unknown_or_mismatched_closure_is_rejected(self) -> None:
        for changes in (
            {"finding_id": "other-finding"},
            {"obligation_id": "other-obligation"},
            {"proof_id": "other-proof"},
        ):
            with self.subTest(changes=changes):
                self.assertFalse(self.assess(reviews=self.closure_reviews(**changes)).ready)

    def test_closure_cannot_precede_original_finding(self) -> None:
        reviews = self.closure_reviews()
        self.assertFalse(self.assess(reviews=tuple(reversed(reviews))).ready)

    def test_replacing_proof_invalidates_old_review_and_closure(self) -> None:
        replacement = self.proof.model_copy(update={"id": "proof-b"})
        result = self.assess(proofs=(self.proof, replacement), reviews=self.closure_reviews())
        self.assertFalse(result.ready)
        self.assertEqual(result.open_findings, ("F7",))

    def test_equivalent_successful_execution_preserves_approval_and_closure(self) -> None:
        """AS-4: execution occurrence is distinct from an explicitly witnessed claim."""
        original = self.proof.model_copy(update={"claim_digest": "witnessed-claim"})
        repeated = original.model_copy(update={"id": "proof-b"})
        result = self.assess(proofs=(original, repeated), reviews=self.closure_reviews())
        self.assertTrue(result.ready, result.blockers)
        self.assertEqual(result.open_findings, ())
        historical = self.finding_review().model_copy(
            update={
                "id": "delayed-repeat",
                "receipt_id": "receipt-delayed-repeat",
                "recorded_current_ids": ("proof-b",),
            }
        )
        self.assertTrue(
            self.assess(
                proofs=(original, repeated), reviews=(*self.closure_reviews(), historical)
            ).ready
        )

    def test_changed_claim_or_failed_execution_cannot_reuse_prior_approval(self) -> None:
        """AS-5: equal artifact bytes alone never establish proof equivalence."""
        original = self.proof.model_copy(update={"claim_digest": "claim-a"})
        for changes in (
            {"claim_digest": "different-specification-or-result"},
            {"selectors": ("tests.other.Case.test_other",)},
            {"contract_digest": "different-contract"},
            {"input_digest": "different-artifact"},
            {"valid": False},
            {"claim_digest": None},
        ):
            with self.subTest(changes=changes):
                new = original.model_copy(update={"id": "proof-b", **changes})
                self.assertFalse(self.assess(proofs=(original, new)).ready)
        failed = original.model_copy(update={"id": "contradiction", "valid": False})
        repeated = original.model_copy(update={"id": "later-success"})
        self.assertFalse(self.assess(proofs=(original, failed, repeated)).ready)

    def test_new_proof_and_independent_repair_closure_reach_readiness(self) -> None:
        replacement = self.proof.model_copy(update={"id": "proof-b", "input_digest": "bytes-b"})
        reviewed = [self.finding_review()]
        for stage in ("spec", "quality", "adversarial"):
            changes = {
                "id": f"new-{stage}",
                "receipt_id": f"new-receipt-{stage}",
                "input_digest": "bytes-b",
                "proof_ids": ("proof-b",),
                "accepted_proof_ids": ("proof-b",),
            }
            if stage == "adversarial":
                changes["closures"] = (
                    Closure(finding_id="F7", obligation_id="REQ-02", proof_id="proof-b"),
                )
            reviewed.append(self.review(stage, **changes))
        result = self.assess(
            proofs=(self.proof, replacement), reviews=reviewed, input_digest="bytes-b"
        )
        self.assertTrue(result.ready, result.blockers)

    def test_claiming_same_receipt_as_multiple_independent_reviews_blocks(self) -> None:
        reviews = (
            self.review("spec", receipt_id="shared-receipt"),
            self.review("quality", receipt_id="shared-receipt"),
        )
        self.assertFalse(self.assess(reviews=reviews, stage="stage2").ready)

    def test_unknown_requirement_finding_survives_as_blocker(self) -> None:
        finding = Finding(
            id="F8", obligation_id="removed-REQ", kind="missing-proof", description="No proof."
        )
        reviews = (
            self.review("spec", findings=(finding,)),
            self.review("quality"),
            self.review("adversarial"),
        )
        result = self.assess(reviews=reviews)
        self.assertFalse(result.ready)
        self.assertEqual(result.open_findings, ("F8",))

    def test_new_report_of_closed_finding_reopens_it(self) -> None:
        reviews = self.closure_reviews() + (
            self.finding_review().model_copy(
                update={"id": "new-counterexample", "receipt_id": "receipt-new-counterexample"}
            ),
        )
        self.assertEqual(self.assess(reviews=reviews).open_findings, ("F7",))

    def test_cannot_reclassify_same_finding_id_as_auxiliary(self) -> None:
        original = self.finding_review()
        observation = original.findings[0].model_copy(update={"obligation_id": None})
        reviews = (
            original,
            self.review("spec", id="changed", receipt_id="changed", findings=(observation,)),
            self.review("quality"),
            self.review("adversarial"),
        )
        self.assertFalse(self.assess(reviews=reviews).ready)

    def test_duplicate_proof_identity_cannot_overwrite_evidence(self) -> None:
        changed = self.proof.model_copy(update={"valid": False})
        self.assertFalse(self.assess(proofs=(changed, self.proof)).ready)

    def test_support_and_fence_do_not_require_behavior_selectors(self) -> None:
        for kind in ("SUPPORT", "STRUCTURAL-FENCE"):
            with self.subTest(kind=kind):
                self.obligation = self.obligation.model_copy(update={"kind": kind})
                proof = self.proof.model_copy(update={"selectors": ()})
                self.assertTrue(self.assess(proofs=(proof,)).ready)

    def test_empty_obligation_set_cannot_vacuously_be_accepted(self) -> None:
        result = assess_readiness((), (), (), input_digest="a", author_id="implementer")
        self.assertFalse(result.ready)

    def test_truthful_refutation_can_be_appended_while_acceptance_is_blocked(self) -> None:
        review = self.finding_review()
        errors = validate_review_record(
            (self.obligation,), (self.proof,), (), review, author_id="implementer"
        )
        self.assertEqual(errors, ())
        self.assertFalse(self.assess(reviews=(review,)).ready)

    def test_invalid_closure_cannot_poison_immutable_history(self) -> None:
        reviews = self.closure_reviews(finding_id="nonexistent")
        errors = validate_review_record(
            (self.obligation,), (self.proof,), reviews[:-1], reviews[-1], author_id="implementer"
        )
        self.assertTrue(errors)

    def test_closure_cannot_claim_invalid_execution_as_remedy(self) -> None:
        reviews = self.closure_reviews()
        invalid = self.proof.model_copy(update={"valid": False})
        errors = validate_review_record(
            (self.obligation,), (invalid,), reviews[:-1], reviews[-1], author_id="implementer"
        )
        self.assertTrue(errors)

    def test_missing_proof_finding_can_be_recorded_before_any_proof_exists(self) -> None:
        review = self.finding_review().model_copy(
            update={"proof_ids": (), "accepted_proof_ids": ()}
        )
        errors = validate_review_record((self.obligation,), (), (), review, author_id="implementer")
        self.assertEqual(errors, ())

    def test_auxiliary_raw_refutation_preserves_existing_accepted_proof(self) -> None:
        observation = Finding(
            id="N2", kind="counterexample", description="Historical commentary is inaccurate."
        )
        reviews = tuple(self.review(stage) for stage in ("spec", "quality", "adversarial")) + (
            self.review(
                "adversarial",
                id="commentary-review",
                receipt_id="commentary-receipt",
                verdict="refuted",
                findings=(observation,),
            ),
        )
        self.assertTrue(self.assess(reviews=reviews).ready)

    def test_raw_accepted_verdict_cannot_grant_unlisted_proof_approval(self) -> None:
        reviews = (self.review("spec", accepted_proof_ids=()), self.review("quality"))
        self.assertFalse(self.assess(reviews=reviews, stage="stage2").ready)

    def test_auxiliary_refutation_without_new_approvals_retains_prior_approval(self) -> None:
        reviews = tuple(self.review(stage) for stage in ("spec", "quality", "adversarial")) + (
            self.review(
                "adversarial",
                id="aux",
                receipt_id="receipt-aux",
                verdict="refuted",
                accepted_proof_ids=(),
                findings=(
                    Finding(id="aux", kind="counterexample", description="Optional note is wrong."),
                ),
            ),
        )
        result = self.assess(reviews=reviews)
        self.assertTrue(result.ready, result.blockers)

    def test_mapped_finding_overrides_explicit_proof_approval(self) -> None:
        result = self.assess(
            reviews=(self.finding_review(), self.review("quality"), self.review("adversarial"))
        )
        self.assertFalse(result.ready)
        self.assertEqual(result.open_findings, ("F7",))

    def test_accepted_proof_scope_cannot_escape_or_repeat_examined_scope(self) -> None:
        for accepted in (("outside",), ("proof-a", "proof-a")):
            with self.subTest(accepted=accepted):
                review = self.review("spec", accepted_proof_ids=accepted)
                self.assertTrue(
                    validate_review_record(
                        (self.obligation,), (self.proof,), (), review, author_id="implementer"
                    )
                )

    def test_missing_proof_review_does_not_allow_unexplained_empty_scope(self) -> None:
        review = self.review("spec", proof_ids=(), accepted_proof_ids=())
        self.assertTrue(
            validate_review_record((self.obligation,), (), (), review, author_id="implementer")
        )

    def test_initial_missing_proof_finding_reaches_verified_closure(self) -> None:
        missing = self.finding_review().model_copy(
            update={"proof_ids": (), "accepted_proof_ids": ()}
        )
        self.assertFalse(self.assess(proofs=(), reviews=(missing,)).ready)
        reviews = (
            missing,
            self.review("spec", id="repair", receipt_id="receipt-repair"),
            self.review("quality"),
            self.review(
                "adversarial",
                closures=(Closure(finding_id="F7", obligation_id="REQ-02", proof_id="proof-a"),),
            ),
        )
        self.assertEqual(
            validate_review_record(
                (self.obligation,),
                (self.proof,),
                reviews[:-1],
                reviews[-1],
                author_id="implementer",
            ),
            (),
        )
        self.assertTrue(self.assess(reviews=reviews).ready)

    def test_task_scope_keeps_future_obligations_and_findings_for_final_gate(self) -> None:
        future = self.obligation.model_copy(update={"id": "REQ-03"})
        reviews = (
            self.review("spec"),
            self.review("quality"),
            self.review(
                "spec",
                id="future-review",
                receipt_id="future-receipt",
                obligation_ids=("REQ-03",),
                proof_ids=(),
                accepted_proof_ids=(),
                findings=(
                    Finding(
                        id="future-gap",
                        obligation_id="REQ-03",
                        kind="missing-proof",
                        description="Not implemented yet.",
                    ),
                ),
            ),
        )
        arguments = {"input_digest": "bytes-a", "author_id": "implementer", "stage": "stage2"}
        scoped = assess_readiness(
            (self.obligation, future),
            (self.proof,),
            reviews,
            obligation_ids=("REQ-02",),
            **arguments,
        )
        self.assertTrue(scoped.ready, scoped.blockers)
        all_obligations = assess_readiness(
            (self.obligation, future), (self.proof,), reviews, **arguments
        )
        self.assertFalse(all_obligations.ready)
        self.assertEqual(all_obligations.open_findings, ("future-gap",))
        self.assertEqual(reviews[-1].obligation_ids, ("REQ-03",))

    def test_explicit_scope_cannot_be_empty_unknown_or_limit_stage4(self) -> None:
        for scope, stage in (((), "stage2"), (("unknown",), "stage2"), (("REQ-02",), "stage4")):
            with self.subTest(scope=scope, stage=stage):
                self.assertFalse(self.assess(obligation_ids=scope, stage=stage).ready)

    def test_declared_review_channels_cannot_waive_proof_or_findings(self) -> None:
        self.assertTrue(self.assess(reviews=(), stage="stage2", required_review_stages=()).ready)
        self.assertFalse(
            self.assess(proofs=(), reviews=(), stage="stage2", required_review_stages=()).ready
        )
        self.assertFalse(
            self.assess(
                reviews=(self.finding_review(),), stage="stage2", required_review_stages=()
            ).ready
        )
        self.assertTrue(
            self.assess(
                reviews=(self.review("adversarial"),), required_review_stages=("adversarial",)
            ).ready
        )
