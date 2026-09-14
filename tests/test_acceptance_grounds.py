"""A reviewer that cannot execute must cite what it read to approve (GHI #994).

OBPI-0.35.0-06's Stage-2 spec review recorded, under "Confirmed", that the
ledger "carries `artifact_edited` events citing `docs/user/manpages/validate.md`
(independently located)". No such event exists, and the claim was the basis on
which the review approved REQ-07's proof. It sat in narrative prose the importer
never reads, so nothing could challenge it, and it failed OPEN: a fabricated
confirmation only ever makes a requirement look more proven than it is.

Reading prose for false claims is the substring-guessing failure GHI #888 closed.
The remedy is a structured channel instead: an approval from a reviewer whose
tool grant cannot execute carries `grounds` -- an exact excerpt from a repository
file it read, or from the proof's recorded evidence -- and the importer confirms
the excerpt is actually there. What the reviewer could not observe belongs in
`verification_gaps`, never in an approval.

The receipts here name `claude --agent <persona>` because that is the Stage-2
dispatch the pipeline skill prescribes, and the persona's tool grant is read from
`.claude/agents/<persona>.md` by the same reader the review composer uses (GHI #941).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.acceptance import Proof
from gzkit.acceptance_execution import canonical_obligations, input_digest
from gzkit.acceptance_store import (
    acceptance_ledger,
    acceptance_status,
    initialize,
    load_history,
    record_proof,
    record_review,
)
from gzkit.ledger_events import acceptance_recorded_event
from tests.test_acceptance_execution import REQ, ExecutionFixture
from tests.test_acceptance_store import captured_receipt

OBPI = "OBPI-0.1.0-01-engine"
_EVIDENCE = '{"fixture":"synthetic executed proof for grounding tests"}'
_SPEC_ARGV = ["claude", "--agent", "spec-reviewer", "--model", "sonnet", "--print", "review"]
# The fabricated confirmation, as a citation: no ledger row in this repository says it.
_ABSENT_LEDGER_ROW = '"event": "artifact_edited", "path": "docs/user/manpages/validate.md"'
# Present in src/engine.py, reflowed the way a reviewer quoting two lines writes it.
_ENGINE_EXCERPT = "def double(value):\n return value * 2"


def _agent(root: Path, name: str, tools: str) -> None:
    path = root / ".claude" / "agents" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f"---\nname: {name}\ndescription: Independent review.\ntools: {tools}\n---\n\nBody.\n",
        encoding="utf-8",
    )


class CitedApprovalTests(ExecutionFixture):
    def setUp(self):
        super().setUp()
        self.write(".gzkit.json", json.dumps({"paths": {"design_root": "design"}}))
        self.brief = self.brief.rename(self.brief.with_name(f"{OBPI}.md"))
        _agent(self.root, "spec-reviewer", "Read, Glob, Grep")
        _agent(self.root, "executing-reviewer", "Read, Glob, Grep, Bash")
        initialize(self.root, OBPI, "implementer-session")
        obligation = canonical_obligations(self.root, self.brief)[0]
        self.proof = Proof(
            id="proof-grounding",
            obligation_id=REQ,
            contract_digest=obligation.contract_digest,
            input_digest=input_digest(self.root, self.brief),
            selectors=("tests.test_engine.EngineTests.test_double",),
            evidence=_EVIDENCE,
            valid=True,
        )
        record_proof(self.root, OBPI, self.proof)

    def spec_receipt(self, grounds=None, *, argv=_SPEC_ARGV, verdict="accepted", findings=()):
        receipt = captured_receipt(self.proof, "spec", findings=findings, verdict=verdict)
        payload = json.loads(receipt["stdout_tail"].removeprefix("```json\n").removesuffix("\n```"))
        if grounds is not None:
            payload["grounds"] = grounds
        legacy = {"verdict": "PASS", "findings": [], "verification_gaps": [], "summary": "s"}
        receipt["stdout_tail"] = json.dumps(legacy) + "\n" + json.dumps(payload)
        receipt["step"]["command"] = list(argv)
        return receipt

    def ground(self, excerpt, path=None, proof_id=None):
        return {"proof_id": proof_id or self.proof.id, "path": path, "excerpt": excerpt}

    def assert_refused_without_append(self, receipt):
        before = len(acceptance_ledger(self.root).read_all())
        with self.assertRaisesRegex(ValueError, "cannot execute"):
            record_review(self.root, OBPI, receipt)
        self.assertEqual(len(acceptance_ledger(self.root).read_all()), before)
        self.assertEqual(load_history(self.root, OBPI).reviews, [])

    def assert_imports(self, receipt):
        """A refusal of a grounded or exempt review is the failure under test, not an error."""
        try:
            return record_review(self.root, OBPI, receipt)
        except ValueError as exc:
            self.fail(f"refused a review this contract admits: {exc}")

    def assert_spec_approval_counts(self):
        blockers = acceptance_status(self.root, OBPI, stage="stage2").blockers
        self.assertFalse(any("lacks accepted spec review" in item for item in blockers), blockers)

    def test_an_approval_citing_a_ledger_row_that_does_not_exist_is_refused(self):
        """The GHI #994 instance: the confirmation names evidence nobody could have read."""
        ledger = acceptance_ledger(self.root).path.relative_to(self.root).as_posix()
        self.assert_refused_without_append(
            self.spec_receipt([self.ground(_ABSENT_LEDGER_ROW, path=ledger)])
        )

    def test_an_approval_that_cites_nothing_is_refused(self):
        for argv in (_SPEC_ARGV, ["claude", "--agent=spec-reviewer", "--print", "review"]):
            with self.subTest(argv=argv):
                self.assert_refused_without_append(self.spec_receipt(argv=argv))

    def test_leaving_the_unperformed_check_as_a_gap_and_citing_a_read_file_imports(self):
        """The valid control: the same review, with the ledger check routed honestly."""
        review = self.assert_imports(
            self.spec_receipt([self.ground(_ENGINE_EXCERPT, "src/engine.py")])
        )
        self.assertEqual(review.accepted_proof_ids, (self.proof.id,))
        self.assertEqual(load_history(self.root, OBPI).reviews[0].grounds, review.grounds)
        self.assert_spec_approval_counts()

    def test_an_excerpt_from_the_proofs_recorded_evidence_grounds_its_approval(self):
        self.assert_imports(self.spec_receipt([self.ground(_EVIDENCE)]))
        self.assert_spec_approval_counts()

    def test_one_false_citation_is_refused_even_beside_a_true_one(self):
        grounds = [
            self.ground(_ENGINE_EXCERPT, "src/engine.py"),
            self.ground("return value * 3 as the required result", "src/engine.py"),
        ]
        self.assert_refused_without_append(self.spec_receipt(grounds))

    def test_a_citation_outside_the_repository_is_refused(self):
        with tempfile.TemporaryDirectory() as outside:
            elsewhere = Path(outside) / "notes.txt"
            elsewhere.write_text(_ENGINE_EXCERPT, encoding="utf-8")
            for path in (elsewhere.as_posix(), f"../{Path(outside).name}/notes.txt"):
                with self.subTest(path=path):
                    self.assert_refused_without_append(
                        self.spec_receipt([self.ground(_ENGINE_EXCERPT, path)])
                    )

    def test_an_excerpt_too_short_to_identify_what_was_read_is_refused(self):
        self.assert_refused_without_append(
            self.spec_receipt([self.ground("value", "src/engine.py")])
        )

    def test_a_citation_for_a_proof_the_review_did_not_examine_is_refused(self):
        grounds = [
            self.ground(_ENGINE_EXCERPT, "src/engine.py"),
            self.ground(_ENGINE_EXCERPT, "src/engine.py", proof_id="proof-never-examined"),
        ]
        self.assert_refused_without_append(self.spec_receipt(grounds))

    def test_a_refutation_needs_no_citation(self):
        """Only approvals fail open; a finding blocks and is never refused for citing nothing."""
        finding = {
            "id": "F-uncited",
            "obligation_id": REQ,
            "kind": "counterexample",
            "description": "Negative inputs violate the required result.",
        }
        self.assert_imports(self.spec_receipt(verdict="refuted", findings=[finding]))
        self.assertEqual(acceptance_status(self.root, OBPI).open_findings, ("F-uncited",))

    def test_an_unresolvable_tool_grant_is_treated_as_unable_to_execute(self):
        for argv in (["claude", "-p", "review"], ["claude", "--agent", "unknown-reviewer", "-p"]):
            with self.subTest(argv=argv):
                self.assert_refused_without_append(self.spec_receipt(argv=argv))

    def test_an_argv_the_persona_file_cannot_decide_is_unable_to_execute(self):
        """The file grant decides only when the argv neither overrides nor escapes it."""
        self.write(".claude/escape.md", "---\nname: escape\ntools: Read, Bash\n---\n")
        persona = ["claude", "--agent", "executing-reviewer"]
        for argv in (
            [*persona, "--disallowedTools", "Bash", "--print", "review"],
            [*persona, "--disallowedTools=Bash", "--print", "review"],
            [*persona, "--tools", "Read", "--print", "review"],
            [*persona, "--agents", '{"executing-reviewer": {"tools": ["Read"]}}', "-p"],
            [*persona, "--agent", "spec-reviewer", "--print", "review"],
            ["claude", "--agent", "../escape", "--print", "review"],
        ):
            with self.subTest(argv=argv):
                self.assert_refused_without_append(self.spec_receipt(argv=argv))

    def test_a_reviewer_whose_grant_executes_is_not_asked_for_citations(self):
        for argv in (
            ["claude", "--agent", "executing-reviewer", "--print", "review"],
            ["claude", "--agent=executing-reviewer", "--print", "second review"],
        ):
            with self.subTest(argv=argv):
                self.assert_imports(self.spec_receipt(argv=argv))
        self.assert_spec_approval_counts()

    def test_a_false_citation_is_refused_whatever_the_transport_can_do(self):
        """Absence claims nothing; a citation that is present is a claim, so it is checked."""
        grounds = [self.ground(_ABSENT_LEDGER_ROW, "src/engine.py")]
        for argv in (
            ["claude", "--agent", "executing-reviewer", "--print", "review"],
            ["node", "codex-companion.mjs", "adversarial-review"],
        ):
            with self.subTest(argv=argv), self.assertRaisesRegex(ValueError, "does not occur"):
                record_review(self.root, OBPI, self.spec_receipt(grounds, argv=argv))
        self.assertEqual(load_history(self.root, OBPI).reviews, [])

    def test_a_cross_vendor_review_is_not_asked_for_citations(self):
        """Its execution claims travel as replay records (GHI #961), not as grounds."""
        receipt = self.spec_receipt(argv=["node", "codex-companion.mjs", "adversarial-review"])
        self.assert_imports(receipt)
        self.assert_spec_approval_counts()

    def test_reviews_recorded_before_citations_existed_still_replay_and_reimport(self):
        """Refusal binds new imports only; an append-only history is never reinterpreted."""
        historical = self.spec_receipt()
        acceptance_ledger(self.root).append(acceptance_recorded_event(OBPI, "review", historical))
        recorded = load_history(self.root, OBPI).reviews
        self.assertEqual(len(recorded), 1)
        self.assert_spec_approval_counts()
        self.assertEqual(self.assert_imports(historical), recorded[0])


if __name__ == "__main__":
    unittest.main()
