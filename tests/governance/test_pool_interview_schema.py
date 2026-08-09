"""Pool ADR interview JSON schema enforcement (GHI #719).

A pool ADR's Step-0 interview is a hand-authored JSON in the pool bucket. The
non-pool path (``gz interview adr --from``) deserializes and fails closed on a
malformed payload; the pool path had no reader at all, so the same artifact
type carried a different governance guarantee by kind.

The audit closes that asymmetry by delegating the answers grammar to the very
function the CLI loader uses, rather than restating it in a second schema. The
subsumption is asserted directly (``TestGrammarIsSingleSourced``) so a future
author cannot fork a parallel authority that drifts.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.taxonomy import audit_pool_interview_schema
from gzkit.interview import answer_payload_problems

PROJECT_ROOT = Path(__file__).resolve().parents[2]

_VALID = {
    "id": "ADR-pool.sample-thing",
    "title": "Sample Thing",
    "semver": "pool",
    "lane": "heavy",
    "parent": "ADR-0.8.0",
    "intent": "why",
    "decision": "what",
    "positive_consequences": "good",
    "negative_consequences": "bad",
    "checklist": "steps",
    "alternatives": "rejected",
}


def _plant(root: Path, name: str, payload: object) -> None:
    """Write *payload* as a pool interview record named *name* under *root*."""
    pool = root / "docs" / "design" / "adr" / "pool"
    pool.mkdir(parents=True, exist_ok=True)
    text = payload if isinstance(payload, str) else json.dumps(payload)
    (pool / name).write_text(text, encoding="utf-8")


class _PlantedPoolCase(unittest.TestCase):
    """Base for cases that plant one record in a throwaway project root."""

    def assert_one_finding(self, name: str, payload: object, needle: str) -> None:
        """Plant *payload* and assert the audit reports it, citing *needle*."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(root, name, payload)
            errors = audit_pool_interview_schema(root)
            self.assertEqual(len(errors), 1, f"expected exactly one finding, got {errors}")
            self.assertIn(needle, errors[0].message)


class TestCommittedPoolInterviewsAreClean(unittest.TestCase):
    def test_the_real_corpus_passes(self) -> None:
        # A regression fence, not a tautology: this is the corpus the check was
        # designed against, and a future hand-edit that breaks the grammar has
        # to fail here before it can reach a promotion.
        self.assertEqual(audit_pool_interview_schema(PROJECT_ROOT), [])

    def test_the_corpus_is_not_empty(self) -> None:
        # Without this, `assertEqual(..., [])` above would pass just as happily
        # if the glob stopped matching anything at all.
        pool = PROJECT_ROOT / "docs" / "design" / "adr" / "pool"
        self.assertTrue(sorted(pool.glob("*-interview.json")))


class TestPayloadGrammar(_PlantedPoolCase):
    def test_unknown_key_is_reported(self) -> None:
        # The exact drift commit 8b0a2f32 repaired by hand: an invented nested
        # key that no reader consumed and the CLI loader already rejected.
        self.assert_one_finding(
            "sample-thing-interview.json",
            {**_VALID, "forcing_functions": "nested"},
            "forcing_functions",
        )

    def test_missing_required_answer_is_reported(self) -> None:
        payload = {k: v for k, v in _VALID.items() if k != "decision"}
        self.assert_one_finding("sample-thing-interview.json", payload, "decision")

    def test_non_object_payload_is_reported(self) -> None:
        self.assert_one_finding("sample-thing-interview.json", ["not", "an", "object"], "object")

    def test_non_string_value_is_reported(self) -> None:
        # Deliberately a validator-free slot. `lane` carries the only validator
        # in ADR_QUESTIONS, so a number there trips the type check AND the
        # validator — two findings for one defect, which would make this
        # assertion pass for the wrong reason.
        self.assert_one_finding("sample-thing-interview.json", {**_VALID, "intent": 3}, "intent")

    def test_unreadable_json_is_a_finding_not_a_skip(self) -> None:
        # Mirrors the GHI #736 correction in this module's taxonomy audit: a
        # record the audit cannot READ is refused, never silently skipped.
        # "cannot read" must not resolve to "nothing to check".
        self.assert_one_finding("sample-thing-interview.json", "{ not json", "could not be read")


class TestPoolArtifactIdentity(_PlantedPoolCase):
    def test_non_pool_id_is_reported(self) -> None:
        self.assert_one_finding(
            "sample-thing-interview.json",
            {**_VALID, "id": "ADR-0.36.0-sample-thing"},
            "ADR-pool.",
        )

    def test_filename_disagreeing_with_id_is_reported(self) -> None:
        self.assert_one_finding(
            "other-slug-interview.json",
            _VALID,
            "other-slug",
        )

    def test_semver_must_be_pool(self) -> None:
        self.assert_one_finding(
            "sample-thing-interview.json",
            {**_VALID, "semver": "0.36.0"},
            "semver",
        )


class TestGrammarIsSingleSourced(unittest.TestCase):
    """The audit and the CLI loader must answer to one authority.

    GHI #719's own scope hint proposed "a pool-interview schema under
    ``src/gzkit/schemas/``". That was declined: ``ADR_QUESTIONS`` already is
    the schema, and a second file would be free to drift from it — the
    parallel-model failure ``.claude/rules/hexagonal-architecture.md`` rule 8
    forbids. These tests pin the delegation so the fork cannot be reintroduced
    without turning one of them red.
    """

    def test_audit_accepts_every_question_id_the_loader_accepts(self) -> None:
        from gzkit.interview import get_interview_questions

        full = {q.id: "filled" for q in get_interview_questions("adr")}
        full["id"] = "ADR-pool.sample-thing"
        full["semver"] = "pool"
        full["lane"] = "heavy"  # the one question carrying a value validator
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _plant(root, "sample-thing-interview.json", full)
            self.assertEqual(audit_pool_interview_schema(root), [])

    def test_grammar_helper_rejects_what_the_loader_rejects(self) -> None:
        # The shared function is the seam. If it stops reporting unknown keys,
        # both readers go blind together and the asymmetry returns.
        self.assertTrue(answer_payload_problems("adr", {"not_a_question_id": "x"}))
        self.assertFalse(answer_payload_problems("adr", {"intent": "x"}))


if __name__ == "__main__":
    unittest.main()
